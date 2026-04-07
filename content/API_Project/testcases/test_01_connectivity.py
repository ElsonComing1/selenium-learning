import pytest
from utils import type_parse
from api import HttpbinAuthService, HttpbinCoreService


@type_parse(core_service=HttpbinCoreService)
def test_network_connectivity(core_service):
    result = core_service.get_ip()
    assert "origin" in result
    assert len(result['origin'].split('.')) == 4
    print(f"\n当前IP: {result['origin']}")


@type_parse(core_service=HttpbinCoreService)
def test_delay_endpoint(core_service):
    '''测试延迟接口'''
    import time
    # 使用时导入，运行更快
    start=time.time()
    result=core_service.test_delay(2)
    # 延迟2秒
    elapsed=time.time()-start
    assert elapsed >= 2.0
    # 确保真的延迟
    assert 'origin' in result
    # 延迟接口也会返回ip
    

'''
将项目的父目录插入其中，为了能够找到对应模块
'''