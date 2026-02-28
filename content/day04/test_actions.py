from all_kinds_of_import import *
from config import *


def create_dr_wait_action():
    dr=None
    try:
        dr=webdriver.Chrome(options=options)
        wait=WebDriverWait(dr,10,0.5)
        actions=ActionChains(dr)
        return dr,wait,actions
    except Exception as e:
        if dr:
            dr.quit()
        raise Exception('创建失败') from e
        # 此处是工具函数实际上可以不需要的
def get_element(wait,k_v):
    try:
        return wait.until(EC.element_to_be_clickable(k_v))
    # 范围又小到大，clickable < visiblity < presence (前面存在，则后面一定存在，且该三条件的判断可以返回值，包括是列表的返回)
    except Exception as e:
        raise Exception(f'没有得到{k_v[1]}') from e


def test_drag_and_drop():
    try:
        dr,wait,actions=create_dr_wait_action()
        dr.get('https://demoqa.com/droppable')
        sleep(5)
        origin_located=(By.ID,'draggable')
        destetion_located=(By.ID,'droppable')
        
        sleep(2)
        get_origin=get_element(wait,origin_located)
        print('已经获得元素origin')
        sleep(1)
        get_destetion=get_element(wait,destetion_located)
        print('已经获得元素destetion')
        sleep(1)
        actions.drag_and_drop(get_origin,get_destetion).perform()
        assert 'Drop Here' in get_destetion.text
        print('我已经完成拖拽')
        # 每一个动作都需要perform才会执行
        # drag_and_drop是元素到元素，更像人机
        # click_and_hold().move_by_offset().release() 是象素控制，且是相当于当前元素的象素。
        sleep(2)
    except NoSuchElementException as e:
        traceback.print_exc()
        # 测试函数的每一个测试类型都需要有一个堆栈打印，先打印再raise
        raise NoSuchElementException(f'没有找到匹配元素') from e
        # 报错会找到对应类型错误返回
        # 测试函数不像工具函数必须raise有try except
    except Exception as e:
        traceback.print_exc()
        if dr:
            # 该方法适用于多平台
            dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
        raise
    finally:
        # 在哪一个函数里创建的dr, 就该在哪一个函数里关闭
        dr.quit()

def test_drag_by_offset():
    try:
        dr,wait,actions=create_dr_wait_action()
        dr.get('https://demoqa.com/dragabble')
        sleep(5)
        origin_located=(By.ID,'dragBox')

        sleep(2)
        get_origin=get_element(wait,origin_located)
        print('已经获得元素origin')
        sleep(1)
        # 直接使用clickable返回的元素更实时
        actions.move_to_element(get_origin).click().click_and_hold().move_by_offset(200,0).pause(1).release().perform()
        # actions.drag_and_drop_by_offset(get_origin,200,100).perform()
        # assert 'Drag Me' in origin_located.text
        print('我已经完成准确位置移动')
        # 每一个动作都需要perform才会执行
        # drag_and_drop是元素到元素，更像人机
        # click_and_hold().move_by_offset().release() 是象素控制，且是相当于当前元素的象素,更像人
        sleep(2)
    except Exception as e:
        print('当前测试方法test_drag_by_offset出问题了')
        traceback.print_exc()
        if dr:
            # 该方法适用于多平台
            dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
        raise
    finally:
        # 在哪一个函数里创建的dr, 就该在哪一个函数里关闭
        dr.quit()

def test_keys_combinations():
    try:
        dr,wait,actions=create_dr_wait_action()
        print('开始访问网页')
        dr.get('https://www.baidu.com')
        sleep(2)
        origin_located=(By.ID,'chat-textarea')

        sleep(1)
        get_origin=get_element(wait,origin_located)

        # actions没有属性clear()
        # send_keys是 key_down 与key_up的结合版
        # 在ctrl期间的send_keys是被控制的不会输入进去
        actions.click(get_origin) \
            .send_keys('selenium自动化') \
            .pause(1) \
            .send_keys(Keys.END) \
            .pause(1) \
            .key_down(Keys.SHIFT) \
            .send_keys(Keys.HOME) \
            .pause(1) \
            .key_up(Keys.SHIFT) \
            .pause(1) \
            .key_down(Keys.CONTROL) \
            .pause(1) \
            .send_keys("x") \
            .pause(1) \
            .perform()
        sleep(2)
        print('组合键已完成\n下面将会是显示组合菜单')
        actions.context_click(get_origin).perform()
        # perform会使得actions的全部动作一一完成
        sleep(2)
        print('恭喜你，你已经完成了')
    except Exception as e:
        print('当前测试方法test_keys_combinations出问题了')
        traceback.print_exc()
        if dr:
            # 该方法适用于多平台
            dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
        raise
    finally:
        # 在哪一个函数里创建的dr, 就该在哪一个函数里关闭
        # 无论失败还是成功，最后一步都是这儿
        dr.quit()

def test_window_switch():
    try:
        dr,wait,actions=create_dr_wait_action()
        print('开始访问网页')
        dr.get('https://www.baidu.com')
        sleep(2)
        current_window=dr.current_window_handle
        print(f'当前窗口是{current_window},其主题是:{dr.title}')
        sleep(1)
        dr.execute_script('window.open("https://news.baidu.com","_blank")')
        # 使用javascript语法来控制web, _blank是强制开启新窗口
        print(f'当前窗口还是{dr.current_window_handle}')
        sleep(1)
        windows=dr.window_handles
        print(f'当前窗口数量是{len(windows)},最后一个窗口值是{windows[-1]}')
        sleep(1)
        dr.switch_to.window(windows[-1])
        print(f'当前窗口已经是最新窗口{dr.current_window_handle},他的主题是:{dr.title}')
        sleep(1)
        dr.close()
        print('已经关闭了当前窗口，默认退回第一个窗口')
        sleep(2)
    except Exception as e:
        print('当前测试方法test_window_switch出问题了')
        traceback.print_exc()
        if dr:
            # 该方法适用于多平台
            dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
        raise
    finally:
        # 在哪一个函数里创建的dr, 就该在哪一个函数里关闭
        # 无论失败还是成功，最后一步都是这儿
        dr.quit()
def test_alert_handling():
    try:
        dr,wait,actions=create_dr_wait_action()
        print('开始访问网页')
        dr.get('https://demoqa.com/alerts')

        alert_located=(By.ID,'alertButton')
        get_alert=get_element(wait,alert_located)
        print('你已经后的alert元素')
        get_alert.click()
        sleep(1)
        print('你已近点击出发警告框,要控制警告框需要你先进入该框')
        alert=dr.switch_to.alert
        sleep(1)
        print(f'获得当前文本内容是{alert.text}')
        sleep(1)
        print('下面我将确认警告框')
        alert.accept()
        sleep(1)

        confirm_located=(By.ID,'confirmButton')
        get_confirm=get_element(wait,alert_located)
        sleep(1)
        get_confirm.click()
        confirm=dr.switch_to.alert
        print('已经获得确认框')
        sleep(1)
        print(f'当前文本是{confirm.text}')
        confirm.dismiss()
        print('你已经拒绝切关闭了该弹窗')

        prompt_located=(By.ID,'promtButton')
        get_prompt=get_element(wait,prompt_located)
        print('你已经获得元素prompt')
        sleep(1)
        get_prompt.click()
        prompt=dr.switch_to.alert
        print('你已经触发prompt，你可以输入信息')
        prompt.send_keys('selenium学习')
        sleep(2)
        print('你已经输入内容')
        prompt.accept()
        print('都完成了')
        sleep(1)
    except Exception as e:
        print('当前测试方法test_alert_handling出问题了')
        traceback.print_exc()
        if dr:
            # 该方法适用于多平台
            dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
        raise
    finally:
        # 在哪一个函数里创建的dr, 就该在哪一个函数里关闭
        # 无论失败还是成功，最后一步都是这儿
        dr.quit()

def test_file_upload():
    try:
        dr,wait,actions=create_dr_wait_action()
        print('开始访问网页')
        dr.get('https://demoqa.com/upload-download')

        upload_located=(By.ID,'uploadFile')
        get_upload=get_element(wait,upload_located)
        print('你已经获得upload元素')
        # 使用这种方式便于他人使用
        get_upload.send_keys(os.path.join(os.path.dirname(__file__),'test_data','sampleFile.jpeg'))
        sleep(1)
        print('你已经输入文件名')
        status_locaed=(By.ID,'uploadedFilePath')
        get_status=get_element(wait,status_locaed)
        dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
        get_status.screenshot(os.path.join('day04','point_shot',f'{status_locaed[1]}.png'))
        print(f'你输入的信息是{get_status.text}')
        sleep(2)
    except Exception as e:
        print('当前测试方法test_file_upload出问题了')
        traceback.print_exc()
        if dr:
            # 该方法适用于多平台
            dr.save_screenshot(os.path.join('error_screenshot','error_screenshot.png'))
        raise
    # 测试函数需要raise 且在这之前需要打印堆栈，知道错在哪里，最后是Exception兜底如果前面的错误类型都不是；如果匹配到了就会跳出
    finally:
        # 在哪一个函数里创建的dr, 就该在哪一个函数里关闭
        # 无论失败还是成功，最后一步都是这儿
        dr.quit()


def main():
    results = []
    test_alert_handling()
    tests = [test_drag_and_drop, test_drag_by_offset, test_keys_combinations,test_window_switch,test_alert_handling,test_file_upload]
    # 一切皆对象
    
    for test in tests:
        try:
            test()
            # 逐一调用
            results.append(f"✅ {test.__name__} 通过")
        except Exception as e:
            results.append(f"❌ {test.__name__} 失败")
            # 不能raise了，我就是最上层，用于分析谁过了，谁没过，也可以计数；就是汇总统计，重点是程序不会崩溃
            # main函数下的except会处理全部报错的函数
    
    # 最终报告
    print("\n".join(results))
    # 这里不需要 raise，因为已经记录所有结果了




if __name__=='__main__':
    main()


# 多个except只会匹配对应类型，但是父类Exception只能放在最后
# 测试函数需要有raise返回给主函数,主函数有不raise扛事儿的，就是有错有对

# 工具函数（如 get_element）：不捕获 或 捕获后必须添加信息再 raise
# 测试函数：必须 raise，否则测试框架不知道失败了
# 入口函数（main）：不 raise，捕获所有异常并生成报告

