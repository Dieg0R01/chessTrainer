"""
Factory y Registry para creación dinámica de motores.
Implementa los patrones Factory Method y Registry.
Actualizado para soportar arquitectura con protocolos.
"""

import logging
from typing import Any, Dict, Type, Optional, List
import yaml
import sys
import os

# Agregar el directorio raíz al path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import resolve_config_dict
from .base import MotorBase, MotorType, MotorOrigin
from .traditional import TraditionalEngine
from .neuronal import NeuronalEngine
from .generative import GenerativeEngine

logger = logging.getLogger(__name__)


class EngineRegistry:
    """
    Registro de tipos de motores disponibles.
    Permite añadir nuevos motores sin modificar código base.
    """
    
    _registry: Dict[str, Type[MotorBase]] = {}
    
    @classmethod
    def register(cls, engine_type: str, engine_class: Type[MotorBase]) -> None:
        """
        Registra una nueva clase de motor.
        
        Args:
            engine_type: Identificador del tipo de motor
            engine_class: Clase del motor a registrar
        """
        if engine_type in cls._registry:
            logger.warning(f"Sobrescribiendo motor registrado: {engine_type}")
        
        cls._registry[engine_type] = engine_class
        logger.info(f"Motor registrado: {engine_type} -> {engine_class.__name__}")
    
    @classmethod
    def get(cls, engine_type: str) -> Optional[Type[MotorBase]]:
        """
        Obtiene la clase de motor registrada.
        
        Args:
            engine_type: Identificador del tipo de motor
            
        Returns:
            Clase del motor o None si no existe
        """
        return cls._registry.get(engine_type)
    
    @classmethod
    def list_registered(cls) -> list:
        """Lista todos los tipos de motores registrados"""
        return list(cls._registry.keys())
    
    @classmethod
    def is_registered(cls, engine_type: str) -> bool:
        """Verifica si un tipo de motor está registrado"""
        return engine_type in cls._registry


# Registrar motores por defecto (simplificado con nueva arquitectura)
EngineRegistry.register("traditional", TraditionalEngine)
EngineRegistry.register("traditional_uci", TraditionalEngine)  # Retrocompatibilidad
EngineRegistry.register("traditional_rest", TraditionalEngine)  # Retrocompatibilidad
EngineRegistry.register("neuronal", NeuronalEngine)
EngineRegistry.register("generative", GenerativeEngine)


class EngineFactory:
    """
    Factory para crear instancias de motores dinámicamente.
    Implementa el patrón Abstract Factory.
    Actualizado para trabajar con arquitectura de protocolos.
    """
    
    @staticmethod
    def create_engine(name: str, config: Dict[str, Any]) -> MotorBase:
        """
        Crea una instancia de motor según la configuración.
        
        Args:
            name: Nombre del motor
            config: Configuración del motor que debe incluir 'engine_type'
            
        Returns:
            Instancia del motor creado
            
        Raises:
            ValueError: Si el tipo de motor no es válido
        """
        # Determinar el tipo de motor
        engine_type = config.get("engine_type")
        
        if not engine_type:
            # Inferir tipo de motor según configuración
            engine_type = EngineFactory._infer_engine_type(config)
        
        # Normalizar tipo de motor (eliminar sufijos de protocolo)
        normalized_type = EngineFactory._normalize_engine_type(engine_type)
        
        # Obtener clase del registro
        engine_class = EngineRegistry.get(normalized_type)
        
        if not engine_class:
            raise ValueError(
                f"Tipo de motor no registrado: {engine_type} (normalizado: {normalized_type}). "
                f"Tipos disponibles: {EngineRegistry.list_registered()}"
            )
        
        # Crear instancia
        try:
            # Añadir nombre del motor a la configuración para que los protocolos puedan usarlo
            config_with_name = config.copy()
            config_with_name["name"] = name
            engine = engine_class(name=name, config=config_with_name)
            logger.info(f"Motor creado por factory: {name} ({normalized_type})")
            return engine
        except Exception as e:
            logger.error(f"Error creando motor {name}: {e}")
            raise
    
    @staticmethod
    def _normalize_engine_type(engine_type: str) -> str:
        """
        Normaliza el tipo de motor eliminando sufijos de protocolo.
        Esto mantiene retrocompatibilidad con configs antiguas.
        
        Args:
            engine_type: Tipo de motor original
            
        Returns:
            Tipo normalizado
        """
        # Mapeo de tipos antiguos a nuevos
        type_mapping = {
            "traditional_uci": "traditional",
            "traditional_rest": "traditional",
            "neuronal_uci": "neuronal",
            "neuronal_rest": "neuronal",
        }
        
        return type_mapping.get(engine_type, engine_type)
    
    @staticmethod
    def _infer_engine_type(config: Dict[str, Any]) -> str:
        """
        Infiere el tipo de motor basándose en la configuración.
        Actualizado para nueva arquitectura con protocolos.
        
        Args:
            config: Configuración del motor
            
        Returns:
            Tipo de motor inferido
        """
        # Motor generativo (detectar por provider o características de LLM)
        if "provider" in config or "api_key" in config:
            return "generative"
        
        if "model" in config and any(key in config for key in ["temperature", "max_tokens"]):
            return "generative"
        
        # Motor neuronal (detectar por características específicas)
        if "protocol" in config:
            # Si tiene weights o backend, es neuronal
            if "weights" in config or "backend" in config:
                return "neuronal"
            # Si tiene protocol y search_mode específico de neuronales
            if config.get("search_mode") in ["nodes", "time"]:
                return "neuronal"
        
        # Si tiene características de neuronal pero no protocol
        if "weights" in config or "backend" in config:
            return "neuronal"
        
        # Motor tradicional UCI
        if "command" in config:
            return "traditional"
        
        # Motor tradicional REST
        if "url" in config and "extract" in config:
            return "traditional"
        
        # Si tiene URL pero no extract, podría ser REST o generativo
        if "url" in config:
            # Si tiene características de API de LLM
            if config.get("method", "").upper() == "POST" and "model" in config:
                return "generative"
            return "traditional"
        
        # Por defecto, asumir tradicional
        logger.warning(
            f"No se pudo inferir tipo de motor claramente, usando 'traditional' por defecto. "
            f"Config: {list(config.keys())}"
        )
        return "traditional"
    
    @staticmethod
    def create_from_yaml(yaml_path: str) -> Dict[str, MotorBase]:
        """
        Crea motores desde un archivo YAML de configuración.
        Resuelve variables de entorno en formato ${VARIABLE}.
        
        Args:
            yaml_path: Ruta al archivo YAML
            
        Returns:
            Diccionario de motores creados {name: engine}
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Resolver variables de entorno en la configuración
            config = resolve_config_dict(config)
            
            engines_config = config.get("engines", {})
            engines = {}
            
            for name, engine_config in engines_config.items():
                try:
                    # Resolver variables de entorno en la configuración del motor
                    engine_config = resolve_config_dict(engine_config)
                    engine = EngineFactory.create_engine(name, engine_config)
                    engines[name] = engine
                except Exception as e:
                    logger.error(f"Error creando motor {name} desde YAML: {e}")
                    # Continuar con los demás motores en lugar de fallar completamente
            
            logger.info(f"Creados {len(engines)}/{len(engines_config)} motores desde {yaml_path}")
            return engines
            
        except FileNotFoundError:
            logger.error(f"Archivo de configuración no encontrado: {yaml_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parseando YAML {yaml_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error leyendo configuración YAML {yaml_path}: {e}")
            raise
    
    @staticmethod
    def create_from_multiple_yaml(yaml_paths: List[str]) -> Dict[str, MotorBase]:
        """
        Crea motores desde múltiples archivos YAML de configuración.
        Combina todos los motores de los archivos en un solo diccionario.
        
        Args:
            yaml_paths: Lista de rutas a archivos YAML
            
        Returns:
            Diccionario combinado de motores creados {name: engine}
            
        Raises:
            ValueError: Si hay nombres de motores duplicados entre archivos
        """
        all_engines = {}
        
        for yaml_path in yaml_paths:
            try:
                engines = EngineFactory.create_from_yaml(yaml_path)
                
                # Verificar duplicados
                duplicates = set(all_engines.keys()) & set(engines.keys())
                if duplicates:
                    raise ValueError(
                        f"Motores duplicados encontrados en {yaml_path}: {', '.join(duplicates)}"
                    )
                
                # Combinar motores
                all_engines.update(engines)
                logger.info(f"Archivo {yaml_path} cargado: {len(engines)} motores")
                
            except FileNotFoundError:
                logger.warning(f"Archivo de configuración no encontrado: {yaml_path}, omitiendo...")
                # Continuar con los demás archivos
                continue
            except Exception as e:
                logger.error(f"Error cargando {yaml_path}: {e}")
                # Continuar con los demás archivos
                continue
        
        logger.info(f"Total de motores cargados desde {len(yaml_paths)} archivos: {len(all_engines)}")
        return all_engines
    
    @staticmethod
    def create_from_dict(engines_config: Dict[str, Dict[str, Any]]) -> Dict[str, MotorBase]:
        """
        Crea motores desde un diccionario de configuración.
        
        Args:
            engines_config: Diccionario {name: config}
            
        Returns:
            Diccionario de motores creados {name: engine}
        """
        engines = {}
        
        for name, config in engines_config.items():
            try:
                engine = EngineFactory.create_engine(name, config)
                engines[name] = engine
            except Exception as e:
                logger.error(f"Error creando motor {name}: {e}")
                # Continuar con los demás motores
        
        logger.info(f"Creados {len(engines)}/{len(engines_config)} motores desde diccionario")
        return engines


class EngineClassifier:
    """
    Clasificador para organizar motores según sus dimensiones.
    Útil para análisis y documentación.
    """
    
    @staticmethod
    def classify_engine(engine: MotorBase) -> Dict[str, str]:
        """
        Clasifica un motor según sus características.
        
        Args:
            engine: Motor a clasificar
            
        Returns:
            Diccionario con clasificación
        """
        return {
            "name": engine.name,
            "type": engine.motor_type.value,
            "origin": engine.motor_origin.value,
            "validation_mode": engine.validation_mode.value,
            "class": engine.__class__.__name__,
            "protocol": engine.protocol.__class__.__name__ if hasattr(engine, 'protocol') else "N/A"
        }
    
    @staticmethod
    def generate_classification_matrix(engines: Dict[str, MotorBase]) -> list:
        """
        Genera matriz de clasificación para todos los motores.
        
        Args:
            engines: Diccionario de motores
            
        Returns:
            Lista de clasificaciones
        """
        matrix = []
        
        for name, engine in engines.items():
            classification = EngineClassifier.classify_engine(engine)
            matrix.append(classification)
        
        return matrix
    
    @staticmethod
    def filter_by_type(engines: Dict[str, MotorBase], motor_type: MotorType) -> Dict[str, MotorBase]:
        """
        Filtra motores por tipo.
        
        Args:
            engines: Diccionario de motores
            motor_type: Tipo de motor a filtrar
            
        Returns:
            Diccionario de motores filtrados
        """
        return {
            name: engine
            for name, engine in engines.items()
            if engine.motor_type == motor_type
        }
    
    @staticmethod
    def filter_by_origin(engines: Dict[str, MotorBase], motor_origin: MotorOrigin) -> Dict[str, MotorBase]:
        """
        Filtra motores por origen.
        
        Args:
            engines: Diccionario de motores
            motor_origin: Origen a filtrar
            
        Returns:
            Diccionario de motores filtrados
        """
        return {
            name: engine
            for name, engine in engines.items()
            if engine.motor_origin == motor_origin
        }
    
    @staticmethod
    def filter_by_protocol(engines: Dict[str, MotorBase], protocol_name: str) -> Dict[str, MotorBase]:
        """
        Filtra motores por tipo de protocolo.
        
        Args:
            engines: Diccionario de motores
            protocol_name: Nombre del protocolo (ej: "UCIProtocol", "RESTProtocol")
            
        Returns:
            Diccionario de motores filtrados
        """
        return {
            name: engine
            for name, engine in engines.items()
            if hasattr(engine, 'protocol') and engine.protocol.__class__.__name__ == protocol_name
        }
