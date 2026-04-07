import requests

from config import get_config, get_base_url
from utils import log


class BaseApi:
    """
    HTTP 基础封装类
    职责：管理网络连接，不管业务逻辑
    """

    def __init__(self, session: requests.Session = None):
        # 获取环境，然后实例化
        self.base_url = get_base_url()
        self.config = get_config()
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
        except requests.HTTPError as e:
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

    def post(self, endpoint: str, json_data: dict = None, **kwargs):
        """POST 请求（JSON格式）"""
        headers = kwargs.pop("headers", {})
        # 获取输入的headers
        headers.setdefault("Content-Type", "application/json")
        # if 'Content-Type' not in headers:
        #     headers['Content-Type']='application/json'
        # 尊重用户选择
        kwargs["headers"] = headers
        return self._request("POST", endpoint, json=json_data, **kwargs)
        # 单个变量要在最前面，关键字变量紧接着后面，然后是**kwargs

    def put(self, endpoint: str = None, json_data: dict = None, **kwargs):
        """PUT请求（全量更新）"""
        headers = kwargs.pop("headers", {})  # 必须要有 , {} 默认值！
        headers.setdefault("Content-Type", "application/json")
        kwargs["headers"] = headers
        return self._request("PUT", endpoint, json=json_data, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        """DELETE请求"""
        return self._request("DELETE", endpoint, **kwargs)

    def set_auth_token(self, token: str):
        """设置bearer token(供Service层使用)"""
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        # 对当前会话设置token，拿去临时权限
        log.debug(f"Token已设置: {token[:10]}...")
        # token在headers中

    def set_basic_auth(self, username: str, password: str):
        """设置Basic Auth（requests会自动编码）"""
        self.session.auth = (username, password)
        # 单独列出
        log.debug(f"Basic Auth已设置: {username}")
