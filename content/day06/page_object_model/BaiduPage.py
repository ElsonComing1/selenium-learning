from PageBase import *

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
    search_button_locator=(By.LINK_TEXT,'百度一下')
    # text_frame_locator=(By.ID,'kw')
    # search_button_locator=(By.ID,'su')
    tieba_locator=(By.XPATH,'//div[@id="s-top-left"]/a[4]')
    settings_locator=(By.XPATH,'//div[@id="u1"]/a')
    body_locator=(By.TAG_NAME,'body')
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
        self.input_text(self.text_frame_locator,key_word)
        self.click_element(self.body_locator)
        self.switch_to_default()
        self.click_element(self.search_button_locator)
        return self
        # 没有具体的值需要返回就直接返回self(当前对象所在进度)

    def open_settings(self):
        if self.is_diplayed(self.settings_locator):
            self.move_to_element(self.settings_locator).click_element(self.settings_locator)
        else:
            raise ValueError(f'没有发现该元素{self.settings_locator}')

    def get_search_text(self):
        text=self.get_attribute_value(self.text_frame_locator,'value')
        return text
    
        




if __name__=='__main__':
    pass
