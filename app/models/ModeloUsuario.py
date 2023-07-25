from ..extensions import obtener_conexion

class ModeloUsuario():
    
    @classmethod
    def login(self,nombre):
        #VALIDAR CUENTA EN DB
        miConexion = obtener_conexion()
        try:
            with miConexion.cursor() as cursor:
        
                sql = "select * from usuario where nombre = %s"
                cursor.execute( sql , ( nombre )  )
                consulta = cursor.fetchone()
                return consulta

        finally:
            miConexion.close()