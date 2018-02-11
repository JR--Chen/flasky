from .. import db


def addNetcard(card_id, password):
    sql = "insert into netcard (card_id, password) VALUE ({},'{}')".format(card_id, password)
    db.engine.execute(sql)


def bindNetcardToUesr(card_id, userid):
    sql2 = "insert into wechat_netcard (card_id, userid) VALUE ({},{})".format(card_id, userid)
    db.engine.execute(sql2)


def findCardByID(card_id):
    sql = 'select * from netcard where card_id = {}'.format(card_id)
    result = db.engine.execute(sql).fetchall()

    return result

def findCardByUser(userid):
    sql = 'select * from wechat_netcard where userid={}'.format(userid)
    result = db.engine.execute(sql).fetchall()

    return result

def updateCardByUser(card_id, userid):
    sql = 'update wechat_netcard set card_id={} where userid={}'.format(card_id, userid)
    db.engine.execute(sql)