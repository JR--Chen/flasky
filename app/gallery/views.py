from flask import request, render_template
from flask_paginate import Pagination, get_page_parameter
from .. import db
from . import gallery


@gallery.route('/<name>')
def gallery(name):
    page = request.args.get(get_page_parameter(), type=int, default=1)

    sql = "SELECT date,url FROM `gallery` WHERE name=%s ORDER BY `date` DESC limit %s, %s"
    sql2 = "SELECT COUNT(*) FROM `gallery` WHERE name=%s "

    fetch = (page-1) * 10

    result = db.engine.execute(sql, (name, fetch, fetch+9)).fetchall()
    count = db.engine.execute(sql2, name).fetchall()[0]['COUNT(*)']

    all_pic_list = []
    width_list = []
    for x in result:
        pic_list = dict()
        pic_list['date'] = x[0]
        url_list = x[1].split()

        length = len(url_list)
        width = 0
        if length == 1:
            width = 12
        elif 1 < length < 4:
            width = 12 / length
        elif length == 4:
            width = 6
        elif 4 < length < 9:
            width = 12 / int(length / 2)
        elif length == 9:
            width = 4
        width_list.append(int(width))

        new_url_list = []
        for url in url_list:
            sub = url.split('/')[3]
            small = url.replace(sub, 'mw690')
            large = url.replace(sub, 'large')

            new_url = {
                'small': small,
                'large': large
            }
            new_url_list.append(new_url)
        pic_list['url'] = new_url_list
        all_pic_list.append(pic_list)

    pagination = Pagination(page=page, total=count, bs_version=4, per_page=10, alignment='center')
    icon = name+'.ico'
    return render_template('gallery/gallery.html', all_pic_list=all_pic_list, width_list=width_list,
                           pagination=pagination, title=name, filename=icon, page=page)

