from ..spider.axinfuSpider import AxinfuSpider
from .dao import findUserByUserID, addUser


def axinfu_info(userid, mobile, password):
    status = 200
    card = None

    info = findUserByUserID(userid)
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
            if login_statu == 'OK':
                addUser(userid, mobile, password)
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

    return result