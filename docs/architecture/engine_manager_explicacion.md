# 📊 Documentación del Engine Manager

## 🎯 Resumen Ejecutivo

El **Engine Manager** es un sistema flexible y extensible para gestionar diferentes tipos de motores de ajedrez (locales y remotos) bajo una interfaz común, utilizando patrones de diseño modernos.

---

## 🏗️ Arquitectura del Sistema

![Diagrama de Arquitectura](engine_manager_architecture.png)

El diagrama generado con [Diagrams](https://diagrams.mingrammer.com/) muestra la arquitectura completa del sistema.

---

## 📚 Componentes Principales

### 1. **EngineInterface** (Interfaz Abstracta)

```python
class EngineInterface(ABC):
    @abstractmethod
    def get_best_move(self, fen: str, depth: int) -> str:
        pass
```

**Propósito**: Define el contrato que todos los adaptadores de motores deben cumplir.

**Teoría**:
- Usa el patrón **Abstract Base Class (ABC)** de Python
- Garantiza que todas las implementaciones tengan el método `get_best_move()`
- Permite **polimorfismo**: diferentes motores pueden usarse intercambiablemente

**Parámetros**:
- `fen` (str): Notación FEN del tablero (ej: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
- `depth` (int): Profundidad de análisis del motor (niveles de búsqueda)
- **Retorna**: Movimiento en notación algebraica estándar (ej: "e2e4")

---

### 2. **UciEngineAdapter** (Adaptador UCI)

```python
class UciEngineAdapter(EngineInterface):
    def __init__(self, config: dict):
        self.command = config["command"]
        self.process = None
```

**Propósito**: Adapta motores que usan el protocolo **UCI (Universal Chess Interface)**, como Stockfish, Komodo, etc.

#### 🔧 Funcionamiento Técnico

**Protocolo UCI**:
```
→ uci                      # Inicializar motor
← id name Stockfish 16     # Identificación
← uciok                    # Motor listo
→ isready                  # ¿Estás listo?
← readyok                  # Sí, listo
→ position fen <fen>       # Establecer posición
→ go depth 20              # Calcular mejor movimiento
← info depth 1 score cp 25 # Información de búsqueda
← bestmove e2e4            # Mejor movimiento encontrado
```

**Métodos Clave**:

1. **`_start_engine()`**
   - Inicia el subproceso del motor usando `asyncio.create_subprocess_exec()`
   - Configura comunicación por stdin/stdout
   - Espera confirmación de inicialización (`uciok`, `readyok`)

2. **`_write_command(command: str)`**
   - Escribe comandos al motor a través de stdin
   - Usa `drain()` para asegurar que los datos se envíen

3. **`_read_until(expected_output: str)`**
   - Lee líneas del stdout hasta encontrar la salida esperada
   - Maneja el protocolo asíncrono del motor

4. **`get_best_move(fen: str, depth: int)`**
   - Verifica que el motor esté activo (lo reinicia si es necesario)
   - Envía la posición FEN
   - Solicita análisis con profundidad específica
   - Espera y extrae el movimiento de la respuesta `bestmove`

**Ventajas**:
- ✅ **Rendimiento**: Motores locales son muy rápidos (sin latencia de red)
- ✅ **Control**: Análisis profundo sin límites de API
- ✅ **Privacidad**: Las partidas no salen del sistema local
- ✅ **Gratuito**: No requiere suscripciones o API keys

---

### 3. **RestEngineAdapter** (Adaptador REST)

```python
class RestEngineAdapter(EngineInterface):
    def __init__(self, config: dict):
        self.method = config["method"]
        self.url = config["url"]
        self.params_template = config.get("params", {})
        self.extract_path = config["extract"]
```

**Propósito**: Adapta motores accesibles vía **APIs REST** (Lichess API, Chess.com, servicios cloud, etc.)

#### 🌐 Funcionamiento Técnico

**Flujo de Comunicación**:
```
1. Aplicación solicita movimiento
   ↓
2. Adapter formatea parámetros (fen, depth)
   ↓
3. Envía petición HTTP (GET/POST)
   ↓
4. Recibe respuesta JSON
   ↓
5. Extrae movimiento usando JSONPath
   ↓
6. Devuelve movimiento a la aplicación
```

**Ejemplo de Configuración**:
```yaml
lichess_api:
  type: rest
  method: GET
  url: https://lichess.org/api/cloud-eval
  params:
    fen: "{fen}"
    multiPv: 1
  extract: "$.pvs[0].moves"
```

**Ejemplo de Respuesta JSON**:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "knodes": 50000,
  "depth": 20,
  "pvs": [
    {
      "moves": "e2e4",
      "cp": 25
    }
  ]
}
```

**JSONPath**: `$.pvs[0].moves` extrae `"e2e4"`

**Métodos Clave**:

1. **`get_best_move(fen: str, depth: int)`**
   - Formatea parámetros usando plantillas: `"{fen}".format(fen=fen_actual)`
   - Crea cliente HTTP asíncrono con `httpx.AsyncClient()`
   - Envía petición (GET o POST según configuración)
   - Valida respuesta con `raise_for_status()`
   - Extrae datos usando `jsonpath`
   - Retorna el movimiento

**Ventajas**:
- ✅ **Acceso a motores potentes**: Servidores con hardware especializado
- ✅ **Sin instalación local**: No requiere motores en el sistema
- ✅ **Escalabilidad**: Múltiples servicios en paralelo
- ✅ **Actualizaciones automáticas**: Los servicios se mantienen actualizados

**Desventajas**:
- ⚠️ Latencia de red
- ⚠️ Límites de rate (peticiones por minuto)
- ⚠️ Dependencia de servicios externos

---

### 4. **EngineManager** (Gestor/Fábrica)

```python
class EngineManager:
    def __init__(self, config_path: str = "config/engines.yaml"):
        self.engines = {}
        self.load_config(config_path)
```

**Propósito**: Gestiona el ciclo de vida de los motores y actúa como fábrica para crearlos.

#### 🏭 Patrón Factory

**Flujo de Inicialización**:
```
1. Lee config/engines.yaml
   ↓
2. Por cada motor configurado:
   - Determina el tipo (uci o rest)
   - Crea instancia del adaptador apropiado
   - Almacena en diccionario engines
   ↓
3. Proporciona método get_engine(name)
```

**Ejemplo de Configuración (engines.yaml)**:
```yaml
engines:
  stockfish:
    type: uci
    command: /usr/local/bin/stockfish
  
  lichess:
    type: rest
    method: GET
    url: https://lichess.org/api/cloud-eval
    params:
      fen: "{fen}"
      multiPv: 1
    extract: "$.pvs[0].moves"
  
  local_api:
    type: rest
    method: POST
    url: http://localhost:5000/analyze
    params:
      position: "{fen}"
      depth: "{depth}"
    extract: "$.best_move"
```

**Métodos Clave**:

1. **`load_config(config_path: str)`**
   - Abre y parsea el archivo YAML
   - Itera sobre cada motor definido
   - Crea la instancia apropiada según el tipo
   - Valida la configuración

2. **`get_engine(name: str) -> EngineInterface`**
   - Busca el motor por nombre
   - Retorna la instancia del adaptador
   - Lanza excepción si no existe

**Ejemplo de Uso**:
```python
# Inicializar manager
manager = EngineManager("config/engines.yaml")

# Obtener motor
stockfish = manager.get_engine("stockfish")

# Usar motor (interfaz común)
best_move = await stockfish.get_best_move(
    fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    depth=20
)
print(best_move)  # "e7e5"
```

---

## 🎨 Patrones de Diseño Aplicados

### 1. 🔌 Adapter Pattern (Patrón Adaptador)

**Problema**: Diferentes sistemas tienen interfaces incompatibles.

**Solución**: Los adaptadores convierten una interfaz en otra esperada por el cliente.

```
UCI Engine (protocolo UCI) ──┐
                             ├─→ EngineInterface ──→ Aplicación
REST API (HTTP/JSON)      ──┘
```

**Beneficios**:
- Código cliente independiente de implementaciones específicas
- Fácil agregar nuevos tipos de motores
- Reutilización de código existente

---

### 2. 🎯 Strategy Pattern (Patrón Estrategia)

**Problema**: Necesitamos alternar entre diferentes algoritmos en tiempo de ejecución.

**Solución**: Encapsular cada algoritmo en una clase con interfaz común.

```python
# La aplicación no sabe si usa UCI o REST
engine = manager.get_engine(user_choice)
move = await engine.get_best_move(fen, depth)
```

**Beneficios**:
- Estrategias intercambiables
- Selección en tiempo de ejecución
- Código cliente simplificado

---

### 3. 🏭 Factory Pattern (Patrón Fábrica)

**Problema**: Creación compleja de objetos debe ser centralizada.

**Solución**: Una clase fábrica maneja la creación basada en configuración.

```python
# EngineManager actúa como fábrica
if engine_type == "uci":
    return UciEngineAdapter(config)
elif engine_type == "rest":
    return RestEngineAdapter(config)
```

**Beneficios**:
- Creación centralizada y consistente
- Configuración externa (YAML)
- Fácil agregar nuevos tipos

---

### 4. 🔄 Dependency Inversion Principle (SOLID)

**Principio**: Depender de abstracciones, no de concreciones.

```python
# Correcto ✅
def analyze_position(engine: EngineInterface, fen: str):
    return engine.get_best_move(fen, 20)

# Incorrecto ❌
def analyze_position(engine: UciEngineAdapter, fen: str):
    return engine.get_best_move(fen, 20)
```

**Beneficios**:
- Bajo acoplamiento
- Alta cohesión
- Fácil testing (mocks)

---

## 🔄 Flujo de Ejecución Completo

### Ejemplo: Analizar una Posición

```python
# 1. Inicialización (una vez al arrancar la aplicación)
manager = EngineManager("config/engines.yaml")

# 2. Seleccionar motor
engine = manager.get_engine("stockfish")

# 3. Analizar posición
fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
best_move = await engine.get_best_move(fen, depth=20)

# 4. Usar resultado
print(f"Mejor movimiento: {best_move}")  # "f1b5"
```

### Secuencia Detallada (Motor UCI)

```
Aplicación
    ↓ [1. get_engine("stockfish")]
EngineManager
    ↓ [2. retorna UciEngineAdapter]
Aplicación
    ↓ [3. get_best_move(fen, 20)]
UciEngineAdapter
    ↓ [4. _start_engine() si no está activo]
    ↓ [5. "position fen <fen>"]
    ↓ [6. "go depth 20"]
Stockfish Process
    ↓ [7. calcula...]
    ↓ [8. "bestmove f1b5"]
UciEngineAdapter
    ↓ [9. extrae "f1b5"]
    ↓ [10. retorna "f1b5"]
Aplicación
```

---

## 🛠️ Tecnologías y Bibliotecas

### Core Python

- **`abc`**: Abstract Base Classes para interfaces
- **`asyncio`**: Programación asíncrona
  - `create_subprocess_exec()`: Ejecutar procesos
  - `PIPE`: Comunicación stdin/stdout
  - `async/await`: Operaciones no bloqueantes

### Bibliotecas Externas

- **`httpx`**: Cliente HTTP asíncrono moderno
  ```python
  async with httpx.AsyncClient() as client:
      response = await client.get(url, params=params)
  ```

- **`pyyaml`**: Parseo de archivos YAML
  ```python
  config = yaml.safe_load(file)
  ```

- **`jsonpath`**: Consultas sobre estructuras JSON
  ```python
  result = jsonpath(data, "$.pvs[0].moves")
  ```

### Herramientas de Desarrollo

- **`diagrams`**: Generación de diagramas como código
- **`graphviz`**: Motor de renderizado de grafos

---

## 📈 Ventajas del Diseño

| Característica | Beneficio |
|---------------|-----------|
| **Extensibilidad** | Agregar nuevos motores sin modificar código existente |
| **Mantenibilidad** | Separación clara de responsabilidades (SRP) |
| **Testabilidad** | Fácil crear mocks de `EngineInterface` |
| **Configurabilidad** | Motores se gestionan en YAML, no en código |
| **Rendimiento** | Operaciones asíncronas permiten concurrencia |
| **Flexibilidad** | Soporta motores locales y remotos transparentemente |
| **Escalabilidad** | Múltiples motores en paralelo si es necesario |

---

## 🔮 Posibles Extensiones

### 1. Agregar Caché de Evaluaciones

```python
class CachedEngineAdapter(EngineInterface):
    def __init__(self, engine: EngineInterface):
        self.engine = engine
        self.cache = {}
    
    async def get_best_move(self, fen: str, depth: int) -> str:
        key = f"{fen}:{depth}"
        if key not in self.cache:
            self.cache[key] = await self.engine.get_best_move(fen, depth)
        return self.cache[key]
```

### 2. Agregar Múltiples Motores en Paralelo

```python
class MultiEngineAdapter(EngineInterface):
    def __init__(self, engines: list[EngineInterface]):
        self.engines = engines
    
    async def get_best_move(self, fen: str, depth: int) -> str:
        results = await asyncio.gather(
            *[e.get_best_move(fen, depth) for e in self.engines]
        )
        # Votar por el movimiento más común
        return max(set(results), key=results.count)
```

### 3. Agregar Logging y Métricas

```python
class InstrumentedEngineAdapter(EngineInterface):
    def __init__(self, engine: EngineInterface):
        self.engine = engine
        self.metrics = {"calls": 0, "total_time": 0}
    
    async def get_best_move(self, fen: str, depth: int) -> str:
        start = time.time()
        result = await self.engine.get_best_move(fen, depth)
        elapsed = time.time() - start
        
        self.metrics["calls"] += 1
        self.metrics["total_time"] += elapsed
        logger.info(f"Motor tomó {elapsed:.2f}s")
        
        return result
```

---

## 📝 Conclusión

El **Engine Manager** es un ejemplo de arquitectura limpia y bien diseñada que:

1. ✅ Utiliza patrones de diseño probados
2. ✅ Sigue principios SOLID
3. ✅ Es fácil de extender y mantener
4. ✅ Proporciona flexibilidad sin complejidad innecesaria
5. ✅ Está preparado para escalar según las necesidades

Este diseño permite que el Chess Trainer sea flexible, mantenible y preparado para el futuro.

---

**Generado con**: [Diagrams](https://diagrams.mingrammer.com/) - Diagram as Code  
**Autor**: Chess Trainer Development Team  
**Fecha**: 2025

