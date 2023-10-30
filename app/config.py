import os
class Config(object):
    TEMPLATE_AUTO_RELOAD = True
    SECRET_KEY = 'test-flask+svelte'
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB
    # Define la ruta a la carpeta principal del proyecto
    PROYECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RELEASE_FOLDER = os.path.join(PROYECT_ROOT, 'releases')
    UPLOAD_FOLDER = os.path.join(PROYECT_ROOT, 'respaldo_adjuntos')
    TOKEN = os.getenv('TOKEN')
    PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
    TEST_NUMBER_ID = os.getenv('TEST_NUMBER_ID')
    
class DevelopConfig(Config):
    HOST = os.getenv('DEV_HOST')
    USER = os.getenv('DEV_USER')
    PASSWORD = os.getenv('DEV_PASSWORD')
    DB = os.getenv('DEV_DB')
class ProductionConfig(Config):
    # BASE DE DATOS
    HOST = os.getenv('PROD_HOST')
    USER = os.getenv('PROD_USER')
    PASSWORD = os.getenv('PROD_PASSWORD')
    DB = os.getenv('PROD_DB')