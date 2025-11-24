# 📊 Documentación: Página de Comparación de Motores

## Índice

1. [Resumen General](#resumen-general)
2. [Propósito y Casos de Uso](#propósito-y-casos-de-uso)
3. [Características Implementadas](#características-implementadas)
4. [Arquitectura y Flujo de Datos](#arquitectura-y-flujo-de-datos)
5. [Interfaz de Usuario](#interfaz-de-usuario)
6. [API Backend](#api-backend)
7. [Formato de Datos](#formato-de-datos)
8. [Manejo de Errores](#manejo-de-errores)
9. [Ejemplos de Uso](#ejemplos-de-uso)
10. [Ubicaciones del Código](#ubicaciones-del-código)

---

## Resumen General

La **Página de Comparación de Motores** es una funcionalidad avanzada que permite comparar las sugerencias de todos los motores disponibles para una posición específica del tablero de ajedrez. Esta herramienta es especialmente útil para:

- Analizar posiciones críticas con múltiples enfoques
- Comparar diferentes tipos de motores (tradicionales, neuronales, generativos)
- Entender cómo cada motor evalúa una posición
- Identificar diferencias en las estrategias de los motores

### Estadísticas

- **Componente**: `ComparePage.jsx` (421 líneas)
- **Endpoint Backend**: `POST /compare`
- **Motores soportados**: Todos los tipos (tradicionales, neuronales, generativos)
- **Formato de respuesta**: Array de objetos con engine, bestmove y explanation

---

## Propósito y Casos de Uso

### Casos de Uso Principales

1. **Análisis de Posiciones Críticas**
   - Comparar cómo diferentes motores evalúan posiciones complejas
   - Identificar movimientos candidatos y sus evaluaciones

2. **Comparación de Tipos de Motores**
   - Ver diferencias entre motores tradicionales (Stockfish) y generativos (GPT-4)
   - Entender enfoques diferentes: cálculo vs. razonamiento

3. **Análisis Educativo**
   - Aprender de las explicaciones de motores generativos
   - Comparar evaluaciones técnicas con explicaciones textuales

4. **Validación de Configuración**
   - Verificar que todos los motores están funcionando correctamente
   - Identificar motores con problemas de configuración

---

## Características Implementadas

### ✅ Funcionalidades Principales

#### 1. **Edición Interactiva del Tablero**
- **Movimiento de piezas**: Click o drag & drop
- **Validación de movimientos**: Solo permite movimientos legales según las reglas del ajedrez
- **Resaltado visual**: 
  - Pieza seleccionada (fondo amarillo)
  - Movimientos posibles (círculos amarillos)
  - Jaque al rey (resaltado rojo)

#### 2. **Comparación de Motores**
- Compara **todos los motores disponibles** automáticamente
- Configuración de **profundidad de análisis** (1-30)
- **Manejo robusto de errores**: Los motores que fallan no bloquean la comparación

#### 3. **Visualización de Resultados**
- **Tabla estructurada** con columnas claras:
  - Motor (nombre del motor)
  - Movimiento (en formato UCI)
  - Análisis/Explicación (explicaciones de motores generativos)
- **Indicadores visuales**:
  - Fondo rojizo para motores con errores
  - Explicaciones completas (no truncadas)
- **Filtrado en tiempo real**: Buscar por nombre de motor, movimiento o explicación

#### 4. **Panel de Control**
- Selector de profundidad numérico
- Botón de comparación con estado de carga
- Botón de reset para volver a posición inicial
- Panel de estado mostrando:
  - Modo actual (Edición/Análisis)
  - Turno actual (Blancas/Negras)
  - Posición FEN actual

---

## Arquitectura y Flujo de Datos

### Flujo Completo de Comparación

```
Usuario en ComparePage
  ↓
1. Edita posición en el tablero (opcional)
   - onSquareClick() / onPieceDrop()
   - gameRef.current.move()
   - updatePosition() → setPosition(newFen)
  ↓
2. Configura profundidad (opcional, default: 10)
   - setDepth(value)
  ↓
3. Click en "COMPARAR MOTORES"
   - handleCompare()
   - setIsComparing(true)
   ↓
4. Llamada a API Frontend
   - compareEngines(position, depth)
   - POST /compare
  ↓
5. Procesamiento Backend
   - engine_manager.compare_engines(fen, depth)
   - Itera sobre todos los motores
   - Para cada motor:
     * engine.get_move(fen, depth, explanation=True)
     * Si es generativo: obtiene explicación
     * Si falla: marca como ERROR
  ↓
6. Transformación de Datos
   - Diccionario {engine: move} → Array [{engine, bestmove, explanation}]
   - Incluye explicaciones de motores generativos
  ↓
7. Respuesta al Frontend
   - setComparisonResults(results)
   - setIsComparing(false)
  ↓
8. Renderizado
   - getFilteredResults() procesa resultados
   - Tabla muestra todos los motores comparados
   - Filtrado en tiempo real disponible
```

### Componentes Principales

#### Frontend (`ComparePage.jsx`)

```javascript
// Estados principales
- position: FEN actual del tablero
- isComparing: Estado de carga durante comparación
- comparisonResults: Resultados de la comparación
- selectedSquare: Casilla seleccionada para movimiento
- possibleMoves: Movimientos posibles de la pieza seleccionada
- resultFilter: Filtro de búsqueda en resultados
- depth: Profundidad de análisis configurada

// Funciones clave
- handleCompare(): Inicia la comparación
- getFilteredResults(): Procesa y filtra resultados
- onSquareClick(): Maneja clicks en el tablero
- onPieceDrop(): Maneja drag & drop de piezas
- updatePosition(): Actualiza posición FEN
- resetPosition(): Resetea a posición inicial
```

#### Backend (`main.py` + `engine_manager.py`)

```python
# Endpoint principal
POST /compare
  - Recibe: {fen, depth}
  - Procesa: engine_manager.compare_engines()
  - Devuelve: {fen, results: [...], engines_compared: N}

# Método del gestor
engine_manager.compare_engines(fen, depth)
  - Itera sobre todos los motores
  - Solicita explicaciones automáticamente para generativos
  - Maneja errores individuales sin bloquear
  - Retorna diccionario {engine_name: move}
```

---

## Interfaz de Usuario

### Layout

```
┌─────────────────────────────────────────┐
│     COMPARACIÓN DE MOTORES (Header)     │
├─────────────────────────────────────────┤
│  Panel Superior:                        │
│  - MODO: EDICIÓN / ANALIZANDO...        │
│  - TURNO: BLANCAS / NEGRAS              │
│  - FEN: [posición actual]               │
├──────────────────┬──────────────────────┤
│                  │                      │
│   TABLERO        │  PANEL CONTROL       │
│   (600x600px)    │  - Profundidad       │
│                  │  - COMPARAR          │
│   Interactivo    │  - RESET             │
│   con resaltado  │  - VOLVER            │
│                  │  - Instrucciones     │
│                  │                      │
├──────────────────┴──────────────────────┤
│  PANEL RESULTADOS (si hay resultados)   │
│  ┌────────────────────────────────────┐ │
│  │ [Filtro de búsqueda]               │ │
│  ├────────────────────────────────────┤ │
│  │ MOTOR │ MOVIMIENTO │ EXPLICACIÓN  │ │
│  ├────────────────────────────────────┤ │
│  │ ...   │ ...        │ ...          │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Elementos Visuales

1. **Tablero de Ajedrez**
   - Colores retro: Verde claro (#24a32a) y oscuro (#147e1f)
   - Resaltado de selección: Amarillo semitransparente
   - Resaltado de jaque: Rojo radial

2. **Tabla de Resultados**
   - Estilo retro con fuente VT323
   - Columnas: Motor (25%), Movimiento (15%), Análisis (60%)
   - Scroll vertical si hay muchos resultados
   - Fondo rojizo para errores

3. **Estados de Carga**
   - Botón "COMPARANDO..." durante procesamiento
   - Footer muestra "PROCESSING DATA..."
   - Tablero bloqueado durante comparación

---

## API Backend

### Endpoint: `POST /compare`

**Ubicación**: `main.py:423-442`

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
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "results": [
    {
      "engine": "stockfish-local",
      "bestmove": "e2e4",
      "explanation": null
    },
    {
      "engine": "gpt-4o-mini",
      "bestmove": "e2e4",
      "explanation": "Apertura clásica e4 que controla el centro..."
    },
    {
      "engine": "motor-con-error",
      "bestmove": "ERROR: Connection timeout",
      "explanation": null
    }
  ],
  "engines_compared": 3
}
```

### Características del Endpoint

1. **Procesamiento Asíncrono**
   - Todos los motores se consultan en paralelo
   - No bloquea si un motor falla

2. **Solicitud Automática de Explicaciones**
   - Detecta automáticamente motores generativos
   - Solicita explicaciones cuando están disponibles
   - Incluye explicaciones en la respuesta

3. **Manejo de Errores Individual**
   - Cada motor se procesa independientemente
   - Errores se marcan como `"ERROR: mensaje"`
   - No afecta a otros motores

---

## Formato de Datos

### Estructura de Resultado Individual

```typescript
interface ComparisonResult {
  engine: string;           // Nombre del motor
  bestmove: string;        // Movimiento en formato UCI o "ERROR: ..."
  explanation: string | null; // Explicación (solo motores generativos)
}
```

### Transformación de Datos

El backend devuelve un diccionario `{engine_name: move}`, pero el endpoint lo transforma a un array:

```python
# Backend interno (engine_manager.compare_engines)
results_dict = {
    "stockfish-local": "e2e4",
    "gpt-4o-mini": "e2e4"
}

# Transformación en endpoint /compare
results_array = [
    {"engine": "stockfish-local", "bestmove": "e2e4", "explanation": null},
    {"engine": "gpt-4o-mini", "bestmove": "e2e4", "explanation": "..."}
]
```

### Compatibilidad

El frontend maneja ambos formatos para retrocompatibilidad:
- Si `results` es un array → usa directamente
- Si `results` es un objeto → lo transforma a array

---

## Manejo de Errores

### Errores de Red

```javascript
try {
  const results = await compareEngines(position, depth);
  setComparisonResults(results);
} catch (err) {
  setError(err.message || 'Error desconocido al comparar motores');
  setComparisonResults(null);
}
```

### Errores Individuales de Motores

Los motores que fallan se muestran en la tabla con:
- **bestmove**: `"ERROR: mensaje de error"`
- **isError**: `true` (marcado internamente)
- **Fondo rojizo** en la tabla

### Validación de Respuesta

```javascript
// Validación en handleCompare()
if (!results || typeof results !== 'object') {
  throw new Error('Respuesta inválida del servidor');
}

if (!results.results) {
  throw new Error('La respuesta no contiene resultados');
}
```

---

## Ejemplos de Uso

### Ejemplo 1: Comparación Básica

```javascript
// Usuario en la interfaz:
1. Navega a /compare
2. Deja posición inicial (o edita el tablero)
3. Configura profundidad: 15
4. Click en "COMPARAR MOTORES"
5. Espera resultados (2-10 segundos dependiendo de motores)
6. Ve tabla con todos los motores y sus movimientos
```

### Ejemplo 2: Análisis de Posición Específica

```javascript
// Usuario quiere analizar una posición crítica:
1. Mueve piezas en el tablero para configurar posición
2. Ejemplo: Posición de jaque mate en 2
3. Configura profundidad: 20
4. Compara motores
5. Ve qué motores encuentran el mate y cuáles no
6. Lee explicaciones de motores generativos sobre la posición
```

### Ejemplo 3: Filtrado de Resultados

```javascript
// Usuario quiere ver solo motores generativos:
1. Ejecuta comparación
2. En campo "Filtrar...", escribe "gpt"
3. Tabla muestra solo motores que contienen "gpt" en el nombre
4. Puede filtrar por movimiento: escribe "e2e4"
5. Ve solo motores que sugieren ese movimiento
```

### Ejemplo 4: Uso desde API

```bash
# Comparar motores desde línea de comandos
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 10
  }'

# Respuesta:
{
  "fen": "...",
  "results": [
    {"engine": "stockfish-local", "bestmove": "e2e4", "explanation": null},
    {"engine": "gpt-4o-mini", "bestmove": "e2e4", "explanation": "..."}
  ],
  "engines_compared": 2
}
```

---

## Ubicaciones del Código

### Frontend

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| `frontend/src/ComparePage.jsx` | 1-421 | Componente principal completo |
| `frontend/src/api.js` | 309-339 | Función `compareEngines()` |
| `frontend/src/App.jsx` | 410 | Ruta `/compare` |
| `frontend/src/App.css` | 316-346 | Estilos específicos de comparación |

### Backend

| Archivo | Líneas | Descripción |
|---------|--------|-------------|
| `main.py` | 423-442 | Endpoint `POST /compare` |
| `engine_manager.py` | 184-205 | Método `compare_engines()` |

### Funciones Clave

#### Frontend

```javascript
// ComparePage.jsx
- handleCompare()          // Línea 146-160
- getFilteredResults()     // Línea 171-189
- onSquareClick()          // Línea 60-95
- onPieceDrop()            // Línea 97-115
- updatePosition()         // Línea 45-52
- resetPosition()          // Línea 162-169

// api.js
- compareEngines()          // Línea 309-339
```

#### Backend

```python
# main.py
- compare_engines()         # Línea 423-442 (endpoint)

# engine_manager.py
- compare_engines()         # Línea 184-205 (método)
```

---

## Detalles Técnicos

### Interacción con el Tablero

La página usa `chess.js` para validar movimientos:

```javascript
// Validación de movimiento
const move = game.move({
  from: selectedSquare,
  to: square,
  promotion: 'q'
});

// Si es válido, actualiza posición
if (move) {
  updatePosition(); // Actualiza FEN
}
```

### Resaltado Visual

```javascript
// Estilos personalizados para casillas
customSquareStyles = {
  [selectedSquare]: { backgroundColor: 'rgba(255, 255, 0, 0.4)' },
  [possibleMove]: { 
    background: 'radial-gradient(circle, rgba(255,255,0,0.4) 36%, transparent 40%)'
  }
}
```

### Procesamiento de Resultados

```javascript
// Transformación y filtrado
const getFilteredResults = () => {
  // 1. Convertir diccionario a array si es necesario
  // 2. Identificar errores
  // 3. Aplicar filtro de búsqueda
  // 4. Retornar resultados procesados
}
```

---

## Mejoras Futuras Sugeridas

### Funcionalidades Adicionales

1. **Filtrado de Motores**
   - Seleccionar qué motores comparar (no todos)
   - Filtrar por tipo (tradicional, neuronal, generativo)

2. **Métricas de Rendimiento**
   - Tiempo de cálculo por motor
   - Evaluación numérica (si disponible)
   - Indicadores de confianza

3. **Historial de Comparaciones**
   - Guardar comparaciones anteriores
   - Comparar resultados de diferentes momentos

4. **Exportación de Resultados**
   - Exportar a CSV/JSON
   - Compartir comparaciones

5. **Análisis Avanzado**
   - Comparar múltiples movimientos candidatos
   - Análisis de variantes
   - Gráficos de evaluación

---

## Referencias

- [API_USAGE.md](./API_USAGE.md) - Documentación completa de APIs
- [ARQUITECTURA.md](../architecture/ARQUITECTURA.md) - Arquitectura del sistema
- [EJEMPLO_USO_PROTOCOLOS.md](./EJEMPLO_USO_PROTOCOLOS.md) - Ejemplos de uso de motores

---

**Última actualización**: Diciembre 2024  
**Versión del documento**: 1.0  
**Estado**: ✅ Completo y funcional

