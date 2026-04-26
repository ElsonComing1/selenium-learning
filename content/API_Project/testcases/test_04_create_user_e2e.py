# import pytest
# import requests
# import allure
# BASE_URL = "http://127.0.0.1:5000"


# @allure.epic('mysql_一致性')
# @allure.feature('api db数据一致性验证')
# @allure.story('api db数据一致性验证')
# @allure.severity(allure.severity_level.CRITICAL)
# @allure.title('数据一致性验证')
# @allure.description('先通过api提交数据，api会将数据存储至DB，测试端，再从DB获取内容与刚才提交的数据进行对比')
# @allure.tag('smoke','db_consistency','负责人：王麻子')
# @pytest.mark.db_consistency
# def test_create_user_e2e(mysql_item):
#     '''
#     测试端到端一致性
#     1. 调 API 创建用户
#     2. 立即查 MySQL 验证数据真的写入了
#     3. 比对 API 返回的 ID 和 DB 中的记录
#     通过api写入数据至数据库然后，通过api返回值与数据库中的值，进行比较是否一致
#     '''
#     payload={
#         'username':'test_elson_001',
#         'email':'elson@test.com'
#     }
#     with allure.step('step1：开始上传数据'):
#         resp=requests.post(f'{BASE_URL}/api/users',json=payload)
#     with allure.step('step2：判断返回状态'):
#         assert resp.status_code==201
#     with allure.step('step3：获取返回json数据'):
#         api_data=resp.json()
#     user_id=api_data['id']
#     with allure.step('step4：开始从数据库中提取数据，将与返回数据中的json数据，进行对比'):
#     # print(f"API 创建成功，返回 ID: {user_id}")
#         db_record=mysql_item.get_single('users','*','id',str(user_id))
#     with allure.step(f'step5：数据库中取出数据是：{db_record}'):
#         assert db_record is not None, f"DB 中找不到 ID={user_id} 的记录，API 说成功了但数据没落地！"
#     with allure.step(f'step6：判断名字是否一样,username:{db_record['username']}'):
#         assert db_record['username'] == payload['username']
#     with allure.step(f'step7：判断邮件是否一致：{db_record['email']}'):
#         assert db_record['email'] == payload['email']
#     with allure.step(f'step8：判断状态是否激活：{db_record['status']}'):    
#         assert db_record['status'] == 'active'  # 验证默认值
#     # print(f"✅ 一致性校验通过：API 返回 ID={user_id}，DB 记录匹配")

