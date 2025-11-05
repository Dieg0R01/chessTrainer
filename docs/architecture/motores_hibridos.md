# Motores Híbridos - Documentación y Ampliación Futura

## Introducción

Los **motores híbridos** combinan las fortalezas de diferentes tipos de motores para aprovechar lo mejor de cada enfoque. Este documento describe los conceptos, arquitecturas y posibles implementaciones de motores híbridos en el sistema Chess Trainer.

> **Nota**: Esta funcionalidad está diseñada como una ampliación futura del sistema. Los conceptos aquí descritos no están implementados en la versión actual, pero la arquitectura está preparada para soportarlos.

---

## 1. Concepto de Motores Híbridos

### 1.1 ¿Qué son los Motores Híbridos?

Un motor híbrido es aquel que combina dos o más tipos de motores para tomar decisiones de ajedrez:

- **Motor Clásico + LLM**: El LLM razona sobre la estrategia, el motor clásico valida y ejecuta.
- **Motor Neuronal + LLM**: El motor neuronal genera candidatos, el LLM selecciona según contexto.
- **Multi-motor con Votación**: Varios motores sugieren movimientos, un sistema de votación decide.

### 1.2 Ventajas de los Motores Híbridos

| Ventaja | Descripción |
|---------|-------------|
| **Razonamiento + Precisión** | LLM aporta razonamiento estratégico, motor clásico aporta cálculo táctico preciso |
| **Explicabilidad** | El LLM puede explicar el "por qué" mientras el motor clásico asegura la validez |
| **Adaptabilidad** | Permite ajustar el balance entre creatividad (LLM) y solidez (motor tradicional) |
| **Contexto histórico** | LLM mantiene memoria de la partida, motor clásico evalúa posiciones puntuales |

### 1.3 Desventajas y Consideraciones

- **Complejidad**: Requiere orquestar múltiples componentes.
- **Latencia**: Llamadas a múltiples motores aumentan el tiempo de respuesta.
- **Costos**: APIs de LLM pueden ser costosas en uso intensivo.
- **Validación**: Necesidad de validar que el LLM y motor tradicional converjan.

---

## 2. Arquitecturas de Motores Híbridos

### 2.1 Arquitectura Secuencial: LLM → Motor Clásico

**Flujo**:
1. El LLM analiza la posición y sugiere una estrategia o movimiento candidato.
2. El motor clásico valida la legalidad del movimiento.
3. Si es ilegal, se solicita al LLM una alternativa o se usa el motor clásico directamente.

**Casos de uso**:
- Entrenamiento con explicaciones pedagógicas.
- Partidas con estilo de juego personalizado.

**Diagrama**:
```
Usuario → LLM (razonamiento) → Motor Clásico (validación) → Movimiento final
```

**Implementación sugerida**:
```python
class SequentialHybridEngine(MotorBase):
    def __init__(self, llm_engine, classical_engine):
        self.llm = llm_engine
        self.classical = classical_engine
    
    async def get_move(self, board_state, **kwargs):
        # 1. LLM sugiere
        llm_move = await self.llm.get_move(board_state, **kwargs)
        
        # 2. Validar con motor clásico
        if self.is_legal(llm_move, board_state):
            return llm_move
        
        # 3. Fallback al motor clásico
        return await self.classical.get_move(board_state)
```

---

### 2.2 Arquitectura Paralela: Motor Clásico + LLM con Votación

**Flujo**:
1. Se consultan varios motores en paralelo (clásico, neuronal, LLM).
2. Se recopilan las sugerencias.
3. Un sistema de votación o árbitro decide el movimiento final.

**Casos de uso**:
- Análisis profundo de posiciones críticas.
- Comparación de enfoques para entrenamiento.

**Diagrama**:
```
                  ┌─→ Motor Clásico → Sugerencia A
Usuario → Posición ┼─→ Motor Neuronal → Sugerencia B  → Árbitro → Movimiento final
                  └─→ LLM            → Sugerencia C
```

**Implementación sugerida**:
```python
class ParallelHybridEngine(MotorBase):
    def __init__(self, engines: List[MotorBase], arbiter):
        self.engines = engines
        self.arbiter = arbiter  # Función de votación
    
    async def get_move(self, board_state, **kwargs):
        # 1. Consultar todos en paralelo
        tasks = [engine.get_move(board_state, **kwargs) for engine in self.engines]
        suggestions = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 2. Filtrar errores
        valid_suggestions = [s for s in suggestions if isinstance(s, str)]
        
        # 3. Árbitro decide
        return self.arbiter(valid_suggestions)
```

**Ejemplos de árbitros**:
- **Votación simple**: El movimiento más frecuente gana.
- **Ponderado**: Motores más fuertes tienen más peso.
- **LLM como árbitro**: El LLM elige entre las opciones dadas.

---

### 2.3 Arquitectura con LangGraph: Agente con Memoria

**Flujo**:
1. LangGraph mantiene el estado de la partida (histórico, estrategia).
2. En cada turno, el agente razona usando el contexto acumulado.
3. El motor clásico valida o ejecuta la jugada sugerida.

**Casos de uso**:
- Partidas completas con memoria y adaptación estratégica.
- Entrenamiento con análisis continuo de errores.

**¿Cuándo usar LangGraph?**
- ✅ **Sí**: Si necesitas memoria de partida, razonamiento continuo, y explicaciones contextuales.
- ❌ **No**: Si solo necesitas "siguiente jugada" sin contexto acumulativo.

**Diagrama**:
```
Estado de Partida (LangGraph)
    ↓
  Agente LLM (razonamiento + memoria)
    ↓
  Motor Clásico (validación)
    ↓
  Actualización de Estado
```

**Implementación sugerida (pseudocódigo)**:
```python
from langgraph.graph import StateGraph

class ChessGameState:
    fen: str
    move_history: List[str]
    strategy: str
    reasoning: List[str]

def reason_node(state: ChessGameState):
    # LLM razona sobre la posición
    prompt = build_context_prompt(state)
    reasoning = llm.call(prompt)
    state.reasoning.append(reasoning)
    return state

def validate_node(state: ChessGameState):
    # Motor clásico valida
    move = extract_move(state.reasoning[-1])
    if is_legal(move, state.fen):
        state.move_history.append(move)
    return state

graph = StateGraph(ChessGameState)
graph.add_node("reason", reason_node)
graph.add_node("validate", validate_node)
graph.add_edge("reason", "validate")
```

---

## 3. Matriz de Decisión: ¿Qué Arquitectura Usar?

| Objetivo | Arquitectura Recomendada | Complejidad | Latencia |
|----------|--------------------------|-------------|----------|
| Explicaciones pedagógicas | Secuencial (LLM → Clásico) | Baja | Media |
| Análisis profundo | Paralela con votación | Media | Alta |
| Partida completa con memoria | LangGraph con agente | Alta | Alta |
| Estilo de juego personalizado | Secuencial o LangGraph | Media | Media-Alta |
| Validación rápida | Clásico con LLM opcional | Baja | Baja |

---

## 4. Implementación en Chess Trainer

### 4.1 Cómo Añadir un Motor Híbrido

La arquitectura actual está preparada para soportar motores híbridos mediante composición:

```python
# En engines/hybrid.py (archivo nuevo)

from engines import MotorBase, MotorType, MotorOrigin, ValidationMode

class HybridEngine(MotorBase):
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(
            name=name,
            motor_type=MotorType.GENERATIVE,  # O crear HYBRID
            motor_origin=MotorOrigin.INTERNAL,
            validation_mode=ValidationMode.SCHEMA,
            config=config
        )
        
        # Cargar sub-motores
        self.llm_engine = config.get("llm_engine")
        self.classical_engine = config.get("classical_engine")
        
        # Estrategia de combinación
        self.strategy = config.get("hybrid_strategy", "sequential")
    
    async def get_move(self, board_state: str, **kwargs):
        if self.strategy == "sequential":
            return await self._sequential_strategy(board_state, **kwargs)
        elif self.strategy == "parallel":
            return await self._parallel_strategy(board_state, **kwargs)
```

### 4.2 Configuración en `engines.yaml`

```yaml
hybrid-assistant:
  engine_type: hybrid
  hybrid_strategy: "sequential"  # sequential, parallel, langgraph
  llm_engine: "gpt4-chess"
  classical_engine: "stockfish-local"
  description: "Motor híbrido: GPT-4 para razonamiento, Stockfish para validación"
```

### 4.3 Registro del Motor

```python
# En engines/factory.py, añadir:
from .hybrid import HybridEngine

EngineRegistry.register("hybrid", HybridEngine)
```

---

## 5. Casos de Uso Avanzados

### 5.1 Entrenador con Explicaciones

**Objetivo**: Ayudar al usuario a entender por qué un movimiento es bueno o malo.

**Flujo**:
1. Usuario hace un movimiento.
2. Motor clásico evalúa la posición antes/después.
3. LLM explica la diferencia en lenguaje natural.

**Implementación**: Usar motor híbrido secuencial con explicaciones activadas.

---

### 5.2 Análisis de Partidas

**Objetivo**: Analizar una partida completa y generar un informe.

**Flujo**:
1. Cargar PGN de la partida.
2. Para cada movimiento crítico, consultar múltiples motores.
3. LLM genera resumen con puntos clave.

**Implementación**: Usar motor paralelo para análisis, LLM para resumen.

---

### 5.3 Sparring con Estilo

**Objetivo**: Jugar contra un motor que imita un estilo (agresivo, posicional, etc.).

**Flujo**:
1. LLM recibe el estilo deseado en el prompt.
2. Motor clásico genera candidatos.
3. LLM selecciona el candidato que mejor se ajusta al estilo.

**Implementación**: Motor híbrido con LLM como selector de candidatos.

---

## 6. Roadmap de Implementación

### Fase 1: Fundamentos (✅ Completado)
- [x] Arquitectura modular con `MotorBase`
- [x] Factory y Registry
- [x] Motores tradicionales, neuronales y generativos

### Fase 2: Motores Híbridos Básicos
- [ ] Implementar `HybridEngine` con estrategia secuencial
- [ ] Añadir árbitros de votación simple
- [ ] Ejemplos en `engines.yaml`

### Fase 3: Integración con LangGraph
- [ ] Crear agente con estado de partida
- [ ] Implementar nodos de razonamiento y validación
- [ ] Interfaz de partida completa

### Fase 4: Casos de Uso Avanzados
- [ ] Entrenador con explicaciones
- [ ] Análisis de partidas con informe
- [ ] Sparring con estilos personalizados

---

## 7. Referencias y Recursos

### Frameworks para Agentes
- **LangChain**: https://python.langchain.com/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Haystack**: https://haystack.deepset.ai/

### Motores de Ajedrez
- **Stockfish**: https://stockfishchess.org/
- **Leela Chess Zero**: https://lczero.org/
- **python-chess**: https://python-chess.readthedocs.io/

### Papers y Artículos
- "Language Models as Zero-Shot Chess Players" (arXiv)
- "Combining Deep Learning and Symbolic Reasoning for Chess" (ACM)

---

## 8. Conclusiones

Los **motores híbridos** representan el futuro de los sistemas de ajedrez inteligentes, combinando:

- **Precisión táctica** de motores tradicionales
- **Razonamiento estratégico** de LLMs
- **Evaluación posicional** de redes neuronales

La arquitectura actual de Chess Trainer está diseñada para soportar esta extensión de forma natural mediante composición y el sistema de Factory/Registry.

**Próximo paso**: Implementar un `HybridEngine` básico con estrategia secuencial como prueba de concepto.

---

**Documento creado**: 2025  
**Versión**: 1.0  
**Autor**: Chess Trainer Team



