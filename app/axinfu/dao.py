from .. import db


def findUserByUserID(userid):
    sql = 'select * from axinfu WHERE userid={}'.format(userid)
    result = db.engine.execute(sql).fetchall()
    return result


def addUser(userid, mobile, password):
    sql = "insert into axinfu (userid, mobile, password) VALUE ({},{},'{}')"
    sql = sql.format(userid, mobile, password)
    db.engine.execute(sql)
