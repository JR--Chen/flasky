from ..models import WechatUser
from wechat_sdk.messages import TextMessage, EventMessage
from flask import url_for

BASE_URL = 'http://www.mrbeen.cn'


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

    return response


def _click(key, source, basic):
    user = WechatUser.query.filter_by(openid=source).first()
    response = None

    if key == 'V1001_TODAY_MUSIC':
        if user is None:
            url = BASE_URL + url_for('wechat.login', openid=source)
            reply = _href(url, '点我绑定')
            response = basic.response_text(content=reply)
        else:
            reply = 'ok'
            response = basic.response_text(content=reply)

    return response


def _href(url, content):
    return '<a href="%s">%s</a>' % (url, content)
