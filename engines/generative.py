"""
Motores generativos basados en LLMs o frameworks de agentes.
Ejemplos: GPT-Chess-Assistant, modelos locales con LangChain/LangGraph
Refactorizado para usar protocolos de comunicación mediante composición.
"""

import logging
from typing import Any, Dict, Optional
import os
import yaml
import re
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader

from .base import MotorBase, MotorType, MotorOrigin, ValidationMode
from .protocols import LocalLLMProtocol, APILLMProtocol
from .validators import PromptValidator, SchemaValidator

logger = logging.getLogger(__name__)

# Cargar estrategias válidas desde configuración
_STRATEGIES_CACHE: Optional[Dict[str, Dict[str, str]]] = None


def _load_chess_strategies() -> Dict[str, Dict[str, str]]:
    """
    Carga las estrategias de ajedrez desde config/chess_strategies.yaml.
    
    Returns:
        Diccionario con todas las estrategias disponibles
    """
    global _STRATEGIES_CACHE
    
    if _STRATEGIES_CACHE is not None:
        return _STRATEGIES_CACHE
    
    try:
        strategies_file = Path(__file__).parent.parent / "config" / "chess_strategies.yaml"
        
        if strategies_file.exists():
            with open(strategies_file, 'r', encoding='utf-8') as f:
                strategies_data = yaml.safe_load(f)
            
            strategies_dict = strategies_data.get("strategies", {})
            
            _STRATEGIES_CACHE = strategies_dict
            
            logger.info(f"Cargadas {len(strategies_dict)} estrategias de ajedrez")
            return strategies_dict
        else:
            logger.warning("Archivo chess_strategies.yaml no encontrado, usando estrategias por defecto")
            _STRATEGIES_CACHE = {}
            return {}
            
    except Exception as e:
        logger.warning(f"Error cargando estrategias: {e}")
        _STRATEGIES_CACHE = {}
        return {}


def get_strategy_info(strategy: str) -> Optional[Dict[str, str]]:
    """
    Obtiene información sobre una estrategia.
    
    Args:
        strategy: Nombre de la estrategia (case-insensitive)
        
    Returns:
        Diccionario con información de la estrategia o None si no existe
    """
    strategies = _load_chess_strategies()
    
    # Normalizar a lowercase
    strategy_lower = strategy.lower() if strategy else None
    
    if not strategy_lower:
        return None
    
    # Buscar estrategia
    strategy_info = strategies.get(strategy_lower)
    
    return strategy_info


def get_valid_strategies() -> list[str]:
    """
    Retorna lista de estrategias válidas.
    
    Returns:
        Lista de nombres de estrategias
    """
    strategies = _load_chess_strategies()
    return list(strategies.keys())


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
        
        # Cargar template de prompt (ahora es un objeto Jinja2 Template)
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> Template:
        """
        Carga el template de prompt Jinja2 desde archivo o configuración.
        
        Orden de prioridad:
        1. prompt_template_file (archivo específico, para casos especiales)
        2. prompt_template (template inline, para casos especiales)
        3. prompt_template.jinja (archivo por defecto para todos los motores generativos)
        4. Template por defecto hardcodeado
        
        Returns:
            Template Jinja2
        """
        config_path = Path(__file__).parent.parent / "config"
        jinja_env = Environment(
            loader=FileSystemLoader(str(config_path)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 1. Forma legacy: prompt_template_file (archivo específico, para casos especiales)
        prompt_file = self.config.get("prompt_template_file")
        
        if prompt_file and os.path.exists(prompt_file):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                    return jinja_env.from_string(template_content)
            except Exception as e:
                logger.warning(f"Error cargando prompt desde {prompt_file}: {e}")
        
        # 2. Forma legacy: prompt_template (template inline, para casos especiales)
        prompt_template = self.config.get("prompt_template")
        
        if prompt_template and isinstance(prompt_template, str):
            # Si parece ser un archivo, intentar cargarlo
            if prompt_template.endswith('.jinja') or prompt_template.endswith('.yaml') or prompt_template.endswith('.yml'):
                try:
                    return jinja_env.get_template(prompt_template)
                except Exception as e:
                    logger.warning(f"Error cargando template {prompt_template}: {e}")
            # Si no, usar como template inline
            return jinja_env.from_string(prompt_template)
        
        # 3. Cargar prompt_template.md.jinja primero (template mejorado con análisis)
        md_template_file = "prompt_template.md.jinja"
        try:
            template = jinja_env.get_template(md_template_file)
            logger.debug(f"Template cargado desde {md_template_file}")
            return template
        except Exception as e:
            logger.warning(f"No se pudo cargar {md_template_file}: {e}")
        
        # 4. Cargar prompt_template.jinja como fallback (archivo estándar para todos los motores)
        default_template_file = "prompt_template.jinja"
        try:
            template = jinja_env.get_template(default_template_file)
            logger.debug(f"Template cargado desde {default_template_file}")
            return template
        except Exception as e:
            logger.warning(f"No se pudo cargar {default_template_file}: {e}")
        
        # 5. Usar template por defecto hardcodeado (fallback)
        logger.warning(f"Usando template por defecto hardcodeado")
        return jinja_env.from_string(self._default_prompt_template())
    
    def _detect_opening_phase(self, move_count: int) -> Optional[str]:
        """
        Detecta la fase de apertura basándose en el número de movimientos.
        Se activa después de 10 movimientos.
        
        Args:
            move_count: Número de movimientos en el historial
            
        Returns:
            Nombre de la fase de apertura o None si no aplica
        """
        if move_count < 10:
            return None
        elif move_count < 16:
            return "apertura media"
        elif move_count < 22:
            return "apertura avanzada"
        else:
            return "transición al medio juego"
    
    def _analyze_legal_moves(self, legal_moves_list: list, board: Any = None) -> Dict[str, Any]:
        """
        Analiza y agrupa movimientos legales por categoría.
        
        Args:
            legal_moves_list: Lista de movimientos legales en formato UCI
            board: Objeto chess.Board para detectar capturas (opcional)
            
        Returns:
            Diccionario con movimientos agrupados por categoría
        """
        captures = []
        development = []
        king_moves = []
        other = []
        
        # Casillas iniciales para detectar desarrollo
        initial_squares = ['e1', 'e8', 'd1', 'd8', 'c1', 'c8', 'f1', 'f8', 
                          'b1', 'b8', 'g1', 'g8', 'a1', 'a8', 'h1', 'h8',
                          'e2', 'e7', 'd2', 'd7']
        
        for move_str in legal_moves_list:
            from_square = move_str[:2]
            to_square = move_str[2:4]
            
            # Detectar capturas usando el tablero si está disponible
            is_capture = False
            if board:
                try:
                    import chess
                    move_obj = chess.Move.from_uci(move_str)
                    if board.is_capture(move_obj):
                        is_capture = True
                        if move_str not in captures:
                            captures.append(move_str)
                except:
                    pass
            
            if not is_capture:
                # Movimientos de desarrollo (desde casillas iniciales)
                if from_square in initial_squares:
                    if move_str not in development:
                        development.append(move_str)
                # Movimientos de rey/enroque
                elif from_square in ['e1', 'e8'] or to_square in ['g1', 'c1', 'g8', 'c8']:
                    if move_str not in king_moves:
                        king_moves.append(move_str)
                else:
                    if move_str not in other:
                        other.append(move_str)
        
        return {
            "captures": captures[:5],
            "development": development[:8],
            "king_moves": king_moves[:3],
            "other": other[:5],
            "total": len(legal_moves_list)
        }
    
    def _count_moves(self, move_history: str) -> int:
        """
        Cuenta el número de movimientos en el historial.
        
        Args:
            move_history: Histórico de movimientos (puede ser PGN, UCI, o texto)
            
        Returns:
            Número de movimientos contados
        """
        if not move_history or move_history.lower() in ["inicio de la partida", "start", ""]:
            return 0
        
        # Intentar contar movimientos en formato PGN
        # Primero contar números de movimientos únicos (1., 2., 3., etc.) que es más preciso
        move_numbers = re.findall(r'\d+\.', move_history)
        if move_numbers:
            # Cada número representa un turno completo (blancas + negras)
            # Pero necesitamos contar movimientos individuales, no turnos
            # Contar todos los movimientos individuales después de cada número
            # Ejemplo: "1. e4 e5 2. Nf3" tiene 2 turnos pero 3 movimientos
            moves_after_numbers = re.findall(r'\d+\.\s+([^\s]+(?:\s+[^\s]+)?)', move_history)
            if moves_after_numbers:
                # Contar movimientos individuales (cada elemento puede tener 1 o 2 movimientos)
                total_moves = 0
                for move_pair in moves_after_numbers:
                    # Cada par puede tener 1 o 2 movimientos separados por espacio
                    individual_moves = move_pair.split()
                    total_moves += len(individual_moves)
                return total_moves
            # Si no hay movimientos después de números, usar el conteo de números como aproximación
            return len(move_numbers)
        
        # Intentar contar movimientos UCI separados por espacios (ej: "e2e4 e7e5")
        uci_moves = re.findall(r'[a-h][1-8][a-h][1-8][qrnb]?', move_history, re.IGNORECASE)
        if uci_moves:
            return len(uci_moves)
        
        # Si no se puede parsear, contar palabras y dividir por 2 (asumiendo pares de movimientos)
        words = move_history.split()
        return len(words) // 2 if len(words) > 1 else 0
    
    def _default_prompt_template(self) -> str:
        """Template de prompt por defecto (fallback si no se puede cargar Jinja2)"""
        return """Eres un asistente experto en ajedrez con amplio conocimiento de estrategia, táctica y teoría del juego.

Posición actual del tablero (FEN): {{ fen }}
Histórico de movimientos: {{ move_history }}

Analiza la posición considerando todos los aspectos relevantes del ajedrez y sugiere el mejor movimiento.

IMPORTANTE: Responde ÚNICAMENTE con el movimiento en formato UCI. No incluyas texto adicional, explicaciones ni comentarios.

FORMATO DE RESPUESTA OBLIGATORIO:
[movimiento en formato UCI]

Ejemplos válidos: e2e4, e7e5, g1f3, e1g1

NO incluyas nada más que el movimiento UCI.
"""
    
    def build_prompt(self, board_state: str, **kwargs) -> str:
        """
        Construye el prompt contextual para el LLM usando Jinja2.
        
        Args:
            board_state: Posición en formato FEN
            **kwargs: Contexto adicional (move_history, strategy, etc.)
            
        Returns:
            Prompt formateado
        """
        # Contexto adicional con valores por defecto
        move_history = kwargs.get("move_history", "Inicio de la partida")
        explanation = kwargs.get("explanation", False)
        
        # Contar movimientos para decidir si mostrar selección de estrategia
        move_count = self._count_moves(move_history)
        show_strategy_selection = move_count >= 4 and move_count < 10
        
        # Detectar fase de apertura después de 10 movimientos
        opening_phase = None
        if move_count >= 10:
            opening_phase = self._detect_opening_phase(move_count)
        
        # Cargar todas las estrategias disponibles
        all_strategies = _load_chess_strategies()
        
        # Si hay una estrategia específica proporcionada, obtener su info
        strategy_raw = kwargs.get("strategy")
        selected_strategy_info = None
        if strategy_raw:
            selected_strategy_info = get_strategy_info(strategy_raw)
        elif opening_phase:
            # Asignar estrategia automáticamente según fase de apertura
            if opening_phase == "apertura media":
                selected_strategy_info = get_strategy_info("positional")
            elif opening_phase == "apertura avanzada":
                selected_strategy_info = get_strategy_info("balanced")
            elif opening_phase == "transición al medio juego":
                selected_strategy_info = get_strategy_info("tactical")
        
        # Obtener movimientos legales y analizarlos
        legal_moves_analyzed = {}
        legal_moves_sample = []
        try:
            import chess
            board = chess.Board(board_state)
            legal_moves_list = list(board.legal_moves)
            legal_moves_str_list = [str(move) for move in legal_moves_list]
            
            # Analizar movimientos legales agrupándolos por categoría
            legal_moves_analyzed = self._analyze_legal_moves(legal_moves_str_list, board)
            
            # Mantener lista simple para compatibilidad
            legal_moves_sample = legal_moves_str_list[:10]
            current_turn = "Negras" if board.turn == chess.BLACK else "Blancas"
        except Exception as e:
            logger.warning(f"Error obteniendo movimientos legales: {e}")
            legal_moves_sample = []
            legal_moves_analyzed = {"captures": [], "development": [], "king_moves": [], "other": [], "total": 0}
            current_turn = "Desconocido"
        
        # Preparar contexto para el template Jinja2
        context = {
            "fen": board_state,
            "move_history": move_history,
            "move_count": move_count,
            "show_strategy_selection": show_strategy_selection,
            "opening_phase": opening_phase,  # Fase de apertura detectada
            "strategies": all_strategies,  # Todas las estrategias disponibles
            "selected_strategy": selected_strategy_info,  # Estrategia seleccionada si existe
            "explanation": explanation,
            "legal_moves": legal_moves_analyzed if legal_moves_analyzed else legal_moves_sample,  # Movimientos analizados o lista simple
            "current_turn": current_turn  # Color que tiene el turno
        }
        
        # Log del historial recibido para debugging
        logger.info(f"📜 Motor {self.name} - Historial recibido: {move_history[:100] if len(move_history) > 100 else move_history}")
        logger.info(f"📊 Motor {self.name} - Total de movimientos contados: {move_count}")
        
        # Renderizar template Jinja2
        try:
            prompt = self.prompt_template.render(**context)
            logger.debug(f"📝 Motor {self.name} - Prompt generado (primeros 200 chars): {prompt[:200]}...")
        except Exception as e:
            logger.error(f"Error renderizando template Jinja2: {e}")
            # Fallback a template simple con movimientos legales
            legal_moves_str = ""
            current_turn_fallback = "Desconocido"
            legal_moves_sample = []
            try:
                import chess
                board = chess.Board(board_state)
                legal_moves_list = list(board.legal_moves)
                legal_moves_sample = [str(move) for move in legal_moves_list[:5]]
                if legal_moves_sample:
                    legal_moves_str = f"\nMOVIMIENTOS LEGALES DISPONIBLES: {', '.join(legal_moves_sample)}\n"
                current_turn_fallback = "Negras" if board.turn == chess.BLACK else "Blancas"
            except Exception:
                pass
            
            # Fallback a template simple
            prompt = f"""Eres un asistente experto en ajedrez.

Posición actual del tablero (FEN): {board_state}
Histórico de movimientos: {move_history}
Turno actual: {current_turn_fallback}
{legal_moves_str}
Analiza la posición cuidadosamente. Las piezas ya están en sus posiciones actuales según el FEN.

⚠️ CRÍTICO: NO repitas movimientos que ya se hayan hecho. Revisa el historial completo antes de decidir.
⚠️ CRÍTICO: NO muevas la misma pieza de ida y vuelta repetidamente (ej: no muevas el caballo de f6 a g8 y luego de vuelta a f6).
NO sugieras movimientos que ya se hayan hecho o que muevan piezas desde casillas donde ya no están.
Si el historial muestra movimientos recientes, asegúrate de NO repetirlos. Busca un movimiento diferente y estratégico.

IMPORTANTE: Responde ÚNICAMENTE con el movimiento en formato UCI. No incluyas texto adicional, explicaciones ni comentarios.

FORMATO DE RESPUESTA OBLIGATORIO:
[movimiento en formato UCI]

{('Ejemplos de movimientos legales válidos: ' + ', '.join(legal_moves_sample[:3]) if legal_moves_sample else 'Ejemplos válidos: e2e4, e7e5, g1f3, e1g1')}

NO incluyas nada más que el movimiento UCI."""
        
        return prompt
    
    def parse_output(self, llm_response: str, board_state: str) -> str:
        """
        Parsea la salida del LLM para extraer el movimiento.
        Valida que el movimiento sea legal en el tablero.
        
        Args:
            llm_response: Respuesta textual del LLM
            board_state: FEN para validar legalidad
            
        Returns:
            Movimiento en formato UCI
            
        Raises:
            ValueError: Si no se puede extraer un movimiento válido y legal
        """
        if not board_state:
            raise ValueError("board_state (FEN) es requerido para validar movimientos")
        
        logger.debug(f"Parseando respuesta del LLM. FEN: {board_state}, Respuesta: {llm_response[:200]}")
        
        move = self.validator.validate_and_extract(llm_response, board_state)
        
        if not move:
            # Intentar obtener movimientos legales para el mensaje de error
            try:
                import chess
                board = chess.Board(board_state)
                legal_moves_sample = [str(m) for m in list(board.legal_moves)[:5]]
                legal_moves_str = ", ".join(legal_moves_sample)
            except Exception:
                legal_moves_str = "N/A"
            
            raise ValueError(
                f"No se pudo extraer movimiento válido y legal de la respuesta del LLM. "
                f"Respuesta recibida: {llm_response[:200]}. "
                f"FEN: {board_state}. "
                f"Ejemplos de movimientos legales: {legal_moves_str}"
            )
        
        # Doble verificación: asegurar que el movimiento es legal usando SchemaValidator
        if not SchemaValidator.validate_move_legal(move, board_state):
            raise ValueError(
                f"Movimiento extraído '{move}' no es legal en posición FEN: {board_state}"
            )
        
        logger.info(f"Movimiento válido extraído: {move}")
        return move
    
    async def _check_availability(self) -> bool:
        """Verifica disponibilidad delegando en el protocolo"""
        return await self.protocol.check_availability()

    async def _do_initialize(self):
        """Inicializa el protocolo de comunicación"""
        await self.protocol.initialize()
    
    async def get_move(self, board_state: str, depth: Optional[int] = None, **kwargs) -> str:
        """
        Obtiene el mejor movimiento usando el motor generativo.
        Implementa sistema de reintentos si la respuesta no es válida.
        
        Args:
            board_state: Posición en formato FEN
            depth: No aplica directamente para LLMs (puede usarse en contexto)
            **kwargs: Contexto adicional (move_history, strategy, explanation)
            
        Returns:
            Mejor movimiento en formato UCI
            
        Raises:
            ValueError: Si después de los reintentos no se obtiene un movimiento válido
        """
        # Asegurar inicialización
        await self.initialize()
        
        # Construir prompt contextual una vez
        prompt = self.build_prompt(board_state, **kwargs)
        
        # Enviar posición al protocolo
        await self.protocol.send_position(board_state)
        
        # Número máximo de reintentos
        max_retries = kwargs.get("max_retries", 3)
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Llamar al LLM vía protocolo (pasar prompt en kwargs)
                llm_response = await self.protocol.request_move(depth, prompt=prompt, **kwargs)
                
                # Parsear la salida y extraer movimiento
                move = self.parse_output(llm_response, board_state)
                
                # Validar (doble chequeo)
                if await self.validate_response(llm_response, board_state):
                    logger.info(f"Motor generativo {self.name} sugiere: {move} (intento {retry_count + 1})")
                    
                    # Guardar explicación si se solicitó
                    if kwargs.get("explanation"):
                        self._last_explanation = llm_response
                    
                    return move
                else:
                    logger.warning(
                        f"Motor generativo {self.name} generó movimiento inválido en intento {retry_count + 1}. "
                        f"Respuesta: {llm_response[:200]}"
                    )
                    
            except ValueError as e:
                logger.warning(
                    f"Error extrayendo movimiento del motor {self.name} en intento {retry_count + 1}: {e}"
                )
            
            # Incrementar contador de reintentos
            retry_count += 1
            
            # Si aún hay reintentos disponibles, esperar un poco antes de reintentar
            # Aumentar el tiempo de espera progresivamente para dar más tiempo al LLM
            if retry_count < max_retries:
                import asyncio
                wait_time = 1.0 + (retry_count * 0.5)  # 1s, 1.5s, 2s...
                logger.debug(f"Esperando {wait_time}s antes del reintento {retry_count + 1}")
                await asyncio.sleep(wait_time)
        
        # Si llegamos aquí, todos los reintentos fallaron
        raise ValueError(
            f"Motor generativo {self.name} no pudo generar un movimiento válido después de {max_retries} intentos. "
            f"Última respuesta: {llm_response[:200] if 'llm_response' in locals() else 'N/A'}"
        )
    
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
