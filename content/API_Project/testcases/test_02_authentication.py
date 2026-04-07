import pytest
from utils import type_parse
from api import HttpbinAuthService, HttpbinCoreService


@type_parse(auth_service=HttpbinAuthService)
def test_bearer_token_propagation(auth_service):
    '''
    测试Token是否被正确传递到服务器
    '''
    token = 'test-token-12345-abcde'
    # token是英文或者数字
    result = auth_service.bearer_auth_check(token)
    # bearer_auth_check该方法其实就是更改发送的headers中Authorization的值

    # 通过返回值来验证是否收到传递的token
    headers = result['headers']
    # result的返回值，在headers中的accept已经定义application/json
    assert 'Authorization' in headers
    assert headers['Authorization'] == f'Bearer {token}'
    # 这两个assert用于判断结果


@type_parse(auth_service=HttpbinAuthService)
def test_basic_authentication(auth_service):
    '''
    测试基础认证
    '''
    result = result = auth_service.basic_auth_login()
    # 只是为了验证是否具有用户认证能力，下次可以改为数据驱动方式的认证
    assert result['authenticated'] is True
    assert result['user'] == 'admin'