import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from settings import *
from pyquery import PyQuery as pq
from datetime import datetime as dt
from datetime import timedelta
from error import *
from login import Login,element_attr_to_be_present,element_attr_has_changed,login_url_has_ok

class wait_city_appear(object):
    def __init__(self, cityName):
        self.cityName = cityName

    def __call__(self, driver):
        doc = pq(driver.page_source)
        length = doc("#panel_cities").children().length
        if length == 0:
            print('0')
            return False
        else:
            for i in range(length):
                if doc("#citem_" + str(i)).find("span:nth-child(1)").text() == self.cityName:
                    return driver.find_elements_by_id("citem_" + str(i))[0]  # 坑逼，id竟然有双份
            print(length)
            print(self.cityName)
            return False


class Order(object):
    def __init__(self, driver=None):
        # self.driver = webdriver.Chrome()
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.actions = ActionChains(self.driver)
        self.retry=0
        pass

    def __del__(self):
        pass
    def searchTecketClk(self):
        if self.retry>=10:
            raise RetryToMuch()
        try:
            searchBtn = self.driver.find_elements_by_css_selector("#query_ticket")[0]
            self.actions.reset_actions()
            self.actions.click(searchBtn)
            self.actions.perform()
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#queryLeftTable tr"))
            )

            train_number = TICKET.get('train_number').upper()
            ticket = self.driver.find_elements_by_css_selector("tr[id*=%s]" % train_number)[0]
            ticketBtn = ticket.find_elements_by_css_selector(".no-br a")[0]
            if ticketBtn:
                self.actions.reset_actions()
                self.actions.click(ticketBtn)
                self.actions.perform()
            else:
                print("已经无票！")
                return -1
        except TimeoutException:
            print("Timeout")
            self.searchTecketClk()

    def run(self):
        try:

            if TICKET.get("journey") == 'single':
                self.driver.get(SINGLE_TICKET)
            elif TICKET.get("journey") == 'round-trip':
                self.driver.get(ROUND_TRIP_TICKET)
            searchBtn = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#query_ticket"))
            )
            # 出发地选择
            sourceInput = self.driver.find_element_by_id("fromStationText")
            self.actions.reset_actions()
            self.actions.click(sourceInput)
            self.actions.perform()
            sourceInput.clear()
            sourceInput.send_keys(TICKET.get('sourcePinyin'))
            # stationSel= self.wait.until(  #返回可点击的目标
            #     wait_city_appear((By.CSS_SELECTOR, "#panel_cities"),TICKET.get('source'))
            # )
            stationSel = self.wait.until(  # 返回可点击的目标
                wait_city_appear(TICKET.get('source'))
            )

            self.actions.reset_actions()
            self.actions.move_to_element(stationSel)
            self.actions.click()
            self.actions.perform()

            # 目的地选择
            targetInput = self.driver.find_element_by_id('toStationText')
            self.actions.reset_actions()
            self.actions.click(targetInput)
            self.actions.perform()
            targetInput.clear()
            targetInput.send_keys(TICKET.get('targetPinyin'))
            stationSel = self.wait.until(  # 返回可点击的目标
                wait_city_appear(TICKET.get('target'))
            )
            self.actions.reset_actions()
            self.actions.move_to_element(stationSel)
            self.actions.click()
            self.actions.perform()
            # 日期选择
            # 方案解决： click日期中的‘今天’  'cal-wamp cal-ft a'
            # 然后点击日期中的对应的cell
            mydate = TICKET.get('time')
            mydate = dt.strptime(mydate, "%Y-%m-%d")
            now = dt.now()
            if mydate > now:  # 时间没问题
                pass
            elif (now - mydate).total_seconds() < 24 * 60 * 60 and mydate.day == now.day:  # 判断是否在同一天
                # 说明是当天的票
                pass
            else:
                raise TimeError("乘车日期不正确，为过去时")
            monthInterval = (mydate.month + 12 - now.month) % 12  # 0 1 不用翻页

            todayClk = self.driver.find_elements_by_css_selector('.cal-wrap > .cal-ft > a')[0]
            # 翻页  ".cal-wrap > .cal-right > .cal-top > .next"
            nextMonthClk = self.driver.find_elements_by_css_selector(".cal-wrap > .cal-right > .cal-top > .next")[0]
            # 左侧的月份 ".cal-wrap > div:nth-child(1) > .cal-cm > div:nth-child(2) > div"  cell
            # 右侧的月份 ".cal-wrap >.cal-right > .cal-cm > div:nth-child(2) > div"   cell

            self.actions.reset_actions()
            # date_icon_1
            calendar=self.driver.find_elements_by_css_selector('#date_icon_1')[0]
            self.actions.click(calendar)
            self.actions.click(todayClk)
            for i in range(int(monthInterval / 2)):  # 翻几次页
                self.actions.click(nextMonthClk)
            self.actions.click(calendar)
            self.actions.perform()

            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".cal-wrap >.cal-right > .cal-cm > div:nth-child(1) > div"))
            )
            self.actions.reset_actions()
            if monthInterval % 2 == 0:  # 左侧
                cellClk = self.driver.find_elements_by_css_selector(
                    ".cal-wrap > div:nth-child(1) > .cal-cm > div:nth-child(%d) > div" % mydate.day)[0]
            else:
                cellClk = self.driver.find_elements_by_css_selector(
                    ".cal-wrap >.cal-right > .cal-cm > div:nth-child(%d) > div" % mydate.day)[0]
            self.actions.move_to_element(cellClk)
            self.actions.click()
            self.actions.perform()
            # 点击搜索按钮
            # body : #queryLeftTable (双份)  未查询的时候是空
            self.retry = 0
            if self.searchTecketClk()==-1:
                self.run()
                return
        except TimeoutException:
            print("Timeout")


        # 解决弹窗，点击确定
        #登陆弹窗
        try:
            if self.driver.find_elements_by_css_selector("#content_defaultwarningAlert_id"):  # alert  点击确定
                if self.driver.find_elements_by_css_selector("#content_defaultwarningAlert_id")[0].text.startswith( '车票信息已过期' ): #
                    #点击确定，然后点击刷新  重新刷新页面
                    self.run()
                    return
            style=self.driver.find_elements_by_css_selector(".modal-login")[0].get_attribute("style")
            # 登陆弹窗
            #有问题，这一块可能有延迟
            if not re.search(r'display.*?none', style):  # model框已经显示出来了 ，需要登陆
                print("need login")
                login = Login(self.driver)
                login.clickLoginBtn()
                self.retry=0
                self.loginOk(login)

        except TimeoutException:
            print("Timeout1")

        try:
            self.wait.until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#normal_passenger_id li label"), TICKET.get('name'))
            )
            #选择乘客
            peopleList = self.driver.find_elements_by_css_selector("#normal_passenger_id li label")
            for i in peopleList:
                if i.text == TICKET.get('name'):
                    selPeople = i
            submit = self.driver.find_element_by_id("submitOrder_id")
            #选择票种
            ticket_type_list=self.driver.find_elements_by_css_selector("#ticketType_1 option")
            for i in ticket_type_list:
                if re.search(TICKET.get('ticket_type'), i.text):
                    selTicketType = i
            #选择席别
            seat_type_list = self.driver.find_elements_by_css_selector("#seatType_1 option")
            for i in seat_type_list:
                if re.search(TICKET.get('seat_type'), i.text):
                    selSeatType = i
            self.actions.reset_actions()
            self.actions.click(selPeople)
            self.actions.click(selTicketType)
            self.actions.click(selSeatType)
            self.actions.click(submit)
            self.actions.perform()



        except TimeoutException:
            print("Timeout2")
    def loginOk(self,login):
        if self.retry>10:
            raise RetryToMuch()
        try:
            self.wait.until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#normal_passenger_id li label"), TICKET.get('name'))
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
            login.clickLoginBtn()
            self.loginOk(login)

if __name__ == '__main__':
    order = Order(webdriver.Chrome())
    order.run()
