"""
环境配置中心
httpbin.org 在国内有镜像，如果官方慢可切换
"""
from utils import common_exception

ENV = "production"  # 可以改一个文件的一个变量，切换不同环境

CONFIG = {
    'production':{
        'base_url':'http://httpbin.org',
        'timeout':5,
        'long_timeout':10,
        'auth':{
            'username':'admin',
            'password':'secret123'
        },
        'default_token':'bootcamp_token_123456'
    },
    'mirror':{
        'base_url':'http://httpbin.org',    # 国内镜像但地址一样
        'timeout':5,
        'long_timeout':10,
        'auth':{
            'username':'admin',
            'password':'secret123'
        },
        'default_tokne':'bootcamp_token_123456'
    }

}

@common_exception
def get_config():
    return CONFIG.get(ENV)


@common_exception
def get_base_url():
    return get_config()['base_url']

