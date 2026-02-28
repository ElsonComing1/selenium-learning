from selenium.webdriver.chrome.options import Options
options=Options()
options.add_argument('--disable-blink-featrues=AutomationControlled')
options.add_argument('--start-Maximized')
options.add_argument('--disable-permission-api')
options.add_argument('--disable-mediea-stream')
options.add_argument('--disable-geolocation')
options.add_argument('--disable-notifications')
options.add_experimental_option('useAutomationExtension', False)