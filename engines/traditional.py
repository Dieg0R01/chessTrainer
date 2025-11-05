"""
Motores tradicionales deterministas (minimax, alfa-beta, etc.)
Ejemplos: Stockfish, Komodo
Refactorizado para usar protocolos de comunicación mediante composición.
"""

import logging
from typing import Any, Dict, Optional

from .base import MotorBase, MotorType, MotorOrigin, ValidationMode
from .protocols import UCIProtocol, RESTProtocol
from .validators import SchemaValidator

logger = logging.getLogger(__name__)


class TraditionalEngine(MotorBase):
    """
    Motor tradicional que puede usar UCI o REST.
    La comunicación se delega al protocolo correspondiente mediante composición.
    Implementa el patrón Bridge para separar lógica de negocio de comunicación.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Inicializa un motor tradicional.
        
        Args:
            name: Nombre del motor
            config: Configuración que especifica el protocolo y parámetros
        """
        # Determinar protocolo basado en configuración
        if "command" in config:
            protocol_type = "uci"
            origin = MotorOrigin.INTERNAL
        elif "url" in config:
            protocol_type = "rest"
            origin = MotorOrigin.EXTERNAL
        else:
            raise ValueError(
                f"Motor tradicional '{name}' requiere 'command' (UCI) o 'url' (REST) en configuración"
            )
        
        super().__init__(
            name=name,
            motor_type=MotorType.TRADITIONAL,
            motor_origin=origin,
            validation_mode=ValidationMode.SCHEMA,
            config=config
        )
        
        # Crear protocolo mediante composición (patrón Bridge)
        if protocol_type == "uci":
            self.protocol = UCIProtocol(config)
            logger.info(f"Motor tradicional {name} usando UCIProtocol")
        else:
            self.protocol = RESTProtocol(config)
            logger.info(f"Motor tradicional {name} usando RESTProtocol")
        
        self.validator = SchemaValidator()
    
    async def _do_initialize(self):
        """Inicializa el protocolo de comunicación"""
        await self.protocol.initialize()
    
    async def get_move(self, board_state: str, depth: Optional[int] = None, **kwargs) -> str:
        """
        Obtiene el mejor movimiento delegando al protocolo.
        
        Args:
            board_state: Posición en formato FEN
            depth: Profundidad de búsqueda
            **kwargs: Parámetros adicionales
            
        Returns:
            Mejor movimiento en formato UCI
        """
        # Asegurar inicialización
        await self.initialize()
        
        # Enviar posición al protocolo
        await self.protocol.send_position(board_state)
        
        # Solicitar movimiento
        move = await self.protocol.request_move(depth, **kwargs)
        
        # Validar movimiento
        if not await self.validate_response(move):
            raise ValueError(f"Motor {self.name} retornó movimiento inválido: {move}")
        
        logger.info(f"Motor tradicional {self.name} sugiere: {move}")
        return move
    
    async def validate_response(self, response: Any) -> bool:
        """
        Valida que la respuesta sea un movimiento UCI válido.
        
        Args:
            response: Movimiento a validar
            
        Returns:
            True si es válido
        """
        if not isinstance(response, str):
            return False
        return self.validator.validate_uci_move(response)
    
    async def _do_cleanup(self):
        """Limpia recursos del protocolo"""
        await self.protocol.cleanup()
