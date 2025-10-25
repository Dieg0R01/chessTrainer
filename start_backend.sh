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

# Iniciar backend
echo -e "${BLUE}📦 Iniciando Backend (FastAPI)...${NC}"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate chess
uvicorn main:app --reload --host 0.0.0.0 --port 8000
