# test_03
import pytest
from utils import type_parse
from api import HttpbinAuthService, HttpbinCoreService

@type_parse(authenticated_core=HttpbinCoreService)
def test_submit_business_data(authenticated_core):
    """
    测试提交业务数据（POST）
    使用已认证的fixture
    """
    import time

    business_data = {
        "username": "bootcamp_trainee",
        "role": "qa_engineer",
        "time_stamp": time.strftime("%Y-%m-%d"),
    }

    result = authenticated_core.submit_data(business_data)

    # httpbin会回显提交的数据，为了验证是否提交成功
    assert result["json"] == business_data
    assert result["url"] == "http://httpbin.org/post"

@type_parse(authenticated_core=HttpbinCoreService)
def test_update_data_flow(authenticated_core):
    """
    测试更新流程（PUT）
    """
    update_data = {"user_id": 123, "status": "active", "level": 2}
    result = authenticated_core.update_data(update_data)
    assert result["json"]["level"] == 2
    assert result["json"]["status"] == "active"

@type_parse(authenticated_core=HttpbinCoreService)
def test_delete_operation(authenticated_core):
    """
    测试删除（DELETE）
    """
    result=authenticated_core.delete_resource()
    assert isinstance(result, dict)
    assert result.get("data") == ""  # DELETE请求的body为空
    assert result.get("url") == "http://httpbin.org/delete"
