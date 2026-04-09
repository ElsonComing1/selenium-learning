# test_03
import pytest
import allure
import json
from utils import type_parse
from api import HttpbinAuthService, HttpbinCoreService

@allure.epic("API自动化")
@allure.feature('核心业务流')
@allure.story('数据提交流程')
@allure.severity(allure.severity_level.BLOCKER)
@allure.title('业务数据提交测试')
@allure.description('通过核心方法提交数据')
@allure.tag('smoke', 'business', 'positive', '负责人：小三')
@pytest.mark.business
@pytest.mark.smoke
@type_parse(authenticated_core=HttpbinCoreService)
def test_submit_business_data(authenticated_core):
    """
    测试提交业务数据（POST）
    使用已认证的fixture
    """
    with allure.step('step1: 导入时间模块'):
        import time

        business_data = {
            "username": "bootcamp_trainee",
            "role": "qa_engineer",
            "time_stamp": time.strftime("%Y-%m-%d"),
        }
    with allure.step("step2: 构造业务数据"):
        allure.attach(json.dumps(business_data, indent=2,
                      ensure_ascii=False), "请求数据", allure.attachment_type.JSON)
    with allure.step("step3: 发送POST请求"):
        result = authenticated_core.submit_data(business_data)
    with allure.step("step4: 验证数据回显正确"):
        # httpbin会回显提交的数据，为了验证是否提交成功
        assert result["json"] == business_data
        allure.attach(json.dumps(
            result["json"], indent=2, ensure_ascii=False), '回显数据', allure.attachment_type.JSON)
    with allure.step("step5: 验证请求URL"):
        assert result["url"] == "http://httpbin.org/post"

@allure.epic("API自动化")
@allure.feature('核心业务流')
@allure.story('数据更新流程')
@allure.severity(allure.severity_level.CRITICAL)
@allure.title('全量更新接口测试')
@allure.description('通过核心方法提交数据')
@allure.tag('business', 'regression', '负责人：小三')
@pytest.mark.business
@pytest.mark.regression
@type_parse(authenticated_core=HttpbinCoreService)
def test_update_data_flow(authenticated_core):
    """
    测试更新流程（PUT）
    """
    update_data = {"user_id": 123, "status": "active", "level": 2}
    with allure.step("step1: 准备更新数据"):
        allure.attach(json.dumps(update_data, indent=2,
                      ensure_ascii=False), '更新内容', allure.attachment_type.JSON)
    with allure.step("step2: 执行PUT请求"):
        result = authenticated_core.update_data(update_data)
    with allure.step("step3: 验证level字段更新成功"):
        assert result["json"]["level"] == 2
    with allure.step("step4: 验证status字段更新成功"):
        assert result["json"]["status"] == "active"

@allure.epic("API自动化")
@allure.feature('核心业务流')
@allure.story('数据删除流程')
@allure.severity(allure.severity_level.CRITICAL)
@allure.title('资源删除接口测试')
@allure.description('验证DELETE请求能正确执行，并返回空data字段')
@allure.tag('business', 'regression', '负责人：小三')
@pytest.mark.business
@pytest.mark.regression
@type_parse(authenticated_core=HttpbinCoreService)
def test_delete_operation(authenticated_core):
    """
    测试删除（DELETE）
    """
    with allure.step("step1: 调用删除接口"):
        result = authenticated_core.delete_resource()
        allure.attach(json.dumps(result, indent=2, ensure_ascii=False),
                      '更新内容', allure.attachment_type.JSON)
    with allure.step("step2: 验证响应类型为字典"):
        assert isinstance(result, dict)
    with allure.step("step3: 验证data字段为空（DELETE无body）"):
        assert result.get("data") == ""  # DELETE请求的body为空
    with allure.step("step4: 验证URL正确"):
        assert result.get("url") == "http://httpbin.org/delete"