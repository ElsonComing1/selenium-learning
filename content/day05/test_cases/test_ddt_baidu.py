# # ========== 2. 数据驱动测试类 ==========
# class TestBaiduDDT:
#     @pytest.fixture(scope="function")
#     # scope='function' 其套件（执行测试前的准备，初始化浏览器，连接数据库，以及执行完毕后的关闭浏览器）
#     def driver(self):
#         """每个用例独立浏览器"""
#         from selenium.webdriver.chrome.options import Options
#         options = Options()
#         options.add_argument("--start-maximized")
#         driver = webdriver.Chrome(options=options)
#         yield driver
#         # return 能返回，但没teardown能力
#         # yield是生成器，用一个产生一个，在pytest中启一个分割线的作用：谁在调用该生成器就会产生且将控制权给测试函数
#         driver.quit()
    
#     def get_excel_data(self):
#         """读取 Excel 数据（数据源）"""
#         excel = ExcelHandler("test_cases.xlsx")
#         return excel.read_cases()
    
#     @pytest.mark.parametrize("case", get_excel_data())
#     # pytest定义的数据名必须和下方的方法形参同名，否则没用。
#     # 数据驱动是由于同一个测试步骤，因为数据的不同而发生变化的测试函数。
#     # 数据和测试逻辑分离
#     def test_search_by_excel(self, driver, case):
#         """
#         参数化测试：Excel 里每一行数据生成一个测试用例
#         类比：Excel 有 4 行数据，pytest 自动执行 4 次，每次用不同数据
#         """
#         print(f"\n执行用例: {case['case_id']} - {case['case_name']}")
        
#         try:
#             # 1. 打开百度
#             driver.get("https://www.baidu.com")
            
#             # 2. 搜索
#             search_box = WebDriverWait(driver, 10).until(
#                 EC.visibility_of_element_located((By.ID, "kw"))
#             )
#             search_box.send_keys(case["keyword"])
#             driver.find_element(By.ID, "su").click()
            
#             # 3. 验证
#             WebDriverWait(driver, 10).until(EC.title_contains(case["keyword"]))
#             actual_result = driver.title
#             expected = case["expected"]
            
#             # 4. 断言并标记结果
#             if expected in actual_result:
#                 status = "Pass"
#                 remark = "实际标题包含期望关键字"
#             else:
#                 status = "Fail"
#                 remark = f"期望包含'{expected}'，实际为'{actual_result}'"
            
#             # 5. 回写 Excel（立即标记结果）
#             excel = ExcelHandler("test_cases.xlsx")
#             excel.write_result(case["row_idx"], actual_result, status, remark)
            
#             assert status == "Pass", remark
            
#         except Exception as e:
#             # 异常也要回写 Excel
#             excel = ExcelHandler("test_cases.xlsx")
#             excel.write_result(case["row_idx"], "Error", "Fail", str(e))
#             raise


# # ========== 3. 生成测试报告 ==========
# if __name__ == "__main__":
#     # 运行并生成 HTML 报告
#     pytest.main([
#         __file__,   # 当前文件的路径，就是只运行本文件下的test开头或者结尾的方法
#         "-v",   # 详细显示信息
#         "--html=report.html",  # 生成测试报告
#         "--self-contained-html" # 将css内联到html中，就是css在html里面，为了美观
#     ])

# '''
#     按名称过滤：
#         只运行包含特定名称的文件: pyetst -v -k "search and not slow"   -k 是过滤已经"发现"的测试，支持逻辑
#         已经发现的测试规则：
#             文件: test_*.py | *_test.py
#             类: Test 基础Object 不含init__
#             函数/方法：test_*(必须test开头)
#         只运行特定类中的测试: pytest -v testfile.py::TestBaidu::test_search_by_excel
#         排除特定测试：pytest -v -k "not search" 

#     使用装饰器标记跳过：
#         @pytest.mark.skip(reason="暂时跳过测试")
#         def test_temp_skip(self):
#             pass
#         @pytest.mark.skipif(condition=sys.platform=="win32",reason="windows 不执行")
#         def test_unix_only(self):
#             pass
#         @pytest.mark.xfail(reason="预期失败，待修复")  # 失败不计入错误
#         def test_known_bug(self):
#             assert 1==2
    
#     自定义标记跳过：
#         # 1. 注册标记（pytest.ini 文件）
#         [pytest]
#         markers=
#             smoke:冒烟测试
#             regression:回归测试
#             slow:慢速测试
#         # 2. 给测试打标记
#         @pytest.mark.smoke
#         def test_critical_path(self):
#             pass

#         # 3. 只运行冒烟测试
#         pytest -v -m "smoke"

#         # 4. 运行标记测试以外的测试
#         pytest -v -m "not slow"
    
#     命令行排除测试：
#         # 忽略特定文件
#         pytest --ignore=test_pld.py

#         # 只运行指定目录
#         pytest test/unit/ -v
# '''

import pytest,os,traceback,sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
# 从当前文件所在位置，往上寻找路径，更方便代码移植，使用os.path.join便与跨平台
from helpers.ExcelHandler import *
from time import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_dirname=os.path.dirname(__file__)
project_name=os.path.dirname(base_dirname)
report_path=os.path.join(project_name,'reports','report.html')
file_path=os.path.join(project_name,'data','test_cases.xlsx')

class TestBaiduDDT(object):

    @pytest.fixture(scope='function')
    # @pyetest.mark.fixture定义当前方法的适用范围（每一个测试方法都需要单独开启一个dr）
    def dr(self):       #### 该fixture的函数名，需要出现在需要测试的且需要的函数的形参中且同名
        # 类中的函数
        options=Options()
        options.add_argument('--start-maximized')
        
        dr=webdriver.Chrome(options=options)    
        # 方法里定义属性
        yield dr    
        # 有谁在用，就支持谁，同时交出指挥权，就像调用别的方法而已，暂时做别的
        dr.quit()
        # 没人用，最后就关闭
    @staticmethod
    # 工具
    def get_excel_data(file_path,id):  # 有self只能实例使用
        real_excel=ExcelHandle(file_path,id)
        return real_excel.read_excel_cases()

    @pytest.mark.parametrize('rows',get_excel_data(file_path,0))
    # 需要与形参同名，第二个就是具体数据
    def test_search_by_excel(self,dr,rows):
        try:
            # 由于需要使用dr，因此该函数参数需要有dr
            wait=WebDriverWait(dr,10,0.5)
            dr.get('https://www.baidu.com')
            text_element=wait.until(EC.element_to_be_clickable((By.ID,'chat-textarea')))
            search_element=wait.until(EC.element_to_be_clickable((By.ID,'chat-submit-button')))
            print(f'这是case:{rows.get('case_id')},case_name是：{rows.get('case_name')}')
            sleep(1)
            text_element.send_keys(rows.get('keyword'))
            sleep(2)
            print('已经输入内容')
            search_element.click()
            sleep(2)
            print('已经点击搜索')
            
            actual_result=dr.title
            expected_result=rows.get('expected')
            # print(rows)
            # print(expected_result)

            if expected_result in actual_result or actual_result in expected_result:
                rows['status']='Pass'
                rows['remark']='实际标题包含期望值'
            else:
                rows['status']='Fail'
                rows['remark']=f'实际值是{actual_result},期望值是{expected_result}'
            real_excel=ExcelHandle(file_path,0)
            # print(rows.values())
            real_excel.write_excel_results([list(rows.values())])
            assert rows['status']=='Pass',rows['remark']
        except Exception as e:
            real_excel=ExcelHandle(file_path,0)
            rows['actual']='Error'
            rows['status']='Fail'
            rows['remark']=str(e)
            real_excel.write_excel_results([list(rows.values())])




if __name__=='__main__':
    # 单独运行该文件才会执行if __name__=='__main__': 下面的代码，因此供全局使用的变量（全局变量）在最前面定义
    pytest.main([
        __file__,
        '-v',   # 详细显示
        f'--html={report_path}',    # 生成html报告
        '--self-contained-html'     # --self-contianed-html使得报告能都独立出来且正常美观显示
    ])
    # 