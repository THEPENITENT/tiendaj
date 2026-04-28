# TIENDAJ - Sistema de Gestión para Tienda de Videojuegos

Sistema de escritorio desarrollado en Python con CustomTkinter para la gestión integral de una tienda de videojuegos. Conecta a una base de datos SQL Server con 22 tablas normalizadas.

## Funcionalidades

- Login de empleados
- Gestión de catálogos (clasificaciones, géneros, plataformas)
- Gestión geográfica (países, estados, ciudades, colonias, calles)
- Administración de sucursales, clientes, empleados y proveedores
- Control de inventarios
- Registro de ventas y detalle de ventas
- Directorio de contacto (teléfonos y correos)

## Requisitos

- Python 3.10+
- SQL Server (Express o superior)
- ODBC Driver for SQL Server

## Instalación rápida

```bash
git clone https://github.com/THEPENITENT/TIENDAJ-App.git
cd TIENDAJ-App
pip install -r requirements.txt
```

Crear la base de datos ejecutando `sql/schema.sql` en SQL Server Management Studio, luego:

```bash
python app.py
```

## Scripts de DevOps

En la carpeta `scripts/` se encuentran 3 scripts bash para automatizar el ciclo de vida de la aplicación:

| Script | Descripción |
|--------|-------------|
| `install.sh` | Clona el repo, instala dependencias, restaura backup si existe |
| `uninstall.sh` | Detiene la app y elimina los archivos del proyecto |
| `backup.sh` | Genera respaldo de la base de datos y archivos del proyecto |

## Tecnologías

- **Frontend:** CustomTkinter (GUI de escritorio)
- **Backend:** Python + pyodbc
- **Base de datos:** SQL Server
- **Control de versiones:** Git/GitHub
