from selenium.webdriver import ActionChains
from settings import *
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
import requests
from urllib.parse import urljoin
import base64
import time
from VerCode import VerCode
import random
from PIL import Image
from error import *
class element_attr_to_be_present(object):
    def __init__(self, locator, attrName,reStr):
        self.locator = locator
        self.attrName=attrName
        self.reStr=reStr
    def __call__(self, driver):
        element = driver.find_element(*self.locator)  # Finding the referenced element
        if element:
            attrValue=element.get_attribute(self.attrName)
            if attrValue:
                result=re.search(self.reStr, attrValue).group()
                if result:
                   return element
        return False
class element_attr_has_changed(object):
    def __init__(self, locator,attrName):
        self.attrName=attrName
        self.locator = locator
        self.lastValue=''
        self.isFirstTime=True
    def __call__(self, driver):
        element = driver.find_element(*self.locator)  # Finding the referenced element
        if self.isFirstTime:
            self.lastValue= element.get_attribute(self.attrName)
            return False
        else:
            attrValue=element.get_attribute(self.attrName)
            if self.lastValue !=attrValue:
                return True
            else:
                return False
class login_url_has_ok(object):
    def __init__(self,login_ok_url):
        self.login_ok_url = login_ok_url
    def __call__(self, driver):
        if self.login_ok_url in driver.current_url:
            return True
        else:
            return False

class Login(object):
    def __init__(self,drive=None):
        #self.drive=drive
        self.verCode=VerCode()
        self.drive=drive
        self.wait = WebDriverWait(self.drive, 10)
        self.pic_rect=""
        self.retry=0
    def __del__(self):
        pass

    def clickLoginBtn(self):
        account_login = self.wait.until(  # 账号登录
            EC.presence_of_element_located((By.CSS_SELECTOR, ".login-hd-account a"))
        )
        actions = ActionChains(self.drive)
        actions.click(account_login)
        actions.perform()  # 点击账号登录
        # 下载图片
        pic_loaded = self.wait.until(  # 账号登录
            element_attr_to_be_present((By.ID, "J-loginImg"), 'src', r'base64,')
        )
        self.pic_rect = pic_loaded.rect
        pic_base64 = pic_loaded.get_attribute("src")
        pos = pic_base64.find("base64,")
        if pos == -1:  # 是http
            img = requests.get(urljoin(self.drive.current_url, pic_base64))
            img = img.content
        else:
            pic_base64 = pic_base64[pos + 7:]
            img = base64.b64decode(pic_base64)

        with open(PIC, 'wb') as f:
            f.write(img)
        #看是否是请求频繁的错误
        template0 = Image.open("later_retry.jpg")
        template1=Image.open("12306.jpg")
        if self.same_image(template0, template1):
            raise LoginError("12306,您的登陆过于频繁，已经刷不出验证码！应该是IP被封")
        recognition = self.verCode.get_result()
        # 从图片中获取9个坐标
        pos = self.picClick(recognition)

        userName = self.drive.find_element_by_id("J-userName")
        userName.clear()
        userName.send_keys(ACCOUNT)
        password = self.drive.find_element_by_id("J-password")
        password.clear()
        password.send_keys(PASSWORD)

        login_btn = self.drive.find_element_by_id("J-login")
        actions = ActionChains(self.drive)
        for i in pos:
            actions.move_to_element_with_offset(pic_loaded, i[0], i[1])
            actions.click()
        actions.click(login_btn)
        actions.perform()  # 点击立即登录
    def run(self):
        if self.retry>10:
            print("retry count has more than 10,exit!")
            return
        try:
            self.drive.get(PAGE_INDEX)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#J-header-logout a"))
            )
            style=self.drive.find_element_by_id("J-header-logout").get_attribute("style")
            if not re.search(r'display.*?none', style).group():   # none  已经登录
                print("had login")
                return
                pass
            else: #未登录
                # print("had logout")
                #点击登录
                login_btn=self.drive.find_element_by_css_selector("#J-header-login > a:nth-child(1)")
                if '登录' in login_btn.text:
                    actions = ActionChains(self.drive)
                    actions.move_to_element(login_btn)
                    actions.click(login_btn)
                    actions.perform()
                    self.clickLoginBtn()
        except TimeoutException:
            print("TimeoutError")
            self.retry+=1
            self.run()
        self.retry = 0
        self.loginOk()
        self.retry=0
    def loginOk(self):
        if self.retry>10:
            print("retry count has more than 10,exit!")
            return
        try:
            self.wait.until(  # 账号登录
                login_url_has_ok(LOGIN_OK)
            )
        except TimeoutException:
            print("验证码错误，或者超时")
            #刷新验证码 重新登录
            pic_loaded = self.wait.until(  # 账号登录
                element_attr_to_be_present((By.ID, "J-loginImg"), 'src', r'base64,')
            )
            actions = ActionChains(self.drive)
            actions.move_to_element_with_offset(pic_loaded, 288, 13)
            actions.click()
            actions.perform()  # 点击更新按钮

            try:
                self.wait.until(  # 等待图片更新
                    element_attr_has_changed((By.ID, "J-loginImg"), 'src')
                )
            except TimeoutException:
                print("图片并未更新")
            self.clickLoginBtn()
            self.loginOk()

    def picClick(self,recognition):  #recognition是一个字符串
        if self.pic_rect:
            height=self.pic_rect['height']
            width=self.pic_rect['width']
            pos=[]
            y=40
            # recognition+="1"
            for i in recognition:
                yOffset=int((int(i)-1)/4)*(height-y)/2 +y
                xOffset=(int(i) - 1) % 4 *width/4
                ra = random.random() * width / 8 - width / 16
                yOffset=yOffset+width/8+ra
                ra = random.random() * width / 8 - width / 16
                xOffset = xOffset + width / 8 + ra
                pos.append([xOffset,yOffset])
            return pos

    def same_image(self, image, template):

        threshold = 0.99
        count = 0
        for x in range(image.width):
            for y in range(image.height):
                # 判断像素是否相同
                if self.is_pixel_equal(image, template, x, y):
                    count += 1
        result = float(count) / (image.width * image.height)
        if result > threshold:
            print('图片相似度很高')
            return True
        return False

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 20
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False


if __name__=="__main__":
    driver = webdriver.Chrome()
    login=Login(driver)
    login.run()