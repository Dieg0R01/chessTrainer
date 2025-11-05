# 🔄 Refactorización: Sistema de Protocolos

## 📋 Resumen

Se ha refactorizado completamente la arquitectura de motores de ajedrez para **separar la lógica de negocio de la lógica de comunicación** mediante el **patrón Bridge** y **composición**.

## 🎯 Problema Resuelto

### Antes (Código Duplicado)
Los tres tipos de motores (`TraditionalEngine`, `NeuronalEngine`, `GenerativeEngine`) tenían código UCI y REST duplicado:

- Código UCI duplicado en `traditional.py` y `neuronal.py` (~100 líneas cada uno)
- Código REST duplicado en los tres archivos
- Mezcla de responsabilidades: tipo de motor + protocolo de comunicación
- Difícil mantenimiento: bug en UCI requería arreglos en múltiples lugares

### Después (Composición con Protocolos)
```
Motor (Lógica de Negocio) ──usa──> Protocolo (Comunicación)
```

- **Separación de responsabilidades**: Motor vs Protocolo
- **Eliminación de duplicación**: código UCI/REST en un solo lugar
- **Patrón Bridge**: dos dimensiones ortogonales independientes
- **Extensibilidad**: añadir nuevo protocolo no afecta motores

## 🏗️ Nueva Arquitectura

### Módulo de Protocolos (`engines/protocols/`)

```
engines/protocols/
├── __init__.py          # Exportaciones
├── base.py              # ProtocolBase (interfaz común)
├── uci.py               # UCIProtocol (motores locales)
├── rest.py              # RESTProtocol (APIs REST tradicionales)
├── local_llm.py         # LocalLLMProtocol (LLMs locales: Ollama, LM Studio)
└── api_llm.py           # APILLMProtocol (APIs externas: OpenAI, Anthropic)
```

### Responsabilidades de los Protocolos

**ProtocolBase** (interfaz común):
- `initialize()` - Inicializar conexión
- `send_position(fen)` - Enviar posición del tablero
- `request_move(depth, **kwargs)` - Solicitar movimiento
- `cleanup()` - Limpiar recursos

**UCIProtocol** (motores locales UCI):
- Maneja comunicación con procesos UCI (Stockfish, LCZero, etc.)
- Protocolo UCI completo: `uci`, `isready`, `position`, `go`, `bestmove`
- Configuración de opciones: weights, backend, threads, hash
- Soporte para diferentes modos de búsqueda: depth, nodes, time

**RESTProtocol** (APIs REST):
- Comunicación HTTP con APIs de ajedrez
- Soporte GET, POST, PUT
- Extracción de movimientos con JSONPath
- Manejo de errores HTTP específicos (404, 500, etc.)
- Headers y autenticación configurables

**LocalLLMProtocol** (LLMs locales):
- Compatible con Ollama, LM Studio, LocalAI
- Prueba múltiples endpoints automáticamente
- Soporte para diferentes formatos de respuesta
- Timeout extendido para generación

**APILLMProtocol** (APIs de LLM):
- OpenAI, Anthropic, Cohere, Google
- Manejo de diferentes formatos de API
- Headers y autenticación específicos por proveedor
- Extracción de texto según formato del proveedor

## 🔧 Cambios en los Motores

### TraditionalEngine (Antes: 305 líneas → Después: 83 líneas)

**Antes**:
```python
class TraditionalUCIEngine(MotorBase):
    # ~150 líneas de código UCI
    async def _start_engine(self): ...
    async def _write_command(self): ...
    async def _read_until(self): ...
    async def get_move(self): ...
    # ... más código

class TraditionalRESTEngine(MotorBase):
    # ~150 líneas de código REST
    async def get_move(self): ...
    def _format_template(self): ...
    # ... más código
```

**Después**:
```python
class TraditionalEngine(MotorBase):
    def __init__(self, name: str, config: Dict[str, Any]):
        # Determinar protocolo
        if "command" in config:
            self.protocol = UCIProtocol(config)  # Composición
        else:
            self.protocol = RESTProtocol(config)  # Composición
    
    async def get_move(self, board_state: str, depth, **kwargs) -> str:
        await self.protocol.send_position(board_state)
        move = await self.protocol.request_move(depth, **kwargs)
        # Validar y retornar
        return move
```

### NeuronalEngine (Similar simplificación)

Ya no necesita código UCI duplicado. Usa los mismos protocolos que `TraditionalEngine`.

### GenerativeEngine (Simplificado y mejorado)

**Mejoras**:
- Soporte para prompts externos desde archivos YAML
- Separación de protocolos: `LocalLLMProtocol` vs `APILLMProtocol`
- Mejor manejo de múltiples proveedores de LLM

## 📊 Beneficios Medidos

### Reducción de Código
- `traditional.py`: 305 → 83 líneas (-73%)
- `neuronal.py`: 255 → 75 líneas (-71%)
- `generative.py`: 328 → 140 líneas (-57%)
- **Total eliminado**: ~500 líneas de código duplicado

### Código Centralizado
- Protocolo UCI: **1 implementación** en lugar de 2
- Protocolo REST: **1 implementación** en lugar de 3
- Validadores: compartidos por todos

### Extensibilidad
Añadir nuevo protocolo (ej: gRPC):
```python
# engines/protocols/grpc_protocol.py
class GRPCProtocol(ProtocolBase):
    # ... implementación

# engines/__init__.py
from .protocols import GRPCProtocol  # Exportar

# No se modifican los motores, solo se usa:
self.protocol = GRPCProtocol(config)
```

## 🔄 Retrocompatibilidad

La refactorización mantiene **100% de retrocompatibilidad** con configuraciones existentes:

### engines.yaml (Sin cambios necesarios)
```yaml
# Funciona con nueva arquitectura
stockfish-local:
  engine_type: traditional_uci  # Se normaliza a "traditional"
  command: "stockfish"

lichess-cloud:
  engine_type: traditional_rest  # Se normaliza a "traditional"
  url: "https://lichess.org/api/cloud-eval"
  extract: "$.pvs[0].moves"
```

### Factory con Normalización
```python
# EngineFactory._normalize_engine_type()
"traditional_uci" → "traditional"
"traditional_rest" → "traditional"
"neuronal_uci" → "neuronal"
```

El factory detecta automáticamente el protocolo correcto según la configuración.

## 🧪 Testing

### Motores se pueden testear con mocks
```python
# Test de TraditionalEngine con protocolo mockeado
mock_protocol = Mock(spec=UCIProtocol)
mock_protocol.request_move.return_value = "e2e4"

engine = TraditionalEngine("test", config)
engine.protocol = mock_protocol  # Inyección de dependencia

move = await engine.get_move("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 15)
assert move == "e2e4"
```

### Protocolos se pueden testear independientemente
```python
# Test de UCIProtocol sin motor
protocol = UCIProtocol({"command": "stockfish"})
await protocol.initialize()
await protocol.send_position(fen)
move = await protocol.request_move(depth=15)
# Verificar movimiento
```

## 📚 Patrones de Diseño Aplicados

### 1. Bridge Pattern
Separa abstracción (Motor) de implementación (Protocolo):
```
Motor ──usa──> Protocolo
  ▲                ▲
  │                │
Traditional    UCI/REST/LLM
Neuronal
Generative
```

### 2. Strategy Pattern
Los protocolos son estrategias intercambiables de comunicación.

### 3. Adapter Pattern
Cada protocolo adapta una interfaz específica (UCI, REST, LLM) a la interfaz común `ProtocolBase`.

### 4. Composition over Inheritance
Los motores **usan** protocolos en lugar de heredar de clases base específicas.

### 5. Dependency Inversion
Los motores dependen de la abstracción `ProtocolBase`, no de implementaciones concretas.

## 🚀 Próximos Pasos

### Mejoras Futuras Posibles
1. **Sistema de caché**: decorador para cachear resultados de motores
2. **Sistema de retries**: decorador para reintentar en caso de fallo
3. **Métricas**: decorador para registrar tiempos y estadísticas
4. **Pool de conexiones**: reutilizar procesos UCI
5. **Protocolo WebSocket**: para streaming de análisis
6. **Protocolo gRPC**: para comunicación eficiente

### Ejemplo de Nueva Feature
Añadir métricas sin modificar motores:

```python
# engines/metrics.py
class MetricsProtocol(ProtocolBase):
    def __init__(self, wrapped_protocol: ProtocolBase):
        self.protocol = wrapped_protocol
        self.metrics = {"calls": 0, "avg_time": 0}
    
    async def request_move(self, depth, **kwargs):
        start = time.time()
        move = await self.protocol.request_move(depth, **kwargs)
        self.metrics["avg_time"] = (time.time() - start)
        self.metrics["calls"] += 1
        return move

# Uso: wrappear cualquier protocolo
protocol = MetricsProtocol(UCIProtocol(config))
engine.protocol = protocol  # ¡Métricas sin modificar el motor!
```

## 📝 Conclusión

Esta refactorización:
- ✅ Elimina **~500 líneas** de código duplicado
- ✅ Mejora **mantenibilidad** (cambios centralizados)
- ✅ Aumenta **testabilidad** (mocks e inyección de dependencias)
- ✅ Facilita **extensibilidad** (nuevos protocolos sin tocar motores)
- ✅ Mantiene **retrocompatibilidad** 100%
- ✅ Aplica **patrones de diseño** probados (Bridge, Strategy, Composition)

**Resultado**: Código más limpio, modular y profesional.

---

**Fecha**: 4 de noviembre de 2025  
**Versión**: 2.0.0  
**Autor**: Chess Trainer Development Team

