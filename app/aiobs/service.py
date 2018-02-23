from ..spider.aiobsSpider import AiobsSpider
from .dao import addNetcard, findCardByID, findCardByUser, bindNetcardToUesr, updateCardByUser


def netcard_info(card_id, password, userid):
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
