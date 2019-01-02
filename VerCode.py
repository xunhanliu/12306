# from pic  get result   (返回一个字符串 例如 35 ，图片从左到右依次编号1-8)

from settings import *
from error import *
# from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.chrome.options import Options
from pyquery import PyQuery as pq
import requests
class VerCode(object):
    def __init__(self):
        self.verCodeURL="http://littlebigluo.qicp.net:47720"
        # chrome_options = Options()
        # #主要用于无界面运行
        # # chrome_options.add_argument('--headless')
        # # chrome_options.add_argument('--disable-gpu')
        # self.driver = webdriver.Chrome(chrome_options=chrome_options)
        # self.driver.set_page_load_timeout(10)  #此处的代码，可能会导致后来的超时
        # self.driver.maximize_window()
        # browser = self.driver
        # self.wait=WebDriverWait(browser, 10)
        # try:
        #     browser.get(self.verCodeURL)
        #     element = self.wait.until(
        #         EC.element_to_be_clickable((By.TAG_NAME, "form"))
        #     )
        #
        #
        #     input = browser.find_element_by_id('kw')
        #     input.send_keys('Python')
        #     input.send_keys(Keys.ENTER)
        #
        #     self.wait.until(EC.presence_of_element_located((By.ID, 'content_left')))
        #     print(browser.current_url)
        #     print(browser.get_cookies())
        #     print(browser.page_source)
        # except TimeoutException:
        #     print("Timeout!")
        # finally:
        #     browser.close()
    def get_result(self):
        files={'file':open(PIC,'rb')}
        r=requests.post(self.verCodeURL,files=files)
        if(r.status_code!=200):
            raise StatusError()
        if '抱歉!系统访问过于频繁，请稍后再试' in r.text:
            raise ResultError('verCode 访问过于频繁！')
        doc=pq(r.text)
        str=doc("font B").text().replace(" ",'')
        return str

if __name__ == '__main__':
    verCode=VerCode()
    print(verCode.get_result())