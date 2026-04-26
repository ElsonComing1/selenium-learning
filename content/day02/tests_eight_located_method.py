# 打印完整库
import traceback
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException
# 动作链
from selenium.webdriver.common.action_chains import ActionChains

def by_method_located_text(wait,located):
    print(f'现在正在使用{repr(located[0])}进行搜索文本框')
    real_element=wait.until(EC.visibility_of_element_located(located))
    real_element.click()
    real_element.clear()
    print(str(located[0]))
    real_element.send_keys(f"{repr(located[0])}")
    real_element.clear()
    # 点击空白处使得后续地图能够被选中
    wait.until(EC.visibility_of_element_located((By.TAG_NAME,"body"))).click()



def by_method_located(wait,located):
    print(f'现在正在使用{repr(located[0])}进行搜索文本框')
    real_element=wait.until(EC.visibility_of_element_located(located))
    if real_element:
        print(real_element,real_element.text)
    print(f'我已经找到了{real_element.text}')


def main():
    driver=None
    try:
        options=Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver=webdriver.Chrome(options=options)
        driver.get("https://www.baidu.com".strip())
        wait=WebDriverWait(driver,10)

        # 创建定位器
        located_id=(By.ID,"chat-textarea")
        located_class_name=(By.CLASS_NAME,"chat-input-textarea")
        located_xpath=(By.XPATH,'//div[@id="chat-input-area"]/textarea')
        located_css=(By.CSS_SELECTOR,'#chat-input-area textarea')

        located_link_text=(By.LINK_TEXT,'更多')
        located_partial_text=(By.PARTIAL_LINK_TEXT,'地')

        by_method_located(wait,located_link_text)
        by_method_located(wait,located_partial_text)
        by_method_located_text(wait,located_id)
        by_method_located_text(wait,located_class_name)
        by_method_located_text(wait,located_xpath)
        by_method_located_text(wait,located_css)
    # 超时异常
    except TimeoutException as e:
        print(e)
    # 未定义到元素异常
    except NoSuchElementException as e:
        print(e)
    except Exception as e:
        if driver:
            driver.save_screenshot("./error_screenshot/error_screenshot.png")
            print(e)
        traceback.print_exc() # 打印完整堆栈，方便调试
    finally:
        driver.quit()


if __name__=="__main__":
    main()


