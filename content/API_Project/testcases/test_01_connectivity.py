import pytest
from utils import type_parse
from api import HttpbinAuthService,HttpbinCoreService

@type_parse(core_service=HttpbinCoreService)
def test_network_connectivity(core_service): 
    result=core_service.get_ip()
    assert "origin" in result
    assert len(result['origin'].split('.'))==4
    print(f"\n当前IP: {result['origin']}")


@type_parse(core_service=HttpbinCoreService)
def test_delay_endpoint(core_service): 
    '''为什么需要先写insert'''
    pass