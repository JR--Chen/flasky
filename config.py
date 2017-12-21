import os
basedir = os.path.abspath(os.path.dirname(__file__))
APP_STATIC = os.path.join(basedir, 'app/static')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'wtf man'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[JR Chan]'
    ADMINS = os.environ.get('FLASKY_ADMIN') or '546159053@qq.com'
    FLASKY_MAIL_SENDER = '黑科校际 <546159053@qq.com>'
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = '546159053@qq.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_POSTS_PER_PAGE = 20
    FLASKY_FOLLOWERS_PER_PAGE = 20
    FLASKY_COMMENTS_PER_PAGE = 20

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root@localhost:3306/flask?charset=utf8'
    CELERY_BROKER_URL = 'redis://119.29.119.49:6379/0'
    CELERY_RESULT_BACKEND = 'redis://119.29.119.49:6379/0'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'mysql+pymysql://root@localhost:3306/flask_test?charset=utf8'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCT_DATABASE_URL')

    # @classmethod
    # def init_app(app):
    #     Config.init_app(app)
    #
    #     import logging
    #     from logging.handlers import SMTPHandler
    #     credentials = None
    #     secure = None

        # if getattr(cls,'MAIL_USERNAME', None) is not None:


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}