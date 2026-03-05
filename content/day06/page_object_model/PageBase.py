import os,sys
from pathlib import Path



PROJECT_PATH=Path(__file__).resolve().parent.parent
REPORT_PATH=os.path.join(PROJECT_PATH,'report')
ERROR_SCREENSHOT_PATH=os.path.join(PROJECT_PATH,'error_screenshot')

sys.path.insert(0,str(PROJECT_PATH))
from config.imports import *

# 定义一个装饰器，用于报错截图，并返回信息
# 模块级，需要使得该函数在使用的方法类上面，否则找不到
def error_screenshot(save_path:str)->None:
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args,**kargs):
            try:
                self=args[0]    # 第一个参数是self
                element=args[1][1]  # 第二个参数是locator
                timestamp=datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                file_path=os.path.join(save_path,f'error_{element}_{timestamp}.png')
                return func(*args,**kargs)
            except NoSuchElementException as e:
                self.driver.save_screenshot(file_path)
                raise NoSuchElementException(f'没能找到元素{element}，也许{element}元素不在DOM中，相关error图片已经保存') from e
            except TimeoutException as e:
                self.driver.save_screenshot(file_path)
                raise TimeoutException(f'超时也没能找到该元素{element}') from e
            except Exception as e:
                # except会逐一匹配从上至下，匹配则进入然后退出，不匹配则Exception万能会匹配raise e给上层处理（甩锅）
                self.driver.save_screenshot(file_path)
                # 工具函数不用traceback.print_exc()
                raise e
            # 工具函数直接往上层反馈信息，不用出，最后会有人处理。
        return wrapper
    return decorate


class PageBase:
    '''
        由单一动作：封装click send_keys get_arribute text;
        只是定义还未实现
    '''
    driver_count=0
    Locater=tuple[str,str]
    def __init__(self,driver: WebDriver,outTime:int=10):
        # 实例化对象driver
        self.driver=driver
        # 创建显示等待器
        self.wait=WebDriverWait(self.driver,outTime,0.5)
        # 创建行为器
        self.action=ActionChains(self.driver)
        # 对象是具体的一个，类是可以多个的。类属性多个实例之间是共用的
        PageBase.driver_count+=1
        # 实例对象是不用return的，带self
        # return self.driver,self.wait,self.action

    def open_url(self,url:str):
        self.driver.get(url)

    def get_attribute_value(self,locator:Locater,attr_name:str='href'):
        return self.find_clickable_element(locator).get_attribute(attr_name)

    # 工具用于返回有多少个对象被实例化
    # 装饰器没有参数就直接没有括号，定义时，就会执行
    @classmethod
    def get_cur_obj_nums() -> int:
        # 可以通过直接类名返回该类的属性（类属性）
        # 也可以定义类方法通过第一个参数cls返回cls.driver_count
        return PageBase.driver_count
    
    # 下面开始定义一些常用且公用的基础方法
    @error_screenshot(ERROR_SCREENSHOT_PATH)
    def find_element(self,element_located:Locater) -> WebElement:
        # 卫生要有self,因为self代表的是当前实例化对象，且只有实例化对象能用带self的方法
        return self.wait.until(EC.presence_of_element_located(element_located))
    #presence visibility clickable都是当前条件且能返回元素的对象（单复一样）


    @error_screenshot(ERROR_SCREENSHOT_PATH)
    def find_clickable_element(self,element_located:Locater) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable(element_located))


    def click_element(self,locater:Locater)->None:
        self.find_clickable_element(locater).click()

    def input_text(self,locater:Locater,searched_text)->None:
        element=self.find_clickable_element(locater)
        # 需要先选中，然后清空原有值，最后再输入搜索文本
        element.click()
        element.clear()
        element.send_keys(searched_text)

    def move_to_element(self,locator:Locater):
        self.action.move_to_element(self.find_clickable_element(locator)).perform


    @error_screenshot(ERROR_SCREENSHOT_PATH)
    def switch_to_frame(self,locater:Locater) -> None:
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(locater))

    def switch_to_default(self):
        # 切回主窗口
        self.driver.switch_to.default_content()

    def is_diplayed(self,locater:Locater):
        if self.find_element(locater).is_displayed():
            return True
        else:
            return False
        