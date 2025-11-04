"""
Motores generativos basados en LLMs o frameworks de agentes.
Ejemplos: GPT-Chess-Assistant, modelos locales con LangChain/LangGraph
Refactorizado para usar protocolos de comunicación mediante composición.
"""

import logging
from typing import Any, Dict, Optional
import os
import yaml

from .base import MotorBase, MotorType, MotorOrigin, ValidationMode
from .protocols import LocalLLMProtocol, APILLMProtocol
from .validators import PromptValidator

logger = logging.getLogger(__name__)


class GenerativeEngine(MotorBase):
    """
    Motor generativo que usa LLMs para generar movimientos.
    La comunicación se delega a protocolos especializados (Local o API).
    Implementa el patrón Bridge para separar lógica de negocio de comunicación.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Inicializa un motor generativo.
        
        Args:
            name: Nombre del motor
            config: Configuración que incluye provider, modelo y prompts
        """
        # Determinar provider
        provider = config.get("provider", "openai")
        origin = MotorOrigin.INTERNAL if provider == "local" else MotorOrigin.EXTERNAL
        
        super().__init__(
            name=name,
            motor_type=MotorType.GENERATIVE,
            motor_origin=origin,
            validation_mode=ValidationMode.PROMPT,
            config=config
        )
        
        self.provider = provider
        self.validator = PromptValidator()
        
        # Crear protocolo según proveedor (patrón Bridge)
        if provider == "local":
            self.protocol = LocalLLMProtocol(config)
            logger.info(f"Motor generativo {name} usando LocalLLMProtocol")
        else:
            # Proveedores externos: openai, anthropic, cohere, google, etc.
            self.protocol = APILLMProtocol(config)
            logger.info(f"Motor generativo {name} usando APILLMProtocol ({provider})")
        
        # Cargar template de prompt
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """
        Carga el template de prompt desde archivo o configuración.
        
        Returns:
            Template de prompt formateado
        """
        # Si hay archivo de prompt configurado
        prompt_file = self.config.get("prompt_template_file")
        
        if prompt_file and os.path.exists(prompt_file):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    if prompt_file.endswith('.yaml') or prompt_file.endswith('.yml'):
                        prompt_data = yaml.safe_load(f)
                        return prompt_data.get("template", self._default_prompt_template())
                    else:
                        return f.read()
            except Exception as e:
                logger.warning(f"Error cargando prompt desde {prompt_file}: {e}")
        
        # Si hay template inline en config
        if inline_template := self.config.get("prompt_template"):
            if isinstance(inline_template, str):
                return inline_template
        
        # Usar template por defecto
        return self._default_prompt_template()
    
    def _default_prompt_template(self) -> str:
        """Template de prompt por defecto"""
        return """Eres un asistente experto en ajedrez. 

Posición actual (FEN): {fen}

Histórico de movimientos: {move_history}

Estrategia deseada: {strategy}

Analiza la posición y sugiere el mejor movimiento en formato UCI (ej: e2e4).
Responde SOLO con el movimiento en formato UCI seguido opcionalmente de tu razonamiento.

Formato de respuesta:
MOVIMIENTO: [movimiento en formato UCI]
"""
    
    def build_prompt(self, board_state: str, **kwargs) -> str:
        """
        Construye el prompt contextual para el LLM.
        
        Args:
            board_state: Posición en formato FEN
            **kwargs: Contexto adicional (move_history, strategy, etc.)
            
        Returns:
            Prompt formateado
        """
        # Contexto adicional con valores por defecto
        move_history = kwargs.get("move_history", "Inicio de la partida")
        strategy = kwargs.get("strategy", "balanced")
        explanation = kwargs.get("explanation", False)
        
        # Formatear template
        try:
            prompt = self.prompt_template.format(
                fen=board_state,
                move_history=move_history,
                strategy=strategy
            )
        except KeyError as e:
            logger.warning(f"Clave faltante en template: {e}")
            prompt = self.prompt_template
        
        # Añadir petición de explicación si se solicita
        if explanation:
            prompt += "\n\nPor favor, explica brevemente tu razonamiento después del movimiento."
        
        return prompt
    
    def parse_output(self, llm_response: str, board_state: str) -> str:
        """
        Parsea la salida del LLM para extraer el movimiento.
        
        Args:
            llm_response: Respuesta textual del LLM
            board_state: FEN para validar legalidad
            
        Returns:
            Movimiento en formato UCI
        """
        move = self.validator.validate_and_extract(llm_response, board_state)
        
        if not move:
            raise ValueError(
                f"No se pudo extraer movimiento válido de la respuesta del LLM. "
                f"Respuesta: {llm_response[:200]}"
            )
        
        return move
    
    async def _do_initialize(self):
        """Inicializa el protocolo de comunicación"""
        await self.protocol.initialize()
    
    async def get_move(self, board_state: str, depth: Optional[int] = None, **kwargs) -> str:
        """
        Obtiene el mejor movimiento usando el motor generativo.
        
        Args:
            board_state: Posición en formato FEN
            depth: No aplica directamente para LLMs (puede usarse en contexto)
            **kwargs: Contexto adicional (move_history, strategy, explanation)
            
        Returns:
            Mejor movimiento en formato UCI
        """
        # Asegurar inicialización
        await self.initialize()
        
        # 1. Construir prompt contextual
        prompt = self.build_prompt(board_state, **kwargs)
        
        # 2. Enviar posición al protocolo
        await self.protocol.send_position(board_state)
        
        # 3. Llamar al LLM vía protocolo (pasar prompt en kwargs)
        llm_response = await self.protocol.request_move(depth, prompt=prompt, **kwargs)
        
        # 4. Parsear la salida y extraer movimiento
        move = self.parse_output(llm_response, board_state)
        
        # 5. Validar (doble chequeo)
        if not await self.validate_response(llm_response, board_state):
            raise ValueError(f"Motor generativo {self.name} generó movimiento inválido")
        
        logger.info(f"Motor generativo {self.name} sugiere: {move}")
        
        # Guardar explicación si se solicitó
        if kwargs.get("explanation"):
            self._last_explanation = llm_response
        
        return move
    
    async def validate_response(self, llm_response: str, board_state: str) -> bool:
        """
        Valida que la respuesta del LLM contenga un movimiento válido.
        
        Args:
            llm_response: Respuesta textual del LLM
            board_state: Posición FEN para validar legalidad
            
        Returns:
            True si es válida
        """
        move = self.validator.validate_and_extract(llm_response, board_state)
        return move is not None
    
    def get_last_explanation(self) -> Optional[str]:
        """Retorna la última explicación generada (si existe)"""
        return getattr(self, '_last_explanation', None)
    
    async def _do_cleanup(self):
        """Limpia recursos del protocolo"""
        await self.protocol.cleanup()
