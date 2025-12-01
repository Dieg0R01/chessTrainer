#!/bin/bash
# Script para detener Chess Trainer completo
# Detiene Docker, backend y frontend

set -e

echo "🛑 Deteniendo Chess Trainer..."
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Detener frontend
echo -e "${YELLOW}🎨 Deteniendo frontend...${NC}"
if lsof -ti:5173 > /dev/null 2>&1; then
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}✅ Frontend detenido${NC}"
else
    echo "   Frontend no estaba corriendo"
fi

# Detener backend local (si está corriendo fuera de Docker)
echo -e "${YELLOW}🔧 Deteniendo backend local...${NC}"
if lsof -ti:8000 > /dev/null 2>&1; then
    # Verificar si es Docker o proceso local
    if docker ps --format '{{.Names}}' | grep -q "^chess-trainer$"; then
        echo "   Backend está en Docker, se detendrá con Docker"
    else
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✅ Backend local detenido${NC}"
    fi
else
    echo "   Backend local no estaba corriendo"
fi

# Detener Docker
echo -e "${YELLOW}🐳 Deteniendo contenedores Docker...${NC}"
if docker ps --format '{{.Names}}' | grep -q "^chess-engines$"; then
    docker stop chess-engines
    echo -e "${GREEN}✅ Contenedor Docker (motores) detenido${NC}"
elif docker ps --format '{{.Names}}' | grep -q "^chess-trainer$"; then
    docker stop chess-trainer
    echo -e "${GREEN}✅ Contenedor Docker detenido${NC}"
else
    echo "   Contenedor Docker no estaba corriendo"
fi

# Detener también con docker-compose si existe
if [ -f "docker-compose.engines.yml" ]; then
    docker-compose -f docker-compose.engines.yml down 2>/dev/null || true
fi
if [ -f "docker-compose.yml" ]; then
    docker-compose down 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}✅ Todo detenido${NC}"
echo ""
