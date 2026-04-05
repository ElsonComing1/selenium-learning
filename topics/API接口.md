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

平台地址（域名）：http://httpbin.org/



6个核心API端点（覆盖完整的测试场景）：

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



训练业务流程设计（模拟真实企业场景）：

```plain
获取IP(验证网络) ——> 携带Token访问受保护资源 ——> POST提交业务数据 ——> PUT更新数据 ——> DELETE清理数据 ——> 验证延迟接口性能
```



环境准备：

```txt
# file path: C:\Users\16531\Desktop\selenium-learning\content\API_Project\requirements.txt
requests==2.31.0
```

​		该requirements.txt文件需要不断更新，当需要其他第三库的时候，便于他人使用你的代码。

安装指令：

```bash
pip install -r C:\Users\16531\Desktop\selenium-learning\content\API_Project\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```



测试域名连通性验证：

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

​		目标：一个文件test_smoke.py，最原始的方式，跑通httpbin.org的全流程

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

1. 搭建基础框架

​		搭建基础框架，基础框架能通就行，不要很高深，后面就是一边使用一边定型。



​		