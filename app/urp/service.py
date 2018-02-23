from ..spider.urpSpider import URPSpider
from .decorators import retry_task
from threading import Thread
from flask import current_app
from ..models import WechatUser
from .. import db


def login(account, password, openid=None):
    stuInfo = {}
    result = {}

    user = WechatUser.query.filter_by(account=account).first()

    if user is None or user.passwd != password:
        student = URPSpider(account, password)
        try:
            result = student.get_user_info(retry=8)
            if result['status'] == 200:
                save_user_info(account, password, stuInfo, openid)
            elif result['status'] == 500:
                app = current_app._get_current_object()
                async_task(_get_user_info_async, app, student, account, password)
        except :
            result['status'] = 500

    return result


def _get_user_info_async(app, student, account, password, openid=None):
    try:
        result = student.get_user_info(retry=8)
        if result['status'] == 200:
            with app.app_context():
                save_user_info(account, password, result['stuinfo'], openid)
    except :
        pass


@retry_task
def get_grade(account, passwd, retry=0):
    user = URPSpider(account, passwd)
    status = user.login(timeout=5)
    grade = None
    data = {
        'status': status,
        'grade': grade
    }

    if status == 200:
        data['grade'] = user.grade(getAll=True)

    return data


def async_task(func, *args, **kwargs):
    thr = Thread(target=func, args=args, kwargs=kwargs)
    thr.start()
    return thr


def save_user_info(account, password, stuinfo, openid=None):
    user = WechatUser(
        openid=openid,
        account=account,
        passwd=password,
        name=stuinfo['name'],
        academy=stuinfo['major'],
        classname=stuinfo['className'])
    db.session.add(user)
    db.session.commit()
