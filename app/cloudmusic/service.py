import math
import gevent
from operator import itemgetter
from flask import current_app
from .. import db
from threading import Thread

try:
    from .dao import findSongIdByUserId, findUserByID, findOtherUserId, findIdByName, findUserInfoById
    from ..spider.cloudMusicSpider import CloudMusicSpider
except:
    from dao import findSongIdByUserId, findUserByID, findOtherUserId, findIdByName
    from flaskpro.flasky.app.spider.cloudMusicSpider import CloudMusicSpider


def recommend(username):
    try:
        result = rank_score(username)
        userid = result['id']
        info = findUserInfoById(userid)[0]
        result = {
            'id': userid,
            'point': result['point'],
            'username': info['username'],
            'avatarUrl': info['avatarUrl'],
            'signature': info['signature'],
            'home': 'http://music.163.com/#/user/home?id={}'.format(userid)
        }
    except :
        result = None

    return result


def rank_score(username):
    result = findIdByName(username)
    app = current_app._get_current_object()

    if result == []:
        cm = CloudMusicSpider(username)
        info = cm.get_user_info()
        userid = info['userId']
        cm.get_playlist()
        self_song_info = cm.get_song_id()
        thr = Thread(target=save_info_async, kwargs={'sqls': cm.insert_sql_factory(), 'app': app})
        thr.start()

    else:
        userid = result[0][0]
        self_song_info = findSongIdByUserId(userid)

    other_id = findOtherUserId(userid)
    reader = [gevent.spawn(get_score, uid[0], self_song_info, app) for uid in other_id]
    results = gevent.joinall(reader)

    point = []
    for result in results:
        point.append(result.value)
    rank = sorted(point, key=itemgetter('point'), reverse=True)

    return rank[0]


def get_score(compared_userid, self_song_info, app):
    self_songidSet = set()
    self_songScoreDict = dict()

    if isinstance(self_song_info, list):
        for result in self_song_info:
            self_songidSet.add(result[0])
            self_songScoreDict[result[0]] = result[1]
    else:
        for id in self_song_info:
            self_songidSet.add(id)
            self_songScoreDict = self_song_info
    with app.app_context():
        results = findSongIdByUserId(compared_userid)
    compared_songidSet = set()
    compared_songScoreDict = dict()

    for result in results:
        compared_songidSet.add(result[0])
        compared_songScoreDict[result[0]] = result[1]

    sameId = self_songidSet & compared_songidSet
    bothId = self_songidSet | compared_songidSet

    compared_songScoreDict.update(self_songScoreDict)

    sameScore = 0
    bothScore = 0
    for id in sameId:
        sameScore += compared_songScoreDict[id]

    for id in bothId:
        bothScore += compared_songScoreDict[id]

    point = math.sqrt(sameScore)/math.sqrt(bothScore)

    return {
        'id': compared_userid,
        'point': round(point, 4)
    }


def save_info_async(sqls, app):
    with app.app_context():
        for sql in sqls:
            try:
                db.engine.execute(sql)
            except:
                pass


if __name__ == '__main__':
    recommend('Ezzreal')
