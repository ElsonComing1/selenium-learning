from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os  # ✅ 补上导入


def test_baidu_search(url):
    driver = None  # 初始化
    try:
        options = Options()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        driver = webdriver.Chrome(options=options)
        driver.get(url.strip())

        # 时间等待器
        wait = WebDriverWait(driver, 10)
        
        # ✅ 先定义所有 EC 条件（按使用顺序）
        ec_element_text = EC.visibility_of_element_located((By.ID, "chat-textarea"))
        ec_element_search = EC.visibility_of_element_located((By.ID, "chat-submit-button"))
       
        # 再执行等待（真实元素元素不在同一个页面要注意先后）
        real_element_text = wait.until(ec_element_text)
        real_element_search = wait.until(ec_element_search)
        # 输入文本操作
        real_element_text.click()
        real_element_text.clear()
        real_element_text.send_keys("追觅")
        # 点击搜索
        real_element_search.click()
        sleep(3)
        
        # 验证标题
        ec_element_zhuimi = EC.title_contains("追觅")
        wait.until(ec_element_zhuimi)
        assert "追觅" in driver.title, "未进入追觅"  # ✅ 去掉 print，直接字符串

    except Exception as e:
        print(f"发生错误: {e}")
        if driver:  # ✅ 检查 driver 是否存在
            os.makedirs("./error_screenshot", exist_ok=True)
            driver.save_screenshot("./error_screenshot/error_screenshot.png")
            
    finally:
        if driver:  # ✅ 检查 driver 是否存在
            driver.quit()


if __name__ == "__main__":
    url = "https://www.baidu.com"
    test_baidu_search(url)
