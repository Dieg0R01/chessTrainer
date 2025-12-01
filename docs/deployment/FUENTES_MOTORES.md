# Guía de Fuentes para Motores de Ajedrez

Este documento lista las fuentes oficiales y confiables para descargar motores de ajedrez tradicionales y neuronales para usar con Chess Trainer.

---

## 🎯 Motores Tradicionales (Deterministas)

### 1. **Stockfish** ⭐ (Recomendado)

**Descripción**: El motor de ajedrez más fuerte del mundo, de código abierto y gratuito.

**Fuentes oficiales**:
- **GitHub Releases**: https://github.com/official-stockfish/Stockfish/releases
  - Versiones para: Linux (x64, ARM64), Windows, macOS
  - Formato: Binarios precompilados en `.zip` o `.tar.gz`
- **Sitio oficial**: https://stockfishchess.org/download/
- **Repositorio**: https://github.com/official-stockfish/Stockfish

**Instalación en Docker**: Ya incluido en el Dockerfile (descarga automática desde GitHub releases).

**Uso en YAML**:
```yaml
stockfish-local:
  engine_type: traditional
  command: "stockfish"  # O "/app/bin/stockfish" si está en el contenedor
  default_depth: 15
```

---

### 2. **Komodo / Dragon**

**Descripción**: Motor comercial muy fuerte, ahora parte de ChessBase.

**Fuentes**:
- **Sitio oficial**: https://komodochess.com/
- **ChessBase**: https://shop.chessbase.com/en/products/komodo_chess_engine

**Nota**: Requiere licencia comercial. No incluido en Dockerfile por defecto.

---

### 3. **Ethereal**

**Descripción**: Motor de código abierto, muy fuerte y activo.

**Fuentes**:
- **GitHub**: https://github.com/AndyGrant/Ethereal/releases
- **Sitio**: https://www.chessengeria.org/

---

### 4. **Berserk**

**Descripción**: Fork de Stockfish con mejoras experimentales.

**Fuentes**:
- **GitHub**: https://github.com/jhonnold/berserk/releases

---

## 🧠 Motores Neuronales

### 1. **Leela Chess Zero (Lc0)** ⭐ (Recomendado)

**Descripción**: Motor neuronal de código abierto inspirado en AlphaZero. El más popular y mantenido.

**Fuentes oficiales**:
- **GitHub Releases**: https://github.com/LeelaChessZero/lc0/releases
  - Versiones: Linux (x64, ARM64, CUDA), Windows, macOS
  - Formato: Binarios precompilados
- **Sitio oficial**: https://lczero.org/
- **Repositorio**: https://github.com/LeelaChessZero/lc0

**Instalación en Docker**: Ya incluido en el Dockerfile (descarga automática desde GitHub releases).

**Redes (Weights)**:
- **Redes oficiales**: https://lczero.org/play/networks/bestnets/
  - Formatos: `.pb.gz`, `.onnx`
  - Recomendadas: `T80-3010`, `J94-100`, `T79-3010`
- **Descarga directa**: https://lczero.org/networks/

**Uso en YAML**:
```yaml
lc0-local:
  engine_type: neuronal
  protocol: uci
  command: "lc0"  # O "/app/bin/lc0"
  weights: "weights/T80-3010.pb.gz"
  backend: "blas"  # En Docker sin GPU: "blas". Con GPU: "cuda" o "cudnn"
  search_mode: "nodes"
  default_search_value: 800000
```

---

### 2. **Maia Chess** ⭐ (Ideal para entrenamiento)

**Descripción**: Redes neuronales entrenadas para jugar como humanos en diferentes niveles de Elo (1100, 1500, 1900). Perfecto para Chess Trainer.

**Fuentes**:
- **GitHub**: https://github.com/CSSLab/maia-chess
- **Descarga de redes**: https://github.com/CSSLab/maia-chess#downloading-weights
  - Formatos: `.pb.gz`
  - Niveles disponibles: 1100, 1500, 1900 Elo

**Uso**: Usa el mismo binario de Lc0 pero con redes diferentes.

**Uso en YAML**:
```yaml
maia-1500:
  engine_type: neuronal
  protocol: uci
  command: "lc0"  # Mismo binario que Lc0
  weights: "weights/maia-1500.pb.gz"
  backend: "blas"
  search_mode: "nodes"
  default_search_value: 1  # Maia está diseñado para jugar con 1 nodo
```

---

### 3. **Fat Fritz / Fat Fritz 2**

**Descripción**: Motor neuronal comercial basado en Lc0 con redes optimizadas.

**Fuentes**:
- **ChessBase**: https://shop.chessbase.com/en/products/fat_fritz_2
- **Nota**: Requiere licencia comercial.

---

### 4. **Allie Chess Engine**

**Descripción**: Motor neuronal de código abierto, más ligero que Lc0.

**Fuentes**:
- **GitHub**: https://github.com/DanielUranga/AllieChessEngine/releases

---

## 📦 Instalación Manual de Redes Neuronales

### Para usar con Docker:

1. **Descargar redes**:
   ```bash
   mkdir -p weights
   cd weights
   
   # Ejemplo: Descargar red de Lc0
   wget https://lczero.org/networks/weights/T80-3010.pb.gz
   
   # Ejemplo: Descargar red de Maia
   wget https://github.com/CSSLab/maia-chess/releases/download/v1.0/maia-1500.pb.gz
   ```

2. **Montar en docker-compose.yml**:
   ```yaml
   volumes:
     - ./weights:/app/weights:rw
   ```

3. **Actualizar `engines_local.yaml`** con las rutas correctas.

---

## 🔧 Backends para Motores Neuronales

### En Docker (sin GPU):
- **`blas`**: Usa CPU con optimizaciones BLAS. Funciona en cualquier contenedor.
- **`opencl`**: Requiere drivers OpenCL (puede no estar disponible en contenedores).

### En Docker (con GPU):
- **`cuda`**: Para NVIDIA GPUs (requiere `nvidia-docker`).
- **`cudnn`**: Versión optimizada de CUDA con cuDNN.

### En macOS nativo:
- **`metal`**: Para Apple Silicon (M1/M2/M3). No disponible en Docker Linux.

---

## 📝 Notas Importantes

1. **Licencias**:
   - Stockfish y Lc0 son de código abierto (GPL).
   - Maia es de código abierto.
   - Komodo/Dragon requieren licencia comercial.

2. **Rendimiento**:
   - En Docker sin GPU, los motores neuronales serán más lentos (usarán CPU).
   - Para mejor rendimiento, considera usar GPU o ejecutar nativamente.

3. **Compatibilidad**:
   - Los binarios en el Dockerfile son para Linux x64.
   - Si necesitas ARM64 o macOS, ajusta las URLs de descarga en el Dockerfile.

4. **Actualización**:
   - Los motores se actualizan frecuentemente. Revisa los releases de GitHub periódicamente.

---

## 🔗 Enlaces Útiles

- **Lista completa de motores UCI**: https://www.chessengeria.org/
- **Comparación de fuerza de motores**: https://ccrl.chessdom.com/ccrl/4040/
- **Documentación de Lc0**: https://lczero.org/play/quickstart/
- **Documentación de Stockfish**: https://stockfishchess.org/get-involved/

