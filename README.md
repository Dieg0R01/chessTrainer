# Chess Trainer - Sistema de Motores de Ajedrez

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](CAMBIOS_v2.0.0.md)

Sistema modular y extensible para trabajar con múltiples motores de ajedrez: tradicionales, neuronales y generativos.

## 🎉 Nuevo en v2.0.0

**Refactorización completa** con arquitectura de protocolos:
- ✨ **~500 líneas de código duplicado eliminadas**
- 🏗️ **Sistema de protocolos** (UCI, REST, LocalLLM, APILLM)
- 🎨 **Patrones Bridge + Composition** aplicados
- 📦 **100% retrocompatible** con configuraciones existentes
- 📚 **Documentación completa** de la nueva arquitectura

👉 **[Ver cambios completos](CAMBIOS_v2.0.0.md)** | **[Documentación técnica](docs/REFACTORIZACION_PROTOCOLOS.md)** | **[Ejemplos de uso](docs/EJEMPLO_USO_PROTOCOLOS.md)**

## 🚀 Características

- **Arquitectura Modular**: Soporta motores tradicionales (Stockfish), neuronales (LCZero) y generativos (GPT-4)
- **API REST**: Interfaz unificada para todos los motores
- **Extensible**: Añade nuevos motores sin modificar el código base
- **Asíncrono**: Máxima performance con async/await
- **Validación Inteligente**: Schema para motores tradicionales, Prompt parsing para LLMs
- **Configuración YAML**: Gestión centralizada de motores

## 📋 Tabla de Contenidos

- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso Rápido](#uso-rápido)
- [Arquitectura](#arquitectura)
- [API Endpoints](#api-endpoints)
- [Tipos de Motores](#tipos-de-motores)
- [Documentación](#documentación)

## 🛠 Instalación

### Requisitos Previos

- Python 3.9+
- Stockfish (para motores UCI locales)
- LCZero (opcional, para motores neuronales)

### Pasos

```bash
# Clonar repositorio
git clone <repo-url>
cd chessTrainer

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## ⚙️ Configuración

Edita `config/engines.yaml` para configurar tus motores:

```yaml
engines:
  # Motor tradicional UCI
  stockfish-local:
    engine_type: traditional_uci
    type: uci
    command: "stockfish"
    default_depth: 15

  # Motor neuronal
  lc0-local:
    engine_type: neuronal
    protocol: uci
    command: "lc0"
    backend: "cuda"

  # Motor generativo (LLM)
  gpt4-chess:
    engine_type: generative
    provider: openai
    model: "gpt-4"
    api_key: "YOUR_API_KEY"
```

> **Nota**: Para motores generativos, necesitas añadir tu API key real.

## 🎮 Uso Rápido

### Iniciar el Servidor

```bash
python main.py
```

El servidor estará disponible en `http://localhost:8000`

### Ejemplos de Uso

#### 1. Listar Motores Disponibles

```bash
curl http://localhost:8000/engines
```

#### 2. Obtener Mejor Movimiento (Stockfish)

```bash
curl -X POST http://localhost:8000/move \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "stockfish-local",
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 20
  }'
```

#### 3. Obtener Movimiento con Explicación (LLM)

```bash
curl -X POST http://localhost:8000/move \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "gpt4-chess",
    "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
    "strategy": "aggressive",
    "explanation": true
  }'
```

#### 4. Comparar Todos los Motores

```bash
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 15
  }'
```

### Uso desde Python

```python
from engine_manager import EngineManager

# Inicializar gestor
manager = EngineManager("config/engines.yaml")

# Obtener movimiento
move = await manager.get_best_move(
    "stockfish-local",
    fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    depth=20
)

print(f"Mejor movimiento: {move}")
```

## 🏗 Arquitectura

### Estructura del Proyecto

```
chessTrainer/
├── engines/              # Módulo de motores
│   ├── base.py          # Clase base y enums
│   ├── validators.py    # Validadores (Schema y Prompt)
│   ├── traditional.py   # Motores tradicionales
│   ├── neuronal.py      # Motores neuronales
│   ├── generative.py    # Motores generativos (LLM)
│   └── factory.py       # Factory y Registry
├── config/
│   └── engines.yaml     # Configuración de motores
├── docs/                # Documentación
│   ├── ARQUITECTURA.md  # Arquitectura detallada
│   └── motores_hibridos.md  # Motores híbridos (futuro)
├── engine_manager.py    # Gestor de motores
├── main.py             # API FastAPI
└── requirements.txt    # Dependencias
```

### Patrones de Diseño

- **Strategy**: Encapsular diferentes algoritmos de obtención de movimientos
- **Factory Method**: Creación dinámica de motores desde configuración
- **Registry**: Añadir nuevos tipos sin modificar código base
- **Adapter**: Unificar APIs externas bajo interfaz común
- **Template Method**: Hooks para inicialización/limpieza

### Matriz de Clasificación

| Tipo | Origen | Validación | Ejemplo |
|------|--------|-----------|---------|
| Traditional | Internal | Schema | Stockfish (UCI) |
| Traditional | External | Schema | Lichess Cloud API |
| Neuronal | Internal | Schema | Leela Chess Zero |
| Neuronal | External | Schema | Servicio GPU remoto |
| Generative | External | Prompt | GPT-4, Claude |
| Generative | Internal | Prompt | LLM local (Ollama) |

## 🌐 API Endpoints

### Información

- `GET /` - Información general de la API
- `GET /health` - Estado de salud
- `GET /engines` - Lista de motores disponibles
- `GET /engines/info` - Información detallada de motores
- `GET /engines/matrix` - Matriz de clasificación

### Filtros

- `GET /engines/filter/type/{type}` - Filtrar por tipo (traditional, neuronal, generative)
- `GET /engines/filter/origin/{origin}` - Filtrar por origen (internal, external)

### Operaciones

- `POST /move` - Obtener mejor movimiento de un motor
- `POST /compare` - Comparar sugerencias de todos los motores
- `POST /reload` - Recargar configuración sin reiniciar

## 🎯 Tipos de Motores

### 1. Motores Tradicionales

**Características**:
- Algoritmos deterministas (minimax, alfa-beta)
- Entrada: FEN
- Salida: Movimiento UCI (ej: e2e4)
- Validación: Schema estricto

**Ejemplos**:
- Stockfish (UCI local)
- Lichess Cloud Analysis (REST API)
- Komodo, Houdini

### 2. Motores Neuronales

**Características**:
- Redes neuronales + búsqueda MCTS
- Pueden requerir GPU
- Usan "nodos" en vez de "profundidad"
- Validación: Schema estricto

**Ejemplos**:
- Leela Chess Zero (LCZero)
- AlphaZero
- Servicios remotos con GPU

### 3. Motores Generativos

**Características**:
- Basados en LLMs
- Razonamiento en lenguaje natural
- Pueden explicar decisiones
- Validación: Parsing de texto

**Ejemplos**:
- GPT-4 Chess Assistant
- Claude Chess
- Modelos locales (LangChain, Ollama)

## 📚 Documentación

### Documentación Detallada

- [**ARQUITECTURA.md**](docs/ARQUITECTURA.md) - Arquitectura completa del sistema
- [**motores_hibridos.md**](docs/motores_hibridos.md) - Motores híbridos (implementación futura)
- [**patrones_diseño.md**](docs/patrones_diseño.md) - Patrones de diseño utilizados

### Guías

1. **Añadir un Nuevo Motor**
   - Crear clase que herede de `MotorBase`
   - Registrar en `EngineRegistry`
   - Añadir configuración en `engines.yaml`
   - Recargar con `POST /reload`

2. **Configurar Motor LLM**
   - Obtener API key del proveedor
   - Añadir configuración en `engines.yaml`
   - Personalizar `prompt_template` si es necesario

3. **Desplegar en Producción**
   - Ver [DESPLIEGUE.md](DESPLIEGUE.md) para instrucciones

## 🔧 Desarrollo

### Ejecutar Tests

```bash
pytest
```

### Linting

```bash
flake8 engines/ engine_manager.py main.py
```

### Formato de Código

```bash
black engines/ engine_manager.py main.py
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Roadmap

- [x] Arquitectura base modular
- [x] Motores tradicionales (UCI y REST)
- [x] Motores neuronales
- [x] Motores generativos (LLM)
- [x] Sistema de Factory y Registry
- [x] API REST completa
- [ ] Tests unitarios completos
- [ ] Motores híbridos (LLM + Tradicional)
- [ ] Integración con LangGraph
- [ ] Dashboard web interactivo
- [ ] Análisis de partidas completas
- [ ] Sistema de entrenamiento personalizado

## 🐛 Problemas Conocidos

- Los motores LLM requieren API keys válidas
- LCZero puede requerir configuración adicional de GPU
- Algunos motores externos tienen rate limits

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- Chess Trainer Team

## 🙏 Agradecimientos

- [Stockfish](https://stockfishchess.org/) - Motor de ajedrez open source
- [Leela Chess Zero](https://lczero.org/) - Motor neuronal open source
- [python-chess](https://python-chess.readthedocs.io/) - Librería de ajedrez
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno

---

**Versión**: 2.0.0  
**Última actualización**: 2025

Para más información, consulta la [documentación completa](docs/ARQUITECTURA.md).
