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

