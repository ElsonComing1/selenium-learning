# conftest.py
# 钩子函数需要放在fixture之前
# 添加自定义参数
import pytest
def pytest_addoption(parser):
    '''
    添加命令行选项
    运行实例：pytest --env=production --config-file=config/env_settings.yaml
    '''
    parser.addoption(
        '--env',
        action='store',
        default='production',
        help='测试环境：production/staging/development (默认: production)'
    )
    parser.addoption(
        '--env-file',
        action='store',
        default=None,
        help='配置文件路径，默认使用项目根目录下的 config/env_settings.yaml'
    )
    # 此钩子函数只用于增加命令行选项；对参数的具体修改需要其伙伴pytest_configure()
from config import log
from core import Config
import requests
import sys

def pytest_configure(config):
    '''
    配置初始化Config类，将命令行参数值赋值给该类的类变量
    注意：这个钩子函数会在所有测试收集前执行
    '''
    # 获取命令行参数值
    env=config.getoption('--env')
    config_file=config.getoption('--env-file')

    # 处理默认配置文件路径
    if config_file is None:
        config_file = str(Path(__file__).parent / 'config' / 'env_settings.yaml')
        import os
        if not os.path.exists(config_file):
            raise FileNotFoundError(f'该文件{config_file}不存在')
        
    Config.ENV = env
    Config.FILE = config_file
    
    # 记录到日志（此时 log 应该已经被导入）
    log.info(f"pytest_configure完成: 环境={Config.ENV}, 配置文件={Config.FILE}")



from api import HttpbinAuthService, HttpbinCoreService
from utils import common_exception
from pathlib import Path
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
    token = Config().get_config()['default_token']
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
