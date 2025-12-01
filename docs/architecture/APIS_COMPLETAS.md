# 📡 Documentación Completa de APIs - Chess Trainer

Este documento describe **todas las APIs** utilizadas en el proyecto Chess Trainer, incluyendo:

1. **API REST del Backend** (FastAPI)
2. **API del Frontend** (JavaScript/React)
3. **Protocolos de Motores** (UCI, REST, LocalLLM, APILLM)
4. **APIs Externas** (OpenAI, Anthropic, Lichess, etc.)

---

## 🎯 Índice

- [1. API REST del Backend](#1-api-rest-del-backend-fastapi)
- [2. API del Frontend](#2-api-del-frontend-javascript)
- [3. Protocolos de Motores](#3-protocolos-de-motores)
- [4. APIs Externas](#4-apis-externas)

---

## 1. API REST del Backend (FastAPI)

Base URL: `http://localhost:8000` (desarrollo) o según configuración de producción.

### 1.1. Endpoints de Información

#### `GET /`
**Descripción**: Información general de la API y redirección al frontend.

**Respuesta**:
- Si existe `frontend/dist`: sirve el HTML de producción
- Si no: redirige a `http://localhost:5173` (desarrollo)

**Ejemplo**:
```bash
curl http://localhost:8000/
```

---

#### `GET /api`
**Descripción**: Información básica de la API.

**Respuesta**:
```json
{
  "message": "Chess Trainer API",
  "version": "2.0.0"
}
```

**Ejemplo**:
```bash
curl http://localhost:8000/api
```

---

#### `GET /health`
**Descripción**: Health check del backend.

**Respuesta**:
```json
{
  "status": "healthy",
  "engines": 10,
  "version": "2.0.0"
}
```

**Campos**:
- `status`: Estado del servidor (`"healthy"` o `"unhealthy"`)
- `engines`: Número de motores cargados
- `version`: Versión del backend

**Ejemplo**:
```bash
curl http://localhost:8000/health
```

---

#### `GET /engines`
**Descripción**: Lista de nombres de motores disponibles.

**Respuesta**:
```json
{
  "engines": ["stockfish-local", "lc0-local", "gpt-4o-mini", ...],
  "count": 10
}
```

**Ejemplo**:
```bash
curl http://localhost:8000/engines
```

---

#### `GET /engines/info`
**Descripción**: Información detallada de todos los motores.

**Respuesta**:
```json
{
  "engines": [
    {
      "name": "stockfish-local",
      "type": "traditional",
      "origin": "internal",
      "validation_mode": "schema",
      "initialized": true,
      "available": true
    },
    ...
  ],
  "count": 10
}
```

**Campos por motor**:
- `name`: Nombre del motor
- `type`: Tipo (`"traditional"`, `"neuronal"`, `"generative"`)
- `origin`: Origen (`"internal"`, `"external"`)
- `validation_mode`: Modo de validación (`"schema"`, `"prompt"`)
- `initialized`: Si el motor está inicializado
- `available`: Si el motor está disponible (verificado al arranque)

**Ejemplo**:
```bash
curl http://localhost:8000/engines/info
```

---

#### `GET /engines/matrix`
**Descripción**: Matriz de clasificación de motores por tipo, origen y modo de validación.

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
  "count": 10,
  "description": {
    "type": ["traditional", "neuronal", "generative"],
    "origin": ["internal", "external"],
    "validation_mode": ["schema", "prompt"]
  }
}
```

**Ejemplo**:
```bash
curl http://localhost:8000/engines/matrix
```

---

### 1.2. Endpoints de Filtrado

#### `GET /engines/filter/type/{motor_type}`
**Descripción**: Filtra motores por tipo.

**Parámetros**:
- `motor_type` (path): `"traditional"`, `"neuronal"`, o `"generative"`

**Respuesta**:
```json
{
  "type": "traditional",
  "engines": ["stockfish-local", "lichess-cloud"],
  "count": 2
}
```

**Ejemplo**:
```bash
curl http://localhost:8000/engines/filter/type/traditional
```

---

#### `GET /engines/filter/origin/{motor_origin}`
**Descripción**: Filtra motores por origen.

**Parámetros**:
- `motor_origin` (path): `"internal"` o `"external"`

**Respuesta**:
```json
{
  "origin": "internal",
  "engines": ["stockfish-local", "lc0-local", "maia-1500"],
  "count": 3
}
```

**Ejemplo**:
```bash
curl http://localhost:8000/engines/filter/origin/internal
```

---

### 1.3. Endpoints de Operación

#### `POST /move`
**Descripción**: Obtiene el mejor movimiento de un motor para una posición.

**Request Body**:
```json
{
  "engine": "stockfish-local",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "depth": 15,
  "move_history": "e2e4 e7e5",
  "strategy": "balanced",
  "explanation": true
}
```

**Campos**:
- `engine` (requerido): Nombre del motor
- `fen` (requerido): Posición en formato FEN
- `depth` (opcional): Profundidad de análisis (default: según motor)
- `move_history` (opcional): Historial de movimientos en formato UCI (para motores generativos)
- `strategy` (opcional): Estrategia para motores generativos (`"balanced"`, `"tactical"`, `"positional"`, etc.)
- `explanation` (opcional): Si se solicita explicación (solo motores generativos)

**Respuesta**:
```json
{
  "engine": "stockfish-local",
  "bestmove": "e2e4",
  "explanation": null
}
```

**Para motores generativos con explicación**:
```json
{
  "engine": "gpt-4o-mini",
  "bestmove": "e2e4",
  "explanation": "Este movimiento controla el centro y permite desarrollar las piezas..."
}
```

**Errores**:
- `404`: Motor no encontrado
- `500`: Error interno del servidor

**Ejemplo**:
```bash
curl -X POST http://localhost:8000/move \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "stockfish-local",
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 15
  }'
```

---

#### `POST /compare`
**Descripción**: Compara las sugerencias de todos los motores disponibles para una posición.

**Request Body**:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "depth": 10
}
```

**Campos**:
- `fen` (requerido): Posición en formato FEN
- `depth` (opcional): Profundidad de análisis

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
      "engine": "lc0-local",
      "bestmove": "d2d4",
      "explanation": null
    },
    {
      "engine": "gpt-4o-mini",
      "bestmove": "e2e4",
      "explanation": "Este movimiento controla el centro..."
    },
    ...
  ],
  "engines_compared": 10
}
```

**Notas**:
- Los motores no disponibles aparecen con `"bestmove": "NO DISPONIBLE"`
- Las explicaciones solo están disponibles para motores generativos
- Los errores individuales no bloquean la comparación

**Ejemplo**:
```bash
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 10
  }'
```

---

#### `GET /strategies`
**Descripción**: Obtiene la lista de estrategias disponibles para motores generativos.

**Respuesta**:
```json
{
  "strategies": {
    "balanced": {
      "name": "Balanced",
      "description": "Estrategia equilibrada entre táctica y posición",
      "prompt_hint": "Considera tanto aspectos tácticos como posicionales"
    },
    "tactical": {
      "name": "Tactical",
      "description": "Enfocado en combinaciones y tácticas",
      "prompt_hint": "Prioriza combinaciones y tácticas"
    },
    ...
  },
  "count": 7,
  "default": "balanced"
}
```

**Ejemplo**:
```bash
curl http://localhost:8000/strategies
```

---

#### `POST /reload`
**Descripción**: Recarga la configuración de motores desde los archivos YAML.

**Respuesta**:
```json
{
  "status": "success",
  "message": "Configuración recargada",
  "engines_loaded": 10
}
```

**Notas**:
- Limpia todos los motores actuales
- Recarga desde `config/engines_local.yaml` y `config/engines_external.yaml`
- Verifica disponibilidad de motores en background
- Útil para añadir/modificar motores sin reiniciar el servidor

**Ejemplo**:
```bash
curl -X POST http://localhost:8000/reload
```

---

## 2. API del Frontend (JavaScript)

Módulo: `frontend/src/api.js`

Base URL: Detectada automáticamente según entorno (desarrollo: `http://localhost:8000`).

### 2.1. Funciones de Utilidad

#### `getBackendUrl()`
**Descripción**: Obtiene la URL base del backend.

**Retorna**: `string` - URL del backend

**Lógica**:
- En desarrollo: siempre `http://localhost:8000`
- En producción: mismo hostname pero puerto 8000

---

### 2.2. Funciones de Información

#### `fetchEngines()`
**Descripción**: Obtiene la lista de nombres de motores disponibles.

**Retorna**: `Promise<string[]>` - Array de nombres de motores

**Ejemplo**:
```javascript
const engines = await fetchEngines();
console.log(engines); // ["stockfish-local", "lc0-local", ...]
```

---

#### `fetchEnginesInfo()`
**Descripción**: Obtiene información detallada de todos los motores.

**Retorna**: `Promise<{engines: Array<EngineInfo>, count: number}>`

**Ejemplo**:
```javascript
const info = await fetchEnginesInfo();
console.log(info.engines[0]);
// {
//   name: "stockfish-local",
//   type: "traditional",
//   origin: "internal",
//   validation_mode: "schema",
//   initialized: true,
//   available: true
// }
```

---

#### `fetchEnginesMatrix()`
**Descripción**: Obtiene la matriz de clasificación de motores.

**Retorna**: `Promise<{matrix: Array, count: number, description: Object}>`

**Ejemplo**:
```javascript
const matrix = await fetchEnginesMatrix();
console.log(matrix.matrix);
```

---

#### `checkBackendHealth()`
**Descripción**: Verifica la salud del backend.

**Retorna**: `Promise<{status: string, engines: number, version: string}>`

**Ejemplo**:
```javascript
const health = await checkBackendHealth();
console.log(health.status); // "healthy"
```

---

### 2.3. Funciones de Filtrado

#### `filterEnginesByType(motorType)`
**Descripción**: Filtra motores por tipo.

**Parámetros**:
- `motorType` (string): `"traditional"`, `"neuronal"`, o `"generative"`

**Retorna**: `Promise<{type: string, engines: string[], count: number}>`

**Ejemplo**:
```javascript
const result = await filterEnginesByType("traditional");
console.log(result.engines); // ["stockfish-local", "lichess-cloud"]
```

---

#### `filterEnginesByOrigin(motorOrigin)`
**Descripción**: Filtra motores por origen.

**Parámetros**:
- `motorOrigin` (string): `"internal"` o `"external"`

**Retorna**: `Promise<{origin: string, engines: string[], count: number}>`

**Ejemplo**:
```javascript
const result = await filterEnginesByOrigin("internal");
console.log(result.engines); // ["stockfish-local", "lc0-local", ...]
```

---

### 2.4. Funciones de Operación

#### `fetchBestMove(engineName, fen, depth, options)`
**Descripción**: Obtiene el mejor movimiento de un motor.

**Parámetros**:
- `engineName` (string): Nombre del motor
- `fen` (string): Posición en formato FEN
- `depth` (number, opcional): Profundidad de análisis (default: 10)
- `options` (object, opcional): Opciones adicionales
  - `move_history` (string): Historial de movimientos UCI
  - `strategy` (string): Estrategia para motores generativos
  - `explanation` (boolean): Si se solicita explicación

**Retorna**: `Promise<{engine: string, bestmove: string, explanation?: string}>`

**Ejemplo**:
```javascript
const result = await fetchBestMove(
  "stockfish-local",
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  15
);
console.log(result.bestmove); // "e2e4"
```

---

#### `compareEngines(fen, depth)`
**Descripción**: Compara las sugerencias de todos los motores.

**Parámetros**:
- `fen` (string): Posición en formato FEN
- `depth` (number, opcional): Profundidad de análisis

**Retorna**: `Promise<{fen: string, results: Array, engines_compared: number}>`

**Ejemplo**:
```javascript
const result = await compareEngines(
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  10
);
console.log(result.results);
```

---

#### `fetchStrategies()`
**Descripción**: Obtiene la lista de estrategias disponibles.

**Retorna**: `Promise<{strategies: Object, count: number, default: string}>`

**Ejemplo**:
```javascript
const strategies = await fetchStrategies();
console.log(strategies.strategies);
```

---

#### `reloadConfig()`
**Descripción**: Recarga la configuración de motores.

**Retorna**: `Promise<{status: string, message: string, engines_loaded: number}>`

**Ejemplo**:
```javascript
const result = await reloadConfig();
console.log(result.engines_loaded); // 10
```

---

## 3. Protocolos de Motores

Los protocolos son interfaces de comunicación entre el sistema y los motores de ajedrez. Implementan el patrón Bridge para separar lógica de negocio de comunicación.

### 3.1. ProtocolBase (Interfaz Común)

**Archivo**: `engines/protocols/base.py`

**Métodos abstractos**:

#### `async initialize() -> None`
Inicializa el protocolo de comunicación.

#### `async send_position(fen: str) -> None`
Envía la posición del tablero al motor.

**Parámetros**:
- `fen` (string): Posición en formato FEN

#### `async request_move(depth: Optional[int] = None, **kwargs) -> str`
Solicita el mejor movimiento al motor.

**Parámetros**:
- `depth` (int, opcional): Profundidad de análisis
- `**kwargs`: Parámetros adicionales específicos del protocolo

**Retorna**: `str` - Movimiento en formato UCI

#### `async cleanup() -> None`
Limpia recursos utilizados por el protocolo.

#### `async check_availability() -> bool`
Verifica si el protocolo puede funcionar con la configuración actual.

**Retorna**: `bool` - `True` si está disponible, `False` en caso contrario

---

### 3.2. UCIProtocol

**Archivo**: `engines/protocols/uci.py`

**Descripción**: Protocolo UCI (Universal Chess Interface) para motores locales.

**Configuración requerida**:
```yaml
command: "stockfish"  # Ejecutable del motor
```

**Configuración opcional**:
```yaml
weights: "weights/network.pb.gz"  # Para motores neuronales (Lc0)
backend: "blas"  # Backend para motores neuronales
threads: 2  # Número de threads
hash: 64  # Tamaño de hash en MB
```

**Flujo de comunicación**:

1. **Inicialización**:
   ```
   uci → uciok
   setoption name ... value ...
   isready → readyok
   ```

2. **Envío de posición**:
   ```
   position fen <fen>
   ```

3. **Solicitud de movimiento**:
   ```
   go depth <depth>  # o go nodes <nodes>, go movetime <ms>
   → bestmove <move>
   ```

4. **Limpieza**:
   ```
   quit
   ```

**Timeouts**:
- Lectura de respuestas: 10s por defecto
- Obtención de bestmove: 30s

**Verificación de disponibilidad**:
- Comprueba si el ejecutable existe y tiene permisos de ejecución
- Busca en PATH si no es ruta absoluta

---

### 3.3. RESTProtocol

**Archivo**: `engines/protocols/rest.py`

**Descripción**: Protocolo HTTP REST para motores remotos o APIs.

**Configuración requerida**:
```yaml
url: "https://api.example.com/move"
```

**Configuración opcional**:
```yaml
method: "POST"  # GET o POST (default: POST)
timeout: 30.0  # Timeout en segundos
extract: "$.bestmove"  # JSONPath para extraer movimiento
api_key: "YOUR_API_KEY"  # O desde variable de entorno
```

**Flujo de comunicación**:

1. **Inicialización**: Verifica disponibilidad del endpoint

2. **Envío de posición**:
   ```http
   POST https://api.example.com/move
   Content-Type: application/json
   
   {
     "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
     "depth": 15
   }
   ```

3. **Solicitud de movimiento**: Mismo request que envío de posición

4. **Respuesta**:
   ```json
   {
     "bestmove": "e2e4"
   }
   ```

**Verificación de disponibilidad**:
- Valida formato de URL
- Si es localhost: intenta ping rápido (timeout 1s)
- Si es remoto: solo valida configuración (no hace llamadas costosas)

---

### 3.4. LocalLLMProtocol

**Archivo**: `engines/protocols/local_llm.py`

**Descripción**: Protocolo para LLMs locales (Ollama, LM Studio, LocalAI, etc.).

**Configuración requerida**:
```yaml
endpoint: "http://localhost:8080"
```

**Configuración opcional**:
```yaml
timeout: 60.0  # Timeout en segundos (default: 60)
model_path: "/path/to/model"  # Ruta al modelo (si aplica)
```

**Flujo de comunicación**:

1. **Inicialización**: Verifica disponibilidad del endpoint

2. **Envío de posición y solicitud de movimiento**:
   ```http
   POST http://localhost:8080/v1/chat/completions
   Content-Type: application/json
   
   {
     "model": "llama2",
     "messages": [
       {
         "role": "system",
         "content": "Eres un experto en ajedrez..."
       },
       {
         "role": "user",
         "content": "Posición FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\n\nMejor movimiento?"
       }
     ],
     "temperature": 0.3
   }
   ```

3. **Respuesta**:
   ```json
   {
     "choices": [{
       "message": {
         "content": "El mejor movimiento es e2e4..."
       }
     }]
   }
   ```

**Verificación de disponibilidad**:
- Intenta endpoints comunes: `/health`, `/version`, `/api/version`, `/v1/models`
- Si responde (incluso con error HTTP), considera disponible

---

### 3.5. APILLMProtocol

**Archivo**: `engines/protocols/api_llm.py`

**Descripción**: Protocolo para APIs de LLMs externos (OpenAI, Anthropic, Cohere, etc.).

**Configuración requerida**:
```yaml
provider: "openai"  # openai, anthropic, cohere, etc.
model: "gpt-4o-mini"
api_url: "https://api.openai.com/v1/chat/completions"
api_key: "YOUR_API_KEY"  # O desde variable de entorno
```

**Configuración opcional**:
```yaml
timeout: 60.0  # Timeout en segundos (default: 60)
temperature: 0.3  # Temperatura para generación
max_tokens: 500  # Máximo de tokens
```

**Flujo de comunicación**:

1. **Inicialización**: Valida URL y presencia de API key

2. **Envío de posición y solicitud de movimiento**:
   ```http
   POST https://api.openai.com/v1/chat/completions
   Authorization: Bearer sk-...
   Content-Type: application/json
   
   {
     "model": "gpt-4o-mini",
     "messages": [
       {
         "role": "system",
         "content": "Eres un experto en ajedrez..."
       },
       {
         "role": "user",
         "content": "Posición FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\n\nMejor movimiento?"
       }
     ],
     "temperature": 0.3,
     "max_tokens": 500
   }
   ```

3. **Respuesta**:
   ```json
   {
     "choices": [{
       "message": {
         "content": "El mejor movimiento es e2e4..."
       }
     }]
   }
   ```

**Verificación de disponibilidad**:
- Valida formato de URL
- Verifica presencia de API key (no hace llamadas costosas)

**Proveedores soportados**:
- OpenAI (`openai`)
- Anthropic (`anthropic`)
- Cohere (`cohere`)
- Otros compatibles con formato OpenAI

---

## 4. APIs Externas

### 4.1. Lichess Cloud API

**Tipo**: REST

**Endpoint**: `https://lichess.org/api/cloud-eval`

**Uso en Chess Trainer**:
- Motor: `lichess-cloud`
- Protocolo: `RESTProtocol`
- Configuración:
  ```yaml
  url: "https://lichess.org/api/cloud-eval"
  method: "POST"
  extract: "$.pvs[0].moves"
  ```

**Request**:
```http
POST https://lichess.org/api/cloud-eval
Content-Type: application/json

{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "multiPv": 1,
  "depth": 15
}
```

**Response**:
```json
{
  "pvs": [{
    "moves": "e2e4",
    "cp": 20,
    "depth": 15
  }]
}
```

---

### 4.2. OpenAI API

**Tipo**: REST (Chat Completions)

**Endpoint**: `https://api.openai.com/v1/chat/completions`

**Uso en Chess Trainer**:
- Motores: `gpt-4o-mini`, `gpt-3.5-turbo`, etc.
- Protocolo: `APILLMProtocol`
- Configuración:
  ```yaml
  provider: "openai"
  model: "gpt-4o-mini"
  api_url: "https://api.openai.com/v1/chat/completions"
  api_key: "${OPENAI_API_KEY}"  # Desde variable de entorno
  ```

**Autenticación**: Bearer token (`Authorization: Bearer sk-...`)

**Request**:
```http
POST https://api.openai.com/v1/chat/completions
Authorization: Bearer sk-...
Content-Type: application/json

{
  "model": "gpt-4o-mini",
  "messages": [...],
  "temperature": 0.3,
  "max_tokens": 500
}
```

**Response**:
```json
{
  "choices": [{
    "message": {
      "content": "El mejor movimiento es e2e4..."
    }
  }]
}
```

---

### 4.3. Anthropic API

**Tipo**: REST (Messages API)

**Endpoint**: `https://api.anthropic.com/v1/messages`

**Uso en Chess Trainer**:
- Motores: `claude-3-opus`, `claude-3-sonnet`, etc.
- Protocolo: `APILLMProtocol`
- Configuración:
  ```yaml
  provider: "anthropic"
  model: "claude-3-opus-20240229"
  api_url: "https://api.anthropic.com/v1/messages"
  api_key: "${ANTHROPIC_API_KEY}"  # Desde variable de entorno
  ```

**Autenticación**: Bearer token (`x-api-key: sk-ant-...`)

**Request**:
```http
POST https://api.anthropic.com/v1/messages
x-api-key: sk-ant-...
anthropic-version: 2023-06-01
Content-Type: application/json

{
  "model": "claude-3-opus-20240229",
  "max_tokens": 500,
  "messages": [...]
}
```

---

### 4.4. Ollama (Local LLM)

**Tipo**: REST (Local)

**Endpoint**: `http://localhost:11434/api/generate` o `http://localhost:11434/api/chat`

**Uso en Chess Trainer**:
- Motor: `ollama-llama2` (ejemplo)
- Protocolo: `LocalLLMProtocol`
- Configuración:
  ```yaml
  endpoint: "http://localhost:11434"
  ```

**Request** (Chat):
```http
POST http://localhost:11434/api/chat
Content-Type: application/json

{
  "model": "llama2",
  "messages": [...],
  "stream": false
}
```

---

## 📚 Referencias

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **UCI Protocol**: https://www.chessprogramming.org/UCI
- **OpenAI API**: https://platform.openai.com/docs/api-reference
- **Anthropic API**: https://docs.anthropic.com/claude/reference
- **Ollama**: https://ollama.ai/

---

**Última actualización**: Diciembre 2024  
**Versión del documento**: 1.0.0

