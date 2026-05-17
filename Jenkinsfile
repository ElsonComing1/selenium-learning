// ==========================================
// 文件名：Jenkinsfile（位于项目根目录）
// 用途：完整 CI/CD 流程：Gitee → 动态容器 → Pytest+Allure → JMeter性能测试 → 钉钉+邮件
// ==========================================

pipeline {
    agent any

    environment {
        // 镜像与容器命名（带构建号隔离，防止并发冲突）
        TEST_IMAGE = "api-test-env:${BUILD_NUMBER}"
        TEST_CONTAINER = "api-test-runner-${BUILD_NUMBER}"
        JMETER_CONTAINER = "jmeter-runner-${BUILD_NUMBER}"

        // Gitee 凭证 ID（需在 Jenkins 中预先配置）
        GITEE_CREDENTIALS = 'gitee-credentials'

        // 钉钉 Webhook 凭证 ID
        DINGDING_CREDENTIALS = 'DINGDING_CREDENTIALS'

        // 邮箱接收列表（逗号分隔）
        // EMAIL_RECIPIENTS = '19015437827@163.com,206432984@qq.com,2567195697@qq.com,1754605787@qq.com,2653202245@qq.com'
        EMAIL_RECIPIENTS = '19015437827@163.com'

        // 宿主机检查用（基于 WORKSPACE 根目录）
        JMETER_SCRIPT_HOST = 'content/API_Project/jmeter/api_load_test.jmx'
        // 容器内执行用（基于 -w 工作目录 content/API_Project）
        JMETER_SCRIPT_CONTAINER = 'jmeter/api_load_test.jmx'
    }

    options {
        // 保留最近 10 次构建记录，节省磁盘
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // 禁止并发构建（避免动态容器名冲突）
        disableConcurrentBuilds()
        // 添加时间戳到控制台输出
        timestamps()
    }

    stages {

        // --------------------------------------------------
        // Stage 1: 构建测试镜像（国内缓存加速，内含 Python + JMeter）
        // --------------------------------------------------
        stage('Build Test Image') {
            steps {
                script {
                    dir('content/API_Project') {
                        echo ">>> 正在构建测试镜像: ${TEST_IMAGE}"

                        sh """
                            docker build \
                                --force-rm  \
                                --no-cache \
                                -t ${TEST_IMAGE} \
                                -f Dockerfile.test \
                                .
                        """

                        // 铁证校验：镜像内必须有 PyYAML
                        sh """
                            docker run --rm ${TEST_IMAGE} python -c "import yaml; print('PyYAML version:', yaml.__version__)" || { echo "ERROR: 镜像内缺少 PyYAML"; exit 1; }
                        """

                        // 铁证校验：镜像内必须有 JMeter
                        sh """
                            docker run --rm ${TEST_IMAGE} jmeter --version | head -n 1 || { echo "ERROR: 镜像内缺少 JMeter"; exit 1; }
                        """

                        echo ">>> 镜像构建完成"
                    }
                }
            }
        }

        // --------------------------------------------------
        // Stage 2: 运行动态容器执行 API 功能测试（Pytest）
        // --------------------------------------------------
        stage('Run Tests in Dynamic Container') {
            steps {
                script {
                    // ✅ 关键：catchError 让 pytest 失败时不阻断流水线
                    // buildResult='UNSTABLE' 表示整体构建继续，但标记为不稳定
                    // stageResult='FAILURE' 表示当前阶段自身标记为失败（便于追溯）
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        echo ">>> 启动动态测试容器: ${TEST_CONTAINER}"

                        sh """
                            docker rm -f ${TEST_CONTAINER} || true

                            echo ">>> [Master] 本地文件铁证:"
                            ls -la content/API_Project/conftest.py || { echo "ERROR: Master 内无 conftest.py"; exit 1; }

                            echo ">>> [Dynamic] 启动容器并执行 Pytest..."
                            docker run --rm \
                                --name ${TEST_CONTAINER} \
                                --volumes-from jenkins-master-cicd \
                                -w /var/jenkins_home/workspace/API-Automation-Pipeline/content/API_Project \
                                -e PYTHONPATH=/var/jenkins_home/workspace/API-Automation-Pipeline/content/API_Project \
                                -e LOGURU_COLORIZE=false \
                                ${TEST_IMAGE} \
                                pytest testcases/ -v \
                                    --color=no \
                                    --alluredir=report/allure-results \
                                    --tb=short \
                                    -rA \
                                    --env=production \
                                    --env-file=config/env_settings.yaml
                        """

                        echo ">>> Pytest 功能测试执行完毕"
                    }
                }
            }
        }

        // --------------------------------------------------
        // Stage 3: 执行 JMeter 性能测试（非 GUI 模式）
        // --------------------------------------------------
        stage('Run JMeter Performance Tests') {
            steps {
                script {
                    def scriptExist = sh(returnStatus: true, script: "test -f ${JMETER_SCRIPT_HOST}")
                    if (scriptExist != 0) {
                        echo "⚠️ 未找到 JMeter 脚本: ${JMETER_SCRIPT_HOST}，跳过性能测试"
                        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                            error("JMeter 脚本缺失，已标记为 UNSTABLE")
                        }
                        return
                    }

                    echo ">>> 启动 JMeter 性能测试容器: ${JMETER_CONTAINER}"

                    sh """
                        docker rm -f ${JMETER_CONTAINER} || true

                        docker run --rm \
                            --name ${JMETER_CONTAINER} \
                            --volumes-from jenkins-master-cicd \
                            -w /var/jenkins_home/workspace/API-Automation-Pipeline/content/API_Project/jmeter \
                            ${TEST_IMAGE} \
                            bash -c 'rm -rf ../report/jmeter-report ../report/jmeter-results.jtl ../report/jmeter.log && \
                                jmeter -n -t api_load_test.jmx \
                                    -l ../report/jmeter-results.jtl \
                                    -j ../report/jmeter.log \
                                    -e -o ../report/jmeter-report \
                                    -Jserver.rmi.ssl.disable=true \
                                    -Jjmeter.save.saveservice.output_format=csv \
                                    -Jjmeter.save.saveservice.assertion_results_failure_message=true'
                        """
                        // ✅ 关键改动：
                        // 1. -w 工作目录切到 jmeter/，./users.csv 直接指向同目录文件
                        // 2. 脚本路径改为 api_load_test.jmx（当前目录下）
                        // 3. 报告路径改为 ../report/（因为当前在 jmeter/ 子目录）
                        // 4. 加 -j ../report/jmeter.log 保留 JMeter 内部日志，便于排查

                    echo ">>> JMeter 性能测试执行完毕"
                }
            }
        }

        // --------------------------------------------------
        // Stage 4: 生成 Allure 报告（功能测试）
        // --------------------------------------------------
        stage('Generate Allure Report') {
            steps {
                script {
                    echo ">>> 生成 Allure 报告..."

                    def allureDir = 'content/API_Project/report/allure-results'
                    // 定义变量存报告目录的相对路径
                    def resultsExist = sh(returnStatus: true, script: "find ${allureDir} -type f 2>/dev/null | grep -q .")
                    // 

                    if (resultsExist == 0) {
                        echo ">>> 发现 Allure 结果，生成报告..."
                        allure([
                            includeProperties: false,
                            jdk: '',
                            properties: [],
                            reportBuildPolicy: 'ALWAYS',
                            results: [[path: "${allureDir}"]]
                        ])
                    } else {
                        echo "⚠️ 警告：未发现 Allure 结果，可能测试未生成或目录为空"
                    }
                }
            }
        }

        // --------------------------------------------------
        // Stage 5: 发布 JMeter HTML 性能报告
        // --------------------------------------------------
        stage('Publish JMeter Report') {
            steps {
                script {
                    def jmeterReportDir = 'content/API_Project/report/jmeter-report'
                    def reportExist = sh(returnStatus: true, script: "test -d ${jmeterReportDir} && test -f ${jmeterReportDir}/index.html")
                    // 无论成与否都是返回数字，不会中断，成功返回0，失败返回别的数字。

                    if (reportExist == 0) {
                        echo ">>> 发布 JMeter HTML 报告..."
                        publishHTML(target: [
                            allowMissing: false,
                            alwaysLinkToLastBuild: true,
                            keepAll: true,
                            reportDir: "${jmeterReportDir}",
                            reportFiles: 'index.html',
                            reportName: 'JMeter Performance Report'
                        ])
                    } else {
                        echo "⚠️ 未找到 JMeter HTML 报告，跳过发布"
                    }
                }
            }
        }
    }

    // --------------------------------------------------
    // Post 构建处理：通知、归档与清理
    // --------------------------------------------------
    post {
        always {
            // 安全清理：保留 Allure 结果、JMeter 报告和 JTL 原始数据
            cleanWs(
                cleanWhenNotBuilt: false,
                deleteDirs: true,
                notFailBuild: true,
                patterns: [
                    [pattern: '**/__pycache__/**', type: 'INCLUDE'],
                    [pattern: '**/.pytest_cache/**', type: 'INCLUDE'],
                    [pattern: '**/*.pyc', type: 'INCLUDE'],
                    [pattern: 'content/API_Project/report/allure-results/**', type: 'EXCLUDE'],
                    [pattern: 'content/API_Project/report/jmeter-report/**', type: 'EXCLUDE'],
                    [pattern: 'content/API_Project/report/jmeter-results.jtl', type: 'EXCLUDE']
                ]
            )

            script {
                echo ">>> 执行清理任务..."

                // 清理动态容器与镜像
                sh """
                    docker rmi ${TEST_IMAGE} || true
                    docker rm -f ${TEST_CONTAINER} || true
                    docker rm -f ${JMETER_CONTAINER} || true
                """

                // 归档 JMeter 原始数据（即使 HTML 发布失败，也能下载 JTL 自行分析）
                archiveArtifacts(
                    artifacts: 'content/API_Project/report/jmeter-results.jtl',
                    allowEmptyArchive: true,
                    onlyIfSuccessful: false
                )

                // 二次清理（保留关键产物）
                cleanWs(
                    cleanWhenNotBuilt: false,
                    deleteDirs: true,
                    notFailBuild: true,
                    patterns: [
                        [pattern: '**/__pycache__/**', type: 'INCLUDE'],
                        [pattern: '**/.pytest_cache/**', type: 'INCLUDE'],
                        [pattern: '**/*.pyc', type: 'INCLUDE'],
                        [pattern: 'content/API_Project/report/allure-results/**', type: 'EXCLUDE'],
                        [pattern: 'content/API_Project/report/jmeter-report/**', type: 'EXCLUDE'],
                        [pattern: 'content/API_Project/report/jmeter-results.jtl', type: 'EXCLUDE']
                    ]
                )
            }
            // 在 post 的 always 里，清理构建残留
            sh """
                docker container prune -f --filter 'until=24h' || true
                docker image prune -f || true
            """
        }

        success {
            script {
                // 1. 钉钉通知（增加 JMeter 报告入口）
                dingtalk(
                    robot: "${DINGDING_CREDENTIALS}",
                    type: 'MARKDOWN',
                    title: "✅ 构建成功: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    text: [
                        "### 🎉 API 自动化测试 + 性能测试 构建成功\n",
                        "---\n",
                        "**项目**: ${env.JOB_NAME}\n",
                        "**构建号**: ${env.BUILD_NUMBER}\n",
                        "**分支**: ${env.GIT_BRANCH}\n",
                        "**持续时间**: ${currentBuild.durationString}\n",
                        "**Allure 报告**: [点击查看](${env.BUILD_URL}allure/)\n",
                        "**Grafana 实时监控**: [点击查看](http://106.14.250.120:3000/d/f4f65d5c-7fc7-4162-a42d-1841beb9e122)\n",
                        "**控制台**: [查看日志](${env.BUILD_URL}console)\n",
                        "---\n",
                        "📊 动态容器与性能测试环境已自动清理，资源已释放\n"
                    ]
                )

                // 2. 邮件通知
                emailext(
                    subject: "✅ 构建成功: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """
                        <h2 style="color: #2ecc71;">API 自动化测试 + 性能测试 构建成功</h2>
                        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
                            <tr><td style="background-color: #f2f2f2;"><b>项目名称</b></td><td>${env.JOB_NAME}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>构建编号</b></td><td>${env.BUILD_NUMBER}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>Git 提交</b></td><td>${env.GIT_COMMIT?.take(7)}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>构建时长</b></td><td>${currentBuild.durationString}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>Allure 报告</b></td><td><a href="${env.BUILD_URL}allure/">点击查看详细报告</a></td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>JMeter 性能报告</b></td><td><a href="http://106.14.250.120:3000/d/f4f65d5c-7fc7-4162-a42d-1841beb9e122">点击查看性能测试报告</a></td></tr>
                        </table>
                        <p>动态测试容器与 JMeter 容器已自动销毁，资源已回收。</p>
                    """,
                    to: "${EMAIL_RECIPIENTS}",
                    mimeType: 'text/html'
                )
                sh """
                    echo "JMeter 性能测试结果:" >> /tmp/build_summary.txt
                    grep "summary =" ${WORKSPACE}/content/API_Project/report/jmeter.log | tail -n 1 >> /tmp/build_summary.txt
                """
            }
        }

        failure {
            script {
                // 1. 钉钉失败通知
                dingtalk(
                    robot: "${DINGDING_CREDENTIALS}",
                    type: 'MARKDOWN',
                    title: "❌ 构建失败: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    atAll: true,
                    text: [
                        "### ⚠️ API 自动化测试 / 性能测试 构建失败\n",
                        "---\n",
                        "**项目**: ${env.JOB_NAME}\n",
                        "**构建号**: ${env.BUILD_NUMBER}\n",
                        "**失败阶段**: ${env.STAGE_NAME}\n",
                        "**Git 提交**: ${env.GIT_COMMIT?.take(7)}\n",
                        "**查看详情**: [控制台日志](${env.BUILD_URL}console)\n",
                        "---\n",
                        "🔴 请立即检查代码、JMeter 脚本或联系 DevOps 工程师\n"
                    ]
                )

                // 2. 邮件失败通知
                emailext(
                    subject: "❌ 构建失败: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """
                        <h2 style="color: #e74c3c;">API 自动化测试 / 性能测试 构建失败</h2>
                        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
                            <tr><td style="background-color: #f2f2f2;"><b>项目名称</b></td><td>${env.JOB_NAME}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>构建编号</b></td><td>${env.BUILD_NUMBER}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>失败阶段</b></td><td>${env.STAGE_NAME}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>错误日志</b></td><td><a href="${env.BUILD_URL}console">点击查看控制台</a></td></tr>
                        </table>
                        <p style="color: #c0392b;"><b>动态容器与 JMeter 容器已销毁，需手动重跑构建调试。</b></p>
                    """,
                    to: "${EMAIL_RECIPIENTS}",
                    mimeType: 'text/html'
                )
            }
        }

        unstable {
            echo "⚠️ 构建状态不稳定（有测试用例失败或 JMeter 脚本缺失，但未阻断流水线）"
        }
    }
}