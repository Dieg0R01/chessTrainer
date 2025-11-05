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

# Inicializar conda
source "$(conda info --base)/etc/profile.d/conda.sh"

# Verificar que el entorno chess existe
if ! conda env list | grep -q "^chess "; then
    echo "❌ Error: El entorno conda 'chess' no existe"
    echo "   Crea el entorno con: conda create -n chess python=3.9"
    exit 1
fi

# Activar entorno y verificar dependencias
conda activate chess
if [ $? -ne 0 ]; then
    echo "❌ Error: No se pudo activar el entorno conda 'chess'"
    exit 1
fi

# Verificar e instalar dependencias si faltan
echo "🔍 Verificando dependencias..."

# Verificar dependencias críticas y instalar si faltan
CHECK_DEPS=$(python -c "
import sys
missing = []
try:
    import uvicorn
except ImportError:
    missing.append('uvicorn[standard]')
try:
    import fastapi
except ImportError:
    missing.append('fastapi')
try:
    import chess
except ImportError:
    missing.append('python-chess')
try:
    import yaml
except ImportError:
    missing.append('PyYAML')
try:
    import httpx
except ImportError:
    missing.append('httpx')
try:
    import jsonpath
except ImportError:
    missing.append('jsonpath')

if missing:
    print(' '.join(missing))
    sys.exit(1)
else:
    print('OK')
" 2>&1)

if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependencias faltantes..."
    echo "$CHECK_DEPS" | grep -v "^OK$" | while read -r dep; do
        if [ -n "$dep" ] && [ "$dep" != "OK" ]; then
            echo "   Instalando: $dep"
            pip install -q "$dep" 2>&1 | grep -v "already satisfied" || true
        fi
    done
    
    # También instalar desde requirements.txt para asegurar versiones correctas
    if [ -f "requirements.txt" ]; then
        echo "   Instalando desde requirements.txt..."
        pip install -q -r requirements.txt 2>&1 | grep -v "already satisfied" || true
    fi
    
    echo "✅ Dependencias verificadas/instaladas"
    echo ""
fi

# Función para manejar Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Deteniendo servidores..."
    pkill -f "uvicorn main:app"
    pkill -f "vite"
    
    # Limpiar script temporal si existe
    if [ -f .backend_script.path ]; then
        BACKEND_SCRIPT_PATH=$(cat .backend_script.path)
        rm -f "$BACKEND_SCRIPT_PATH" .backend_script.path .backend.pid 2>/dev/null || true
    fi
    
    echo "✅ Servidores detenidos"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Obtener IP local para mostrar en la salida
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

# Iniciar backend en segundo plano
echo -e "${BLUE}📦 Iniciando Backend (FastAPI)...${NC}"

# Asegurar que estamos en el entorno correcto
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate chess

# Verificar que podemos importar los módulos antes de iniciar
echo "🔍 Verificando importaciones del backend..."
IMPORT_CHECK=$(python -c "
try:
    import main
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
    import sys
    sys.exit(1)
" 2>&1)

if [ $? -ne 0 ]; then
    echo "❌ Error al importar módulos del backend:"
    echo "$IMPORT_CHECK"
    echo ""
    echo "💡 Intentando instalar todas las dependencias desde requirements.txt..."
    pip install -q -r requirements.txt
    echo ""
    echo "🔍 Verificando nuevamente..."
    if ! python -c "import main" 2>/dev/null; then
        echo "❌ Error: No se pueden importar los módulos del backend después de instalar dependencias"
        echo "   Revisa los logs anteriores para más detalles"
        exit 1
    fi
    echo "✅ Módulos importados correctamente después de instalar dependencias"
else
    echo "✅ Módulos del backend verificados correctamente"
fi
echo ""

# Limpiar procesos anteriores si existen
pkill -f "uvicorn main:app" 2>/dev/null || true
sleep 1

# Obtener ruta absoluta del proyecto
PROJECT_DIR=$(pwd)

# Crear script temporal para iniciar backend con entorno conda
BACKEND_SCRIPT=$(mktemp /tmp/chess_trainer_backend_XXXXXX.sh)
cat > "$BACKEND_SCRIPT" << EOF
#!/bin/bash
source "\$(conda info --base)/etc/profile.d/conda.sh"
conda activate chess
cd "$PROJECT_DIR"
exec uvicorn main:app --reload --host 0.0.0.0 --port 8000
EOF
chmod +x "$BACKEND_SCRIPT"

# Iniciar backend en segundo plano con el script
"$BACKEND_SCRIPT" > logs_backend.log 2>&1 &
BACKEND_PID=$!

# Guardar el PID del script también para limpieza
echo "$BACKEND_PID" > .backend.pid
echo "$BACKEND_SCRIPT" > .backend_script.path
echo "   Backend PID: $BACKEND_PID"
echo "   URL Local: http://localhost:8000"
if [ -n "$LOCAL_IP" ]; then
    echo "   URL Red: http://$LOCAL_IP:8000"
fi
echo ""

# Esperar un poco para que el backend inicie
sleep 2

# Iniciar frontend en segundo plano
echo -e "${BLUE}🎨 Iniciando Frontend (Vite)...${NC}"
cd frontend
npm run dev -- --host > ../logs_frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   Frontend PID: $FRONTEND_PID"
echo "   URL Local: http://localhost:5173"
if [ -n "$LOCAL_IP" ]; then
    echo "   URL Red: http://$LOCAL_IP:5173"
fi
echo ""

# Esperar un poco para verificar que iniciaron correctamente
sleep 3

# Verificar que los procesos estén corriendo
echo "🔍 Verificando procesos..."
sleep 2  # Dar tiempo para que los procesos inicien

if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo "❌ Error: El backend no pudo iniciar."
    echo "📝 Últimas líneas del log del backend:"
    tail -20 logs_backend.log 2>/dev/null | head -20 || echo "   (no hay logs disponibles)"
    echo ""
    echo "💡 Intenta ejecutar manualmente: bash start_backend.sh"
    exit 1
fi

if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo "❌ Error: El frontend no pudo iniciar."
    echo "📝 Últimas líneas del log del frontend:"
    tail -20 logs_frontend.log 2>/dev/null | head -20 || echo "   (no hay logs disponibles)"
    pkill -f "uvicorn main:app" 2>/dev/null || true
    exit 1
fi

# Verificar que el backend esté respondiendo
echo "🔍 Verificando que el backend responda..."
BACKEND_RESPONDING=false
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        BACKEND_RESPONDING=true
        echo "✅ Backend respondiendo correctamente"
        break
    fi
    sleep 1
done

if [ "$BACKEND_RESPONDING" = false ]; then
    echo "⚠️  Advertencia: El backend no responde aún (puede tardar unos segundos más)"
    echo "   El proceso está corriendo (PID: $BACKEND_PID)"
    echo "   Revisa los logs: tail -f logs_backend.log"
fi
echo ""

echo -e "${GREEN}✅ Chess Trainer está corriendo!${NC}"
echo ""
echo "📋 Información:"
if [ -n "$LOCAL_IP" ]; then
    echo "   🌐 Acceso desde tu red local:"
    echo "      - Frontend: http://$LOCAL_IP:5173"
    echo "      - Backend:  http://$LOCAL_IP:8000"
    echo ""
fi
echo "   💻 Acceso local:"
echo "      - Frontend: http://localhost:5173"
echo "      - Backend:  http://localhost:8000"
echo ""
echo "   📝 Logs:"
echo "      - Backend:  tail -f logs_backend.log"
echo "      - Frontend: tail -f logs_frontend.log"
echo ""
echo "Para detener la aplicación:"
echo "   - Presiona Ctrl+C en esta terminal"
echo "   - O ejecuta: ./stop.sh"
echo ""

# Mantener el script corriendo
wait


