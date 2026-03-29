import os,sys,allure
from pathlib import Path



PROJECT_PATH=str(Path(__file__).resolve().parent.parent)
REPORT_PATH=str(os.path.join(PROJECT_PATH,'report'))
ERROR_SCREENSHOT_PATH=os.path.join(PROJECT_PATH,'error_screenshot')

sys.path.insert(0,str(PROJECT_PATH))
from config.imports import *

# 定义一个装饰器，用于报错截图，并返回信息
# 模块级，需要使得该函数在使用的方法类上面，否则找不到
def error_screenshot(save_path:str)->None:
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args,**kargs):
            self=args[0]    # 第一个参数是self
            element=args[1][1] if len(args[1])>1 else (args[1],None)  # 第二个参数是locator
            try:
                return func(*args,**kargs)
            except (TimeoutException,NoSuchElementException,ElementNotInteractableException) as e:
                _take_screenshot(self,save_path,func.__name__,element)
                raise type(e)(f'没能找到元素{element}，也许{element}元素不在DOM中，相关error图片已经保存') from e
            except Exception as e:
                _take_screenshot(self,save_path,func.__name__,element)
                raise type(e)(f'异常捕获：{e}') from e
                # 越底层越是raise上抛问题，不处理，交给pyetst(外层)
        def _take_screenshot(slef,external_path,func_name,element):
            timestamp=datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            file_path=os.path.join(external_path,f'{func_name.__name__}_error_{element}_{timestamp}.png')
            os.makedirs(os.path.join(save_path,f'{dir_name}'),exist_ok=True)
            self.driver.save_screenshot(file_path)
        return wrapper
    return decorate


class PageBase:
    '''
        由单一动作：封装click send_keys get_arribute text;
        只是定义还未实现，个人习惯，可以的最底层直接返回bool值，方法切得及其简单，甚至就是套一层名字（单个动作）。外层要见名知义（多个动作，返回self(链式调用)）
        self的实例属性不用返回，继承该类的方法都会有。
    '''
    driver_count=0
    Locater=tuple[str,str]
    def __init__(self,driver: WebDriver,outTime:int=180):
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
        for i in range(3):
            try:
                self.driver.get(url)
                return True
            except Exception as e:
                if i < 3 - 1:
                    raise e
                    time.sleep(3)
                else:
                    raise

    def get_attribute_value(self,locator:Locater,attr_name:str='href'):
        return self.find_clickable_element(locator).get_attribute(attr_name)

    # 工具用于返回有多少个对象被实例化
    # 装饰器没有参数就直接没有括号，定义时，就会执行
    @staticmethod
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
        sleep(1)
        return self.wait.until(EC.element_to_be_clickable(element_located))


    def click_element(self,locater:Locater):
        sleep(1)
        self.find_clickable_element(locater).click()
        return self

    def input_text(self,locater:Locater,searched_text)->None:
        element=self.find_clickable_element(locater)
        # 需要先选中，然后清空原有值，最后再输入搜索文本
        element.click()

        element.clear()

        element.send_keys(searched_text)
        return self


    def move_to_element(self,locator:Locater):
        self.action.move_to_element(self.find_clickable_element(locator)).perform()
        return self


    @error_screenshot(ERROR_SCREENSHOT_PATH)
    def switch_to_frame(self,locater:Locater):
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(locater))
        return True

    def switch_to_default(self):
        # 切回主窗口
        self.driver.switch_to.default_content()
        return True

    def is_diplayed(self,locater:Locater):
        if self.find_element(locater).is_displayed():
            return True
        else:
            return False

    def check_title(self,expected:str)->bool:
        '''用于判断页面跳转是否成功'''
        return bool(self.wait.until(EC.title_contains(expected)))
    
    def get_title(self):
        return self.driver.title

    def attach_important_element_png(self,element:WebElement,picture_name:str='重要元素截图'):
        allure.attach(
            element.screenshot_as_png,
            name=picture_name,
            attachment_type=allure.attachment_type.PNG
        )        

