
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine_manager import EngineManager


class MoveRequest(BaseModel):
    engine: str
    fen: str
    depth: int


app = FastAPI()

# Configurar CORS - Permitir conexiones desde cualquier origen (desarrollo local en red)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen (útil para desarrollo en red local)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine_manager = EngineManager()


@app.get("/")
async def read_root():
    return {
        "message": "Chess Trainer API",
        "version": "1.0.0",
        "endpoints": {
            "GET /engines": "Lista de motores disponibles",
            "POST /move": "Obtener mejor movimiento de un motor"
        }
    }


@app.get("/engines")
async def get_engines():
    """Devuelve la lista de motores disponibles"""
    return {"engines": list(engine_manager.engines.keys())}


@app.post("/move")
async def get_best_move(move_request: MoveRequest):
    engine = engine_manager.get_engine(move_request.engine)
    best_move = await engine.get_best_move(move_request.fen, move_request.depth)
    return {"bestmove": best_move}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
