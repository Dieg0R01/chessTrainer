# 🚀 Guía de Despliegue Completo - Chess Trainer

Esta guía documenta el despliegue completo del sistema Chess Trainer en su estado actual (v3.0.0).

---

## 📋 Arquitectura del Sistema

El sistema utiliza una arquitectura híbrida:

- **🐳 Docker**: Contenedor `chess-engines` que proporciona los binarios de los motores (Stockfish, Lc0, Maia)
  - LC0 se compila automáticamente durante el build del Docker
  - Contenedor solo para motores, no ejecuta el backend
- **🐍 Backend Local**: FastAPI ejecutándose en conda `chess` (puerto 8000)
- **🎨 Frontend Local**: React + Vite ejecutándose en conda `chess` (puerto 5173)

### Puertos Utilizados

- **8000**: Backend FastAPI (local, conda)
- **8001**: Docker container (solo para motores, no se usa directamente)
- **5173**: Frontend Vite (local, conda)

---

## 📦 Requisitos Previos

### Software Necesario

1. **Docker Desktop** (o Docker Engine)
   - Verificar instalación: `docker --version`
   - Verificar que está corriendo: `docker info`

2. **Conda** (Miniconda o Anaconda)
   - Verificar instalación: `conda --version`
   - Entorno `chess` con Python 3.10+

3. **Node.js 18+** y **npm**
   - Verificar: `node --version` y `npm --version`

### Estructura de Directorios

```
chessTrainer/
├── config/
│   ├── engines_local.yaml      # Configuración de motores locales
│   └── engines_external.yaml  # Configuración de motores externos
├── weights/                    # Redes neuronales (montado en Docker)
├── scripts/
│   └── build_lc0.sh           # Script para compilar Lc0 (ejecutado automáticamente en build)
├── docker-compose.engines.yml  # Configuración Docker para motores
├── Dockerfile.engines          # Imagen Docker para motores (compila LC0 automáticamente)
├── start.sh                   # Script de inicio automatizado
└── stop.sh                    # Script de detención
```

---

## 🚀 Inicio Rápido (Recomendado)

### Opción 1: Script Automatizado

```bash
# Dar permisos de ejecución (solo la primera vez)
chmod +x start.sh stop.sh

# Iniciar todo el sistema
./start.sh

# El script:
# 1. Verifica Docker y levanta el contenedor chess-engines
# 2. Activa conda 'chess'
# 3. Inicia el backend en puerto 8000
# 4. Inicia el frontend en puerto 5173
```

### Detener el Sistema

```bash
./stop.sh
```

---

## 🔧 Configuración Paso a Paso

### 1. Preparar Entorno Conda

```bash
# Crear entorno conda si no existe
conda create -n chess python=3.10 -y
conda activate chess

# Instalar dependencias del backend
pip install -r requirements.txt
```

### 2. Configurar Docker

#### Construir la Imagen Docker

```bash
# Construir la imagen (incluye Stockfish y compila LC0 automáticamente)
docker-compose -f docker-compose.engines.yml build

# Esto puede tardar 10-30 minutos la primera vez debido a la compilación de LC0
# Las siguientes veces será más rápido gracias al cache de Docker
```

**Nota**: LC0 se compila automáticamente durante el build del Docker. No es necesario compilarlo manualmente.

#### Iniciar el Contenedor

```bash
# Iniciar contenedor (solo para motores)
docker-compose -f docker-compose.engines.yml up -d

# Verificar que está corriendo
docker ps | grep chess-engines
```

#### Verificar Motores en el Contenedor

```bash
# Verificar que los binarios están disponibles
docker exec chess-engines ls -la /app/bin/

# Deberías ver:
# - stockfish
# - lc0 (compilado automáticamente durante el build)

# Probar LC0
docker exec chess-engines /app/bin/lc0 --help
```

### 4. Descargar Redes Neuronales

```bash
# Crear directorio de pesos
mkdir -p weights

# Descargar pesos (script automatizado)
chmod +x download_weights.sh
./download_weights.sh

# O manualmente:
cd weights
wget https://storage.lczero.org/files/768x15x24h-t82-swa-7464000.pb.gz
wget https://github.com/CSSLab/maia-chess/releases/download/v1.0/maia-1500.pb.gz
cd ..
```

**Nota**: Los pesos se montan automáticamente en Docker como volumen.

### 5. Configurar Motores en YAML

El archivo `config/engines_local.yaml` ya está configurado para usar Docker:

```yaml
stockfish-local:
  command: "docker exec -i chess-engines stockfish"
  
lc0-local:
  command: "docker exec -i chess-engines /app/bin/lc0"
  weights: "weights/T82-768x15x24h-swa-7464000.pb.gz"
  
maia-1500:
  command: "docker exec -i chess-engines /app/bin/lc0"
  weights: "weights/maia-1500.pb.gz"
```

**Importante**: 
- El nombre del contenedor es `chess-engines` (no `chess-trainer`)
- El flag `-i` es necesario para mantener stdin interactivo
- Los pesos se resuelven desde `/app/weights/` dentro del contenedor

**Importante**: El flag `-i` es necesario para mantener stdin interactivo.

### 6. Iniciar Backend Local

```bash
# Activar conda
conda activate chess

# Iniciar backend
python main.py

# O con uvicorn directamente:
uvicorn main:app --reload --port 8000
```

El backend estará disponible en: **http://localhost:8000**

### 7. Iniciar Frontend Local

```bash
# En otra terminal, activar conda
conda activate chess

# Ir al directorio del frontend
cd frontend

# Instalar dependencias (solo la primera vez)
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en: **http://localhost:5173**

---

## 🔍 Verificación del Sistema

### Verificar Docker

```bash
# Verificar contenedor corriendo
docker ps | grep chess-engines

# Verificar binarios en el contenedor
docker exec chess-engines ls -la /app/bin/

# Deberías ver:
# - stockfish
# - lc0 (compilado automáticamente durante el build)

# Probar Stockfish
docker exec chess-engines /app/bin/stockfish --version

# Probar LC0
docker exec chess-engines /app/bin/lc0 --help
```

### Verificar Backend

```bash
# Health check
curl http://localhost:8000/health

# Listar motores disponibles
curl http://localhost:8000/engines/info | python3 -m json.tool

# Verificar disponibilidad de motores
curl -s http://localhost:8000/engines/info | python3 -c "
import sys, json
data = json.load(sys.stdin)
engines = data.get('engines', [])
avail = sum(1 for e in engines if e.get('available'))
print(f'Disponibles: {avail}/{len(engines)}')
for e in engines:
    status = '🟢' if e.get('available') else '🔴'
    print(f'{status} {e[\"name\"]}')
"
```

### Verificar Frontend

```bash
# Verificar que responde
curl http://localhost:5173

# Abrir en navegador
open http://localhost:5173  # macOS
# o
xdg-open http://localhost:5173  # Linux
```

---

## 🐛 Solución de Problemas

### Docker no inicia

```bash
# Verificar que Docker Desktop está corriendo
docker info

# Si falla, reiniciar Docker Desktop
# Luego verificar contexto
docker context ls
docker context use desktop-linux  # Si estás en macOS
```

### Contenedor no encuentra binarios

```bash
# Verificar que Stockfish está instalado
docker exec chess-engines /app/bin/stockfish --version

# Verificar que LC0 está compilado (debería estar si el build fue exitoso)
docker exec chess-engines ls -la /app/bin/lc0

# Si LC0 no existe, reconstruir la imagen:
docker-compose -f docker-compose.engines.yml build --no-cache
docker-compose -f docker-compose.engines.yml up -d
```

### Motores no aparecen como disponibles

1. **Verificar contenedor corriendo**:
   ```bash
   docker ps | grep chess-engines
   ```

2. **Verificar configuración YAML**:
   ```bash
   # El comando debe incluir "docker exec -i" y usar "chess-engines"
   grep "command:" config/engines_local.yaml
   # Debe mostrar: "docker exec -i chess-engines ..."
   ```

3. **Recargar configuración**:
   ```bash
   curl -X POST http://localhost:8000/reload
   ```

4. **Revisar logs del backend**:
   ```bash
   tail -f /tmp/chess_trainer_backend.log
   # Buscar errores de disponibilidad
   ```

### Backend no inicia

```bash
# Verificar entorno conda
conda activate chess
which python
python --version  # Debe ser 3.10+

# Verificar dependencias
pip list | grep fastapi
pip list | grep uvicorn

# Si faltan, instalar
pip install -r requirements.txt
```

### Frontend no inicia

```bash
# Verificar Node.js
node --version  # Debe ser 18+

# Reinstalar dependencias
cd frontend
rm -rf node_modules package-lock.json
npm install

# Verificar puerto 5173 libre
lsof -ti:5173
# Si está ocupado, matar proceso:
pkill -f "vite"
```

### Error CORS

El backend está configurado para permitir `localhost:5173` incluso en producción. Si persiste:

1. Verificar que el backend está en puerto 8000
2. Verificar que el frontend está en puerto 5173
3. Revisar `main.py` - función `get_cors_origins()`

### Lc0 no responde o da timeout

1. **Verificar que Lc0 está compilado**:
   ```bash
   docker exec chess-engines /app/bin/lc0 --help
   ```

2. **Verificar que los pesos están disponibles**:
   ```bash
   docker exec chess-engines ls -la /app/weights/
   # Debe mostrar los archivos .pb.gz
   ```

3. **Probar Lc0 directamente**:
   ```bash
   docker exec -i chess-engines /app/bin/lc0 <<< "uci"
   # Debe responder con información UCI
   ```

4. **Verificar librerías de runtime**:
   ```bash
   # Si da error de librerías faltantes, reconstruir la imagen
   docker-compose -f docker-compose.engines.yml build
   ```

4. **Revisar logs del backend**:
   ```bash
   tail -100 /tmp/chess_trainer_backend.log | grep -i "lc0\|uciok\|error"
   ```

---

## 📝 Notas Importantes

### Arquitectura Híbrida

- **Docker solo para motores**: El contenedor `chess-engines` solo proporciona los binarios de los motores (Stockfish, Lc0, Maia). No ejecuta el backend.
  - **Compilación automática**: LC0 se compila automáticamente durante el build del Docker usando `Dockerfile.engines`
  - **Librerías incluidas**: La imagen final incluye todas las librerías de runtime necesarias (libopenblas, libprotobuf)
- **Backend y Frontend locales**: Ambos se ejecutan en el entorno conda `chess` para facilitar el desarrollo y debugging.
- **Comunicación**: El backend se comunica con los motores mediante `docker exec -i`, ejecutando comandos dentro del contenedor.

### Puertos

- **8000**: Backend local (conda)
- **8001**: Docker container (no se usa directamente, solo para evitar conflictos)
- **5173**: Frontend local (conda)

### Persistencia de Datos

- **Configuración**: `config/` se monta como volumen de solo lectura en Docker
- **Pesos**: `weights/` se monta como volumen de lectura/escritura en Docker
- **Logs**: Los logs del backend se guardan en `/tmp/chess_trainer_backend.log`

### Recarga de Configuración

Después de modificar `config/engines_local.yaml`:

```bash
# Opción 1: Recargar sin reiniciar
curl -X POST http://localhost:8000/reload

# Opción 2: Reiniciar backend
pkill -f "python.*main.py"
conda activate chess
python main.py
```

---

## 🔄 Flujo de Inicio Completo

1. **Docker**: 
   ```bash
   docker-compose -f docker-compose.engines.yml build  # Primera vez o si cambias algo
   docker-compose -f docker-compose.engines.yml up -d  # Iniciar contenedor chess-engines
   ```
   - Contenedor `chess-engines` corriendo
   - LC0 compilado automáticamente durante el build

2. **Backend**: 
   ```bash
   conda activate chess
   python main.py
   ```
   - API en puerto 8000
   - Verifica disponibilidad de motores al iniciar

3. **Frontend**: 
   ```bash
   conda activate chess
   cd frontend
   npm run dev
   ```
   - UI en puerto 5173

4. **Verificación**: Backend verifica disponibilidad de motores al iniciar
5. **Uso**: Frontend se conecta al backend, backend ejecuta motores vía `docker exec -i chess-engines`

---

## 📚 Documentación Adicional

- **`docs/deployment/DOCKER_SETUP.md`**: Detalles sobre Docker
- **`docs/deployment/COMPILAR_LC0.md`**: Guía detallada para compilar Lc0
- **`docs/deployment/FUENTES_MOTORES.md`**: Fuentes de descarga de motores y redes
- **`docs/changelog/CAMBIOS_v3.0.0.md`**: Cambios completos de la versión 3.0.0

---

## ✅ Checklist de Despliegue

- [ ] Docker Desktop instalado y corriendo
- [ ] Conda instalado con entorno `chess` creado
- [ ] Node.js 18+ instalado
- [ ] Contenedor Docker construido (`docker-compose -f docker-compose.engines.yml build`)
- [ ] Contenedor Docker corriendo (`docker ps | grep chess-engines`)
- [ ] LC0 compilado automáticamente durante el build (verificar con `docker exec chess-engines ls -la /app/bin/lc0`)
- [ ] Pesos de redes neuronales descargados en `weights/`
- [ ] Backend iniciado en puerto 8000 (conda `chess`)
- [ ] Frontend iniciado en puerto 5173 (conda `chess`)
- [ ] Health check del backend responde (`curl http://localhost:8000/health`)
- [ ] Frontend accesible (`curl http://localhost:5173`)
- [ ] Motores aparecen como disponibles en `/engines/info` (debe mostrar `available: true` para lc0-local y maia-1500)

---

**Última actualización**: Diciembre 2024 (v3.0.0)

---

## 🎯 Inicio Rápido con VS Code

Si usas VS Code, puedes usar las tasks predefinidas:

1. **Abrir VS Code** en el directorio del proyecto
2. **Presionar `Cmd+Shift+P`** (macOS) o `Ctrl+Shift+P` (Linux/Windows)
3. **Escribir "Tasks: Run Task"**
4. **Seleccionar "🚀 Iniciar Chess Trainer Completo"**

Esto iniciará automáticamente:
- Contenedor Docker `chess-engines`
- Backend en conda `chess`
- Frontend en conda `chess`

Ver `.vscode/tasks.json` para más detalles.
