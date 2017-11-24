from flask import jsonify, request, Response
import requests
from . import api


@api.route('/app/login/', methods=['POST'])
def app_login():
    userid = request.values.get('userid', 0)
    password = request.values.get('password', 0)
    data = {
        'userid': userid,
        'password': password
    }
    result = requests.post(url='http://127.0.0.1:9000/app/login', data=data)
    return jsonify(result.json())


@api.route('/app/grade', methods=['POST'])
def get_grade():
    openid = request.values.get('openid', 0)
    first = request.values.get('first', 0)
    data = {
        'openid': openid,
        'first': first
    }
    result = requests.post(url='http://127.0.0.1:9000/app/grade', data=data)
    return jsonify(result.json())


@api.route('/kebiao/', methods=['POST'])
def kebiao():
    stuinfo = request.values.get('stuinfo', 0)
    result = requests.post(url='http://127.0.0.1:9000/app/kebiao', data={'stuinfo': stuinfo})
    return jsonify(result.json())
