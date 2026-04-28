# login_dao.py — Login con restricción de puesto autorizado
from conexion import obtener_conexion


# Puestos autorizados para usar la app de gestión completa.
# Comparación case-insensitive y sin espacios extras.
# Más adelante se puede agregar 'cajero' u otros con vistas limitadas.
PUESTOS_AUTORIZADOS = {"administrador", "dueno", "dueño", "gerente"}


class LoginDAO:
    def verificar_credenciales(self, id_usuario, password):
        conn = obtener_conexion()
        if not conn:
            return False, "Error de conexión con la base de datos"

        try:
            cursor = conn.cursor()

            # 1) Buscar al empleado por su ID; traer contraseña y puesto
            cursor.execute(
                "SELECT contrasena, puesto FROM empleados WHERE idempleados = ?",
                (id_usuario,)
            )
            registro = cursor.fetchone()

            # 2) ¿Existe el usuario?
            if registro is None:
                return False, "El usuario (ID) ingresado no existe."

            contrasena_db = registro[0]
            puesto_db     = registro[1]

            # 3) ¿La contraseña coincide?
            if contrasena_db != password:
                return False, "La contraseña es incorrecta."

            # 4) ¿El puesto está autorizado para esta versión?
            if not puesto_db:
                return False, "El usuario no tiene un puesto asignado en la BD."

            puesto_norm = puesto_db.strip().lower()
            if puesto_norm not in PUESTOS_AUTORIZADOS:
                return False, (f"Acceso denegado.\n"
                               f"Tu puesto ('{puesto_db}') no tiene permiso para esta "
                               f"versión.\nSolo administrador, dueño y gerente pueden acceder.")

            # Login exitoso
            return True, puesto_db

        except Exception as e:
            return False, f"Error en el sistema: {e}"
        finally:
            conn.close()
