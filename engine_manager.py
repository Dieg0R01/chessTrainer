"""
Gestor de motores de ajedrez.
Utiliza el sistema de Factory y Registry para gestionar múltiples motores.
"""

import logging
import asyncio
from typing import Dict, Optional, List
from engines import MotorBase, EngineFactory, EngineClassifier, MotorType, MotorOrigin

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EngineManager:
    """
    Gestor centralizado de motores de ajedrez.
    Proporciona interfaz unificada para trabajar con múltiples motores.
    """
    
    def __init__(self, config_path = None):
        """
        Inicializa el gestor de motores.
        
        Args:
            config_path: Ruta al archivo de configuración YAML (opcional).
                        Si es None, carga engines_local.yaml y engines_external.yaml por defecto.
                        Si es una cadena, carga ese archivo único (retrocompatibilidad).
                        Si es una lista, carga todos los archivos especificados.
        """
        if config_path is None:
            # Por defecto, cargar ambos archivos separados
            self.config_paths = ["config/engines_local.yaml", "config/engines_external.yaml"]
            self.config_path = None  # Mantener para retrocompatibilidad
        elif isinstance(config_path, str):
            # Retrocompatibilidad: un solo archivo
            self.config_path = config_path
            self.config_paths = [config_path]
        elif isinstance(config_path, list):
            # Múltiples archivos explícitos
            self.config_paths = config_path
            self.config_path = config_path[0] if config_path else None
        else:
            raise ValueError(f"config_path debe ser str, list o None, recibido: {type(config_path)}")
        
        self.engines: Dict[str, MotorBase] = {}
        self.load_config()
    
    def load_config(self, config_paths: Optional[List[str]] = None) -> None:
        """
        Carga la configuración de motores desde YAML.
        
        Args:
            config_paths: Lista de rutas a archivos de configuración (opcional).
                         Si es None, usa self.config_paths
        """
        paths_to_load = config_paths if config_paths is not None else self.config_paths
        
        try:
            if len(paths_to_load) == 1:
                # Un solo archivo: usar método original para retrocompatibilidad
                self.engines = EngineFactory.create_from_yaml(paths_to_load[0])
            else:
                # Múltiples archivos: usar método nuevo
                self.engines = EngineFactory.create_from_multiple_yaml(paths_to_load)
            
            logger.info(f"Configuración cargada: {len(self.engines)} motores disponibles")
        except Exception as e:
            logger.error(f"Error cargando configuración desde {paths_to_load}: {e}")
            raise
    
    async def check_all_availability(self) -> None:
        """
        Verifica la disponibilidad de todos los motores.
        Actualiza el estado interno 'available' de cada motor.
        """
        logger.info("Verificando disponibilidad de motores...")
        tasks = []
        for engine in self.engines.values():
            tasks.append(engine.check_availability())
        
        if tasks:
            await asyncio.gather(*tasks)
            
        # Log resumen
        available_count = sum(1 for e in self.engines.values() if e._available)
        logger.info(f"Verificación completada: {available_count}/{len(self.engines)} motores disponibles")

    def reload_config(self) -> None:
        """Recarga la configuración desde los archivos"""
        # Limpiar motores existentes
        for engine in self.engines.values():
            try:
                import asyncio
                # Usar loop actual si existe, o crear tarea background
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(engine.cleanup())
                except RuntimeError:
                    pass # No hay loop corriendo
            except Exception as e:
                logger.warning(f"Error limpiando motor al recargar: {e}")
        
        self.engines.clear()
        self.load_config()
        
        # Intentar lanzar verificación si hay loop
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.check_all_availability())
        except RuntimeError:
            pass # Se verificará bajo demanda o al arranque de la app
    
    def get_engine(self, name: str) -> MotorBase:
        """
        Obtiene un motor por nombre.
        
        Args:
            name: Nombre del motor
            
        Returns:
            Instancia del motor
            
        Raises:
            ValueError: Si el motor no existe
        """
        if name not in self.engines:
            available = ", ".join(self.engines.keys())
            raise ValueError(
                f"Motor '{name}' no encontrado. "
                f"Motores disponibles: {available}"
            )
        
        return self.engines[name]
    
    def list_engines(self) -> List[str]:
        """
        Lista los nombres de todos los motores disponibles.
        
        Returns:
            Lista de nombres de motores
        """
        return list(self.engines.keys())
    
    def get_engines_info(self) -> List[Dict]:
        """
        Obtiene información de todos los motores.
        
        Returns:
            Lista con información de cada motor
        """
        return [engine.get_info() for engine in self.engines.values()]
    
    def get_classification_matrix(self) -> List[Dict]:
        """
        Genera matriz de clasificación de motores.
        
        Returns:
            Matriz de clasificación
        """
        return EngineClassifier.generate_classification_matrix(self.engines)
    
    def filter_engines_by_type(self, motor_type: MotorType) -> Dict[str, MotorBase]:
        """
        Filtra motores por tipo.
        
        Args:
            motor_type: Tipo de motor (TRADITIONAL, NEURONAL, GENERATIVE)
            
        Returns:
            Diccionario de motores filtrados
        """
        return EngineClassifier.filter_by_type(self.engines, motor_type)
    
    def filter_engines_by_origin(self, motor_origin: MotorOrigin) -> Dict[str, MotorBase]:
        """
        Filtra motores por origen.
        
        Args:
            motor_origin: Origen (INTERNAL, EXTERNAL)
            
        Returns:
            Diccionario de motores filtrados
        """
        return EngineClassifier.filter_by_origin(self.engines, motor_origin)
    
    async def get_best_move(self, engine_name: str, fen: str, depth: Optional[int] = None, **kwargs) -> str:
        """
        Obtiene el mejor movimiento de un motor específico.
        
        Args:
            engine_name: Nombre del motor
            fen: Posición en formato FEN
            depth: Profundidad de análisis (opcional)
            **kwargs: Parámetros adicionales específicos del motor
            
        Returns:
            Mejor movimiento en formato UCI
        """
        engine = self.get_engine(engine_name)
        
        # Verificar disponibilidad antes de intentar
        if engine._available is False:
             raise ValueError(f"El motor {engine_name} no está disponible (verifique configuración o conexión)")
        
        try:
            move = await engine.get_move(fen, depth, **kwargs)
            logger.info(f"Movimiento obtenido de {engine_name}: {move}")
            return move
        except Exception as e:
            logger.error(f"Error obteniendo movimiento de {engine_name}: {e}")
            raise
    
    async def compare_engines(self, fen: str, depth: Optional[int] = None) -> Dict[str, str]:
        """
        Compara las sugerencias de todos los motores disponibles.
        
        Args:
            fen: Posición en formato FEN
            depth: Profundidad de análisis
            
        Returns:
            Diccionario {engine_name: move}
        """
        results = {}
        
        # Ejecutar check rápido si no se ha hecho
        # await self.check_all_availability() # Opcional, puede ser lento
        
        for name, engine in self.engines.items():
            # Saltar motores no disponibles
            if engine._available is False:
                results[name] = "NO DISPONIBLE"
                continue
                
            try:
                # Para motores generativos, solicitar explicación automáticamente
                # Verificar si el motor soporta explicaciones
                kwargs = {}
                if hasattr(engine, 'get_last_explanation'):
                    kwargs['explanation'] = True
                
                move = await engine.get_move(fen, depth, **kwargs)
                results[name] = move
            except Exception as e:
                logger.warning(f"Motor {name} falló: {e}")
                results[name] = f"ERROR: {str(e)}"
        
        return results
    
    async def cleanup_all(self) -> None:
        """Limpia recursos de todos los motores"""
        for name, engine in self.engines.items():
            try:
                await engine.cleanup()
                logger.info(f"Motor {name} limpiado")
            except Exception as e:
                logger.warning(f"Error limpiando motor {name}: {e}")
    
    def __len__(self) -> int:
        """Retorna el número de motores cargados"""
        return len(self.engines)
    
    def __contains__(self, engine_name: str) -> bool:
        """Verifica si un motor existe"""
        return engine_name in self.engines
    
    def __str__(self) -> str:
        return f"EngineManager({len(self.engines)} motores: {', '.join(self.engines.keys())})"
    
    def __repr__(self) -> str:
        return self.__str__()
