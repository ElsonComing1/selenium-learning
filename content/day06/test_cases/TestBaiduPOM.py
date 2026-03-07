from pathlib import Path
PROJECT_PATH=str(Path(__file__).parent.parent)
import sys
sys.path.insert(0,PROJECT_PATH)

from page_object_model.BaiduPage import *
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from tools.ExcelHandler import *
from datetime import datetime
import pytest

# @pytest.fixture(scope='class',params=[os.path.join(PROJECT_PATH,'test_data','test_data.xlsx')])
# def data_file(request): # 此处的函数名，后面的类方法使用时，其类方法的参数也必须是该函数名，一致才能调用
#     # 此处的形参名必须是request，固定写法
#     file=request.params
#     if not os.path.exists(file):
#         # 当该路径文件不存在时上抛问题，先判断，通过则能返回
#         raise FileExistsError(f'当前文件路径的{file}不存在')
#     print(f'当前正在使用{file}')
#     return file,0
data_file = os.path.join(PROJECT_PATH, "test_data", "test_cases.xlsx")


class TestBaiduPom:
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

    # 类方法，就没有self自己（实例特有），但在类中需要有@staticmethod装饰
    @staticmethod
    @common_exception
    # 实例方法无法在类中调用
    def get_data(data_file: str, sheet: int = 0):
        excel = ExcelHandler(data_file)
        return excel.read_point_sheet_rows(sheet)

    @pytest.mark.parametrize("data", get_data(data_file, 0))
    def test_data_driven_search(self, driver, data):
        # parametrize 会将[['TC001', '搜索Selenium', 'Selenium', 'Selenium', None, 'Fail', None]]拆成一个实体，单列表
        try:
            # 该方法的参数名字需要与装饰器参数化的第一个参数名一致，且在使用中也必须是driver
            baidu = BaiduPage(driver)
            baidu.open_target_page("https://www.baidu.com")
            result_data = []

            # print(f'yesysyeys{data}')
            # for row in data:
            # print(row)
            (
                case_id,
                case_name,
                keyword,
                expected_result,
                actual_result,
                status,
                remark,
            ) = data
            actual_result = baidu.search_content(keyword).get_title()
            # 在获取title之前，记得显示判断title是否成功跳转，太快获取的title还是旧有窗口

            if str(expected_result) in actual_result:
                status = "Pass"
                remark = f"{actual_result}在期望值:{expected_result} 里面"
            else:
                status = "Fail"
                remark = f"{actual_result}不在期望值:{expected_result} 里面"
            result_data.append(
                [
                    case_id,
                    case_name,
                    keyword,
                    expected_result,
                    actual_result,
                    status,
                    remark,
                ]
            )
            # list接收多个对象而不是参数
        except Exception as e:
            # 测试函数的error直接处理，不在上抛
            status = "Error"
            remark = f"程序出错啦，原因是：{e}"
            result_data.append(
                [
                    case_id,
                    case_name,
                    keyword,
                    expected_result,
                    actual_result,
                    status,
                    remark,
                ]
            )
            # 报错也需要处理
        finally:
            # print(result_data)
            excel = ExcelHandler(data_file)
            excel.cover_write_point_sheet(0, result_data)

    def test_settings(self, driver):
        baidu = BaiduPage(driver)
        baidu.open_url(r"https://www.baidu.com")
        baidu.open_settings()
        sleep(2)


if __name__ == "__main__":
    timestamp = datetime.now().strftime(r"%Y-%m-%d_%H-%M-%S")
    # windows系统文件名不能包含：
    # print(PROJECT_PATH)
    report_name = os.path.join(
        PROJECT_PATH, "report", f"{TestBaiduPom.__name__}_{timestamp}_report.html"
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
            "TestBaiduPom",
            f"--html={report_name}",
            "--self-contained-html",
        ]
    )
