
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine_manager import EngineManager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os


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

# Solo montar archivos estáticos si existe el directorio dist (modo producción)
if os.path.exists("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")


@app.get("/")
async def read_root():
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
