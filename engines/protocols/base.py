"""
Clase base para protocolos de comunicación con motores.
Implementa el patrón Bridge para separar comunicación de lógica de negocio.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ProtocolBase(ABC):
    """
    Clase base abstracta para protocolos de comunicación.
    Define la interfaz común que todos los protocolos deben implementar.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el protocolo con configuración.
        
        Args:
            config: Configuración específica del protocolo
        """
        self.config = config
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Inicializa el protocolo de comunicación.
        Debe ser llamado antes de usar el protocolo.
        """
        pass
    
    @abstractmethod
    async def send_position(self, fen: str) -> None:
        """
        Envía la posición del tablero al motor.
        
        Args:
            fen: Posición en formato FEN
        """
        pass
    
    @abstractmethod
    async def request_move(self, depth: Optional[int] = None, **kwargs) -> str:
        """
        Solicita el mejor movimiento al motor.
        
        Args:
            depth: Profundidad de análisis (si aplica)
            **kwargs: Parámetros adicionales específicos del protocolo
            
        Returns:
            Movimiento en formato UCI o respuesta del motor
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        Limpia recursos utilizados por el protocolo.
        Debe ser llamado al finalizar el uso del protocolo.
        """
        pass
    
    @property
    def is_initialized(self) -> bool:
        """Indica si el protocolo está inicializado"""
        return self._initialized

