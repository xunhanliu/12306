
PIC="12306.jpg"


ACCOUNT=""
PASSWORD=""

PAGE_INDEX="https://www.12306.cn/index"
LOGIN_INDEX="https://kyfw.12306.cn/otn/resources/login.html"
LOGIN_OK="https://kyfw.12306.cn/otn/view/index.html"
SINGLE_TICKET="https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
ROUND_TRIP_TICKET="https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
TICKET={
    'name':[,],  #乘车人
    'time':["2019-1-26","2019-1-27","2019-1-28","2019-1-29","2019-1-30","2019-1-31",], #乘车时间
    "source":"天津",
    'sourcePinyin':"tianjin",
    "target":"商丘",
    "targetPinyin":"shangqiu",
    'journey':'single', #"round-trip" / 'single'
    'train_number':["K1622"],
    'ticket_type':"成人票"  #儿童票，成人票，学生票，残军票
    ,'seat_type':["硬卧",'硬座']#硬座，无座
}

CHECK_FREQ=3  #3S  多久点一次search