#!/bin/bash

# Script para detener el frontend y limpiar todos los procesos relacionados
echo "🛑 Deteniendo Frontend..."

# Función para matar procesos de forma segura
kill_process_by_port() {
    local port=$1
    local pids=$(lsof -ti :$port 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "🔍 Encontrados procesos en puerto $port: $pids"
        for pid in $pids; do
            echo "   ⚔️  Matando proceso $pid..."
            kill -9 $pid 2>/dev/null
        done
        echo "✅ Puerto $port liberado"
    else
        echo "✓ Puerto $port ya está libre"
    fi
}

# Función para matar procesos por nombre
kill_process_by_name() {
    local process_name=$1
    local pids=$(pgrep -f "$process_name" 2>/dev/null)
    
    if [ -n "$pids" ]; then
        echo "🔍 Encontrados procesos '$process_name': $pids"
        for pid in $pids; do
            # Verificar que el proceso está relacionado con el proyecto
            if ps -p $pid -o command= 2>/dev/null | grep -q "chessTrainer"; then
                echo "   ⚔️  Matando proceso $pid..."
                kill -9 $pid 2>/dev/null
            fi
        done
    fi
}

# 1. Matar procesos en puerto 5173 (Vite frontend)
kill_process_by_port 5173

# 2. Intentar matar proceso usando el archivo PID
if [ -f ".frontend.pid" ]; then
    PID=$(cat .frontend.pid)
    if [ -n "$PID" ]; then
        if ps -p $PID > /dev/null 2>&1; then
            echo "🔍 Encontrado proceso guardado con PID: $PID"
            echo "   ⚔️  Matando proceso $PID y sus hijos..."
            # Matar el proceso y todos sus hijos
            pkill -P $PID 2>/dev/null
            kill -9 $PID 2>/dev/null
        fi
    fi
fi

# 3. Matar procesos específicos de Vite en el proyecto
echo "🔍 Buscando procesos de Vite relacionados con el proyecto..."
kill_process_by_name "vite.*chessTrainer"

# 4. Matar procesos de npm run dev en el proyecto
echo "🔍 Buscando procesos de npm relacionados con el proyecto..."
kill_process_by_name "npm.*dev.*chessTrainer"

# 5. Limpiar archivo de logs
if [ -f "logs_frontend.log" ]; then
    echo "🧹 Limpiando logs antiguos..."
    > logs_frontend.log
fi

# 6. Limpiar archivo de PID si existe
if [ -f ".frontend.pid" ]; then
    echo "🧹 Eliminando archivo de PID..."
    rm -f .frontend.pid
fi

# Verificar que el puerto esté libre
sleep 1
if lsof -i :5173 >/dev/null 2>&1; then
    echo "⚠️  Advertencia: El puerto 5173 todavía está en uso"
    echo "   Puede que necesites reiniciar o matar manualmente: kill -9 \$(lsof -ti :5173)"
else
    echo "✅ Puerto 5173 completamente libre"
fi

echo ""
echo "🎉 Frontend detenido correctamente!"
echo ""

