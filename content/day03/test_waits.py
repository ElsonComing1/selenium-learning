from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,ElementNotInteractableException,NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains as AC
from time import sleep
import traceback
import random,os

from config import *


def create_dr():
    dr=None
    # options来自外部config.py文件配置
    dr=webdriver.Chrome(options=options)
    global action
    global wait
    action=AC(dr)
    # 隐式等待每隔0.5刷新一次，超时会报错
    wait=WebDriverWait(dr,10)
    return dr
def human_typing(element, text):
    """模拟真人输入"""
    for char in text:
        element.send_keys(char)
        sleep(random.uniform(0.05, 0.1))
def by_visible_located(k_v):
    return wait.until(EC.visibility_of_element_located(k_v))

def by_clickable_located(k_v):
    return wait.until(EC.element_to_be_clickable(k_v))
def test_sleep_vs_wait():
    dr=create_dr()
    try:
        dr.get("https://www.baidu.com")
        # 强制等待
        sleep(5)
        located_settings=(By.LINK_TEXT,'更多')
        # 设置显示等待，且该设置是全局的，但由于有隐式等待的时间设置比较大，所以会按照隐式等待使用
        # dr.implicitly_wait(5)
        settings=by_clickable_located(located_settings)
        # 移动鼠标到指定位置(元素)
        action.move_to_element(settings).perform()
        # 睡两秒为了查看结果
        sleep(2)
    except NoSuchElementException as e:
        print('没有该元素')
    except ElementNotInteractableException as e:
        print('没有可交互元素')
    except TimeoutException as e:
        print('超时也没有找到元素')
    except Exception as e:
        #trace_back不需要每一个except都放，一般放在Exception中
        traceback.print_exc()
        # 使用os.path.join好处是解决跨平台问题
        # 截图当然是放在报错的时候截图，所以要放在EXception中且只用一次
        dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
    finally:
        # quit是关闭浏览器，close是关闭当前窗口
        dr.quit()

def test_ajax_loading():
    dr=create_dr()
    try:
        # 直接
        dr.get('https://www.taobao.com/')
        sleep(1)
        print('目前已经进入淘宝主页面了')
        located_input=(By.CSS_SELECTOR,'#q')
        get_input=by_clickable_located(located_input)
        get_input.click()
        get_input.clear()
        get_input.send_keys("手机")
        sleep(1)
        print('已经输入内容')
        located_search=(By.XPATH,'//button[contains(@class,"btn-search") and contains(@class,"tb-bg")]')
        get_search=by_clickable_located(located_search)
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


        located_username = (By.CSS_SELECTOR, "input.fm-text[aria-label='账号名/邮箱/手机号']")
        located_password = (By.CSS_SELECTOR, "input.fm-text[placeholder='请输入登录密码']")

        get_username=by_clickable_located(located_username)
        get_username.click()
        get_username.clear()
        human_typing(get_username,user)
        print('已经输入手机号')
        sleep(1)
        get_password=by_clickable_located(located_password)
        get_password.click()
        get_password.clear()
        human_typing(get_password,password)
        print('已经输入密码')
        sleep(1)
        located_login=(By.LINK_TEXT,'登录')
        get_login=by_clickable_located(located_login)
        get_login.click()
        print('已经登录')
        sleep(1)

    except NoSuchElementException as e:
        print('没有该元素')
    except ElementNotInteractableException as e:
        print('没有可交互元素')
    except TimeoutException as e:
        print('超时也没有找到元素')
    except Exception as e:
        #trace_back不需要每一个except都放，一般放在Exception中
        traceback.print_exc()
        # 使用os.path.join好处是解决跨平台问题
        # 截图当然是放在报错的时候截图，所以要放在EXception中且只用一次
        dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
    finally:
        dr.quit()


def test_clickable_vs_visible():
    dr=create_dr()
    try:
        dr.get(r'https://www.baidu.com')
        located_settings=(By.LINK_TEXT,'更多')
        by_clickable_located((By.TAG_NAME,'body')).click()
        sleep(1)
        # 条件和wait.until()结合使用
        wait.until(EC.any_of(EC.visibility_of_element_located((located_settings)),EC.element_to_be_clickable((located_settings))))
        
        action.move_to_element(by_clickable_located(located_settings)).perform()
        sleep(2)
    except ElementNotInteractableException as e:
        print('没有可交互元素')
    except NoSuchElementException as e:
        print('没有该元素')
    except TimeoutException as e:
        print('超时也没有找到元素')
    except Exception as e:
        #trace_back不需要每一个except都放，一般放在Exception中
        traceback.print_exc()
        # 使用os.path.join好处是解决跨平台问题
        # 截图当然是放在报错的时候截图，所以要放在EXception中且只用一次
        dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
    finally:
        dr.quit()

def test_custom_wait_condition():
    dr=create_dr()
    try:
        dr.get(r'https://www.baidu.com')
        located_input=(By.CSS_SELECTOR,'#chat-textarea')
        located_search=(By.CSS_SELECTOR,'#chat-submit-button')

        text='手机'
        by_clickable_located(located_input).send_keys(text)
        print(f'已经输入文本{text}')
        by_visible_located(located_search).click()
        print('已经成功点击百度一下')
        sleep(2)
        # 一般使用直接查找，EC全是条件用于先判断某个元素是否存在，存在则直接查找；
        # 自定义条件也是条件，因此需要和wait.until()结合轮训判断
        # 使用匿名函数默认传递driver
        # lambda(申明匿名函数) ：之前是参数，之后是函数体（且只能是一句话）
        wait.until(lambda d: len(d.find_elements(By.XPATH,'//div[@id="content_left"]/child::*')) >5)

    except ElementNotInteractableException as e:
        print('没有可交互元素')
    except TimeoutException as e:
        print('超时也没有找到元素')
    except NoSuchElementException as e:
        print('没有该元素')
    except Exception as e:
    #trace_back不需要每一个except都放，一般放在Exception中;放在finally中无论错误还是正确都会报错
        traceback.print_exc()
        # 使用os.path.join好处是解决跨平台问题
        # 截图当然是放在报错的时候截图，所以要放在EXception中且只用一次
        dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
    finally:
        dr.quit()

def main():
    print("=== 测试 1: 等待方式对比 ===")
    test_sleep_vs_wait()
    print("\n=== 测试 2: AJAX 加载处理 ===")
    test_ajax_loading()
    print('\n=== 测试 3: Clickable vs Visible ===')
    test_clickable_vs_visible()
    print("\n=== 测试 4: 自定义条件 ===")
    test_custom_wait_condition()

if __name__=="__main__":
    main()

