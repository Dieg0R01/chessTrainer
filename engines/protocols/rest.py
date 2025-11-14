"""
Protocolo REST para motores remotos o APIs.
Soporta GET y POST, con configuración flexible de parámetros.
"""

import logging
import httpx
from typing import Optional, Dict, Any
from jsonpath import jsonpath
from .base import ProtocolBase

# Importar módulo de configuración para variables de entorno
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_api_key

logger = logging.getLogger(__name__)


class RESTProtocol(ProtocolBase):
    """
    Implementa comunicación HTTP REST para motores remotos.
    Soporta APIs como Lichess Cloud, Chess.com, etc.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el protocolo REST.
        
        Args:
            config: Debe incluir 'url', opcionalmente 'method', 'extract', etc.
        """
        super().__init__(config)
        self.url = config.get("url")
        self.method = config.get("method", "POST").upper()
        self.timeout = config.get("timeout", 30.0)
        self.extract_path = config.get("extract")  # JSONPath para extraer movimiento
        
        # Obtener API key: primero desde config, luego desde variables de entorno
        config_api_key = config.get("api_key")
        engine_name = config.get("name")  # Nombre del motor si está disponible
        
        if config_api_key and config_api_key != "YOUR_API_KEY" and not config_api_key.startswith("YOUR_"):
            # Usar API key de configuración si está presente y no es placeholder
            self.api_key = config_api_key
        else:
            # Buscar en variables de entorno (usar provider si está disponible, sino None)
            provider = config.get("provider") or config.get("engine_type", "").split("_")[0] if config.get("engine_type") else None
            self.api_key = get_api_key(provider or "rest", engine_name)
        
        if not self.url:
            raise ValueError("RESTProtocol requiere 'url' en configuración")
        
        self.current_fen: Optional[str] = None
    
    async def initialize(self) -> None:
        """REST no requiere inicialización especial"""
        self._initialized = True
        logger.debug(f"RESTProtocol inicializado: {self.url}")
    
    async def send_position(self, fen: str) -> None:
        """
        Guarda la posición FEN para la siguiente petición.
        REST envía la posición junto con la petición de movimiento.
        
        Args:
            fen: Posición en formato FEN
        """
        self.current_fen = fen
        logger.debug(f"Posición guardada: {fen[:50]}...")
    
    async def request_move(self, depth: Optional[int] = None, **kwargs) -> str:
        """
        Solicita movimiento vía API REST.
        
        Args:
            depth: Profundidad de análisis (si la API lo soporta)
            **kwargs: Parámetros adicionales
            
        Returns:
            Movimiento en formato UCI o respuesta cruda
        """
        if not self._initialized:
            await self.initialize()
        
        # Construir headers
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            # Soportar diferentes formatos de autenticación
            auth_header = self.config.get("auth_header", "Authorization")
            auth_format = self.config.get("auth_format", "Bearer {api_key}")
            headers[auth_header] = auth_format.format(api_key=self.api_key)
        
        # Añadir headers adicionales de configuración
        if extra_headers := self.config.get("headers"):
            headers.update(extra_headers)
        
        # Construir payload
        payload = self._build_payload(
            fen=self.current_fen,
            depth=depth,
            **kwargs
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Realizar petición según método
                if self.method == "GET":
                    response = await client.get(
                        self.url,
                        params=payload,
                        headers=headers
                    )
                elif self.method == "POST":
                    response = await client.post(
                        self.url,
                        json=payload,
                        headers=headers
                    )
                elif self.method == "PUT":
                    response = await client.put(
                        self.url,
                        json=payload,
                        headers=headers
                    )
                else:
                    raise ValueError(f"Método HTTP no soportado: {self.method}")
                
                # Manejo especial de errores 404 (común en APIs de ajedrez)
                if response.status_code == 404:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', 'Recurso no encontrado')
                    except:
                        error_msg = 'Recurso no encontrado'
                    raise ValueError(f"API Error 404: {error_msg}")
                
                # Lanzar excepción para otros errores HTTP
                response.raise_for_status()
                
                # Parsear respuesta
                data = response.json()
                
                # Extraer movimiento
                move = self._extract_move(data)
                logger.debug(f"Movimiento extraído de REST: {move}")
                
                return move
                
        except httpx.HTTPError as e:
            logger.error(f"Error HTTP en RESTProtocol: {e}")
            raise
        except Exception as e:
            logger.error(f"Error en RESTProtocol: {e}")
            raise
    
    def _build_payload(self, fen: Optional[str], depth: Optional[int], **kwargs) -> Dict[str, Any]:
        """
        Construye el payload de la petición según la configuración.
        
        Args:
            fen: Posición FEN
            depth: Profundidad de análisis
            **kwargs: Parámetros adicionales
            
        Returns:
            Diccionario con el payload formateado
        """
        params_template = self.config.get("params", {})
        
        # Valores para formatear templates
        format_values = {
            "fen": fen or "",
            "depth": depth or self.config.get("default_depth", 15)
        }
        format_values.update(kwargs)
        
        # Formatear parámetros
        payload = {}
        for key, value_template in params_template.items():
            if isinstance(value_template, str):
                try:
                    payload[key] = value_template.format(**format_values)
                except KeyError as e:
                    logger.warning(f"Clave no disponible para formatear: {e}")
                    payload[key] = value_template
            else:
                payload[key] = value_template
        
        # Añadir parámetros extra de configuración
        if extra := self.config.get("extra_params"):
            payload.update(extra)
        
        return payload
    
    def _extract_move(self, data: Dict[str, Any]) -> str:
        """
        Extrae el movimiento de la respuesta JSON.
        
        Args:
            data: Respuesta JSON de la API
            
        Returns:
            Movimiento extraído
        """
        # Si hay JSONPath configurado (para APIs tradicionales)
        if self.extract_path:
            result = jsonpath(data, self.extract_path)
            if result:
                move_data = result[0]
                # Si es una cadena con múltiples movimientos (ej: "e2e4 e7e5")
                if isinstance(move_data, str) and ' ' in move_data:
                    return move_data.split()[0]
                return str(move_data)
        
        # Intentar claves comunes de APIs de ajedrez
        for key in ["move", "bestmove", "best_move", "uci", "san"]:
            if key in data:
                move = str(data[key])
                # Extraer primer movimiento si es una secuencia
                if ' ' in move:
                    return move.split()[0]
                return move
        
        # Si no se encuentra, lanzar error descriptivo
        raise ValueError(
            f"No se pudo extraer movimiento de la respuesta. "
            f"Datos recibidos: {data}. "
            f"Configure 'extract' en YAML o asegúrese que la respuesta tenga 'move'/'bestmove'."
        )
    
    async def cleanup(self) -> None:
        """REST no requiere limpieza de recursos"""
        self._initialized = False
        logger.debug("RESTProtocol cleanup completado")

