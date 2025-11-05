"""
Módulo de protocolos de comunicación para motores de ajedrez.
Separa la lógica de comunicación de la lógica del motor.
"""

from .base import ProtocolBase
from .uci import UCIProtocol
from .rest import RESTProtocol
from .local_llm import LocalLLMProtocol
from .api_llm import APILLMProtocol

__all__ = [
    'ProtocolBase',
    'UCIProtocol',
    'RESTProtocol',
    'LocalLLMProtocol',
    'APILLMProtocol'
]

