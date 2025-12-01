"""
Módulo de configuración centralizado.
Carga variables de entorno desde archivo .env una sola vez al importar.
"""

import os
from pathlib import Path
from typing import Optional

# Cargar dotenv solo una vez cuando se importa el módulo
_dotenv_loaded = False


def load_env():
    """
    Carga variables de entorno desde archivo .env.
    Solo se ejecuta una vez, incluso si se llama múltiples veces.
    """
    global _dotenv_loaded
    
    if _dotenv_loaded:
        return
    
    try:
        from dotenv import load_dotenv
        
        # Buscar archivo .env en el directorio raíz del proyecto
        project_root = Path(__file__).parent
        env_file = project_root / ".env"
        
        if env_file.exists():
            load_dotenv(env_file)
            _dotenv_loaded = True
        else:
            # Si no existe .env, intentar cargar desde variables de entorno del sistema
            # Esto permite usar variables de entorno sin archivo .env
            _dotenv_loaded = True
            
    except ImportError:
        # Si dotenv no está instalado, usar variables de entorno del sistema directamente
        _dotenv_loaded = True


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Obtiene una variable de entorno.
    Asegura que dotenv esté cargado antes de leer.
    
    Args:
        key: Nombre de la variable de entorno
        default: Valor por defecto si no existe
        
    Returns:
        Valor de la variable de entorno o default
    """
    load_env()
    return os.getenv(key, default)


def get_api_key(provider: str, engine_name: Optional[str] = None) -> Optional[str]:
    """
    Obtiene la API key para un proveedor específico.
    Busca en el siguiente orden:
    1. {PROVIDER}_API_KEY (ej: OPENAI_API_KEY)
    2. {ENGINE_NAME}_API_KEY (ej: GPT4_CHESS_API_KEY)
    3. API_KEY (genérico)
    
    Args:
        provider: Nombre del proveedor (openai, anthropic, etc.)
        engine_name: Nombre del motor (opcional, para keys específicas)
        
    Returns:
        API key o None si no se encuentra
    """
    load_env()
    
    # 1. Buscar key específica del proveedor (ej: OPENAI_API_KEY)
    provider_key = f"{provider.upper()}_API_KEY"
    api_key = get_env(provider_key)
    if api_key:
        return api_key
    
    # 2. Buscar key específica del motor (ej: GPT4_CHESS_API_KEY)
    if engine_name:
        engine_key = f"{engine_name.upper().replace('-', '_')}_API_KEY"
        api_key = get_env(engine_key)
        if api_key:
            return api_key
    
    # 3. Buscar key genérica
    api_key = get_env("API_KEY")
    if api_key:
        return api_key
    
    return None


def get_api_url(provider: str, engine_name: Optional[str] = None) -> Optional[str]:
    """
    Obtiene la URL de la API para un proveedor específico.
    Busca en el siguiente orden:
    1. {PROVIDER}_API_URL (ej: OPENAI_API_URL)
    2. {ENGINE_NAME}_API_URL (ej: GPT_4O_MINI_API_URL)
    3. API_URL (genérico)
    
    Args:
        provider: Nombre del proveedor (openai, anthropic, etc.)
        engine_name: Nombre del motor (opcional, para URLs específicas)
        
    Returns:
        API URL o None si no se encuentra
    """
    load_env()
    
    # 1. Buscar URL específica del proveedor (ej: OPENAI_API_URL)
    provider_url = f"{provider.upper()}_API_URL"
    api_url = get_env(provider_url)
    if api_url:
        return api_url
    
    # 2. Buscar URL específica del motor (ej: GPT_4O_MINI_API_URL)
    if engine_name:
        engine_url = f"{engine_name.upper().replace('-', '_')}_API_URL"
        api_url = get_env(engine_url)
        if api_url:
            return api_url
    
    # 3. Buscar URL genérica
    api_url = get_env("API_URL")
    if api_url:
        return api_url
    
    return None


def resolve_env_variables(value: str) -> str:
    """
    Resuelve variables de entorno en formato ${VARIABLE} o ${VARIABLE:default}.
    
    Args:
        value: Cadena que puede contener variables ${VARIABLE}
        
    Returns:
        Cadena con variables resueltas
    """
    import re
    
    load_env()
    
    # Patrón para ${VARIABLE} o ${VARIABLE:default}
    # Nota: En Python, $ necesita ser escapado como \$ en el patrón regex
    pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'
    
    def replace_var(match):
        var_name = match.group(1)
        default = match.group(2) if match.group(2) else None
        env_value = get_env(var_name, default)
        # Si no hay valor y no hay default, devolver cadena vacía para que el protocolo pueda manejarlo
        if env_value is None:
            return ""  # Devolver vacío en lugar de mantener ${VARIABLE} sin resolver
        return env_value
    
    result = re.sub(pattern, replace_var, value)
    return result


def resolve_config_dict(config: dict) -> dict:
    """
    Resuelve variables de entorno en un diccionario de configuración recursivamente.
    Busca valores tipo string que contengan ${VARIABLE} y los resuelve.
    
    Args:
        config: Diccionario de configuración
        
    Returns:
        Diccionario con variables resueltas
    """
    resolved = {}
    
    for key, value in config.items():
        if isinstance(value, str):
            # Resolver variables de entorno
            resolved[key] = resolve_env_variables(value)
        elif isinstance(value, dict):
            # Recursión para diccionarios anidados
            resolved[key] = resolve_config_dict(value)
        elif isinstance(value, list):
            # Procesar listas
            resolved[key] = [
                resolve_config_dict(item) if isinstance(item, dict) else
                resolve_env_variables(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            resolved[key] = value
    
    return resolved


# Cargar dotenv automáticamente al importar el módulo
load_env()

