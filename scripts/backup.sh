#!/bin/bash
# ============================================
# backup.sh - Respaldo de TIENDAJ App
# Genera un respaldo de la base de datos
# y los archivos del proyecto
# ============================================

# --- Configuración ---
APP_DIR="$HOME/TIENDAJ-App"
BACKUP_DIR="$HOME/backups-tiendaj"
FECHA=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="tiendaj_backup_$FECHA"
DB_NAME="TIENDAjp"

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sin color

echo "=========================================="
echo "  TIENDAJ - Script de Respaldo"
echo "=========================================="
echo ""

# Verificar que el proyecto existe
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}[ERROR] No se encontró el proyecto en $APP_DIR${NC}"
    echo "Asegúrate de que la aplicación esté instalada."
    exit 1
fi

# Crear directorio de backups si no existe
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}[1/3] Respaldando archivos del proyecto...${NC}"
# Copiar archivos del proyecto (excluyendo __pycache__ y venv)
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_archivos.tar.gz" \
    --exclude='__pycache__' \
    --exclude='venv' \
    --exclude='.git' \
    -C "$HOME" "TIENDAJ-App" 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   Archivos respaldados correctamente.${NC}"
else
    echo -e "${RED}   Error al respaldar archivos.${NC}"
    exit 1
fi

echo -e "${YELLOW}[2/3] Respaldando base de datos...${NC}"
# Intentar respaldo de BD con sqlcmd (si está disponible)
if command -v sqlcmd &> /dev/null; then
    sqlcmd -S localhost -d "$DB_NAME" -Q \
        "BACKUP DATABASE [$DB_NAME] TO DISK='$BACKUP_DIR/${BACKUP_NAME}_db.bak'" \
        2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}   Base de datos respaldada correctamente.${NC}"
    else
        echo -e "${YELLOW}   No se pudo conectar a SQL Server. Se respaldó solo el schema SQL.${NC}"
        cp "$APP_DIR/sql/schema.sql" "$BACKUP_DIR/${BACKUP_NAME}_schema.sql" 2>/dev/null
    fi
else
    echo -e "${YELLOW}   sqlcmd no disponible. Respaldando schema SQL como alternativa...${NC}"
    cp "$APP_DIR/sql/schema.sql" "$BACKUP_DIR/${BACKUP_NAME}_schema.sql" 2>/dev/null
fi

echo -e "${YELLOW}[3/3] Generando archivo de registro...${NC}"
# Crear log del respaldo
cat > "$BACKUP_DIR/${BACKUP_NAME}_info.txt" << EOF
=== Registro de Respaldo TIENDAJ ===
Fecha: $(date '+%Y-%m-%d %H:%M:%S')
Directorio original: $APP_DIR
Archivos: ${BACKUP_NAME}_archivos.tar.gz
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
echo ""
