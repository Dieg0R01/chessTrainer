"""
Módulo base que define la interfaz común para todos los motores de ajedrez.
Implementa el patrón Strategy.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MotorType(Enum):
    """Naturaleza del motor de ajedrez"""
    TRADITIONAL = "traditional"  # Motores deterministas clásicos (minimax, alfa-beta)
    NEURONAL = "neuronal"        # Motores basados en redes neuronales
    GENERATIVE = "generative"    # Motores basados en LLMs o agentes


class MotorOrigin(Enum):
    """Origen del servicio del motor"""
    INTERNAL = "internal"  # Contenedores propios, procesos locales
    EXTERNAL = "external"  # APIs públicas, servicios remotos


class ValidationMode(Enum):
    """Modo de validación de la respuesta del motor"""
    SCHEMA = "schema"      # Validación estricta con schema/regex
    PROMPT = "prompt"      # Validación por parsing de texto LLM


class MotorBase(ABC):
    """
    Clase base abstracta para todos los motores de ajedrez.
    Implementa el patrón Strategy para encapsular diferentes algoritmos.
    """
    
    def __init__(
        self,
        name: str,
        motor_type: MotorType,
        motor_origin: MotorOrigin,
        validation_mode: ValidationMode,
        config: Dict[str, Any]
    ):
        """
        Inicializa el motor con configuración base.
        
        Args:
            name: Nombre identificador del motor
            motor_type: Tipo de motor (traditional, neuronal, generative)
            motor_origin: Origen del motor (internal, external)
            validation_mode: Modo de validación (schema, prompt)
            config: Configuración específica del motor
        """
        self.name = name
        self.motor_type = motor_type
        self.motor_origin = motor_origin
        self.validation_mode = validation_mode
        self.config = config
        self._initialized = False
        
        logger.info(
            f"Motor creado: {name} | Tipo: {motor_type.value} | "
            f"Origen: {motor_origin.value} | Validación: {validation_mode.value}"
        )
    
    @abstractmethod
    async def get_move(self, board_state: str, depth: Optional[int] = None, **kwargs) -> str:
        """
        Obtiene el mejor movimiento para un estado del tablero dado.
        
        Args:
            board_state: Estado del tablero (FEN, PGN, etc.)
            depth: Profundidad de análisis (para motores que lo soporten)
            **kwargs: Parámetros adicionales específicos del motor
            
        Returns:
            Movimiento en notación algebraica (ej: "e2e4")
        """
        pass
    
    @abstractmethod
    async def validate_response(self, response: Any) -> bool:
        """
        Valida la respuesta del motor según el modo de validación.
        
        Args:
            response: Respuesta del motor a validar
            
        Returns:
            True si la respuesta es válida
        """
        pass
    
    async def initialize(self) -> None:
        """Inicializa el motor (si requiere setup previo)"""
        if not self._initialized:
            await self._do_initialize()
            self._initialized = True
            logger.info(f"Motor {self.name} inicializado correctamente")
    
    async def _do_initialize(self) -> None:
        """Hook para implementar lógica de inicialización específica"""
        pass
    
    async def cleanup(self) -> None:
        """Limpia recursos del motor al finalizar"""
        if self._initialized:
            await self._do_cleanup()
            self._initialized = False
            logger.info(f"Motor {self.name} limpiado correctamente")
    
    async def _do_cleanup(self) -> None:
        """Hook para implementar lógica de limpieza específica"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Retorna información descriptiva del motor"""
        return {
            "name": self.name,
            "type": self.motor_type.value,
            "origin": self.motor_origin.value,
            "validation_mode": self.validation_mode.value,
            "initialized": self._initialized
        }
    
    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(name='{self.name}', "
            f"type={self.motor_type.value}, origin={self.motor_origin.value})"
        )
    
    def __repr__(self) -> str:
        return self.__str__()
