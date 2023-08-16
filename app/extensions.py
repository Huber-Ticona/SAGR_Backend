import pymysql
from flask import current_app
def obtener_conexion():
    return pymysql.connect(
        host=current_app.config['HOST'],
        user=current_app.config['USER'],
        password=current_app.config['PASSWORD'],
        db=current_app.config['DB'])
