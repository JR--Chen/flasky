import json
from flask import jsonify, request
import requests
from ..spider.urpSpider import URPSpider
from . import api
from ..models import WechatUser
from ..axinfu.service import axinfu_info
from ..axinfu.dao import findUserByUserID as findAxinfuUserByUserID
from ..aiobs.service import netcard_info
from ..aiobs.dao import findCardByID, findCardByUser
from ..urp.service import login as urp_login


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


def app_login(userid, password):
    stuInfo = {}
    status = 200
    result = {}

    user = WechatUser.query.filter_by(account=userid).first()

    if user is None or user.passwd != password:
        result = urp_login(userid, password)

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
    student = URPSpider(userid, password)
    try:
        result = student.get_grade(getAll, retry=8)
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

    data = json.loads(request.values.get('data'))
    userid = data.get('userid', None)
    mobile = data.get('mobile', None)
    password = data.get('password', None)

    result = axinfu_info(userid, mobile, password)

    return jsonify(result)


@api.route('/app/netcard', methods=['POST'])
def net_card():

    data = json.loads(request.values.get('data'))
    card_id = data.get('card_id', None)
    password = data.get('password', None)
    userid = data.get('userid', None)

    result = netcard_info(card_id, password, userid)

    return jsonify(result)



