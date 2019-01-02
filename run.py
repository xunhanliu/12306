import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from settings import *
from selenium.webdriver.chrome.options import Options
from login import Login
from order import Order
import pickle
from pyquery import PyQuery as pq
import os
from error import *   

class wait_city_appear(object):
    def __init__(self, cityName):
        self.cityName = cityName

    def __call__(self, driver):
        doc=pq(driver.page_source)
        length=doc("#panel_cities").children().length
        if length==0:
            print('0')
            return False
        else:
            for i in range(length):
                if doc("#citem_"+str(i)).find("span:nth-child(1)").text()==self.cityName:
                    return  driver.find_elements_by_id("citem_"+str(i))[0]  #坑逼，id竟然有双份
            print(length)
            print(self.cityName)
            return False

class text_to_be_present_in_element(object):

    def __init__(self, locator, text_):
        self.locator = locator
        self.text = text_

    def __call__(self, driver):
        try:
            element_text = driver.find_element(*self.locator).text
            if self.text in element_text:
                for i in driver.find_element(*self.locator):
                    if i.text == self.text:
                        return i
                return True
            else :
                return False
        except StaleElementReferenceException:
            return False





class RailwayTicket(object):
    def __init__(self,driver=None):
        ##测试阶段防止频繁登陆
        # if os.path.isfile("driver.pkl"):
        #     with open('driver.pkl', 'r') as f:
        #         self.driver = pickle.load(f)
        # else:
        #     self.driver=None
        # if not self.driver:  #为空
        #     chrome_options = Options()
        #     # 主要用于无界面运行
        #     # chrome_options.add_argument('--headless')
        #     # chrome_options.add_argument('--disable-gpu')
        #     self.driver = webdriver.Chrome(chrome_options=chrome_options)
        #     # self.driver.set_page_load_timeout(10)  #此处的代码，可能会导致后来的超时
        #     # self.driver.maximize_window()
        #     login = Login(self.driver)
        #     login.run()
        #     with open('driver.pkl', 'wb') as f:
        #         pickle.dump(self.driver, f)
        if not driver:
            chrome_options = Options()
            chrome_options.add_argument("--proxy-server=http://202.20.16.82:10152")
            # 主要用于无界面运行
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument('--disable-gpu')
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
            # self.driver.set_page_load_timeout(10)  #此处的代码，可能会导致后来的超时
            # self.driver.maximize_window()
        else:
            self.driver=driver
        self.wait=WebDriverWait(self.driver, 10)
    def __del__(self):
        # self.driver.close()
        pass
    def run(self):
        # load 从数据文件中读取数据，并转换为python的数据结构
        try:
            order = Order(self.driver)
            order.run()
        except LoginError:
            self.driver.close()
            # 获取代理
            r = requests.get('http://localhost:5000/get')
            proxy = r.text
            chrome_options = Options()
            chrome_options.add_argument("--proxy-server=%s"%('http://'+proxy))
            # 主要用于无界面运行
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(chrome_options=chrome_options)
            self.driver=driver
            self.run()
        a=0

    def getMyOrder(self):
        pass
if __name__ == '__main__':


    r = requests.get('http://localhost:5000/get')
    proxy = r.text
    chrome_options = Options()
   # chrome_options.add_argument("--proxy-server=%s" % ('http://' + proxy))
    # 主要用于无界面运行
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    railwayTicket = RailwayTicket(driver)
    railwayTicket.run()
