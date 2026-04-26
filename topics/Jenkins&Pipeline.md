### Jenkins&Pipeline

```groovy
// '''   
//     pipeline就是流水线，定义好的剧本，jenkins自动按照剧本执行步骤：
//     拉代码（不存）-->装依赖-->跑测试(开发提交的对测试环境（开发产品代码）的测试)-->发报告-->清理环境 = 自动化+流程化+可视化

//     groovy是java平台的“脚本化”语言，一种变成语言，运行在Java虚拟机（JVM）上，语法相似java；主要用于构建脚本 自动化和配置
//     Groovy = Java 的语法糖 + Python 的灵活性；对我只需要知道用groovy编程语言进行组织流程即可，实体还是我的python

//     groovy关键字学习：
//     Groovy/jenkins 语法             类似Java/Python的写法           作用
//     pipeline{}                      类定义                          声明这是一个流水线
//     stage{'名字'}                   函数调用                        定义一个阶段（如“编译”，“测试”）
//     step{}                          代码块                          某个阶段具体内容操作
//     sh '命令'                       os.system()                     执行shell命令(linux)
//     bat '命令'                      os.system()                     执行Windows cmd
//     echo 'xxx'                      print()                         打印日志



    
//     agent any                 // 固定：在哪跑（可换参数），是Jenkins 关键字（Keyword）
//     // any "随便哪台，有空的就来"（通常是 Master 或第一个可用 Agent）
//     // none 不指定，每个stage自己选
//     //  { label 'linux' } 必须是有 linux 标签的节点
//     //  { docker 'python:3.12' } 在 Docker 容器里跑（推荐）
    

// 固定模板：


// pipeline {
//     agent any
    
//     stages {
//         // 第1步：拉代码（浅克隆，不存历史）
//         stage('拉取代码') {
//             steps {
//                 // 方式1：直接拉（推荐）
//                 git branch: 'main', 
//                     url: 'https://github.com/yourname/your-project.git',
//                     shallow: true  // 浅克隆，只拉最新代码，节省空间
                
//                 // 方式2：如果是私有仓库，用凭证
//                 // git branch: 'main', 
//                 //     credentialsId: 'github-token', 
//                 //     url: 'https://github.com/yourname/your-project.git'
//             }
//         }
        
//         // 第2步：装依赖（每次干净安装）
//         stage('安装依赖') {
//             steps {
//                 sh 
//                 'python3 -m pip install --upgrade pip
//                  pip install -r requirements.txt --no-cache-dir'
                
                
//                 // 如果是 Docker 环境
//                 // sh 'docker build -t test-env:latest .'
//             }
//         }
        
//         // 第3步：跑测试（核心）
//         stage('执行测试') {
//             steps {
//                 sh '
//                     pytest test_cases/ \
//                         -v \
//                         --alluredir=allure-results \
//                         --html=report.html \
//                         --self-contained-html
//                 '
                
//                 // 生成测试数据（截图、日志等）
//                 sh 'mkdir -p artifacts && cp -r allure-results report.html artifacts/ || true'
//             }
//         }
        
//         // 第4步：发报告（你需要的详细代码）
//         stage('发送报告') {
//             steps {
//                 script {
//                     // 生成 Allure 报告（供网页查看）
//                     allure([
//                         includeProperties: false,
//                         jdk: '',
//                         results: [[path: 'allure-results']]
//                     ])
                    
//                     // 发邮件（带附件）
//                     emailext (
//                         to: 'team@company.com, ${env.CHANGE_AUTHOR_EMAIL}',
//                         subject: "${currentBuild.result == 'SUCCESS' ? '✅' : '❌'} 测试完成: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        
//                         // 附件：HTML报告、截图、日志、音频
//                         attachmentsPattern: '
//                             report.html, 
//                             allure-results/*.json, 
//                             **/screenshots/*.png, 
//                             **/recordings/*.mp3, 
//                             **/*.log
//                         ',
                        
//                         mimeType: 'text/html',
//                         body: """
//                             <h2 style='color:${currentBuild.result == "SUCCESS" ? "green" : "red"}'>
//                                 构建结果: ${currentBuild.result}
//                             </h2>
                            
//                             <p><b>项目:</b> ${env.JOB_NAME}</p>
//                             <p><b>构建号:</b> #${env.BUILD_NUMBER}</p>
//                             <p><b>提交人:</b> ${env.CHANGE_AUTHOR ?: 'N/A'}</p>
//                             <p><b>提交信息:</b> ${env.CHANGE_TITLE ?: 'N/A'}</p>
                            
//                             <hr/>
                            
//                             <h3>📊 报告链接</h3>
//                             <ul>
//                                 <li><a href="${env.BUILD_URL}allure/">Allure 详细报告</a></li>
//                                 <li><a href="${env.BUILD_URL}">构建控制台输出</a></li>
//                             </ul>
                            
//                             <h3>📎 附件说明</h3>
//                             <ul>
//                                 <li>report.html - 测试报告</li>
//                                 <li>screenshots/*.png - 失败截图</li>
//                                 <li>recordings/*.mp3 - 测试录音（如有）</li>
//                                 <li>*.log - 运行日志</li>
//                             </ul>
                            
//                             <p><i>此邮件由 Jenkins 自动发送，请勿回复</i></p>
//                         """
//                     )
//                 }
//             }
//         }
        
//         // 第5步：清理环境（临时文件）
//         stage('清理环境') {
//             steps {
//                 sh '
//                     # 清理 Python 缓存
//                     find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
//                     find . -type f -name "*.pyc" -delete 2>/dev/null || true
                    
//                     # 清理测试产生的临时文件（保留报告目录，post 会处理）
//                     rm -rf .pytest_cache/ 2>/dev/null || true
                    
//                     # 如果是 Docker 方式，清理临时容器
//                     # docker system prune -f 2>/dev/null || true
//                 '
//             }
//         }
//     }
    
//     // 最终保险：无论成功失败都清理（Always 块）
//     post {
//         always {
//             // 清理工作区（保留 artifacts 目录的话注释掉这行）
//             // cleanWs()
            
//             // 或者只清理特定目录
//             sh 'rm -rf allure-results/ __pycache__/ || true'
            
//             echo "流水线结束，环境已清理"
//         }
        
//         // 失败时额外通知（可选）
//         failure {
//             echo "测试失败，已保留现场数据供排查"
//             // 这里可以再加一个紧急通知给管理员
//         }
//     }
// }


// jenkins内置全局变量，jenkins运行自动注入，无需声明直接使用。
// currentBuild 对象：
//     currentBuild.result	                构建结果	SUCCESS/FAILURE/UNSTABLE/ABORTED/null
//     currentBuild.displayName	        显示名称	#5、#20250323-1
//     currentBuild.durationString	        持续时间	2 min 30 sec
//     currentBuild.number	                构建编号	5、23
//     currentBuild.absoluteUrl	        完整 URL	http://jenkins/job/test/5/
//     currentBuild.previousBuild.result	上次结果	SUCCESS
//     注意：result 在 post 块之前可能为 null，只有在构建结束后（post 阶段）才确定。

// env 对象：
//     Map（键值对），对应系统环境变量 + Jenkins 注入变量
//     env.JOB_NAME	    任务名称	            MyProject/TestPipeline
//     env.BUILD_NUMBER	构建序号	            5
//     env.BUILD_URL	    构建页面 URL	        http://localhost:8080/job/Test/5/
//     env.WORKSPACE	    工作区绝对路径	        /var/jenkins_home/workspace/Test
//     env.BRANCH_NAME	    分支名（多分支流水线）	 main、feature/login
//     env.GIT_COMMIT	    Git 提交哈希	        a1b2c3d...
//     env.GIT_URL	Git     仓库地址	            https://github.com/...
//     env.CHANGE_AUTHOR	提交人（PR 场景）	    zhangsan
//     env.NODE_NAME	    执行节点名	            master、agent-1

// 其他常用全局对象：
// params	参数化构建参数	params.ENV、params.VERSION
// scm	    源码管理对象	scm.userRemoteConfigs[0].url
// manager	构建管理器	    manager.addShortText("Deployed")
// '''


pipeline {
    agent {
        label 'my-test-agent'
    }
    
    environment {
        DISPLAY = ':99'
        // DISPLAY是linux系统变量，这样设置让代码中的selenium知道，在哪儿显示，假屏幕
    }
    
    stages {
        stage('检出代码') {
            steps {
                // 克隆代码到 /app（WORKDIR）
                sh '''
                    git clone https://github.com/ElsonComing1/selenium-learning.git .
                    ls -la
                '''
            }
        }
        
        stage('启动虚拟显示') {
            steps {
                sh '''
                    Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
                    sleep 1
                '''
            }
        }
        
        stage('执行测试') {
            steps {
                // 注意路径：content/day06/
                sh """
                    cd content/day06
                    ls -alh
                    python -m pytest test_cases/TestBaiduPOM.py \
                        -v \
                        --alluredir=./allure-results \
                """
            }
        }
        
        stage('生成报告') {
            steps {
                
                allure([
                    includeProperties: false,   // 是否在报告中包含环境变量等属性文件
                    jdk: '',    // Pipeline DSL 语言，留空，默认系统jdk
                    results: [[path: 'content/day06/allure-results/']] // allure 原始数据目录
                ])
                // allure 执行位置jenkins master
            }
        }
        // 无论在哪一个stage还是step，一个sh就是一个进程，在不同的终端，起始目录规定在WORKDIR中
        // 每一个sh命令是默认在WORKDIR根目录下
    }
    
    post {
        always {
            sh 'pkill Xvfb || true'
            cleanWs()
        }
    }
}

// 是使用jenkins在CI/CD,借助dokcer能够提供容器的特点，来完成任务。
// jenkins的master调度安排一切。报告也是master从容器中拿一份出来。
// 这些数据，不会影响windows github下的代码。而且动态容器也会使用完后还是构建完后就会删除。
// 但是镜像和volume还在。容器基于镜像构建。


```

