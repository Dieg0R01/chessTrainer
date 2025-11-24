# Documentación de Uso de APIs - Chess Trainer

## Índice

1. [Resumen General](#resumen-general)
2. [APIs del Backend](#apis-del-backend)
3. [Funciones del Frontend](#funciones-del-frontend)
4. [Flujos de Datos](#flujos-de-datos)
5. [Ubicaciones del Código](#ubicaciones-del-código)
6. [Ejemplos de Uso](#ejemplos-de-uso)

---

## Resumen General

Este documento describe el uso completo de todas las APIs disponibles en Chess Trainer, tanto en el backend (FastAPI) como en el frontend (React). Todas las APIs están implementadas y funcionando.

### Estadísticas

- **Total de endpoints backend**: 12
- **Total de funciones API frontend**: 11
- **APIs implementadas y en uso**: 11 (100%)
- **Componentes que consumen APIs**: 4 (App.jsx, GamePage.jsx, ComparePage.jsx, EnginesMatrixPage.jsx)

---

## APIs del Backend

### 1. `GET /engines`

**Ubicación**: `main.py:202-224`

**Descripción**: Lista todos los motores disponibles.

**Respuesta**:
```json
{
  "engines": ["stockfish-local", "gpt-4o-mini", ...],
  "count": 5
}
```

**Uso en Frontend**: 
- Función: `fetchEngines()` en `api.js:36-95`
- Componente: `App.jsx` (SelectionPage)
- Líneas: `App.jsx:20-47`

**Flujo**:
```
SelectionPage (useEffect al montar)
  → fetchEngines()
    → GET /engines
      → engine_manager.list_engines()
        → setAvailableEngines(engines)
          → Renderiza selects con motores
```

---

### 2. `GET /engines/info`

**Ubicación**: `main.py:227-238`

**Descripción**: Obtiene información detallada de todos los motores (tipo, origen, modo de validación, estado de inicialización).

**Respuesta**:
```json
{
  "engines": [
    {
      "name": "stockfish-local",
      "type": "traditional",
      "origin": "internal",
      "validation_mode": "schema",
      "initialized": true
    },
    ...
  ],
  "count": 5
}
```

**Uso en Frontend**: 
- Función: `fetchEnginesInfo()` en `api.js:166-187`
- Componente: `App.jsx` (SelectionPage)
- Líneas: `App.jsx:48-52` (carga en paralelo con fetchEngines)

**Flujo**:
```
SelectionPage (useEffect al montar)
  → Promise.all([fetchEngines(), fetchEnginesInfo()])
    → GET /engines/info
      → engine_manager.get_engines_info()
        → setEnginesInfo(infoMap)
          → Muestra info detallada cuando se selecciona un motor
```

**Visualización**: Panel "SELECCIONADO" en `App.jsx:190-210` muestra tipo, origen, validación y estado.

---

### 3. `GET /engines/matrix`

**Ubicación**: `main.py:241-260`

**Descripción**: Obtiene la matriz de clasificación de motores con sus dimensiones (tipo, origen, modo de validación).

**Respuesta**:
```json
{
  "matrix": [
    {
      "name": "stockfish-local",
      "type": "traditional",
      "origin": "internal",
      "validation_mode": "schema"
    },
    ...
  ],
  "count": 5,
  "description": {
    "type": ["traditional", "neuronal", "generative"],
    "origin": ["internal", "external"],
    "validation_mode": ["schema", "prompt"]
  }
}
```

**Uso en Frontend**: 
- Función: `fetchEnginesMatrix()` en `api.js:193-214`
- Componente: `EnginesMatrixPage.jsx`
- Líneas: `EnginesMatrixPage.jsx:12-20`

**Flujo**:
```
Usuario navega a /matrix
  → EnginesMatrixPage (useEffect al montar)
    → fetchEnginesMatrix()
      → GET /engines/matrix
        → engine_manager.get_classification_matrix()
          → EngineClassifier.generate_classification_matrix()
            → setMatrix(data)
              → Renderiza tabla con colores por tipo/origen
```

**Visualización**: Tabla completa con colores diferenciados por tipo y origen en `EnginesMatrixPage.jsx:60-95`.

---

### 4. `GET /engines/filter/type/{motor_type}`

**Ubicación**: `main.py:263-290`

**Descripción**: Filtra motores por tipo (traditional, neuronal, generative).

**Parámetros**:
- `motor_type`: `"traditional"`, `"neuronal"`, o `"generative"`

**Respuesta**:
```json
{
  "type": "generative",
  "engines": ["gpt-4o-mini", "gpt-3.5-turbo"],
  "count": 2
}
```

**Uso en Frontend**: 
- Función: `filterEnginesByType()` en `api.js:221-244`
- Componente: `App.jsx` (SelectionPage)
- Líneas: `App.jsx:75-87` (en useEffect de filtros)

**Flujo**:
```
Usuario selecciona filtro de tipo
  → setFilterType("generative")
    → useEffect detecta cambio
      → filterEnginesByType("generative")
        → GET /engines/filter/type/generative
          → engine_manager.filter_engines_by_type(MotorType.GENERATIVE)
            → setFilteredEngines(result.engines)
              → Actualiza selects con motores filtrados
```

**Visualización**: Select de filtro en `App.jsx:108-120`, aplica filtro en tiempo real.

---

### 5. `GET /engines/filter/origin/{motor_origin}`

**Ubicación**: `main.py:293-318`

**Descripción**: Filtra motores por origen (internal, external).

**Parámetros**:
- `motor_origin`: `"internal"` o `"external"`

**Respuesta**:
```json
{
  "origin": "external",
  "engines": ["gpt-4o-mini"],
  "count": 1
}
```

**Uso en Frontend**: 
- Función: `filterEnginesByOrigin()` en `api.js:251-274`
- Componente: `App.jsx` (SelectionPage)
- Líneas: `App.jsx:75-87` (en useEffect de filtros, función `applyOriginFilter`)

**Flujo**:
```
Usuario selecciona filtro de origen
  → setFilterOrigin("external")
    → useEffect detecta cambio
      → applyOriginFilter()
        → filterEnginesByOrigin("external")
          → GET /engines/filter/origin/external
            → engine_manager.filter_engines_by_origin(MotorOrigin.EXTERNAL)
              → setFilteredEngines(result.engines)
                → Actualiza selects con motores filtrados
```

**Visualización**: Select de filtro en `App.jsx:121-133`, se combina con filtro de tipo.

---

### 6. `POST /move`

**Ubicación**: `main.py:321-393`

**Descripción**: Obtiene el mejor movimiento de un motor específico para una posición FEN.

**Request Body**:
```json
{
  "engine": "gpt-4o-mini",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "depth": 10,
  "move_history": "e2e4 e7e5",
  "strategy": "balanced",
  "explanation": true
}
```

**Respuesta**:
```json
{
  "engine": "gpt-4o-mini",
  "bestmove": "e2e4",
  "explanation": "Apertura clásica que controla el centro..."
}
```

**Uso en Frontend**: 
- Función: `fetchBestMove()` en `api.js:105-140`
- Componente: `GamePage.jsx`
- Líneas: `GamePage.jsx:69-71` (en función `makeEngineMove`)

**Flujo**:
```
GamePage detecta turno de motor
  → makeEngineMove(engineName)
    → Prepara historial UCI desde game.history()
      → fetchBestMove(engineName, fen, depth, { move_history, strategy, explanation })
        → POST /move
          → engine_manager.get_best_move()
            → Motor calcula mejor movimiento
              → game.move(bestMove)
                → setPosition(game.fen())
                  → Actualiza tablero
```

**Parámetros opcionales**:
- `move_history`: Historial en formato UCI (siempre enviado)
- `strategy`: Estrategia para motores generativos (si está seleccionada en UI)
- `explanation`: Solicitar explicación (si checkbox está marcado)

**Visualización**: 
- Selector de estrategias en `GamePage.jsx:395-410`
- Checkbox de explicación en `GamePage.jsx:412-422`
- Explicación mostrada en `GamePage.jsx:437-448`

---

### 7. `GET /strategies`

**Ubicación**: `main.py:396-420`

**Descripción**: Obtiene la lista de estrategias disponibles para motores generativos.

**Respuesta**:
```json
{
  "strategies": {
    "balanced": {
      "name": "Equilibrado",
      "description": "Equilibrio entre táctica y posición",
      "prompt_hint": "..."
    },
    "aggressive": {
      "name": "Agresivo",
      "description": "Juego agresivo, busca ataque",
      "prompt_hint": "..."
    },
    ...
  },
  "count": 7,
  "default": "balanced"
}
```

**Uso en Frontend**: 
- Función: `fetchStrategies()` en `api.js:280-301`
- Componente: `GamePage.jsx`
- Líneas: `GamePage.jsx:172-180` (useEffect al montar)

**Flujo**:
```
GamePage monta
  → useEffect carga estrategias
    → fetchStrategies()
      → GET /strategies
        → get_valid_strategies() y get_strategy_info()
          → setStrategies(data.strategies)
            → Renderiza select de estrategias
```

**Visualización**: Select dropdown en `GamePage.jsx:395-410` con todas las estrategias disponibles.

---

### 8. `POST /compare`

**Ubicación**: `main.py:423-442`

**Descripción**: Compara las sugerencias de todos los motores disponibles para una posición.

**Request Body**:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "depth": 10
}
```

**Respuesta**:
```json
{
  "fen": "...",
  "results": [
    {
      "engine": "stockfish-local",
      "bestmove": "e2e4",
      "explanation": null
    },
    {
      "engine": "gpt-4o-mini",
      "bestmove": "e2e4",
      "explanation": "Apertura clásica..."
    },
    ...
  ],
  "engines_compared": 5
}
```

**Uso en Frontend**: 
- Función: `compareEngines()` en `api.js:309-339`
- Componente: `ComparePage.jsx`
- Líneas: `ComparePage.jsx:18-28` (función `handleCompare`)

**Flujo**:
```
Usuario en ComparePage hace click en "COMPARAR MOTORES"
  → handleCompare()
    → compareEngines(position, depth)
      → POST /compare
        → engine_manager.compare_engines()
          → Itera sobre todos los motores
            → Cada motor calcula su mejor movimiento
              → setComparisonResults(results)
                → Renderiza tabla con resultados
```

**Visualización**: Tabla de resultados en `ComparePage.jsx:120-135` mostrando motor, movimiento y explicación.

---

### 9. `GET /health`

**Ubicación**: `main.py:192-199`

**Descripción**: Verifica el estado de salud del backend.

**Respuesta**:
```json
{
  "status": "healthy",
  "engines": 5,
  "version": "2.0.0"
}
```

**Uso en Frontend**: 
- Función: `checkBackendHealth()` en `api.js:146-160`
- Componente: `App.jsx` (SelectionPage)
- Líneas: `App.jsx:15-23` (useEffect al montar)

**Flujo**:
```
SelectionPage monta
  → useEffect verifica salud
    → checkBackendHealth()
      → GET /health
        → Respuesta con status, engines, version
          → setBackendHealth(health)
            → Muestra estado en panel superior
```

**Visualización**: Panel de estado en `App.jsx:87-98` muestra "ONLINE", versión y cantidad de motores.

---

### 10. `POST /reload`

**Ubicación**: `main.py:445-465`

**Descripción**: Recarga la configuración de motores desde el archivo YAML sin reiniciar el servidor.

**Respuesta**:
```json
{
  "status": "success",
  "message": "Configuración recargada",
  "engines_loaded": 5
}
```

**Uso en Frontend**: 
- Función: `reloadConfig()` en `api.js:342-365`
- Componente: `App.jsx` (SelectionPage)
- Líneas: `App.jsx:90-98` (función `handleReloadConfig`)

**Flujo**:
```
Usuario hace click en "RECARGAR CONFIG"
  → handleReloadConfig()
    → reloadConfig()
      → POST /reload
        → engine_manager.cleanup_all()
          → engine_manager.reload_config()
            → Recarga desde YAML
              → alert con resultado
                → window.location.reload()
```

**Visualización**: Botón en `App.jsx:211-217`, muestra alerta y recarga la página.

---

### 11. `GET /api`

**Ubicación**: `main.py:171-189`

**Descripción**: Información general de la API y lista de endpoints disponibles.

**Respuesta**:
```json
{
  "message": "Chess Trainer API",
  "version": "2.0.0",
  "engines_loaded": 5,
  "endpoints": {
    "GET /": "...",
    "GET /api": "...",
    ...
  }
}
```

**Estado**: No implementado en frontend (endpoint informativo, no requiere función específica).

---

### 12. `GET /`

**Ubicación**: `main.py:150-168`

**Descripción**: Sirve el HTML del frontend o redirige a desarrollo.

**Estado**: No requiere función en `api.js` (manejo de servidor estático).

---

## Funciones del Frontend

Todas las funciones están ubicadas en `frontend/src/api.js`:

### 1. `getBackendUrl()`
- **Líneas**: `api.js:11-30`
- **Descripción**: Determina la URL del backend según el entorno (desarrollo/producción).
- **Uso**: Todas las funciones API la utilizan internamente.

### 2. `fetchEngines()`
- **Líneas**: `api.js:36-95`
- **Endpoint**: `GET /engines`
- **Uso**: `App.jsx:20`

### 3. `fetchBestMove()`
- **Líneas**: `api.js:105-140`
- **Endpoint**: `POST /move`
- **Uso**: `GamePage.jsx:69`

### 4. `checkBackendHealth()`
- **Líneas**: `api.js:146-160`
- **Endpoint**: `GET /health`
- **Uso**: `App.jsx:16`

### 5. `fetchEnginesInfo()`
- **Líneas**: `api.js:166-187`
- **Endpoint**: `GET /engines/info`
- **Uso**: `App.jsx:48`

### 6. `fetchEnginesMatrix()`
- **Líneas**: `api.js:193-214`
- **Endpoint**: `GET /engines/matrix`
- **Uso**: `EnginesMatrixPage.jsx:12`

### 7. `filterEnginesByType()`
- **Líneas**: `api.js:221-244`
- **Endpoint**: `GET /engines/filter/type/{type}`
- **Uso**: `App.jsx:78`

### 8. `filterEnginesByOrigin()`
- **Líneas**: `api.js:251-274`
- **Endpoint**: `GET /engines/filter/origin/{origin}`
- **Uso**: `App.jsx:89`

### 9. `fetchStrategies()`
- **Líneas**: `api.js:280-301`
- **Endpoint**: `GET /strategies`
- **Uso**: `GamePage.jsx:173`

### 10. `compareEngines()`
- **Líneas**: `api.js:309-339`
- **Endpoint**: `POST /compare`
- **Uso**: `ComparePage.jsx:24`

### 11. `reloadConfig()`
- **Líneas**: `api.js:342-365`
- **Endpoint**: `POST /reload`
- **Uso**: `App.jsx:91`

---

## Flujos de Datos

### Flujo Principal: Selección y Juego

```
1. Usuario abre aplicación (/)
   ↓
2. SelectionPage monta
   ↓
3. useEffect ejecuta:
   - checkBackendHealth() → GET /health
   - Promise.all([
       fetchEngines() → GET /engines,
       fetchEnginesInfo() → GET /engines/info
     ])
   ↓
4. Usuario selecciona filtros (tipo/origen)
   ↓
5. useEffect detecta cambios:
   - filterEnginesByType() → GET /engines/filter/type/{type}
   - filterEnginesByOrigin() → GET /engines/filter/origin/{origin}
   ↓
6. Usuario selecciona motores y hace click en "EMPEZAR PARTIDA"
   ↓
7. Navega a /game con state { selectedEngineA, selectedEngineB }
   ↓
8. GamePage monta
   ↓
9. useEffect carga estrategias:
   - fetchStrategies() → GET /strategies
   ↓
10. useEffect detecta turno de motor:
    - makeEngineMove(engineName)
      - Prepara historial UCI
      - fetchBestMove(engineName, fen, depth, { move_history, strategy?, explanation? })
        → POST /move
      - Aplica movimiento al tablero
   ↓
11. Ciclo continúa hasta fin de partida
```

### Flujo de Comparación

```
1. Usuario navega a /compare
   ↓
2. ComparePage monta
   ↓
3. Usuario ajusta posición (opcional) y profundidad
   ↓
4. Usuario hace click en "COMPARAR MOTORES"
   ↓
5. handleCompare() ejecuta:
   - compareEngines(position, depth)
     → POST /compare
   ↓
6. Backend itera sobre todos los motores:
   - Cada motor calcula su mejor movimiento
   ↓
7. Resultados se muestran en tabla
```

### Flujo de Matriz de Clasificación

```
1. Usuario navega a /matrix
   ↓
2. EnginesMatrixPage monta
   ↓
3. useEffect ejecuta:
   - fetchEnginesMatrix()
     → GET /engines/matrix
   ↓
4. Backend genera matriz:
   - engine_manager.get_classification_matrix()
     → EngineClassifier.generate_classification_matrix()
   ↓
5. Tabla se renderiza con colores por tipo/origen
```

---

## Ubicaciones del Código

### Backend

| Endpoint | Archivo | Líneas |
|----------|---------|--------|
| `GET /engines` | `main.py` | 202-224 |
| `GET /engines/info` | `main.py` | 227-238 |
| `GET /engines/matrix` | `main.py` | 241-260 |
| `GET /engines/filter/type/{type}` | `main.py` | 263-290 |
| `GET /engines/filter/origin/{origin}` | `main.py` | 293-318 |
| `POST /move` | `main.py` | 321-393 |
| `GET /strategies` | `main.py` | 396-420 |
| `POST /compare` | `main.py` | 423-442 |
| `GET /health` | `main.py` | 192-199 |
| `POST /reload` | `main.py` | 445-465 |
| `GET /api` | `main.py` | 171-189 |
| `GET /` | `main.py` | 150-168 |

### Frontend - Funciones API

| Función | Archivo | Líneas |
|---------|---------|--------|
| `getBackendUrl()` | `api.js` | 11-30 |
| `fetchEngines()` | `api.js` | 36-95 |
| `fetchBestMove()` | `api.js` | 105-140 |
| `checkBackendHealth()` | `api.js` | 146-160 |
| `fetchEnginesInfo()` | `api.js` | 166-187 |
| `fetchEnginesMatrix()` | `api.js` | 193-214 |
| `filterEnginesByType()` | `api.js` | 221-244 |
| `filterEnginesByOrigin()` | `api.js` | 251-274 |
| `fetchStrategies()` | `api.js` | 280-301 |
| `compareEngines()` | `api.js` | 309-339 |
| `reloadConfig()` | `api.js` | 342-365 |

### Frontend - Componentes

| Componente | Archivo | APIs Utilizadas |
|------------|---------|-----------------|
| `SelectionPage` | `App.jsx` | `fetchEngines`, `fetchEnginesInfo`, `filterEnginesByType`, `filterEnginesByOrigin`, `checkBackendHealth`, `reloadConfig` |
| `GamePage` | `GamePage.jsx` | `fetchBestMove`, `fetchStrategies` |
| `ComparePage` | `ComparePage.jsx` | `compareEngines` |
| `EnginesMatrixPage` | `EnginesMatrixPage.jsx` | `fetchEnginesMatrix` |

---

## Ejemplos de Uso

### Ejemplo 1: Cargar motores con información detallada

```javascript
// En SelectionPage (App.jsx)
useEffect(() => {
  Promise.all([
    fetchEngines(),
    fetchEnginesInfo()
  ])
    .then(([engines, infoData]) => {
      setAvailableEngines(engines);
      const infoMap = {};
      infoData.engines.forEach(engineInfo => {
        infoMap[engineInfo.name] = engineInfo;
      });
      setEnginesInfo(infoMap);
    });
}, []);
```

### Ejemplo 2: Filtrar motores por tipo y origen

```javascript
// En SelectionPage (App.jsx)
useEffect(() => {
  let filtered = [...availableEngines];
  
  if (filterType !== "all") {
    filterEnginesByType(filterType)
      .then(result => {
        filtered = filtered.filter(engine => result.engines.includes(engine));
        if (filterOrigin !== "all") {
          filterEnginesByOrigin(filterOrigin)
            .then(originResult => {
              filtered = filtered.filter(engine => originResult.engines.includes(engine));
              setFilteredEngines(filtered);
            });
        } else {
          setFilteredEngines(filtered);
        }
      });
  }
}, [filterType, filterOrigin]);
```

### Ejemplo 3: Obtener movimiento con estrategia y explicación

```javascript
// En GamePage (GamePage.jsx)
const makeEngineMove = async (engineName) => {
  const options = {
    move_history: moveHistory
  };
  
  if (selectedStrategy) {
    options.strategy = selectedStrategy;
  }
  
  if (showExplanation) {
    options.explanation = true;
  }
  
  const data = await fetchBestMove(engineName, currentFen, 10, options);
  // data.bestmove contiene el movimiento
  // data.explanation contiene la explicación si se solicitó
};
```

### Ejemplo 4: Comparar todos los motores

```javascript
// En ComparePage (ComparePage.jsx)
const handleCompare = async () => {
  setIsComparing(true);
  try {
    const results = await compareEngines(position, depth);
    // results.results contiene array con movimientos de cada motor
    setComparisonResults(results);
  } catch (err) {
    setError(err.message);
  } finally {
    setIsComparing(false);
  }
};
```

### Ejemplo 5: Recargar configuración

```javascript
// En SelectionPage (App.jsx)
const handleReloadConfig = async () => {
  try {
    const result = await reloadConfig();
    alert(`✅ Configuración recargada. ${result.engines_loaded} motores cargados.`);
    window.location.reload();
  } catch (error) {
    alert(`❌ Error: ${error.message}`);
  }
};
```

---

## Notas de Implementación

### Manejo de Errores

Todas las funciones API incluyen manejo de errores consistente:
- Errores de conexión se detectan y muestran mensajes específicos
- Errores HTTP se capturan y muestran detalles del servidor
- Los componentes muestran estados de carga y error apropiados

### Estados de Carga

Los componentes manejan estados de carga:
- `isLoadingEngines`: Para carga inicial de motores
- `isComparing`: Para comparación de motores
- `isProcessing`: Para movimientos de motores

### Optimizaciones

- `useCallback` y `useMemo` se usan para evitar re-renders innecesarios
- Las funciones API están memoizadas donde es apropiado
- Los filtros se aplican de forma eficiente combinando resultados

---

## Conclusión

Todas las APIs del backend están implementadas y siendo utilizadas en el frontend. El sistema proporciona:

1. **Gestión completa de motores**: Listado, filtrado, información detallada
2. **Juego funcional**: Movimientos con soporte para estrategias y explicaciones
3. **Análisis y comparación**: Comparación de motores y visualización de matriz
4. **Administración**: Recarga de configuración y verificación de salud

El código está bien organizado, documentado y sigue patrones consistentes en todo el proyecto.

