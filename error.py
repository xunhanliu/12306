class StatusError(Exception):

    def __init__(self,mess=None):
        Exception.__init__(self)
        self.mess=mess
    def __str__(self):
        print('The status_code is not 200!:',self.mess)  #字符串会加引号

class TimeError(Exception):

    def __init__(self,mess=None):
        Exception.__init__(self)
        self.mess=mess
    def __str__(self):
        print('Time Error!:',self.mess)  #字符串会加引号
class LoginError(Exception):

    def __init__(self,mess=None):
        Exception.__init__(self)
        self.mess=mess
    def __str__(self):
        print('Login Error!:',self.mess)  #字符串会加引号


class ResultError(Exception):

    def __init__(self,mess=None):
        Exception.__init__(self)
        self.mess = mess
    def __str__(self):
        print('接口无返回结果！！：',self.mess)


class RetryToMuch(Exception):

    def __init__(self,mess=None):
        Exception.__init__(self)
        self.mess = mess
    def __str__(self):
        print('RetryToMuch：',self.mess)

#
# class PoolEmptyError(Exception):
#
#     def __init__(self):
#         Exception.__init__(self)
#
#     def __str__(self):
#         return repr('The proxy pool is empty')
