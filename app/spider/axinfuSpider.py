import time
try:
    from .baseSpider import BaseSpider

except :
    from baseSpider import BaseSpider

loginURL = 'https://h5.axinfu.com/login/login'
ecardURL = 'https://h5.axinfu.com/getEcard'
chargeURL = 'https://h5.axinfu.com/ecard/ecard-recharge'


class AxinfuSpider(BaseSpider):
    def __init__(self, mobile, password):
        super().__init__()
        self.mobile = mobile
        self.password = password

    def login(self):
        data = {
            'mobile': self.mobile,
            'password': self.password,
            'statu': 'OK'
        }
        resp = super().get_html(loginURL, 'POST', data)
        return resp.text

    def getECard(self):
        time.sleep(1)
        resp = super().get_html(ecardURL, 'GET')
        result = resp.json()
        return result


