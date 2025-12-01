# Multi-stage build para Chess Trainer con motores incluidos
# Usar plataforma específica para evitar problemas de arquitectura
# ARG BUILDPLATFORM
# ARG TARGETPLATFORM

# ============================================================================
# ETAPA 1: Backend Builder
# ============================================================================
FROM python:3.10-slim AS backend-builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar/instalar motores
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    curl \
    git \
    cmake \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend completo
COPY main.py engine_manager.py config.py ./
COPY engines/ ./engines/
COPY config/ ./config/

# ============================================================================
# ETAPA 2: Instalación de Motores de Ajedrez
# ============================================================================
FROM python:3.10-slim AS engines-installer

WORKDIR /app

# Instalar dependencias del sistema para motores
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Crear directorios para motores y pesos
RUN mkdir -p /app/bin /app/weights

# --- INSTALAR STOCKFISH ---
# Descargar Stockfish desde GitHub releases (versión más reciente)
# Detectar arquitectura y descargar el binario correcto
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then \
        echo "Descargando Stockfish para ARM64..." && \
        (wget --progress=bar:force https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-android-armv8.tar -O /tmp/stockfish.tar || \
         wget --progress=bar:force https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64.tar -O /tmp/stockfish.tar); \
    else \
        echo "Descargando Stockfish para x86-64..." && \
        (wget --progress=bar:force https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar -O /tmp/stockfish.tar || \
         wget --progress=bar:force https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64.tar -O /tmp/stockfish.tar); \
    fi && \
    tar -xf /tmp/stockfish.tar -C /tmp/ && \
    find /tmp -name "stockfish*" -type f -executable -exec mv {} /app/bin/stockfish \; && \
    chmod +x /app/bin/stockfish && \
    rm -rf /tmp/stockfish* && \
    test -f /app/bin/stockfish && test -s /app/bin/stockfish || (echo "ERROR: Stockfish no se instaló correctamente" && exit 1)

# --- INSTALAR LC0 (Leela Chess Zero) ---
# NOTA: Lc0 debe compilarse desde el código fuente.
# Opción 1: Compilar automáticamente durante el build (descomenta las líneas siguientes)
# Opción 2: Compilar manualmente después con el script build_lc0.sh
#
# Para compilar automáticamente, descomenta estas líneas:
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     cmake \
#     git \
#     build-essential \
#     libprotobuf-dev \
#     protobuf-compiler \
#     libopenblas-dev \
#     pkg-config \
#     zlib1g-dev \
#     && rm -rf /var/lib/apt/lists/* \
#     && BUILD_DIR=/tmp/lc0-build && mkdir -p $BUILD_DIR \
#     && cd $BUILD_DIR \
#     && git clone --depth 1 https://github.com/LeelaChessZero/lc0.git \
#     && cd lc0 && git submodule update --init --recursive \
#     && mkdir build && cd build \
#     && cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/app/bin \
#     && make -j$(nproc) \
#     && cp lc0 /app/bin/lc0 && chmod +x /app/bin/lc0 \
#     && rm -rf $BUILD_DIR
#
# Por ahora, solo copiamos el script de compilación manual:
COPY scripts/build_lc0.sh /app/scripts/build_lc0.sh
RUN chmod +x /app/scripts/build_lc0.sh

# Añadir /app/bin al PATH
ENV PATH="/app/bin:${PATH}"

# ============================================================================
# ETAPA 3: Frontend Builder
# ============================================================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copiar y instalar dependencias de Node.js
COPY frontend/package*.json ./
RUN npm install

# Copiar el código del frontend y construirlo
COPY frontend/ ./
RUN npm run build

# ============================================================================
# ETAPA FINAL: Imagen de Producción
# ============================================================================
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias mínimas del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar las dependencias de Python de la etapa backend-builder
COPY --from=backend-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=backend-builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copiar el código del backend completo
COPY --from=backend-builder /app/main.py /app/engine_manager.py /app/config.py ./
COPY --from=backend-builder /app/engines/ ./engines/
COPY --from=backend-builder /app/config/ ./config/
# Copiar scripts (incluye build_lc0.sh)
RUN mkdir -p ./scripts
COPY --from=engines-installer /app/scripts/build_lc0.sh ./scripts/build_lc0.sh

# Copiar los motores instalados
COPY --from=engines-installer /app/bin/ /app/bin/
COPY --from=engines-installer /app/weights/ /app/weights/

# Copiar los archivos estáticos del frontend
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Añadir /app/bin al PATH para que los motores sean accesibles
ENV PATH="/app/bin:${PATH}"

# Variables de entorno por defecto
ENV ENVIRONMENT=production
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Exponer el puerto que usará FastAPI
EXPOSE 8000

# Health check para verificar que el servicio está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
