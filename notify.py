import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from settings import *
from pyquery import PyQuery as pq
from datetime import datetime as dt
from datetime import timedelta
from error import *
from login import Login,element_attr_to_be_present,element_attr_has_changed,login_url_has_ok
from mail import  Mymail
from time import clock,sleep
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

class presence_of_order_page(object):
    def __init__(self):
        pass
    def __call__(self, driver):
        if driver.find_elements_by_css_selector("#content_defaultwarningAlert_id"):  # alert  点击确定
            if driver.find_elements_by_css_selector("#content_defaultwarningAlert_id")[0].text.startswith( '车票信息已过期' ): #
                #点击确定，然后点击刷新  重新刷新页面
                return "refresh"
        style=driver.find_elements_by_css_selector(".modal-login")[0].get_attribute("style")
        # 登陆弹窗
        #有问题，这一块可能有延迟
        if not re.search(r'display.*?none', style):  # model框已经显示出来了 ，需要登陆
            print("need login")
            return "needLogin"
        if driver.find_elements_by_css_selector('#normal_passenger_id li label'):
            return "orderPage"
        return False
class Order(object):
    def __init__(self, driver=None):
        # self.driver = webdriver.Chrome()
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.actions = ActionChains(self.driver)
        self.retry=0
        self.fillPaceRetry=0
        self.start=clock()
        self.email = Mymail(receivers=["1638081534@qq.com", ], to_nickname="火车票信息")
        pass

    def __del__(self):
        pass
    def searchTecketClk(self):
        self.start=clock()
        self.retry+=1
        if self.retry>=10:
            raise RetryToMuch("搜索按钮超时")
        try:
            searchBtn = self.driver.find_elements_by_css_selector("#query_ticket")[0]
            self.actions.reset_actions()
            self.actions.click(searchBtn)
            self.actions.perform()
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#queryLeftTable tr"))
            )
            for train_number in TICKET.get('train_number'):
                train_number=train_number.upper()
                ticket = self.driver.find_elements_by_css_selector("tr[id*=%s]" % train_number)[0]
                ticketBtn = ticket.find_elements_by_css_selector(".no-br a")
                if ticketBtn:
                    seat_type=TICKET.get('seat_type')
                    WZ = ticket.find_elements_by_css_selector('td[hbdata$="#WZ_#"][id*="%s"]' % train_number)[0].text.strip()
                    YZ = ticket.find_elements_by_css_selector('td[hbdata$="#YZ_#"][id*="%s"]' % train_number)[0].text.strip()
                    YW = ticket.find_elements_by_css_selector('td[hbdata$="#YW_#"][id*="%s"]' % train_number)[
                        0].text.strip()
                    strHtml = "<p>%s</p>"%train_number
                    strHtml+="<p>"
                    strHtml += "<p>硬卧：%s</p>" % YW
                    strHtml += "<p>硬座：%s</p>" % YZ
                    strHtml += "<p>无座：%s</p>" % WZ
                    # 无票情况 '--'  '无'
                    if "硬卧" in seat_type:
                        if (YW=='--' or YW=='无'):  #无票，不通知
                            continue
                        else:
                            print(strHtml)
                            self.email.sendMail(subject="%s车次" % train_number, body=strHtml)
                            return train_number
                    elif "硬座" in seat_type:
                        if (YZ=='--' or YZ=='无') :  #无票，不通知
                            continue
                        else:
                            print(strHtml)
                            self.email.sendMail(subject="%s车次" % train_number, body=strHtml)
                            return train_number
                    elif "无座" in seat_type:
                        if (WZ=='--' or WZ=='无') :  #无票，不通知
                            continue
                        else:
                            print(strHtml)
                            self.email.sendMail(subject="%s车次" % train_number, body=strHtml)
                            return train_number
                else:
                    print("已经无票！")
                    continue
            print("无合适的票！")
            return False
        except TimeoutException:
            print("searchTecketClk Timeout")
            self.searchTecketClk()
    def fillPlace(self):
        self.fillPaceRetry+=1
        if self.fillPaceRetry>=10:
            raise RetryToMuch('fillPaceRetry')
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
        except TimeoutException:
            print("fillPlace timeOut")
            self.fillPlace()
    def freshTicket(self):
        '''
        刷到票才返回
        :return:
        '''
        for trainTime in TICKET.get("time"):
            # 票种选择
            if TICKET.get("ticket_type") == "学生票":
                ticketTypeClk = self.driver.find_elements_by_css_selector('#sf2_label')[0]
            else:
                ticketTypeClk = self.driver.find_elements_by_css_selector('#sf1_label')[0]
            self.actions.reset_actions()
            self.actions.click(ticketTypeClk)
            self.actions.perform()
            # 日期选择
            # 方案解决： click日期中的‘今天’  'cal-wamp cal-ft a'
            # 然后点击日期中的对应的cell
            mydate = trainTime
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
            calendar = self.driver.find_elements_by_css_selector('#date_icon_1')[0]
            self.actions.click(calendar)
            self.actions.click(todayClk)
            for i in range(int(monthInterval / 2)):  # 翻几次页
                self.actions.click(nextMonthClk)
            self.actions.click(calendar)
            self.actions.perform()

            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".cal-wrap >.cal-right > .cal-cm > div:nth-child(1) > div"))
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


            interval = clock() -self.start
            if interval < CHECK_FREQ:
                sleep(CHECK_FREQ - interval)
            self.retry=0
            result=self.searchTecketClk()
            if result:
                return result

    def loginOk(self,login):
        if self.retry>10:
            raise RetryToMuch("login retry")
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
            actions = ActionChains(self.driver)
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
    def run(self):
        self.fillPaceRetry=0
        self.fillPlace()
        trainNumber=self.freshTicket()
        while not trainNumber:  #无票
            trainNumber = self.freshTicket()
        #搜索页面，点击购票按钮
        orderBtn=self.driver.find_elements_by_css_selector("tr[id*=%s] .no-br a"%trainNumber)[0]
        self.actions.reset_actions()
        self.actions.click(orderBtn)
        self.actions.perform()
        result=self.wait.until(   #等3种情况之一  1，弹窗警告，2 登录弹窗  ,3 orderPage
            presence_of_order_page()
        )
        if result=="refresh":
            print("warning: 重新运行order")
            self.run()
        elif result=="needLogin":
            login = Login(self.driver)
            login.clickLoginBtn()
            self.retry = 0
            self.loginOk(login)
        elif result=="orderPage":
            pass

        self.orderPage()

    def orderPage(self):
        self.wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#normal_passenger_id li label"), TICKET.get('name'))
        )
        # 选择乘客
        peopleList = self.driver.find_elements_by_css_selector("#normal_passenger_id li label")
        for i in peopleList:
            for name in TICKET.get('name'):
                if i.text == name:
                    selPeople = i
                    #解决学生弹窗问题

                    self.actions.click(selPeople).perform()
                    style = self.driver.find_element_by_id("dialog_xsertcj").get_attribute("style")
                    if not re.search(r'display.*?none', style):  # 窗口弹出
                        self.actions.click(self.driver.find_element_by_id("dialog_xsertcj_ok")).perform()



                    # 选择票种
                    # ticket_type_list = self.driver.find_elements_by_css_selector("#ticketType_1 option")
                    # for i in ticket_type_list:
                    #     if re.search(TICKET.get('ticket_type'), i.text):
                    #         selTicketType = i
                    # 选择席别
                    seat_type_option = self.driver.find_elements_by_css_selector("select[id*=seatType] option")
                    seat_type = TICKET.get('seat_type')
                    flag=0
                    for seat in seat_type:
                        if flag :break
                        for i in seat_type_option:
                            if flag: break
                            if re.search(seat, i.text):
                                selSeatType = i
                                flag=True
                    self.actions.click(selSeatType).perform()

        submit = self.driver.find_elements_by_css_selector("#submitOrder_id")[0]
        # self.actions.click(submit).perform()
if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
    chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    order = Order(driver)
    order.run()
    # order.fillMess()



