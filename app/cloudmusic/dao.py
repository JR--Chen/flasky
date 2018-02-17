try:
    from.. import db
except:
    from sqlalchemy import create_engine
    engine = create_engine('mysql+pymysql://root@localhost:3306/flask?charset=utf8')
    db = engine.connect()


def findIdByName(username):
    sql = "select id from flask.cloudmusic_user WHERE username = '{}'".format(username)
    result = db.engine.execute(sql).fetchall()

    return result


def findUserByID(userid):
    sql = 'select id from flask.cloudmusic_user WHERE id = {}'.format(userid)
    result = db.engine.execute(sql).fetchall()

    return result


def findSongIdByUserId(userid):
    sql = """SELECT
                    song_id,
                    b.score
                FROM
                    cloudmusic_user_playlist_songs AS a
                LEFT JOIN cloudmusic_songs AS b ON a.song_id = b.id
                WHERE
                    userid = {}""".format(userid)

    result = db.engine.execute(sql).fetchall()

    return result


def findOtherUserId(userid):
    sql = 'select id from cloudmusic_user WHERE id != {}'.format(userid)
    result = db.engine.execute(sql).fetchall()

    return result


def findUserInfoById(userid):
    sql = 'select username,avatarUrl,signature from cloudmusic_user WHERE id = {}'.format(userid)
    result = db.engine.execute(sql).fetchall()

    return result

if __name__ == '__main__':
    result = findUserInfoById(136195873)
    print(result[0]['username'])
    # results = findSongIdByUserId(136195873)
    # songidSet = set()
    # songScoreDict = dict()
    # for result in results:
    #     songidSet.add(result[0])
    #     songScoreDict[result[0]] = result[1]
    # print(songScoreDict)
    db.close()
