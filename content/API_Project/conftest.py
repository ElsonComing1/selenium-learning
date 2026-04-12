# conftest.py
# 钩子函数需要放在fixture之前
# 添加自定义参数
import pytest


def pytest_addoption(parser):
    """
    添加命令行选项
    运行实例：pytest --env=production --env-file=config/env_settings.yaml
    """
    parser.addoption(
        "--env",
        action="store",
        default="production",
        help="测试环境：production/staging/development (默认: production)",
    )
    parser.addoption(
        "--env-file",
        action="store",
        default=None,
        help="配置文件路径，默认使用项目根目录下的 config/env_settings.yaml",
    )
    # 此钩子函数只用于增加命令行选项；对参数的具体修改需要其伙伴pytest_configure()


from config import log
from core import Config
import requests
import sys
from pathlib import Path

# 将 conftest.py 所在目录（即 API_Project）加入 Python 搜索路径
conftest_dir = str(Path(__file__).parent)
if conftest_dir not in sys.path:
    sys.path.insert(0, conftest_dir)


def pytest_configure(config):
    """
    配置初始化Config类，将命令行参数值赋值给该类的类变量
    注意：这个钩子函数会在所有测试收集前执行
    """
    # 获取命令行参数值
    env = config.getoption("--env")
    config_file = config.getoption("--env-file")

    # 处理默认配置文件路径
    if config_file is None:
        config_file = str(Path(__file__).parent / "config" / "env_settings.yaml")
        import os

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"该文件{config_file}不存在")

    Config.ENV = env
    Config.FILE = config_file

    # 记录到日志（此时 log 应该已经被导入）
    log.info(f"pytest_configure完成: 环境={Config.ENV}, 配置文件={Config.FILE}")


from api import HttpbinAuthService, HttpbinCoreService
from utils import common_exception

# # 在根目录级别，初始化日志，后面就可以直接使用log
# setup_logger()
# 由于在logger.py中，已经调用setup_logger且使用时已经导入log，此处就不再需要setup_logger()

import allure
# 测试失败处理
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
# tryfist是确保当有多个pytest_runtest_makereport被调用时，确保当前函数是第一个调用
# hookwrapper作用是确保在yield前后可以插入操作，而不是覆盖yield（测试函数）
def pytest_runtest_makereport(item, call):
    """
    item：是当前测试函数对象
    call：是测试执行阶段
    setup --> call --> teardown pytest_runtest_makereport是在这三个阶段均可以写入，且是yield前后
    而pytest_runtest_protocol是setup和teardown前后，先执行pytest_runtest_makereport，后执行pytest_runtest_protocol
    item.name 测试函数名字
    item.module 测试所在模块
    item.funcargs 测试函数接收的所有fixture参数
    item.cls 如果有类，则是所在的类
    """
    # 一般都是在每个阶段之后插入操作
    outcome = yield
    report = outcome.get_result()
    """
    report是单个测试报告对象，拥有以下属性：
    report.nodeid       测试id:"testcases/test_login.py::TestLogin::test_success"
    report.outcome      结果状态：passed failed skipper error
    report.location     文件路径和行号，如("testcases/test_login.py", 15, "test_success")
    report.longrepr     失败是详细的错误信息（tracebask+异常信息）
    report.duration     测试执行耗时
    report.when         执行阶段：“setup” “call” “teardown”
    report.sections     测试输出的分阶段信息（stdout stderr）
    report.keywords     测试标记 如{"test_success", "TestLogin", "pytestmark"}
    """
    if report.when == "call":
        # 确保是在测试函数执行阶段，而不是setup teardown阶段
        if hasattr(item, "funcargs"):
            # 防御性变成，确保测试对象，也即是测试函数，是有参数的
            for fixture_name, fixture_value in item.funcargs.items():
                # 识别 Service 类（假设都有 base_url 属性）
                if hasattr(fixture_value, "base_url") and hasattr(
                    fixture_value, "session"
                ):
                    context = (
                        f"Fixture:{fixture_name}\n"
                        f"Base URL:{fixture_value.base_url}\n"
                        f"Session Headers:{dict(fixture_value.session.headers)}"
                    )

                    allure.attach(context, name=f"请求上下文 - {fixture_name}")
                    # 不指定类型就是allure.attachment_type.TEXT
        if report.outcome in ("failed", "error"):
            # 但不是passed情况下上传相关日志
            log_dir = Path(__file__).parent / "logs"
            if log_dir.exists():
                log_files = list(log_dir.glob("*.log"))
                if log_files:
                    # 按照修改时间排序
                    latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                    allure.attach.file(
                        str(latest_log),
                        name="测试执行日志",
                        attachment_type=allure.attachment_type.TEXT,
                    )


from utils import Mysql_tool
from dotenv import load_dotenv
from config import common_varaints as cv
import os


@common_exception
@pytest.fixture(scope="session")
# 单独写出一个pool，原因是pool对应着会话级别，不需要不断地创建新的pool,不然太麻烦，也失去意义
def mysql_item():
    if not load_dotenv(dotenv_path=cv.ENV_FILE):
        log.info('成功加载mysql配置文件：{cv.ENV_FILE}')
        raise ValueError(f"该路径{cv.ENV_FILE}下，没能成功加载")

    mysql_item=Mysql_tool(host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        db=os.getenv('DB_NAME'),)
    log.info('成功创建mysql实例')
    yield mysql_item
    mysql_item.conn.rollback()
    log.info('成功回滚')
    mysql_item.close_connect()
    log.info('成功关闭连接')
    mysql_item.close_pool()
    log.info('成功关闭mysql pool')



@common_exception
@pytest.fixture(scope="session")
def api_session():
    """
    全局session（类似Selenium的driver_session）
    整个测试会话期间复用tcp连接，省去多次建立TCP连接环节
    """
    log.info("创建全局Session...")
    session = requests.Session()
    # 该会话被提出来是为了，更好的公用会话；虽是都是session级别，但是为了是在同一会话
    yield session
    session.close()
    log.info("全局Session关闭")
    # 一个session可以有多个服务，似一个浏览器对个标签


@pytest.fixture(scope="session")
def core_service(api_session):
    """
    使用同一个会话，来实现不同服务，当前是业务服务
    """
    service = HttpbinCoreService(api_session)
    # 实例化对象业务类，使用父类BaseApi构造
    # 夹具可以供夹具使用；只有被调用时才会创建
    return service


@pytest.fixture(scope="session")
def auth_service(api_session):
    """
    使用同一个session,创建不同服务，当前是认证服务
    """
    service = HttpbinAuthService(api_session)
    # 实例化认证类，通过基类BaseApi构造
    return service


@pytest.fixture(scope="function")
def authenticated_core(api_session):
    """
    已认证的core服务（每个测试函数独立，避免Token污染）
    不通用户拥有不同的临时权限
    """
    service = HttpbinCoreService(api_session)
    token = Config().get_config()["default_token"]
    service.set_auth_token(token)
    log.info(f"测试函数获取已认证实例，Token: {token[:10]}...")
    return service


@pytest.hookimpl(hookwrapper=True)
# 声明这是一个包装器钩子，通过yield在测试前后插入逻辑
# hookwrapper=True就是让该函数在yield前后操作是包裹，而不是覆盖。
def pytest_runtest_protocol(item, nextitem):
    """每个测试用例执行后自动换行"""
    # 也可以在测试执行前，插入操作
    yield  # 测试实际执行位置
    print()  # 在测试结束后输出空行


"""
Session 复用：省 TCP 连接（性能）
Service 分离：业务逻辑解耦（可维护）
authenticated_core 隔离：认证状态不串扰（稳定性）
"""
