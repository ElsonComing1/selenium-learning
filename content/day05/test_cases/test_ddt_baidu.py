# ========== 2. 数据驱动测试类 ==========
class TestBaiduDDT:
    @pytest.fixture(scope="function")
    # scope='function' 其套件（执行测试前的准备，初始化浏览器，连接数据库，以及执行完毕后的关闭浏览器）
    def driver(self):
        """每个用例独立浏览器"""
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        yield driver
        # return 能返回，但没teardown能力
        # yield是生成器，用一个产生一个，在pytest中启一个分割线的作用：谁在调用该生成器就会产生且将控制权给测试函数
        driver.quit()
    
    def get_excel_data(self):
        """读取 Excel 数据（数据源）"""
        excel = ExcelHandler("test_cases.xlsx")
        return excel.read_cases()
    
    @pytest.mark.parametrize("case", get_excel_data())
    # pytest定义的数据名必须和下方的方法形参同名，否则没用。
    # 数据驱动是由于同一个测试步骤，因为数据的不同而发生变化的测试函数。
    # 数据和测试逻辑分离
    def test_search_by_excel(self, driver, case):
        """
        参数化测试：Excel 里每一行数据生成一个测试用例
        类比：Excel 有 4 行数据，pytest 自动执行 4 次，每次用不同数据
        """
        print(f"\n执行用例: {case['case_id']} - {case['case_name']}")
        
        try:
            # 1. 打开百度
            driver.get("https://www.baidu.com")
            
            # 2. 搜索
            search_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "kw"))
            )
            search_box.send_keys(case["keyword"])
            driver.find_element(By.ID, "su").click()
            
            # 3. 验证
            WebDriverWait(driver, 10).until(EC.title_contains(case["keyword"]))
            actual_result = driver.title
            expected = case["expected"]
            
            # 4. 断言并标记结果
            if expected in actual_result:
                status = "Pass"
                remark = "实际标题包含期望关键字"
            else:
                status = "Fail"
                remark = f"期望包含'{expected}'，实际为'{actual_result}'"
            
            # 5. 回写 Excel（立即标记结果）
            excel = ExcelHandler("test_cases.xlsx")
            excel.write_result(case["row_idx"], actual_result, status, remark)
            
            assert status == "Pass", remark
            
        except Exception as e:
            # 异常也要回写 Excel
            excel = ExcelHandler("test_cases.xlsx")
            excel.write_result(case["row_idx"], "Error", "Fail", str(e))
            raise


# ========== 3. 生成测试报告 ==========
if __name__ == "__main__":
    # 运行并生成 HTML 报告
    pytest.main([
        __file__,   # 当前文件的路径，就是只运行本文件下的test开头或者结尾的方法
        "-v",   # 详细显示信息
        "--html=report.html",  # 生成测试报告
        "--self-contained-html" # 将css内联到html中，就是css在html里面，为了美观
    ])

'''
    按名称过滤：
        只运行包含特定名称的文件: pyetst -v -k "search and not slow"   -k 是过滤已经发现的测试，支持逻辑
        已经发现的测试规则：
            文件：test_*.py | *_test.py
            类：Test 基础Object 不含init__
            函数/方法：test_*(必须test开头)
        只运行特定类中的测试: pytest -v testfile.py::TestBaidu::test_search_by_excel
        排除特定测试：pytest -v -k "not search" 

    使用装饰器标记跳过：
        @pytest.mark.skip(reason="暂时跳过测试")
        def test_temp_skip(self):
            pass
        @pytest.mark.skipif(condition=sys.platform=="win32",reason="windows 不执行")
        def test_unix_only(self):
            pass
        @pytest.mark.xfail(reason="预期失败，待修复")  # 失败不计入错误
        def test_known_bug(self):
            assert 1==2
    
    自定义标记跳过：
        # 1. 注册标记（pytest.ini 文件）
        [pytest]
        markers=
            smoke:冒烟测试
            regression:回归测试
            slow:慢速测试
        # 2. 给测试打标记
        @pytest.mark.smoke
        def test_critical_path(self):
            pass

        # 3. 只运行冒烟测试
        pytest -v -m "smoke"

        # 4. 排除标记测试
        pytest -v -m "not slow"
    
    命令行排除测试：
        # 忽略特定文件
        pytest --ignore=test_pld.py

        # 只运行指定目录
        pytest test/unit/ -v
'''
