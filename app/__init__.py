from flask import Flask
from .config import DevelopConfig, ProductionConfig
from dotenv import load_dotenv
from flask_cors import CORS


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

    print(app.config['SQLALCHEMY_DATABASE_URI'])
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

   

    return app
