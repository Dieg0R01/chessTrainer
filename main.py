"""
Chess Trainer API - Backend FastAPI
Proporciona endpoints para interactuar con múltiples motores de ajedrez.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from engine_manager import EngineManager
from engines import MotorType, MotorOrigin
from engines.generative import get_valid_strategies, get_strategy_info
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de CORS óptima
def get_cors_origins() -> List[str]:
    """
    Obtiene los orígenes permitidos para CORS.
    En desarrollo permite localhost con diferentes puertos.
    En producción usa variable de entorno o lista específica.
    """
    # Obtener orígenes desde variable de entorno si existe
    cors_origins_env = os.getenv("CORS_ORIGINS")
    if cors_origins_env:
        return [origin.strip() for origin in cors_origins_env.split(",")]
    
    # En desarrollo, permitir localhost con diferentes puertos comunes
    is_production = os.getenv("ENVIRONMENT") == "production"
    
    if not is_production:
        # Desarrollo: permitir localhost en puertos comunes
        return [
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # React dev server común
            "http://localhost:8080",  # Otro puerto común
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
        ]
    
    # Producción: solo orígenes específicos (configurar según tu dominio)
    return [
        "https://tudominio.com",
        "https://www.tudominio.com",
    ]


# Modelos Pydantic
class MoveRequest(BaseModel):
    """Request para obtener un movimiento"""
    engine: str = Field(..., description="Nombre del motor a usar")
    fen: str = Field(..., description="Posición del tablero en formato FEN")
    depth: Optional[int] = Field(None, description="Profundidad de análisis")
    move_history: Optional[str] = Field("", description="Histórico de movimientos (para motores generativos)")
    strategy: Optional[str] = Field(
        None, 
        description="Estrategia de juego (para motores generativos, opcional). El modelo elegirá automáticamente después de 4 movimientos. Opciones: balanced, aggressive, defensive, tactical, positional, material, king_safety"
    )
    explanation: Optional[bool] = Field(False, description="Solicitar explicación (motores generativos)")


class MoveResponse(BaseModel):
    """Response con el movimiento sugerido"""
    engine: str
    bestmove: str
    explanation: Optional[str] = None


class EngineInfo(BaseModel):
    """Información de un motor"""
    name: str
    type: str
    origin: str
    validation_mode: str
    initialized: bool


class CompareRequest(BaseModel):
    """Request para comparar motores"""
    fen: str = Field(..., description="Posición del tablero en formato FEN")
    depth: Optional[int] = Field(None, description="Profundidad de análisis")


# Crear aplicación FastAPI
app = FastAPI(
    title="Chess Trainer API",
    description="API para entrenar y analizar partidas de ajedrez con múltiples motores",
    version="2.0.0"
)

# Configurar CORS de manera óptima
cors_origins = get_cors_origins()
logger.info(f"CORS configurado para orígenes: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Solo métodos necesarios
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],  # Solo headers necesarios
    expose_headers=["Content-Type"],  # Headers que el frontend puede leer
    max_age=3600,  # Cache de preflight requests por 1 hora
)

# Log de inicio para debugging
logger.info("=" * 50)
logger.info("Chess Trainer API iniciando...")
logger.info(f"Backend URL: http://0.0.0.0:8000")
logger.info(f"CORS permitiendo orígenes: {cors_origins}")
logger.info("=" * 50)

# Inicializar gestor de motores
engine_manager = EngineManager()

# Solo montar archivos estáticos si existe el directorio dist (modo producción)
if os.path.exists("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("Iniciando Chess Trainer API v2.0.0")
    logger.info(f"Motores cargados: {len(engine_manager)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("Cerrando Chess Trainer API")
    await engine_manager.cleanup_all()


@app.get("/")
async def read_root():
    # Si existe frontend/dist, servir el HTML de producción
    if os.path.exists("frontend/dist/index.html"):
        with open("frontend/dist/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    # En desarrollo, redirigir al servidor de Vite
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=http://localhost:5173">
    </head>
    <body>
        <p>Redirigiendo a <a href="http://localhost:5173">http://localhost:5173</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api")
async def api_info():
    """Información de la API"""
    return {
        "message": "Chess Trainer API",
        "version": "2.0.0",
        "engines_loaded": len(engine_manager),
        "endpoints": {
            "GET /": "Servir frontend o redirigir a desarrollo",
            "GET /api": "Información de la API",
            "GET /engines": "Lista de motores disponibles",
            "GET /engines/info": "Información detallada de motores",
            "GET /engines/matrix": "Matriz de clasificación de motores",
            "POST /move": "Obtener mejor movimiento de un motor",
            "POST /compare": "Comparar sugerencias de todos los motores",
            "GET /strategies": "Lista de estrategias disponibles para motores generativos",
            "GET /health": "Estado de salud de la API"
        }
    }


@app.get("/health")
async def health_check():
    """Verifica el estado de salud de la API"""
    return {
        "status": "healthy",
        "engines": len(engine_manager),
        "version": "2.0.0"
    }


@app.get("/engines")
async def get_engines():
    """Lista todos los motores disponibles"""
    try:
        engines = engine_manager.list_engines()
        logger.info(f"Listando {len(engines)} motores disponibles")
        
        # Asegurar que engines es una lista
        if not isinstance(engines, list):
            logger.warning(f"list_engines() no retornó una lista, convirtiendo...")
            engines = list(engines) if engines else []
        
        response = {
            "engines": engines,
            "count": len(engines)
        }
        
        logger.debug(f"Respuesta /engines: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error listando motores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/engines/info")
async def get_engines_info():
    """Obtiene información detallada de todos los motores"""
    try:
        info = engine_manager.get_engines_info()
        return {
            "engines": info,
            "count": len(info)
        }
    except Exception as e:
        logger.error(f"Error obteniendo información de motores: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/engines/matrix")
async def get_classification_matrix():
    """
    Obtiene la matriz de clasificación de motores.
    Muestra tipo, origen y modo de validación de cada motor.
    """
    try:
        matrix = engine_manager.get_classification_matrix()
        return {
            "matrix": matrix,
            "count": len(matrix),
            "description": {
                "type": ["traditional", "neuronal", "generative"],
                "origin": ["internal", "external"],
                "validation_mode": ["schema", "prompt"]
            }
        }
    except Exception as e:
        logger.error(f"Error generando matriz de clasificación: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/engines/filter/type/{motor_type}")
async def filter_engines_by_type(motor_type: str):
    """Filtra motores por tipo (traditional, neuronal, generative)"""
    try:
        # Convertir string a enum
        if motor_type == "traditional":
            type_enum = MotorType.TRADITIONAL
        elif motor_type == "neuronal":
            type_enum = MotorType.NEURONAL
        elif motor_type == "generative":
            type_enum = MotorType.GENERATIVE
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo inválido. Use: traditional, neuronal, generative"
            )
        
        filtered = engine_manager.filter_engines_by_type(type_enum)
        return {
            "type": motor_type,
            "engines": list(filtered.keys()),
            "count": len(filtered)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtrando por tipo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/engines/filter/origin/{motor_origin}")
async def filter_engines_by_origin(motor_origin: str):
    """Filtra motores por origen (internal, external)"""
    try:
        # Convertir string a enum
        if motor_origin == "internal":
            origin_enum = MotorOrigin.INTERNAL
        elif motor_origin == "external":
            origin_enum = MotorOrigin.EXTERNAL
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Origen inválido. Use: internal, external"
            )
        
        filtered = engine_manager.filter_engines_by_origin(origin_enum)
        return {
            "origin": motor_origin,
            "engines": list(filtered.keys()),
            "count": len(filtered)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtrando por origen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/move", response_model=MoveResponse)
async def get_best_move(move_request: MoveRequest):
    """
    Obtiene el mejor movimiento de un motor específico.
    
    Soporta parámetros adicionales para motores generativos:
    - move_history: Histórico de movimientos
    - strategy: Estrategia deseada (balanced, aggressive, defensive, tactical, positional, material, king_safety)
    - explanation: Solicitar explicación del movimiento
    
    Estrategias disponibles:
    - balanced: Equilibrio entre táctica y posición (por defecto)
    - aggressive: Juego agresivo, busca ataque y combinaciones
    - defensive: Juego defensivo, prioriza seguridad
    - tactical: Enfoque en combinaciones y tácticas
    - positional: Enfoque en estructura y planes a largo plazo
    - material: Prioriza ganancia de material
    - king_safety: Prioriza seguridad del rey
    """
    try:
        # Preparar kwargs para el motor
        kwargs = {}
        if move_request.move_history:
            kwargs["move_history"] = move_request.move_history
            logger.info(f"📜 Historial recibido para motor {move_request.engine}: {move_request.move_history[:100]}...")
        else:
            logger.warning(f"⚠️ No se recibió historial de movimientos para motor {move_request.engine}")
        # La estrategia ahora es opcional - el modelo la elegirá automáticamente después de 4 movimientos
        if move_request.strategy:
            # Validar estrategia si se proporciona explícitamente
            valid_strategies = get_valid_strategies()
            if move_request.strategy.lower() not in [s.lower() for s in valid_strategies]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estrategia inválida: '{move_request.strategy}'. "
                           f"Estrategias válidas: {', '.join(valid_strategies)}"
                )
            kwargs["strategy"] = move_request.strategy
        if move_request.explanation:
            kwargs["explanation"] = move_request.explanation
        
        # Obtener movimiento
        best_move = await engine_manager.get_best_move(
            move_request.engine,
            move_request.fen,
            move_request.depth,
            **kwargs
        )
        
        response = MoveResponse(
            engine=move_request.engine,
            bestmove=best_move
        )
        
        # Si es motor generativo y se solicitó explicación
        if move_request.explanation:
            try:
                engine = engine_manager.get_engine(move_request.engine)
                if hasattr(engine, 'get_last_explanation'):
                    explanation = engine.get_last_explanation()
                    if explanation:
                        response.explanation = explanation
            except Exception as e:
                logger.warning(f"No se pudo obtener explicación: {e}")
        
        return response
        
    except ValueError as e:
        logger.warning(f"Error de validación: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error obteniendo movimiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/strategies")
async def get_strategies():
    """
    Obtiene la lista de estrategias disponibles para motores generativos.
    """
    try:
        valid_strategies = get_valid_strategies()
        strategies_info = {}
        
        for strategy_name in valid_strategies:
            info = get_strategy_info(strategy_name)
            strategies_info[strategy_name] = {
                "name": info.get("name", strategy_name),
                "description": info.get("description", ""),
                "prompt_hint": info.get("prompt_hint", "")
            }
        
        return {
            "strategies": strategies_info,
            "count": len(valid_strategies),
            "default": "balanced"
        }
    except Exception as e:
        logger.error(f"Error obteniendo estrategias: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
async def compare_engines(compare_request: CompareRequest):
    """
    Compara las sugerencias de todos los motores disponibles para una posición.
    Útil para análisis y comparación de diferentes enfoques.
    """
    try:
        results = await engine_manager.compare_engines(
            compare_request.fen,
            compare_request.depth
        )
        
        return {
            "fen": compare_request.fen,
            "results": results,
            "engines_compared": len(results)
        }
    except Exception as e:
        logger.error(f"Error comparando motores: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reload")
async def reload_configuration():
    """
    Recarga la configuración de motores desde el archivo YAML.
    Útil para añadir o modificar motores sin reiniciar el servidor.
    """
    try:
        # Limpiar motores actuales
        await engine_manager.cleanup_all()
        
        # Recargar configuración
        engine_manager.reload_config()
        
        return {
            "status": "success",
            "message": "Configuración recargada",
            "engines_loaded": len(engine_manager)
        }
    except Exception as e:
        logger.error(f"Error recargando configuración: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
