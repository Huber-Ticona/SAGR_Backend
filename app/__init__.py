from flask import Flask
from .config import DevelopConfig, ProductionConfig
from dotenv import load_dotenv
from flask_cors import CORS
from heyoo import WhatsApp

def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)
    print(app.config['DEBUG'])
    # CARGA CONFIGURACION
    if app.config['DEBUG'] == True:
        app.config.from_object(DevelopConfig)
    else:
        app.config.from_object(ProductionConfig)

    # Se genera instancia de whatsapp
    token= app.config["TOKEN"]
    idNumeroTeléfono= app.config["TEST_NUMBER_ID"]
    messenger = WhatsApp(token, idNumeroTeléfono)
    app.messenger = messenger
    
    # Se registran los blueprints
    from .api import api_bp
    print( f'mysql+pymysql://{app.config["USER"]}:{app.config["PASSWORD"]}@{app.config["HOST"]}/{app.config["DB"]}')
    
    app.register_blueprint(api_bp, url_prefix='/api')

    
    return app
