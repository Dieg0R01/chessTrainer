
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine_manager import EngineManager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse


class MoveRequest(BaseModel):
    engine: str
    fen: str
    depth: int


app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Puertos comunes de Vite y React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine_manager = EngineManager()

# Montar los archivos estáticos del frontend
app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")


@app.get("/")
async def read_root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())


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
