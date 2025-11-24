# 📚 Documentación Chess Trainer

Índice completo de la documentación del proyecto Chess Trainer v2.0.0.

> 📋 **¿Primera vez aquí?** Lee [NUEVA_ESTRUCTURA_DOCS.md](NUEVA_ESTRUCTURA_DOCS.md) para conocer la nueva organización.

---

## 🏗️ Arquitectura

Documentación sobre el diseño y arquitectura del sistema.

- **[ARQUITECTURA.md](architecture/ARQUITECTURA.md)** - Arquitectura completa del sistema
  - Visión general del sistema
  - Ejes de clasificación de motores
  - Matriz de clasificación
  - Patrones de diseño aplicados
  - Flujos por tipo de motor

- **[REFACTORIZACION_PROTOCOLOS.md](architecture/REFACTORIZACION_PROTOCOLOS.md)** - Refactorización v2.0 con protocolos
  - Sistema de protocolos (UCI, REST, LocalLLM, APILLM)
  - Arquitectura antes y después
  - Comparación de implementaciones
  - Beneficios de la refactorización

- **[REFACTOR_COMPLETADO.md](architecture/REFACTOR_COMPLETADO.md)** - Detalles del proceso de refactorización
  - Checklist completo
  - Validaciones realizadas
  - Métricas de calidad

- **[patrones_diseño.md](architecture/patrones_diseño.md)** - Patrones de diseño utilizados
  - Strategy Pattern
  - Factory Method
  - Adapter Pattern
  - Bridge Pattern
  - Template Method

- **[engine_manager_explicacion.md](architecture/engine_manager_explicacion.md)** - Gestión de motores
  - Funcionamiento del EngineManager
  - Teoría de patrones aplicados
  - Ejemplos de uso

- **[motores_hibridos.md](architecture/motores_hibridos.md)** - Motores híbridos (futuro)
  - Diseño propuesto
  - Casos de uso
  - Implementación futura

---

## 💻 Desarrollo

Guías y ejemplos para desarrolladores.

- **[EJEMPLO_USO_PROTOCOLOS.md](development/EJEMPLO_USO_PROTOCOLOS.md)** - Ejemplos prácticos
  - 10 ejemplos de uso de protocolos
  - Casos avanzados
  - Testing con mocks
  - Personalización de prompts

- **[API_USAGE.md](development/API_USAGE.md)** - Documentación completa de APIs
  - Todos los endpoints del backend
  - Funciones del frontend
  - Flujos de datos
  - Ejemplos de uso

- **[COMPARACION_MOTORES.md](development/COMPARACION_MOTORES.md)** - Página de Comparación
  - Funcionalidad completa de comparación
  - Edición interactiva del tablero
  - Visualización de resultados
  - Manejo de errores
  - Ejemplos de uso

- **[class_diagram_mermaid.md](development/class_diagram_mermaid.md)** - Diagrama de clases UML
  - Diagrama completo en Mermaid
  - Relaciones entre clases
  - Atributos y métodos

---

## 📝 Changelog

Historial de cambios y versiones.

- **[CAMBIOS_v2.0.0.md](changelog/CAMBIOS_v2.0.0.md)** - Changelog completo v2.0.0
  - Nuevas características
  - Cambios en arquitectura
  - Mejoras de rendimiento
  - Bugs corregidos
  - Guía de migración

- **[RESUMEN_REFACTORIZACION.md](changelog/RESUMEN_REFACTORIZACION.md)** - Resumen ejecutivo
  - Resultados en números
  - Beneficios obtenidos
  - Estado final

- **[TODO_REFACTORIZACION.md](changelog/TODO_REFACTORIZACION.md)** - Tareas completadas
  - Checklist de tareas
  - Estado de implementación

---

## 🚀 Despliegue

Guías de instalación, despliegue y verificación.

- **[DESPLIEGUE.md](deployment/DESPLIEGUE.md)** - Guía de despliegue
  - Requisitos previos
  - Instalación paso a paso
  - Configuración de motores
  - Solución de problemas
  - Scripts de inicio/parada

- **[VERIFICACION_FINAL.md](deployment/VERIFICACION_FINAL.md)** - Verificación completa
  - Checklist de verificación
  - Validaciones técnicas
  - Métricas de calidad
  - Estado de producción

---

## 📊 Diagramas

Diagramas visuales de la arquitectura.

- **[class_diagram_mermaid.html](diagrams/class_diagram_mermaid.html)** - Diagrama de clases interactivo
  - Abrirlo en navegador para visualización completa

- **[engine_manager_architecture.png](diagrams/engine_manager_architecture.png)** - Diagrama de arquitectura
  - Arquitectura visual completa
  - Flujos de comunicación

- **[generate_diagram.py](diagrams/generate_diagram.py)** - Script generador
  - Genera el diagrama de arquitectura
  - Ejecutar: `python docs/diagrams/generate_diagram.py`

---

## 🎯 Rutas de Aprendizaje

### Para Desarrolladores Nuevos

1. Comienza con el [README principal](../README.md)
2. Lee la [Arquitectura completa](architecture/ARQUITECTURA.md)
3. Revisa los [Patrones de diseño](architecture/patrones_diseño.md)
4. Explora los [Ejemplos de uso](development/EJEMPLO_USO_PROTOCOLOS.md)
5. Consulta la [Documentación de APIs](development/API_USAGE.md)
6. Visualiza el [Diagrama de clases](development/class_diagram_mermaid.md)

### Para Extender el Sistema

1. Revisa la [Arquitectura de protocolos](architecture/REFACTORIZACION_PROTOCOLOS.md)
2. Consulta los [Ejemplos prácticos](development/EJEMPLO_USO_PROTOCOLOS.md)
3. Estudia los [Patrones de diseño](architecture/patrones_diseño.md)
4. Revisa la [Documentación de APIs](development/API_USAGE.md)
5. Consulta la [Documentación de Comparación](development/COMPARACION_MOTORES.md) para entender funcionalidades avanzadas
6. Revisa el código fuente en los módulos correspondientes

### Para Desplegar

1. Sigue la [Guía de despliegue](deployment/DESPLIEGUE.md)
2. Consulta la [Verificación final](deployment/VERIFICACION_FINAL.md)
3. Lee sobre posibles problemas en la sección de solución de problemas

### Para Entender los Cambios v2.0

1. Lee el [Resumen de refactorización](changelog/RESUMEN_REFACTORIZACION.md)
2. Revisa el [Changelog completo](changelog/CAMBIOS_v2.0.0.md)
3. Compara con la [Documentación de protocolos](architecture/REFACTORIZACION_PROTOCOLOS.md)

---

## 🔗 Enlaces Rápidos

- [README Principal](../README.md)
- [Configuración de Motores](../config/engines.yaml)
- [Código Fuente - engines/](../engines/)
- [Gestor de Motores](../engine_manager.py)
- [API Principal](../main.py)

---

## 📦 Estructura del Proyecto

```
chessTrainer/
├── README.md                  # Documentación principal
├── main.py                    # API FastAPI
├── engine_manager.py          # Gestor de motores
├── config/
│   └── engines.yaml          # Configuración de motores
├── engines/                   # Módulo de motores
│   ├── base.py
│   ├── factory.py
│   ├── traditional.py
│   ├── neuronal.py
│   ├── generative.py
│   ├── validators.py
│   └── protocols/            # Protocolos de comunicación
│       ├── base.py
│       ├── uci.py
│       ├── rest.py
│       ├── local_llm.py
│       └── api_llm.py
└── docs/                     # Documentación (aquí estás)
    ├── architecture/         # Arquitectura del sistema
    ├── development/          # Guías de desarrollo
    ├── changelog/            # Historial de cambios
    ├── deployment/           # Despliegue y verificación
    └── diagrams/             # Diagramas visuales
```

---

## 🛠️ Tecnologías

- **Python 3.9+**
- **FastAPI** - Framework web asíncrono
- **python-chess** - Librería de ajedrez
- **httpx** - Cliente HTTP asíncrono
- **pyyaml** - Configuración YAML
- **jsonpath** - Extracción de datos JSON

---

## 📞 Soporte

- Consulta el [README principal](../README.md) para información general
- Revisa la [Guía de despliegue](deployment/DESPLIEGUE.md) para problemas de instalación
- Lee los [Ejemplos de uso](development/EJEMPLO_USO_PROTOCOLOS.md) para casos específicos

---

**Versión**: 2.0.0  
**Última actualización**: Noviembre 2025  
**Mantenedor**: Chess Trainer Development Team


