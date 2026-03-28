from pathlib import Path
import pandas as pd
PROJECT_PATH=str(Path(__file__).parent.parent)
import sys
sys.path.insert(0,PROJECT_PATH)

from page_object_model.BaiduPage import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tools.ExcelHandler import *
from datetime import datetime
from selenium.common.exceptions import TimeoutException
import pytest,allure

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

'''
    allure的全部内容针对的都是所要测试内容
    BLOCKER > CRITICAL > NORMAL > MINOR > TRIVAL：均是针对不同测试案例设置的级别，也就是我们所要测试的东西的某一个部分的验证程度
    设置级别，便于管理查看；测试类和测试方法均可以设置严重程度。测试类设置严重程度后，其对应的测试方法也会随着测试类的严重程度变化，当然内部方法可以再次设置对应的严重程度

    BLOCKER：阻塞级（系统崩溃，必须立即修复）
    CRITICAL：严重（核心功能失败）
    NORMAL：一般（默认级别）
    MINOR：轻微（UI 错位等）
    TRIVIAL：微不足道（拼写错误等）

常用附件类型：
    allure.attachment_type.PNG / JPG：截图
    allure.attachment_type.TEXT：纯文本
    allure.attachment_type.HTML：HTML 片段
    allure.attachment_type.JSON：接口返回数据

装饰器：
    是保证被装饰函数功能完整的情况下，前后有一些别的操作

钩子Hook：
    是测试函数内部插入别的操作


'''
# 将该类下的全部测试方法设置成统一默认的严重级别
@allure.severity(allure.severity_level.BLOCKER)
@allure.feature('百度首页搜索模块')
# feature装饰测试类
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

    # 类方法，就没有self自己（实例特有），但在类中需要有@staticmethod装饰
    @staticmethod
    @common_exception
    # 实例方法无法在类中调用
    def get_data(data_file: str, sheet: int = 0):
        excel = ExcelHandler(data_file)
        return excel.read_point_sheet_rows(sheet)



    '''
        由于该参数驱动测试方法比较容易因为时间超时而导致错误，因此下载对应的插件pyets-rerunfailures库
        1. 对指定文件或者类进行失败重试机制：
            pyest ./TestBaiduPOM.y::TestBaiduPom ./TestLogin.py -v --reruns 2 --reruns-delay 3 --alluredir=../allure-results --clean-alluredir
            会自动失败重试两次，直至遇见pass或者尝试完毕都未成功
        
        2. 正对特定方法的重试机制：
            @pytest.mark.flaky(reruns=2,reruns_delay=2,only_rerun=['TimeoutException'])
            失败会休息两秒，用于缓冲，然后再次执行，但要在指定错误条件下，才会执行重试机制, 需要导入相应的库
            rerun两次，总共三次，
    '''
    @allure.story('不同关键字搜索')
    # 使用feature story也就是对该测试类或者测试方法的名字进行翻译解释用途
    # @allure.severity(allure.severity_level.BLOCKER) 由于类已经设置过级别，所以内部方法不用再设置
    @pytest.mark.parametrize("data", get_data(data_file, 0))
    @allure.description('通过百度首页，搜索不通关键字，然后判断搜索后的页面主题是否包含对应的关键字')
    @pytest.mark.flaky(reruns=2,reruns_delay=3,only_rerun=["TimeoutException"])
    # 重试机制
    def test_data_driven_search(self, driver, data):
        # parametrize 会将[['TC001', '搜索Selenium', 'Selenium', 'Selenium', None, 'Fail', None]]拆成一个实体，单列表
        allure.dynamic.title(f'百度动态搜索关键字：{data[2]}')
        result_data=[]
        # 方法上方需要装饰器，而方法内部是不需要@
        try:
            # 该方法的参数名字需要与装饰器参数化的第一个参数名一致，且在使用中也必须是driver
            baidu = BaiduPage(driver)
            with allure.step('步骤1：打开百度搜索页面'):
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
            with allure.step('步骤2：搜索关键字后，获取其对应的title'):
                actual_result = baidu.search_content(keyword).get_title()
            # 在获取title之前，记得显示判断title是否成功跳转，太快获取的title还是旧有窗口

            with allure.step('步骤3：判断获得结果值，是否与期望值匹配'):
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
            with allure.step(f'报错步骤：运行搜索案例{data[0]}程序报错了'):
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
            raise       # 会打印堆栈信息
            # pytest.fail(f'用例执行失败：{e},pytrace=True')  # 不打印堆栈信息
            # 这样做的目的就是为了，让pytest知道程序报错了，而不是错误了，也还是pass
        finally:
            # 仅使用于单进程
            # with allure.step(f'步骤4：正在将案例{data[0]}的数据写入excel表格'):
            #     # print(result_data)
            #     excel = ExcelHandler(data_file)
            #     excel.cover_write_point_sheet(0, result_data)


            # 多进程并发 pytest-xdist;
            result_df=pd.DataFrame(result_data,columns=[
                'case_id', 'case_name', 'keyword', 
                'expected_result', 'actual_result', 
                'status', 'remark'
            ])
            # 表格形式，一个内部列表就是一个实例，也是数据类型从[[]]转换成 pd.dataframe
            worker_id=os.getenv('PYTEST_XDIST_WORKER','master')
            # 多进程时，返回对应的进程id,单进程只会返回master; 此处就是区分多进程与当单进程的关键点
            temp_file=f'temp_result_{worker_id}.xlsx'

            # 需要针对进程，来对文件进行不同的输入模式: 单进程 追加，多进程，单个文件
            if os.path.exists(temp_file):
                # 文件存在，则是追加
                existing_data=pd.read_excel(temp_file)
                curr_worker_data=pd.concat([existing_data,result_df],ignore_index=True)
                # 始终保持不带行索引号
                curr_worker_data.to_excel(temp_file,index=False)
                # pd数据类型，直接方法再次写入该文件，始终保持不带含索引号


            else:
                # 不存在。则是直接写入，写入会直接创建文件
                result_df.to_excel(temp_file,index=False)

            # 此处finally 均是写入临时文件，需要conftest.py文件中写对应的后续处理pytest_sessionfinish(session,existstatus)








    @allure.severity(allure.severity_level.NORMAL)
    # 设置其他级别，进行覆盖类的严重级别
    @allure.story('测试百度首页设置')
    @allure.description('移动鼠标至百度首页设置，观察是否会有下拉框显示')
    def test_settings(self, driver):
        try:
            baidu = BaiduPage(driver)
            with allure.step('步骤1：打开百度首页'):
                baidu.open_url(r"https://www.baidu.com")
            with allure.step('步骤2：打开设置'):
                element=baidu.open_settings()
            sleep(2)
        except Exception as e:
            with allure.step(f'报错步骤：{e}'):
                raise e


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
'''
    1. pytest-allure 是 一个让python 和 allure沟通的适配器，运行测试后，会生成一个.json测试文件
    最终通过scoop(windows包管理器) install allure(安装命令行工具) 作用将.json文件生成html报告

    2. 运行方式：
        cd project_path
        pytest test_cases/TestBaiduPOM.py -v --alluredir=./allure-results  指定 Allure 原始数据（JSON）输出目录，默认为 allure-results 自动生成

    3. 报告生成：
        1. 启动临时报告服务器
            allure serve ./alliure-results
            ✅ 即开即用，适合本地调试
            ✅ 自动清理，关闭后端口释放，不残留文件
        
        2. 生成静态报告（CI持续集成/CD持续推送）
            allure generate ./allure-results -o ./allure-report --clean 
            -o指定报告输出路径，--clean 若目录已存在，先清空
            ✅ 生成静态文件，可打包、发邮件、部署到 Jenkins/Nginx
        
        3. 结合pytest直接运行
        pytest.main([__file__,
            '-v',
            '--alluredir=./allure-results',
            '--clean-alluredir'
        ])

    4. 我采用的方式bash：
        # 1. 精确指定：文件::类::方法（推荐，最准确）
        pytest test_cases/TestBaiduPOM.py::TestBaiduPom::test_data_driven_search -v --alluredir=./allure-results --clean-alluredir(清空，再产生json,不然不断累加)	

        # 2. 关键字匹配（方法名写错部分也能匹配到，更宽松）
        pytest test_cases/TestBaiduPOM.py -v -k "test_data_driven_search" --alluredir=./allure-results -x(以有错就停止)

        # 3. 查看报告
        allure serve ./allure-results
        同一个终端运行，才能更得上当前json

    5. 并行运行,需要下载pytest-xdist库
    pytest ./test_cases/ -v --alluredir=./allure-results --clean-alluredir -n auto  根据电脑核心，自动分配
    pytest ./test_cases/ -v --alluredir=./allure-results --clean-alluredir -n 4 指定并行运行数量 --reruns 2 --resuns-delay 1
'''