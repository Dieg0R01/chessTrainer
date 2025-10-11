# 📚 Documentación del Chess Trainer

Bienvenido a la documentación técnica del proyecto Chess Trainer.

## 📁 Archivos Disponibles

### 🏗️ Arquitectura y Diseño

1. **[engine_manager_explicacion.md](engine_manager_explicacion.md)**
   - Explicación detallada del funcionamiento del Engine Manager
   - Teoría de los patrones de diseño aplicados
   - Ejemplos de uso y código
   - Posibles extensiones futuras

2. **[patrones_diseño.md](patrones_diseño.md)**
   - Explicación visual y práctica de los patrones de diseño
   - Analogías del mundo real
   - Comparación antes/después del diseño
   - Ejemplos de código comentados

### 📊 Diagramas

#### Diagrama de Arquitectura (Diagrams)

3. **[engine_manager_architecture.png](engine_manager_architecture.png)**
   - Diagrama visual de la arquitectura completa
   - Generado con [Diagrams](https://diagrams.mingrammer.com/)
   - Muestra flujos de comunicación y relaciones entre componentes

4. **[generate_diagram.py](generate_diagram.py)**
   - Script para regenerar el diagrama de arquitectura
   - Usa la biblioteca Diagrams (Diagram as Code)
   - Ejecutar con: `python docs/generate_diagram.py`

#### Diagrama de Clases UML (Mermaid)

5. **[class_diagram_mermaid.html](class_diagram_mermaid.html)**
   - Diagrama de clases UML interactivo
   - Generado con [Mermaid.js](https://mermaid.js.org/)
   - Incluye detalles de atributos, métodos y relaciones
   - Abrir en navegador para visualización completa

6. **[class_diagram_mermaid.md](class_diagram_mermaid.md)**
   - Diagrama de clases en formato Markdown
   - Se renderiza automáticamente en GitHub
   - Compatible con editores que soportan Mermaid
   - Incluye documentación completa de cada clase

## 🚀 Cómo Usar Esta Documentación

### Para Desarrolladores Nuevos

1. Lee primero `engine_manager_explicacion.md` para entender la arquitectura
2. Revisa el diagrama `engine_manager_architecture.png` para visualizar el sistema
3. Consulta el código fuente en `../engine_manager.py`

### Para Extender el Sistema

1. Revisa la sección "Posibles Extensiones" en `engine_manager_explicacion.md`
2. Sigue los patrones de diseño existentes (Adapter, Strategy, Factory)
3. Actualiza la configuración en `../config/engines.yaml`

### Para Regenerar los Diagramas

#### Diagrama de Arquitectura (Diagrams)
```bash
# Asegúrate de estar en el entorno conda correcto
conda activate chess

# Ejecuta el script desde el directorio raíz del proyecto
cd /Users/diegor/dev/chessTrainer
python docs/generate_diagram.py
```

#### Diagrama de Clases UML (Mermaid)

**Opción 1: Ver en Navegador (Recomendado)**
```bash
open docs/class_diagram_mermaid.html
```

**Opción 2: Ver en GitHub**
- Sube el archivo `class_diagram_mermaid.md` a GitHub
- El diagrama se renderiza automáticamente

**Opción 3: Ver en VS Code**
1. Instala la extensión "Markdown Preview Mermaid Support"
2. Abre `class_diagram_mermaid.md`
3. Presiona `Cmd+Shift+V` (Mac) o `Ctrl+Shift+V` (Windows)

**Opción 4: Editor Online**
- Visita [https://mermaid.live](https://mermaid.live)
- Copia y pega el código del diagrama

## 🎯 Componentes Principales Documentados

- ✅ **EngineInterface**: Interfaz abstracta para motores
- ✅ **UciEngineAdapter**: Adaptador para motores UCI (Stockfish, etc.)
- ✅ **RestEngineAdapter**: Adaptador para APIs REST
- ✅ **EngineManager**: Gestor y fábrica de motores

## 🛠️ Tecnologías

- **Python 3.12+**
- **asyncio**: Programación asíncrona
- **httpx**: Cliente HTTP asíncrono
- **pyyaml**: Configuración
- **jsonpath**: Extracción de datos JSON
- **diagrams**: Generación de diagramas
- **graphviz**: Renderizado de grafos

## 📖 Recursos Adicionales

- [Documentación de Diagrams](https://diagrams.mingrammer.com/)
- [Protocolo UCI](https://www.chessprogramming.org/UCI)
- [Patrones de Diseño](https://refactoring.guru/es/design-patterns)
- [Principios SOLID](https://en.wikipedia.org/wiki/SOLID)

---

**Última actualización**: Octubre 2025  
**Versión**: 1.0

