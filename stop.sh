#!/bin/bash

# Script para detener Chess Trainer
# Uso: ./stop.sh

echo "🛑 Deteniendo Chess Trainer..."
echo ""

# Detener backend
echo "📦 Deteniendo Backend..."
pkill -f "uvicorn main:app"
if [ $? -eq 0 ]; then
    echo "   ✅ Backend detenido"
else
    echo "   ⚠️  Backend no estaba corriendo o ya fue detenido"
fi

# Detener frontend
echo "🎨 Deteniendo Frontend..."
pkill -f "vite"
if [ $? -eq 0 ]; then
    echo "   ✅ Frontend detenido"
else
    echo "   ⚠️  Frontend no estaba corriendo o ya fue detenido"
fi

echo ""
echo "✅ Chess Trainer detenido completamente"
echo ""

# Verificar que no haya procesos corriendo
REMAINING=$(ps aux | grep -E "(uvicorn main:app|vite)" | grep -v grep | wc -l)
if [ $REMAINING -gt 0 ]; then
    echo "⚠️  Advertencia: Aún hay $REMAINING proceso(s) relacionado(s) corriendo"
    echo "   Puedes intentar: killall -9 python3 node"
else
    echo "🎉 Todos los procesos detenidos correctamente"
fi


