// ==========================================
// 文件名：Jenkinsfile（位于项目根目录）
// 用途：完整 CI/CD 流程：Gitee → 动态容器 → Allure → 钉钉+邮件
// ==========================================

pipeline {
    // 使用 any 即可，因为我们手动控制 Docker 容器
    agent any
    
    environment {
        // 镜像与容器命名（带构建号隔离，防止并发冲突）
        TEST_IMAGE = "api-test-env:${BUILD_NUMBER}"
        TEST_CONTAINER = "api-test-runner-${BUILD_NUMBER}"
        
        // Gitee 凭证 ID（需在 Jenkins 中预先配置）
        GITEE_CREDENTIALS = 'gitee-credentials'
        
        // 钉钉 Webhook 凭证 ID
        DINGDING_CREDENTIALS = 'dingding-token'
        
        // 邮箱接收列表（逗号分隔）
        EMAIL_RECIPIENTS = '16531@qq.com,manager@company.com'  // 修改为你的邮箱
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
        // Stage 1: 从 Gitee 拉取最新代码
        // --------------------------------------------------
        stage('Checkout from Gitee') {
            steps {
                script {
                    echo ">>> 正在从 Gitee 拉取代码..."
                    
                    // 方式 A：使用预存凭证（推荐）
                    git(
                        url: 'https://gitee.com/ElsonComing1/selenium-learning.git',  // ★ 修改为你的仓库地址
                        branch: 'main',  // 或 master
                        credentialsId: "${GITEE_CREDENTIALS}"
                    )
                    
                    // 方式 B：如果是公开仓库，可省略 credentialsId
                    // git url: 'https://gitee.com/yourname/selenium-learning.git', branch: 'main'
                    
                    echo ">>> 代码拉取完成，当前提交: ${sh(returnStdout: true, script: 'git log -1 --pretty=format:"%h %s"').trim()}"
                }
            }
        }
        
        // --------------------------------------------------
        // Stage 2: 构建测试镜像（国内缓存加速）
        // --------------------------------------------------
        stage('Build Test Image') {
            steps {
                script {
                    dir('content/API_Project') {
                        echo ">>> 正在构建测试镜像: ${TEST_IMAGE}"
                        
                        // 使用宿主机的 Docker（通过 docker.sock）
                        sh """
                            docker build \
                                --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
                                -t ${TEST_IMAGE} \
                                -f Dockerfile.test \
                                .
                        """
                        
                        echo ">>> 镜像构建完成"
                    }
                }
            }
        }
        
        // --------------------------------------------------
        // Stage 3: 运行动态容器执行测试（核心数据传递）
        // --------------------------------------------------
        stage('Run Tests in Dynamic Container') {
            steps {
                script {
                    echo ">>> 启动动态测试容器: ${TEST_CONTAINER}"
                    
                    // ★ 核心机制：将 Jenkins Workspace（含刚拉取的代码）挂载进当前容器
                    // 这样容器内 /workspace 就是最新代码，无需 stash/unstash
                    // 同时挂载 report 目录用于收集 Allure 结果
                    
                    sh """
                        # 清理可能存在的同名容器（防御性编程）
                        docker rm -f ${TEST_CONTAINER} || true
                        
                        # 运行动态容器：
                        # --rm: 停止后自动删除（真正"用完即走"）
                        # -v ${WORKSPACE}:/workspace: 将 Jenkins 工作空间挂载到容器内
                        # -w /workspace/API_Project: 设置工作目录到测试项目
                        # --volumes-from: 也可继承数据卷，但直接挂载更清晰
                        
                        docker run --rm \
                            --name ${TEST_CONTAINER} \
                            -v "${WORKSPACE}:/workspace:rw" \
                            -w /workspace/content/API_Project \
                            -e PYTHONPATH=/workspace/content/API_Project \
                            ${TEST_IMAGE} \
                            pytest prepare_works/ testcases/ -v \
                                --alluredir=/workspace/content/API_Project/report/allure-results \
                                --tb=short \
                                -rA
                    """
                    
                    echo ">>> 动态容器执行完毕"
                }
            }
        }
        
        // --------------------------------------------------
        // Stage 4: 生成 Allure 报告（在 Master 端执行）
        // --------------------------------------------------
        stage('Generate Allure Report') {
            steps {
                script {
                    echo ">>> 生成 Allure 报告..."
                    
                    // 检查 Allure 结果是否存在
                    def allureDir = 'content/API_Project/report/allure-results'
                    def resultsExist = sh(returnStatus: true, script: "find ${allureDir} -type f 2>/dev/null | grep -q .")
                    
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
    }
    
    // --------------------------------------------------
    // Post 构建处理：通知与清理（无论成败都执行）
    // --------------------------------------------------
    post {
        always {
            script {
                echo ">>> 执行清理任务..."
                
                // 清理本次构建的镜像（节省磁盘，保留缓存层）
                sh """
                    docker rmi ${TEST_IMAGE} || true
                    docker rm -f ${TEST_CONTAINER} || true
                """
                
                // 清理工作空间中的临时文件（保留 Allure 结果用于展示）
                cleanWs(
                    cleanWhenNotBuilt: false,
                    deleteDirs: true,
                    notFailBuild: true,
                    patterns: [
                        [pattern: '**/__pycache__/**', type: 'INCLUDE'],
                        [pattern: '**/.pytest_cache/**', type: 'INCLUDE'],
                        [pattern: '**/*.pyc', type: 'INCLUDE'],
                        [pattern: 'content/API_Project/report/allure-results/**', type: 'EXCLUDE']  // 保留结果
                    ]
                )
            }
        }
        
        // --------------------------------------------------
        // 成功时：发送钉钉通知 + 邮件
        // --------------------------------------------------
        success {
            script {
                // 1. 钉钉通知
                dingtalk(
                    robot: "${DINGDING_CREDENTIALS}",  // 使用凭证 ID
                    type: 'MARKDOWN',
                    title: "✅ 构建成功: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    text: [
                        "### 🎉 API 自动化测试构建成功",
                        "---",
                        "**项目**: ${env.JOB_NAME}",
                        "**构建号**: ${env.BUILD_NUMBER}",
                        "**分支**: ${env.GIT_BRANCH}",
                        "**持续时间**: ${currentBuild.durationString}",
                        "**Allure 报告**: [点击查看](${env.BUILD_URL}allure/)",
                        "**控制台**: [查看日志](${env.BUILD_URL}console)",
                        "---",
                        "📊 测试环境已自动清理，资源已释放"
                    ].join("\n")
                )
                
                // 2. 邮件通知
                emailext(
                    subject: "✅ 构建成功: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """
                        <h2 style="color: #2ecc71;">API 自动化测试构建成功</h2>
                        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
                            <tr><td style="background-color: #f2f2f2;"><b>项目名称</b></td><td>${env.JOB_NAME}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>构建编号</b></td><td>${env.BUILD_NUMBER}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>Git 提交</b></td><td>${env.GIT_COMMIT?.take(7)}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>构建时长</b></td><td>${currentBuild.durationString}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>Allure 报告</b></td><td><a href="${env.BUILD_URL}allure/">点击查看详细报告</a></td></tr>
                        </table>
                        <p>动态测试容器已自动销毁，资源已回收。</p>
                    """,
                    to: "${EMAIL_RECIPIENTS}",
                    mimeType: 'text/html'
                )
            }
        }
        
        // --------------------------------------------------
        // 失败时：发送钉钉通知 + 邮件（更高优先级告警）
        // --------------------------------------------------
        failure {
            script {
                // 1. 钉钉失败通知（@所有人）
                dingtalk(
                    robot: "${DINGDING_CREDENTIALS}",
                    type: 'MARKDOWN',
                    title: "❌ 构建失败: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    atAll: true,  // 失败时 @所有人
                    text: [
                        "### ⚠️ API 自动化测试构建失败",
                        "---",
                        "**项目**: ${env.JOB_NAME}",
                        "**构建号**: ${env.BUILD_NUMBER}",
                        "**失败阶段**: ${env.STAGE_NAME}",
                        "**Git 提交**: ${env.GIT_COMMIT?.take(7)}",
                        "**查看详情**: [控制台日志](${env.BUILD_URL}console)",
                        "---",
                        "🔴 请立即检查代码或联系 DevOps 工程师"
                    ].join("\n")
                )
                
                // 2. 邮件失败通知
                emailext(
                    subject: "❌ 构建失败: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """
                        <h2 style="color: #e74c3c;">API 自动化测试构建失败</h2>
                        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
                            <tr><td style="background-color: #f2f2f2;"><b>项目名称</b></td><td>${env.JOB_NAME}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>构建编号</b></td><td>${env.BUILD_NUMBER}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>失败阶段</b></td><td>${env.STAGE_NAME}</td></tr>
                            <tr><td style="background-color: #f2f2f2;"><b>错误日志</b></td><td><a href="${env.BUILD_URL}console">点击查看控制台</a></td></tr>
                        </table>
                        <p style="color: #c0392b;"><b>动态容器已销毁，需手动重跑构建调试。</b></p>
                    """,
                    to: "${EMAIL_RECIPIENTS}",
                    mimeType: 'text/html'
                )
            }
        }
        
        unstable {
            echo "⚠️ 构建状态不稳定（有测试用例失败但未阻断流水线）"
        }
    }
}