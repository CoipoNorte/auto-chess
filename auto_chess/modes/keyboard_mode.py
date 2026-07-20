"""
Modo Teclado: El usuario escribe las jugadas y el tool las ejecuta.
"""
import logging
import chess
from typing import Optional, Callable

from auto_chess.engine.chess_engine import ChessEngine
from auto_chess.capture.board_reader import BoardReader
from auto_chess.controller.chess_com import ChessComController

logger = logging.getLogger(__name__)


class KeyboardMode:
    """
    Modo teclado: el usuario escribe jugadas en formato simplificado
    y la herramienta las ejecuta en chess.com.
    
    Formatos de entrada:
    - UCI directo: "e2e4", "g1f3"
    - Con espacio: "e2 e4"
    - Con promoción: "e7e8q"
    - Algebraica simplificada: "e4" (el tool intenta resolver la jugada)
    """

    def __init__(self, engine: ChessEngine, reader: BoardReader,
                 controller: ChessComController):
        self.engine = engine
        self.reader = reader
        self.controller = controller
        self._active = False
        self._on_move_callback: Optional[Callable] = None
        self._on_status_callback: Optional[Callable] = None
        self._on_error_callback: Optional[Callable] = None

    def activate(self):
        """Activa el modo teclado."""
        self._active = True
        self._emit_status("Modo Teclado activado. Escriba sus jugadas.")

    def deactivate(self):
        """Desactiva el modo teclado."""
        self._active = False
        self._emit_status("Modo Teclado desactivado.")

    def process_input(self, move_input: str) -> bool:
        """
        Procesa la entrada del usuario y ejecuta el movimiento.
        
        move_input: texto escrito por el usuario
        Retorna True si se ejecutó correctamente.
        """
        if not self._active:
            return False

        move_input = move_input.strip()
        if not move_input:
            return False

        logger.info(f"[Teclado] Entrada: {move_input}")

        # Intentar interpretar la entrada
        move_uci = self._interpret_input(move_input)

        if move_uci is None:
            self._emit_error(f"Entrada no reconocida: '{move_input}'. "
                           f"Use formato: e2e4, Nf3, e4")
            return False

        # Verificar que el movimiento es legal
        board = self.reader.read_board_with_fallback()
        try:
            move = chess.Move.from_uci(move_uci)
        except ValueError:
            self._emit_error(f"Movimiento UCI inválido: {move_uci}")
            return False

        if move not in board.legal_moves:
            self._emit_error(f"Movimiento ilegal en la posición actual: {move_uci}")
            return False

        # Ejecutar el movimiento
        self._emit_status(f"Ejecutando: {move_uci} ({move_input})")
        success = self.controller.execute_move(move_uci)

        if success:
            self.reader.update_from_move(move_uci)
            self._emit_status(f"✓ Movimiento ejecutado: {move_uci}")

            if self._on_move_callback:
                self._on_move_callback(move_uci)

            # Manejar promoción si es necesario
            if move.promotion:
                self.controller.handle_promotion(
                    self.controller.board_config.get_square_center(
                        chess.square_file(move.to_square),
                        chess.square_rank(move.to_square)
                    ),
                    piece=chess.piece_symbol(move.promotion)
                )
        else:
            self._emit_error("No se pudo ejecutar el movimiento en chess.com")

        return success

    def _interpret_input(self, move_input: str) -> Optional[str]:
        """
        Intenta interpretar la entrada del usuario como un movimiento.
        Retorna el movimiento en formato UCI o None.
        """
        # Intento 1: Formato UCI directo
        uci = ChessComController.parse_move_input(move_input)
        if uci:
            return uci

        # Intento 2: Notación algebraica estándar
        board = self.reader.read_board_with_fallback()
        try:
            move = board.parse_san(move_input)
            return move.uci()
        except (ValueError, chess.InvalidMoveError):
            pass

        # Intento 3: Notación simplificada (solo casilla destino)
        # Por ejemplo: "e4" -> intentar encontrar qué pieza puede ir a e4
        move_input_lower = move_input.lower().strip()
        if len(move_input_lower) == 2:
            move = self._try_resolve_short_notation(move_input_lower, board)
            if move:
                return move.uci()

        # Intento 4: Formato con letra de pieza + casilla (ej: "Ne3", "Bb5")
        if len(move_input_lower) >= 2 and move_input_lower[0].upper() in 'PNBRQK':
            san_input = move_input  # Mantener case original para la pieza
            try:
                move = board.parse_san(san_input)
                return move.uci()
            except (ValueError, chess.InvalidMoveError):
                pass

        return None

    def _try_resolve_short_notation(self, square: str,
                                     board: chess.Board) -> Optional[chess.Move]:
        """
        Intenta resolver una notación corta (solo casilla destino)
        encontrando el movimiento legal que va a esa casilla.
        Si hay ambigüedad, retorna None.
        """
        if len(square) != 2:
            return None

        col = ord(square[0]) - ord('a')
        row = int(square[1]) - 1

        if not (0 <= col <= 7 and 0 <= row <= 7):
            return None

        target_sq = chess.square(col, row)
        candidates = []

        for move in board.legal_moves:
            if move.to_square == target_sq:
                candidates.append(move)

        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) > 1:
            # Ambigüedad - preferir el movimiento de peón
            pawn_moves = [m for m in candidates
                         if board.piece_at(m.from_square) and
                         board.piece_at(m.from_square).piece_type == chess.PAWN]
            if len(pawn_moves) == 1:
                return pawn_moves[0]
            # Si sigue habiendo ambigüedad, retornar None
            self._emit_error(
                f"Ambigüedad: {len(candidates)} piezas pueden ir a {square}. "
                f"Especifique la pieza (ej: Ned4, Rfe1)"
            )

        return None

    def get_legal_moves_hint(self) -> str:
        """Retorna una lista de movimientos legales para ayuda."""
        board = self.reader.read_board_with_fallback()
        moves = []
        for move in board.legal_moves:
            san = board.san(move)
            uci = move.uci()
            moves.append(f"{san} ({uci})")
        return ", ".join(moves[:20])  # Limitar a 20 para no saturar

    def _emit_status(self, message: str):
        logger.info(f"[Teclado] {message}")
        if self._on_status_callback:
            self._on_status_callback(message)

    def _emit_error(self, message: str):
        logger.warning(f"[Teclado] Error: {message}")
        if self._on_error_callback:
            self._on_error_callback(message)

    def set_on_move(self, callback: Callable):
        self._on_move_callback = callback

    def set_on_status(self, callback: Callable):
        self._on_status_callback = callback

    def set_on_error(self, callback: Callable):
        self._on_error_callback = callback

    @property
    def is_active(self) -> bool:
        return self._active
