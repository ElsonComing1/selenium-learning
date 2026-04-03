### API接口

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
        URL: https://api.zhuimi.com/v1/robots/status
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
    4. 第三方库可以写在需要的业务库中，外加，当真正需要时，再导入=lazy 导入

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
    
    一个域名下，有多个业务模块；一个业务模块下，有多个API；API=URL + method + params + response
    业务模块=服务(Service)，一个服务指的就是业务模块(一组相关的API集合)。单个API叫"接口"或"API 端点（API Endpoint）"

    https://api.example.com:8080/api/v1/users/123?active=true&page=1
    \_____________________/  \_/ \______________/ \________________/
            Domain          Port  Path/Endpoint   Query String
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
    先拿到需要的资料，然后就是直截了当的编写核心的代码，看能不能通，再是重构代码，最后就是优化维护代码。
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

