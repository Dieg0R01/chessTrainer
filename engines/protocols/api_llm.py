"""
Protocolo para APIs de LLMs externos (OpenAI, Anthropic, Cohere, etc.)
"""

import logging
import httpx
from typing import Optional, Dict, Any
from .base import ProtocolBase

# Importar módulo de configuración para variables de entorno
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_api_key, get_api_url

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
        
        # Propiedades críticas: deben estar en configuración (ya resueltas por EngineFactory)
        self.provider = config.get("provider")
        self.model = config.get("model")
        self.api_url = config.get("api_url")
        engine_name = config.get("name")  # Nombre del motor si está disponible
        
        # Validar propiedades críticas
        if not self.provider:
            raise ValueError("APILLMProtocol requiere 'provider' en configuración")
        if not self.model:
            raise ValueError("APILLMProtocol requiere 'model' en configuración")
        
        # api_url ya debería estar resuelto desde variables de entorno si estaba como ${VARIABLE}
        # Si aún no está, intentar obtenerlo desde variables de entorno directamente
        if not self.api_url:
            self.api_url = get_api_url(self.provider, engine_name)
        
        if not self.api_url:
            raise ValueError(
                f"APILLMProtocol requiere 'api_url' en configuración (puede usar ${{OPENAI_API_URL}}) "
                f"o variable de entorno ({self.provider.upper()}_API_URL)"
            )
        
        # api_key ya debería estar resuelto desde variables de entorno si estaba como ${VARIABLE}
        # Si aún no está, intentar obtenerlo desde variables de entorno directamente
        config_api_key = config.get("api_key")
        
        if config_api_key and config_api_key != "YOUR_OPENAI_API_KEY" and not config_api_key.startswith("YOUR_"):
            # Usar API key de configuración si está presente y no es placeholder
            self.api_key = config_api_key
        else:
            # Buscar en variables de entorno
            self.api_key = get_api_key(self.provider, engine_name)
        
        if not self.api_key:
            logger.warning(
                f"APILLMProtocol para {self.provider} sin api_key. "
                f"Busca en variables de entorno: {self.provider.upper()}_API_KEY o API_KEY. "
                "Puede fallar en producción."
            )
        
        # Propiedades no críticas: pueden tener valores por defecto
        self.timeout = config.get("timeout", 60.0)
        
        self.current_fen: Optional[str] = None
    
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
        
        # Reintentos para errores 503 (Service Unavailable) y 429 (Too Many Requests)
        max_retries = 3
        retry_count = 0
        last_exception = None
        
        while retry_count < max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.debug(f"Llamando a API {self.provider} (intento {retry_count + 1}/{max_retries})")
                    logger.debug(f"URL: {self.api_url}, Modelo: {self.model}")
                    
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
                error_detail = f"Error HTTP {e.response.status_code} en API {self.provider}"
                try:
                    error_body = e.response.json()
                    error_detail += f": {error_body}"
                except:
                    error_detail += f": {e.response.text[:500]}"
                
                logger.warning(f"{error_detail} (intento {retry_count + 1}/{max_retries})")
                logger.debug(f"URL utilizada: {self.api_url}")
                logger.debug(f"Modelo: {self.model}")
                
                last_exception = e
                
                # Reintentar solo para errores 503 y 429
                if e.response.status_code in [503, 429] and retry_count < max_retries - 1:
                    retry_count += 1
                    wait_time = 2 ** retry_count  # Backoff exponencial: 2s, 4s, 8s
                    logger.info(f"Esperando {wait_time}s antes de reintentar...")
                    import asyncio
                    await asyncio.sleep(wait_time)
                    continue
                
                # Para errores 503, proporcionar información útil
                if e.response.status_code == 503:
                    # Según la documentación de free_chatgpt_api, algunos modelos pueden no estar disponibles
                    # Los modelos que suelen funcionar: gpt-4o-mini, gpt-3.5-turbo (versión estándar)
                    # Los modelos con fecha específica (ej: gpt-3.5-turbo-1106) pueden no estar disponibles
                    error_msg = (
                        f"Servicio no disponible (503) después de {retry_count + 1} intentos. "
                        f"Modelo solicitado: '{self.model}'. "
                        f"Posibles causas: 1) El modelo '{self.model}' no está disponible en la API gratuita "
                        f"(algunos modelos con fecha específica como gpt-3.5-turbo-1106 pueden no estar disponibles), "
                        f"2) El servicio está sobrecargado, "
                        f"3) Se excedió el límite de RPM (96 requests/minuto). "
                        f"Recomendación: Usa 'gpt-4o-mini' o 'gpt-3.5-turbo' (sin fecha específica) que son más estables."
                    )
                    logger.error(error_msg)
                    raise httpx.HTTPStatusError(error_msg, request=e.request, response=e.response)
                
                # Para otros errores HTTP, no reintentar
                raise
                
            except Exception as e:
                last_exception = e
                logger.error(f"Error llamando a API {self.provider} (intento {retry_count + 1}): {e}")
                
                # Reintentar solo para errores de conexión/timeout
                if retry_count < max_retries - 1:
                    retry_count += 1
                    wait_time = 2 ** retry_count
                    logger.info(f"Esperando {wait_time}s antes de reintentar...")
                    import asyncio
                    await asyncio.sleep(wait_time)
                    continue
                
                raise
        
        # Si llegamos aquí, todos los reintentos fallaron
        if last_exception:
            raise last_exception
        raise Exception(f"No se pudo obtener respuesta de {self.provider} después de {max_retries} intentos")
    
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

