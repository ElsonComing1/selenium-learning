"""
Day 7: Allure 报告集成
在原有 POM 基础上添加 Allure 注解
"""

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 假设你复用了 day06 的代码
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "day06"))

from page_object_model.BaiduPage import BaiduPage


@allure.feature("百度搜索模块")  # 大功能模块
@allure.story("关键词搜索")      # 用户故事/场景
class TestBaiduWithAllure:
    
    @pytest.fixture(scope="function")
    def driver(self):
        options = Options()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()

    @allure.title("搜索追觅科技")           # 用例标题
    @allure.description("验证搜索功能正常") # 详细描述
    @allure.severity(allure.severity_level.CRITICAL)  # 优先级：Blocker/Critical/Normal/Minor/Trivial
    @allure.step("步骤1：打开百度首页")     # 步骤分解（会显示在报告里）
    def test_search_zhuimi(self, driver):
        page = BaiduPage(driver)
        
        with allure.step("步骤2：输入关键词并搜索"):
            page.open_target_page("https://www.baidu.com")
            page.search_content("追觅科技")
        
        with allure.step("步骤3：验证搜索结果"):
            title = page.get_title()
            assert "追觅" in title, f"期望包含'追觅'，实际：{title}"
            
            # 添加附件到报告（截图）
            allure.attach(
                driver.get_screenshot_as_png(),
                name="搜索结果截图",
                attachment_type=allure.attachment_type.PNG
            )

    @allure.title("搜索失败案例演示")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_failed_demo(self, driver):
        """故意失败，展示 Allure 的错误追踪"""
        page = BaiduPage(driver)
        page.open_target_page("https://www.baidu.com")
        
        with allure.step("步骤：搜索不存在的内容"):
            page.search_content("xxxxxxxxxxxxxxx")
            
            # 添加文本附件（日志）
            allure.attach(
                "这是测试日志：正在验证一个不存在的词条",
                name="测试日志",
                attachment_type=allure.attachment_type.TEXT
            )
            
            # 这个断言会失败，展示 Allure 的错误捕获
            assert "找到相关结果" in page.get_title()

    @allure.title("数据驱动测试（Allure 动态标题）")
    @pytest.mark.parametrize("keyword,expected", [
        ("Selenium", "Selenium"),
        ("Python", "Python"),
        ("Allure", "Allure")
    ])
    def test_search_with_params(self, driver, keyword, expected):
        """参数化测试在 Allure 中会显示为多个用例"""
        allure.dynamic.title(f"搜索关键词：{keyword}")  # 动态设置标题
        
        page = BaiduPage(driver)
        page.open_target_page("https://www.baidu.com")
        page.search_content(keyword)
        
        assert expected in page.get_title()