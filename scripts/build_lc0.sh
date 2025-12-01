#!/bin/bash
# Script para compilar Lc0 dentro del contenedor Docker
# Uso: docker exec chess-trainer /app/scripts/build_lc0.sh

set -e

echo "🔨 Compilando Lc0 (Leela Chess Zero)..."
echo ""

# Directorio de trabajo
BUILD_DIR="/tmp/lc0-build"
LC0_DIR="$BUILD_DIR/lc0"
INSTALL_DIR="/app/bin"

# Limpiar si existe
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Instalar dependencias si no están instaladas
echo "📦 Instalando dependencias..."
apt-get update -qq
apt-get install -y -qq \
    meson \
    ninja-build \
    git \
    build-essential \
    libprotobuf-dev \
    protobuf-compiler \
    libopenblas-dev \
    pkg-config \
    zlib1g-dev \
    > /dev/null 2>&1

# Clonar repositorio
echo "📥 Clonando repositorio de Lc0..."
cd "$BUILD_DIR"
if [ ! -d "lc0" ]; then
    git clone --depth 1 https://github.com/LeelaChessZero/lc0.git
fi
cd "$LC0_DIR"

# Inicializar submódulos
echo "📦 Inicializando submódulos..."
git submodule update --init --recursive

# Verificar que meson.build existe
if [ ! -f "meson.build" ]; then
    echo "❌ Error: No se encontró meson.build en $LC0_DIR"
    echo "📁 Contenido del directorio:"
    ls -la | head -20
    exit 1
fi

# Crear directorio de build
echo "📁 Configurando con Meson..."
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    # ARM64: usar backend blas
    BACKEND="blas"
else
    # x86_64
    BACKEND="blas"
fi

# Configurar con Meson
meson setup build \
    --buildtype=release \
    --prefix="$INSTALL_DIR" \
    -Dbackend="$BACKEND" \
    || (echo "⚠️  Error en configuración inicial. Intentando sin especificar backend..." && \
        meson setup build --buildtype=release --prefix="$INSTALL_DIR")

cd build

# Compilar (usar todos los cores disponibles)
echo "🔨 Compilando (esto puede tardar varios minutos)..."
CORES=$(nproc)
ninja -j"$CORES"

# Instalar
echo "📦 Instalando binario..."
ninja install

# Meson instala en $INSTALL_DIR/bin, mover a $INSTALL_DIR
if [ -f "$INSTALL_DIR/bin/lc0" ]; then
    echo "📦 Moviendo binario de $INSTALL_DIR/bin a $INSTALL_DIR..."
    mv "$INSTALL_DIR/bin/lc0" "$INSTALL_DIR/lc0"
    chmod +x "$INSTALL_DIR/lc0"
elif [ -f "$INSTALL_DIR/lc0" ]; then
    echo "✅ Binario ya está en la ubicación correcta"
    chmod +x "$INSTALL_DIR/lc0"
else
    echo "⚠️  Buscando binario compilado..."
    find . -name "lc0" -type f -executable | head -1 | while read bin_path; do
        echo "📦 Copiando binario desde $bin_path..."
        cp "$bin_path" "$INSTALL_DIR/lc0"
        chmod +x "$INSTALL_DIR/lc0"
    done
fi

# Verificar instalación
if [ -f "$INSTALL_DIR/lc0" ]; then
    echo ""
    echo "✅ Lc0 compilado e instalado correctamente en $INSTALL_DIR/lc0"
    echo "📊 Información del binario:"
    "$INSTALL_DIR/lc0" --help | head -5 || echo "   (no se pudo ejecutar --help, pero el binario existe)"
    echo ""
    echo "💡 Próximos pasos:"
    echo "   1. Asegúrate de tener los weights descargados en /app/weights/"
    echo "   2. Recarga la configuración con: POST /reload"
    echo "   3. Verifica disponibilidad en el frontend"
else
    echo "❌ Error: No se encontró el binario después de la compilación"
    exit 1
fi

# Limpiar
echo "🧹 Limpiando archivos temporales..."
rm -rf "$BUILD_DIR"

echo ""
echo "✅ Proceso completado!"

