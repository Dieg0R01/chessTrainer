"""
Motores neuronales basados en redes neuronales.
Ejemplos: Leela Chess Zero (LCZero), AlphaZero
Refactorizado para usar protocolos de comunicación mediante composición.
"""

import logging
from typing import Any, Dict, Optional

from .base import MotorBase, MotorType, MotorOrigin, ValidationMode
from .protocols import UCIProtocol, RESTProtocol
from .validators import SchemaValidator

logger = logging.getLogger(__name__)


class NeuronalEngine(MotorBase):
    """
    Motor neuronal que puede usar UCI o REST.
    La comunicación se delega al protocolo correspondiente mediante composición.
    Implementa el patrón Bridge para separar lógica de negocio de comunicación.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Inicializa un motor neuronal.
        
        Args:
            name: Nombre del motor
            config: Configuración que especifica el protocolo y parámetros
        """
        # Determinar protocolo basado en configuración
        protocol_name = config.get("protocol", "uci")
        
        if protocol_name == "uci":
            origin = MotorOrigin.INTERNAL
        elif protocol_name in ["rest", "http"]:
            origin = MotorOrigin.EXTERNAL
        else:
            raise ValueError(
                f"Protocolo no soportado para motor neuronal: {protocol_name}. "
                "Use 'uci' o 'rest'"
            )
        
        super().__init__(
            name=name,
            motor_type=MotorType.NEURONAL,
            motor_origin=origin,
            validation_mode=ValidationMode.SCHEMA,
            config=config
        )
        
        # Crear protocolo mediante composición (patrón Bridge)
        if protocol_name == "uci":
            self.protocol = UCIProtocol(config)
            logger.info(f"Motor neuronal {name} usando UCIProtocol")
        else:
            self.protocol = RESTProtocol(config)
            logger.info(f"Motor neuronal {name} usando RESTProtocol")
        
        self.validator = SchemaValidator()
    
    async def _do_initialize(self):
        """Inicializa el protocolo de comunicación"""
        await self.protocol.initialize()
    
    async def get_move(self, board_state: str, depth: Optional[int] = None, **kwargs) -> str:
        """
        Obtiene el mejor movimiento delegando al protocolo.
        
        Args:
            board_state: Posición en formato FEN
            depth: Profundidad/nodos (motores neuronales pueden usar nodos en vez de profundidad)
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
            raise ValueError(f"Motor neuronal {self.name} retornó movimiento inválido: {move}")
        
        logger.info(f"Motor neuronal {self.name} sugiere: {move}")
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
