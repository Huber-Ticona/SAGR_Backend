from flask import Blueprint, jsonify,json,request,send_from_directory,abort,current_app
from datetime import datetime
from .extensions import obtener_conexion
from .models.ModeloUsuario import ModeloUsuario
import os
api_bp = Blueprint('api_bp', __name__)



@api_bp.route('/nota_venta')
def nota_venta():
    venta = [1, 2]
    return venta
@api_bp.route('/test')
def test():
    venta = {
        "data": [2,3,4,5],
        "success" : "true"
    }
    return jsonify(venta)

# OBTENCION DE DATOS DE DOCUMENTO (BOLETA,FACTURA Y GUIA)
def busqueda_docs_fecha(inicio, fin):
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            # cursor = miConexion.cursor()

            sql1 = "select interno,vendedor,folio,monto_total,nro_boleta,nombre,vinculaciones,adjuntos,estado_retiro,revisor,despacho,fecha,historial_retiro from nota_venta where folio = 0 and fecha between %s and %s "
            cursor.execute(sql1, (inicio, fin))
            boletas = cursor.fetchall()

            sql2 = "select interno,vendedor,folio,monto_total,nro_boleta,nombre,vinculaciones,adjuntos,estado_retiro,revisor ,despacho,fecha,historial_retiro from nota_venta where nro_boleta = 0 and  fecha between %s and %s "
            cursor.execute(sql2, (inicio, fin))
            facturas = cursor.fetchall()

            sql3 = """select folio, interno,JSON_EXTRACT(detalle, '$.vendedor'),JSON_EXTRACT(detalle, '$.monto_final'),
            JSON_EXTRACT(detalle, '$.estado_retiro'),vinculaciones, JSON_EXTRACT(detalle, '$.tipo_doc'),despacho,JSON_EXTRACT(detalle, '$.revisor'),
            historial_retiro,fecha, JSON_EXTRACT(detalle, '$.doc_ref') from guia where fecha between %s and %s """
            cursor.execute(sql3, (inicio, fin))
            guias = cursor.fetchall()
            return (boletas, facturas, guias)
    except:
        return False
    finally:
        miConexion.close()
# obt 2

# RUTA PRINCIPAL PARA SONDEAR EL PANEL CLASICO
@api_bp.route('/obtener/docs/<string:fecha>')
def obt_docs(fecha=None):
    print("Fecha recibida: " + fecha)
    inicio = str(fecha) + ' 00:00'
    fin = str(fecha) + ' 23:59'

    documentos = busqueda_docs_fecha(inicio, fin)
    if documentos:
        print('NRo bol: ', len(documentos[0]))
        print('NRo fact: ', len(documentos[1]))
        print('NRo guia: ', len(documentos[2]))
        l_bol = documentos[0]
        l_fact = documentos[1]
        l_guia = documentos[2]
        # print(l_guia)
        return jsonify(boletas=l_bol, facturas=l_fact, guias=l_guia)
    else:
        return 404
# OBTENCION DE ITEMS X NRO INTERNO
@api_bp.route('/obt_detalle_bol_fact/<int:interno>', methods=['POST'])
def obt_detalle_bol_fact_interno(interno=None):
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            print('Obteniendo bol-fact: ',interno)
            cursor = miConexion.cursor()
            # SE AGREGO EL ESTADO RETIRADO
            cursor.execute(
                "select trim(descripcion), cantidad, retirado, codigo, interno, unitario, total from item  where interno = %s ", interno)
            detalle = cursor.fetchall()
            print(detalle)
            print(jsonify(detalle))
            """ [ [descripcion, comprada,retirada,codigo,interno,unitario,total] ] """
            return jsonify(detalle)
    finally:
        miConexion.close()

@api_bp.route('/obt_detalle_guia/<int:interno>', methods=['POST'])
def obt_detalle_guia_interno(interno):
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            cursor = miConexion.cursor()
            cursor.execute(
                "select detalle,interno from guia  where interno = %s ", interno)
            detalle = cursor.fetchone()
            print(detalle)
            detalle = json.loads(detalle[0])
            print('DETALLE: ',detalle['descripciones'])
            """ [ [descripcion, comprada,retirada,codigo,interno,unitario,total] ] """
            new_detalle = []
            for i in range(len(detalle['descripciones'])):
                array = []
                array.append(detalle['descripciones'][i])
                array.append(detalle['cantidades'][i])
                array.append(detalle['retirado'][i])
                new_detalle.append(array)
            return jsonify(new_detalle)
    finally:
        miConexion.close()

""" DOCUMENTOS """

@api_bp.route('/documentos/guias/folio/<int:folio>', methods=['POST'])
@api_bp.route('/documentos/guias/fecha/<string:fecha1>/<string:fecha2>', methods=['POST'])
@api_bp.route('/documentos/guias/cliente/<string:cliente>', methods=['POST'])
def obt_guia(folio=None, fecha1=None, fecha2=None, cliente=None):
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            detalle = []
            print('llego a buscar guias ..')
            if folio:
                print('buscando guias x folio ....')

                sql = """SELECT folio,fecha,interno,nombre,JSON_EXTRACT(detalle,'$.vendedor'),vinculaciones,JSON_EXTRACT(detalle,'$.estado_retiro'),
                JSON_EXTRACT(detalle,'$.revisor'),despacho,historial_retiro,JSON_EXTRACT(detalle, '$.tipo_doc'), JSON_EXTRACT(detalle, '$.doc_ref')  from guia where folio = %s """
                cursor.execute(sql, folio)
                detalle = cursor.fetchall()

            elif fecha1 and fecha2:
                print('buscando guias x fecha ....')
                inicio = str(fecha1) + ' 00:00'
                fin = str(fecha2) + ' 23:59'
                #,vinculaciones,estado_retiro,revisor,despacho,historial_retiro
                sql = """SELECT folio,fecha,interno,nombre,JSON_EXTRACT(detalle,'$.vendedor'),vinculaciones,JSON_EXTRACT(detalle,'$.estado_retiro'),
                JSON_EXTRACT(detalle,'$.revisor'),despacho,historial_retiro,JSON_EXTRACT(detalle, '$.tipo_doc'), JSON_EXTRACT(detalle, '$.doc_ref') from guia where fecha between %s and %s ORDER BY fecha desc """
                cursor.execute(sql, (inicio, fin))
                detalle = cursor.fetchall()
            elif cliente:
                print('buscando guias x nombre cliente ...')
                sql = "SELECT folio,fecha,interno,nombre,JSON_EXTRACT(detalle,'$.vendedor'),vinculaciones,JSON_EXTRACT(detalle,'$.estado_retiro'),JSON_EXTRACT(detalle,'$.revisor'),despacho,historial_retiro,JSON_EXTRACT(detalle, '$.tipo_doc'), JSON_EXTRACT(detalle, '$.doc_ref')  from guia where nombre like '%" + cliente + "%' ORDER BY fecha desc "
                cursor.execute(sql)
                detalle = cursor.fetchall()

            return jsonify(detalle)
    finally:
        miConexion.close()


@api_bp.route('/documentos/boletas/folio/<int:folio>', methods=['POST'])
@api_bp.route('/documentos/boletas/fecha/<string:fecha1>/<string:fecha2>', methods=['POST'])
@api_bp.route('/documentos/boletas/cliente/<string:cliente>', methods=['POST'])
def obt_boleta(folio=None, fecha1=None, fecha2=None, cliente=None):
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            detalle = []
            print('llego a buscar guias ..')
            if folio:
                print('buscando boleta x folio ....')
                sql = "SELECT nro_boleta,fecha,interno,'Cliente Boleta',vendedor,vinculaciones,estado_retiro,revisor,despacho,historial_retiro from nota_venta where nro_boleta = %s ORDER BY fecha desc "
                cursor.execute(sql, folio)
                detalle = cursor.fetchall()
                # print(detalle)

            elif fecha1 and fecha2:
                print('buscando boleta x fecha ....')
                inicio = str(fecha1) + ' 00:00'
                fin = str(fecha2) + ' 23:59'
                #interno,vendedor,folio,monto_total,nro_boleta,nombre,vinculaciones,adjuntos,estado_retiro,revisor,despacho,fecha,historial_retiro
                #nro_boleta,fecha,interno,'Cliente Boleta',vendedor,vinculaciones,estado_retiro,revisor,despacho,historial_retiro
                sql = "SELECT nro_boleta,fecha,interno,'Cliente Boleta',vendedor,vinculaciones,estado_retiro,revisor,despacho,historial_retiro  from nota_venta where folio = 0 and ( fecha between %s and %s) ORDER BY fecha desc "
                cursor.execute(sql, (inicio, fin))
                detalle = cursor.fetchall()
                # print(detalle)
            # TODAS LOS CLIENTES SON CLIENTES BOLETAS.
            """ elif cliente:
                print('buscando boleta x nombre cliente ...')
                sql = "SELECT nro_boleta,fecha,interno,'Cliente Boleta',vendedor,vinculaciones,estado_retiro,revisor,despacho,historial_retiro from nota_venta where folio = 0 and ( fecha between %s and %s) ORDER BY fecha desc " 
                cursor.execute( sql )
                detalle = cursor.fetchall()
                print(detalle) """

            return jsonify(detalle)
    finally:
        miConexion.close()


@api_bp.route('/documentos/facturas/folio/<int:folio>', methods=['POST'])
@api_bp.route('/documentos/facturas/fecha/<string:fecha1>/<string:fecha2>', methods=['POST'])
@api_bp.route('/documentos/facturas/cliente/<string:cliente>', methods=['POST'])
def obt_factura(folio=None, fecha1=None, fecha2=None, cliente=None):
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            detalle = []
            print('llego a buscar facturas ..')
            if folio:
                print('buscando factura x folio ....')
                sql = "SELECT folio,fecha,interno,nombre,vendedor,vinculaciones,estado_retiro,revisor,despacho,historial_retiro  from nota_venta where folio = %s  ORDER BY fecha desc"
                cursor.execute(sql, folio)
                detalle = cursor.fetchall()
                # print(detalle)

            elif fecha1 and fecha2:
                print('buscando factura x fecha ....')
                inicio = str(fecha1) + ' 00:00'
                fin = str(fecha2) + ' 23:59'
                sql = "SELECT folio,fecha,interno,nombre,vendedor,vinculaciones,estado_retiro,revisor,despacho,historial_retiro  from nota_venta where nro_boleta = 0 and ( fecha between %s and %s) ORDER BY fecha desc"
                cursor.execute(sql, (inicio, fin))
                detalle = cursor.fetchall()
                # print(detalle)
            elif cliente:
                print('buscando factura x nombre cliente ...')
                sql = "SELECT folio,fecha,interno,nombre,vendedor,vinculaciones,estado_retiro,revisor,despacho,historial_retiro   from nota_venta where nro_boleta = 0 and nombre like  '%" + cliente + "%' ORDER BY fecha desc"
                cursor.execute(sql)
                detalle = cursor.fetchall()
                # print(detalle)

            return jsonify(detalle)
    finally:
        miConexion.close()


@api_bp.route('/documentos/creditos/folio/<int:folio>', methods=['POST'])
@api_bp.route('/documentos/creditos/fecha/<string:fecha1>/<string:fecha2>', methods=['POST'])
@api_bp.route('/documentos/creditos/cliente/<string:cliente>', methods=['POST'])
def obt_creditos(folio=None, fecha1=None, fecha2=None, cliente=None):
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            detalle = []
            print('llego a buscar creditos ..')
            if folio:
                print('buscando creditos x folio ....')
                sql = "SELECT folio,fecha,interno,nombre,detalle,'No Registrado' from nota_credito where folio = %s"
                cursor.execute(sql, folio)
                detalle = cursor.fetchall()
                # print(detalle)

            elif fecha1 and fecha2:
                print('buscando creditos x fecha ....')
                inicio = str(fecha1) + ' 00:00'
                fin = str(fecha2) + ' 23:59'
                sql = "SELECT folio,fecha,interno,nombre,detalle,'No Registrado'  from nota_credito where fecha between %s and %s "
                cursor.execute(sql, (inicio, fin))
                detalle = cursor.fetchall()
                # print(detalle)
            elif cliente:
                print('buscando creditos x nombre cliente ...')
                sql = "SELECT folio,fecha,interno,nombre,detalle,'No Registrado' from nota_credito where nombre like  '%" + cliente + "%'"
                cursor.execute(sql)
                detalle = cursor.fetchall()
                # print(detalle)

            return jsonify(detalle)
    finally:
        miConexion.close()


@api_bp.route('/documentos/ordenes/<string:tipo>/folio/<int:folio>', methods=['POST'])
@api_bp.route('/documentos/ordenes/<string:tipo>/fecha/<string:fecha1>/<string:fecha2>', methods=['POST'])
@api_bp.route('/documentos/ordenes/<string:tipo>/cliente/<string:cliente>', methods=['POST'])
def obt_ordenes(folio=None, tipo=None, fecha1=None, fecha2=None, cliente=None):
    miConexion = obtener_conexion()
    # Sanitizar valores , analisis futuro.
    try:
        with miConexion.cursor() as cursor:
            detalle = []
            print('llego a buscar orden de: ' + tipo + ' ...')
            if folio:
                print('buscando orden x folio ....')
                sql = "SELECT nro_orden,fecha_orden,0,nombre, detalle, JSON_EXTRACT(detalle ,'$.creado_por') ,tipo_doc ,nro_doc  from orden_" + \
                    tipo + " where nro_orden = " + str(folio)
                cursor.execute(sql)
                detalle = cursor.fetchall()
                print(detalle)

            elif fecha1 and fecha2:
                print('buscando orden x fecha ....')
                inicio = str(fecha1) + ' 00:00'
                fin = str(fecha2) + ' 23:59'
                sql = "SELECT nro_orden,fecha_orden,0,nombre, detalle, JSON_EXTRACT(detalle ,'$.creado_por') ,tipo_doc ,nro_doc from orden_" + \
                    tipo + " where fecha_orden between '" + inicio + "' and  '" + fin + "'"
                cursor.execute(sql)
                detalle = cursor.fetchall()
                # print(detalle)
            elif cliente:
                print('buscando orden x nombre cliente ...')
                sql = "SELECT nro_orden,fecha_orden,0,nombre, detalle, JSON_EXTRACT(detalle ,'$.creado_por') ,tipo_doc ,nro_doc  from orden_" + \
                    tipo + " where nombre like  '%" + cliente + "%'"
                cursor.execute(sql)
                detalle = cursor.fetchall()
                # print(detalle)

            return jsonify(detalle)
    finally:
        miConexion.close()


#ACTUALIZAR 
@api_bp.route('/actualizar/nota_venta/item', methods=['POST'])
def actualizar_nota_venta():
    dato = request.json
    estado = None
    print(dato)
    print('----- datos update -------')
    print('dato 0: ',dato[0])
    print('dato 1: ',dato[1])
    print('dato 2: ',dato[2])
    print('----- datos historial --------')
    # historial
    revisor = dato[6]
    fecha = datetime.now()
    detalle = {
        "revisor": revisor,
        "fecha": str(fecha.strftime("%d-%m-%Y %H:%M:%S")),
        "descripciones": dato[3],
        "antes": dato[4],
        "despues": dato[5]
    }
    vale_id = dato[7]
    print("dato 6(vale_id): ", vale_id)
    historial = json.dumps(detalle)
    print(historial)

    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            # Se actualiza el estado de retiro y revisor
            sql = 'update nota_venta set estado_retiro = %s, revisor = %s where interno = %s'
            cursor.execute(sql, (dato[0],revisor, dato[2]))
           
            # miConexion.commit()
            # Crea la consulta
            sql = 'update item set retirado = %s where codigo = %s and interno = %s'
            cursor.executemany(sql, dato[1])
            # connection is not autocommit by default. So you must commit to save
            # your changes.

            # historial
            sql = 'select historial_retiro,interno from nota_venta where interno = %s'
            cursor.execute(sql, dato[2])
            lista = cursor.fetchone()
            if lista[0] == None:
                print('--------creando historial ----------')
                lista_historial = []
                lista_historial.append(historial)
                detalle2 = {
                    "lista_historial": lista_historial
                }
                nuevo_historial = json.dumps(detalle2)
                sql = 'update nota_venta set historial_retiro = %s where interno = %s'
                cursor.execute(sql, (nuevo_historial, dato[2]))
            else:
                print('--------actualizando historial ----------')
                aux_historial = json.loads(lista[0])
                try:
                    aux_historial['lista_historial'].append(historial)
                    nuevo_historial = json.dumps(aux_historial)
                    sql = 'update nota_venta set historial_retiro = %s where interno = %s'
                    cursor.execute(sql, (nuevo_historial, dato[2]))
                except KeyError:
                    print(' llave "lista_historial" no encontrado. Historial NO creado')
            #ACTUALIZAR FECHA REAL VALE DESPACHO
            if vale_id:
                print("|(DOCUMENTO CON VALE DESPACHO)  Actualizando fecha real vale despacho ...")
                fecha_real = datetime.now()
                sql = "update vale_despacho set fecha_real = %s where vale_id = %s"
                cursor.execute(sql, (str(fecha_real), vale_id ))
            else:
                print("(DOCUMENTO SIN VALE DESPACHO) : NO SE ACTUALIZA FECHA REAL.")

            miConexion.commit()
            return jsonify(data=True, message="Cantidad retirada actualizada")
    except:
        return jsonify(data=False, message="Error al actualizar cantidades. Consulte a su operador")
    finally:
        miConexion.close()

@api_bp.route('/actualizar/guia/item', methods=['POST'])
def actualizar_guia():
    dato = request.json
    print('----- datos update -------')
    print(dato[0])
    print(dato[1])
    print(dato[2])
    print('----- datos historial --------')
    # historial
    fecha = datetime.now()
    revisor = dato[6]
    detalle = {
        "revisor": revisor,
        "fecha": str(fecha.strftime("%d-%m-%Y %H:%M:%S")),
        "descripciones": dato[3],
        "antes": dato[4],
        "despues": dato[5]
    }
    vale_id = dato[7]
    print("dato 6(vale_id): ", vale_id)
    historial = json.dumps(detalle)
    print(historial)

    nuevo = json.dumps(dato[1])  # items retirados
    nuevo = nuevo[1: len(nuevo) - 1]

    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:

            '''sql = "SELECT JSON_EXTRACT( detalle , '$.retirado') from guia where interno = %s"
            cursor.execute(sql, dato[2])
            registro = cursor.fetchone()
            print(registro)'''

            # if registro[0]:#Si existe registro del retiro y revisor anteriormente **MODIFICADO ya que el agente capturador, otorga dichos parametros en la creacion
            print("tiene registrado retiros, comenzando a actualizar...")
            sql = "SELECT JSON_REPLACE(detalle, '$.retirado', JSON_ARRAY(" + nuevo + \
                "),'$.estado_retiro', %s,'$.revisor', %s ) from guia where interno = %s"
            cursor.execute(sql, (dato[0], revisor, dato[2]))
            resultado = cursor.fetchone()
            # print(resultado)

            '''else:
                print("no tiene registrado retiros y revisor, creando registros ...")
                sql = "SELECT JSON_INSERT( detalle , '$.retirado', JSON_ARRAY("+ nuevo +"),'$.estado_retiro', %s, '$.revisor', %s ) from guia where interno = %s"
                cursor.execute(sql, (estado , session['usuario'], dato[2] ))
                resultado = cursor.fetchone()
                print(resultado)'''

            sql2 = "UPDATE guia SET detalle = %s where interno = %s"
            cursor.execute(sql2, (resultado, dato[2]))

            # ACTUALIZANDO EL HISTORIAL
            sql = 'select historial_retiro,interno from guia where interno = %s'
            cursor.execute(sql, dato[2])
            lista = cursor.fetchone()
            if lista[0] == None:
                print('--------creando historial ----------')
                lista_historial = []
                lista_historial.append(historial)
                detalle2 = {
                    "lista_historial": lista_historial
                }
                nuevo_historial = json.dumps(detalle2)
                sql = "UPDATE guia SET historial_retiro = %s where interno = %s"
                cursor.execute(sql, (nuevo_historial, dato[2]))
            else:
                print('--------actualizando historial ----------')
                aux_historial = json.loads(lista[0])
                try:
                    aux_historial['lista_historial'].append(historial)
                    nuevo_historial = json.dumps(aux_historial)
                    sql = "UPDATE guia SET historial_retiro = %s where interno = %s"
                    cursor.execute(sql, (nuevo_historial, dato[2]))
                except KeyError:
                    print(' llave "lista_historial" no encontrado. Historial NO creado')
            
            #ACTUALIZAR FECHA REAL VALE DESPACHO
            if vale_id:
                print("|(DOCUMENTO CON VALE DESPACHO)  Actualizando fecha real vale despacho ...")
                fecha_real = datetime.now()
                sql = "update vale_despacho set fecha_real = %s where vale_id = %s"
                cursor.execute(sql, (str(fecha_real), vale_id ))
            else:
                print("(DOCUMENTO SIN VALE DESPACHO) : NO SE ACTUALIZA FECHA REAL.")

            miConexion.commit()

            return jsonify(data=True, message="GUIA: Cantidad retirada actualizada")
    except:
        return jsonify(data=False, message="GUIA: Error al actualizar cantidades. Consulte a su operador")
    finally:
        miConexion.close()

#ESTADISTICAS
@api_bp.route('/estadisticas/pendientes/<string:fecha1>/<string:fecha2>')
def obt_pendientes(fecha1=None, fecha2=None):

    inicio = str(fecha1) + ' 00:00'
    fin = str(fecha2) + ' 23:59'
    print('Pendientes Desde: ' + inicio + ' - Hasta: ' + fin)
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            sql1 = "SELECT interno,vendedor,folio,monto_total,nro_boleta,nombre,vinculaciones,adjuntos,estado_retiro,revisor,despacho,fecha,historial_retiro from nota_venta where (estado_retiro = 'NO RETIRADO' OR estado_retiro = 'INCOMPLETO' ) and nro_boleta = 0 AND (fecha between '" + \
                inicio + "' and '" + fin + "')"
            cursor.execute(sql1)
            facturas = cursor.fetchall()

            sql2 = "SELECT interno,vendedor,folio,monto_total,nro_boleta,nombre,vinculaciones,adjuntos,estado_retiro,revisor,despacho,fecha,historial_retiro from nota_venta where (estado_retiro = 'NO RETIRADO' OR estado_retiro = 'INCOMPLETO' ) and folio = 0 AND (fecha between '" + \
                inicio + "' and '" + fin + "')"
            cursor.execute(sql2)
            boletas = cursor.fetchall()

            sql3 = "SELECT folio, interno,JSON_EXTRACT(detalle, '$.vendedor'),JSON_EXTRACT(detalle, '$.monto_final'), JSON_EXTRACT(detalle, '$.estado_retiro'),vinculaciones, JSON_EXTRACT(detalle, '$.tipo_doc'),despacho,JSON_EXTRACT(detalle, '$.revisor'),historial_retiro,fecha, JSON_EXTRACT(detalle, '$.doc_ref') from guia where ( JSON_EXTRACT(detalle, '$.estado_retiro') = 'NO RETIRADO' OR JSON_EXTRACT(detalle, '$.estado_retiro') = 'INCOMPLETO' ) AND (fecha between '" + inicio + "' and '" + fin + "')"
            cursor.execute(sql3)
            guias = cursor.fetchall()

            # datos = []
            # datos.append(boletas)
            # datos.append(facturas)
            # datos.append(guias)documentos = busqueda_docs_fecha(inicio, fin)
            return jsonify(boletas=boletas, facturas=facturas, guias=guias)
    except:
        return 404

    finally:
        miConexion.close()

# CRUD OBSERVACION
@api_bp.route('/parametros_porteria' , methods=['POST'])
def obt_parametros_porteria():
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            sql = "select nombre_config,json_extract(detalle,'$.lista_observaciones')from config where nombre_config = 'parametros_porteria' "
            cursor.execute(sql)
            lista = cursor.fetchone()
            lista_porteria = lista[1]  # Se obtiene la lista []
            # lista_porteria = json.loads(lista_porteria) incompatible con javascript
            return lista_porteria
    finally:
        miConexion.close()

@api_bp.route('/registrar_observacion', methods=['POST'])
def registrar_observacion():
    data = request.json
    print("Data: ", data)
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            #S everifica que vinculaciones exista.
            sql1 = ""
            sql2 = ""
            sql3 = ""
            if data['tipo_doc'] in ['boleta', 'factura']:
                sql1 = """SELECT interno, vinculaciones from nota_venta WHERE interno = %s"""
                sql2 = """
                UPDATE nota_venta
                SET vinculaciones = JSON_SET(vinculaciones, '$.observacion', 
                CAST( %s AS JSON))
                WHERE interno = %s
                """
                sql3 = """
                UPDATE nota_venta
                SET vinculaciones = JSON_OBJECT(
                        'observacion', CAST( %s AS JSON)
                    )
                WHERE interno = %s """

            elif data['tipo_doc'] == 'guia':
                sql1 = """SELECT interno, vinculaciones from guia WHERE interno = %s """
                sql2 = """
                UPDATE guia
                SET vinculaciones = JSON_SET(vinculaciones, '$.observacion', 
                CAST( %s AS JSON))
                WHERE interno = %s
                """
                sql3 = """
                UPDATE guia
                SET vinculaciones = JSON_OBJECT(
                        'observacion', CAST( %s AS JSON)
                        )
                
                WHERE interno = %s 
                """
            cursor.execute(sql1, ( data['interno'] ))
            result = cursor.fetchone()
            print('result(vinculaciones): ', result)

            if result[1] != None:
                print('Existe OBJETO vinculaciones --> actualizando JSON .')
                result = cursor.execute(sql2, ( data['lista'] , data['interno'] ))
            else:
                print('NO Existe OBJETO vinculaciones --> creando JSON.')
                result = cursor.execute(sql3, ( data['lista'] , data['interno'] ))

            print("result : ",result)

            
            miConexion.commit()
            return jsonify(exito=True, msg='Observacion registrada Con exito.')
    finally:
        miConexion.close() 

# LOGIN
@api_bp.route('/login', methods=['GET', 'POST'])  # iniciar sesión
def login():
    print(' ------- LOGIN --------')
    if request.method == 'POST':
        data = request.json
        print("Data: ", data)
        nombre = data['usuario']
        contra = data['contra']
        print(f'Nombre: {nombre} | contra: {contra}')
        consulta = ModeloUsuario.login(nombre)

        success = False
        msg = ""
        datos_usuario = {
            "id" : None,
            "tipo" : None
        }
        if consulta:
            print('Usuario encontrado: ', consulta)
            if consulta[8] == 'porteria':  # or consulta[8] == 'area':
                if consulta[2] == contra:
                    print('usuario con privilegios')
                    success = True
                    msg = "Login exitoso."
                    datos_usuario = {
                        "id" : consulta[0],
                        "tipo" : consulta[8],
                        "nombre": consulta[10]
                    }
                else:
                    print('Contraseña invalida')
                    msg = "Contraseña invalida"
            else:
                msg = "Usuario sin privilegios"
                print('Usuario sin privilegios ')
        else:
            msg = "Usuario no existe."
            print("usuario no encontrado, en la bd")

        return jsonify(success = success , msg = msg, datos_usuario = datos_usuario)
    
@api_bp.route("/releases", methods=["POST"])
def get_releases():
    releases = os.listdir(current_app.config["RELEASE_FOLDER"])
    return jsonify(releases)

@api_bp.route('/releases/<filename>')
def download_release(filename):
    try:
        return send_from_directory(current_app.config["RELEASE_FOLDER"], filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

#DESPACHO ATRASADO
@api_bp.route('/despachos_atrasados_defecto', methods=['POST'])
def atraso():
    print('---- OBTENIENDO DESPACHOS ATRASADOS X 3 DIAS -----')
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            sql = '''SELECT * 
                FROM nota_venta
                WHERE nro_boleta = 0 and despacho = "SI" AND (DATEDIFF(NOW(), fecha) >= 3) and estado_retiro != "COMPLETO" '''
            cursor.execute(sql)
            facturas = cursor.fetchall()

            sql = '''SELECT *
                FROM nota_venta
                WHERE folio = 0 and despacho = "SI" AND (DATEDIFF(NOW(), fecha) >= 3) and estado_retiro != "COMPLETO" '''
            cursor.execute(sql)
            boletas = cursor.fetchall()

            sql = '''SELECT *
                FROM guia
                WHERE despacho = "SI" AND (DATEDIFF(NOW(), fecha) >= 3) and detalle->"$.estado_retiro" != "COMPLETO" '''
            cursor.execute(sql)
            guias = cursor.fetchall()

            return jsonify(
                boletas=boletas,
                facturas=facturas,
                guias=guias
            )
    finally:
        miConexion.close()
@api_bp.route('/estadisticas/despachos-atrasados', methods=['POST'])
def despachos_atrasados():
    ventas = []
    guias = []
    miConexion = obtener_conexion()
    try:
        with miConexion.cursor() as cursor:
            sql1 ='''SELECT COUNT(*) 
                FROM nota_venta
                WHERE nro_boleta = 0 and despacho = "SI" AND (DATEDIFF(NOW(), fecha) >= 3) and estado_retiro != "COMPLETO" '''
            cursor.execute(sql1)
            boletas = cursor.fetchall()

            sql2 = '''SELECT *
                FROM nota_venta
                WHERE folio = 0 and despacho = "SI" AND (DATEDIFF(NOW(), fecha) >= 3) and estado_retiro != "COMPLETO" '''
            cursor.execute(sql1)
            facturas = cursor.fetchall()

            sql3 = "SELECT * from guia where despacho is not null and despacho = 'SI' and detalle->'$.estado_retiro' != 'COMPLETO' "
            cursor.execute(sql3)
            guias = cursor.fetchall()

            return jsonify(
                ventas=ventas,
                guias=guias
            )
    finally:
        miConexion.close()