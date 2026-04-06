from pathlib import Path
import sys
# 将 conftest.py 所在目录（即 API_Project）加入 Python 搜索路径
conftest_dir = str(Path(__file__).parent)
if conftest_dir not in sys.path:
    sys.path.insert(0, conftest_dir)

import pytest,requests
from api import HttpbinAuthService,HttpbinCoreService
from utils import setup_logger,common_exception,log
from config import get_config


# 在根目录级别，初始化日志，后面就可以直接使用log
setup_logger()

@common_exception
@pytest.fixture(scope='session')
def api_session():
    '''
        全局session（类似Selenium的driver_session）
        整个测试会话期间复用tcp连接，省去多次建立TCP连接环节
    '''
    log.info('创建全局Session...')
    session=requests.Session()
    yield session
    session.close()
    log.info('全局Session关闭')
    # 一个session可以有多个服务，似一个浏览器对个标签

@pytest.fixture(scope='session')
def core_service(api_session):
    '''
    使用同一个会话，来实现不同服务，当前是业务服务
    '''
    service=HttpbinCoreService(api_session)
    # 实例化对象业务类，使用父类BaseApi构造
    return service

@pytest.fixture(scope='session')
def auth_service(api_session):
    '''
    使用同一个session,创建不同服务，当前是认证服务
    '''
    service=HttpbinAuthService(api_session)
    # 实例化认证类，通过基类BaseApi构造
    return service

@pytest.fixture(scope='function')
def authenticated_core(api_session):
    '''
    已认证的core服务（每个测试函数独立，避免Token污染）
    不通用户拥有不同的临时权限
    '''
    service=HttpbinCoreService(api_session)
    token=get_config()['default_token']
    service.set_auth_token(token)
    log.info(f"测试函数获取已认证实例，Token: {token[:10]}...")
    return service
'''
Session 复用：省 TCP 连接（性能）
Service 分离：业务逻辑解耦（可维护）
authenticated_core 隔离：认证状态不串扰（稳定性）
'''