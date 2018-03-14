import re
from requests.exceptions import ReadTimeout
from threading import Thread
from flask import current_app
try:
    from .baseSpider import BaseSpider
    from .decorators import retry_task
    from .. import db
    from ..models import WechatUser
except :
    from baseSpider import BaseSpider
    from decorators import retry_task


bxqURL = 'http://60.219.165.24/bxqcjcxAction.do'
loginURL = 'http://60.219.165.24/loginAction.do'
gradeURL = 'http://60.219.165.24/gradeLnAllAction.do?type=ln&oper=fainfo&fajhh=3468'
stuinfoURL = 'http://60.219.165.24/xjInfoAction.do?oper=xjxx'
resultUrl = 'http://60.219.165.24/gradeLnAllAction.do?type=ln&oper=qbinfo&lnxndm=2016-2017%D1%A7%C4%EA%' \
                         'B5%DA%D2%BB%D1%A7%C6%DA(%C1%BD%D1%A7%C6%DA)'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Cache-Control': 'max-age=0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive',
    'Host': '60.219.165.24',
    'Referer': 'http://60.219.165.24/',
    'Upgrade-Insecure-Requests': 1
    }


class URPSpider(BaseSpider):
    def __init__(self, account, passwd):
        super().__init__()
        self.account = account
        self.passwd = passwd
        self.classname = None
        self.name = None
        self.academy = None
        self.heaers = super().build_headers(headers)

    def login(self, **kwargs):
        """
        模拟登录,检验密码是否正确。密码正确获取cookie
        :param kwargs: 关键字参数会传递给requests，在此设置timeout
        :return:
        status{
            200 登录成功
            400 密码错误
            500 服务器请求超时
        }
        """
        status = 200
        try:
            resp = super().get_html(loginURL, 'POST', data={'zjh': self.account, 'mm': self.passwd}, **kwargs)
            content = resp.text
            if len(content) > 500:
                status = 400

        except ReadTimeout:
            return 500

        return status

    def user_info(self, **kwargs):
        try:
            resp = super().get_html(stuinfoURL, 'GET', **kwargs)

        except ReadTimeout:
            return None

        content = resp.text
        try:
            banji = re.search(
                '<td class="fieldName" width="180">.*?班级:&nbsp;.*?</td>.*?<td .*? .*?>(.*?)</td>',
                content, re.S)
            self.classname = banji.group(1).strip()

            xisuo = re.search(
                '<td class="fieldName" width="180">.*?系所:&nbsp;.*?</td>.*?.*?<td .*? .*?>(.*?)</td>',
                content, re.S)
            self.academy = xisuo.group(1).strip()

            name = re.search(
                '<td class="fieldName" width="180">.*?姓名:&nbsp;.*?</td>.*?.*?<td width="275">(.*?)</td>',
                content, re.S)
            self.name = name.group(1).strip()
        except AttributeError:
            pass

        stuInfo = {
            'num': self.account,
            'className': self.classname,
            'major': self.academy,
            'name': self.name
        }
        return stuInfo

    def grade(self, getAll=False, **kwargs):
        allGrades = {}
        everGrades = {}
        nowGrade = []

        try:
            resp = super().get_html(bxqURL, 'GET', **kwargs)

        except ReadTimeout:
            # print('user info ReadTimeout')
            return None

        text = resp.text

        myItems = re.findall('<tr.*?class="odd".*?</td>.*?</td>.*?<td align="center">(.*?)</td>.*?</td>.*?<td align="'
                             'center">.*?</td>.*?<td align="center">(.*?)</td>.*?<td align="center">(.*?)</td>', text,
                             re.S)

        if myItems is not []:
            for x in myItems:
                grade = []
                for y in range(0, 3):
                    if y != 2:
                        grade.append(x[y].strip())
                    else:
                        if len(x[y].strip()) < 10:

                            grade.append(x[y].strip())
                        else:
                            num = re.search('<p align="center">''(.*?)&nbsp;</P>', x[y], re.S)
                            grade.append(num.group(1))
                nowGrade.append(grade)
        allGrades['now'] = nowGrade

        if getAll:
            resp = super().get_html(resultUrl, 'GET', **kwargs)
            text = resp.text
            terms = re.findall(r'<a name="(.*?)" /></a>.*?<table width="100%" border="0" '
                               'cellpadding="0" cellspacing="0" class="titleTop2">(.*?)</table>', text, re.S)
            for term in terms:
                termgrade = []
                key = term[0]
                myItems = re.findall('<tr.*?class="odd".*?</td>.*?</td>.*?<td align="center">(.*?)</td>.*?</td>.*?'
                                     '<td align="center">(.*?)</td>.*?<p align="center">''(.*?)&nbsp;</P>', term[1], re.S)
                for x in myItems:
                    grade = []
                    for y in range(0, 3):
                        grade.append(x[y].strip())
                    termgrade.append(grade)

                everGrades[key] = termgrade

        allGrades['ever'] = everGrades

        return allGrades

    @retry_task
    def get_user_info(self, retry=False, app=None):
        status = self.login(timeout=5)
        stuInfo = None
        data = {
            'status': status,
            'stuinfo': stuInfo
        }

        if status == 200:
            data['stuinfo'] = self.user_info()

        return data

    def get_user_info_async(self, retry=-1):
        app = current_app._get_current_object()

        self.async_task(self.get_user_info, retry=retry, app=app)

    @retry_task
    def get_grade(self, getAll=False, retry=0):
        status = self.login(timeout=5)
        grade = None
        data = {
            'status': status,
            'grade': grade
        }

        if status == 200:
            data['grade'] = self.grade(getAll=getAll)

        return data

    def async_task(self, func, **kwargs):
        thr = Thread(target=func, kwargs=kwargs)
        thr.start()
        return thr

    def save_user_info(self):
        user = WechatUser(
            openid=self.openid,
            account=self.account,
            passwd=self.passwd,
            name=self.name,
            academy=self.academy,
            classname=self.classname)
        db.session.add(user)
        db.session.commit()


if __name__ == '__main__':
    urp = URPSpider(2014025838, 1)
    result = urp.get_grade(retry=-1)
