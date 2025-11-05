# ♟️ Chess Trainer

Aplicación de entrenamiento de ajedrez construida con React + Vite.

## 📋 Requisitos Previos

- **Conda**: El proyecto usa el entorno conda `chess`
- **Node.js**: Instalado en el sistema (se usa a través de conda)
- **npm**: Para gestionar dependencias del frontend

## 🚀 Inicio Rápido

### Configuración Inicial

1. **Crear el entorno conda** (si no existe):
```bash
conda create -n chess python=3.9
conda activate chess
```

2. **Clonar el repositorio** (si aún no lo has hecho):
```bash
git clone <repository-url>
cd chessTrainer
```

### Control del Frontend

El proyecto incluye un sistema de scripts para gestionar el frontend de manera sencilla:

#### Opción 1: Script Maestro (Recomendado)

```bash
# Ver ayuda
./frontend.sh help

# Iniciar el servidor
./frontend.sh start

# Ver estado
./frontend.sh status

# Detener el servidor
./frontend.sh stop

# Reiniciar
./frontend.sh restart
```

#### Opción 2: Scripts Individuales

```bash
# Iniciar
bash start_frontend.sh

# Detener
bash stop_frontend.sh
```

## 🛠️ Características del Sistema de Scripts

### `frontend.sh` (Script Maestro)
- **start**: Inicia el servidor frontend
- **stop**: Detiene todos los procesos relacionados
- **restart**: Reinicia el servidor
- **status**: Muestra el estado actual del servidor

### Sistema de Inicio (`start_frontend.sh`)
1. ✅ Limpia procesos previos automáticamente
2. ✅ Activa el entorno conda `chess`
3. ✅ Verifica e instala dependencias si es necesario
4. ✅ Inicia el servidor Vite
5. ✅ Guarda el PID para control posterior
6. ✅ Abre el navegador automáticamente
7. ✅ Muestra logs en tiempo real

### Sistema de Detención (`stop_frontend.sh`)
1. ✅ Mata procesos por puerto (5173)
2. ✅ Usa archivo PID para limpieza precisa
3. ✅ Busca y elimina procesos huérfanos
4. ✅ Limpia archivos temporales
5. ✅ Verifica que el puerto quede libre

## 📊 Verificar Estado

Para verificar si el frontend está corriendo:

```bash
# Opción 1: Usar el script
./frontend.sh status

# Opción 2: Verificar manualmente
curl http://localhost:5173
lsof -i :5173
```

## 🌐 Acceso

Una vez iniciado, el frontend estará disponible en:
- **Local**: http://localhost:5173
- **Red**: http://<tu-ip>:5173

## 📝 Logs

Los logs del servidor se guardan en:
```bash
tail -f logs_frontend.log
```

## 🐛 Solución de Problemas

### El servidor no inicia

1. Verificar que el entorno conda está activo:
```bash
conda env list
```

2. Verificar que el puerto está libre:
```bash
./frontend.sh stop
```

3. Reinstalar dependencias:
```bash
cd frontend
rm -rf node_modules
npm install
```

### Puerto en uso

Si el puerto 5173 está ocupado:
```bash
# Opción 1: Usar el script de detención
./frontend.sh stop

# Opción 2: Matar manualmente
kill -9 $(lsof -ti :5173)
```

### Proceso zombie

Si hay procesos que no responden:
```bash
# El script de detención usa kill -9 para forzar
./frontend.sh stop
```

## 🏗️ Estructura del Proyecto

```
chessTrainer/
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── App.jsx
│   │   ├── GamePage.jsx
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
├── engines/               # Motores de ajedrez (backend)
├── frontend.sh            # Script maestro de control
├── start_frontend.sh      # Script de inicio
├── stop_frontend.sh       # Script de detención
└── README.md             # Este archivo
```

## 🔧 Desarrollo

### Tecnologías

- **Frontend**: React 19 + Vite
- **Chess Engine**: chess.js
- **UI Components**: react-chessboard
- **Routing**: react-router-dom

### Scripts npm disponibles

```bash
cd frontend

# Desarrollo
npm run dev

# Build producción
npm run build

# Preview build
npm run preview

# Linting
npm run lint
```

## 📦 Dependencias

Las dependencias se instalan automáticamente al ejecutar `./frontend.sh start` o `bash start_frontend.sh`.

Para instalar manualmente:
```bash
cd frontend
npm install
```

## 🤝 Contribuir

1. Crear un branch desde `develop/frontend`
2. Hacer cambios
3. Commit y push
4. Crear Pull Request

## 📄 Licencia

[Agregar licencia aquí]

---

**Nota**: Todos los scripts deben ejecutarse desde el directorio raíz del proyecto (`chessTrainer/`).
