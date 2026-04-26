# test_01
import pytest
import allure
from utils import type_parse
from api import HttpbinAuthService, HttpbinCoreService


@allure.epic("API自动化")
@allure.feature("网络连接测试")
@allure.story("基础连通性检查")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("连通目的ip")
@allure.description(
    "用文字描述当前函数所做的事：通过endpoint=/ip和http协议+域名，构成url，访问url，同时获得返回内容，来验证访问成功"
)
@allure.step("基础连通性检查")
@allure.tag("network", "smoke", "负责人：张三")
@pytest.mark.network
@pytest.mark.smoke
# 通过pytest来设置模块，为了控制模块级运行
@type_parse(core_service=HttpbinCoreService)
def test_network_connectivity(core_service):
    with allure.step("step1：调用HttpbinCoreService类里的get_ip服务"):
        result = core_service.get_ip()
    with allure.step("step2：判断得到的返回值是否正确，依次来证明是连通的"):
        assert "origin" in result
        assert len(result["origin"].split(".")) == 4
        allure.attach(result["origin"], "当前出口IP", allure.attachment_type.TEXT)
        print(f"\n当前IP: {result['origin']}")


@allure.epic("API自动化")  # 项目 文件夹  可以重复
@allure.feature("网络连接测试")  # 功能模块  文件夹 可以重复
# 统一模块下，因此同名便于管理
@allure.story("基础连通性检查")  # 具体业务场景  文件夹  可以重复
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("延迟测试")  # 具体功能      文件
@allure.description("延迟测试：在规定时间后才能响应")
@allure.tag("network", "slow", "负责人：张三")
@pytest.mark.network
@pytest.mark.slow
@type_parse(core_service=HttpbinCoreService)
def test_delay_endpoint(core_service):
    """测试延迟接口"""
    with allure.step("step1：导入时间库"):
        import time

    with allure.step("step2：开始运行时间"):
        # 使用时导入，运行更快
        start = time.time()
    with allure.step("step3：开始调用"):
        result = core_service.test_delay(2)
    # 延迟2秒
    with allure.step("step4：测试耗时"):
        elapsed = time.time() - start
    with allure.step("step5：判断耗时是否在规定时间之后才响应"):
        assert elapsed >= 2.0
    with allure.step(f"step6：验证是否真的访问到目的ip:{result.get('origin',None)}"):
        # 确保真的延迟
        assert "origin" in result
        # 延迟接口也会返回ip


"""
将项目的父目录插入其中，为了能够找到对应模块
"""
