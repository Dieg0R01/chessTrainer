#!/bin/bash
# Script para descargar redes neuronales para motores de ajedrez
# Uso: ./download_weights.sh

set -e

WEIGHTS_DIR="./weights"
mkdir -p "$WEIGHTS_DIR"

echo "📦 Descargando redes neuronales para motores de ajedrez..."
echo ""

# Función para descargar con barra de progreso
download_file() {
    local url=$1
    local filename=$2
    local description=$3
    
    echo "⬇️  Descargando: $description"
    echo "   URL: $url"
    
    if command -v wget &> /dev/null; then
        wget -q --show-progress -O "$WEIGHTS_DIR/$filename" "$url" || {
            echo "❌ Error descargando $filename"
            return 1
        }
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$WEIGHTS_DIR/$filename" "$url" || {
            echo "❌ Error descargando $filename"
            return 1
        }
    else
        echo "❌ Error: Necesitas wget o curl instalado"
        return 1
    fi
    
    echo "✅ Descargado: $filename"
    echo ""
}

# ============================================================================
# REDES DE LC0 (Leela Chess Zero)
# ============================================================================

echo "🧠 Redes de Leela Chess Zero (Lc0):"
echo ""

# Red T82-768x15x24h (muy fuerte, recomendada - alternativa a T80-3010)
# Nota: T80-3010 ya no está disponible, esta es una red equivalente muy fuerte
download_file \
    "https://storage.lczero.org/files/768x15x24h-t82-swa-7464000.pb.gz" \
    "T82-768x15x24h-swa-7464000.pb.gz" \
    "Lc0 T82-768x15x24h (Red muy fuerte)"

# ============================================================================
# REDES DE MAIA CHESS (Estilo humano)
# ============================================================================

echo "👤 Redes de Maia Chess (Estilo humano):"
echo ""

# Maia 1500 Elo (intermedio)
download_file \
    "https://github.com/CSSLab/maia-chess/releases/download/v1.0/maia-1500.pb.gz" \
    "maia-1500.pb.gz" \
    "Maia Chess 1500 Elo (Nivel intermedio)"

# ============================================================================
# RESUMEN
# ============================================================================

echo "✅ Descarga completada!"
echo ""
echo "📁 Archivos descargados en: $WEIGHTS_DIR"
echo ""
echo "📋 Archivos disponibles:"
ls -lh "$WEIGHTS_DIR"/*.pb.gz 2>/dev/null || echo "   (ningún archivo .pb.gz encontrado)"
echo ""
echo "💡 Próximos pasos:"
echo "   ✅ Configuración YAML ya está lista (stockfish-local, lc0-local, maia-1500)"
echo "   ✅ Si usas Docker: los archivos deben estar en ./weights/ (se monta como volumen)"
echo "   ✅ Reinicia el backend o usa POST /reload para recargar la configuración"
echo ""
echo "📚 Ver docs/deployment/FUENTES_MOTORES.md para más información"

