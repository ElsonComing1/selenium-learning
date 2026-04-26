from typing import Union,List,Generator
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException,ElementNotInteractableException
from selenium.webdriver.remote.webelement import WebElement  # 补充导入
from selenium.webdriver.remote.webdriver import WebDriver  # 补充导入
from datetime import datetime
import functools
from time import sleep