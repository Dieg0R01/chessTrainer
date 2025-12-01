#!/bin/bash
# Script para iniciar Chess Trainer completo
# Inicia Docker, backend y frontend

set -e

echo "🚀 Iniciando Chess Trainer..."
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para verificar si Docker está corriendo
check_docker() {
    # Verificar si Docker está disponible
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker no está instalado${NC}"
        exit 1
    fi
    
    # Limpiar DOCKER_HOST si está configurado incorrectamente
    if [ -n "$DOCKER_HOST" ] && [ "$DOCKER_HOST" != "unix://$HOME/.docker/run/docker.sock" ]; then
        unset DOCKER_HOST
    fi
    
    # Intentar usar el contexto de Docker Desktop si está disponible
    if docker context ls 2>/dev/null | grep -q "desktop-linux"; then
        docker context use desktop-linux > /dev/null 2>&1 || true
    fi
    
    # Intentar conectar a Docker
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker no está corriendo o no se puede conectar${NC}"
        echo "💡 Por favor, inicia Docker Desktop y vuelve a intentar"
        echo "   Verifica que Docker Desktop esté completamente iniciado"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker está corriendo${NC}"
}

# Función para levantar contenedor Docker (solo motores)
start_docker_engines() {
    echo ""
    echo -e "${YELLOW}🐳 Levantando contenedor Docker para motores...${NC}"
    
    # Crear directorio para binarios si no existe
    mkdir -p ./engines-bin
    
    # Verificar si el contenedor chess-trainer ya está corriendo
    if docker ps --format '{{.Names}}' | grep -q "^chess-trainer$"; then
        echo -e "${GREEN}✅ Contenedor chess-trainer ya está corriendo${NC}"
    else
        # Verificar si existe pero está detenido
        if docker ps -a --format '{{.Names}}' | grep -q "^chess-trainer$"; then
            echo "🔄 Iniciando contenedor existente..."
            docker start chess-trainer
        else
            echo "🏗️  Construyendo e iniciando contenedor de motores..."
            docker-compose up -d --build
        fi
        
        # Esperar un momento para que el contenedor esté listo
        echo "⏳ Esperando a que el contenedor esté listo..."
        sleep 5
    fi
    
    # Preparar scripts y binarios dentro del contenedor
    echo "📦 Preparando scripts de compilación..."
    docker cp scripts/build_lc0.sh chess-trainer:/app/scripts/build_lc0.sh 2>/dev/null || true
    docker exec chess-trainer chmod +x /app/scripts/build_lc0.sh 2>/dev/null || true
    
    # Verificar y mover Lc0 si está en /app/bin/bin/lc0 (como el usuario mencionó)
    echo "🔍 Verificando binarios de motores..."
    docker exec chess-trainer sh -c "if [ -f /app/bin/bin/lc0 ]; then mv /app/bin/bin/lc0 /app/bin/lc0 && chmod +x /app/bin/lc0 && echo '✅ Binario movido'; fi" 2>/dev/null || true
    
    # Verificar que los motores estén disponibles en el contenedor
    echo "✅ Contenedor Docker listo para motores"
    docker exec chess-trainer ls -la /app/bin/ 2>/dev/null | head -5 || true
}

# Función para activar conda
activate_conda() {
    if command -v conda &> /dev/null; then
        if conda env list | grep -q "^chess "; then
            echo "🐍 Activando entorno conda 'chess'..."
            source "$(conda info --base)/etc/profile.d/conda.sh"
            conda activate chess
            echo -e "${GREEN}✅ Entorno conda 'chess' activado${NC}"
            return 0
        else
            echo -e "${RED}❌ Entorno conda 'chess' no encontrado${NC}"
            echo "💡 Crea el entorno con: conda create -n chess python=3.10"
            return 1
        fi
    else
        echo -e "${RED}❌ Conda no está instalado${NC}"
        return 1
    fi
}

# Función para iniciar backend local en conda
start_backend_local() {
    echo ""
    echo -e "${YELLOW}🔧 Iniciando backend local (conda 'chess')...${NC}"
    
    # Activar conda
    if ! activate_conda; then
        exit 1
    fi
    
    # Añadir engines-bin al PATH
    export PATH="$(pwd)/engines-bin:${PATH}"
    
    # Verificar si el puerto 8000 está libre
    if lsof -ti:8000 > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Puerto 8000 ya está en uso${NC}"
        echo "💡 El backend puede estar ya corriendo"
    else
        echo "🚀 Iniciando backend en segundo plano..."
        # Ejecutar en conda activado
        bash -c "source \"$(conda info --base)/etc/profile.d/conda.sh\" && conda activate chess && cd $(pwd) && export PATH=\"$(pwd)/engines-bin:\$PATH\" && python main.py > /tmp/chess_trainer_backend.log 2>&1" &
        BACKEND_PID=$!
        echo "📝 Backend iniciado (PID: $BACKEND_PID)"
        echo "📝 Logs: tail -f /tmp/chess_trainer_backend.log"
        
        # Esperar a que el backend responda
        echo "⏳ Esperando a que el backend esté listo..."
        sleep 3
        for i in {1..10}; do
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Backend listo${NC}"
                break
            fi
            sleep 1
        done
    fi
}

# Función para iniciar frontend en conda
start_frontend() {
    echo ""
    echo -e "${YELLOW}🎨 Iniciando frontend (conda 'chess')...${NC}"
    
    # Activar conda (aunque npm no lo necesite, el usuario quiere que esté en conda)
    if ! activate_conda; then
        exit 1
    fi
    
    cd frontend
    
    # Verificar si node_modules existe
    if [ ! -d "node_modules" ]; then
        echo "📦 Instalando dependencias del frontend..."
        npm install
    fi
    
    # Verificar si el puerto 5173 está libre
    if lsof -ti:5173 > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Puerto 5173 ya está en uso${NC}"
        echo "💡 Frontend puede estar ya corriendo"
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Frontend ya está accesible${NC}"
        fi
    else
        echo "🚀 Iniciando frontend en segundo plano..."
        # Usar el script wrapper para asegurar que persista
        nohup bash ./start_vite.sh > /tmp/chess_trainer_frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo "📝 Frontend iniciado (PID: $FRONTEND_PID)"
        echo "📝 Logs: tail -f /tmp/chess_trainer_frontend.log"
        
        # Esperar a que Vite esté listo
        echo "⏳ Esperando a que el frontend esté listo..."
        for i in {1..20}; do
            if curl -s http://localhost:5173 > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Frontend listo${NC}"
                break
            fi
            sleep 1
            if [ $((i % 3)) -eq 0 ]; then
                echo -n "."
            fi
        done
        echo ""
        
        # Verificar que el proceso sigue corriendo
        if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo -e "${RED}⚠️  El proceso del frontend se detuvo. Revisa los logs:${NC}"
            echo "   tail -20 /tmp/chess_trainer_frontend.log"
        fi
    fi
    
    cd ..
}

# Función principal
main() {
    # Verificar Docker
    check_docker
    
    # Activar conda primero
    if ! activate_conda; then
        exit 1
    fi
    
    # Levantar Docker solo para motores
    start_docker_engines
    
    # Iniciar backend local en conda
    start_backend_local
    
    # Iniciar frontend en conda
    start_frontend
    
    # Resumen
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Chess Trainer iniciado${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo "📊 Servicios:"
    echo "  🐳 Docker: Contenedor 'chess-engines' (solo motores)"
    echo "  🔧 Backend local (conda): http://localhost:8000"
    echo "  🎨 Frontend (conda): http://localhost:5173"
    echo ""
    echo "📁 Motores disponibles en: $(pwd)/engines-bin"
    echo ""
    echo "📝 Logs:"
    echo "  Backend: tail -f /tmp/chess_trainer_backend.log"
    echo "  Frontend: tail -f /tmp/chess_trainer_frontend.log"
    echo "  Docker engines: docker logs -f chess-engines"
    echo ""
    echo "🛑 Para detener: ./stop.sh"
    echo ""
}

# Ejecutar función principal
main
