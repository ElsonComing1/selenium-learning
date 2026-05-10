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
        EMAIL_RECIPIENTS = '19015437827@163.com,206432984@qq.com,2567195697@qq.com'  // 修改为你的邮箱
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
        // Stage 2: 构建测试镜像（国内缓存加速）
        // --------------------------------------------------
        stage('Build Test Image') {
            steps {
                // script是因为内部会使用groovy代码
                script {
                    // 切换当前工作目录，后续所有工作路径均在当前路径下
                        dir('content/API_Project') {
                        echo ">>> 正在构建测试镜像: ${TEST_IMAGE}"
                        
                        // sh指shell脚本，"""支持多行，不可以三个单引号"""
                        // --no-cache 强制重新安装依赖，避免缓存导致新包漏装
                        // --no-cahce牺牲速度来提高正确性
                        sh """
                            docker build \
                                --no-cache \
                                --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
                                -t ${TEST_IMAGE} \
                                -f Dockerfile.test \
                                .
                        """
                        
                        // 铁证校验：镜像内必须有 yaml 模块
                        sh """
                            docker run --rm ${TEST_IMAGE} python -c "import yaml; print('PyYAML version:', yaml.__version__)" || { echo "ERROR: 镜像内缺少 PyYAML"; exit 1; }
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
                        
                        sh """
                            docker rm -f ${TEST_CONTAINER} || true
                            
                            echo ">>> [Master] 本地文件铁证:"
                            ls -la content/API_Project/conftest.py || { echo "ERROR: Master 内无 conftest.py"; exit 1; }
                            
                            echo ">>> [Dynamic] 启动容器并执行测试..."
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
                        // --tb=short 失败是只打印精简的Traceback；-rA测试结束后打印所有结果的摘要
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
                    // groovy定义局部变量，存储allure结果目录
                    def resultsExist = sh(returnStatus: true, script: "find ${allureDir} -type f 2>/dev/null | grep -q .")
                    // 有文件返回0，无文件返回1（但是会报错），returnStatus: true的存在是为了避免程序崩溃。
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
                    // 
                }
            }
        }
    }
    
    // --------------------------------------------------
    // Post 构建处理：通知与清理（无论成败都执行）
    // --------------------------------------------------
    post {
        always {
            // ✅ 构建结束后安全清理，保留 allure-results 用于报告
            cleanWs(
                cleanWhenNotBuilt: false,
                deleteDirs: true,
                notFailBuild: true,
                patterns: [
                    [pattern: '**/__pycache__/**', type: 'INCLUDE'],
                    [pattern: '**/.pytest_cache/**', type: 'INCLUDE'],
                    [pattern: '**/*.pyc', type: 'INCLUDE'],
                    [pattern: 'content/API_Project/report/allure-results/**', type: 'EXCLUDE']
                ]
            )

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
                    robot: "DINGDING_CREDENTIALS",  // 使用凭证 ID；jenkins自己会用当前字符串去系统找对应的value
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
                    ]
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
                    robot: "DINGDING_CREDENTIALS",
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
                    ]
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
// jenkins下配置的凭证或者工具凭证，可以直接使用凭证名，不用${}写法
// --volumes-from jenkins-master-cicd 表示继承jenkins-master-cicd的全部挂载
// -w设置容器内的工作目录为项目的根目录

// 1.environment模块下是定义的环境变量是么？供当前pipeline下所有模块使用？这样类似的变量${BUILD_NUMBER}是jenkins自带的是么？
// environment下定义的是全局环境变量，供pipeline全局使用；而${BUILD_NUMBER}是jenkins内置变量；
// 不管自定义的变量还是jenkins内置变量均称呼为“环境变量”。
// | 内置变量               | 含义                                |
// | ------------------ | --------------------------------- |
// | `${BUILD_NUMBER}`  | 当前构建序号                            |
// | `${JOB_NAME}`      | 任务名称（如 `API-Automation-Pipeline`） |
// | `${WORKSPACE}`     | 当前工作空间绝对路径                        |
// | `${GIT_COMMIT}`    | 本次拉取的 Git commit hash             |
// | `${GIT_BRANCH}`    | 当前分支（如 `main`）                    |
// | `${env.BUILD_URL}` | 本次构建的 Jenkins URL                 |

// 2.直接输入字符串就能获取到credentials的值么？GITEE_CREDENTIALS = 'gitee-credentials'


// 3.options模块是设置jenkins下当前项目的参数是么？
// 配置的当前流水线的元数据，不是业务参数，不会影响jenkins全局或其他任务

// 4.stage可以写该模块的名字，那stages steps step可以么？
// stages > stage > steps;只有stage带阶段名字，没有step；steps下是具体步骤，script{多个步骤}；
// pipeline {
//     stages {           // ← 只能叫 stages，复数，包裹所有阶段
//         stage('A') {   // ← 叫 stage，单数，定义一个阶段
//             steps {    // ← 只能叫 steps，复数，包裹该阶段的所有步骤
//                 sh 'echo 1'   // ← 具体步骤指令，不写 step 关键字
//                 echo '2'      // ← 另一个步骤
//                 script { ... } // ← script 也是一个步骤
//             }
//         }
//     }
// }

// 5.script可以放在steps下，那可以放在step下么？以及script模块作用是啥，可以放多个linux指令么？
// script下是为了能够写groovy脚本，if/else;for;def 定义变量；try/catch;也能多个linux指令；

// 6.dir('content/API_Project')是切换当前工作目录是么？会不会创建？
// dir()只会切换，不会创建，不存在会报错；docker中地wordir会创建；

// 7.构建镜像，会将上下文.当前路径下的全部内容加入镜像么？-t参数是什么作用？以及为什么要加上--build-arg？--no-cache强制重新安装是安装啥，重新构建么？还是？
// // --no-cache 强制重新安装依赖，避免缓存导致新包漏装
//                         sh """
//                             docker build \
//                                 --no-cache \
//                                 --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple  \
//                                 -t ${TEST_IMAGE} \
//                                 -f Dockerfile.test \
//                                 .
//                         """
// 不会全部进入镜像，只是当前路径下，且镜像代码文件使用到的文件（COPY）才会构建进入镜像中。但是是全部文件传递给docker deamon进行筛选
// --build-arg PIP_INDEX_URL=url:想dockerfile.test文件传递构建是临时变量；-t tag标签的意思

// 8.为什么要加sh """"""，我能用''''''替代双引号么？sh是shell脚本意思，不用&&链接么？当前sh使用完毕后，会自己关闭么？一个sh就是一个终端么？不加sh直接指令能运行么？有什么区别？个人觉得下面代码有问题，前面执行完，一般是没问题的返回0,那么后面就肯定会执行，执行了，会提示镜像缺失pyyaml，但事实不缺失。应该改为，{ echo "镜像构建成功"; exit 1; }
// sh """
//                             docker run --rm ${TEST_IMAGE} python -c "import yaml; print('PyYAML version:', yaml.__version__)" || { echo "ERROR: 镜像内缺少 PyYAML"; exit 1; }
//                         """
// 三个双引号支持变量插值，而三个单引号不支持插值${},但是都支持多行，多行不是指令；
// sh """是shell脚本，因此可以多个指令，一个sh就是一个终端""""；&&用于连接多个指令echo && sh pipeline中没有，主要在docker file
// liunx的判断逻辑是0为true,1为false

// 9.要是前半段指令报错，那么后面就会保证程序正常是吧，为什么要加-f，此处是防御性变成是吧？我需要docker删除镜像 容器 卷的指令
// docker rm -f ${TEST_CONTAINER} || true
// -f启到一个强制删除作用，哪怕是运行中容器也无法逃脱命运。
// 删除容器
// docker rm 容器名 || true
// 删除镜像，构建没变化还是一样快的
// docker rmi 镜像名:标签 || true
// 删除卷（慎用）
// dcoker volume rm 卷名
// 删除垃圾
// docker system prune -a -f

// 10.--volumes-from jenkins-master-cicd能直接是容器名字么？-w参数作用？数据是存储在卷中是么？容器没了，但卷中数据还在。
// --volumes-from 继承容器的全部挂在卷，-w是设置容器启动后的工作路径。

// 11.一下两个参数作用？
// --tb=short \
//  -rA \
// 打印精简错误和测试全部结束后，答应一个摘要报告

// 12.这两句语法看不懂
// def allureDir = 'content/API_Project/report/allure-results'
// def resultsExist = sh(returnStatus: true, script: "find ${allureDir} -type f 2>/dev/null | grep -q .")
// 

// 13.这个构建报告是构建到哪里？谁来构建
// if (resultsExist == 0) {
//                         echo ">>> 发现 Allure 结果，生成报告..."
//                         allure([
//                             includeProperties: false,
//                             jdk: '',
//                             properties: [],
//                             reportBuildPolicy: 'ALWAYS',
//                             results: [[path: "${allureDir}"]]
//                         ])
//                     } else {
//                         echo "⚠️ 警告：未发现 Allure 结果，可能测试未生成或目录为空"
//                     }
// 由jenkins allure plugin构建，根据输入content/API_Project/report/allure-results/*.json，allure cli会处理，最后生成在临时目录，挂载至jenkins ui上

// 14.这是有条件的清理是么？**和EXCLUDE什么作用？
// cleanWs(
//                 cleanWhenNotBuilt: false,
//                 deleteDirs: true,
//                 notFailBuild: true,
//                 patterns: [
//                     [pattern: '**/__pycache__/**', type: 'INCLUDE'],
//                     [pattern: '**/.pytest_cache/**', type: 'INCLUDE'],
//                     [pattern: '**/*.pyc', type: 'INCLUDE'],
//                     [pattern: 'content/API_Project/report/allure-results/**', type: 'EXCLUDE']
//                 ]
//             )

// 15.此处的env是什么鬼？是wsl下的.env文件还是前面的environment变量？还是什么？
// ${env.JOB_NAME}"
// env是jenkins内置的groovy对象，包含当前构建的所有环境变量。

// 16.sh返回的状态码，0表示ture,其他表示有问题。

// pipeline script from scm