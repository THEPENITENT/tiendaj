#!/bin/bash
# ============================================
# install.sh - Instalación de TIENDAJ Web App
# Clona el repo, instala dependencias,
# configura MariaDB y lanza la app web
# PRIMERO verifica si hay respaldo previo
# ============================================

REPO_URL="https://github.com/THEPENITENT/tiendaj.git"
APP_DIR="$HOME/TIENDAJ-Web"
BACKUP_DIR="$HOME/backups-tiendaj"
DB_NAME="tiendaj"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "  TIENDAJ - Script de Instalación"
echo "=========================================="
echo ""

# ─── PASO 1: Verificar respaldo previo ───
echo -e "${YELLOW}[1/5] Verificando respaldos previos...${NC}"
RESTAURAR="n"

if [ -d "$BACKUP_DIR" ]; then
    ULTIMO_BACKUP=$(ls -t "$BACKUP_DIR"/*_archivos.tar.gz 2>/dev/null | head -1)

    if [ -n "$ULTIMO_BACKUP" ]; then
        echo -e "${CYAN}   Se encontró respaldo:${NC}"
        echo "   $ULTIMO_BACKUP"
        echo ""
        read -p "   ¿Restaurar desde respaldo? (s/n): " RESTAURAR

        if [[ "$RESTAURAR" == "s" || "$RESTAURAR" == "S" ]]; then
            echo -e "${YELLOW}   Restaurando...${NC}"
            [ -d "$APP_DIR" ] && rm -rf "$APP_DIR"
            tar -xzf "$ULTIMO_BACKUP" -C "$HOME" 2>/dev/null

            # Restaurar BD si existe dump
            ULTIMO_DB=$(ls -t "$BACKUP_DIR"/*_db.sql 2>/dev/null | head -1)
            if [ -n "$ULTIMO_DB" ]; then
                echo -e "${YELLOW}   Restaurando base de datos...${NC}"
                mysql -u root -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;" 2>/dev/null
                mysql -u root "$DB_NAME" < "$ULTIMO_DB" 2>/dev/null
                echo -e "${GREEN}   BD restaurada.${NC}"
            fi

            echo -e "${GREEN}   Respaldo restaurado.${NC}"
        fi
    else
        echo -e "   No se encontraron respaldos."
    fi
else
    echo -e "   No existe directorio de respaldos."
fi

# ─── PASO 2: Clonar repositorio ───
echo ""
echo -e "${YELLOW}[2/5] Preparando archivos...${NC}"

if [[ "$RESTAURAR" != "s" && "$RESTAURAR" != "S" ]]; then
    [ -d "$APP_DIR" ] && rm -rf "$APP_DIR"

    echo -e "   Clonando repositorio..."
    git clone "$REPO_URL" "$APP_DIR" 2>/dev/null

    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] No se pudo clonar el repositorio.${NC}"
        exit 1
    fi
    echo -e "${GREEN}   Repositorio clonado.${NC}"
fi

# ─── PASO 3: Verificar Python ───
echo ""
echo -e "${YELLOW}[3/5] Verificando Python...${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}[ERROR] Python no instalado.${NC}"
    echo "   sudo pacman -S python"
    exit 1
fi
echo -e "${GREEN}   $($PYTHON_CMD --version)${NC}"

# ─── PASO 4: Instalar dependencias ───
echo ""
echo -e "${YELLOW}[4/5] Instalando dependencias...${NC}"

cd "$APP_DIR"
$PYTHON_CMD -m venv venv 2>/dev/null
source venv/bin/activate 2>/dev/null
pip install -r requirements.txt 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   Dependencias instaladas.${NC}"
else
    echo -e "${RED}   Error en dependencias.${NC}"
fi

# ─── PASO 5: Configurar BD y ejecutar ───
echo ""
echo -e "${YELLOW}[5/5] Configurando base de datos...${NC}"

# Verificar MariaDB
if systemctl is-active --quiet mariadb; then
    echo -e "${GREEN}   MariaDB está corriendo.${NC}"
else
    echo -e "${YELLOW}   Iniciando MariaDB...${NC}"
    sudo systemctl start mariadb 2>/dev/null
fi

# Crear BD si no se restauró
if [[ "$RESTAURAR" != "s" && "$RESTAURAR" != "S" ]]; then
    mysql -u root < "$APP_DIR/sql/schema.sql" 2>/dev/null
    echo -e "${GREEN}   Base de datos creada con datos de ejemplo.${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  INSTALACIÓN COMPLETADA${NC}"
echo "  Directorio: $APP_DIR"
echo "=========================================="
echo ""
echo "Para ejecutar manualmente:"
echo "  cd $APP_DIR"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""

read -p "¿Ejecutar la app ahora? (s/n): " EJECUTAR
if [[ "$EJECUTAR" == "s" || "$EJECUTAR" == "S" ]]; then
    echo -e "${CYAN}   Abriendo en http://localhost:5000${NC}"
    $PYTHON_CMD app.py
fi
