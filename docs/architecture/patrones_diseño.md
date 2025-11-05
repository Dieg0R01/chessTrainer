# 🎨 Patrones de Diseño en Engine Manager

Este documento explica de forma visual y práctica los patrones de diseño implementados en el Engine Manager.

---

## 📐 1. Adapter Pattern (Patrón Adaptador)

### Problema
Tienes sistemas con interfaces incompatibles que necesitan trabajar juntos.

### Analogía del Mundo Real
Piensa en un adaptador de corriente para viajar:
- 🇺🇸 Enchufe estadounidense (110V, tipo A)
- 🇪🇺 Enchufe europeo (220V, tipo C)
- 🔌 **Adaptador**: convierte un tipo en otro

### En Nuestro Código

```
┌─────────────────┐
│  Aplicación     │ "Quiero el mejor movimiento"
│  de Ajedrez     │
└────────┬────────┘
         │
         ↓ Interfaz común
┌────────────────────────────┐
│    EngineInterface         │
│  ┌──────────────────────┐  │
│  │ get_best_move()      │  │
│  └──────────────────────┘  │
└────────┬───────────────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌─────────┐ ┌──────────┐
│   UCI   │ │   REST   │
│ Adapter │ │ Adapter  │
└────┬────┘ └────┬─────┘
     ↓           ↓
┌─────────┐ ┌──────────┐
│Stockfish│ │Chess API │
│(UCI)    │ │(HTTP)    │
└─────────┘ └──────────┘
```

### Código Real

```python
# Sin Adapter (código acoplado ❌)
if motor == "stockfish":
    process = subprocess.Popen(["stockfish"])
    process.stdin.write(b"position fen ...\n")
    process.stdin.write(b"go depth 20\n")
    # ... lógica UCI específica
elif motor == "lichess":
    response = requests.get("https://lichess.org/api/...")
    # ... lógica REST específica

# Con Adapter (código desacoplado ✅)
engine = manager.get_engine("stockfish")  # o "lichess"
move = await engine.get_best_move(fen, depth)  # ¡Interfaz común!
```

### Beneficios
- ✅ Código cliente simple y uniforme
- ✅ Fácil agregar nuevos tipos de motores
- ✅ Cada adaptador encapsula su complejidad

---

## 🎯 2. Strategy Pattern (Patrón Estrategia)

### Problema
Necesitas cambiar el algoritmo/comportamiento en tiempo de ejecución.

### Analogía del Mundo Real
Métodos de pago en una tienda online:
- 💳 Tarjeta de crédito
- 🏦 Transferencia bancaria
- 📱 PayPal
- 🪙 Criptomoneda

El proceso de compra es el mismo, pero el **método de pago es intercambiable**.

### En Nuestro Código

```python
# El usuario elige el motor en tiempo de ejecución
motor_elegido = input("¿Qué motor usar? (stockfish/lichess): ")

# La estrategia se selecciona dinámicamente
engine = manager.get_engine(motor_elegido)

# El código cliente es el mismo ¡sin importar la estrategia!
mejor_movimiento = await engine.get_best_move(fen, 20)
```

### Diagrama

```
         ┌──────────────┐
         │  Aplicación  │
         └──────┬───────┘
                │ usa
                ↓
    ┌────────────────────┐
    │ EngineInterface    │ ← Estrategia abstracta
    │ (Interfaz)         │
    └────────────────────┘
              △
              │ implementan
      ┌───────┴────────┐
      │                │
┌─────┴──────┐   ┌────┴──────┐
│ Estrategia │   │ Estrategia│
│    UCI     │   │    REST   │
└────────────┘   └───────────┘
```

### Beneficios
- ✅ Cambio de algoritmo sin modificar código cliente
- ✅ Nuevas estrategias sin tocar las existentes
- ✅ Código más mantenible y testeable

---

## 🏭 3. Factory Pattern (Patrón Fábrica)

### Problema
La creación de objetos es compleja y debe centralizarse.

### Analogía del Mundo Real
Fábrica de automóviles:
- 🏭 Fábrica (EngineManager)
- 📋 Orden de producción (engines.yaml)
- 🚗 Producto (UciEngineAdapter / RestEngineAdapter)

No necesitas saber **cómo** se fabrica un auto, solo pides uno.

### En Nuestro Código

```yaml
# engines.yaml (Orden de producción)
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
    extract: "$.pvs[0].moves"
```

```python
# EngineManager (La Fábrica)
class EngineManager:
    def load_config(self, config_path):
        config = yaml.safe_load(open(config_path))
        
        for name, cfg in config["engines"].items():
            # La fábrica decide qué crear
            if cfg["type"] == "uci":
                self.engines[name] = UciEngineAdapter(cfg)
            elif cfg["type"] == "rest":
                self.engines[name] = RestEngineAdapter(cfg)
```

```python
# Cliente (El comprador)
manager = EngineManager("config/engines.yaml")  # Inicializa la fábrica
motor = manager.get_engine("stockfish")         # "Dame un Stockfish"
```

### Flujo

```
1. Cliente solicita motor
        ↓
2. Fábrica lee configuración
        ↓
3. Fábrica decide qué tipo crear
        ↓
4. Fábrica construye el adaptador
        ↓
5. Cliente recibe motor listo para usar
```

### Beneficios
- ✅ Creación centralizada y consistente
- ✅ Configuración externa (sin hardcodear)
- ✅ Fácil agregar nuevos tipos de motores

---

## 🔄 4. Dependency Inversion Principle (SOLID)

### Problema
El código de alto nivel no debe depender de detalles de implementación.

### Analogía del Mundo Real
Conducir un auto:
- ✅ Dependes de la **interfaz** (volante, pedales, palanca)
- ❌ NO dependes de si el motor es gasolina, eléctrico o híbrido

### Diagrama de Dependencias

```
❌ INCORRECTO (Dependencia directa)
┌──────────────┐
│  Aplicación  │
└──────┬───────┘
       ↓ depende directamente
┌─────────────────┐
│ UciEngineAdapter│ ← Implementación concreta
└─────────────────┘

Problema: Si cambias de UCI a REST, 
¡debes modificar la Aplicación!


✅ CORRECTO (Inversión de dependencia)
┌──────────────┐
│  Aplicación  │
└──────┬───────┘
       ↓ depende de abstracción
┌─────────────────┐
│ EngineInterface │ ← Interfaz abstracta
└────────△────────┘
         │ implementa
   ┌─────┴──────┐
   │            │
┌──┴───┐   ┌───┴────┐
│ UCI  │   │  REST  │ ← Implementaciones concretas
└──────┘   └────────┘

Beneficio: Cambias de UCI a REST
¡sin tocar la Aplicación!
```

### En Código

```python
# ❌ INCORRECTO: Dependencia de implementación concreta
def analizar_posicion(engine: UciEngineAdapter, fen: str):
    return engine.get_best_move(fen, 20)

# Problema: Solo funciona con UCI, no con REST


# ✅ CORRECTO: Dependencia de abstracción
def analizar_posicion(engine: EngineInterface, fen: str):
    return engine.get_best_move(fen, 20)

# Beneficio: Funciona con CUALQUIER motor (UCI, REST, futuro...)
```

### Beneficios
- ✅ Bajo acoplamiento (módulos independientes)
- ✅ Alta cohesión (cada módulo tiene una responsabilidad)
- ✅ Fácil crear mocks para testing
- ✅ Cambios en implementación no afectan clientes

---

## 🔗 Cómo se Relacionan los Patrones

Estos patrones **NO son independientes**, trabajan juntos:

```
┌─────────────────────────────────────────────────┐
│          APLICACIÓN (Código Cliente)            │
│                                                 │
│  engine = manager.get_engine("stockfish")       │
│  move = await engine.get_best_move(fen, 20)    │
└────────────────────┬────────────────────────────┘
                     │
                     ↓ (Dependency Inversion)
        ┌────────────────────────┐
        │   EngineInterface      │ ← Abstracción
        └────────┬───────────────┘
                 △
                 │ (Strategy)
        ┌────────┴─────────┐
        │                  │
┌───────┴────────┐  ┌─────┴──────────┐
│  UCI Adapter   │  │  REST Adapter  │ ← Adapters
└───────┬────────┘  └─────┬──────────┘
        │                 │
        ↓                 ↓
   [Stockfish]       [Chess API]
        △                 △
        │                 │
        └─────────┬───────┘
                  │ (Factory)
          ┌───────┴────────┐
          │ EngineManager  │ ← Crea adaptadores
          └────────────────┘
```

**Flujo completo**:
1. **Factory** (EngineManager) crea adaptadores según configuración
2. **Adapter** (UciAdapter/RestAdapter) convierte interfaces
3. **Strategy** permite elegir motor en tiempo de ejecución
4. **Dependency Inversion** mantiene código desacoplado

---

## 📊 Comparación Antes vs Después

### ❌ ANTES (Sin Patrones)

```python
def get_best_move(motor, fen, depth):
    if motor == "stockfish":
        proc = subprocess.Popen(["stockfish"], ...)
        proc.stdin.write(b"uci\n")
        # 50 líneas de código UCI...
        
    elif motor == "lichess":
        response = requests.get("https://lichess.org/...", ...)
        data = response.json()
        # 30 líneas de código REST...
        
    elif motor == "chess_com":
        # Otro bloque de 40 líneas...
        
    # ... más motores = más líneas
```

**Problemas**:
- 🔴 Código monolítico (todo en una función)
- 🔴 Difícil de mantener (un cambio afecta todo)
- 🔴 Difícil de testear (no puedes hacer mock fácilmente)
- 🔴 Violación del principio Open/Closed

### ✅ DESPUÉS (Con Patrones)

```python
# Código cliente simple y elegante
manager = EngineManager("config/engines.yaml")
engine = manager.get_engine("stockfish")  # o cualquier motor
move = await engine.get_best_move(fen, 20)
```

**Ventajas**:
- 🟢 Código modular (cada clase tiene una responsabilidad)
- 🟢 Fácil de mantener (cambios localizados)
- 🟢 Fácil de testear (mocks simples)
- 🟢 Extensible (nuevos motores sin tocar código existente)
- 🟢 Configuración externa (YAML)

---

## 🎓 Resumen de Aprendizajes

| Patrón | Cuándo Usarlo | Beneficio Clave |
|--------|---------------|-----------------|
| **Adapter** | Interfaces incompatibles | Unificación de APIs |
| **Strategy** | Múltiples algoritmos intercambiables | Flexibilidad en runtime |
| **Factory** | Creación compleja de objetos | Centralización y configuración |
| **Dependency Inversion** | Evitar acoplamiento | Módulos independientes |

---

## 💡 Para Recordar

> **"Un buen diseño no es agregar más código,  
> es hacer que el código existente sea más simple."**

Los patrones de diseño NO son sobre complejidad, son sobre:
- ✨ Simplicidad
- 🔧 Mantenibilidad
- 📈 Escalabilidad
- 🧪 Testabilidad

---

**Recursos Adicionales**:
- [Refactoring Guru - Patrones de Diseño](https://refactoring.guru/es/design-patterns)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Python Design Patterns](https://python-patterns.guide/)

**Fecha**: Octubre 2025  
**Versión**: 1.0

