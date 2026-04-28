#!/bin/bash
# ============================================
# uninstall.sh - Desinstalación TIENDAJ Web
# Detiene la app, ofrece respaldo y elimina
# ============================================

APP_DIR="$HOME/TIENDAJ-Web"
BACKUP_DIR="$HOME/backups-tiendaj"
DB_NAME="tiendaj"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "  TIENDAJ - Script de Desinstalación"
echo "=========================================="
echo ""

# Verificar que existe
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}[ERROR] No se encontró $APP_DIR${NC}"
    exit 1
fi

# ─── PASO 1: Ofrecer respaldo ───
echo -e "${YELLOW}[1/4] Verificación de respaldo...${NC}"
read -p "   ¿Crear respaldo antes de desinstalar? (s/n): " BACKUP

if [[ "$BACKUP" == "s" || "$BACKUP" == "S" ]]; then
    if [ -f "$APP_DIR/scripts/backup.sh" ]; then
        bash "$APP_DIR/scripts/backup.sh"
    else
        echo -e "${YELLOW}   Creando respaldo rápido...${NC}"
        mkdir -p "$BACKUP_DIR"
        FECHA=$(date +%Y%m%d_%H%M%S)
        tar -czf "$BACKUP_DIR/tiendaj_backup_${FECHA}_archivos.tar.gz" \
            --exclude='__pycache__' --exclude='venv' --exclude='.git' \
            -C "$HOME" "TIENDAJ-Web" 2>/dev/null
        echo -e "${GREEN}   Respaldo creado.${NC}"
    fi
fi

# ─── PASO 2: Detener procesos ───
echo ""
echo -e "${YELLOW}[2/4] Deteniendo procesos...${NC}"
pkill -f "python.*app.py" 2>/dev/null
pkill -f "flask" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   Procesos detenidos.${NC}"
else
    echo -e "   No había procesos activos."
fi

# ─── PASO 3: Eliminar base de datos ───
echo ""
echo -e "${YELLOW}[3/4] Base de datos...${NC}"
read -p "   ¿Eliminar la base de datos '$DB_NAME'? (s/n): " DROP_DB

if [[ "$DROP_DB" == "s" || "$DROP_DB" == "S" ]]; then
    mysql -u root -e "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   Base de datos eliminada.${NC}"
    else
        echo -e "${RED}   No se pudo eliminar la BD.${NC}"
    fi
else
    echo -e "   Base de datos conservada."
fi

# ─── PASO 4: Eliminar archivos ───
echo ""
echo -e "${YELLOW}[4/4] Eliminando archivos...${NC}"
echo -e "${RED}   ADVERTENCIA: Se eliminará $APP_DIR${NC}"
read -p "   ¿Estás seguro? (s/n): " CONFIRMAR

if [[ "$CONFIRMAR" == "s" || "$CONFIRMAR" == "S" ]]; then
    rm -rf "$APP_DIR"
    if [ ! -d "$APP_DIR" ]; then
        echo -e "${GREEN}   Archivos eliminados.${NC}"
    else
        echo -e "${RED}   Error al eliminar.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}   Cancelado.${NC}"
    exit 0
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  DESINSTALACIÓN COMPLETADA${NC}"
echo "=========================================="

if [ -d "$BACKUP_DIR" ]; then
    echo ""
    echo -e "${CYAN}  Respaldos en: $BACKUP_DIR${NC}"
fi
