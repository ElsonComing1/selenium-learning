### Docker 笔记

##### 1. 自动化docker常用指令：

dockerfile: 类比构造函数; 文本文件定义如何构建镜像（安装依赖, 复制代码等）; 源码用于构建image

Image: 类比类; 只读模板，包含操作系统+python+代码; image模板用于container实例

container: 类比实例; 镜像的运行态, 一个镜像可以跑多个运行态

docker是进程级别的隔离，以及环境不一致的问题，是生产 Image 的标准化工厂（CI/CD 流水线用）；而 写Dockerfile 是为了打包测试环境。

```python
'''
1. 镜像管理(Image)
    docker pull <镜像> : 拉去测试环境; eg: docker pull selenium/standalone-chrome:latest
    docker images : 查看本地拥有的镜像; eg: docker images | grep selenium
    docker rmi <image_id> : 删除指定镜像; eg: docker rmi abc123
    docker save -o xxx.tar <镜像> : 导出到指定镜像到指定位置同时命名(离线传输); eg: docker save -o selenium.tar selenium/standalone-chrome
    docker load -i xxx.tar : 导入镜像(内网传输); eg: docker load -i selenium.tar

2. 容器(Container; 实例具体唯一的)生命周期:
    1. 创建并启动: docker run 
        参数: 
        1. -d后台
        2. -p宿主机:容器 端口映射(单向: 宿主机 ---> 容器)
        3. -v宿主机:容器 挂载(实时双向同步变化)
        4. --name 给容器命名
        5. --rm 用完即删除
        eg: docker run -d -p 4444:4444 -v /dev/shm:/dev/shm --name selenium-hub/standalone-chrome
        容器名字必须唯一
    2. 启动: docker run
        format: docker start <name>
        eg: docker start selenium-hub 唤醒休眠的容器
    3. 停止: docker stop
        format: docker stop <name>
        eg: docker stop selenium-hub -t 10 -t是等待10s强制杀死; 没有-t是优雅关闭保存状态
    4. 重启: docker restart
        format: docker restart <name>
        eg: docker restart selenium-hub
    5. 删除: docker rm
        format: docker rm <name>
        eg: docker rm selenium-hub -f是强制删除, -v是连带卷一起删除, 连卷一起删除就是真的啥也没有了

3. 容器操作 (调试 | 监控) 
    1. 看日志: docker logs <container_name>
        eg: docker logs -f --tail 100 selenium-hub 实时查看selenium-hub容器的最后100行日志
    2. 进容器内部: docker exec -it <container_name> bash
        eg: docker exec -it selenium-hub bash 进入容器内部查看chromedriver是否再运行
    3. 查看详情: docker inspect <container_name>
        eg: docker inspect selenium-hub | grep IPAddress 查看容器IP, 将用于配置测试脚本
    4. 复制文件 docker cp container:路径 宿主机路径
        eg: docker cp selenium-hub:/var/log/selenium.log ./logs. 将指定容器内的日志拷贝至宿主机

4. 资源监控(排查性能问题)
    1. docker ps 查看运行中的容器; 类似ps -aux
    2. docker ps -a 看所有容器(含已停止); 类似 ps -aux含僵尸进程
    3. docker stats 实时查看容器 cpu/memory; 类似vmstat/top
    4. docker top <name> 查看容器内的进程; 类似top
      
5. 数据持久化(Volume)
    1. docker volume ls 查看全部数据卷, 容器删除, 卷还在
    2. docker volume rm <volume_name> 删除指定卷
    3. docker run -v 宿主机:容器 挂载

6. 网络(多容器协作)
    1. docker network ls 查看网络 bridge/host/none
    2. docker network create net-test 创建测试专用网络
    3. docker run --network net-test 指定容器加入网络(容器间互访)

7. 清理(磁盘满了急救)
    1. docker system df 查看docker占用多少磁盘
    2. docker system prune 删除所有未使用的数据(容器, 网络, 镜像, 卷) 很危险
    3. docker system prune -a 连带删除所有未运行的容器镜像 最危险
    4. docker container prune 只删除已停止的容器 
    5. docker volume prune 只删除未使用的卷 

8. 构建(dockerfile)
    1. docker build -t 镜像名:标签 . ; 构建指定当前目录的dockerfile
    2. docker build --no-cache -t mytest:v1 . 不用缓存, 强制重新构建
'''
```

##### 2. 安装部署

在windows环境下，通过安装wsl(windows subsystem for linux)内核可以让docker这个小汽车发挥更好的性能。

wsl和windows分别安装docker目的分别是c/s服务，wsl作为client，而windows作为server

- ##### 前置配置：让 WSL 连上 Windows 的 Docker

让docker desktop与wsl连接

![](../picturs/5.png)

- ##### 启动 Jenkins 容器

jenkins是一个CI/CD工具，用于把测试自动化的嵌入到开发过程中，是负责串联自动化步骤的中央调度器（智能控制执行步骤），**"测试自动执行器 + 报告生成器 + 团队协作中枢"**。

CI(continuous itegration)：持续集成，把提交的代码自动编译、打包、运行测试。

CD(continuous delivery/deployment)：持续交付/部署，测试通过后自动发布到测试环境或生产环境。

实际工作流程示例：

```bash
# 开发提交代码到 GitHub/GitLab
git push origin main

# Jenkins 自动触发 Pipeline：
1. 拉取最新代码（既有开发产品的代码，又有测试代码）
2. 构建 Docker 镜像（包含你的 pytest 环境）
3. 运行容器执行测试：pytest test_cases/ --alluredir=./allure-results
4. 生成 Allure 报告并归档
5. 发送钉钉/邮件通知：本次构建 20 条用例通过，2 条失败（附链接）
6. 如果测试通过，自动部署到测试环境；失败则阻止部署
测试代码是"考官"，产品代码是"考生"，测试环境是"考场"，生产环境是"正式舞台"。Jenkins 负责把"考生"送到"考场"考试，通过了再送到"舞台"表演。
测试代码是脚本（pytest文件），测试环境是服务器（运行产品（产品代码）的机器）。Jenkins 部署的是产品代码，不是测试代码。
```

| 测试类型                | 测什么                  | 工具                       | 你的 pytest 里的例子                                      |
| ----------------------- | ----------------------- | -------------------------- | --------------------------------------------------------- |
| **API 测试** (接口测试) | HTTP 接口（后端逻辑）   | `requests` 库、Postman     | `requests.get("http://api/login", json={"user":"admin"})` |
| **UI 测试** (E2E 测试)  | 浏览器页面（前端+后端） | Selenium、Playwright       | `driver.find_element(By.ID, "login").click()`             |
| **单元测试**            | 单个函数/类             | `pytest` + `unittest.mock` | `assert add(1,2) == 3`                                    |

```bash
开发提交代码
    ↓
单元测试（本地函数级）→ 集成测试（模块级）→ [部署到测试环境] 
    ↓
API 测试（接口级）→ UI 测试（你的 Selenium，用户级）
    ↓
部署到生产环境
```

| 阶段        | 名称         | 谁写       | 测什么                               | 是否需要部署                    |
| ----------- | ------------ | ---------- | ------------------------------------ | ------------------------------- |
| **第 1 层** | **单元测试** | 开发       | 单个函数/类（如 `calculator.add()`） | ❌ 不需要，本地直接跑            |
| **第 2 层** | **集成测试** | 开发/测试  | 模块间交互（如数据库连接、Redis）    | ❌ 通常用内存数据库（H2/SQLite） |
| **第 3 层** | **API 测试** | 测试（你） | HTTP 接口（REST API）                | ✅ **首次部署到测试环境**        |
| **第 4 层** | **UI 测试**  | 测试（你） | 完整用户流程（登录→搜索→下单）       | ✅ **测试环境已运行**            |

- **测试环境** = 部署**产品代码**的目标机器（服务器）
- **Jenkins** = 执行**测试代码**的调度器（运行你的 pytest 脚本）
- **Git** = 存储**测试代码**的仓库（Jenkins 从这里拉取）

```bash
Git 仓库（测试代码） 
    ↓ Jenkins 拉取
Jenkins 服务器（执行 pytest）
    ↓ HTTP/WebDriver 调用
测试环境服务器（运行产品）

触发时机：
开发提交产品代码 → Jenkins 自动拉取最新测试代码 + 部署产品 → 跑你的脚本
你提交测试代码 → Jenkins 验证脚本本身是否能跑通（冒烟）
```

##### 个人总结：

jenkins从git仓库中被触发，由于开发或者测试代码的提交；对开发提交的代码进行编译、单元测试、集成测试，最后测试通过部署到测试环境；而对测试提交的代码会触发对测试环境进行API测试和UI测试、不会进行部署到生产环境。最终的生产部署权在产品经理和运维手中，他们要基于产品代码测试结果。

**测试提交和开发提交都会触发 CI，但前者是验证脚本正确性，后者是验证产品功能，两者都不会直接触发部署到生产环境。**

```bash
docker run -d \	# 后台运行
--name jenkins \ # 对容器命名
-p 8080:8080 \	# 端口映射，不用宿主机和容器端口一致，已使用不可再使用；web使用
-p 50000:50000 \	# agent通信使用，一个服务功能对应一个port
-v ~/jenkins_home:/var/jenkins_home \	# 卷映射，可以写一个，但是容易脏；多个实现功能分离。
# Jenkins 配置、插件、Job 定义此时宿主机是wsl；宿主机 wsl ubuntu=命令中的宿主机
-v /var/run/docker.scok:/var/run/docker.sock \	# docker的权限控制，宿主机是docker desktop的转发；于上一指令宿主机不是同一个。wsl 底层=docker引擎的宿主机
--group-add $(stat -c '%g' /var/run/docker.sock) \ # 动态精准获取该文件的组id且将jenkins添加进去，赋权
jenkins/jenkins:lts	# 基于的jenkins镜像基础上实现容器，是将远程镜像拉至docker本地仓库
# -v 容器删除，配置还在。便于再次运行
```

换源：

![](../picturs/6.png)

docker desktop 提供docker，wsl在windows下，为docker容器提供宿主机，在linux基础上，创建docker容器性能更好。

##### 总结：

WSL2 为 Docker Desktop 提供了 Linux 内核运行环境，Docker 引擎是docker desktop的一部分，还有docker cli、docker compose，但需要linux环境，因此跑在 WSL2 里，容器跑在 Docker 引擎上。

docker desktop常用他的其中的GUI 看状态，适合可视化；WSL是用命令行操控Docker，适合自动化脚本；两者操作的是同一套容器，数据存在WSL2的虚拟磁盘中。

```bash
docker logs -f jenkins
# 等待看到 "Jenkins is fully up and running" 后，Ctrl+C 停止日志跟踪

# 获取密码
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
# 复制这串字符（如：a1b2c3d4...）
```

![](../picturs/7.png)

