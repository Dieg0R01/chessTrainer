# Plataforma de Ajedrez con Motores Externos

## Objetivo
Este proyecto tiene como objetivo construir una aplicación web que permita a los usuarios jugar partidas de ajedrez contra motores externos configurados a través de una API, o espectar partidas entre dos motores seleccionados. La configuración de los motores se realiza de manera declarativa utilizando archivos YAML.

## Arquitectura
La aplicación se divide en dos componentes principales: Frontend y Backend.

### Frontend (React.js)
El frontend está construido con React.js y Vite, utilizando las siguientes librerías clave:
-   `chess.js`: Para la lógica de validación de movimientos y las reglas del ajedrez.
-   `react-chessboard`: Para el renderizado visual del tablero de ajedrez interactivo.
-   `react-router-dom`: Para la navegación entre las diferentes páginas de la aplicación.

El frontend consta de dos páginas principales:

1.  **Página de Selección (`/`)**:
    -   Permite al usuario elegir uno o dos motores de ajedrez de una lista desplegable.
    -   Opciones:
        -   **Humano vs. Motor**: Seleccionar un motor contrincante y "Humano" en tu lugar.
        -   **Motor A vs. Motor B**: Seleccionar dos motores para una partida automática.
    -   Un botón "Empezar Partida" que navega a la página de juego.

2.  **Página de Partida (`/game`)**:
    -   Muestra un tablero interactivo (`react-chessboard`).
    -   **Flujo Humano vs. Motor**: Las jugadas del humano se validan localmente con `chess.js` y se envían al backend para que el motor responda con su mejor movimiento.
    -   **Flujo Motor vs. Motor**: El frontend consulta a ambos motores a un intervalo fijo (por ejemplo, 3 segundos por movimiento) y actualiza el tablero automáticamente.

### Backend (Python, FastAPI)
El backend está desarrollado en Python utilizando FastAPI, ofreciendo una API REST para interactuar con los motores de ajedrez. 

**Endpoints**:
-   `POST /move`:
    -   **Request**:
        ```json
        { "engine": "string", "fen": "string", "depth": int }
        ```
    -   **Response**:
        ```json
        { "bestmove": "string" }
        ```
    -   Este endpoint recibe el nombre del motor, la posición actual del tablero en formato FEN (Forsyth-Edwards Notation) y la profundidad de análisis, y devuelve el mejor movimiento sugerido por el motor.
-   `GET /`: Sirve el archivo `index.html` del frontend, actuando como un servidor de archivos estáticos para la aplicación React.

**Componentes Clave del Backend**:
-   `EngineInterface`: Un contrato común (clase abstracta) que todos los adaptadores de motor deben implementar. Define el método estándar `get_best_move(fen: str, depth: int) -> str`.
-   `EngineManager`: El punto central para gestionar los motores. Carga la configuración desde un archivo YAML, inicializa los adaptadores de motor apropiados (REST, UCI), y enruta las peticiones genéricas al adaptador correcto.
-   `RestEngineAdapter`: Un adaptador genérico para motores REST. Basado en la configuración declarativa en YAML, construye dinámicamente las llamadas HTTP (GET/POST) y extrae el mejor movimiento de la respuesta JSON utilizando `jsonpath`.
-   `UciEngineAdapter`: (Opcional) Un adaptador para motores UCI (Universal Chess Interface) locales, como Stockfish. Se comunica con el motor a través de un subproceso.

## Configuración de Motores (YAML)
Los motores se configuran en el archivo `config/engines.yaml` de forma declarativa. Cada entrada de motor define cómo conectarse y extraer información.

**Ejemplo de `config/engines.yaml`**:
```yaml
engines:
  lichess:
    method: GET
    url: "https://lichess.org/api/cloud-eval"
    params: {"fen": "{fen}", "depth": "{depth}"}
    extract: "pvs[0].moves"
  stockfish-local:
    type: uci
    command: "stockfish"
```

## Toma de Decisiones Tecnológicas

-   **Frontend (React + Vite)**: Se eligió React por su popularidad, ecosistema robusto y facilidad para construir interfaces de usuario interactivas. Vite se seleccionó como herramienta de construcción por su velocidad y eficiencia en el desarrollo. La decisión de cambiar de `chessboard2.js` a `react-chessboard` se tomó para una mejor integración con el paradigma de componentes de React y para evitar problemas de compatibilidad y manejo de estado, resultando en un código más limpio y fácil de mantener.
-   **Backend (FastAPI)**: FastAPI fue elegido por su alto rendimiento, facilidad de uso, y soporte nativo para la programación asíncrona (`async/await`), lo cual es ideal para manejar múltiples peticiones a motores externos concurrentemente. La validación de datos con Pydantic es una ventaja adicional.
-   **Configuración (YAML)**: El uso de YAML para la configuración de motores proporciona una forma flexible y declarativa de definir nuevos motores sin modificar el código del backend, facilitando la adición de nuevos motores o la adaptación a cambios en APIs existentes.
-   **Extracción de Datos (`jsonpath`)**: Se optó por la librería `jsonpath` para la extracción de datos de las respuestas JSON de los motores REST debido a su sintaxis intuitiva y su capacidad para navegar estructuras de datos complejas. Se migró de `jsonpath-ng` a `jsonpath` para resolver conflictos de importación que surgieron en el entorno de desarrollo.
-   **Contenedorización (Docker)**: La aplicación está diseñada para ser empaquetada en un `Dockerfile`, lo que facilita el despliegue en cualquier entorno que soporte contenedores. Esto asegura la portabilidad y la reproducibilidad del entorno de ejecución.

## Funcionalidades de las Partes

-   **`main.py` (Backend)**: Contiene la instancia de la aplicación FastAPI, el `EngineManager` inicializado, y los endpoints de la API (`/` para servir el frontend y `/move` para gestionar las jugadas de ajedrez). También maneja la configuración de archivos estáticos para el frontend.
-   **`engine_manager.py` (Backend)**: Define la `EngineInterface` y la clase `EngineManager`. Es responsable de cargar y gestionar las configuraciones de los motores, instanciando los adaptadores (`RestEngineAdapter`, `UciEngineAdapter`) según el tipo de motor definido en el YAML. También contiene la lógica para delegar las peticiones a los adaptadores correctos.
-   **`config/engines.yaml` (Configuración)**: Almacena las definiciones de los motores de ajedrez externos. Cada motor se especifica con su método de conexión (GET/POST), URL, plantilla de parámetros y la ruta de extracción para el mejor movimiento.
-   **`frontend/src/App.jsx` (Frontend)**: Es el componente raíz de la aplicación React. Utiliza `react-router-dom` para gestionar la navegación, presentando la `SelectionPage` en la ruta `/` y la `GamePage` en `/game`.
-   **`frontend/src/GamePage.jsx` (Frontend)**: El componente principal que renderiza el tablero de ajedrez interactivo. Contiene la lógica para manejar las interacciones del usuario (movimientos de piezas), validar movimientos con `chess.js`, comunicarse con el backend para obtener movimientos de motor, y actualizar el estado y la posición del tablero.
-   **`frontend/src/SelectionPage.jsx` (Frontend)**: (Refactorizado de `App.jsx`) Un componente que permite a los usuarios seleccionar los motores de ajedrez para la partida y navegar a la `GamePage` con las opciones seleccionadas.
-   **`Dockerfile`**: Define cómo construir la imagen Docker de la aplicación, incluyendo la construcción del frontend, la instalación de dependencias del backend y la configuración del servidor Uvicorn para servir tanto los archivos estáticos del frontend como la API de FastAPI.

## Cómo Iniciar el Proyecto (Desarrollo Local)

1.  **Backend (Python)**:
    -   Asegúrate de tener Miniconda/Anaconda instalado.
    -   Crea y activa el ambiente conda:
        ```bash
        conda create -n chess python=3.10 --yes
        conda activate chess
        ```
    -   Instala las dependencias de Python:
        ```bash
        pip install -r requirements.txt
        ```
    -   Inicia el servidor FastAPI (en segundo plano):
        ```bash
        uvicorn main:app --host 0.0.0.0 --port 8000 &
        ```

2.  **Frontend (React)**:
    -   Navega a la carpeta `frontend`:
        ```bash
        cd frontend
        ```
    -   Instala las dependencias de Node.js:
        ```bash
        npm install
        ```
    -   Inicia el servidor de desarrollo de React:
        ```bash
        npm run dev
        ```
    -   La aplicación estará disponible en `http://localhost:5173/` (o un puerto similar si el 5173 ya está en uso).

Ahora, puedes abrir tu navegador y acceder a la URL del frontend para empezar a usar la aplicación.
