from selenium.webdriver.chrome.options import Options

options=Options()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled') ## 隐藏自动化特征
# 【关键】禁用"访问设备上的应用"权限（就是你截图中的弹窗）
options.add_argument('--disable-permissions-api')
# 同时禁用其他常见权限请求（建议全加上）
options.add_argument('--disable-notifications')      # 通知
options.add_argument('--disable-geolocation')        # 地理位置
options.add_argument('--disable-media-stream')       # 麦克风/摄像头

# 禁用" Chrome 正受到自动测试软件控制"的提示条（你截图左侧也有）
# options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)