import pytest
from utils import setup_logger,common_exception,log


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
