#!/bin/bash

# Script para iniciar frontend y abrir navegador
echo "🎨 Iniciando Frontend..."

# 1. Primero detener cualquier instancia previa
echo "🧹 Limpiando procesos previos..."
if [ -f "stop_frontend.sh" ]; then
    bash stop_frontend.sh 2>/dev/null
else
    # Limpiar puerto 5173 manualmente si no existe el script
    PIDS=$(lsof -ti :5173 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "🔍 Matando procesos previos en puerto 5173..."
        kill -9 $PIDS 2>/dev/null
    fi
fi
sleep 1

# 2. Activar entorno de conda chess
echo "🐍 Activando entorno conda 'chess'..."

# Intentar diferentes ubicaciones de conda
CONDA_PATHS=(
    "$HOME/miniconda3/etc/profile.d/conda.sh"
    "$HOME/anaconda3/etc/profile.d/conda.sh"
    "$HOME/conda/etc/profile.d/conda.sh"
    "/opt/miniconda3/etc/profile.d/conda.sh"
    "/opt/anaconda3/etc/profile.d/conda.sh"
    "/usr/local/miniconda3/etc/profile.d/conda.sh"
    "/usr/local/anaconda3/etc/profile.d/conda.sh"
)

CONDA_FOUND=false
for conda_path in "${CONDA_PATHS[@]}"; do
    if [[ -f "$conda_path" ]]; then
        echo "📁 Encontrado conda en: $conda_path"
        source "$conda_path"
        CONDA_FOUND=true
        break
    fi
done

if [[ "$CONDA_FOUND" == false ]]; then
    echo "⚠️  No se encontró conda en las ubicaciones estándar"
    echo "🔄 Intentando con 'conda' directamente..."
    
    # Verificar si conda está en el PATH
    if command -v conda &> /dev/null; then
        echo "✅ Conda encontrado en PATH"
        CONDA_FOUND=true
    else
        echo "❌ Error: No se pudo encontrar conda"
        echo "💡 Instala conda o asegúrate de que esté en tu PATH"
        echo "💡 O ejecuta: export PATH=\"\$HOME/miniconda3/bin:\$PATH\""
        exit 1
    fi
fi

# Intentar activar el entorno
if [[ "$CONDA_FOUND" == true ]]; then
    echo "🔄 Activando entorno 'chess'..."
    conda activate chess 2>/dev/null || {
        echo "❌ Error: No se pudo activar el entorno 'chess'"
        echo "💡 Crear el entorno: conda create -n chess python=3.9"
        echo "💡 O verificar que existe: conda env list"
        exit 1
    }
fi

# Verificar que el entorno esté activo
if [[ "$CONDA_DEFAULT_ENV" != "chess" ]]; then
    echo "❌ Error: El entorno 'chess' no está activo"
    echo "💡 Estado actual: $CONDA_DEFAULT_ENV"
    exit 1
fi

echo "✅ Entorno conda 'chess' activado correctamente"

# 3. Cambiar al directorio frontend
cd frontend

# 4. Verificar e instalar dependencias si es necesario
if [ ! -d "node_modules" ]; then
    echo "📦 Dependencias no encontradas. Instalando..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error al instalar dependencias"
        exit 1
    fi
    echo "✅ Dependencias instaladas"
else
    echo "✓ Dependencias ya instaladas"
fi

# 5. Iniciar Vite en segundo plano
echo "🚀 Iniciando servidor Vite..."
npm run dev -- --host > ../logs_frontend.log 2>&1 &
VITE_PID=$!

# Guardar PID en archivo
echo $VITE_PID > ../.frontend.pid

echo "📦 Vite iniciado con PID: $VITE_PID"
echo "⏳ Esperando que el servidor esté listo..."

# Esperar hasta que el servidor esté listo
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "✅ Servidor listo!"
        break
    fi
    sleep 1
done

# Abrir navegador
echo "🌐 Abriendo navegador..."
open http://localhost:5173

echo ""
echo "🎉 Frontend iniciado correctamente!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 URL: http://localhost:5173"
echo "📦 PID: $VITE_PID (guardado en .frontend.pid)"
echo "📋 Logs: tail -f logs_frontend.log"
echo "🛑 Para detener: bash stop_frontend.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Mantener el script corriendo para mostrar logs
tail -f ../logs_frontend.log