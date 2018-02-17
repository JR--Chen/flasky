import gevent
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://root@localhost:3306/flask?charset=utf8')

try:
    from .baseSpider import BaseSpider
except :
    from baseSpider import BaseSpider


class CloudMusicSpider(BaseSpider):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.user_info = None
        self.playlist_info = []
        self.song_info = []

    def get_user_info(self, offset=0, total=True):
        """
        获取用户信息
        :param offset:返回结果数量
        :param total: 是否返回全部结果
        :return: 'nickname'： 昵称
                  'userId'： 用户ID
                  'avatarUrl': 头像地址
                  'signature': 签名
        """
        url = 'http://music.163.com/api/search/get/web'
        data = {
            's': self.username,
            'type': 1002,
            'offset': offset,
            'total': total,
            'limit': 5
        }
        result = super().get_html(url, 'POST', data=data)
        user_info = result.json()['result']['userprofiles']
        for info in user_info:
            if info['nickname'] == self.username:
                self.user_info = info

        return self.user_info

    def get_playlist(self, offset=0, limit=100):
        """
        用户歌单列表
        '['creator']['userId']'： 创建者id
        'trackCount': 歌曲数目,
        'playCount': 播放次数
        'id'： 歌单id
        :param offset:
        :param limit:
        :return:
        """
        url = 'http://music.163.com/api/user/playlist/?offset=' + str(offset) + '&limit=' + str(
            limit) + '&uid=' + str(self.user_info['userId'])

        result = self.get_html(url, 'GET')
        playlist = result.json()['playlist']

        for info in playlist:
            if info['creator']['userId'] == self.user_info['userId']:
                self.playlist_info.append({
                    'id': info['id'],
                    'trackCount': info['trackCount'],
                    'playCount': info['playCount'],
                    'name': info['name']
                })

        return playlist

    def playlist_detail(self, playlist_id):
        """
        歌单里每首歌的详细信息
        'id': id
        'artists'[0]'id': 歌手id
        'artists'[0]'name': 歌手名称
        'score': ?
        'popularity' ?
        :param playlist_id:
        :return:
        """
        url = 'http://music.163.com/api/playlist/detail?id=' + str(playlist_id)

        result = super().get_html(url, 'GET')
        data = result.json()['result']['tracks']
        songs = []

        return data

    def get_song_id(self):
        readers = [gevent.spawn(self.playlist_detail, info['id']) for info in self.playlist_info]
        results = gevent.joinall(readers)

        songInfoDict = dict()

        for x, result in enumerate(results):
            songs = []
            for detail in result.value:
                id = detail['id']
                score = detail['score']

                songs.append({
                    'id': id,
                    'name': detail['name'],
                    'score': score
                })

                songInfoDict[id] = score

            self.playlist_info[x]['songs'] = songs
        return songInfoDict

    def insert_sql_factory(self):
        sql = []
        user = "insert into flask.cloudmusic_user(username, id, avatarUrl, signature) VALUE ('{}',{},'{}','{}')"

        sql.append(user.format(
            self.user_info['nickname'], self.user_info['userId'], self.user_info['avatarUrl'], self.user_info['signature']))

        for lists in self.playlist_info:
            playlist = "insert into flask.cloudmusic_playlist(id, trackCount, playCount, name) VALUE ({},{},{},'{}')"
            sql.append(playlist.format(lists['id'], lists['trackCount'], lists['playCount'], lists['name']))

            for song in lists['songs']:
                song_sql = "insert into flask.cloudmusic_songs(id, name, score) VALUE ({},'{}',{})"

                sql.append(song_sql.format(song['id'], song['name'], song['score']))
                relationship = "insert into flask.cloudmusic_user_playlist_songs(userid, playlist_id, song_id) VALUE ({},{},{})"
                sql.append(relationship.format(self.user_info['userId'], lists['id'], song['id']))
        return sql


if __name__ == '__main__':
    cm = CloudMusicSpider('又云_')
    cm.get_user_info()
    cm.get_playlist()
    result = cm.get_song_id()
    cm.insert_sql_factory()
    # print(cm.playlist_info)

