# BaiduPage.py
from .PageBase import *

PROJECT_PATH=Path(__file__).resolve().parent.parent


# 类名与文件名一致
class BaiduPage(PageBase):
    '''
        该类由 元素 + 单一动作组合（打开首页；搜索东西；甚至单一懂也会被套在一个方法里面而已）；也只是定义为实现，但方法更"实例生动"一些了，因此方法名得形象；基础类得生硬
        只用更改该类的元素定位，即可，不用更改基础方法，已经动作组装的逻辑=测试流程
        写注释便于程序员快速上手
    '''
    # 元素定位
    text_frame_locator=(By.ID,'chat-textarea')
    search_button_locator=(By.ID,'chat-submit-button')
    # text_frame_locator=(By.ID,'kw')
    # search_button_locator=(By.ID,'su')
    tieba_locator=(By.XPATH,'//div[@id="s-top-left"]/a[4]')
    settings_locator=(By.XPATH,'//div[@id="u1"]/span')
    body_locator=(By.TAG_NAME,'body')

    user_name_locator=(By.ID,'userName')
    password_locator=(By.ID,'password')
    login_button_locator=(By.ID,'login')
    result_check_locator=(By.ID,'name')
    # 该类的全部方法需要将以上的locator包含完
    # 以上变量，要么是实例self.变量获取（实例属性），要么类名.变量获取（类属性），不能直接变量。只有两种

    def open_target_page(self,url:str):
        if url:
            self.open_url(url)
            # 该文件的重点，链式调用，没有别的返回值或者状态判断，就返回self
            return self
        else:
            # 打开页面不用返回
            raise ValueError(f'输入的url值不对，输入的值是:{url}')
    
    def search_content(self,key_word:str):
        # 形象的方法就不用将locator再作为参数传入，本类里已有
        if self.move_to_element(self.text_frame_locator):
            self.input_text(self.text_frame_locator,key_word)
        # self.input_text(self.text_frame_locator,key_word)
        if self.move_to_element(self.search_button_locator):
            self.click_element(self.search_button_locator)
        # sleep(3)
        if self.check_title(key_word):
            return self
        return None
        # 没有具体的值需要返回就直接返回self(当前对象所在进度)

    def open_settings(self):
        if self.is_diplayed(self.settings_locator):
            if self.move_to_element(self.settings_locator):
                self.click_element(self.settings_locator)
                sleep(3)
                self.attach_important_element_png_by_locator(self.settings_locator,'设置元素截图')
            else:
                raise
            return self
        else:
            raise ValueError(f'没有发现该元素{self.settings_locator}')

    def get_search_text(self):
        text=self.get_attribute_value(self.text_frame_locator,'value')
        return text

    def get_result_text(self):
        text=self.find_element(self.result_check_locator).text
        return text

    def login_to_target(self,username,passwd):
        self.input_text(self.user_name_locator,username)
        sleep(1)
        self.input_text(self.password_locator,passwd)
        sleep(1)
        self.click_element(self.login_button_locator)
        sleep(1)
        return self
    
    def attach_important_element_png_by_locator(self,locater,picture_name):
        element=self.driver.find_element(*locater)
        if element:
            self.attach_important_element_png(element,picture_name)
    
        




if __name__=='__main__':
    pass
