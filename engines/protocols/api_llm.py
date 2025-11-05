"""
Protocolo para APIs de LLMs externos (OpenAI, Anthropic, Cohere, etc.)
"""

import logging
import httpx
from typing import Optional, Dict, Any
from .base import ProtocolBase

logger = logging.getLogger(__name__)


class APILLMProtocol(ProtocolBase):
    """
    Protocolo para comunicación con APIs de LLMs externos.
    Soporta OpenAI, Anthropic, Cohere y otros proveedores.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el protocolo para API de LLM.
        
        Args:
            config: Debe incluir 'provider', 'api_key', 'model'
        """
        super().__init__(config)
        self.provider = config.get("provider", "openai")
        self.api_key = config.get("api_key")
        self.model = config.get("model", "gpt-4")
        self.api_url = config.get("api_url")
        self.timeout = config.get("timeout", 60.0)
        
        # Configurar URL por defecto según proveedor
        if not self.api_url:
            self.api_url = self._get_default_url()
        
        if not self.api_key:
            logger.warning(
                f"APILLMProtocol para {self.provider} sin api_key. "
                "Puede fallar en producción."
            )
        
        self.current_fen: Optional[str] = None
    
    def _get_default_url(self) -> str:
        """Retorna URL por defecto según el proveedor"""
        urls = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "cohere": "https://api.cohere.ai/v1/generate",
            "google": "https://generativelanguage.googleapis.com/v1/models",
        }
        return urls.get(self.provider, "")
    
    async def initialize(self) -> None:
        """API LLM no requiere inicialización especial"""
        self._initialized = True
        logger.debug(f"APILLMProtocol inicializado: {self.provider} / {self.model}")
    
    async def send_position(self, fen: str) -> None:
        """
        Guarda FEN para construcción de prompt.
        
        Args:
            fen: Posición en formato FEN
        """
        self.current_fen = fen
        logger.debug(f"Posición guardada para API LLM: {fen[:50]}...")
    
    async def request_move(self, depth: Optional[int] = None, **kwargs) -> str:
        """
        Envía prompt a la API de LLM y obtiene respuesta.
        
        Args:
            depth: No usado directamente
            **kwargs: Debe incluir 'prompt' con el prompt construido
            
        Returns:
            Respuesta textual del LLM
        """
        if not self._initialized:
            await self.initialize()
        
        prompt = kwargs.get("prompt")
        if not prompt:
            raise ValueError("APILLMProtocol requiere 'prompt' en kwargs")
        
        # Construir headers y payload según proveedor
        headers, payload = self._build_request(prompt)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Extraer texto según proveedor
                text = self._extract_text(data)
                
                logger.info(f"Respuesta de {self.provider}: {text[:100]}...")
                return text
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP en API {self.provider}: {e.response.status_code}")
            logger.error(f"Respuesta: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error llamando a API {self.provider}: {e}")
            raise
    
    def _build_request(self, prompt: str) -> tuple[Dict[str, str], Dict[str, Any]]:
        """
        Construye headers y payload según el proveedor.
        
        Args:
            prompt: Prompt construido
            
        Returns:
            Tupla (headers, payload)
        """
        headers = {"Content-Type": "application/json"}
        
        if self.provider == "openai":
            headers["Authorization"] = f"Bearer {self.api_key}"
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en ajedrez."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.config.get("temperature", 0.3),
                "max_tokens": self.config.get("max_tokens", 500)
            }
            
        elif self.provider == "anthropic":
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": self.config.get("max_tokens", 500),
                "temperature": self.config.get("temperature", 0.3)
            }
            
        elif self.provider == "cohere":
            headers["Authorization"] = f"Bearer {self.api_key}"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": self.config.get("max_tokens", 500),
                "temperature": self.config.get("temperature", 0.3)
            }
            
        elif self.provider == "google":
            headers["Authorization"] = f"Bearer {self.api_key}"
            payload = {
                "model": self.model,
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": self.config.get("temperature", 0.3),
                    "maxOutputTokens": self.config.get("max_tokens", 500)
                }
            }
            
        else:
            # Formato genérico para otros proveedores
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "max_tokens": self.config.get("max_tokens", 500),
                "temperature": self.config.get("temperature", 0.3)
            }
        
        return headers, payload
    
    def _extract_text(self, data: Dict[str, Any]) -> str:
        """
        Extrae el texto generado según el proveedor.
        
        Args:
            data: Respuesta JSON de la API
            
        Returns:
            Texto generado
        """
        if self.provider == "openai":
            return data["choices"][0]["message"]["content"]
        
        elif self.provider == "anthropic":
            return data["content"][0]["text"]
        
        elif self.provider == "cohere":
            return data["generations"][0]["text"]
        
        elif self.provider == "google":
            return data["candidates"][0]["content"]["parts"][0]["text"]
        
        else:
            # Intentar formatos genéricos
            if "text" in data:
                return data["text"]
            if "response" in data:
                return data["response"]
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "text" in choice:
                    return choice["text"]
                if "message" in choice:
                    return choice["message"].get("content", "")
        
        raise ValueError(f"No se pudo extraer texto de respuesta de {self.provider}: {data}")
    
    async def cleanup(self) -> None:
        """API LLM no requiere limpieza"""
        self._initialized = False
        logger.debug(f"APILLMProtocol cleanup completado ({self.provider})")

