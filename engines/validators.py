"""
Módulo de validadores para respuestas de motores de ajedrez.
Implementa el patrón Decorator para añadir validación.
"""

import re
import logging
from typing import Any, Optional
import chess

logger = logging.getLogger(__name__)


class SchemaValidator:
    """
    Validador basado en schema/regex para motores tradicionales y neuronales.
    Valida que la jugada esté en formato correcto.
    """
    
    # Regex para notación UCI (ej: e2e4, e7e5q para promoción)
    UCI_PATTERN = re.compile(r'^[a-h][1-8][a-h][1-8][qrbn]?$')
    
    @staticmethod
    def validate_uci_move(move: str) -> bool:
        """
        Valida que una jugada esté en formato UCI válido.
        
        Args:
            move: Jugada en notación UCI
            
        Returns:
            True si es válida
        """
        if not isinstance(move, str):
            logger.warning(f"Jugada no es string: {type(move)}")
            return False
        
        move = move.strip().lower()
        is_valid = bool(SchemaValidator.UCI_PATTERN.match(move))
        
        if not is_valid:
            logger.warning(f"Jugada UCI inválida: {move}")
        
        return is_valid
    
    @staticmethod
    def validate_move_legal(move: str, fen: str) -> bool:
        """
        Valida que una jugada sea legal en un tablero dado.
        
        Args:
            move: Jugada en notación UCI
            fen: Posición del tablero en formato FEN
            
        Returns:
            True si la jugada es legal
        """
        try:
            board = chess.Board(fen)
            chess_move = chess.Move.from_uci(move)
            is_legal = chess_move in board.legal_moves
            
            if not is_legal:
                logger.warning(f"Jugada ilegal {move} en posición {fen}")
            
            return is_legal
        except Exception as e:
            logger.error(f"Error validando legalidad de jugada: {e}")
            return False
    
    @staticmethod
    def validate_full(move: str, fen: Optional[str] = None) -> bool:
        """
        Validación completa: formato UCI + legalidad (si se proporciona FEN).
        
        Args:
            move: Jugada en notación UCI
            fen: Posición del tablero en formato FEN (opcional)
            
        Returns:
            True si es válida
        """
        # Primero validar formato
        if not SchemaValidator.validate_uci_move(move):
            return False
        
        # Si hay FEN, validar legalidad
        if fen:
            return SchemaValidator.validate_move_legal(move, fen)
        
        return True


class PromptValidator:
    """
    Validador basado en parsing de respuestas de LLMs.
    Extrae y valida jugadas de texto generado.
    """
    
    # Patrones para extraer jugadas de texto LLM
    MOVE_PATTERNS = [
        # Buscar formato UCI directo
        re.compile(r'\b([a-h][1-8][a-h][1-8][qrbn]?)\b', re.IGNORECASE),
        # Buscar en JSON: "move": "e2e4"
        re.compile(r'"move"\s*:\s*"([a-h][1-8][a-h][1-8][qrbn]?)"', re.IGNORECASE),
        # Buscar en texto: "la mejor jugada es e2e4"
        re.compile(r'(?:mejor jugada|best move|move|jugada).*?([a-h][1-8][a-h][1-8][qrbn]?)', re.IGNORECASE),
    ]
    
    @staticmethod
    def extract_move_from_text(text: str) -> Optional[str]:
        """
        Extrae una jugada de un texto generado por LLM.
        
        Args:
            text: Texto generado por el LLM
            
        Returns:
            Jugada en formato UCI o None si no se encuentra
        """
        if not isinstance(text, str):
            logger.warning(f"Texto no es string: {type(text)}")
            return None
        
        # Intentar con cada patrón
        for pattern in PromptValidator.MOVE_PATTERNS:
            matches = pattern.findall(text)
            if matches:
                # Tomar la primera coincidencia
                move = matches[0].lower().strip()
                if SchemaValidator.validate_uci_move(move):
                    logger.info(f"Jugada extraída del texto: {move}")
                    return move
        
        logger.warning(f"No se pudo extraer jugada válida del texto: {text[:100]}...")
        return None
    
    @staticmethod
    def validate_and_extract(text: str, fen: Optional[str] = None) -> Optional[str]:
        """
        Extrae y valida una jugada de texto LLM.
        
        Args:
            text: Texto generado por el LLM
            fen: Posición del tablero en formato FEN (opcional)
            
        Returns:
            Jugada válida en formato UCI o None
        """
        move = PromptValidator.extract_move_from_text(text)
        
        if move and fen:
            # Validar legalidad
            if SchemaValidator.validate_move_legal(move, fen):
                return move
            else:
                logger.warning(f"Jugada extraída {move} es ilegal en posición {fen}")
                return None
        
        return move


class ValidatorFactory:
    """Factory para crear validadores según el modo de validación"""
    
    @staticmethod
    def get_validator(validation_mode: str):
        """
        Retorna el validador apropiado según el modo.
        
        Args:
            validation_mode: 'schema' o 'prompt'
            
        Returns:
            Clase validadora
        """
        if validation_mode == "schema":
            return SchemaValidator
        elif validation_mode == "prompt":
            return PromptValidator
        else:
            raise ValueError(f"Modo de validación desconocido: {validation_mode}")
