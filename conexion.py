import pyodbc

def obtener_conexion():
    datos_conexion = (
        "Driver={SQL Server};"
        "Server=.;"
        "Database=TIENDAjp;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    try:
        return pyodbc.connect(datos_conexion)
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None
