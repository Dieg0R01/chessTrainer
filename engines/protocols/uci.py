"""
Protocolo UCI (Universal Chess Interface) para motores locales.
Soporta Stockfish, LCZero, y otros motores UCI estándar.
"""

import asyncio
import logging
import shutil
import os
from typing import Optional, Dict, Any
from .base import ProtocolBase

logger = logging.getLogger(__name__)


class UCIProtocol(ProtocolBase):
    """
    Implementa el protocolo UCI para comunicación con motores locales.
    Maneja el ciclo completo de comunicación UCI de forma centralizada.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el protocolo UCI.
        
        Args:
            config: Debe incluir 'command' (ejecutable del motor)
        """
        super().__init__(config)
        self.command = config.get("command")
        if not self.command:
            raise ValueError("UCIProtocol requiere 'command' en configuración")
        
        self.process: Optional[asyncio.subprocess.Process] = None
        self.current_fen: Optional[str] = None
    
    async def check_availability(self) -> bool:
        """
        Verifica si el comando del motor existe en el sistema.
        """
        # Si el comando empieza con "docker exec", verificar que docker y el contenedor estén disponibles
        if self.command.startswith("docker exec"):
            try:
                # Usar asyncio para ejecutar comandos de forma asíncrona
                import asyncio
                
                # Verificar que docker esté disponible
                proc = await asyncio.create_subprocess_exec(
                    "docker", "--version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await asyncio.wait_for(proc.wait(), timeout=5.0)
                if proc.returncode != 0:
                    return False
                
                # Extraer nombre del contenedor
                # Ejemplos: "docker exec chess-trainer stockfish" -> "chess-trainer"
                #          "docker exec -i chess-trainer /app/bin/lc0" -> "chess-trainer"
                parts = self.command.split()
                container_name = None
                
                # Buscar el nombre del contenedor (está después de "exec" o "-i")
                for i, part in enumerate(parts):
                    if part == "exec" and i + 1 < len(parts):
                        next_part = parts[i + 1]
                        if next_part == "-i" and i + 2 < len(parts):
                            container_name = parts[i + 2]
                        elif next_part != "-i":
                            container_name = next_part
                        break
                
                if container_name:
                    logger.debug(f"Verificando contenedor Docker: {container_name}")
                    # Verificar que el contenedor esté corriendo
                    proc = await asyncio.create_subprocess_exec(
                        "docker", "ps", "--format", "{{.Names}}",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5.0)
                    if proc.returncode == 0:
                        containers = stdout.decode().strip().split('\n')
                        logger.debug(f"Contenedores corriendo: {containers}")
                        if container_name in containers:
                            logger.debug(f"Contenedor {container_name} encontrado, motor disponible")
                            return True
                        else:
                            logger.warning(f"Contenedor {container_name} no encontrado en: {containers}")
                    else:
                        logger.warning(f"Error ejecutando docker ps: returncode={proc.returncode}")
                else:
                    logger.warning(f"No se pudo extraer nombre del contenedor de: {self.command}")
                return False
            except asyncio.TimeoutError:
                logger.warning(f"Timeout verificando disponibilidad de Docker para {self.command}")
                return False
            except Exception as e:
                logger.warning(f"Error verificando disponibilidad de Docker: {e}")
                return False
        
        # Comando normal: verificar si existe
        cmd_base = self.command.split()[0]
        
        # Verificar si es ruta absoluta o relativa
        if os.path.sep in cmd_base:
            return os.path.exists(cmd_base) and os.access(cmd_base, os.X_OK)
        
        # Verificar en el PATH
        return shutil.which(cmd_base) is not None

    async def initialize(self) -> None:
        """Inicia el proceso del motor UCI"""
        if self._initialized and self.process and self.process.returncode is None:
            logger.debug("UCIProtocol ya inicializado")
            return
        
        # Lock para evitar inicializaciones concurrentes
        if not hasattr(self, '_init_lock'):
            self._init_lock = asyncio.Lock()
        
        async with self._init_lock:
            # Verificar nuevamente después de adquirir el lock
            if self._initialized and self.process and self.process.returncode is None:
                logger.debug("UCIProtocol ya inicializado (después de lock)")
                return
            
            try:
                # Si el comando empieza con "docker exec", asegurar que tenga -i para mantener stdin interactivo
                command_parts = self.command.split()
                if command_parts[0] == "docker" and command_parts[1] == "exec":
                    # Insertar -i después de "exec" si no está presente
                    if "-i" not in command_parts:
                        command_parts.insert(2, "-i")
                    # Asegurar que el comando dentro del contenedor use ruta completa si es necesario
                    # Si el comando es "lc0" o "stockfish" sin ruta, intentar /app/bin/
                    if len(command_parts) >= 4:
                        cmd_in_container = command_parts[3]
                        if cmd_in_container in ["lc0", "stockfish"] and "/" not in cmd_in_container:
                            command_parts[3] = f"/app/bin/{cmd_in_container}"
                            logger.debug(f"Usando ruta completa para comando en Docker: {command_parts[3]}")
                    
                    self.process = await asyncio.create_subprocess_exec(
                        *command_parts,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                else:
                    # Comando normal
                    self.process = await asyncio.create_subprocess_exec(
                        *command_parts,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                
                # Protocolo de inicio UCI estándar
                await self._write("uci")
                await self._read_until("uciok")
                
                # Configurar opciones específicas
                await self._set_options()
                
                # Verificar que está listo
                await self._write("isready")
                await self._read_until("readyok")
                
                self._initialized = True
                logger.info(f"UCIProtocol inicializado: {self.command}")
                
            except Exception as e:
                logger.error(f"Error iniciando UCIProtocol: {e}")
                if self.process:
                    try:
                        self.process.kill()
                    except:
                        pass
                    self.process = None
                self._initialized = False
                raise
    
    async def _set_options(self) -> None:
        """Configura opciones específicas del motor UCI"""
        # Opciones para motores neuronales (LCZero, etc.)
        if weights := self.config.get("weights"):
            await self._write(f"setoption name WeightsFile value {weights}")
            logger.debug(f"Configurado WeightsFile: {weights}")
        
        if backend := self.config.get("backend"):
            await self._write(f"setoption name Backend value {backend}")
            logger.debug(f"Configurado Backend: {backend}")
        
        # Opciones UCI estándar
        if threads := self.config.get("threads"):
            await self._write(f"setoption name Threads value {threads}")
            logger.debug(f"Configurado Threads: {threads}")
        
        if hash_size := self.config.get("hash"):
            await self._write(f"setoption name Hash value {hash_size}")
            logger.debug(f"Configurado Hash: {hash_size}")
    
    async def send_position(self, fen: str) -> None:
        """
        Envía la posición al motor UCI.
        
        Args:
            fen: Posición en formato FEN
        """
        if not self._initialized:
            await self.initialize()
        
        self.current_fen = fen
        await self._write(f"position fen {fen}")
        logger.debug(f"Posición enviada: {fen[:50]}...")
    
    async def request_move(self, depth: Optional[int] = None, **kwargs) -> str:
        """
        Solicita el mejor movimiento al motor UCI.
        
        Args:
            depth: Profundidad de búsqueda
            **kwargs: Parámetros adicionales (ignorados)
            
        Returns:
            Movimiento en formato UCI (ej: "e2e4")
        """
        if not self._initialized:
            await self.initialize()
        
        # Verificar que el proceso sigue activo
        if not self.process or self.process.returncode is not None:
            logger.warning("Proceso UCI murió, reiniciando...")
            await self.initialize()
            if self.current_fen:
                await self.send_position(self.current_fen)
        
        # Determinar modo de búsqueda
        search_mode = self.config.get("search_mode", "depth")
        search_value = depth or self.config.get("default_depth") or self.config.get("default_search_value", 15)
        
        # Enviar comando de búsqueda según el modo
        if search_mode == "nodes":
            await self._write(f"go nodes {search_value}")
        elif search_mode == "time":
            await self._write(f"go movetime {search_value}")
        else:
            await self._write(f"go depth {search_value}")
        
        # Leer hasta obtener bestmove (con timeout)
        max_iterations = 1000
        iteration = 0
        timeout_seconds = 30.0  # Timeout para obtener bestmove
        
        while iteration < max_iterations:
            if not self.process or not self.process.stdout:
                raise RuntimeError("Proceso UCI perdió stdout")
            
            try:
                line = await asyncio.wait_for(
                    self.process.stdout.readline(),
                    timeout=timeout_seconds
                )
                decoded = line.decode().strip()
                logger.debug(f"UCIProtocol bestmove lectura: {decoded}")
                
                if decoded.startswith("bestmove"):
                    parts = decoded.split()
                    if len(parts) >= 2:
                        move = parts[1]
                        logger.info(f"Movimiento recibido de {self.config.get('name', 'motor')}: {move}")
                        return move
                    else:
                        raise ValueError(f"Formato de bestmove inválido: {decoded}")
                
                iteration += 1
            except asyncio.TimeoutError:
                logger.error(f"Timeout esperando bestmove después de {timeout_seconds}s")
                raise RuntimeError(f"Timeout esperando bestmove del motor UCI (más de {timeout_seconds}s)")
            except Exception as e:
                logger.error(f"Error leyendo bestmove: {e}")
                raise
        
        raise RuntimeError(f"No se recibió bestmove después de {max_iterations} iteraciones")
    
    async def _write(self, command: str) -> None:
        """
        Escribe un comando al proceso UCI.
        
        Args:
            command: Comando UCI a enviar
        """
        if not self.process or not self.process.stdin:
            raise RuntimeError("Proceso UCI no disponible para escribir")
        
        self.process.stdin.write(f"{command}\n".encode())
        await self.process.stdin.drain()
    
    async def _read_until(self, expected: str, timeout: float = 10.0) -> str:
        """
        Lee la salida del motor hasta encontrar el texto esperado.
        
        Args:
            expected: Texto a buscar en la salida
            timeout: Tiempo máximo de espera en segundos (default: 10s)
            
        Returns:
            Todas las líneas leídas hasta encontrar el texto
        """
        if not self.process or not self.process.stdout:
            raise RuntimeError("Proceso UCI no tiene stdout disponible")
        
        output_lines = []
        max_iterations = 1000  # Límite de seguridad
        iteration = 0
        
        while iteration < max_iterations:
            try:
                line = await asyncio.wait_for(
                    self.process.stdout.readline(),
                    timeout=timeout
                )
                decoded = line.decode().strip()
                output_lines.append(decoded)
                logger.debug(f"UCIProtocol leído: {decoded}")
                
                if expected in decoded:
                    return "\n".join(output_lines)
                
                iteration += 1
            except asyncio.TimeoutError:
                output_preview = "\n".join(output_lines[-10:])
                logger.error(f"Timeout esperando '{expected}' en UCIProtocol. Output recibido: {output_preview}")
                raise RuntimeError(f"Timeout esperando respuesta '{expected}' del motor UCI")
            except Exception as e:
                logger.error(f"Error leyendo de UCIProtocol: {e}")
                raise
        
        raise RuntimeError(f"No se encontró '{expected}' después de {max_iterations} iteraciones")
    
    async def cleanup(self) -> None:
        """Cierra el proceso del motor UCI"""
        if self.process and self.process.returncode is None:
            try:
                await self._write("quit")
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
                logger.info("Proceso UCI cerrado correctamente")
            except asyncio.TimeoutError:
                logger.warning("Timeout cerrando proceso UCI, forzando kill")
                self.process.kill()
                await self.process.wait()
            except Exception as e:
                logger.warning(f"Error cerrando UCIProtocol: {e}")
                self.process.kill()
            finally:
                self.process = None
                self._initialized = False
