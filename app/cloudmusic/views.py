from flask import render_template, request
from . import music
from . service import recommend


@music.route('/search', methods=['GET'])
def search():
    return render_template('cloudmusic/search.html')


@music.route('/result', methods=['POST'])
def result():
    data = request.values.get('username')
    user = recommend(data)

    return render_template('cloudmusic/result.html', user=user)
