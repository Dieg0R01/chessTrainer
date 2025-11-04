"""
Chess Trainer API - Backend FastAPI
Proporciona endpoints para interactuar con múltiples motores de ajedrez.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from engine_manager import EngineManager
from engines import MotorType, MotorOrigin
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Modelos Pydantic
class MoveRequest(BaseModel):
    """Request para obtener un movimiento"""
    engine: str = Field(..., description="Nombre del motor a usar")
    fen: str = Field(..., description="Posición del tablero en formato FEN")
    depth: Optional[int] = Field(None, description="Profundidad de análisis")
    move_history: Optional[str] = Field("", description="Histórico de movimientos (para motores generativos)")
    strategy: Optional[str] = Field("balanced", description="Estrategia (para motores generativos)")
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

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar gestor de motores
engine_manager = EngineManager()


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
    """Endpoint raíz con información de la API"""
    return {
        "message": "Chess Trainer API",
        "version": "2.0.0",
        "engines_loaded": len(engine_manager),
        "endpoints": {
            "GET /": "Información de la API",
            "GET /engines": "Lista de motores disponibles",
            "GET /engines/info": "Información detallada de motores",
            "GET /engines/matrix": "Matriz de clasificación de motores",
            "POST /move": "Obtener mejor movimiento de un motor",
            "POST /compare": "Comparar sugerencias de todos los motores",
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
        return {
            "engines": engines,
            "count": len(engines)
        }
    except Exception as e:
        logger.error(f"Error listando motores: {e}")
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
    - strategy: Estrategia deseada
    - explanation: Solicitar explicación del movimiento
    """
    try:
        # Preparar kwargs para el motor
        kwargs = {}
        if move_request.move_history:
            kwargs["move_history"] = move_request.move_history
        if move_request.strategy:
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
