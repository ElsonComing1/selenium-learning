# test_02
import pytest
import allure
from utils import type_parse
from api import HttpbinAuthService, HttpbinCoreService

@allure.epic("API自动化")
@allure.feature('认证授权模块')
@allure.story('Bearer Token认证')
@allure.severity(allure.severity_level.CRITICAL)
@allure.title('验证token正确传递服务器')
@allure.description("""
测试场景：验证通过set_auth_token设置的Token能否通过HTTP Headers正确传递到服务端
预期结果：
1. 请求头中包含Authorization字段
2. 字段值为Bearer + 传入的token
""")
@allure.tag('auth', 'security', '负责人：李四')
@pytest.mark.auth
@pytest.mark.security
@type_parse(auth_service=HttpbinAuthService)
def test_bearer_token_propagation(auth_service):
    '''
    测试Token是否被正确传递到服务器
    '''
    with allure.step('step1：可以获取动态token,当前是静态，实现不同token拥有不同的权限'):
        token = 'test-token-12345-abcde'
    with allure.step('开始传递token'):
        # token是英文或者数字
        result = auth_service.bearer_auth_check(token)
        # bearer_auth_check该方法其实就是更改发送的headers中Authorization的值
    with allure.step('step2：检查验证传递是否成功'):
        # 通过返回值来验证是否收到传递的token
        headers = result['headers']
        # result的返回值，在headers中的accept已经定义application/json
    with allure.step('step3：通过检查传递值，与返回值之间进行判断，是否一致'):
        assert 'Authorization' in headers
        assert headers['Authorization'] == f'Bearer {token}'
        # 这两个assert用于判断结果

@allure.epic("API自动化")
@allure.feature('认证授权模块')
@allure.story('Basic Auth认证')
@allure.severity(allure.severity_level.CRITICAL)
@allure.title('验证基础认证流程')
@allure.description('用户认证')
@allure.link("https://httpbin.org/#/Auth/get_basic_auth__user___passwd_ ",
             name="HttpBin Basic Auth文档")
@allure.tag('auth', 'security', '负责人：李四')
@pytest.mark.auth
@pytest.mark.security
@type_parse(auth_service=HttpbinAuthService)
def test_basic_authentication(auth_service):
    '''
    测试基础认证
    行为+验证
    '''
    with allure.step('step1：开始基础认证'):
        result = result = auth_service.basic_auth_login()
        # 只是为了验证是否具有用户认证能力，下次可以改为数据驱动方式的认证
    with allure.step('step2：验证基础认证'):
        assert result['authenticated'] is True
        assert result['user'] == 'admin'