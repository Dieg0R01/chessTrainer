## 🎉 Chess Trainer v3.0.0 - Changelog

---

## 🚀 Visión General

La versión **3.0.0** se centra en:

1. **UX del tablero y responsividad completa** (selección por click, drag mejorado, casillas de 75px, layout simplificado).
2. **Herramientas de análisis avanzadas** (página de comparación de motores totalmente documentada).
3. **Sistema de Disponibilidad de Motores** (verificación de binarios/conexión y filtrado automático).
4. **Mejoras de frontend y documentación** sobre la base de la refactorización de protocolos introducida en v2.x.
5. **Integración y pulido** de las mejoras introducidas en el commit `ee8dcc0` (v2.1.0).

---

## 📌 Resumen de Cambios por Capas

- **Basado en v2.0.0** (`CAMBIOS_v2.0.0.md` – refactor de protocolos).
- **v2.1.0 (`ee8dcc0`)**: nueva selección de motores, filtros, UI mejorada y explicaciones de motores generativos.
- **v3.0.0 (cambios actuales sin commitear)**: simplificación de UI, responsividad real del tablero, mejoras de interacción, sistema de disponibilidad y documentación avanzada.

---

## 🧩 Cambios del Commit `ee8dcc0` (v2.1.0)

### 🎛 1. Nueva Pantalla de Selección de Motores

**Archivos clave**:
- `frontend/src/App.jsx`
- `frontend/src/App.css`
- `frontend/src/CustomSelect.jsx`
- `frontend/src/index.css`
- `frontend/src/api.js`

**Características:**

- **Selector principal de motores**:
  - Motor A (blancas) y Motor B (negras/ninguno/humano).
  - Opción de jugar humano vs motor, motor vs motor, o humano vs humano.
- **Filtros avanzados** en la pantalla de selección:
  - Filtro por **tipo** de motor: `traditional`, `neuronal`, `generative`.
  - Filtro por **origen**: interno/externo.
- **Componente `CustomSelect`**:
  - Reemplaza los `<select>` nativos con un estilo retro, lista desplegable propia y comportamiento consistente.

**Nuevas APIs frontend** (`frontend/src/api.js`):

- `fetchEngines()` – Lista de motores disponibles.
- `fetchEnginesInfo()` – Metadatos detallados (tipo, origen, validación, estado, etc.).
- `filterEnginesByType(type)` – Filtro remoto por tipo.
- `filterEnginesByOrigin(origin)` – Filtro remoto por origen.
- `reloadConfig()` – Recarga de configuración de motores desde backend.
- `checkBackendHealth()` – Estado del backend (versión, número de motores, etc.).

---

### 📡 2. Mejoras en GamePage y Motores Generativos

**Archivos clave**:
- `frontend/src/GamePage.jsx`
- `frontend/src/App.css`
- `frontend/src/index.css`
- `frontend/src/api.js`
- `main.py`
- `engines/generative.py`
- `config/prompt_template.jinja`
- `config/prompt_template.md.jinja`

**Funcionalidades añadidas en `ee8dcc0`:**

- **Selección de estrategia** para motores generativos:
  - Posibilidad de elegir estrategias o modos (ej. posicional, balanced, táctico).
  - Integración con templates de prompts externos (`prompt_template.jinja`, `prompt_template.md.jinja`).
- **Explicaciones detalladas de motores generativos**:
  - GamePage muestra texto explicativo sobre por qué se ha elegido un movimiento.
  - Backend y templates de prompt se ajustan para:
    - Evitar movimientos repetitivos.
    - Asegurar que el historial se envía en formato correcto (UCI).
- **Estado y logging mejorados**:
  - Logs más detallados sobre:
    - Historial de movimientos enviado al motor generativo.
    - Respuestas de los proveedores LLM.
  - Mejor manejo de errores de comunicación con LLMs.

---

### 🧪 3. API y Scripts

**Archivos:**
- `main.py`
- `start.sh`
- `docs/development/API_USAGE.md`
- `frontend/src/api.js`

**Cambios:**

- `start.sh`:
  - Mejora de inicialización de conda y entorno para evitar fallos intermitentes.
- `API_USAGE.md`:
  - Nuevas secciones describiendo las funciones añadidas en `api.js` y los endpoints asociados.
- `main.py`:
  - Endpoints extendidos para:
    - Salud del backend (`/health`).
    - Recarga de configuración de motores.
    - Obtención de info detallada de motores.

---

## 🎨 Cambios v3.0.0 – UI y UX del Tablero

### 🧭 1. Layout Simplificado y Más Estrecho

**Archivos:**
- `frontend/src/App.css`
- `frontend/src/index.css`
- `frontend/src/App.jsx`

**Cambios:**

- `retro-container`:
  - `max-width` reducido a ~700px y centrado, estilo terminal estrecho.
  - Fondo sólido (`var(--retro-bg)`) sin gradientes pesados.
  - Bordes simplificados a `1px` (footer/header/paneles) en lugar de 3–4px + sombras.
- Títulos y textos:
  - Tamaños reducidos (`main-title`, `terminal-title`, `status-line`) para encajar mejor en el nuevo layout.
- Logo:
  - De `321px` fijados a ~`200px`, respetando el estilo retro pero ocupando menos espacio visual.
- **Eliminación de scrollbars innecesarios**:
  - Los paneles `.panel-content` y `.history-content` ahora se expanden verticalmente de forma dinámica según su contenido, eliminando barras de desplazamiento internas.

---

### ♟ 2. Responsividad Completa del Tablero

**Archivos:**
- `frontend/src/App.css`
- `frontend/src/GamePage.jsx`

**Objetivo:** que el tablero:

1. **Mantenga proporción cuadrada.**
2. **Use casillas de 75px** en desktop.
3. **Se adapte a móviles y tablets** sin romper el layout ni dejar espacios enormes.

**Cambios clave en CSS:**

- `board-frame`:
  - En modo juego (`.board-frame.game-mode`):
    - `aspect-ratio: 1;`
    - `max-width: 640px` (desktop) con padding reducido.
  - En modo selección (`.board-frame.selection-mode`):
    - Sin `aspect-ratio`, altura auto, contenido centrado verticalmente.
- `board-inner`:
  - Centrado con flexbox.
  - En modo juego: rellena el espacio disponible; en selección, deja espacio extra arriba/abajo para el formulario.
- **Casillas de 75px**:
  - `.board-inner .chess-square` y overrides específicos:
    - `width: 75px !important;`
    - `height: 75px !important;`
  - En desktop, tablero de **600x600** (8×75px).

**Media queries actualizados:**

- **Móviles (`max-width: 480px`)**
  - `board-frame.game-mode`:
    - `max-height: min(70vh, calc(100vw - 50px));`
    - padding reducido.
  - `board-inner.game-mode > div` y `.chess-board`:
    - 100% del contenedor con `aspect-ratio: 1`.
- **Tablets pequeñas / móviles grandes (481–768px)**
  - Ajustes similares con límites adaptados a ese rango.
- **Tablets (769–1024px)**
  - `boardSize` calculado en frontend (ver siguiente sección).
- **Desktop (≥1025px)**
  - Tablero fijo 600×600, casillas 75px, enmarcado en un `board-inner` centrado.

---

### 🧮 3. Tamaño del Tablero en Función de Casillas (75px)

**Archivo:**
- `frontend/src/GamePage.jsx`

**Nuevo estado:**

```javascript
const [boardSize, setBoardSize] = useState(600); // 8 * 75
```

**Lógica responsive:**

```javascript
useEffect(() => {
  const updateBoardSize = () => {
    const width = window.innerWidth;
    const squareSize = 75;
    const squaresPerRow = 8;

    if (width <= 480) {
      const maxWidth = width - 50;
      const maxSquares = Math.floor(maxWidth / squareSize);
      const boardSize = Math.min(maxSquares, squaresPerRow) * squareSize;
      setBoardSize(boardSize);
    } else if (width <= 768) {
      const maxWidth = width - 60;
      const maxSquares = Math.floor(maxWidth / squareSize);
      const boardSize = Math.min(maxSquares, squaresPerRow) * squareSize;
      setBoardSize(boardSize);
    } else if (width <= 1024) {
      const maxWidth = width - 80;
      const maxSquares = Math.floor(maxWidth / squareSize);
      const boardSize = Math.min(maxSquares, squaresPerRow) * squareSize;
      setBoardSize(boardSize);
    } else {
      setBoardSize(squaresPerRow * squareSize); // 600px
    }
  };

  updateBoardSize();
  window.addEventListener('resize', updateBoardSize);
  return () => window.removeEventListener('resize', updateBoardSize);
}, []);
```

**Integración con `Chessboard`:**

```javascript
<Chessboard
  position={position}
  onPieceDrop={onPieceDrop}
  onSquareClick={onSquareClick}
  onPieceDragBegin={onPieceDragBegin}
  onPieceDragEnd={onPieceDragEnd}
  customSquareStyles={customSquareStyles}
  customBoardStyle={{ width: '100%', height: '100%', borderRadius: 0, boxShadow: 'none' }}
  customLightSquareStyle={{ backgroundColor: '#24a32a' }}
  customDarkSquareStyle={{ backgroundColor: '#147e1f' }}
  boardWidth={boardSize}
  arePiecesDraggable={!isProcessing}
/>
```

---

### 🖱 4. Interacción del Tablero: Click + Drag Unificados

**Documento de soporte:** `docs/changelog/MEJORAS_UI_TABLERO.md`  
**Archivo principal:** `frontend/src/GamePage.jsx`

**Nuevos estados:**

- `selectedSquare`: casilla actualmente seleccionada.
- `possibleMoves`: mapa de casillas destino → estilos de resaltado.

**Funciones añadidas / mejoradas:**

- `getPossibleMoves(square)`:
  - Usa `chess.js` para calcular movimientos legales desde `square`.
  - Genera estilos con gradientes radiales para indicar casillas destino.
- `onSquareClick(square)`:
  - Click en pieza propia → selecciona y muestra movimientos.
  - Click en casilla destino válida → ejecuta movimiento.
  - Click en otra cosa → limpia selección.
- `onPieceDragBegin(piece, sourceSquare)`:
  - Muestra movimientos posibles al empezar un drag (solo turno humano).
- `onPieceDragEnd()`:
  - Limpia selección si el drag no termina en un movimiento válido.
- Limpieza consistente:
  - Después de un movimiento aceptado en `onPieceDrop` se limpian `selectedSquare` y `possibleMoves`.

**Resultado UX:**

- Dos formas equivalentes de jugar:
  - **Click → Click**
  - **Drag & Drop**
- Resaltados siempre consistentes:
  - Casilla seleccionada + casillas posibles.
- Eliminados artefactos visuales (círculos gigantes o mal posicionados).

---

### 🚦 5. Sistema de Disponibilidad de Motores

**Archivos:**
- `engine_manager.py`, `main.py`
- `engines/base.py` y protocolos (`UCI`, `REST`, `LocalLLM`, `APILLM`)
- `frontend/src/hooks/useEngines.js`
- `frontend/src/App.jsx`
- `frontend/src/ComparePage.jsx`

**Funcionalidad:**

- **Verificación activa (Backend)**:
  - Al iniciar el servidor, se verifica si cada motor configurado es realmente utilizable:
    - **UCI**: Comprueba si el archivo binario existe y es ejecutable.
    - **REST / LLM**: Verifica la URL, hace ping si es localhost, y valida API keys.
  - Los motores se marcan con una propiedad `available: true/false`.
- **Filtrado automático (Frontend)**:
  - El hook `useEngines` filtra automáticamente los motores no disponibles de la lista principal.
  - Los selectores de partida solo muestran motores válidos.
  - El contador "ENGINES: X" refleja el número de motores disponibles para usar.
- **Visualización de estado**:
  - En `SelectionPage`, se muestran detalles dinámicos ("MOTOR A:", "MOTOR B:") solo para los motores seleccionados, incluyendo su estado de disponibilidad.
  - En `ComparePage`, los motores no disponibles aparecen en gris con el mensaje "Motor no disponible o mal configurado" en lugar de generar errores.

---

## 📊 v3.0.0 – Herramientas de Análisis y Documentación

### 🔍 1. Página de Comparación de Motores

**Documento:** `docs/development/COMPARACION_MOTORES.md`  
**Archivos de código:**
- `frontend/src/ComparePage.jsx`
- `frontend/src/api.js`
- `frontend/src/App.css`
- `main.py`
- `engine_manager.py`

**Características principales:**

- Página `/compare` que permite:
  - Editar la posición en un tablero interactivo.
  - Elegir profundidad de análisis.
  - Comparar **todos los motores** registrados (tradicionales, neuronales, generativos).
- Tabla de resultados:
  - Motor, mejor jugada (UCI), explicación (si está disponible).
  - Filtrado en tiempo real por motor, jugada o texto de explicación.
  - Señalización clara de errores por motor sin bloquear el resto.
  - Detección visual de motores no disponibles (grisaceos).

**Backend:**

- Endpoint `POST /compare`:
  - Request: `{ fen, depth }`.
  - Respuesta: `{ fen, results: [...], engines_compared: N }`.
- `engine_manager.compare_engines()`:
  - Itera motores en paralelo.
  - Salta motores no disponibles.
  - Pide explicación automáticamente para motores generativos.
  - Formatea resultados en un diccionario y luego array.

**Docs detalladas en `COMPARACION_MOTORES.md`:**
- Flujo completo de datos.
- Estados y funciones clave en `ComparePage.jsx`.
- Ejemplos de uso en UI y vía curl/API.
- Sugerencias de futuras mejoras (filtros, métricas, historial, exportación).

---

### 📚 2. Otros Documentos y Mejoras de Docs

**Archivos:**
- `docs/development/API_USAGE.md`
- `docs/changelog/MEJORAS_UI_TABLERO.md`
- `docs/development/COMPARACION_MOTORES.md`
- `docs/README.md`

**Cambios:**

- `API_USAGE.md`:
  - Actualizado para reflejar:
    - Nuevas funciones del módulo `api.js`.
    - Nuevos endpoints (`/compare`, `/health`, recarga de config, etc.).
- `MEJORAS_UI_TABLERO.md`:
  - Documento centrado en las mejoras de interacción con el tablero (click + drag, estilos, limpieza).
- `COMPARACION_MOTORES.md`:
  - Documento extenso sobre la página de comparación (modo análisis global).
- `docs/README.md`:
  - Actualizado para mencionar las nuevas capacidades de análisis (compare) y UX del tablero.

---

## 🛠 3. Backend y Motor Manager

**Archivos:**
- `engine_manager.py`
- `main.py`

**Principales mejoras adicionales (sobre v2.x):**

- `compare_engines(fen, depth)`:
  - Lógica robusta para iterar motores, pedir movimientos y explicaciones.
  - Manejo de errores individuales por motor.
- Integración con motores generativos:
  - Usa la nueva refactorización de protocolos de v2.0.0 y los templates mejorados.
- Logging mejorado:
  - Logs de llamadas a `/compare`.
  - Trazas de errores por motor.

---

## 🐛 Bugs y Comportamientos Corregidos en v3

1. **Desalineación del tablero vs contenedor (`board-inner`)**
   - Ahora:
     - Casillas de 75px → tablero 600×600.
     - `boardSize` en frontend sincronizado con este tamaño.
2. **Círculos de movimientos posibles mal posicionados / gigantes**
   - Eliminado código de manipulación directa del DOM.
   - Todo se hace con `customSquareStyles` + CSS bien encapsulado.
3. **Scrolls internos y layouts inestables en pantallas pequeñas**
   - Paneles con scroll interno solo cuando es necesario, ahora expandibles verticalmente para mostrar contenido completo.
   - `board-container` y `board-frame` ajustados por media queries.
4. **Inconsistencias entre `/game` y `/compare`**
   - Comportamiento del tablero unificado:
     - Mismas reglas de interacción.
     - Misma paleta de colores y estilo retro.
5. **Errores silenciosos por motores no disponibles**
   - Implementado sistema de verificación de disponibilidad (`check_availability`).
   - Filtrado preventivo en selectores.

---

## 🐳 v3.0.0 – Dockerización y Gestión de Motores

### 🏗️ 1. Sistema Docker Completo

**Archivos:**
- `Dockerfile.engines` (multi-stage build para motores)
- `docker-compose.engines.yml` (configuración para contenedor de motores)
- `scripts/build_lc0.sh` (ejecutado automáticamente durante el build)
- `docs/deployment/DOCKER_SETUP.md`
- `docs/deployment/FUENTES_MOTORES.md`
- `docs/deployment/COMPILAR_LC0.md`
- `docs/deployment/DESPLIEGUE.md`
- `download_weights.sh`

**Características:**

- **Multi-stage Docker build para motores**:
  - Etapa 1: Engines installer (compila LC0, descarga Stockfish)
  - Etapa 2: Final (imagen mínima con binarios y librerías de runtime)
  - Contenedor `chess-engines` solo para motores, no ejecuta backend

- **Instalación automática de motores**:
  - **Stockfish**: Descarga automática desde GitHub releases
    - Detección automática de arquitectura (ARM64 vs x86-64)
    - Binarios precompilados para ambas arquitecturas
  - **Lc0**: Compilación automática durante el build del Docker
    - Script `build_lc0.sh` se ejecuta automáticamente en `Dockerfile.engines`
    - Compilación con Meson (sistema de build moderno)
    - Soporte para backend BLAS (CPU)
    - Librerías de runtime incluidas en la imagen final (libopenblas, libprotobuf)

- **Gestión de weights (redes neuronales)**:
  - Script `download_weights.sh` para descargar redes automáticamente
  - Volumen Docker montado para persistir weights (`./weights:/app/weights`)
  - Configuración YAML lista para usar weights descargados

- **Configuración Docker**:
  - `docker-compose.engines.yml` para contenedor de motores
  - Contenedor `chess-engines` corriendo en background
  - Volúmenes para config y weights (editable sin rebuild)
  - Backend y frontend se ejecutan localmente en conda `chess`
  - Comunicación mediante `docker exec -i chess-engines`

---

### 🔧 2. Mejoras en Sistema de Disponibilidad

**Archivos:**
- `engines/protocols/uci.py`
- `engines/protocols/rest.py`
- `engines/protocols/local_llm.py`
- `engines/protocols/api_llm.py`
- `engines/base.py`
- `engine_manager.py`
- `main.py`

**Mejoras implementadas:**

- **Timeouts robustos en UCIProtocol**:
  - `_read_until()` con timeout configurable (10s por defecto)
  - Timeout de 30s para obtener `bestmove`
  - Mejor manejo de errores y logging detallado
  - Prevención de cuelgues infinitos

- **Verificación de disponibilidad mejorada**:
  - **UCI**: Verifica existencia y permisos de ejecución del binario
    - Para comandos Docker (`docker exec -i chess-engines ...`): verifica que el contenedor esté corriendo
    - Extrae nombre del contenedor del comando y verifica con `docker ps`
  - **REST**: Valida formato de URL y hace ping a localhost
  - **LocalLLM**: Verifica endpoints de health (`/health`, `/version`, etc.)
  - **APILLM**: Valida URL y presencia de API key

- **Verificación en background**:
  - `check_all_availability()` se ejecuta al iniciar el servidor
  - No bloquea el arranque (ejecuta en background con `asyncio.create_task`)
  - Se re-ejecuta automáticamente al recargar configuración (`POST /reload`)

- **Filtrado automático en frontend**:
  - `useEngines` hook filtra motores no disponibles
  - Contador "ENGINES: X" refleja solo motores disponibles
  - Selectores de partida solo muestran motores válidos

---

### 🧠 3. Compilación y Configuración de Lc0

**Archivos:**
- `Dockerfile.engines` (compila LC0 automáticamente durante el build)
- `scripts/build_lc0.sh` (ejecutado automáticamente en el Dockerfile)
- `config/engines_local.yaml`
- `docs/deployment/COMPILAR_LC0.md`
- `docs/deployment/DESPLIEGUE.md`
- `INSTRUCCIONES_LC0.md`

**Características:**

- **Compilación automática durante el build del Docker**:
  - El script `build_lc0.sh` se ejecuta automáticamente en `Dockerfile.engines`
  - Instala dependencias automáticamente (meson, ninja, build-essential, etc.)
  - Clona repositorio de Lc0 desde GitHub
  - Compila con Meson (sistema de build moderno)
  - Detecta arquitectura y configura backend apropiado (BLAS)
  - Instala binario en `/app/bin/lc0`
  - Verifica que la compilación fue exitosa antes de continuar
  - Librerías de runtime (libopenblas, libprotobuf) incluidas en la imagen final

- **Configuración lista para usar**:
  - `lc0-local`: Motor fuerte con red T82-768x15x24h
    - Comando: `docker exec -i chess-engines /app/bin/lc0`
  - `maia-1500`: Motor estilo humano (Elo 1500) con red Maia
    - Comando: `docker exec -i chess-engines /app/bin/lc0`
  - Rutas de weights configuradas para Docker (`weights/...`)
  - Contenedor `chess-engines` debe estar corriendo

- **Documentación completa**:
  - Guía paso a paso para despliegue completo (`DESPLIEGUE.md`)
  - Instrucciones para compilación automática en Dockerfile (ya implementado)
  - Solución de problemas comunes
  - Referencias a fuentes oficiales
  - Tasks de VS Code para iniciar el sistema completo

---

### 🎯 4. Tasks de VS Code para Despliegue Automatizado

**Archivos:**
- `.vscode/tasks.json`

**Características:**

- **Tasks predefinidas para desarrollo**:
  - 🐳 **Iniciar Docker Engines**: Levanta el contenedor `chess-engines`
  - 🐳 **Construir Docker Engines**: Construye la imagen (compila LC0 automáticamente)
  - 🐍 **Iniciar Backend**: Inicia el backend usando `start_backend.sh` con conda `chess`
  - 🎨 **Iniciar Frontend**: Inicia el frontend usando `start_frontend.sh` con conda `chess`
  - 🚀 **Iniciar Chess Trainer Completo**: Task principal que ejecuta todo en secuencia (marcada como default)
  - 🛑 **Detener Docker Engines**: Detiene el contenedor
  - 🔍 **Verificar Estado del Sistema**: Verifica el estado de todos los componentes
  - 📋 **Listar Motores Disponibles**: Muestra información de los motores

- **Uso simplificado**:
  - Presionar `Cmd+Shift+B` (macOS) o `Ctrl+Shift+B` (Linux/Windows) para ejecutar la task default
  - O usar `Cmd+Shift+P` → "Tasks: Run Task" → seleccionar la task deseada
  - Las tasks usan los scripts existentes (`start_backend.sh`, `start_frontend.sh`) que manejan conda correctamente

- **Integración con documentación**:
  - Documentado en `docs/deployment/DESPLIEGUE.md`
  - Permite iniciar todo el sistema con un solo comando

---

### 🔄 5. Mejoras en Gestión de Estado Frontend

**Archivos:**
- `frontend/src/App.jsx`
- `frontend/src/hooks/useEngines.js`

**Cambios:**

- **Contexto de motores persistente**:
  - `useEngines` movido al nivel de `App` para persistir entre navegaciones
  - Evita recarga innecesaria al volver a la pantalla de selección
  - Lista de motores se mantiene disponible durante toda la sesión

- **Mejor manejo de errores**:
  - Logging detallado en `useEngines` para debugging
  - Manejo de estados `available: null` vs `available: false`
  - Filtrado explícito de motores no disponibles

---

### 🐛 6. Correcciones Adicionales

**Problemas resueltos:**

1. **Stockfish no respondía en Docker (ARM64)**:
   - Solución: Detección automática de arquitectura y descarga del binario correcto
   - Verificación de existencia sin ejecutar (evita errores de Rosetta en macOS)

2. **CORS bloqueando frontend local con backend Dockerizado**:
   - Solución: `localhost:5173` siempre permitido, incluso en producción
   - Permite desarrollo local del frontend con backend en Docker

3. **Lc0 no se compilaba automáticamente**:
   - Solución: Compilación automática durante el build del Docker
   - Script `build_lc0.sh` ejecutado automáticamente en `Dockerfile.engines`
   - Detección automática de arquitectura para configuración de BLAS
   - Librerías de runtime incluidas en la imagen final
   - Verificación de compilación exitosa antes de continuar

4. **Timeouts infinitos en UCIProtocol**:
   - Solución: Timeouts configurables en todas las operaciones de lectura
   - Mejor logging de errores para debugging

---

## 📈 Resumen de Impacto v3.0.0

- **UX/Front**:
  - Interacción del tablero muy mejorada (click + drag, casillas claras, responsivo).
  - Layout más limpio y estrecho, fiel al estilo retro-terminal.
  - Eliminación de elementos estáticos innecesarios en favor de información dinámica y contextual.
  - Gestión de estado mejorada (persistencia de motores entre navegaciones).
- **Análisis**:
  - Herramienta de comparación de motores completa y documentada.
- **Robustez**:
  - Detección automática de motores rotos o mal configurados.
  - Timeouts robustos para prevenir cuelgues.
  - Verificación de disponibilidad en background sin bloquear arranque.
- **Deployment**:
  - Sistema Docker completo con motores pre-instalados y LC0 compilado automáticamente.
  - Contenedor `chess-engines` encapsula todos los motores.
  - Scripts de compilación y descarga automatizados.
  - Documentación exhaustiva de deployment (`DESPLIEGUE.md`).
  - Tasks de VS Code para iniciar el sistema completo con un solo comando.
- **Docs**:
  - Documentación alineada con arquitectura real (tablero, compare, API).
  - Guías completas de Docker, compilación de motores y fuentes.
- **Compatibilidad**:
  - Mantiene compatibilidad con la infraestructura de protocolos y motores introducida en v2.0.0 y v2.1.0.
  - CORS configurado para desarrollo local con Docker.
  - Backend y frontend se ejecutan localmente en conda `chess` para facilitar desarrollo.
  - Contenedor Docker solo para motores, comunicación mediante `docker exec`.

---

**Versión**: 3.0.0  
**Basada en**: 2.1.0 (`ee8dcc0`) + cambios actuales del workspace  
**Fecha**: Diciembre 2024  
**Tipo de Release**: Major (UX + nuevas herramientas de análisis + Dockerización, sin romper compatibilidad con configs)
