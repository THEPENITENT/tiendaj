#!/bin/bash
# ============================================
# install.sh - Instalación de TIENDAJ App
# Clona el repositorio, instala dependencias
# y verifica si existe un respaldo previo
# ============================================

# --- Configuración ---
REPO_URL="https://github.com/THEPENITENT/tiendaj.git"
APP_DIR="$HOME/TIENDAJ-App"
BACKUP_DIR="$HOME/backups-tiendaj"

# Colores para mensajes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "=========================================="
echo "  TIENDAJ - Script de Instalación"
echo "=========================================="
echo ""

# ─── PASO 1: Verificar si existe un respaldo previo ───
echo -e "${YELLOW}[1/5] Verificando respaldos previos...${NC}"

if [ -d "$BACKUP_DIR" ]; then
    # Buscar el backup más reciente
    ULTIMO_BACKUP=$(ls -t "$BACKUP_DIR"/*_archivos.tar.gz 2>/dev/null | head -1)

    if [ -n "$ULTIMO_BACKUP" ]; then
        echo -e "${CYAN}   Se encontró un respaldo previo:${NC}"
        echo "   $ULTIMO_BACKUP"
        echo ""
        read -p "   ¿Deseas restaurar desde el respaldo? (s/n): " RESPUESTA

        if [[ "$RESPUESTA" == "s" || "$RESPUESTA" == "S" ]]; then
            echo -e "${YELLOW}   Restaurando desde respaldo...${NC}"

            # Limpiar instalación anterior si existe
            if [ -d "$APP_DIR" ]; then
                rm -rf "$APP_DIR"
            fi

            # Extraer backup
            tar -xzf "$ULTIMO_BACKUP" -C "$HOME" 2>/dev/null

            if [ $? -eq 0 ]; then
                echo -e "${GREEN}   Respaldo restaurado correctamente.${NC}"
            else
                echo -e "${RED}   Error al restaurar. Se procederá con instalación limpia.${NC}"
                RESPUESTA="n"
            fi
        fi
    else
        echo -e "   No se encontraron respaldos."
        RESPUESTA="n"
    fi
else
    echo -e "   No existe directorio de respaldos."
    RESPUESTA="n"
fi

# ─── PASO 2: Clonar repositorio (si no se restauró backup) ───
echo ""
echo -e "${YELLOW}[2/5] Preparando archivos del proyecto...${NC}"

if [[ "$RESPUESTA" != "s" && "$RESPUESTA" != "S" ]]; then
    # Verificar si ya existe el directorio
    if [ -d "$APP_DIR" ]; then
        echo -e "${YELLOW}   El directorio ya existe. Eliminando para instalación limpia...${NC}"
        rm -rf "$APP_DIR"
    fi

    # Clonar desde GitHub
    echo -e "   Clonando repositorio..."
    git clone "$REPO_URL" "$APP_DIR" 2>/dev/null

    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] No se pudo clonar el repositorio.${NC}"
        echo "   Verifica tu conexión a internet y que el repo exista."
        exit 1
    fi
    echo -e "${GREEN}   Repositorio clonado.${NC}"
fi

# ─── PASO 3: Verificar Python ───
echo ""
echo -e "${YELLOW}[3/5] Verificando Python...${NC}"

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}   Python3 encontrado: $($PYTHON_CMD --version)${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "${GREEN}   Python encontrado: $($PYTHON_CMD --version)${NC}"
else
    echo -e "${RED}[ERROR] Python no está instalado.${NC}"
    echo "   Instala Python 3.10+ con: sudo pacman -S python (Garuda/Arch)"
    exit 1
fi

# ─── PASO 4: Crear entorno virtual e instalar dependencias ───
echo ""
echo -e "${YELLOW}[4/5] Instalando dependencias...${NC}"

cd "$APP_DIR"

# Crear entorno virtual
$PYTHON_CMD -m venv venv 2>/dev/null
source venv/bin/activate 2>/dev/null

# Instalar dependencias
pip install -r requirements.txt 2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   Dependencias instaladas correctamente.${NC}"
else
    echo -e "${RED}   Error al instalar dependencias.${NC}"
    echo "   Intenta manualmente: pip install -r requirements.txt"
fi

# ─── PASO 5: Ejecutar la aplicación ───
echo ""
echo -e "${YELLOW}[5/5] Iniciando aplicación...${NC}"
echo -e "${CYAN}   NOTA: Asegúrate de que SQL Server esté corriendo${NC}"
echo -e "${CYAN}   y que la base de datos 'TIENDAjp' exista.${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}  INSTALACIÓN COMPLETADA${NC}"
echo "  Directorio: $APP_DIR"
echo "=========================================="
echo ""
echo "Para ejecutar la app manualmente:"
echo "  cd $APP_DIR"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""

# Preguntar si desea ejecutar ahora
read -p "¿Deseas ejecutar la aplicación ahora? (s/n): " EJECUTAR
if [[ "$EJECUTAR" == "s" || "$EJECUTAR" == "S" ]]; then
    $PYTHON_CMD app.py
fi
