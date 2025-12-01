# 🔨 Guía para Compilar y Configurar Lc0

Esta guía explica cómo compilar y configurar **Lc0 (Leela Chess Zero)** para usarlo con Chess Trainer.

---

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Contenedor `chess-trainer` en ejecución
- Redes neuronales descargadas (ver `download_weights.sh`)

---

## 🚀 Opción 1: Compilación Manual (Recomendada)

Esta es la opción más flexible y permite compilar Lc0 después de que el contenedor esté en ejecución.

### Paso 1: Copiar el script al contenedor

Si el script no está en el contenedor, cópialo:

```bash
docker cp scripts/build_lc0.sh chess-trainer:/app/scripts/build_lc0.sh
docker exec chess-trainer chmod +x /app/scripts/build_lc0.sh
```

### Paso 2: Ejecutar el script de compilación

```bash
docker exec chess-trainer /app/scripts/build_lc0.sh
```

**⏱️ Tiempo estimado**: 10-30 minutos (depende de tu CPU)

El script:
- ✅ Instala todas las dependencias necesarias
- ✅ Clona el repositorio de Lc0
- ✅ Compila el binario
- ✅ Lo instala en `/app/bin/lc0`
- ✅ Limpia archivos temporales

### Paso 3: Verificar la instalación

```bash
# Verificar que el binario existe
docker exec chess-trainer ls -lh /app/bin/lc0

# Probar que funciona
docker exec chess-trainer /app/bin/lc0 --help | head -10
```

### Paso 4: Recargar la configuración

```bash
# Desde el frontend: botón "RECARGAR CONFIG"
# O desde la línea de comandos:
curl -X POST http://localhost:8000/reload
```

---

## 🏗️ Opción 2: Compilación Automática en Dockerfile

Si prefieres que Lc0 se compile automáticamente al construir la imagen Docker:

### Paso 1: Editar el Dockerfile

Abre `Dockerfile` y busca la sección `# --- INSTALAR LC0 ---`. Descomenta las líneas que compilan Lc0:

```dockerfile
# --- INSTALAR LC0 (Leela Chess Zero) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    cmake \
    git \
    build-essential \
    libprotobuf-dev \
    protobuf-compiler \
    libopenblas-dev \
    pkg-config \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/* \
    && BUILD_DIR=/tmp/lc0-build && mkdir -p $BUILD_DIR \
    && cd $BUILD_DIR \
    && git clone --depth 1 https://github.com/LeelaChessZero/lc0.git \
    && cd lc0 && git submodule update --init --recursive \
    && mkdir build && cd build \
    && cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/app/bin \
    && make -j$(nproc) \
    && cp lc0 /app/bin/lc0 && chmod +x /app/bin/lc0 \
    && rm -rf $BUILD_DIR
```

### Paso 2: Reconstruir la imagen

```bash
docker-compose build --no-cache
docker-compose up -d
```

**⚠️ Nota**: Esto aumentará significativamente el tiempo de build (20-40 minutos).

---

## 📦 Descargar Redes Neuronales

Lc0 necesita archivos de pesos (weights) para funcionar. Descarga las redes:

```bash
# Ejecutar el script de descarga
./download_weights.sh

# O descargar manualmente:
mkdir -p weights
cd weights

# Red Lc0 (fuerte)
wget https://storage.lczero.org/files/768x15x24h-t82-swa-7464000.pb.gz -O T82-768x15x24h-swa-7464000.pb.gz

# Red Maia 1500 (estilo humano)
wget https://github.com/CSSLab/maia-chess/releases/download/v1.0/maia-1500.pb.gz
```

---

## ⚙️ Configuración en YAML

La configuración ya está lista en `config/engines_local.yaml`:

```yaml
lc0-local:
  engine_type: neuronal
  protocol: uci
  command: "lc0"
  weights: "weights/T82-768x15x24h-swa-7464000.pb.gz"
  backend: "blas"  # Para CPU. Si tienes GPU NVIDIA, usa "cuda" o "cudnn"
  search_mode: "nodes"
  default_search_value: 800000
  description: "Leela Chess Zero - Motor neuronal local"

maia-1500:
  engine_type: neuronal
  protocol: uci
  command: "lc0"
  weights: "weights/maia-1500.pb.gz"
  backend: "blas"
  search_mode: "nodes"
  default_search_value: 1
  description: "Maia Chess 1500 - Motor neuronal estilo humano (Elo 1500)"
```

---

## ✅ Verificar que Funciona

### 1. Verificar disponibilidad en el backend

```bash
curl http://localhost:8000/engines/info | python3 -m json.tool | grep -A 10 "lc0-local"
```

Deberías ver:
```json
{
  "name": "lc0-local",
  "available": true,
  "initialized": false
}
```

### 2. Probar un movimiento

```bash
curl -X POST http://localhost:8000/move \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "lc0-local",
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 3
  }' | python3 -m json.tool
```

### 3. Verificar en el frontend

1. Abre el frontend en `http://localhost:5173`
2. Ve a la página de selección
3. Verifica que `lc0-local` y `maia-1500` aparecen en la lista
4. Selecciona uno y verifica que muestra "Disponible: ✓ Sí"

---

## 🐛 Solución de Problemas

### Error: "lc0: command not found"

**Solución**: El binario no está en el PATH. Verifica:

```bash
docker exec chess-trainer ls -lh /app/bin/lc0
docker exec chess-trainer which lc0
```

Si no existe, ejecuta el script de compilación.

### Error: "Cannot find weights file"

**Solución**: Asegúrate de que los weights están en el volumen montado:

```bash
# Verificar que los archivos existen
ls -lh weights/*.pb.gz

# Verificar que están montados en el contenedor
docker exec chess-trainer ls -lh /app/weights/
```

### Error: "Backend 'blas' not available"

**Solución**: Instala OpenBLAS en el contenedor:

```bash
docker exec chess-trainer apt-get update
docker exec chess-trainer apt-get install -y libopenblas-dev
```

### Compilación falla por falta de memoria

**Solución**: Reduce el número de cores usados en la compilación:

Edita `scripts/build_lc0.sh` y cambia:
```bash
make -j"$CORES"
```
por:
```bash
make -j2  # Usar solo 2 cores
```

---

## 📚 Referencias

- **Repositorio oficial de Lc0**: https://github.com/LeelaChessZero/lc0
- **Documentación de compilación**: https://github.com/LeelaChessZero/lc0#building
- **Redes neuronales disponibles**: https://lczero.org/play/networks/
- **Maia Chess**: https://github.com/CSSLab/maia-chess

---

## 💡 Notas Adicionales

- **GPU NVIDIA**: Si tienes una GPU NVIDIA, puedes usar `backend: "cuda"` o `backend: "cudnn"` para mejor rendimiento. Necesitarás instalar CUDA en el contenedor.
- **Rendimiento**: Lc0 es más lento que Stockfish en CPU. Para mejor rendimiento, usa más `default_search_value` (más nodos).
- **Maia Chess**: Está diseñado para jugar con `default_search_value: 1` (1 nodo) para simular juego humano.

---

**¿Problemas?** Abre un issue en el repositorio o consulta los logs:

```bash
docker-compose logs chess-trainer | grep -i lc0
```

