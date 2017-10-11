import os
import requests
from wechat_sdk import WechatBasic, WechatConf
from wechat_sdk.exceptions import OfficialAPIError

menu1 = \
    {
        "button": [
            {
                "name": "五日契约",
                "sub_button": [
                    {
                        "type": "view_limited",
                        "name": "名片",
                        "media_id": "qcf_h2hm7P1RL81csrh8MN2pfLBGsqCikUOXz7fy7Hc"
                    },
                    {
                        "type": 'view',
                        'name': '五日契约CP',
                        'url': 'http://heikexiaojipro.mikecrm.com/ce90tmC'
                    }
                ]
            },
            {
                "name": "充一卡通",
                "sub_button": [
                    # {
                    #     "type": "text",
                    #     "name": "颜值评分",
                    #     "value": "发张自拍给我看看~"
                    # },
                    {
                        "type": "view",
                        "name": "抖腿电台",
                        "url": "http://music.163.com/#/program/909115243/404514237/?userid=250919102"
                    },
                    {
                        "type": "view",
                        "name": "制作头像",
                        "url": "http://app.nickboy.cc/badge-avatar/index.html?media_id=gh_44e9316291c6&v=2032239200222074020170907/"
                    },
                    {
                        "type": "view",
                        "name": "充值一卡通",
                        "url": "https://h5.axinfu.com/third-party-entrance/by-school?school_code=Zh9JCA3uWiU51jA8GiAAIg%3D%3D%0A/"
                    }
                ]
            },
            {
                "name": "必备功能",
                "sub_button": [
                    {
                        "type": "miniprogram",
                        "name": "课表成绩",
                        "url": "http://60.219.165.24/",
                        "appid": "wx05f7264e83fa40e9",
                        "pagepath": "pages/index/index"
                    },
                    {
                        "type": "view",
                        "name": "17级课表",
                        "url": "https://www.mrbeen.cn/searchcourse/"
                    },
                    {
                        "type": "view",
                        "name": "校历",
                        "url": "http://msg.weixiao.qq.com/t/c37e86ae56334a07b66a0564d8fad6d2/"
                    },
                    {
                        "type": "view",
                        "name": "快递代取",
                        "url": "http://pbphp.lqdao3.com/pengcc/mobile?sn=2f236f5a015dafa75f4855232e95ad82/"
                    }
                ]
            }
        ]
    }

menu2 = \
    {
        'button': [
            {
                'type': 'click',
                'name': '今日歌曲',
                'key': 'V1001_TODAY_MUSIC'
            },
            {
                'type': 'click',
                'name': '歌手简介',
                'key': 'V1001_TODAY_SINGER'
            },
            {
                'name': '菜单',
                'sub_button': [
                    {
                        'type': 'view',
                        'name': '搜索',
                        "url": "http://app.nickboy.cc/badge-avatar/index.html?media_id=gh_44e9316291c6&v=2032239200222074020170907/"
                    },
                    {
                        'type': 'view',
                        'name': '视频',
                        "url": 'http://v.qq.com/'
                    },
                    {
                        'type': 'click',
                        'name': '赞一下我们',
                        'key': 'V1001_GOOD'
                    }
                ]
            }
        ]
    }


def getbasic():

    conf = WechatConf(
        token=os.environ.get('WECHAT_TOKEN'),
        appid='wx2fa77d7048b61431',
        appsecret='d9dd89550c7c221d44ccd581a6558fd6',
        encrypt_mode='normal',
    )

    basic = WechatBasic(conf=conf)

    return basic


def main():
    basic = getbasic()
    news = basic.meterial_list('image', offset=10, count=10)
    print(news)
    for x in range(0, len(news['item'])):
        title = news['item'][x]['content']['news_item'][0]['title'].encode('ISO-8859-1').decode('utf-8')
        print('id %s  title %s' % (news['item'][x]['media_id'], title))


def get_menue():
    basic = getbasic()
    token = basic.access_token
    resp = requests.get(url='https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token=%s' % token)
    print(resp.content.decode('utf-8'))


def manage_menu():
    basic = getbasic()
    print(basic.access_token)
    menu_data = menu1

    basic.create_menu(menu_data)


if __name__ == '__main__':
    main()