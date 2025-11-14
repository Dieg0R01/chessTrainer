# Arquitectura del Sistema Chess Trainer

## Índice
1. [Visión General](#visión-general)
2. [Ejes de Clasificación](#ejes-de-clasificación)
3. [Matriz de Clasificación](#matriz-de-clasificación)
4. [Arquitectura de Software](#arquitectura-de-software)
5. [Patrones de Diseño](#patrones-de-diseño)
6. [Flujos por Tipo de Motor](#flujos-por-tipo-de-motor)
7. [Guía de Uso](#guía-de-uso)

---

## Visión General

Chess Trainer es un sistema modular para trabajar con diferentes tipos de motores de ajedrez. La arquitectura está diseñada para soportar:

- **Motores tradicionales deterministas** (Stockfish, Komodo)
- **Motores neuronales** (Leela Chess Zero, AlphaZero)
- **Motores generativos** (GPT-4, Claude, LLMs locales)
- **Motores híbridos** (combinaciones de los anteriores - futura implementación)

### Características Principales

- ✅ **Modular**: Cada tipo de motor es un módulo independiente
- ✅ **Extensible**: Añadir nuevos motores sin modificar código base
- ✅ **Tipado**: Sistema de tipos claro con enums y clases base
- ✅ **Async**: Totalmente asíncrono para máxima performance
- ✅ **Validación**: Dos modos (Schema para tradicionales, Prompt para LLMs)
- ✅ **Factory Pattern**: Creación dinámica desde configuración YAML

---

## Ejes de Clasificación

Los motores se organizan según dos dimensiones independientes:

### A. Naturaleza del Motor

#### 1. Motores Tradicionales Deterministas
- **Características**: Minimax, alfa-beta, búsqueda determinista
- **Entrada**: FEN o PGN
- **Salida**: Movimiento en notación UCI
- **Ejemplos**: Stockfish, Komodo, Fruit
- **Predictibilidad**: Alta (misma entrada → misma salida)

#### 2. Motores Neuronales o Híbridos
- **Características**: Redes neuronales + búsqueda (MCTS)
- **Entrada**: FEN o PGN
- **Salida**: Movimiento en notación UCI
- **Ejemplos**: Leela Chess Zero, AlphaZero
- **Recursos**: Pueden requerir GPU

#### 3. Motores Generativos o de Razonamiento Natural
- **Características**: Basados en LLMs, razonamiento en lenguaje natural
- **Entrada**: Prompt contextual con estado del tablero
- **Salida**: Texto con movimiento y razonamiento
- **Ejemplos**: GPT-4 Chess, Claude, modelos locales con LangChain
- **Validación**: Parsing de texto + validación de legalidad
- **Sistema de Estrategias**: Selección automática después de 4 movimientos
  - **Movimientos 0-3**: El prompt no incluye selección de estrategia, el modelo juega de forma equilibrada
  - **Movimientos 4+**: El prompt incluye una lista de estrategias disponibles y pide al modelo que elija una
  - **Estrategia forzada**: Opcionalmente, el usuario puede pasar `strategy` en el request para forzar una estrategia específica

### B. Origen del Servicio

#### 1. Motores Internos
- Contenedores propios (Docker)
- Procesos locales (UCI)
- Modelos locales
- Control total sobre recursos
- Sin límites de uso
- Comunicación rápida (IPC, sockets)

#### 2. Motores Externos
- APIs públicas (Lichess, Chess.com)
- Servicios de IA (OpenAI, Anthropic)
- Servidores remotos con GPU
- Requieren autenticación
- Límites de uso (rate limits)
- Mayor latencia

---

## Matriz de Clasificación

| Tipo de Motor | Ejemplo | Origen | Validación | Interacción |
|---------------|---------|--------|-----------|-------------|
| **Traditional** | Stockfish | Interno | Schema | UCI / Subprocess |
| **Traditional** | Lichess Cloud | Externo | Schema | HTTPS API |
| **Neuronal** | Leela Zero | Interno | Schema | UCI / Docker |
| **Neuronal** | Motor GPU Remoto | Externo | Schema | HTTPS / gRPC |
| **Generative** | GPT-4 Chess | Externo | Prompt | LLM API |
| **Generative** | Modelo Local | Interno | Prompt | HTTP / Pipeline |

---

## Arquitectura de Software

### Estructura de Módulos

```
engines/
├── __init__.py          # Exports públicos
├── base.py              # MotorBase, enums (MotorType, MotorOrigin, ValidationMode)
├── validators.py        # SchemaValidator, PromptValidator
├── traditional.py       # TraditionalUCIEngine, TraditionalRESTEngine
├── neuronal.py          # NeuronalEngine
├── generative.py        # GenerativeEngine
└── factory.py           # EngineFactory, EngineRegistry
```

### Diagrama de Clases

```
┌─────────────────────────────────────────────────┐
│                   MotorBase                     │
│  (Abstract Base Class)                          │
│                                                 │
│  + get_move(board_state, depth, **kwargs)      │
│  + validate_response(response)                  │
│  + initialize()                                 │
│  + cleanup()                                    │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┬──────────────┬───────────────┐
        │                 │              │               │
┌───────▼──────┐  ┌───────▼──────┐  ┌──▼──────────┐  ┌─▼──────────┐
│ Traditional  │  │  Traditional  │  │  Neuronal   │  │ Generative │
│ UCIEngine    │  │  RESTEngine   │  │   Engine    │  │   Engine   │
└──────────────┘  └───────────────┘  └─────────────┘  └────────────┘
     (UCI)             (REST API)      (UCI/REST/gRPC)  (LLM API)
```

### Componentes Principales

#### 1. MotorBase (Base Abstracta)
```python
class MotorBase(ABC):
    - name: str
    - motor_type: MotorType
    - motor_origin: MotorOrigin
    - validation_mode: ValidationMode
    - config: Dict
    
    @abstractmethod
    async def get_move(board_state, depth, **kwargs) -> str
    
    @abstractmethod
    async def validate_response(response) -> bool
```

#### 2. Validadores
- **SchemaValidator**: Regex + validación de legalidad (UCI moves)
- **PromptValidator**: Extracción de movimientos de texto LLM

#### 3. Factory y Registry
- **EngineRegistry**: Registro de tipos de motores disponibles
- **EngineFactory**: Creación dinámica desde configuración YAML

#### 4. EngineManager
- Gestor centralizado
- Carga configuración YAML
- Proporciona acceso unificado a motores
- Métodos de filtrado y clasificación

---

## Patrones de Diseño

### 1. Strategy Pattern
**Dónde**: `MotorBase` y sus implementaciones  
**Por qué**: Encapsular diferentes algoritmos de obtención de movimientos bajo una interfaz común.

```python
# El cliente usa la misma interfaz para todos los motores
engine = engine_manager.get_engine("stockfish")
move = await engine.get_move(fen, depth=20)

engine = engine_manager.get_engine("gpt4-chess")
move = await engine.get_move(fen, strategy="aggressive")
```

### 2. Factory Method / Abstract Factory
**Dónde**: `EngineFactory`  
**Por qué**: Crear motores dinámicamente desde configuración sin hardcodear tipos.

```python
# Crea el motor apropiado basándose en la config
engine = EngineFactory.create_engine(name="stockfish", config={...})
```

### 3. Registry Pattern
**Dónde**: `EngineRegistry`  
**Por qué**: Permitir añadir nuevos tipos de motores sin modificar el código base.

```python
# Registrar un nuevo tipo de motor
EngineRegistry.register("custom_engine", CustomEngineClass)
```

### 4. Adapter Pattern
**Dónde**: `TraditionalRESTEngine`  
**Por qué**: Unificar diferentes APIs externas bajo la interfaz `MotorBase`.

```python
# Adapta Lichess API a nuestra interfaz
lichess_engine = TraditionalRESTEngine(name="lichess", config={
    "url": "https://lichess.org/api/cloud-eval",
    "extract": "$.pvs[0].moves"
})
```

### 5. Template Method
**Dónde**: `MotorBase.initialize()` y `cleanup()`  
**Por qué**: Definir estructura de inicialización/limpieza con hooks para subclases.

```python
async def initialize(self):
    if not self._initialized:
        await self._do_initialize()  # Hook para subclases
        self._initialized = True
```

### 6. Decorator Pattern (Validación)
**Dónde**: `ValidatorFactory`  
**Por qué**: Añadir validación sin modificar los motores.

---

## Flujos por Tipo de Motor

### Flujo 1: Motor Tradicional UCI (Interno)

```
Usuario
  │
  ├─ POST /move (engine=stockfish, fen="...")
  │
  ▼
EngineManager
  │
  ├─ get_engine("stockfish")
  │
  ▼
TraditionalUCIEngine
  │
  ├─ 1. initialize() → Start subprocess
  ├─ 2. Write "position fen ..."
  ├─ 3. Write "go depth 20"
  ├─ 4. Read until "bestmove"
  │
  ▼
SchemaValidator
  │
  ├─ Validar formato UCI (e2e4)
  │
  ▼
Retorno: "e2e4"
```

### Flujo 2: Motor Tradicional REST (Externo)

```
Usuario
  │
  ├─ POST /move (engine=lichess, fen="...")
  │
  ▼
EngineManager
  │
  ├─ get_engine("lichess")
  │
  ▼
TraditionalRESTEngine
  │
  ├─ 1. Formatear params con FEN
  ├─ 2. HTTP GET a Lichess API
  ├─ 3. Extraer con JSONPath ($.pvs[0].moves)
  │
  ▼
SchemaValidator
  │
  ├─ Validar formato UCI
  │
  ▼
Retorno: "e2e4"
```

### Flujo 3: Motor Neuronal (Interno UCI)

```
Usuario
  │
  ├─ POST /move (engine=lc0, fen="...")
  │
  ▼
EngineManager
  │
  ├─ get_engine("lc0")
  │
  ▼
NeuronalEngine
  │
  ├─ 1. initialize() → Start LCZero process
  ├─ 2. Set options (weights, backend=cuda)
  ├─ 3. Write "position fen ..."
  ├─ 4. Write "go nodes 800000"  # Motores neuronales usan nodos
  ├─ 5. Read until "bestmove"
  │
  ▼
SchemaValidator
  │
  ├─ Validar formato UCI
  │
  ▼
Retorno: "e2e4"
```

### Flujo 4: Motor Generativo (Externo LLM)

```
Usuario
  │
  ├─ POST /move (engine=gpt4, fen="...", move_history="1. e4 e5 2. Nf3", explanation=true)
  │
  ▼
EngineManager
  │
  ├─ get_engine("gpt4")
  │
  ▼
GenerativeEngine
  │
  ├─ 1. Contar movimientos desde move_history
  │      → move_count = 4
  │
  ├─ 2. build_prompt(fen, move_history, move_count)
  │      → Si move_count < 4: Prompt simple sin selección de estrategia
  │      → Si move_count >= 4: Prompt con lista de estrategias desde chess_strategies.yaml
  │      → Template Jinja2 renderizado con contexto dinámico
  │      → "Eres un experto en ajedrez. Posición: ...
  │         Ahora que la partida ha avanzado (4 movimientos), elige una estrategia:
  │         - balanced: Equilibrio entre táctica y posición...
  │         - aggressive: Juego agresivo..."
  │
  ├─ 3. call_llm(prompt)
  │      → POST a OpenAI API
  │      → Respuesta: "ESTRATEGIA: aggressive
  │                    MOVIMIENTO: e2e4 porque controla el centro..."
  │
  ├─ 4. parse_output(llm_response, fen)
  │      → PromptValidator.extract_move_from_text()
  │      → "e2e4"
  │
  ▼
PromptValidator
  │
  ├─ Extraer movimiento con regex
  ├─ Validar formato UCI
  ├─ Validar legalidad con python-chess
  │
  ▼
Retorno: "e2e4" + explicación
```

#### Sistema de Estrategias Automático

Los motores generativos implementan un sistema inteligente de selección de estrategias:

**Fase Temprana (Movimientos 0-3)**
- El prompt **no incluye** selección de estrategia
- El modelo juega de forma equilibrada sin instrucciones específicas de estilo
- Permite que el modelo explore la posición sin sesgos estratégicos

**Fase Intermedia (Movimientos 4-9)**
- El prompt **incluye automáticamente** una lista de todas las estrategias disponibles desde `config/chess_strategies.yaml`
- El modelo debe elegir una estrategia y responder en formato:
  ```
  ESTRATEGIA: [nombre de la estrategia]
  MOVIMIENTO: [movimiento en formato UCI]
  ```
- Las estrategias se listan dinámicamente con sus descripciones:
  - `balanced`: Equilibrio entre táctica y posición
  - `aggressive`: Juego agresivo, busca ataque y combinaciones
  - `defensive`: Juego defensivo, prioriza seguridad
  - `tactical`: Enfoque en combinaciones y tácticas
  - `positional`: Enfoque en estructura y planes a largo plazo
  - `material`: Prioriza ganancia de material
  - `king_safety`: Prioriza seguridad del rey

**Fase de Apertura Avanzada (Movimientos 10+)**
- El sistema **detecta automáticamente** la fase de apertura y **asigna una estrategia** según el número de movimientos:
  - **Apertura media** (10-15 movimientos) → Estrategia `positional`: Completa el desarrollo, conecta las torres
  - **Apertura avanzada** (16-21 movimientos) → Estrategia `balanced`: Define planes estratégicos, busca debilidades
  - **Transición al medio juego** (22+ movimientos) → Estrategia `tactical`: Busca tácticas, mejora la posición
- El prompt incluye análisis estructurado de la posición con proceso paso a paso
- Los movimientos legales se agrupan por categoría (capturas, desarrollo, movimientos de rey, otros) para mejor contexto

**Estrategia Forzada (Opcional)**
- Si el usuario pasa `strategy` en el request API, se usa esa estrategia específica
- Útil para forzar un estilo de juego particular independientemente del número de movimientos
- Ejemplo: `POST /move { "engine": "gpt-4o-mini", "fen": "...", "strategy": "aggressive" }`

**Implementación Técnica**
- El conteo de movimientos se realiza automáticamente desde `move_history` (soporta PGN y UCI)
- El template de prompt usa **Jinja2** con lógica condicional:
  - Prioridad: `config/prompt_template.md.jinja` (template mejorado con análisis estructurado)
  - Fallback: `config/prompt_template.jinja` (template básico)
- Las estrategias se cargan dinámicamente desde `config/chess_strategies.yaml`
- La detección de fase de apertura se realiza mediante `_detect_opening_phase()` en `GenerativeEngine`
- El análisis de movimientos legales se realiza mediante `_analyze_legal_moves()` que agrupa por categoría

---

## Guía de Uso

### Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd chessTrainer

# Instalar dependencias
pip install -r requirements.txt

# Configurar motores en config/engines.yaml
# (Añadir API keys para motores externos)
```

### Configuración de Motores

Editar `config/engines.yaml`:

```yaml
engines:
  # Motor tradicional UCI local
  stockfish-local:
    engine_type: traditional_uci
    type: uci
    command: "stockfish"
    default_depth: 15

  # Motor neuronal local
  lc0-local:
    engine_type: neuronal
    protocol: uci
    command: "lc0"
    backend: "cuda"
    search_mode: "nodes"
    default_search_value: 800000

  # Motor generativo (LLM)
  gpt4-chess:
    engine_type: generative
    provider: openai
    model: "gpt-4"
    api_key: "YOUR_API_KEY"
```

### Uso desde Python

```python
from engine_manager import EngineManager

# Inicializar gestor
manager = EngineManager("config/engines.yaml")

# Obtener movimiento de Stockfish
move = await manager.get_best_move("stockfish-local", fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", depth=20)

# Obtener movimiento de LLM (selección automática de estrategia después de 4 movimientos)
move = await manager.get_best_move(
    "gpt4-chess",
    fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    move_history="1. e4 e5 2. Nf3 Nc6 3. Bb5 a6",  # 4 movimientos → modelo elegirá estrategia
    explanation=True
)

# O forzar una estrategia específica (opcional)
move = await manager.get_best_move(
    "gpt4-chess",
    fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    strategy="aggressive",  # Fuerza estrategia agresiva
    explanation=True
)
```

### Uso desde API REST

```bash
# Iniciar servidor
python main.py

# Listar motores
curl http://localhost:8000/engines

# Obtener movimiento
curl -X POST http://localhost:8000/move \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "stockfish-local",
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 20
  }'

# Comparar motores
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 15
  }'
```

### Añadir un Nuevo Motor

1. **Crear clase del motor** (si es tipo nuevo):
```python
# En engines/custom.py
from engines.base import MotorBase, MotorType, MotorOrigin, ValidationMode

class CustomEngine(MotorBase):
    async def get_move(self, board_state, depth, **kwargs):
        # Tu lógica aquí
        pass
    
    async def validate_response(self, response):
        # Tu validación aquí
        pass
```

2. **Registrar en Factory**:
```python
# En engines/factory.py
from .custom import CustomEngine
EngineRegistry.register("custom", CustomEngine)
```

3. **Añadir a configuración**:
```yaml
# En config/engines.yaml
my-custom-engine:
  engine_type: custom
  # ... tus parámetros
```

4. **Recargar**:
```bash
curl -X POST http://localhost:8000/reload
```

---

## API Endpoints

### GET /
Información general de la API

### GET /engines
Lista de motores disponibles

### GET /engines/info
Información detallada de todos los motores

### GET /engines/matrix
Matriz de clasificación (tipo × origen)

### GET /engines/filter/type/{type}
Filtrar por tipo (traditional, neuronal, generative)

### GET /engines/filter/origin/{origin}
Filtrar por origen (internal, external)

### POST /move
Obtener mejor movimiento de un motor
```json
{
  "engine": "stockfish-local",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "depth": 20,
  "strategy": "aggressive",  // Opcional: fuerza estrategia específica (si no se pasa, el modelo elegirá automáticamente después de 4 movimientos)
  "explanation": true         // Opcional para motores generativos
}
```

### POST /compare
Comparar todos los motores disponibles

### POST /reload
Recargar configuración sin reiniciar servidor

---

## Próximos Pasos

1. ✅ **Arquitectura base implementada**
2. ⏳ **Testing unitario de cada motor**
3. ⏳ **Implementar motores híbridos** (ver `motores_hibridos.md`)
4. ⏳ **Integración con LangGraph para agentes**
5. ⏳ **Dashboard web para visualización**
6. ⏳ **Sistema de análisis de partidas completas**

---

**Documento**: ARQUITECTURA.md  
**Versión**: 2.0.0  
**Fecha**: 2025  
**Autor**: Chess Trainer Team



