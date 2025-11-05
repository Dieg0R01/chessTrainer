"""
Módulo de motores de ajedrez.
Proporciona una arquitectura flexible para trabajar con diferentes tipos de motores.
Actualizado con sistema de protocolos para separar comunicación de lógica de negocio.
"""

from .base import MotorBase, MotorType, MotorOrigin, ValidationMode
from .factory import EngineFactory, EngineRegistry, EngineClassifier
from .traditional import TraditionalEngine
from .neuronal import NeuronalEngine
from .generative import GenerativeEngine
from .validators import SchemaValidator, PromptValidator, ValidatorFactory

# Protocolos (exportados para uso avanzado)
from .protocols import (
    ProtocolBase,
    UCIProtocol,
    RESTProtocol,
    LocalLLMProtocol,
    APILLMProtocol
)

__all__ = [
    # Clases base
    'MotorBase',
    'MotorType',
    'MotorOrigin',
    'ValidationMode',
    
    # Factory y Registry
    'EngineFactory',
    'EngineRegistry',
    'EngineClassifier',
    
    # Motores
    'TraditionalEngine',
    'NeuronalEngine',
    'GenerativeEngine',
    
    # Validadores
    'SchemaValidator',
    'PromptValidator',
    'ValidatorFactory',
    
    # Protocolos
    'ProtocolBase',
    'UCIProtocol',
    'RESTProtocol',
    'LocalLLMProtocol',
    'APILLMProtocol',
]

__version__ = '2.0.0'
__author__ = 'Chess Trainer Development Team'
