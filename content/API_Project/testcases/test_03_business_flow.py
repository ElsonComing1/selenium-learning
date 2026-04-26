# test_03
import pytest
import allure
from pathlib import Path
import json
from utils import type_parse,Json_tool
from api import HttpbinAuthService, HttpbinCoreService
from config import common_varaints as CV

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


def get_data():
    data_file=str(CV.TEST_CASES_FILE)
    json_item=Json_tool()
    return json_item.read_json_file(data_file)

@allure.epic("API自动化")
@allure.feature('核心业务流')
@allure.story('上传不同用户数据')
@allure.severity(allure.severity_level.NORMAL)
@allure.tag('data_driver','positive')
@pytest.mark.data_driver
@pytest.mark.positive
@pytest.mark.flaky(reruns=2,reruns_delay=2,only_rerun=AssertionError)
# 该处指定会覆盖终端命令行指令
# 指定测试函数且指定条件下，总共执行3次，两次重试，失败后会缓2秒；或者终端指令--reruns 2 --reruns-delay 2 --only-rerun requests.Timeout
@pytest.mark.parametrize('case',get_data(),ids=lambda x:x['case_id'])
# ids=lambda x:x['case_id']是将名字列入id中，显示出来，便于维护
def test_create_users_with_data(authenticated_core,case):
    # parametrize会自动将多个实例拆解成单个case
    allure.dynamic.title(f'{case["case_id"]}: {case["description"]}')
    allure.dynamic.description(f"输入参数: {Json_tool().translate_to_json(case['input'])}")
    with allure.step(f'step1：提交用户信息{Json_tool().translate_to_json(case["input"])}'):
        result = authenticated_core.submit_data(case["input"])
    
    with allure.step("step2：验证返回数据是否与提交数据一致"):
        # 断言失败时，Allure 会显示：TC001: 创建普通用户
        assert result["json"]["role"] == case["expected_role"]

# allure generate .\report -o .\report --clean 
# allure open .\allure-report