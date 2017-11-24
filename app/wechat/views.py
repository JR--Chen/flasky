import requests
import os
from flask import render_template, redirect, Response, request, flash, url_for
from wechat_sdk import WechatConf, WechatBasic
from wechat_sdk.exceptions import ParseError
from time import time
from . import wechat
from .forms import LoginForm
from .message_handler import message_handle
from ..models import AccessToken, WechatUser
from .. import db


@wechat.route('/signature', methods=["GET", "POST"])
def check_signature():
    basic = getbasic()

    if request.method == 'GET':
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')

        if not basic.check_signature(signature=signature, timestamp=timestamp, nonce=nonce):
            return Response(
                response='error',
                status=404
            )
        else:
            return Response(
                response=request.args.get('echostr'),
                content_type="text/plain",
                status=200
            )

    if request.method == 'POST':

        try:
            basic.parse_data(request.data)
        except ParseError:
            pass

        message = basic.message

        response = message_handle(message, basic)

        return Response(
            response=response,
            status=200
        )


@wechat.route('/login/<openid>', methods=['GET', 'POST'])
def login(openid):
    form = LoginForm()
    if form.validate_on_submit():
        user = WechatUser.query.filter_by(openid=openid).first()
        if user is not None:
            flash('你已经绑定过了(*^__^*) ')
            return redirect(url_for('main.index'))
        data = {
            'userid': form.account.data,
            'password': form.passwd.data
        }
        result = requests.post(url='http://127.0.0.1:9000/app/login', data=data)
        result = result.json()
        if result['status']['status'] != 200:
            flash('你的账号或者密码错误')
        else:
            stuinfo = result['status']['stuinfo']
            name = stuinfo['name']
            if name.endswith('班'):
                name = name[:-1]
            user = WechatUser(
                openid=openid,
                account=form.account.data,
                passwd=form.passwd.data,
                name=name,
                academy=stuinfo['major'],
                classname=stuinfo['className'])
            db.session.add(user)
            db.session.commit()
            flash('绑定成功，回到公众号界面回复关键词即可。')
    return render_template('wechat/login.html', form=form)


def getbasic():
    access_token = None
    access_token_expires_at = None

    accesstoken = db.session.query(AccessToken).order_by(AccessToken.id.desc()).first()

    if accesstoken is not None:
        access_token = accesstoken.accesstoken
        access_token_expires_at = accesstoken.expires

    conf = WechatConf(
        token=os.environ.get('WECHAT_TOKEN'),
        appid=os.getenv('appid') or 'wx2fa77d7048b61431',
        appsecret=os.getenv('appsecret') or 'd9dd89550c7c221d44ccd581a6558fd6',
        encrypt_mode='normal',
        access_token=access_token,
        access_token_expires_at=access_token_expires_at,
    )

    basic = WechatBasic(conf=conf)

    now = time()

    if access_token_expires_at - now < 60:
        token = basic.get_access_token()
        db.session.add(AccessToken(accesstoken=token['access_token'], expires=token['access_token_expires_at']))

    return basic


