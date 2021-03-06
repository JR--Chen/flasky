from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_pagedown import PageDown
from .redis_orm import create_pool as create_redis_pool
try:
    from config import config
except:
    pass


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
create_redis_pool()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    from .wechat import wechat as wechat_blueprint
    from .api_1_0 import api as api_1_0_blueprint
    from .gallery import gallery as gallery_blueprint
    from .cloudmusic import music as music_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(gallery_blueprint, url_prefix="/gallery")
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(wechat_blueprint, url_prefix='/wechat')
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')
    app.register_blueprint(music_blueprint, url_prefix='/music')

    return app

