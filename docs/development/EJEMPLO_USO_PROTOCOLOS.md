# 📖 Ejemplos de Uso - Nueva Arquitectura con Protocolos

## 🚀 Uso Básico

### 1. Crear Motor Tradicional (UCI o REST)

```python
from engines import TraditionalEngine

# Motor UCI local (Stockfish)
config_uci = {
    "command": "stockfish",
    "default_depth": 20,
    "threads": 4,
    "hash": 128
}
stockfish = TraditionalEngine("stockfish", config_uci)

# Motor REST externo (Lichess)
config_rest = {
    "url": "https://lichess.org/api/cloud-eval",
    "method": "GET",
    "params": {"fen": "{fen}", "multiPv": "1"},
    "extract": "$.pvs[0].moves",
    "timeout": 30.0
}
lichess = TraditionalEngine("lichess", config_rest)

# Usar motor (interfaz idéntica para ambos)
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
move = await stockfish.get_move(fen, depth=15)
print(f"Stockfish sugiere: {move}")

move = await lichess.get_move(fen, depth=15)
print(f"Lichess sugiere: {move}")
```

### 2. Crear Motor Neuronal

```python
from engines import NeuronalEngine

# LCZero local (UCI)
config_lc0 = {
    "protocol": "uci",
    "command": "lc0",
    "weights": "/path/to/weights.pb.gz",
    "backend": "cuda",
    "search_mode": "nodes",
    "default_search_value": 800000
}
lc0 = NeuronalEngine("lc0", config_lc0)

# Motor neuronal remoto (REST)
config_remote = {
    "protocol": "rest",
    "url": "https://api.neural-chess.com/analyze",
    "method": "POST",
    "api_key": "YOUR_API_KEY",
    "timeout": 60.0
}
neural_remote = NeuronalEngine("neural-api", config_remote)

# Usar
move = await lc0.get_move(fen, depth=800000)
print(f"LCZero sugiere: {move}")
```

### 3. Crear Motor Generativo

```python
from engines import GenerativeEngine

# GPT-4 (API externa)
config_gpt4 = {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "YOUR_OPENAI_KEY",
    "temperature": 0.3,
    "max_tokens": 500
}
gpt4 = GenerativeEngine("gpt4-chess", config_gpt4)

# LLM local (Ollama)
config_local = {
    "provider": "local",
    "endpoint": "http://localhost:11434",
    "model": "llama2:7b",
    "temperature": 0.3
}
llama = GenerativeEngine("llama-local", config_local)

# Usar con contexto adicional
# Nota: Después de 4 movimientos, el modelo elegirá automáticamente una estrategia

# Movimientos tempranos (0-3): sin selección de estrategia
move = await gpt4.get_move(
    fen,
    move_history="1. e4 e5",  # Solo 2 movimientos
    explanation=True
)
print(f"GPT-4 sugiere: {move}")

# Movimientos avanzados (4+): el modelo elegirá estrategia automáticamente
move = await gpt4.get_move(
    fen,
    move_history="1. e4 e5 2. Nf3 Nc6 3. Bb5 a6",  # 4 movimientos → selección automática
    explanation=True
)
print(f"GPT-4 sugiere: {move}")

# Forzar una estrategia específica (opcional)
move = await gpt4.get_move(
    fen,
    move_history="1. e4 e5 2. Nf3",
    strategy="aggressive",  # Fuerza estrategia agresiva
    explanation=True
)
print(f"GPT-4 sugiere: {move}")

# Obtener explicación si se solicitó
explanation = gpt4.get_last_explanation()
print(f"Explicación: {explanation}")
```

## 🔧 Uso Avanzado

### 4. Trabajar Directamente con Protocolos

```python
from engines.protocols import UCIProtocol, RESTProtocol, APILLMProtocol

# Protocolo UCI independiente
uci_protocol = UCIProtocol({"command": "stockfish"})
await uci_protocol.initialize()
await uci_protocol.send_position(fen)
move = await uci_protocol.request_move(depth=20)
await uci_protocol.cleanup()

# Protocolo REST independiente
rest_protocol = RESTProtocol({
    "url": "https://api.chess.com/pub/analysis",
    "method": "POST",
    "params": {"fen": "{fen}"}
})
await rest_protocol.send_position(fen)
move = await rest_protocol.request_move()

# Protocolo LLM independiente
llm_protocol = APILLMProtocol({
    "provider": "anthropic",
    "model": "claude-3-opus",
    "api_key": "YOUR_KEY"
})
prompt = "Analiza esta posición de ajedrez: {fen} y sugiere el mejor movimiento."
response = await llm_protocol.request_move(prompt=prompt)
```

### 5. Inyección de Protocolos (Testing)

```python
from unittest.mock import Mock, AsyncMock

# Crear motor con protocolo mockeado
mock_protocol = Mock()
mock_protocol.initialize = AsyncMock()
mock_protocol.send_position = AsyncMock()
mock_protocol.request_move = AsyncMock(return_value="e2e4")
mock_protocol.cleanup = AsyncMock()

engine = TraditionalEngine("test", {"command": "stockfish"})
engine.protocol = mock_protocol  # Inyección de dependencia

# Test
move = await engine.get_move(fen, depth=15)
assert move == "e2e4"
mock_protocol.send_position.assert_called_once_with(fen)
mock_protocol.request_move.assert_called_once()
```

### 6. Usar EngineManager

```python
from engine_manager import EngineManager

# Cargar todos los motores desde YAML
manager = EngineManager("config/engines.yaml")

# Listar motores disponibles
engines = manager.list_engines()
print(f"Motores disponibles: {engines}")

# Obtener información detallada
info = manager.get_engines_info()
for engine_info in info:
    print(f"{engine_info['name']}: {engine_info['type']} ({engine_info['origin']})")

# Usar un motor específico
move = await manager.get_best_move("stockfish-local", fen, depth=20)

# Comparar todos los motores
results = await manager.compare_engines(fen, depth=15)
for engine_name, move in results.items():
    print(f"{engine_name}: {move}")

# Filtrar por tipo
traditional_engines = manager.filter_engines_by_type(MotorType.TRADITIONAL)
generative_engines = manager.filter_engines_by_type(MotorType.GENERATIVE)

# Limpiar al finalizar
await manager.cleanup_all()
```

## 🏭 Usando Factory

### 7. Crear Motores Dinámicamente

```python
from engines import EngineFactory

# Crear desde diccionario
config = {
    "stockfish": {
        "command": "stockfish",
        "default_depth": 20
    },
    "gpt4": {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "YOUR_KEY"
    }
}

engines = EngineFactory.create_from_dict(config)
stockfish = engines["stockfish"]
gpt4 = engines["gpt4"]

# Crear desde YAML
engines = EngineFactory.create_from_yaml("config/engines.yaml")

# Crear un motor individual
engine = EngineFactory.create_engine("my-engine", {
    "engine_type": "traditional",  # Opcional (se infiere automáticamente)
    "command": "stockfish"
})
```

## 📊 Clasificación y Filtrado

### 8. Analizar Matriz de Motores

```python
from engines import EngineClassifier

# Clasificar un motor
classification = EngineClassifier.classify_engine(stockfish)
print(classification)
# {
#   "name": "stockfish",
#   "type": "traditional",
#   "origin": "internal",
#   "validation_mode": "schema",
#   "class": "TraditionalEngine",
#   "protocol": "UCIProtocol"
# }

# Generar matriz completa
matrix = EngineClassifier.generate_classification_matrix(manager.engines)
for row in matrix:
    print(f"{row['name']:20} | {row['type']:12} | {row['protocol']:20}")

# Filtrar por protocolo
uci_engines = EngineClassifier.filter_by_protocol(manager.engines, "UCIProtocol")
rest_engines = EngineClassifier.filter_by_protocol(manager.engines, "RESTProtocol")
```

## 🎨 Sistema de Estrategias Automático (Motores Generativos)

### 9. Selección Automática de Estrategias

El sistema implementa un mecanismo inteligente de selección de estrategias basado en el progreso de la partida:

**Fase Temprana (Movimientos 0-3)**
- El prompt **no incluye** selección de estrategia
- El modelo juega de forma equilibrada sin sesgos estratégicos
- Permite exploración natural de la posición

**Fase Avanzada (Movimientos 4+)**
- El prompt **incluye automáticamente** una lista de estrategias disponibles
- El modelo debe elegir una estrategia y responder:
  ```
  ESTRATEGIA: [nombre]
  MOVIMIENTO: [uci]
  ```
- Las estrategias se cargan dinámicamente desde `config/chess_strategies.yaml`

**Estrategias Disponibles:**
- `balanced`: Equilibrio entre táctica y posición
- `aggressive`: Juego agresivo, busca ataque y combinaciones
- `defensive`: Juego defensivo, prioriza seguridad
- `tactical`: Enfoque en combinaciones y tácticas
- `positional`: Enfoque en estructura y planes a largo plazo
- `material`: Prioriza ganancia de material
- `king_safety`: Prioriza seguridad del rey

**Implementación Técnica:**
- El conteo de movimientos se realiza automáticamente desde `move_history` (soporta formatos PGN y UCI)
- El template de prompt usa **Jinja2** con lógica condicional (`config/prompt_template.jinja`)
  - Permite renderizado dinámico basado en el número de movimientos
  - Las estrategias se iteran automáticamente desde el YAML
- El sistema no requiere configuración adicional: funciona automáticamente para todos los motores generativos

**Ejemplo de uso:**
```python
from engines import GenerativeEngine

config = {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key": "YOUR_KEY"
}
engine = GenerativeEngine("gpt-chess", config)

# Movimientos tempranos: sin selección de estrategia
move = await engine.get_move(
    fen,
    move_history="1. e4 e5"  # 2 movimientos → prompt simple
)

# Movimientos avanzados: selección automática de estrategia
move = await engine.get_move(
    fen,
    move_history="1. e4 e5 2. Nf3 Nc6 3. Bb5 a6"  # 4 movimientos → modelo elige estrategia
)

# Forzar estrategia específica (opcional)
move = await engine.get_move(
    fen,
    move_history="1. e4 e5",
    strategy="aggressive"  # Fuerza estrategia agresiva
)
```

### 10. Personalizar Prompts (Legacy)

Para casos especiales, puedes usar prompts externos:

Crear archivo `prompts/custom_style.yaml`:
```yaml
template: |
  Eres un jugador de ajedrez agresivo y táctico.
  
  Posición: {{ fen }}
  Histórico: {{ move_history }}
  
  Busca el movimiento más agresivo posible.
  
  MOVIMIENTO:
```

Usar en el motor:
```python
config = {
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "YOUR_KEY",
    "prompt_template_file": "prompts/custom_style.yaml"
}
custom_gpt = GenerativeEngine("custom-gpt", config)
```

## 🔄 Gestión de Ciclo de Vida

### 10. Inicialización y Limpieza

```python
# Los motores se inicializan automáticamente en el primer uso
engine = TraditionalEngine("stockfish", config)

# Puedes inicializar manualmente
await engine.initialize()

# Verificar estado
if engine._initialized:
    print("Motor listo")

# Obtener movimientos
move = await engine.get_move(fen, depth=20)

# Limpiar recursos al finalizar
await engine.cleanup()

# El protocolo también se limpia
await engine.protocol.cleanup()
```

## 🧪 Ejemplo Completo de Aplicación

```python
import asyncio
from engines import EngineFactory, MotorType

async def main():
    # Cargar motores
    engines = EngineFactory.create_from_yaml("config/engines.yaml")
    
    # Posición inicial
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    
    # Analizar con cada tipo de motor
    for name, engine in engines.items():
        try:
            print(f"\n🔍 Analizando con {name}...")
            
            # Preparar kwargs según tipo
            kwargs = {}
            if engine.motor_type == MotorType.GENERATIVE:
                kwargs["move_history"] = "Inicio de la partida"
                kwargs["strategy"] = "balanced"
            
            # Obtener movimiento
            move = await engine.get_move(fen, depth=15, **kwargs)
            print(f"✅ {name} sugiere: {move}")
            
        except Exception as e:
            print(f"❌ Error con {name}: {e}")
    
    # Limpiar todos los motores
    for engine in engines.values():
        await engine.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📝 Notas Importantes

1. **Todos los motores son asíncronos**: Usa `await` en todas las operaciones
2. **Limpieza**: Siempre llama a `cleanup()` al finalizar
3. **Inicialización**: Es automática en el primer `get_move()`
4. **Protocolos intercambiables**: Mismo motor puede usar diferentes protocolos
5. **Retrocompatibilidad**: Configs antiguas siguen funcionando

## 🔗 Recursos

- [Documentación de Refactorización](../architecture/REFACTORIZACION_PROTOCOLOS.md)
- [Patrones de Diseño](../architecture/patrones_diseño.md)
- [Configuración de Motores](../config/engines.yaml)

---

**Versión**: 2.0.0  
**Última actualización**: 4 de noviembre de 2025

