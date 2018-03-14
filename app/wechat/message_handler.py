import datetime
from ..models import WechatUser
from wechat_sdk.messages import TextMessage, EventMessage
from flask import url_for, current_app
from .. import db
from ..redis_orm import RedisQueue, RedisHash, RedisSet
from ..aiobs.service import netcard_info
from ..aiobs.dao import findCardByID, findCardByUser
from ..axinfu.service import axinfu_info
from ..axinfu.dao import findUserByUserID


def message_handle(message, basic):
    """
    判断传入的信息类型并进行处理
    :param message: 从微信服务器接收到的信息，包括信息来源source，内容content
    :param basic: 微信配置完成的一个实例，对返回的信息作封装处理
    :return: 返回经过封装好的
    """
    response = None
    source = message.source

    if isinstance(message, TextMessage):
        content = message.content
        response = _text_reply(content, source, basic)

    elif isinstance(message, EventMessage):
        if message.type == 'subscribe':  # 关注事件(包括普通关注事件和扫描二维码造成的关注事件)
            key = message.key  # 对应于 XML 中的 EventKey (普通关注事件时此值为 None)
            ticket = message.ticket  # 对应于 XML 中的 Ticket (普通关注事件时此值为 None)
        elif message.type == 'unsubscribe':  # 取消关注事件（无可用私有信息）
            pass
        elif message.type == 'scan':  # 用户已关注时的二维码扫描事件
            key = message.key  # 对应于 XML 中的 EventKey
            ticket = message.ticket  # 对应于 XML 中的 Ticket
        elif message.type == 'location':  # 上报地理位置事件
            latitude = message.latitude  # 对应于 XML 中的 Latitude
            longitude = message.longitude  # 对应于 XML 中的 Longitude
            precision = message.precision  # 对应于 XML 中的 Precision
        elif message.type == 'click':  # 自定义菜单点击事件
            key = message.key  # 对应于 XML 中的 EventKey
            response = _click(key, source, basic)
        elif message.type == 'view':  # 自定义菜单跳转链接事件
            key = message.key  # 对应于 XML 中的 EventKey
        elif message.type == 'templatesendjobfinish':  # 模板消息事件
            status = message.status  # 对应于 XML 中的 Status
        elif message.type in ['scancode_push', 'scancode_waitmsg', 'pic_sysphoto',
                              'pic_photo_or_album', 'pic_weixin', 'location_select']:  # 其他事件
            key = message.key  # 对应于 XML 中的 EventKey

    if response is None:
        response = basic.response_none()

    return response


def _text_reply(content, source, basic):
    response = None

    if content in ['外网', '教务网', '内网']:
        link1 = _href('http://192.168.11.239/', '戳我进内网')
        link2 = _href('http://60.219.165.24/', '戳我进外网')
        reply = link1 + '\n\n' + link2
        response = basic.response_text(content=reply)

    elif content in ['课表', '17课表', '课程表', '课程', 17]:
        link = _href('https://www.mrbeen.cn/searchcourse', '点我查看17级课表')
        reply = link + '\n老家伙请移步菜单右下角小程序'
        response = basic.response_text(content=reply)

    elif content == '成绩':
        reply = '请移步菜单右下角小程序查询'
        response = basic.response_text(content=reply)

    elif content == '校历':
        reply = _href('http://msg.weixiao.qq.com/t/c37e86ae56334a07b66a0564d8fad6d2', '戳我看校历')
        response = basic.response_text(content=reply)

    elif content in['作息', '时刻表', '冬令时', '时间', '休息']:
        response = basic.response_image(media_id='qcf_h2hm7P1RL81csrh8MHstoytIAQOkEH4Jej5T4io')

    elif content == '绑定':
        response = _check_bind(source, basic)

    elif content in ['一卡通', '饭卡', '校园卡']:
        user = WechatUser.query.filter_by(openid=source).first()
        if user is None:
            response = _check_bind(source, basic)
        else:
            card = findUserByUserID(user.account)
            if card != []:
                pass


    elif content in ['网卡', '网费']:
        user = WechatUser.query.filter_by(openid=source).first()
        if user is None:
            response = _check_bind(source, basic)
        else:
            netcard = findCardByUser(user.account)
            if netcard != []:
                card_info = findCardByID(netcard[0][0])
                card_id = card_info[0][0]
                password = card_info[0][1]
                netcard = netcard_info(card_id, password, user.account)
                if netcard['status'] == 500:
                    reply = '服务器给我们提了个问题，请联系吴彦祖~'
                else:
                    balance = netcard['card']['balance']
                    details = netcard['card']['detail']

                    reply = '网卡余额：{} \n\n最近3次使用情况:\n'.format(balance)

                    for detail in details:
                        reply += '开始时间{}\n结束时间{}\n 使用金额{}\n'.format(detail[1], detail[2], detail[3])

            else:
                reply = '你还没绑定网卡'

            response = basic.response_text(content=reply)

    elif content in ['考试', '考试时间']:
        user = WechatUser.query.filter_by(openid=source).first()
        if user is None:
            response = _check_bind(source, basic)
        else:
            sql = r"SELECT * FROM 2017exam WHERE classname LIKE '%%{}%%'".format(user.classname)
            result = db.engine.execute(sql).fetchall()
            reply = ''

            if result == []:
                reply = 'sry~暂时还没有你的考试信息,我们会尽快添加'

            else:
                for item in result:
                    reply = reply + '科目:' + item[4] + '\n''日期:' + item[1] + '\n' + '时间:' + item[2] + '\n' + '教室:' + \
                            item[5] + '\n\n'

            response = basic.response_text(content=reply)

    elif content in ['补考', '补考时间']:
        user = WechatUser.query.filter_by(openid=source).first()
        if user is None:
            response = _check_bind(source, basic)
        else:
            sql = r"SELECT * FROM 17_18bukao WHERE classname LIKE '%%{}%%'".format(user.classname)
            result = db.engine.execute(sql).fetchall()

            if result == []:
                reply = '恭喜~你没有公共课需要补考'

            else:
                reply = '这是您所属班级的补考信息，不是个人的补考信息\n\n'
                for item in result:
                    reply = reply + '科目:' + item[3] + '\n''日期:' + item[1] + '\n' + '时间:' + item[2] + '\n' + '教室:' + \
                            item[4] + '\n\n'

            response = basic.response_text(content=reply)

    elif content in ['解除绑定', '解绑']:
        user = WechatUser.query.filter_by(openid=source).first()

        reply = '你还没有绑定'

        if user is not None:
            db.session.delete(user)
            db.session.commit()
            reply = '解除绑定成功'
        response = basic.response_text(content=reply)

    elif content.startswith('无主情话'):

        now = datetime.datetime.now()
        starttime = datetime.datetime.strptime('2018-03-15 00:00:00', '%Y-%m-%d %H:%M:%S')
        passtieme = datetime.datetime.strptime('2018-03-15 00:00:00', '%Y-%m-%d %H:%M:%S')

        if now > passtieme:
            reply = '活动时间已经过了，下次记得早点参与'

        else:
            message_queue = RedisQueue(name='flag')
            message_dict = RedisHash(name='flag')
            poem_queue = RedisQueue(name='poem')
            superuser = RedisSet(name='superuser')
            issuper = source.encode('utf-8') in superuser
            content = content.split('无主情话')[1].strip()

            if content == '':
                reply = '不要发空消息哦~'

            else:
                if issuper or source.encode('utf-8') not in message_dict:
                    if len(message_queue) == 0:
                        reply = '且将新火试新茶，诗酒趁年华。'
                    else:
                        message = message_queue.get_nowait()
                        if message is None:
                            poem = poem_queue.get_nowait()
                            if poem is None:
                                message = '你是少年的欢喜\n这句话倒过来还是你'
                            else:
                                message = poem.decode('utf-8')
                        else:
                            message = message.decode('utf-8')
                        reply = message.strip()
                    if issuper:
                        reply += '\n队列里还有%s条消息' % len(message_queue)

                    message_queue.put(content)
                    message_dict[source] = content
                    message_queue.save()
                    message_dict.save()
                else:
                    reply = '您已经发送过消息了，下次活动期待你参与'

        response = basic.response_text(content=reply)

    elif content.startswith('put'):
        message_queue = RedisQueue(name='poem')
        message_dict = RedisHash(name='test')
        content = content.split('put')[1]

        reply = '队列里还有%s条消息' % len(message_queue)
        message_queue.put(content)
        message_dict[source] = content
        message_dict.save()
        message_queue.save()
        response = basic.response_text(content=reply)

    elif content == 'superuser':
        superuser = RedisSet(name='superuser')
        superuser.add(source)
        superuser.save()
        reply = source

        response = basic.response_text(content=reply)

    elif content == 'openid':
        reply = source
        response = basic.response_text(content=reply)

    return response


def _click(key, source, basic):
    user = WechatUser.query.filter_by(openid=source).first()
    response = None

    if key == 'V1001_TODAY_MUSIC':
        if user is None:
            url = url_for('wechat.login', openid=source, _external=True)
            reply = _href(url, '点我绑定')
            response = basic.response_text(content=reply)
        else:
            reply = 'ok'
            response = basic.response_text(content=reply)

    return response


def _href(url, content):
    return '<a href="%s">%s</a>' % (url, content)


def _check_bind(source, basic):
    user = WechatUser.query.filter_by(openid=source).first()
    if user is None:
        url = url_for('wechat.login', openid=source, _external=True)
        reply = _href(url, '亲，请先点我绑定(*^__^*) ')
    else:
        reply = '已经绑定过了，回复要查询的关健词就可以啦~'

    response = basic.response_text(content=reply)
    return response
