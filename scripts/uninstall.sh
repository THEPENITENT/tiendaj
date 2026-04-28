#!/bin/bash
# ============================================
# uninstall.sh - Desinstalación de TIENDAJ App
# Detiene procesos y elimina archivos
# ============================================

# --- Configuración ---
APP_DIR="$HOME/TIENDAJ-App"
BACKUP_DIR="$HOME/backups-tiendaj"

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "  TIENDAJ - Script de Desinstalación"
echo "=========================================="
echo ""

# Verificar que el proyecto existe
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}[ERROR] No se encontró el proyecto en $APP_DIR${NC}"
    echo "La aplicación no está instalada."
    exit 1
fi

# ─── PASO 1: Preguntar si desea hacer respaldo antes de borrar ───
echo -e "${YELLOW}[1/3] Verificación de respaldo...${NC}"
read -p "   ¿Deseas crear un respaldo antes de desinstalar? (s/n): " BACKUP

if [[ "$BACKUP" == "s" || "$BACKUP" == "S" ]]; then
    echo -e "${CYAN}   Ejecutando script de respaldo...${NC}"

    if [ -f "$APP_DIR/scripts/backup.sh" ]; then
        bash "$APP_DIR/scripts/backup.sh"
    else
        echo -e "${YELLOW}   Script de backup no encontrado. Creando respaldo rápido...${NC}"
        mkdir -p "$BACKUP_DIR"
        FECHA=$(date +%Y%m%d_%H%M%S)
        tar -czf "$BACKUP_DIR/tiendaj_backup_${FECHA}_archivos.tar.gz" \
            --exclude='__pycache__' \
            --exclude='venv' \
            --exclude='.git' \
            -C "$HOME" "TIENDAJ-App" 2>/dev/null
        echo -e "${GREEN}   Respaldo rápido creado.${NC}"
    fi
fi

# ─── PASO 2: Detener procesos de la aplicación ───
echo ""
echo -e "${YELLOW}[2/3] Deteniendo procesos...${NC}"

# Matar procesos de Python relacionados con la app
pkill -f "python.*app.py" 2>/dev/null
pkill -f "python3.*app.py" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   Procesos detenidos.${NC}"
else
    echo -e "   No se encontraron procesos activos de la app."
fi

# ─── PASO 3: Eliminar archivos del proyecto ───
echo ""
echo -e "${YELLOW}[3/3] Eliminando archivos del proyecto...${NC}"
echo -e "${RED}   ADVERTENCIA: Se eliminará $APP_DIR${NC}"
read -p "   ¿Estás seguro? (s/n): " CONFIRMAR

if [[ "$CONFIRMAR" == "s" || "$CONFIRMAR" == "S" ]]; then
    rm -rf "$APP_DIR"

    if [ ! -d "$APP_DIR" ]; then
        echo -e "${GREEN}   Archivos eliminados correctamente.${NC}"
    else
        echo -e "${RED}   Error al eliminar archivos.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}   Desinstalación cancelada por el usuario.${NC}"
    exit 0
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  DESINSTALACIÓN COMPLETADA${NC}"
echo "=========================================="

# Mostrar si quedan backups
if [ -d "$BACKUP_DIR" ]; then
    echo ""
    echo -e "${CYAN}  Nota: Los respaldos siguen en:${NC}"
    echo "  $BACKUP_DIR"
    echo ""
fi
