# 🚀 Guía de Despliegue - Chess Trainer

## 📋 Requisitos previos

- Python 3.10+ con Conda
- Node.js 18+ y npm
- Environment de Conda llamado `chess` (ya creado)

## 🎮 Iniciar la aplicación

### Opción 1: Usando scripts automatizados (RECOMENDADO)

```bash
# Dar permisos de ejecución (solo la primera vez)
chmod +x start.sh stop.sh

# Iniciar toda la aplicación
./start.sh

# Detener toda la aplicación
./stop.sh
```

### Opción 2: Inicio manual

#### 1️⃣ Iniciar el Backend (Terminal 1)

```bash
# Activar environment de conda
conda activate chess

# Ir al directorio del proyecto
cd /Users/diegor/dev/chessTrainer

# Iniciar el servidor FastAPI
uvicorn main:app --reload --port 8000
```

El backend estará disponible en: **http://localhost:8000**

#### 2️⃣ Iniciar el Frontend (Terminal 2)

```bash
# Ir al directorio del frontend
cd /Users/diegor/dev/chessTrainer/frontend

# Iniciar el servidor de desarrollo Vite
npm run dev
```

El frontend estará disponible en: **http://localhost:5173**

## 🛑 Cerrar la aplicación

### Opción 1: Usando el script

```bash
./stop.sh
```

### Opción 2: Cierre manual

#### Si los ejecutaste en terminales separadas:
- Presiona `Ctrl + C` en cada terminal

#### Si se ejecutan en segundo plano o perdiste la terminal:

```bash
# Detener el backend
pkill -f "uvicorn main:app"

# Detener el frontend
pkill -f "vite"

# Verificar que se detuvieron
ps aux | grep -E "(uvicorn|vite)" | grep -v grep
```

## 🔧 Motores de ajedrez disponibles

### 1. **Lichess Cloud** (online)
- ✅ Ya configurado
- ⚠️ Solo funciona con posiciones populares (primeras 10-15 jugadas)
- 📝 Selecciona "lichess" en el frontend

### 2. **Stockfish Local** (offline)
- Requiere instalación:
  ```bash
  # En Mac
  brew install stockfish
  
  # En Linux (Ubuntu/Debian)
  sudo apt-get install stockfish
  ```
- 📝 Selecciona "stockfish-local" en el frontend

## 🐛 Solución de problemas

### El backend no inicia
```bash
# Verificar que el environment está activo
conda activate chess

# Verificar dependencias
pip install -r requirements.txt
```

### El frontend no inicia
```bash
# Reinstalar dependencias
cd frontend
npm install
```

### Error CORS
- Asegúrate de que ambos servidores estén corriendo
- El backend debe estar en puerto 8000
- El frontend debe estar en puerto 5173 o 3000

### Lichess devuelve error 404
- Normal después de ~10 jugadas en posiciones no populares
- Usa Stockfish local en su lugar

## 📦 Estructura del proyecto

```
chessTrainer/
├── main.py                 # Backend FastAPI
├── engine_manager.py       # Gestión de motores de ajedrez
├── config/
│   └── engines.yaml       # Configuración de motores
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Componente principal
│   │   └── GamePage.jsx   # Lógica del juego
│   └── package.json       # Dependencias frontend
├── requirements.txt       # Dependencias backend
├── start.sh              # Script para iniciar
├── stop.sh               # Script para detener
└── DESPLIEGUE.md         # Este archivo
```

## 🔐 Puertos utilizados

- **Backend:** 8000
- **Frontend:** 5173

Asegúrate de que estos puertos estén disponibles antes de iniciar.

## 📝 Notas

- La aplicación usa chess.js **v1.4.0** (versión estable más reciente)
- Los cambios en el código se recargan automáticamente (hot reload)
- Los logs del backend aparecen en la terminal donde se ejecuta uvicorn
- Los logs del frontend aparecen en la consola del navegador


