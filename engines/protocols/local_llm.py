"""
Protocolo para LLMs locales (Ollama, LM Studio, LocalAI, etc.)
"""

import logging
import httpx
from typing import Optional, Dict, Any
from .base import ProtocolBase

logger = logging.getLogger(__name__)


class LocalLLMProtocol(ProtocolBase):
    """
    Protocolo para comunicación con LLMs locales.
    Compatible con Ollama, LM Studio, LocalAI y otros servidores locales.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el protocolo para LLM local.
        
        Args:
            config: Debe incluir 'endpoint' (obligatorio)
        """
        super().__init__(config)
        
        # Propiedad crítica: debe estar en configuración
        self.endpoint = config.get("endpoint")
        
        if not self.endpoint:
            raise ValueError(
                "LocalLLMProtocol requiere 'endpoint' en configuración. "
                "Ejemplo: 'http://localhost:8080'"
            )
        
        # Propiedades no críticas: pueden tener valores por defecto
        self.timeout = config.get("timeout", 60.0)  # Mayor timeout para LLMs
        self.model_path = config.get("model_path")
        
        self.current_fen: Optional[str] = None
    
    async def initialize(self) -> None:
        """
        Verifica que el endpoint del LLM local esté disponible.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Intentar ping al endpoint
                try:
                    response = await client.get(f"{self.endpoint}/health")
                    if response.status_code == 200:
                        logger.info(f"LocalLLMProtocol conectado: {self.endpoint}")
                except:
                    # Algunos servidores no tienen endpoint de health
                    logger.warning(
                        f"No se pudo verificar health de {self.endpoint}, "
                        "asumiendo que está disponible"
                    )
            
            self._initialized = True
            
        except Exception as e:
            logger.warning(f"No se pudo conectar a LLM local: {e}")
            # No falla la inicialización, se intentará en request_move
            self._initialized = True
    
    async def send_position(self, fen: str) -> None:
        """
        Guarda FEN para construcción de prompt.
        
        Args:
            fen: Posición en formato FEN
        """
        self.current_fen = fen
        logger.debug(f"Posición guardada para LLM local: {fen[:50]}...")
    
    async def request_move(self, depth: Optional[int] = None, **kwargs) -> str:
        """
        Envía prompt al LLM local y obtiene respuesta.
        
        Args:
            depth: No usado directamente, puede incluirse en el prompt
            **kwargs: Debe incluir 'prompt' con el prompt construido
            
        Returns:
            Respuesta textual del LLM (debe ser parseada por el motor)
        """
        if not self._initialized:
            await self.initialize()
        
        prompt = kwargs.get("prompt")
        if not prompt:
            raise ValueError("LocalLLMProtocol requiere 'prompt' en kwargs")
        
        # Construir payload según formato del servidor local
        payload = self._build_payload(prompt, **kwargs)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Intentar endpoint de generación
                endpoints_to_try = [
                    "/generate",  # LM Studio, LocalAI
                    "/api/generate",  # Ollama
                    "/v1/completions",  # OpenAI-compatible
                    "/completion",  # Alternativa
                ]
                
                last_error = None
                for endpoint_path in endpoints_to_try:
                    try:
                        url = f"{self.endpoint}{endpoint_path}"
                        logger.debug(f"Intentando endpoint: {url}")
                        
                        response = await client.post(url, json=payload)
                        
                        if response.status_code == 404:
                            continue  # Probar siguiente endpoint
                        
                        response.raise_for_status()
                        data = response.json()
                        
                        # Extraer texto de respuesta
                        text = self._extract_text(data)
                        
                        if text:
                            logger.info(f"Respuesta del LLM local: {text[:100]}...")
                            return text
                        
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code != 404:
                            last_error = e
                            break
                    except Exception as e:
                        last_error = e
                        continue
                
                # Si llegamos aquí, ningún endpoint funcionó
                raise RuntimeError(
                    f"No se pudo conectar a LLM local en {self.endpoint}. "
                    f"Endpoints probados: {endpoints_to_try}. "
                    f"Último error: {last_error}"
                )
                
        except Exception as e:
            logger.error(f"Error llamando a LLM local: {e}")
            raise
    
    def _build_payload(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Construye el payload según el formato del servidor local.
        
        Args:
            prompt: Prompt construido
            **kwargs: Parámetros adicionales
            
        Returns:
            Payload formateado
        """
        payload = {
            "prompt": prompt,
            "max_tokens": self.config.get("max_tokens", 500),
            "temperature": self.config.get("temperature", 0.3),
            "stop": self.config.get("stop_sequences", ["\n\n", "Human:", "User:"])
        }
        
        # Si hay modelo específico configurado
        if model := self.config.get("model"):
            payload["model"] = model
        
        # Parámetros adicionales del config
        if extra := self.config.get("extra_params"):
            payload.update(extra)
        
        return payload
    
    def _extract_text(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Extrae el texto generado de la respuesta.
        Soporta diferentes formatos de servidores locales.
        
        Args:
            data: Respuesta JSON del servidor
            
        Returns:
            Texto generado o None si no se encuentra
        """
        # Ollama format
        if "response" in data:
            return data["response"]
        
        # LM Studio / LocalAI format
        if "text" in data:
            return data["text"]
        
        # OpenAI-compatible format
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            if "text" in choice:
                return choice["text"]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
        
        # Formato genérico
        if "output" in data:
            return data["output"]
        
        if "generated_text" in data:
            return data["generated_text"]
        
        logger.warning(f"No se pudo extraer texto de respuesta local: {data}")
        return None
    
    async def cleanup(self) -> None:
        """LLM local no requiere limpieza especial"""
        self._initialized = False
        logger.debug("LocalLLMProtocol cleanup completado")

