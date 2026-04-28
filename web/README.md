# TIENDAJ Web - Sistema de Gestión para Tienda de Videojuegos

Aplicación web desarrollada con Flask y MariaDB para la gestión de una tienda de videojuegos. Incluye dashboard, CRUD de videojuegos, clientes y registro de ventas.

## Requisitos

- Python 3.10+
- MariaDB
- Git

## Instalación rápida

```bash
git clone https://github.com/THEPENITENT/tiendaj.git
cd tiendaj
pip install -r requirements.txt
python app.py
```

Abrir en el navegador: `http://localhost:5000`

## Scripts de DevOps

| Script | Descripción |
|--------|-------------|
| `scripts/install.sh` | Verifica respaldo, clona repo, instala deps, configura MariaDB, lanza app |
| `scripts/uninstall.sh` | Ofrece respaldo, detiene procesos, elimina BD y archivos |
| `scripts/backup.sh` | Respaldo de archivos (tar.gz) y base de datos (mysqldump) |

## Tecnologías

- **Backend:** Flask (Python)
- **Base de datos:** MariaDB
- **Frontend:** HTML/CSS (tema gaming oscuro)
