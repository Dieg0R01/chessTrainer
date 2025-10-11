#!/bin/bash

# Script para iniciar Chess Trainer
# Uso: ./start.sh

echo "🚀 Iniciando Chess Trainer..."
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
    echo "🛑 Deteniendo servidores..."
    pkill -f "uvicorn main:app"
    pkill -f "vite"
    echo "✅ Servidores detenidos"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar backend en segundo plano
echo -e "${BLUE}📦 Iniciando Backend (FastAPI)...${NC}"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate chess
uvicorn main:app --reload --port 8000 > logs_backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   URL: http://localhost:8000"
echo ""

# Esperar un poco para que el backend inicie
sleep 2

# Iniciar frontend en segundo plano
echo -e "${BLUE}🎨 Iniciando Frontend (Vite)...${NC}"
cd frontend
npm run dev > ../logs_frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   Frontend PID: $FRONTEND_PID"
echo "   URL: http://localhost:5173"
echo ""

# Esperar un poco para verificar que iniciaron correctamente
sleep 3

# Verificar que los procesos estén corriendo
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Error: El backend no pudo iniciar. Revisa logs_backend.log"
    exit 1
fi

if ! ps -p $FRONTEND_PID > /dev/null; then
    echo "❌ Error: El frontend no pudo iniciar. Revisa logs_frontend.log"
    pkill -f "uvicorn main:app"
    exit 1
fi

echo -e "${GREEN}✅ Chess Trainer está corriendo!${NC}"
echo ""
echo "📋 Información:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend:  http://localhost:8000"
echo "   - Logs backend:  tail -f logs_backend.log"
echo "   - Logs frontend: tail -f logs_frontend.log"
echo ""
echo "Para detener la aplicación:"
echo "   - Presiona Ctrl+C en esta terminal"
echo "   - O ejecuta: ./stop.sh"
echo ""

# Mantener el script corriendo
wait

