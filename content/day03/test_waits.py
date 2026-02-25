from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains as AC
from time import sleep
import traceback

from config import *


def human_typing(element, text):
    """模拟真人输入"""
    for char in text:
        element.send_keys(char)
        sleep(random.uniform(0.05, 0.1))

def by_method_located(k_v):
    return wait.until(EC.element_to_be_clickable(k_v))
def test_sleep_vs_wait():
    try:
        dr.get("https://www.baidu.com".strip())
        # 强制等待
        sleep(5)
        located_settings=(By.LINK_TEXT,'更多')
        # 设置显示等待，且该设置是全局的，但由于有隐式等待的时间设置比较大，所以会按照隐式等待使用
        dr.implicitly_wait(5)
        settings=by_method_located(located_settings)
        # 移动鼠标到指定位置(元素)
        action.move_to_element(settings).perform()
        # 睡两秒为了查看结果
        sleep(2)
        
    except TimeoutException as e:
        print(e)
    except ElementNotInteractableException as e:
        print(e)
    except Exception as e:
        print(e)
        dr.save_screenshot('.\error_screenshot\error_screenshot.png')
        traceback.print_exc()
    finally:
        dr.quit()

def test_ajax_loading():
    # try:
        dr.get(r'https://www.taobao.com/'.strip())
        sleep(1)
        print('目前已经进入淘宝主页面了')
        located_input=(By.CSS_SELECTOR,'#q')
        get_input=by_method_located(located_input)
        get_input.click()
        get_input.clear()
        get_input.send_keys("手机")
        sleep(1)
        print('已经输入内容')
        located_search=(By.XPATH,'//button[contains(@class,"btn-search") and contains(@class,"tb-bg")]')
        get_search=by_method_located(located_search)
        get_search.click()
        # action.double_click(located_search)
        sleep(1)
        print('已经点击搜索')

        locted_loading1=(By.CSS_SELECTOR,".loading-overlay")
        locted_loading2=(By.CSS_SELECTOR,'.loader')
        sleep(2)
        wait.until(EC.invisibility_of_element_located((locted_loading1)))
        wait.until(EC.invisibility_of_element_located((locted_loading2)))
        print('已经加载完毕')
        sleep(10)

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,'//iframe[@id="baxia-dialog-content"]')))
        print('已经切换至登录框架')


        # located_username=(By.NAME,'fm-login-id')
        # located_password=(By.NAME,'fm-login-password')

        located_username = (By.CSS_SELECTOR, "input.fm-text[aria-label='账号名/邮箱/手机号']")
        located_password = (By.CSS_SELECTOR, "input.fm-text[placeholder='请输入登录密码']")


        # if 'fm-login-id' in dr.page_source:
        #     print("✅ 页面源码中包含 fm-login-id")
        # else:
        #     print("❌ 页面源码中没有 fm-login-id，尝试搜索其他关键词...")
        #     # 尝试搜索登录相关的文本
        #     if '密码登录' in dr.page_source:
        #         print("✅ 但找到了'密码登录'文本，说明登录框存在但 ID 不对")
        #     elif '账号名' in dr.page_source:
        #         print("✅ 找到了'账号名'文本")

        # # 【调试3】打印当前所有 iframe（检查是否在 iframe 里）
        # iframes = dr.find_elements(By.TAG_NAME, "iframe")
        # print(f"当前页面有 {len(iframes)} 个 iframe：")
        # for i, frame in enumerate(iframes[:3]):  # 只打印前3个
        #     print(f"  iframe {i}: id={frame.get_attribute('id')}, name={frame.get_attribute('name')}")





        get_username=by_method_located(located_username)
        get_username.click()
        get_username.clear()
        human_typing(get_username,"19015437827")
        # get_username.send_keys("19015437827")
        print('已经输入手机号')
        sleep(1)
        get_password=by_method_located(located_password)
        get_password.click()
        get_password.clear()
        # get_password.send_keys("289355cVBNM*")
        human_typing(get_password,"289355cVBNM")
        print('已经输入密码')
        sleep(1)
        located_login=(By.LINK_TEXT,'登录')
        get_login=by_method_located(located_login)
        get_login.click()
        print('已经登录')
        sleep(1)


    # except TimeoutException as e:
    #     print(e)
    # except ElementNotInteractableException as e:
    #     print(e)
    # except Exception as e:
    #     print(e)
    #     dr.save_screenshot(r'.\error_screenshot\debug_before_login.png')
    #     traceback.print_exc()
    # finally:
        dr.quit()
def main():
    # print("=== 测试 1: 等待方式对比 ===")
    # test_sleep_vs_wait()
    print("\n=== 测试 2: AJAX 加载处理 ===")
    test_ajax_loading()


if __name__=="__main__":
    # options来自外部config.py文件配置
    dr=webdriver.Chrome(options=options)
    action=AC(dr)
    # 隐式等待每隔0.5刷新一次，超时会报错
    wait=WebDriverWait(dr,20)
    main()

