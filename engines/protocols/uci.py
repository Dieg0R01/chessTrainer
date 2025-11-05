"""
Protocolo UCI (Universal Chess Interface) para motores locales.
Soporta Stockfish, LCZero, y otros motores UCI estándar.
"""

import asyncio
import logging
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
    
    async def initialize(self) -> None:
        """Inicia el proceso del motor UCI"""
        if self._initialized and self.process and self.process.returncode is None:
            logger.debug("UCIProtocol ya inicializado")
            return
        
        try:
            # Iniciar proceso
            self.process = await asyncio.create_subprocess_exec(
                *self.command.split(),
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
                self.process.kill()
                self.process = None
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
        
        # Leer hasta obtener bestmove
        while True:
            if not self.process or not self.process.stdout:
                raise RuntimeError("Proceso UCI perdió stdout")
            
            line = await self.process.stdout.readline()
            decoded = line.decode().strip()
            
            if decoded.startswith("bestmove"):
                parts = decoded.split()
                if len(parts) >= 2:
                    move = parts[1]
                    logger.debug(f"Movimiento recibido: {move}")
                    return move
                else:
                    raise ValueError(f"Formato de bestmove inválido: {decoded}")
    
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
    
    async def _read_until(self, expected: str) -> str:
        """
        Lee la salida del motor hasta encontrar el texto esperado.
        
        Args:
            expected: Texto a buscar en la salida
            
        Returns:
            Todas las líneas leídas hasta encontrar el texto
        """
        if not self.process or not self.process.stdout:
            raise RuntimeError("Proceso UCI no tiene stdout disponible")
        
        output_lines = []
        while True:
            line = await self.process.stdout.readline()
            decoded = line.decode().strip()
            output_lines.append(decoded)
            
            if expected in decoded:
                return "\n".join(output_lines)
    
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

