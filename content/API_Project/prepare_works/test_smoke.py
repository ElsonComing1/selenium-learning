import requests,json,time

def test_httpbin_full_flow():
    '''
        硬编码测试：httpbin.org完整流程
        包含：IP查询 -> 认证 -> POST -> PUT -> DELETE -> 延迟测试
    '''
    base_url=r"http://httpbin.org"
    print("=" * 60)
    print("开始Phase 1 硬编码测试 - httpbin.org")
    print("=" * 60)

    # =========Step 1：基础连通性测试===========
    print("\n[Step 1] 获取请求IP (验证网络连通)...")
    ip_resp=requests.get(f"{base_url}/ip",timeout=5)
    assert ip_resp.status_code==200,f"网络不通{ip_resp.status_code}"
    json_result=ip_resp.json()
    print(f"✅ 网络通畅，你的ip：{json_result['origin']}")

    # =========Step 2：模拟认证（Bearer Token）===========
    print("\n[Step 2] 模拟认证（Bearer Token）...")
    token='bootcamp_token_123456'   
    headers={
        'Authorization':f'Bearer {token}',
        'Content-Type':'application/json',
        'Accept':'application/json',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
        'Cookie':''
    }

    # 访问受保护资源（httpbin会回显我们的Header）
    auth_resp=requests.get(f'{base_url}/headers',headers=headers,timeout=5)
    assert auth_resp.status_code==200,f"返回状态码:{auth_resp.status_code}不对"
    received_json=auth_resp.json()
    received_headers=received_json['headers']
    assert 'Authorization' in received_headers,"Token应该被服务器收到"
    print(f"✅ 认证通过，服务器收到:{received_headers['Authorization'][:20]}...")

    # ========== Step 3: 提交业务数据（POST）==========
    print("\n[Step 3] 提交业务数据（POST JSON）...")
    business_data={
        "username": "bootcamp_trainee",
        "role": "qa_engineer",
        "project": "api_automation",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    post_resp=requests.post(f'{base_url}/post',json=business_data,headers=headers,timeout=5)
    assert post_resp.status_code==200,"POST应该返回200"
    response_data=post_resp.json()
    assert response_data['json']==business_data,'服务器应该返回相同数据'
    print(f'  ✅ POST成功，服务器回显: {response_data['json']['username']}')
    print(f'     请求ID: {response_data['headers']['Host']}')
    print(f'all {response_data}')

    # ========== Step 4: 更新数据（PUT）==========
    print("\n[Step 4] 更新数据（PUT）...")
    update_data = {
        "username": "bootcamp_trainee",
        "role": "senior_qa_engineer",  # 升职了
        "level": 2
    }
    put_resp=requests.put(f"{base_url}/put",json=update_data,headers=headers,timeout=5)
    assert put_resp.status_code==200,"PUT应该返回200"
    put_result=put_resp.json()
    print(f'put_result:{put_result}')
    assert put_result['json']['role']=='senior_qa_engineer'
    print(f"  ✅ PUT成功，新职位: {put_result['json']['role']}")

    # ========== Step 5: 删除数据（DELETE）==========
    print("\n[Step 5] 删除数据（DELETE）...")
    delete_resp=requests.delete(f"{base_url}/delete",headers=headers,timeout=5)
    assert delete_resp.status_code == 200
    delete_result = delete_resp.json()
    assert delete_result['data']==''        # delete通常没有body
    print(f"  ✅ DELETE成功，服务器确认: {delete_result['url']}")

    # ========== Step 6: 基础认证测试（Basic Auth）==========
    print("\n[Step 6] 基础认证测试（Basic Auth）...")
    auther_user='admin'
    auther_pass='secret123'
    basic_resp =requests.get(
        f'{base_url}/basic-auth/{auther_user}/{auther_pass}',
        auth=(auther_user,auther_pass),     # requests自动处理basic auth编码
        timeout=5
        )
    print(f'basic_resp:{basic_resp.json()}')
    assert basic_resp.status_code == 200
    assert basic_resp.json()["authenticated"] is True
    assert basic_resp.json()["user"] == auther_user
    print(f"  ✅ Basic Auth成功，用户: {basic_resp.json()['user']}")

    # ========== Step 7: 性能测试（延迟接口）==========
    print("\n[Step 7] 延迟接口测试（模拟慢接口）...")
    delay_seconds=2
    start_time=time.time()
    delay_resp=requests.get(f'{base_url}/delay/{delay_seconds}',timeout=10)
    elapsed=time.time()-start_time

    assert delay_resp.status_code == 200
    assert elapsed >= delay_seconds, f"应该至少延迟{delay_seconds}秒"
    print(f"  ✅ 延迟接口正常，实际耗时: {elapsed:.2f}秒")

    # ========== 完成 ==========
    print("\n" + "=" * 60)
    print("🎉 Phase 1 完成！所有硬编码步骤跑通！")
    print("   下一步：开始 Phase 2 重构（三层架构）")
    print("=" * 60)
if __name__=="__main__":
    test_httpbin_full_flow()