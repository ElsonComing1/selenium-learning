from pathlib import Path

PROJECT_PATH = str(Path(__file__).parent.parent)
import sys

sys.path.insert(0, PROJECT_PATH)

from page_object_model.BaiduPage import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tools.ExcelHandler import *
from datetime import datetime
import pytest,allure

data_file = os.path.join(PROJECT_PATH, "test_data", "test_cases.xlsx")

@allure.feature('测试页面')
@allure.description('测试登录页面的各个功能模块')
@allure.severity(allure.severity_level.NORMAL)
class TestLogin:
    """
    包括类名在内的需要测试的方法起名以test开头
    通过创建实例类，来使用里面的方法（页面类非基础类）
    """

    # 首先直接创建套件，其function是功能测试，也就是每一个测试方法会单独运行依次该套件函数
    @pytest.fixture(scope="function")
    # 套件不用以test起名。不是测试部分
    def driver(self):
        # 需要使用套件里变量的测试，需要其有一个参数名是套件的方法名
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        # 新增：禁用图片和 CSS 加速加载
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-javascript')  # 如果测试不需要 JS，可启用

        # 新增：设置页面加载策略（不等全部资源加载完）
        options.page_load_strategy = 'eager'  # 或 'none'

        # 新增：设置 DNS 预读取和缓存
        options.add_argument('--dns-prefetch-disable')
        options.add_argument('--disable-browser-side-navigation')

        driver = webdriver.Chrome(options=options)

        # 关键：设置页面加载超时时间为 60 秒（默认 30 秒可能不够）
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(30)
        yield driver
        # 此处的yield是迭代器，会将控制权交予使用该套件名的测试方法，此处dr是内部变量
        driver.quit()
        # 当使用完毕，会关闭浏览器
    @allure.story('测试登录模块')
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description('测试测试网页的登录模块')
    @pytest.mark.flake(reruns=2,reruns_delay=3,only_rerun=['TimeoutException'])
    def test_login_demo(self,driver):
        url=r'https://demoqa.com/login'
        try:
            
            with allure.step('步骤1：打开测试网页'):
                test_login=BaiduPage(driver,15)
            # 测试方法中使用assert, 页面对象中使用if 结合araise;均不会导致程序崩溃，因为Pyetst会处理他们
            with allure.step('步骤2：判断是否成打开网页'):
                assert test_login.open_url(url) is True,f'没能成功打开你想要的网址{url}'
            with allure.step('步骤3：验证登录'):
                text=test_login.login_to_target('Elson','123456').get_result_text()
            sleep(1)
        except Exception as e:
            raise 
        
        # print(text)



if __name__ == "__main__":
    timestamp = datetime.now().strftime(r"%Y-%m-%d_%H-%M-%S")
    # windows系统文件名不能包含：
    # print(PROJECT_PATH)
    report_name = os.path.join(
        PROJECT_PATH, "report", f"{TestLogin.__name__}_{timestamp}_report.html"
    )
    # 运行程序之前一定得关闭excel表格，否则代码无法操作

    # print(f'afaefqwfwqe{report_name}')
    # print(PROJECT_PATH)
    # 指定测试案例
    """
        命令行：
            pytest  TestBaiduPOM.py::TestBaiduPOM::test_settings  -v
            pytest -v -k 'test_settings'
        代码：
            target_case=__file__::TestBaiduPOM::test_settings
            pytest.main(['-v',target_case,'--html={report_name}','--self-contained-html'])
    """
    pytest.main(
        [
            __file__,
            "-v",
            "-k",
            "TestLogin",
            f"--html={report_name}",
            "--self-contained-html",
        ]
    )

'''
    | 装饰器                   | 类级别作用  | 方法级别作用  | 叠加 or 覆盖？                    |
| --------------------- | ------ | ------- | ---------------------------- |
| `@allure.feature`     | 定义功能模块 | ❌ 不推荐   | **叠加**（类+方法都有会合并）            |
| `@allure.story`       | ❌ 不推荐  | 定义用户故事  | **叠加**（类feature+方法story形成层级） |
| `@allure.description` | 类整体描述  | 单个测试描述  | **覆盖**（方法覆盖类）                |
| `@allure.severity`    | 类默认优先级 | 单个测试优先级 | **覆盖**（方法覆盖类，未标注方法继承类）       |
| `@allure.title`       | 类标题    | 测试用例标题  | **覆盖**（方法优先）                 |

'''