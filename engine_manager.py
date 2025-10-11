from abc import ABC, abstractmethod
import yaml
import httpx
import asyncio
from jsonpath import jsonpath


class EngineInterface(ABC):
    @abstractmethod
    def get_best_move(self, fen: str, depth: int) -> str:
        pass


class UciEngineAdapter(EngineInterface):
    def __init__(self, config: dict):
        self.command = config["command"]
        self.process = None

    async def _start_engine(self):
        self.process = await asyncio.create_subprocess_exec(
            *self.command.split(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )
        await self._read_until("uciok")
        await self._write_command("isready")
        await self._read_until("readyok")

    async def _write_command(self, command: str):
        if self.process and self.process.stdin:  # type: ignore
            self.process.stdin.write(f"{command}\n".encode())
            await self.process.stdin.drain()

    async def _read_until(self, expected_output: str) -> str:
        output = []
        while True:
            if self.process and self.process.stdout:  # type: ignore
                line = await self.process.stdout.readline()
                line = line.decode().strip()
                output.append(line)
                if expected_output in line:
                    return "\n".join(output)
            else:
                raise RuntimeError("Motor UCI no iniciado o canal de salida no disponible.")

    async def get_best_move(self, fen: str, depth: int) -> str:
        if not self.process or self.process.returncode is not None:
            await self._start_engine()

        await self._write_command(f"position fen {fen}")
        await self._write_command(f"go depth {depth}")
        
        while True:
            output_line = await self.process.stdout.readline() # type: ignore
            decoded_line = output_line.decode().strip()
            if decoded_line.startswith("bestmove"):
                return decoded_line.split()[1]


class RestEngineAdapter(EngineInterface):
    def __init__(self, config: dict):
        self.method = config["method"]
        self.url = config["url"]
        self.params_template = config.get("params", {})
        self.extract_path = config["extract"]

    async def get_best_move(self, fen: str, depth: int) -> str:
        # Formatear los parámetros
        formatted_params = {}
        for k, v in self.params_template.items():
            formatted_value = v.format(fen=fen, depth=depth)
            formatted_params[k] = formatted_value
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            if self.method.upper() == "GET":
                # Para Lichess, construir la URL manualmente para evitar problemas de codificación
                response = await client.get(self.url, params=formatted_params)
            elif self.method.upper() == "POST":
                response = await client.post(self.url, json=formatted_params)
            else:
                raise ValueError(f"Método HTTP no soportado: {self.method}")
            # Manejar respuestas de error específicas de la API
            if response.status_code == 404:
                data = response.json()
                error_msg = data.get('error', 'Recurso no encontrado')
                raise ValueError(f"API Error: {error_msg}. La posición no está en la base de datos de Lichess cloud.")
            
            response.raise_for_status()
            data = response.json()
            
            # Extracción del mejor movimiento usando jsonpath
            result = jsonpath(data, self.extract_path)
            if result:
                # Si el resultado es una cadena de movimientos (ej: "e2e4 e7e5"), tomar solo el primero
                moves_string = result[0]
                if isinstance(moves_string, str) and ' ' in moves_string:
                    return moves_string.split()[0]
                return moves_string
            else:
                raise ValueError(f"No se pudo extraer el mejor movimiento de la respuesta con '{self.extract_path}': {data}")


class EngineManager:
    def __init__(self, config_path: str = "config/engines.yaml"):
        self.engines = {}
        self.load_config(config_path)

    def load_config(self, config_path: str):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        for engine_name, engine_config in config.get("engines", {}).items():
            engine_type = engine_config.get("type", "rest") # Por defecto, REST
            if engine_type == "rest":
                self.engines[engine_name] = RestEngineAdapter(engine_config)
            elif engine_type == "uci":
                self.engines[engine_name] = UciEngineAdapter(engine_config)
            else:
                raise ValueError(f"Tipo de motor no soportado: {engine_type}")

    def get_engine(self, name: str) -> EngineInterface:
        if name not in self.engines:
            raise ValueError(f"Motor '{name}' no encontrado en la configuración.")
        return self.engines[name]
