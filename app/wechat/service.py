from ..urp.service import get_user_info


def wechat_login(account, passwd):
    info = get_user_info(account, passwd)
