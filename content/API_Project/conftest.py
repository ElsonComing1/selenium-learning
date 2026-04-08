# conftest.py
from config import get_config,  log
import requests
import pytest
from api import HttpbinAuthService, HttpbinCoreService
from utils import common_exception
from pathlib import Path
import sys
# 将 conftest.py 所在目录（即 API_Project）加入 Python 搜索路径
conftest_dir = str(Path(__file__).parent)
if conftest_dir not in sys.path:
    sys.path.insert(0, conftest_dir)


# # 在根目录级别，初始化日志，后面就可以直接使用log
# setup_logger()
# 由于在logger.py中，已经调用setup_logger且使用时已经导入log，此处就不再需要setup_logger()


@common_exception
@pytest.fixture(scope='session')
def api_session():
    '''
        全局session（类似Selenium的driver_session）
        整个测试会话期间复用tcp连接，省去多次建立TCP连接环节
    '''
    log.info('创建全局Session...')
    session = requests.Session()
    # 该会话被提出来是为了，更好的公用会话
    yield session
    session.close()
    log.info('全局Session关闭')
    # 一个session可以有多个服务，似一个浏览器对个标签


@pytest.fixture(scope='session')
def core_service(api_session):
    '''
    使用同一个会话，来实现不同服务，当前是业务服务
    '''
    service = HttpbinCoreService(api_session)
    # 实例化对象业务类，使用父类BaseApi构造
    # 夹具可以供夹具使用；只有被调用时才会创建
    return service


@pytest.fixture(scope='session')
def auth_service(api_session):
    '''
    使用同一个session,创建不同服务，当前是认证服务
    '''
    service = HttpbinAuthService(api_session)
    # 实例化认证类，通过基类BaseApi构造
    return service


@pytest.fixture(scope='function')
def authenticated_core(api_session):
    '''
    已认证的core服务（每个测试函数独立，避免Token污染）
    不通用户拥有不同的临时权限
    '''
    service = HttpbinCoreService(api_session)
    token = get_config()['default_token']
    service.set_auth_token(token)
    log.info(f"测试函数获取已认证实例，Token: {token[:10]}...")
    return service


@pytest.hookimpl(hookwrapper=True)
# 声明这是一个包装器钩子，通过yield在测试前后插入逻辑
# hookwrapper=True就是让该函数在yield前后操作是包裹，而不是覆盖。
def pytest_runtest_protocol(item, nextitem):
    """每个测试用例执行后自动换行"""
    # 也可以在测试执行前，插入操作
    yield       # 测试实际执行位置
    print()  # 在测试结束后输出空行


'''
Session 复用：省 TCP 连接（性能）
Service 分离：业务逻辑解耦（可维护）
authenticated_core 隔离：认证状态不串扰（稳定性）
'''