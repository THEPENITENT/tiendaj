#!/bin/bash
# ============================================
# backup.sh - Respaldo de TIENDAJ Web App
# Respalda archivos del proyecto y base de
# datos MariaDB usando mysqldump
# ============================================

APP_DIR="$HOME/TIENDAJ-Web"
BACKUP_DIR="$HOME/backups-tiendaj"
FECHA=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="tiendaj_backup_$FECHA"
DB_NAME="tiendaj"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "  TIENDAJ - Script de Respaldo"
echo "=========================================="
echo ""

# Verificar que el proyecto existe
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}[ERROR] No se encontró el proyecto en $APP_DIR${NC}"
    exit 1
fi

# Crear directorio de backups
mkdir -p "$BACKUP_DIR"

# 1. Respaldar archivos
echo -e "${YELLOW}[1/3] Respaldando archivos del proyecto...${NC}"
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_archivos.tar.gz" \
    --exclude='__pycache__' \
    --exclude='venv' \
    --exclude='.git' \
    -C "$HOME" "TIENDAJ-Web" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   Archivos respaldados correctamente.${NC}"
else
    echo -e "${RED}   Error al respaldar archivos.${NC}"
    exit 1
fi

# 2. Respaldar base de datos MariaDB
echo -e "${YELLOW}[2/3] Respaldando base de datos MariaDB...${NC}"
if command -v mysqldump &> /dev/null; then
    mysqldump -u root "$DB_NAME" > "$BACKUP_DIR/${BACKUP_NAME}_db.sql" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   Base de datos respaldada correctamente.${NC}"
    else
        echo -e "${YELLOW}   No se pudo respaldar la BD. Copiando schema...${NC}"
        cp "$APP_DIR/sql/schema.sql" "$BACKUP_DIR/${BACKUP_NAME}_schema.sql"
    fi
else
    echo -e "${YELLOW}   mysqldump no encontrado. Copiando schema...${NC}"
    cp "$APP_DIR/sql/schema.sql" "$BACKUP_DIR/${BACKUP_NAME}_schema.sql"
fi

# 3. Registro del respaldo
echo -e "${YELLOW}[3/3] Generando registro...${NC}"
cat > "$BACKUP_DIR/${BACKUP_NAME}_info.txt" << EOF
=== Registro de Respaldo TIENDAJ ===
Fecha: $(date '+%Y-%m-%d %H:%M:%S')
Directorio: $APP_DIR
Base de datos: $DB_NAME
Usuario: $(whoami)
Hostname: $(hostname)
EOF

echo -e "${GREEN}   Registro generado.${NC}"
echo ""
echo "=========================================="
echo -e "${GREEN}  RESPALDO COMPLETADO${NC}"
echo "  Ubicación: $BACKUP_DIR/"
echo "=========================================="
echo ""
ls -lh "$BACKUP_DIR"/${BACKUP_NAME}* 2>/dev/null
