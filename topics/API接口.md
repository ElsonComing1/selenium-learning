### API接口

#### 1. 基础知识

```python
'''
1. Pytest执行顺序：
    默认按照文件的书写顺序执行：把所有测试方法收集到一个队列（list）里，默认按收集顺序串行执行
    使用xdist多进程，无顺序，谁快谁先：把队列里的任务随机分配给多个 worker，谁先执行完谁领下一个，全局顺序是乱的
    pytest-order插件，可以指定测试文件方法顺序，方法默认从上至下，文件是动态的顺序
        @pytest.mark.order(1)
2. URL VS API
    URL: 统一资源定位，endpoint是URL一部分
    API: API = Endpoint + HTTP Method + Request/Response Schema(包含参数) + 业务逻辑
    URL: URL与API没关系；URL 是完整地址，是字符串地址；API 是"怎么敲门、怎么对话"的完整约定，是行为规范。
    Endpoint = URL 中的 Path 部分（如 /v1/robots/status），是资源定位。
    eg: 查询机器人状态
        URL: https://api.zhuimi.com/v1/robots/status（域名+endpoint1）
        method: GET
        params: device_id(string)
        返回: json {"voltage": 12.5, "status": "running"}
    
3.  post(增) delete(删) put(改) get(查):
    post(增):
        url=r'https://httpbin.org/post'     # 接口的url
        payload={
            "sn": "BOT20240223001",
            "test_result": "PASS",
            "voltage": 12.5
        }   # 接口的参数
        headers={"Content-Type": "application/json"}    # 接口的参数
        response=requests.post(url,json=payload,headers=headers)    # 返回内容
        适用范围：携带大量数据块，写入服务器，URL后缀不可见；更加安全

    delete(删):
        url = r'https://httpbin.org/delete'  # 接口的url
        params = {
            'device_id': 'BOT001',
            'force': 'true'  # 是否强制删除
        }  # 接口的参数
        headers = {
            "Authorization": "Bearer token123"  # 删除通常需要严格权限验证
        }  # 接口的参数
        response = requests.delete(url, params=params, headers=headers)
        # 或者不带参数：response = requests.delete(url, headers=headers)
        print(response.status_code)  # 200(成功) 或 204(成功且无返回体) 或 404(资源不存在)
        适用范围：从服务器永久移除数据，需要身份验证，防止误删


    put(改):
        url=r'https://httpbin.org/put' # 接口的url
        payload = {
                "device_id": "BOT001",
                "firmware_version": "v2.1.0",    # 完整的新数据
                "config": {
                    "speed": 100,
                    "sensitivity": 80
                }
            }  # 接口的参数（完整资源）
        headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer token123"  # 通常需要认证才能修改
            }  # 接口的参数
        response = requests.put(url, json=payload, headers=headers) # 返回内容
        # 查看结果
        print(response.status_code)  # 200 表示更新成功
        print(response.json())       # 返回更新后的完整资源
        适用范围：发送完整资源数据，覆盖服务器原有记录；通常要指定资源 ID，POST不需要

    get(查):
        url=r'https://httpbin.org/get'  # 接口的URL
        params={'device_id:'BOT001','station':'TEST'}   # 接口的参数
        response=requests.get(url,params=params)  # 发起请求后，服务器会响应返回response; 接口的请求方式和返回格式及内容
        适用范围：不适合敏感数据，有长度限制，url后面能看见参数值
    
    | 方法         | 操作 | 幂等性 | 参数位置     | 安全性     | 使用场景         
    | ----------   | --  | ---    | --------     | -----      | ------------ 
    | **POST**     | 增  | ❌ 否  | Body         | 高（隐藏） | 创建新资源，提交表单   
    | **GET**      | 查  | ✅ 是  | URL 后       | 低（暴露） | 查询数据，获取资源    
    | **PUT**      | 改  | ✅ 是  | Body         | 高（隐藏） | **全量更新**替换资源 
    | **DELETE**   | 删  | ✅ 是  | URL/Body     | 高         | 删除资源         

4. requests vs Session vs cookie
    三者连接递进关系：requests 是基础工具 → Session 是连接管理器 → Cookie 是身份凭证。

    requests:每次都是新tcp连接; 每次都要花费时间握手
    Session(服务器中，Session会将当前会话Id存入cookie放置在客户浏览器) session内部维护TCP连接池，避免重复建立连接
    适用场景：自动化测试、爬虫、API 客户端（需要保持登录状态）
    
    cookie(客户浏览器中，会有expire)

    第一次：客户端 → [握手] → 服务器 → 传数据 → [保持连接] (Session 会省去握手时间)
    requests.Session（客户端）：管理连接和存储 Cookie的工具
    服务器 Session（服务端）：服务器内存/Redis 里的用户数据（靠 Cookie 里的 ID 查找）,与上行的requests.Session不一样

5. Session 保持的是"对某个服务器（服务器对应一个域名）的连接"，不是"浏览器窗口"，也不是"某个固定 URL"。
    eg:
        import requests
        session = requests.Session()
        # 同一个服务器（httpbin.org），不同 URL 路径
        session.get("https://httpbin.org/get")      # 路径 /get
        session.get("https://httpbin.org/post")     # 路径 /post  
        session.get("https://httpbin.org/put")      # 路径 /put
        session.get("https://httpbin.org/delay/3")  # 路径 /delay/3
        # ✅ 以上 4 个请求，只发生 1 次 TCP 三次握手
        # ✅ 因为 Host 都是 httpbin.org
6. 文件层级导入关系与管理：
    1. 每一层都需要__init__.py用于暴露库；__all__=[str]白名单适用from module import *；无法避开指定导入
    2. 导入顺序：最先写0依赖，再写依赖少且是单向，依赖方向始终是单向，不可形成环形。
    3. python内部库（轻量库）以及第三方库（多为重量库）那个文件需要，显示导入，不可隐式导入（使用的变量来自前一个文件导入的库）；自定义库采用1 2方式构造
    4. 第三方库可以写在需要的业务库中；另外，当真正需要使用时，再导入=lazy 导入

7. API 接口采用Service Object Model(面向服务)
                 API测试            UI测试             loguru
    1 技术层     BaseAPI           BasePage            debug
    2 业务层     Service           BaiduPage           info
    3 测试层     Testcases         Testcases           info

8. 日志级别控制：
    技术层和业务层的logger分开；debug时，只要技术层；CI时，只要业务层。
    也就是运行时，配置不同的环境变量。设置三个loguru.add()放进终端一个，整体日志一个，提纯错误日志一个。通过LOG_LEVEL和detailed详细程度变量

9. API是接口端点，Service是业务模块封装，域名是服务器
    域名 (Domain)
    └── https://api.example.com
        ├── 用户服务 (User Service) ← 业务模块
        │   ├── POST   /api/users/login      ← API
        │   ├── POST   /api/users/register   ← API
        │   └── GET    /api/users/{id}       ← API
        │
        ├── 订单服务 (Order Service) ← 业务模块
        │   ├── POST   /api/orders           ← API (创建)
        │   ├── GET    /api/orders/{id}      ← API (查询)
        │   └── DELETE /api/orders/{id}      ← API (取消)
        │
        └── 支付服务 (Payment Service) ← 业务模块
            └── POST   /api/payments/charge  ← API
    
    一个域名下，有多个业务模块；一个业务模块下，有多个API；API=URL(域名+endpoint) + method + params + response
    业务模块=服务(Service)，一个服务指的就是业务模块(一组相关的API集合)。单个API叫"接口"或"API 端点（API Endpoint）"

    https://api.example.com:8080/api/v1/users/123?active=true&page=1
    \_____________________/  \_/ \______________/ \________________/
            Domain          Port  Path | Endpoint   params
    \______________________________________________________________/
                            (URI)

    URI = 只要能标识资源就行（范围最大）
    URL = 必须能定位资源（包含地址信息：http://...）
    URN = 只给名字，不给地址（通常用于持久化标识，如图书ISBN）

10. API测试概念
    ❌ 没有"页面"，只有 URL Endpoint
    ❌ 没有"元素定位"，只有 JSON 字段提取
    ❌ 没有"点击操作"，只有 HTTP 方法（GET/POST）

11. API流程：
    先拿到需要的资料；然后就是直截了当的编写核心的代码，看能不能通；再是重构代码（技术层 业务层 测试层）；最后就是优化维护代码。
    让使用人员改尽量少的文件，依次达到广泛适用

12. 变量规范化
    1. 模块变量集中管理
    2. 只在跨 try-except 访问时提前初始化，其他变量就近定义。
    3. 使用已定义变量（✅ DRY 原则）
    4. 环境变量 > 硬编码（12-因素应用法）
    5. 类型注解（Python 3.6+）
    6. 配置类封装（进阶）
    7. 避免全局变量污染
'''

'''
requests学习
    发请求（类似发诊断指令）→ 收响应（类似读诊断数据）→ 验结果（类似判断正/负响应）。

1. 请求构造类（发指令）
    1. Session级方法（保持会话）
    session=requests.Session()
    # 基础请求方法(所有方法都用的该方法)
    session.request(method='GET',url='',**kwargs)

    # 封装基础方法后的常用方法
    session.post(url,data=None,json=None,**kwargs)  # 写
    session.delete(url,**kwargs)            # 删除

    session.put(url,data=None)              # 更新资源
    session.patch(url,data=None,**kwargs)   # 局部修改

    session.get(url,params=None,**kwargs)   # 查
    
    session.head(url)           # 返回响应头，不下载body，检查文件是否存在以及大小
    session.options(url)        # 查看服务器支持哪些Http方法

    2. 请求参数(kwargs通用)
    # 查询参数
    params={"device_id":"BOT001","page":1}

    # 请求体(Body)三选一，不能混用；一个 HTTP 请求只有一个 Body
    data={"key":"value"}            # 表单格式(application/x-www-form-urlencoded)
    json={"key","value"}            # JSON格式(application/json最常用)
    files={"file":open("a.jpg")}    # 文件上传(multipart/form-data)
    data 和 files 可以混用（ multipart/form-data 允许文本字段和文件字段共存），但 json 和它们绝对不能混用。
    内部有检查逻辑，同时传会冲突（json 通常优先）

    # 请求头(headers)
    headers={
        "Authorization":"Bearer token123",   # 鉴权
        "Content-Type":"application/json",  # 内容类型
        "X-request-ID":"uuid-123"   # 链路追踪ID
    }

    # 超时控制
    timeout=5   # 总超时5
    timeout=(3.05,27)   # 元组：（连接超时，读取超时）

    # 其他高级参数
    allow_redirects=True    # 允许重定向
    verify=False        # 跳过SSL证书验证
    cert=('/path/cert.pem','/path/key.pem') # 双向SSL认证
    proxies={"http":"http://proxy:8080"}    # 代理（翻墙或者内网穿透）

2. 响应处理类（收数据）
    1. Response对象核心属性
    response = session.get("https://api.example.com/data")

    # 状态码
    response.status_code    # 200 ok, 404 not found, 500 server error
    response.ok             # 快捷判断：true if 200<=status_code<=400

    # 响应体(Body)三种状态
    response.text           # 字符串（适合普通html文本）
    response.content        # 字节流bytes(适合图片音频文件下载)
    response.json()         # json装python dict(最常用，API测试90%用这个)

    # 响应头(Headers)
    response.headers        # 字典，如{"Content-Type":"application/json"}
    response.headers.get('X-Requests-ID')   # 获取特定关键字

    # URL信息（避免重定向后，不知道具体URL）    
    response.url            # 最终访问的url
    response.history        # 重定向历史列表
    
    # 编码信息
    response.encoding       # 编码格式（utf-8），修改后会重新解析response.txt
    response.apparent_encoding  # 自动检测编码（不准确，慎用）

    2. response 方法(验证工具)
    # 状态码断言（一行搞定，失败异常）；如果是400-599 抛出HTTPError,包含详细信息
    response.raise_for_status()

    # 迭代读取（大文件流式处理，不占用内存）
    for chunk in response.iter_content(chunk_size=1024):
        process(chunk)

    # 行迭代（处理文本流）
    for line in response.lines():
        print(line.decode('utf-8'))

3. 异常处理类
    from requests.exceptions import (
        RequestException,      # 所有异常的父类（万能捕获）
        HTTPError,             # HTTP 4xx/5xx（raise_for_status 抛出的）
        ConnectionError,       # 网络连接失败（DNS 解析失败、拒绝连接）
        Timeout,               # 超时（分连接超时和读取超时）
        TooManyRedirects,      # 重定向过多（死循环）
        URLRequired,           # URL 必填但给了 None
        MissingSchema,         # URL 缺少 http:// 或 https://
        InvalidSchema,         # URL 协议不支持（如 ftp://）
        ChunkedEncodingError,  # 分块传输编码错误（网络中断）
        ContentDecodingError   # gzip/deflate 解压缩失败
    )

    # 使用示例（类似你 UDS 测试的 try-except）
    try:
        resp = session.post(url, json=payload, timeout=5)
        resp.raise_for_status()  # 检查 HTTP 状态码
        data = resp.json()
    except Timeout as e:
        # 类似诊断超时（ECU 无响应）
        print(f"请求超时: {e}")
        raise
    except ConnectionError as e:
        # 类似诊断仪物理连接断开
        print(f"连接失败，检查网络或服务器状态: {e}")
    except HTTPError as e:
        # 类似收到负响应码 0x7F
        print(f"服务器返回错误: {e.response.status_code}")
        print(f"错误详情: {e.response.text}")
    except RequestException as e:
        # 兜底捕获
        print(f"请求异常: {e}")
        
4. 重试策略
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    # 配置重试策略（类似 UDS 诊断的超时重发机制）
    retry_strategy = Retry(
        total=3,                    # 总共重试 3 次
        backoff_factor=1,           # 间隔时间：1s, 2s, 4s（指数退避）
        status_forcelist=[429, 500, 502, 503, 504],  # 遇到这些状态码才重试
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]  # 哪些方法允许重试
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)  # 给所有 https 请求挂载重试策略
    session.mount("http://", adapter)
'''
```

#### 2. HTTP API 功能测试

##### 1. 平台调研

###### 1. 平台地址（域名）：http://httpbin.org/



###### 2. 6个核心API端点（覆盖完整的测试场景）：

| HTTP   Method | Endpoint                    | 功能描述           | 请求示例                          | 响应特点                |
| ------------- | --------------------------- | ------------------ | --------------------------------- | :---------------------- |
| GET           | /ip                         | 获取请求ip         | 无                                | 返回请求者ip            |
| GET           | /headers                    | 获取请求头         | 无                                | 回显发送的Headers       |
| POST          | /post                       | 提交JSON数据       | {"name":"test"}                   | 返回提交的数据+响应头   |
| PUT           | /put                        | 全量更新           | {"job":"senior"}                  | 返回更新后的数据        |
| DELETE        | /delete                     | 删除资源           | 无                                | 返回删除确认            |
| GET           | /basic-auth/{user}/{passwd} | 基础认证           | Header: Authorization: Basic xxx  | 401(失败)   / 200(成功) |
| GET           | /bearer                     | Bearer   Token认证 | Header: Authorization: Bearer xxx | 验证Token有效性         |
| GET           | /delay/{seconds}            | 延迟响应           | /delay/3                          | 延迟3秒后返回           |



###### 3. 训练业务流程设计（模拟真实企业场景）：

```plain
获取IP(验证网络) ——> 携带Token访问受保护资源 ——> POST提交业务数据 ——> PUT更新数据 ——> DELETE清理数据 ——> 验证延迟接口性能
```



###### 4. 环境准备：

```txt
# file path: C:\Users\16531\Desktop\selenium-learning\content\API_Project\requirements.txt
requests==2.31.0
```

​		该requirements.txt文件需要不断更新，当需要其他第三库的时候，便于他人使用你的代码。

###### 5. 安装指令：

```bash
pip install -r C:\Users\16531\Desktop\selenium-learning\content\API_Project\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```



###### 6. 测试域名连通性验证：

```python
import requests
url='http://httpbin.org/ip'
response=requests.get(url)
response.raise_for_status()
print(response.status_code)
# 获取期望值200
# 执行结果
# PS C:\Users\16531\Desktop\selenium-learning> & D:\Python312\python.exe     c:/Users/16531/Desktop/selenium-learning/content/API_Project/verify_network_connectivity.py
# 200
```



##### 2. 探路期-硬编码跑通

​	目标：一个文件test_smoke.py，最原始的方式，跑通httpbin.org的全流程

```python
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
```

1. 所有方法均会返回json数据，包括delete

2. 经过NAT(Network Address translate)后，是互联网IP全球唯一；而本地的ipconfig是路由器下的。解决ip不够用问题。

3. 不通API返回的json数据字段不一样

4. HTTP请求=信封（headers）+信纸（body）

   常见headers字段：

   Authorization	身份凭证（我是谁）		与token一起使用

   Content-Type	信纸格式（告诉对方怎么看）

   User-Agent		客户端是谁（什么浏览器）

   Accept				期望返回格式（我要JSON还是HTML）

   Cookie				状态保持（维持登录会话）

5. Token是临时凭证（临时使用权限）

   ```json
   {
     "user_id": 10086,
     "username": "admin",
     "role": "qa_engineer",
     "exp": 1712222222  // 过期时间（关键！）
   }
   ```

6. Cookie有会话Cookie还有持久Cookie，后者关闭浏览器后，还能继续保持会话，存在硬盘。

7. Bearer Token vs Basic Auth

   Bearer Token是临时通行证，而后者是验证身份；前者不暴露密码。

8. 何时传headers参数

   默认是requests会自带headers参数，只有一下特俗需求才会显示传递

   | 场景                | 必须传的 Header                  | 示例                             |
   | ------------------- | -------------------------------- | -------------------------------- |
   | **需要登录**        | `Authorization`                  | Bearer Token                     |
   | **POST JSON 数据**  | `Content-Type: application/json` | `json=` 参数**自动帮你加**了     |
   | **要求返回 JSON**   | `Accept: application/json`       | 有些 API 默认返回 HTML，需要指定 |
   | **防爬虫/特殊标识** | `User-Agent`                     | 模拟浏览器访问                   |
   | **携带 Cookie**     | `Cookie`                         | 维持登录会话                     |

9. 延迟服务用途

   故意让服务器延迟响应，当前进程阻塞等待，用于验证超时机制，重试逻辑，验证用户体验。

##### 3. 筑路期 - 三层架构重构

###### 1. 框架

```bash

```

###### 2. 环境配置

```yaml
# CONFIG:
# :后面的值必须与冒号保持至少一个空格；关键字是变量，用缩进来表示关系
production:
  base_url: "http://httpbin.org"
  timeout: 5
  long_timeout: 10
  auth:
    username: "admin"
    password: "secret123"
  default_token: "bootcamp_token_123456"
mirror:
  base_url: "http://httpbin.org"
  timeout: 5
  long_timeout: 10
  auth:
    username: "admin"
    password: "secret123"
  default_token: "bootcamp_token_123456"
```

###### 3. 日志器配置

```python
import sys
from loguru import logger
from pathlib import Path

from .exceptionTools import common_exception
# 同层级导入模块必须.

test='你成功测试S'

@common_exception
def steup_logger():
    '''配置loguru'''
    # 清空日志器，避免串扰
    logger.remove()
    # 日志目录
    log_dir=Path(__file__).parent.parent / 'logs'
    # 确保日志目录存在
    log_dir.mkdir(exist_ok=True)
    # 错误日志目录
    error_log_dir=log_dir / 'error_logs'
    # 确保错误日志路径存在
    error_log_dir.mkdir(exist_ok=True)

    # 程序启动时生成固定时间戳
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f'httpbin_API_test_{run_id}.log'
    error_log_file=error_log_dir / f'httpbin_API_test_error_{run_id}.log'

    # 配置日志文件详细结构
    logger.add(
        str(log_file),
        level='DEBUG',
        format='{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {module:<20} | {function:<20} | {message}',
        # 设置时间 等级 文件名 函数|方法 日志消息
        # rotation='10MB',     # 日志轮转，每达到10MB开始清理旧日志
        retention=20,           # 只保留最近20个日志文件；同时满足，既可以非固定的日志文件名，又可以控制文件数量，防止日志爆炸
        encoding='utf-8'        # 防止乱码
    )

    # 控制台日志配置
    logger.add(
        sys.stderr,         # 输出至控制台
        level='INFO',       # 只显示比>=INFO级别的信息，INFO WARNING ERROR SUCCESS
        format='''
        <green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{module:<20}</cyan> | {function:<20} | {message}''',
        # 进行颜色设置
        colorize=True
    )

    # 错误日志提纯
    logger.add(
        str(error_log_file),
        level='ERROR',      # 必须大写
        format='{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {module:<20} | {function:<20} | {message}',
        retention=20,           # 只保留最近20个日志文件；同时满足，既可以非固定的日志文件名，又可以控制文件数量，防止日志爆炸
        encoding='utf-8'        # 防止乱码
    )
    return logger

```

###### 4. 基础层（技术层）

```python
import requests

from config import get_config, get_base_url, log


class BaseApi:
    """
    HTTP 基础封装类
    职责：管理网络连接，不管业务逻辑
    """

    def __init__(self, session: requests.Session = None):
        # 获取环境，然后实例化
        self.base_url = get_base_url
        self.config = get_config
        # 当根目录级别没有创建session就会自动使用or后面创建session确保成功
        self.session = session or requests.Session()

        # 设置当前会话的请求头
        self.session.headers.update(
            {
                "Accept": "application/json",  # 设置当前接受返回的数据格式为json
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0",
                # 设置当前会话的客户端使用的浏览器是什么
            }
        )
        # update可以一次改多个值
        log.info(f"BaseApi初始化完成，目标: {self.base_url}")

    def _request(self, method: str, endpoint: str, **kwargs):
        """
        统一请求方法
        :param method: POST/PATCH/DELETE/PUT/GET
        :param endpoint: 如 '/ip'，'/post'
        :param kwargs: json,params,headers,timeout等
        :return: dict（解析后的JSON）
        """
        url = rf"{self.base_url}{endpoint}"

        # 设置超时（如果没有传值就用默认值）
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.config["timeout"]
        log.debug(f"[HTTP] {method} {url}")
        # 技术层是debug 不是info

        try:
            response = self.session.request(method, url, **kwargs)
            # 400-599会自动报错，程序会停止
            response.raise_for_status()

            # 处理204 No content(DELETE借口)
            if response.status_code == 204:
                return {}
                # 返回空内容，因为该对应接口已经删完数据

            return response.json()
            # 处理DELETE方法，其余方法返回json数据

        except requests.Timeout as e:
            log.error(f"请求超时：{method} {url}")
            raise TimeoutError(f"接口{endpoint}超时") from e
            # TimeoutError(f'接口{endpoint}超时')整理一遍信息，再结合from e就可以保留堆栈信息，有可以显示翻译信息
        except request.HTTPError as e:
            log.error(f"HTTP错误{respnse.status_code}: {response.text[:200]}")
            raise RuntimeError(f"HTTP {response.status_code}: {response.text}") from e
        except Exception as e:
            log.error(f"请求异常{e}")
            raise e
            # 技术基础层，直接上抛问题

    def get(self, endpoint: str, params: dict = None, **kwargs):
        """GET请求"""
        return self._request("GET", endpoint, params=params, **kwargs)
        # _request中，没有params，但有**kwargs会被包含进去

    def post(self,endpoint:str,json_data:dict=None,**kwargs): 
        '''POST 请求（JSON格式）'''
        if 'headers' in kwargs:
            headers=kwargs.pop('headers',{})
            # 获取输入的headers
        headers.setdefault("Content-Type", "application/json")  
        # if 'Content-Type' not in headers:
        #     headers['Content-Type']='application/json'
        # 尊重用户选择
        return self._request('POST',endpoint,json_data=json_data,**kwargs)
        # 单个变量要在最前面，关键字变量紧接着后面，然后是**kwargs

    def put(self,endpoint:str=None,json_data:dict=None,**kwargs):
        '''PUT请求（全量更新）'''
        headers=kwargs.pop('headers')
        # 获取用户传入的值
        headers.setdefault({'Content-Type':'application/json'})
        # 设置默认值，但是有用户值，就会是用户值
        return self._request(endpoint,json_data=json_data,**kwargs)

    def delete(self,endpoint:str,**kwargs):
        '''DELETE请求'''
        return self._request(endpoint,**kwargs)

    def set_auth_token(self,token:str):
        '''设置bearer token(供Service层使用)'''
        self.session.headers.update({'Authorization':f'Bearer {token}'})
        # 对当前会话设置token，拿去临时权限
        log.debug(f"Token已设置: {token[:10]}...")
        # token在headers中
    
    def set_basic_auth(self,username:str,password:str):
        '''设置Basic Auth（requests会自动编码）'''
        self.session.auth=(username,password)
        # 单独列出
        log.debug(f'Basic Auth已设置: {username}')
        
```

​	Session 常用属性/配置知识补充：

| 属性          | 类型                | 作用                               | 示例                                                         |
| ------------- | ------------------- | ---------------------------------- | ------------------------------------------------------------ |
| **`auth`**    | `tuple`             | Basic Auth 账号密码                | `session.auth = ('user', 'pass')`                            |
| **`headers`** | `dict`              | **默认请求头**（所有请求自动带上） | `session.headers.update({'X-Token': 'xxx'})`                 |
| **`cookies`** | `RequestsCookieJar` | **会话保持**（自动管理 Cookie）    | 登录后自动携带，无需手动传                                   |
| **`params`**  | `dict`              | 默认查询参数（每次请求自动附加）   | `session.params = {'api_key': 'xxx'}`                        |
| **`verify`**  | `bool`              | SSL 证书验证开关                   | `session.verify = False`（慎用！）                           |
| **`proxies`** | `dict`              | 代理设置                           | `session.proxies = {'http': 'http://127.0.0.1:8080'}`        |
| **`timeout`** | `float/tuple`       | 默认超时时间                       | 注意：Session 没有直接的 timeout 属性，需通过 `request` 方法或自定义 Adapter |

###### 5. 业务层

```python
from api import BaseApi
from utils import log, type_parse
from config import get_config


class HttpbinCoreService(BaseApi):
    """
    httpbin 核心业务服务（IP查询、POST/PUT/DELETE、延迟）
    """

    def get_ip(self) -> dict:
        """获取请求IP"""
        log.info("查询当前IP...")
        return self.get("/ip")

    @type_parse("dict", param_name="data")
    def submit_data(self, data: dict):
        """
        提交JSON数据（POST）
        :param data:要提交的字典数据
        :return:服务器回显数据
        """
        log.info(f"提交数据：{data}")
        result = self.post("/post", json_data=data)
        return result

    @type_parse("dict", param_name="data")
    def update_data(self, data: dict = None) -> dict:
        """更新数据（PUT）"""
        log.info(f"更新数据：{data}")
        return self.put(endpoint="/put", json_data=data)

    def delete_resource(self) -> dict:
        """删除资源（DELETE）"""
        log.info("执行删除操作...")
        return self.delete(endpoint="/delete")

    @type_parse("int", param_name="seconds")
    def test_delay(self, secodns: int) -> dict:
        """
        测试延迟接口
        :params seconds 延迟秒数
        """
        log.info(f"测试延迟接口：{seconds}秒")
        # 使用长超时
        return self._request(
            method="GET", endpoint="/delay", timeout=get_config["long_timeout"]
        )

    def get_request_headers(self)->dict:
        '''获取服务器收到的请求头（用于调试认证）'''
        return self.get('/headers')


class HttpbinAuthService(BaseApi):
    '''
    httpbin 认证服务（Basic Auth、Bearer Token验证）
    '''
    def __init__(self,session=None):
        super.__init__(session)
        # BaseApi().__init__(session)
        self.credentials=get_config()['auth']

    def basic_auth_login(self)->dict:
        '''
        使用Basic Auth登录
        返回：认证结果（包含authenticated字段）
        '''
        user=self.credentials['username']
        password=self.credentials['password']

        log.info(f'尝试Basic Auth登录：{user}')

        # 先设置认证信息
        self.set_basic_auth(user,password)

        # 访问受保护资源
        result=self.get(endpoint=f'/basic_auth/{user}/{password}')
        return result

    @type_parse(cur_type='str',param_name='token')
    def bearer_auth_check(self,token:str=None)->dict:
        '''
        验证Bearer Token（通过查看服务器回显的Headers）
        '''
        if token:
            self.set_auth_token(token)

        result=self.get('/headers')
        return result
'''
    Basic Auth是“账号密码登录”，一次登录后面就不用再显示输入，当前会话一直保持；
    Bearer Token是“令牌验证”，效果同上
'''
```

###### 6. 根目录`conftest.py`

```python
# conftest.py
# 钩子函数需要放在fixture之前
# 添加自定义参数
import pytest
def pytest_addoption(parser):
    '''
    添加命令行选项
    运行实例：pytest --env=production --env-file=config/env_settings.yaml
    '''
    parser.addoption(
        '--env',
        action='store',
        default='production',
        help='测试环境：production/staging/development (默认: production)'
    )
    parser.addoption(
        '--env-file',
        action='store',
        default=None,
        help='配置文件路径，默认使用项目根目录下的 config/env_settings.yaml'
    )
    # 此钩子函数只用于增加命令行选项；对参数的具体修改需要其伙伴pytest_configure()
from config import log
from core import Config
import requests
import sys

def pytest_configure(config):
    '''
    配置初始化Config类，将命令行参数值赋值给该类的类变量
    注意：这个钩子函数会在所有测试收集前执行
    '''
    # 获取命令行参数值
    env=config.getoption('--env')
    config_file=config.getoption('--env-file')

    # 处理默认配置文件路径
    if config_file is None:
        config_file = str(Path(__file__).parent / 'config' / 'env_settings.yaml')
        import os
        if not os.path.exists(config_file):
            raise FileNotFoundError(f'该文件{config_file}不存在')
        
    Config.ENV = env
    Config.FILE = config_file
    
    # 记录到日志（此时 log 应该已经被导入）
    log.info(f"pytest_configure完成: 环境={Config.ENV}, 配置文件={Config.FILE}")



from api import HttpbinAuthService, HttpbinCoreService
from utils import common_exception
from pathlib import Path
# 将 conftest.py 所在目录（即 API_Project）加入 Python 搜索路径
conftest_dir = str(Path(__file__).parent)
if conftest_dir not in sys.path:
    sys.path.insert(0, conftest_dir)


# # 在根目录级别，初始化日志，后面就可以直接使用log
# setup_logger()
# 由于在logger.py中，已经调用setup_logger且使用时已经导入log，此处就不再需要setup_logger()

# 测试失败处理
@pytest.hookimpl(tryfirst=True,hookwrapper=True)
# tryfist是确保当有多个pytest_runtest_makereport被调用时，确保当前函数是第一个调用
# hookwrapper作用是确保在yield前后可以插入操作，而不是覆盖yield（测试函数）
def pytest_runtest_makereport(item,call):
    '''
    item：是当前测试函数对象
    call：是测试执行阶段
    setup --> call --> teardown pytest_runtest_makereport是在这三个阶段均可以写入，且是yield前后
    而pytest_runtest_protocol是setup和teardown前后，先执行pytest_runtest_makereport，后执行pytest_runtest_protocol
    item.name 测试函数名字
    item.module 测试所在模块
    item.funcargs 测试函数接收的所有fixture参数
    item.cls 如果有类，则是所在的类
    '''
    # 一般都是在每个阶段之后插入操作
    outcome=yield
    report=outcome.get_result()
    '''
    report是单个测试报告对象，拥有以下属性：
    report.nodeid       测试id:"testcases/test_login.py::TestLogin::test_success"
    report.outcome      结果状态：passed failed skipper error
    report.location     文件路径和行号，如("testcases/test_login.py", 15, "test_success")
    report.longrepr     失败是详细的错误信息（tracebask+异常信息）
    report.duration     测试执行耗时
    report.when         执行阶段：“setup” “call” “teardown”
    report.sections     测试输出的分阶段信息（stdout stderr）
    report.keywords     测试标记 如{"test_success", "TestLogin", "pytestmark"}
    '''
    if report.when == 'call':
        # 确保是在测试函数执行阶段，而不是setup teardown阶段
        if hasattr(item,'funcargs'):
            # 防御性变成，确保测试对象，也即是测试函数，是有参数的
            for fixture_name,fixture_value in item.funcargs.items():
                # 识别 Service 类（假设都有 base_url 属性）
                if hasattr(fixture_value,'base_url') and hasattr(fixture_value,'session'):
                    context=(f'Fixture:{fixture_name}\n'
                        f'Base URL:{fixture_value.base_url}\n'
                        f'Session Headers:{dict(fixture_value.session.headers)}')
                    import allure
                    allure.attach(context,name=f'请求上下文 - {fixture_name}')
                    # 不指定类型就是allure.attachment_type.TEXT
        if report.outcome in ('failed', 'error'):
            # 但不是passed情况下上传相关日志
            log_dir=Path(__file__).parent / 'logs'
            if log_dir.exists():
                log_files=list(log_dir.glob("*.log"))
                if log_files:
                    # 按照修改时间排序
                    latest_log=max(log_files,key=lambda x:x.stat().st_mtime)
                    allure.attach.file(str(latest_log),name='测试执行日志',attachment_type=allure.attachment_type.TEXT)



@common_exception
@pytest.fixture(scope='session')
def api_session():
    '''
        全局session（类似Selenium的driver_session）
        整个测试会话期间复用tcp连接，省去多次建立TCP连接环节
    '''
    log.info('创建全局Session...')
    session = requests.Session()
    # 该会话被提出来是为了，更好的公用会话
    yield session
    session.close()
    log.info('全局Session关闭')
    # 一个session可以有多个服务，似一个浏览器对个标签


@pytest.fixture(scope='session')
def core_service(api_session):
    '''
    使用同一个会话，来实现不同服务，当前是业务服务
    '''
    service = HttpbinCoreService(api_session)
    # 实例化对象业务类，使用父类BaseApi构造
    # 夹具可以供夹具使用；只有被调用时才会创建
    return service


@pytest.fixture(scope='session')
def auth_service(api_session):
    '''
    使用同一个session,创建不同服务，当前是认证服务
    '''
    service = HttpbinAuthService(api_session)
    # 实例化认证类，通过基类BaseApi构造
    return service


@pytest.fixture(scope='function')
def authenticated_core(api_session):
    '''
    已认证的core服务（每个测试函数独立，避免Token污染）
    不通用户拥有不同的临时权限
    '''
    service = HttpbinCoreService(api_session)
    token = Config().get_config()['default_token']
    service.set_auth_token(token)
    log.info(f"测试函数获取已认证实例，Token: {token[:10]}...")
    return service


@pytest.hookimpl(hookwrapper=True)
# 声明这是一个包装器钩子，通过yield在测试前后插入逻辑
# hookwrapper=True就是让该函数在yield前后操作是包裹，而不是覆盖。
def pytest_runtest_protocol(item, nextitem):
    """每个测试用例执行后自动换行"""
    # 也可以在测试执行前，插入操作
    yield       # 测试实际执行位置
    print()  # 在测试结束后输出空行


'''
Session 复用：省 TCP 连接（性能）
Service 分离：业务逻辑解耦（可维护）
authenticated_core 隔离：认证状态不串扰（稳定性）
'''
```

​	执行顺序保证：

1. 先跑 `core_service` 测试（确保网络通）

2. 再跑 `auth_service` 测试（确保能登录）

3. 最后跑 `authenticated_core` 测试（确保业务正常）

   不同Token代表着不通权限

###### 7. 测试层

1. `test_01_connectivity.py`

   ```python
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
   
   ```

2. `test_02_authentication.py`

   ```python
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
   ```

3. `test_03_business_flow.py`

   ```python
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
   ```

###### 8. pytest钩子函数执行逻辑

| 钩子函数                                             | 作用域       | 执行次数                                                | 执行时机                        | 核心用途                                           |
| :--------------------------------------------------- | ------------ | ------------------------------------------------------- | ------------------------------- | -------------------------------------------------- |
| ***`pytest_addoption(parser)`***                     | **Session**  | **1次**（最早）                                         | pytest 启动，解析**命令行**之前 | 添加**自定义命令行**选项（如 `--env=prod`）        |
| ***`pytest_configure(config)`***                     | **Session**  | **1次**                                                 | **配置对象**创建**后**          | 注册插件、**修改配置**、初始化全局资源             |
| ***`pytest_sessionstart(session)`***                 | **Session**  | **1次**                                                 | 测试会话**开始时**              | **建立数据库连接、启动测试环境**                   |
| `pytest_collection_modifyitems(config, items)`       | **Session**  | **1次**                                                 | 收集完**所有测试**用例后        | 用例**排序**、打标签、过滤用例                     |
| `pytest_generate_tests(metafunc)`                    | **Function** | **每个参数化函数1次**                                   | 生成测试参数时                  | 动态参数化（比 `@pytest.mark.parametrize` 更灵活） |
| ***`pytest_runtest_setup(item)`***                   | **Function** | **每个测试函数1次**                                     | 执行 `setup` **前**             | 准备测试数据、**mock 初始化**                      |
| ***`pytest_runtest_protocol(item, nextitem)`***      | **Function** | **每个测试函数1次**                                     | 包裹整个**测试生命周期**        | 控制测试执行流程、添加切面逻辑                     |
| `pytest_runtest_call(item)`                          | **Function** | **每个测试函数1次**                                     | 执行**实际测试代码**时          | 包裹测试函数执行（在 protocol 内部）               |
| ***`pytest_runtest_teardown(item, nextitem)`***      | **Function** | **每个测试函数1次**                                     | 执行 `teardown` **后**          | 清理资源（注意：**即使失败**也会执行）             |
| ***`pytest_runtest_makereport(item, call)`***        | **Function** | **每个阶段1次**（**setup/call/teardown** 各1次，共3次） | 每个阶段结束**后**              | **最常用**：生成报告、判断结果、失败截图           |
| ***`pytest_fixture_setup(fixturedef, request)`***    | **Fixture**  | **每个 fixture 1次**                                    | fixture 初始化**时**            | 修改 fixture 行为                                  |
| `pytest_fixture_post_finalizer(fixturedef, request)` | **Fixture**  | **每个 fixture 1次**                                    | fixture 销毁**后**              | fixture 清理验证                                   |
| ***`pytest_sessionfinish(session, exitstatus)`***    | **Session**  | **1次**（最后）                                         | **所有测试**结束后              | 生成报告、关闭连接、发送通知                       |

1. pytest_runtest_makereport(item,call)

   ```python
   @pytest.hookimpl(hookwrapper=True)
   def pytest_runtest_makereport(item, call):
       # call.when 告诉你当前是哪个阶段
       if call.when == "setup":
           print("【setup 阶段】无论成功失败都会进这里")
       elif call.when == "call":
           print("【实际测试执行阶段】这才是我们通常关心的")
           if call.excinfo is not None:
               print("测试失败了！可以在这里截图/记录日志")
       elif call.when == "teardown":
           print("【teardown 阶段】清理阶段，通常忽略")
   ```

   

2. web自动化截图

   ```python
   @pytest.hookimpl(hookwrapper=True)
   def pytest_runtest_makereport(item, call):
       outcome = yield
       report = outcome.get_result()
       
       # 只在实际测试(call)且失败时截图
       if call.when == "call" and report.failed:
           driver = item.funcargs.get('driver')  # 获取 fixture 中的 driver
           if driver:
               driver.save_screenshot(f"failed_{item.name}.png")
   ```

   

3. pytest_generate_tests与@pytest.mark.parametrize的关系

   ```python
   # @pytest.mark.parametrize 是声明式的
   # pytest_generate_tests 是编程式的，更早执行（收集阶段）
   
   # 动态参数化，无需在函数上加装饰器
   def pytest_generate_tests(metafunc):
       if "user_data" in metafunc.fixturenames:
           # 从数据库/文件读取参数
           metafunc.parametrize("user_data", [
               {"name": "张三", "age": 20},
               {"name": "李四", "age": 25}
           ])
   # 该部分学习pymsql时，需要深入学习
   ```

   

4. pytest_configure vs pytest_sessionstart

   | 对比项           | pytest\_configure   | pytest\_sessionstart |
   | ---------------- | ------------------- | -------------------- |
   | **执行顺序**     | 更早                | 较晚                 |
   | **主要用途**     | 注册插件、添加 mark | 建立连接、初始化资源 |
   | **测试用例收集** | 尚未开始            | 可能已完成收集       |
   | **Session 对象** | 正在创建            | 已完全可用           |

   **最佳实践**：

   - 配置类操作 → `pytest_configure`
   - 资源初始化（如创建 Session）→ `pytest_sessionstart`

###### 9. 钩子函数常用组合模版

1. 命令行传参 + 环境配置

   ```python
   # conftest.py
   import pytest
   
   def pytest_addoption(parser):
       """添加自定义命令行选项"""
       parser.addoption(
           "--env", default="test", 
           help="测试环境: test/staging/prod"
       )
   
   def pytest_configure(config):
       """读取选项并设置全局变量"""
       env = config.getoption("--env")
       # 可以存入 config.stash 或全局变量供后续使用
       config.stash["env"] = env
   
   @pytest.fixture(scope="session")
   def env_config(request):
       return request.config.stash["env"]
   ```

   

2. 用例自动打标签

   ```python
   def pytest_collection_modifyitems(config, items):
       """自动根据函数名添加标记"""
       for item in items:
           if "login" in item.nodeid:
               item.add_marker(pytest.mark.login)
           if "smoke" in item.name:
               item.add_marker(pytest.mark.smoke)
   ```

   口诀：

   ```bash
   Session 级最早：
     addoption → configure → sessionstart
   
   Function 级最密：
     setup → call → teardown（各配一个 makereport）
   
   收集阶段在中间：
     collect → generate_tests → modify_items
   
   结束收尾最重要：
     sessionfinish（资源不释放，运维来找你）
   ```

###### 10. 工具类

1. `json_tool.py`

   ```python
   import json
   from pathlib import Path
   class Json_tool(object):
       def read_json_file(self, file):
           if not Path(file).exists():
               raise
           with open(file, 'r', encoding='utf-8') as f:
               data = json.load(f)
               return data
   
       def write_json_file(self, file, data):
           if not Path(file).exists():
               raise
           with open(file, 'w', encoding='utf-8') as f:
               json.dump(data, f, indent=2, ensure_ascii=False)
   
       def append_data_to_json_file(self, file, data):
           if not Path(file).exists():
               raise
           with open(file, 'w+', encoding='utf-8') as f:
               json.dump(data, f, indent=2, ensure_ascii=False)
   
       def translate_to_dict(self, data):
           return json.loads(data)
   
       def translate_to_json(self, data):
           return json.dumps(data, indent=2, ensure_ascii=False)
   ```

2. `yaml_tool.py`

   ```python
   # yaml_tool.py
   import yaml
   
   class Yaml_tool(object):
       def read_yaml_file(self,file):
           with open(file, 'r', encoding='utf-8') as f:
               data = yaml.safe_load(f)
               return data
               # print(data)
   
       def write_yaml_file(self,data, file):
           with open(file, 'w', encoding='utf-8') as f:
               yaml.safe_dump(data, f, allow_unicode=True,
                           default_flow_style=False,
                           sort_keys=False)
   ```

3. `exceptionTools.py`

   ```python
   # exceptionTools.py
   import functools
   import inspect
   from typing import Dict, Any, Type
   
   
   def common_exception(func_main):
       @functools.wraps(func_main)
       def wrapper(*args, **kwargs):
           try:
               return func_main(*args, **kwargs)
           except Exception as e:
               # e 就是错误的内容
               raise e
   
       return wrapper
   
   
   def type_parse(**type_map: Type):
       """
       多参数类型检查器
       用法：
       @type_parse(id=int,name=str,price=float)
       def process(id, name, price):
           pass
       """
   
       def decorate(func):
           sig = inspect.signature(func)
           # 记录参数
           param_names = list(sig.parameters.keys())
           # 把参数做成列表
   
           # 回去被装饰函数的参数名称，构成一个列表
           @functools.wraps(func)
           def wrapper(*args, **kwargs):
               bound_kwargs = sig.bind(*args, **kwargs)
               # 将参数名称与参数值对应构成字典，但是有默认值的参数，且没有传递值，就需要使用apply_defaults进行使用默认值
               bound_kwargs.apply_defaults()
               # 没有默认值的形参是必传参数
               for param_name, expected_type in type_map.items():
                   if param_name not in param_names:
                       raise TypeError(f"参数{param_name}不存在函数签名中")
                   value = bound_kwargs.arguments[param_name]
                   # 检查类型（允许 None 跳过，除非类型是 type(None)）
                   if value is not None and not isinstance(value, expected_type):
                       raise TypeError(
                           f"参数 '{param_name}' 类型错误: "
                           f"期望 {expected_type.__name__}, "
                           f"实际得到 {type(value).__name__} (值: {value!r})"
                       )
               return func(*args, **kwargs)
   
           return wrapper
   
       return decorate
   
   
   def mysql_args_parse(func):
       @functools.wraps(func)
       def wrapper(*args,**kwargs):
           try:
               fun_name=func.__name__
               self=args[0]
               # 绑定参数自动处理位置参数和关键字参数
               sig=inspect.signature(func)
               bound=sig.bind(*args,**kwargs)
               bound.apply_defaults()  # 应用默认值
   
               # 获取参数值（无论怎么传递）
               argsments=bound.arguments
               table=argsments.get('table')
               columns=argsments.get('columns')
               enabled_commit=kwargs.get('enabled_commit',False)
   
               # 进行过滤
               if not table or not table.replace("_", "").isalnum():
                   raise ValueError(f"非法表名{table}")
               if fun_name in ('get_single','get_many','insert_many',):
                   if isinstance(columns, list) and columns != "*":
                       for column in columns:
                           if (
                               not isinstance(column, str)
                               or not column.replace("_", "").isalnum()
                           ):
                               raise ValueError(f"非法字段名: {column}")
                       fields = ",".join(columns)
                   else:
                       fields = "*"
               elif fun_name in ('insert_single','update_row','delete_row'):
                   pass
               else:
                   raise ValueError(f'当前函数名字{fun_name}不在使用范围内，你不能使用该装饰器')
   
               result= func(*args,**kwargs)
               # 重点，将被装饰函数的执行结果保存起来，不立即返回。
               # 否则后面的代码就不会执行了
               if enabled_commit:
                   self.conn.commit()
                   print(f"✅ 已自动提交事务")
               return result
           except Exception as e:
               raise e
       return wrapper
   
   ```

###### 11. 终端执行指令

```bash
# 执行指令
cd project
pytest -s -v --env=production --env-file=.\config\env_settings.yaml --alluredir=.\report --clean-alluredir .\testcases\

# 动态报告
allure serve .\report\

# 静态报告
allure generate .\report -o .\allure-report --clean
allure open .\allure-report
```

#### 3. 数据库一致性

##### 1. Mysql学习

###### 1. 数据库：

1. 进入数据库

   ```mysql
   mysql -u root -p
   ```

2. 显示数据库

   ```
   show databases;
   ```

3. 创建数据库

   ```mysql
   create database test_api_db character set utf8mb4 collate utf8mb4_unicode_ci;
   ```

4. 删除数据库

   ```mysql
   drop database test_api_db;
   ```

5. 选择数据库

   ```mysql
   use test_api_db;
   ```

6. 不推荐更改名字

###### 2. 表：

1. 显示表

   ```mysql
   show tables;
   ```

2. 创建表

   ```mysql
   CREATE TABLE if not exists departments (
       id INT AUTO_INCREMENT PRIMARY KEY COMMENT '部门ID',
       name VARCHAR(50) NOT NULL COMMENT '部门名称',
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP
   ) ENGINE=InnoDB COMMENT='部门表';
   
   -- 3. 子表：员工表（带外键）
   CREATE TABLE employees (
       id INT AUTO_INCREMENT PRIMARY KEY COMMENT '员工ID',
       name VARCHAR(50) NOT NULL COMMENT '姓名',
       department_id INT COMMENT '所属部门ID',
       salary DECIMAL(10,2) COMMENT '工资',
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
       
       -- 外键约束：部门删除时，所属员工自动删除（也可设为 SET NULL 保留员工）
   	CONSTRAINT fk_emp_dept
       FOREIGN KEY (department_id)
       REFERENCES departments(id)
       ON DELETE CASCADE
       ON UPDATE CASCADE
   ) ENGINE=InnoDB COMMENT='员工表';
   ```

3. 删除表

   ```
   drop table employees;
   ```

4. 更改表

   ```mysql
   alter table old_name RENAME TO new_name CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

###### 3. 数据：

 1. 增加数据

    ```mysql
    --增加单条数据
    insert into employees values ('技术部');
    --增加多数据
    insert into employees(name, department_id, salary)
    values
    ('张三', 1, 15000.00),   -- 技术部
    ('李四', 1, 12000.00),   -- 技术部
    ('王五', 2, 8000.00);    -- 销售部
    ```

 2. 删除数据

    ```mysql
    delete from employees where id=1;
    ```

 3. 改数据

    ```mysql
    update employees set name='Elson' where id=2;
    ```

 4. 查数据

    ```mysql
    select * from employees;
    ```

##### 2. pymysql学习

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

import pymysql
import os
from config import common_varaints as cv
from core import Config
from dotenv import load_dotenv
from utils import type_parse, mysql_args_parse
import datetime


class Mysql_tool:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = None,
        password: str = None,
        db: str = None,
    ):
        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db,
            charset="utf8mb4",
            autocommit=False,
            cursorclass=pymysql.cursors.DictCursor,
        )
        if password is None or user is None or db is None:
            raise ValueError(f"你输入的值中有不正确值，请你检查")
            # raise用于内部，上抛问题
            # assert 会触发对应的except类型;

        # autocommit用于测试时，手动提交，避免污染数据
        # pymysql.cursors.Dictcursor设置cursor的返回类型

    @mysql_args_parse
    @type_parse(table=str, columns=list | str, con_key=str, conditions=str)
    def get_single(
        self,
        table: str = None,
        columns: list | str = [],
        con_key: str = None,
        conditions: str = None,
    ):
        try:
            sql = (
                f"select {fields} from {table} where {con_key}=%s"
                if con_key and conditions
                else f"select {fields} from {table}"
            )
            # 只有值才是%s, 且永远是%s, 表名等就是字符
            cursor = self.conn.cursor()
            cursor.execute(sql, (conditions,))
            return cursor.fetchone()
            # 元组必须要有,
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    @type_parse(table=str, columns=list | str, con_key=str, conditions=str, number=int)
    def get_many(
        self,
        table: str = None,
        columns: list | str = None,
        con_key: str = None,
        conditions: str = None,
        number: int = 10,
    ):
        try:
            sql = (
                f"select {fields} from {table} where {con_key}=%s"
                if con_key and conditions
                else f"select {fields} from {table}"
            )
            cursor = self.conn.cursor()
            cursor.execute(sql, (conditions,))
            return cursor.fetchmany(number)
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @type_parse(table=str, values=dict)
    def insert_single(self, table: str = None, values: dict = None):
        # dict能明确顺序
        try:
            if not table.replace("_", "").isalnum():
                raise ValueError(f"非法表名{table}")
            fields = []
            data = []
            placeholders = []

            for key, value in values.items():
                if not key.replace("_", "").isalnum():
                    raise ValueError(f"非法字段{key}")
                fields.append(f"`{key}`")
                # 加反引号目的为了，避免关键字干扰
                data.append(value)
                placeholders.append("%s")
            fields_sql = ",".join(fields)
            placeholders_sql = ",".join(placeholders)
            sql = f"insert into `{table}` ({fields_sql}) values ({placeholders_sql})"
            cursor = self.conn.cursor()
            cursor.execute(sql, data)
            self.conn.commit()
            return cursor.lastrowid  # 返回自增ID
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    # @type_parse(table=str,columns=list[str],values=list[list|set]|set[list|set])
    def insert_many(self,table:str=None,columns:list[str]=[None],values:list[list|set]|set[list|set]=None):
        try:
            if not isinstance(values,(list,set)):
                # isinstance只能检查外层
                raise TypeError(f'你输入的参数类型不对，当前是{values.__class__}')
            if not columns or not values or len(columns)!=len(values[0]):
                raise ValueError(f'columns与values的长度不一致')
            placeholder_sql=','.join(['%s' for i in range(len(columns))])
            fields_sql=','.join([column for column in columns])
            sql=f'insert `{table}` ({fields_sql}) values ({placeholder_sql})'
            cursor=self.conn.cursor()
            cursor.executemany(sql,values)
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()


    @type_parse(table=str, set_key=str, new_value=str, con_key=str, con_value=str)
    def update_row(
        self,
        table: str = None,
        set_key: str = None,
        new_value: str = None,
        con_key: str = None,
        con_value: str = None,
    ):
        try:
            if not table.replace("_", "").isalnum():
                raise ValueError(f"非法表名{table}")
            if None in (set_key, con_key, con_value):
                raise ValueError(f"传递参数有空值")
            sql = f"update `{table}` set `{set_key}`=%s where `{con_key}`=%s"
            cursor = self.conn.cursor()
            cursor.execute(sql, (new_value, con_value))
            self.conn.commit()
            # 更改完数据后，需要提交数据
            return cursor.rowcount
            # 返回有几行被改
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @type_parse(table=str,con_key=str,con_value=str)
    def delete_row(self, table, con_key: str = None, con_value: str = None):
        try:
            if not table.replace('_','').isalnum():
                raise ValueError(f"非法表名{table}")
            if None in (con_key, con_value):
                raise ValueError(f"传递参数有空值")
            sql=f'delete from `{table}` where `{con_key}`={con_value}'
            cursor=self.conn.cursor()
            cursor.execute(cursor)
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    def close_connect(self):
        self.conn.close()


if __name__ == "__main__":
    load_dotenv(dotenv_path=str(cv.CONFIG_DIR / ".env"))
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT"))
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    db = os.getenv("DB_NAME")

    mysql_item = Mysql_tool(host=host, port=port, user=user, password=password, db=db)
    # print(mysql_item,type(mysql_item),mysql_item.__class__)
    data=[
        ['4','营业部',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['5','维护部',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    ]
    data = mysql_item.insert_many(table='departments',columns=['id','name','created_at'],values=data)
    mysql_item.close_connect()
    print(data)

```

##### 3. DBUtils连接池

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

import pymysql
import os
from config import common_varaints as cv
from core import Config
from dotenv import load_dotenv
from utils import type_parse, mysql_args_parse
import datetime
from dbutils.pooled_db import PooledDB


class Mysql_tool:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = None,
        password: str = None,
        db: str = None,
    ):
        # self.conn = pymysql.connect(
        #     host=host,
        #     port=port,
        #     user=user,
        #     password=password,
        #     database=db,
        #     charset="utf8mb4",
        #     autocommit=False,
        #     cursorclass=pymysql.cursors.DictCursor,
        # )
        # 使用PooledDB类，创建mysql连接池，池中会至少保存多少个，最多多少个，来使得进程或者线程更加便利
        # 创建池子
        self.pool = PooledDB(
            creator=pymysql,
            host=host,
            port=port,
            user=user,
            password=password,
            database=db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            mincached=2,  # 内存总至少得有两个连接进程活着
            maxcached=5,  # 最多只有5个进程被建立
            maxshared=0,  # 最多共享连接数，是线程之间，同一个进程能否被共享。建议0；否者适用于单线程的协程
            maxconnections=10,  # 最大连接数是只能为10个，也就是只能有十个进程或者线程会想用pool池
            blocking=True,  # 没吃上就等着
            maxusage=None,  # 连上使用次数是没有限制的
            setsession=[
                "SET SESSION wait_timeout=28800"
            ],  # 防止连接被mysql踢掉，用之前的setup
            ping=1,  # 避免拿到的连接是死的
        )
        # 从池子中，拿去一个连接
        self.conn = self.pool.connection()
        if password is None or user is None or db is None:
            raise ValueError(f"你输入的值中有不正确值，请你检查")
            # raise用于内部，上抛问题
            # assert 会触发对应的except类型;

        # autocommit用于测试时，手动提交，避免污染数据
        # pymysql.cursors.Dictcursor设置cursor的返回类型

    @mysql_args_parse
    @type_parse(
        table=str, columns=list | str, con_key=str, conditions=str, enabled_commit=bool
    )
    def get_single(
        self,
        table: str = None,
        columns: list | str = [],
        con_key: str = None,
        conditions: str = None,
        enabled_commit: bool = False,
    ):
        try:
            sql = (
                f"select {columns} from {table} where {con_key}=%s"
                if con_key and conditions
                else f"select {columns} from {table}"
            )

            # 只有值才是%s, 且永远是%s, 表名等就是字符
            cursor = self.conn.cursor()
            cursor.execute(sql, (conditions,) if con_key and conditions else None)
            return cursor.fetchone()
            # 元组必须要有,
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    @type_parse(
        table=str,
        columns=list | str,
        con_key=str,
        conditions=str,
        number=int,
        enabled_commit=bool,
    )
    def get_many(
        self,
        table: str = None,
        columns: list | str = None,
        con_key: str = None,
        conditions: str = None,
        number: int = 10,
        enabled_commit: bool = False,
    ):
        try:
            sql = (
                f"select {columns} from {table} where {con_key}=%s"
                if con_key and conditions
                else f"select {columns} from {table}"
            )
            cursor = self.conn.cursor()
            cursor.execute(sql, (conditions,) if con_key and conditions else None)
            return cursor.fetchmany(number)
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    @type_parse(table=str, values=dict, enabled_commit=bool)
    def insert_single(
        self, table: str = None, values: dict = None, enabled_commit: bool = False
    ):
        # dict能明确顺序
        try:
            if not table.replace("_", "").isalnum():
                raise ValueError(f"非法表名{table}")
            fields = []
            data = []
            placeholders = []

            for key, value in values.items():
                if not key.replace("_", "").isalnum():
                    raise ValueError(f"非法字段{key}")
                fields.append(f"`{key}`")
                # 加反引号目的为了，避免关键字干扰
                data.append(value)
                placeholders.append("%s")
            fields_sql = ",".join(fields)
            placeholders_sql = ",".join(placeholders)
            sql = f"insert into `{table}` ({fields_sql}) values ({placeholders_sql})"
            cursor = self.conn.cursor()
            cursor.execute(sql, data)
            # self.conn.commit()    # 装饰器完成是否提交
            # 由于只是测试，因此，多数是不需要提交的；如果需要提交需要改变参数值enabled_commit即可
            # 而且其fixture中，是常结合self.conn.rollback进行回滚，避免污染数据。
            return cursor.lastrowid  # 返回自增ID
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    # @type_parse(table=str,columns=list[str],values=list[list|set]|set[list|set])
    def insert_many(
        self,
        table: str = None,
        columns: list[str] = [None],
        values: list[list | set] | set[list | set] = None,
        enabled_commit: bool = False,
    ):
        try:
            if not isinstance(values, (list, set)):
                # isinstance只能检查外层
                raise TypeError(f"你输入的参数类型不对，当前是{values.__class__}")
            if not columns or not values or len(columns) != len(values[0]):
                raise ValueError(f"columns与values的长度不一致")
            placeholder_sql = ",".join(["%s" for i in range(len(columns))])
            fields_sql = ",".join([column for column in columns])
            sql = f"insert `{table}` ({fields_sql}) values ({placeholder_sql})"
            cursor = self.conn.cursor()
            cursor.executemany(sql, values)
            # self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    @type_parse(
        table=str,
        set_key=str,
        new_value=str,
        con_key=str,
        con_value=str,
        enabled_commit=bool,
    )
    def update_row(
        self,
        table: str = None,
        set_key: str = None,
        new_value: str = None,
        con_key: str = None,
        con_value: str = None,
        enabled_commit: bool = False,
    ):
        try:
            if not table.replace("_", "").isalnum():
                raise ValueError(f"非法表名{table}")
            if None in (set_key, con_key, con_value):
                raise ValueError(f"传递参数有空值")
            sql = f"update `{table}` set `{set_key}`=%s where `{con_key}`=%s"
            cursor = self.conn.cursor()
            cursor.execute(sql, (new_value, con_value))
            # self.conn.commit()
            # 更改完数据后，需要提交数据
            return cursor.rowcount
            # 返回有几行被改
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    @mysql_args_parse
    @type_parse(table=str, con_key=str, con_value=str, enabled_commit=bool)
    def delete_row(
        self,
        table,
        con_key: str = None,
        con_value: str = None,
        enabled_commit: bool = False,
    ):
        try:
            if not table.replace("_", "").isalnum():
                raise ValueError(f"非法表名{table}")
            if None in (con_key, con_value):
                raise ValueError(f"传递参数有空值")
            sql = f"delete from `{table}` where `{con_key}`={con_value}"
            cursor = self.conn.cursor()
            cursor.execute(cursor)
            # self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            # 失败回滚
            raise e
        finally:
            cursor.close()

    def close_connect(self):
        self.conn.close()

    def close_pool(self):
        self.pool.close()


if __name__ == "__main__":
    load_dotenv(dotenv_path=str(cv.CONFIG_DIR / ".env"))
    host = os.getenv("DB_HOST")
    port = int(os.getenv("DB_PORT"))
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    db = os.getenv("DB_NAME")

    mysql_item = Mysql_tool(host=host, port=port, user=user, password=password, db=db)
    # print(mysql_item,type(mysql_item),mysql_item.__class__)
    # data=[
    #     ['4','营业部',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    #     ['5','维护部',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    # ]
    data = mysql_item.get_single("departments", "*")
    mysql_item.close_connect()
    mysql_item.close_pool()
    print(data)

```

##### 4. 密码保护

###### 1. 先忽略，后创建，模版公开，密码私有。

```tex
# 环境变量（敏感信息）
.env
*.env
.env.*

# 其他忽略规则...
__pycache__/
*.log
```

###### 2. 先创建，后忽略，挽救措施

```bash
# step1: 确保工作区干净
git status
# 如果有红色未提交文件，先执行
git add . && git -m  "temp: 保存当前工作"

# step2: 从git移除追踪，但保留本地文件
git rm --cached content/API_Project/config/.env		# 不想上传的文件，重要文件

# Step3: 确认.gitignore文件中已经包含不想上传文件
cat .gitignore

# step4: 提交这次删除（Git会理解为停止追踪）
git add .gitignore
git commit -m "security: 移除 .env 文件，改为本地环境变量管理"

# step5: 如果已经推送到github/gitee, 强制更新远程（删除远程的.env）
git push origin main --forece-with-lease
```

