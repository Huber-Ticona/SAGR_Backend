import os


class Config(object):
    TEMPLATE_AUTO_RELOAD = True
    SECRET_KEY = 'test-flask+svelte'
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB

class DevelopConfig(Config):
    HOST = os.getenv('DEV_HOST')
    USER = os.getenv('DEV_USER')
    PASSWORD = os.getenv('DEV_PASSWORD')
    DB = os.getenv('DEV_DB')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    # BASE DE DATOS
    HOST = os.getenv('PROD_HOST')
    USER = os.getenv('PROD_USER')
    PASSWORD = os.getenv('PROD_PASSWORD')
    DB = os.getenv('PROD_DB')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
