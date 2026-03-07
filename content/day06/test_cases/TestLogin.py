from pathlib import Path

PROJECT_PATH = str(Path(__file__).parent.parent)
import sys

sys.path.insert(0, PROJECT_PATH)

from page_object_model.BaiduPage import *
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from tools.ExcelHandler import *
from datetime import datetime
import pytest

data_file = os.path.join(PROJECT_PATH, "test_data", "test_cases.xlsx")


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
        options.add_argument("--start-maximized")
        dr = webdriver.Edge(options=options)
        yield dr
        # 此处的yield是迭代器，会将控制权交予使用该套件名的测试方法，此处dr是内部变量
        dr.quit()
        # 当使用完毕，会关闭浏览器
    def test_login_demo(self,driver):
        url=r'https://demoqa.com/login'
        test_login=BaiduPage(driver,15)
        # 测试方法中使用assert, 页面对象中使用if 结合araise;均不会导致程序崩溃，因为Pyetst会处理他们
        assert test_login.open_url(url) is True,f'没能成功打开你想要的网址{url}'
        text=test_login.login_to_target('Elson','123456').get_result_text()
        sleep(1)
        print(text)



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
