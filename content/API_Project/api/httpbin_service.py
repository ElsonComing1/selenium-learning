# httpbin_service.py
from core import BaseApi
from utils import type_parse
from config  import log
from core import Config


class HttpbinCoreService(BaseApi):
    """
    httpbin 核心业务服务（IP查询、POST/PUT/DELETE、延迟）
    """

    def get_ip(self) -> dict:
        """获取请求IP"""
        log.info("查询当前IP...")
        return self.get("/ip")

    @type_parse(data=dict)
    def submit_data(self, data: dict):
        """
        提交JSON数据（POST）
        :param data:要提交的字典数据
        :return:服务器回显数据
        """
        log.info(f"提交数据：{data}")
        result = self.post("/post", json_data=data)
        return result

    @type_parse(data=dict)
    def update_data(self, data: dict = None) -> dict:
        """更新数据（PUT）"""
        log.info(f"更新数据：{data}")
        return self.put(endpoint="/put", json_data=data)

    def delete_resource(self) -> dict:
        """删除资源（DELETE）"""
        log.info("执行删除操作...")
        return self.delete(endpoint="/delete")

    @type_parse(seconds=int)
    def test_delay(self, seconds: int) -> dict:
        """
        测试延迟接口
        :params seconds 延迟秒数
        """
        log.info(f"测试延迟接口：{seconds}秒")
        # 使用长超时
        return self._request(
            method="GET",
            endpoint=f"/delay/{seconds}",
            timeout=Config().get_config()["long_timeout"],
        )

    def get_request_headers(self) -> dict:
        """获取服务器收到的请求头（用于调试认证）"""
        return self.get("/headers")


class HttpbinAuthService(BaseApi):
    """
    httpbin 认证服务（Basic Auth、Bearer Token验证）
    """

    def __init__(self, session=None):
        super().__init__(session)
        # BaseApi().__init__(session)
        self.credentials = Config().get_config()["auth"]

    def basic_auth_login(self) -> dict:
        """
        使用Basic Auth登录
        返回：认证结果（包含authenticated字段）
        """
        user = self.credentials["username"]
        password = self.credentials["password"]

        log.info(f"尝试Basic Auth登录：{user}")

        # 先设置认证信息
        self.set_basic_auth(user, password)

        # 访问受保护资源
        result = self.get(endpoint=f"/basic-auth/{user}/{password}")
        # headers中参数名字都是-不是下划线
        return result

    @type_parse(token=str)
    def bearer_auth_check(self, token: str = None) -> dict:
        """
        验证Bearer Token（通过查看服务器回显的Headers）
        """
        if token:
            self.set_auth_token(token)

        result = self.get("/headers")
        return result


"""
    Basic Auth是“账号密码登录”，一次登录后面就不用再显示输入，当前会话一直保持；
    Bearer Token是“令牌验证”，效果同上
"""