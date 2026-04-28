import pymysql
import os

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': 'tiendaj',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    """Obtener conexión a MariaDB."""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

def init_db():
    """Crear base de datos y tablas si no existen."""
    try:
        # Conectar sin especificar database para poder crearla
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        # Leer y ejecutar schema
        schema_path = os.path.join(os.path.dirname(__file__), 'sql', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        # Ejecutar cada statement por separado
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except pymysql.err.IntegrityError:
                    # Datos ya existen, ignorar
                    pass

        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente.")
        return True
    except Exception as e:
        print(f"Error al inicializar BD: {e}")
        return False
