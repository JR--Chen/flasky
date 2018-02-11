import json
from flask import jsonify, request
import requests
from ..spider.urpSpider import URPSpider
from ..spider.axinfuSpider import AxinfuSpider
from ..spider.aiobsSpider import AiobsSpider
from . import api
from ..models import WechatUser
from .app_dao import findAxinfuUserByUserID, addAxinfuUser
from .netcard_dao import addNetcard, findCardByID, findCardByUser, bindNetcardToUesr, updateCardByUser


@api.route('/app/login', methods=['POST'])
def app_login_wrapper():
    """
    先从数据库中查找用户信息，存在用户信息则直接返回
    如果不存在用户信息或者用户密码不正确，则请求教务网更新信息

    :return:
        {
            'status':{
                200 登录成功
                400 密码错误
                500 服务器请求超时
            },
            'stuinfo': {
            'num': 学号,
            'className': 班级名称,
            'major': 专业,
            'name': 姓名
            'mobile':手机号(如果绑定安心付会返回)
            }
        }
    """
    stuInfo = {}
    status = 200
    result = {}

    data = json.loads(request.values.get('data'))
    userid = data.get('userid', 0)
    password = data.get('password', 0)

    result = app_login(userid, password)

    return jsonify(result)


def app_login(userid, password, openid=None):
    stuInfo = {}
    status = 200
    result = {}

    user = WechatUser.query.filter_by(account=userid).first()

    if user is None or user.passwd != password:
        student = URPSpider(userid, password, openid)
        try:
            result = student.get_user_info(retry=8)
        except []:
            result['status'] = 500
        if result['status'] == 500:
            student.get_user_info_async()

    else:
        mobile = None
        net_card = None
        info = findAxinfuUserByUserID(userid)
        try:
            netcard = findCardByUser(userid)
            if netcard != []:
                card_info = findCardByID(netcard[0][0])
                net_card = {
                    'card_id': card_info[0][0],
                    'password': card_info[0][1]
                }
            if info != []:
                 mobile = info[0][1]
        except :
            result['status'] = 500
        stuInfo = {
            'num': userid,
            'className': user.classname,
            'major': user.academy,
            'name': user.name,
            'mobile': mobile,
            'net_card': net_card
        }
        result = {
            'status': status,
            'stuinfo': stuInfo
        }

    return result


@api.route('/app/grade', methods=['POST'])
def get_grade_wrapper():
    data = json.loads(request.values.get('data'))

    userid = data.get('userid', 0)
    getAll = data.get('getAll', False)

    result = get_grade(userid, getAll)

    return jsonify(result)


def get_grade(userid, getAll=False):

    user = WechatUser.query.filter_by(account=userid).first()
    password = user.passwd
    student = URPSpider(userid, password, getAll)
    try:
        result = student.get_grade(retry=8)
    except []:
        result = {
            'status': 500
        }

    return result


@api.route('/app/kebiao', methods=['POST'])
def kebiao():
    data = json.loads(request.values.get('data'))
    stuinfo = data.get('stuinfo', 0)
    try:
        result = requests.post(url='http://127.0.0.1:9000/app/kebiao', data={'stuinfo': stuinfo})
    except :
        result = {}
    return jsonify(result.json())


@api.route('/app/ecard', methods=['POST'])
def axinfu():
    status = 200
    card = None

    data = json.loads(request.values.get('data'))
    userid = data.get('userid', None)
    mobile = data.get('mobile', None)
    password = data.get('password', None)

    info = findAxinfuUserByUserID(userid)
    if info != []:
        mobile = info[0][1]
        password = info[0][2]

        try:
            user = AxinfuSpider(mobile, password)
            user.login()
            card = user.getECard()
        except Exception as e:
            print(e)
            status = 500
    else:
        user = AxinfuSpider(mobile, password)
        try:
            login_statu = user.login()
            print(login_statu)
            if login_statu == 'OK':
                addAxinfuUser(userid, mobile, password)
                card = user.getECard()
            else:
                status = 400
        except Exception as e:
            print(e)
            status = 500

    result = {
        'status': status,
        'card': card
    }

    return jsonify(result)


@api.route('/app/netcard', methods=['POST'])
def net_card_wrapper():

    data = json.loads(request.values.get('data'))
    card_id = data.get('card_id', None)
    password = data.get('password', None)
    userid = data.get('userid', None)
    print(card_id)
    result = net_card(card_id, password, userid)
    return jsonify(result)


def net_card(card_id, password, userid):
    card = {}
    user = AiobsSpider(card_id, password)
    try:
        user.get_key_and_code()
        status = user.login()
        if status == 200:
            is_card_exit = findCardByID(card_id)
            # 如果卡不存在的话就是新卡，
            if is_card_exit == []:
                addNetcard(card_id, password)
                updateCardByUser(card_id, userid)
            else:
                is_user_bind = findCardByUser(userid)
                if is_user_bind != [] and is_user_bind[0][1] != card_id:
                    updateCardByUser(card_id, userid)
                else:
                    bindNetcardToUesr(card_id, userid)

            balance = user.get_balance()
            detail = user.get_use_detial()
            card = {
                'balance': balance,
                'detail': detail,
                'begin': user.begin_date,
                'card_id': user.card_id
            }
    except Exception as e:
        print(e)
        status = 500

    result = {
        'status': status,
        'card': card
    }
    return result

