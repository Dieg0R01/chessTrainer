#!/bin/bash

# Script para iniciar solo el Backend de Chess Trainer
# Uso: ./start_backend.sh

echo "🚀 Iniciando Chess Trainer Backend..."
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar que conda está disponible
if ! command -v conda &> /dev/null; then
    echo "❌ Error: Conda no está instalado o no está en el PATH"
    exit 1
fi

# Inicializar conda
source "$(conda info --base)/etc/profile.d/conda.sh"

# Verificar que el entorno chess existe
if ! conda env list | grep -q "^chess "; then
    echo "❌ Error: El entorno conda 'chess' no existe"
    echo "   Crea el entorno con: conda create -n chess python=3.9"
    exit 1
fi

# Activar entorno
conda activate chess
if [ $? -ne 0 ]; then
    echo "❌ Error: No se pudo activar el entorno conda 'chess'"
    exit 1
fi

# Verificar e instalar dependencias si faltan
echo "🔍 Verificando dependencias..."
if ! python -c "import uvicorn, fastapi, chess, yaml, httpx" 2>/dev/null; then
    echo "⚠️  Instalando dependencias desde requirements.txt..."
    pip install -q -r requirements.txt 2>&1 | grep -v "already satisfied" || true
    echo "✅ Dependencias instaladas"
    echo ""
fi

# Función para manejar Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Deteniendo backend..."
    pkill -f "uvicorn main:app"
    echo "✅ Backend detenido"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Obtener IP local para mostrar en la salida
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

# Verificar que podemos importar los módulos antes de iniciar
echo "🔍 Verificando importaciones del backend..."
if ! python -c "import main" 2>/dev/null; then
    echo "❌ Error: No se pueden importar los módulos del backend"
    echo "   Instalando dependencias desde requirements.txt..."
    pip install -q -r requirements.txt
    if ! python -c "import main" 2>/dev/null; then
        echo "❌ Error: No se pueden importar los módulos después de instalar dependencias"
        echo "   Revisa los errores anteriores"
        exit 1
    fi
fi
echo "✅ Backend listo para iniciar"
echo ""

# Limpiar procesos anteriores si existen
pkill -f "uvicorn main:app" 2>/dev/null || true
sleep 1

# Iniciar backend
echo -e "${BLUE}📦 Iniciando Backend (FastAPI)...${NC}"
echo "   URL Local: http://localhost:8000"
if [ -n "$LOCAL_IP" ]; then
    echo "   URL Red: http://$LOCAL_IP:8000"
fi
echo ""
echo "📝 Los logs se mostrarán a continuación. Presiona Ctrl+C para detener."
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
