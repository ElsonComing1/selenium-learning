# settings.py
"""
环境配置中心
httpbin.org 在国内有镜像，如果官方慢可切换
"""

ENV = "production"  # 可切换为 "mirror"（国内镜像）

CONFIG = {
    "production": {
        "base_url": "http://httpbin.org",  # 官方地址（你当前用的）
        "timeout": 5,
        "long_timeout": 10,  # 延迟接口用
        "auth": {
            "username": "admin",
            "password": "secret123"
        },
        "default_token": "bootcamp_token_123456"
    },
    "mirror": {
        "base_url": "http://httpbin.org ",  # 国内有镜像但地址一样，CDN不同
        "timeout": 5,
        "long_timeout": 10,
        "auth": {
            "username": "admin", 
            "password": "secret123"
        },
        "default_token": "bootcamp_token_123456"
    }
}

def get_config():
    """获取当前环境配置"""
    return CONFIG[ENV]

def get_base_url():
    return get_config()["base_url"]