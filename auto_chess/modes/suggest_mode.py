"""
Modo Sugerencia: El motor sugiere jugadas y las muestra como overlays clickeables.
Incluye comportamiento humanizado al ejecutar las jugadas seleccionadas.
"""
import time
import random
import logging
import chess
from typing import Optional, Callable, List

from auto_chess.engine.chess_engine import ChessEngine, MoveAnalysis
from auto_chess.capture.board_reader import BoardReader
from auto_chess.controller.chess_com import ChessComController

logger = logging.getLogger(__name__)


class SuggestMode:
    """
    Modo sugerencia: calcula las mejores jugadas y las muestra
    como flechas/highlights clickeables en un overlay sobre chess.com.
    
    El usuario puede hacer click en la sugerencia que prefiera
    y la herramienta la ejecuta con comportamiento humanizado.
    """

    def __init__(self, engine: ChessEngine, reader: BoardReader,
                 controller: ChessComController):
        self.engine = engine
        self.reader = reader
        self.controller = controller
        self._active = False
        self._current_suggestions: List[MoveAnalysis] = []
        self._current_board: Optional[chess.Board] = None
        self._on_suggestions_callback: Optional[Callable] = None
        self._on_move_callback: Optional[Callable] = None
        self._on_status_callback: Optional[Callable] = None

    def activate(self):
        """Activa el modo sugerencia."""
        self._active = True
        self.controller.reset_stealth()
        self._emit_status("Modo Sugerencia activado. Las jugadas se mostrarán como flechas.")
        self.update_suggestions()

    def deactivate(self):
        """Desactiva el modo sugerencia."""
        self._active = False
        self._current_suggestions = []
        self._emit_status("Modo Sugerencia desactivado.")
        if self._on_suggestions_callback:
            self._on_suggestions_callback([])

    def update_suggestions(self) -> List[MoveAnalysis]:
        """
        Calcula y actualiza las sugerencias de jugadas.
        Retorna la lista de sugerencias.
        """
        if not self._active:
            return []

        board = self.reader.read_board_with_fallback()
        self._current_board = board

        if board.is_game_over():
            self._emit_status("La partida ha terminado.")
            self._current_suggestions = []
            return []

        self._emit_status("Calculando sugerencias...")

        suggestions = self.engine.get_top_moves(
            board, num_moves=self.engine.config.multi_pv
        )

        self._current_suggestions = suggestions

        if suggestions:
            best = suggestions[0]
            # Mostrar info adicional sobre las jugadas
            capture_info = ""
            if board.is_capture(best.move):
                capture_info = " ⚔️ captura"
            if board.gives_check(best.move):
                capture_info += " ‡"

            self._emit_status(
                f"Mejor jugada: {board.san(best.move)} ({best.score_display}){capture_info}"
            )
        else:
            self._emit_status("No se encontraron sugerencias.")

        # Notificar al overlay
        if self._on_suggestions_callback:
            self._on_suggestions_callback(suggestions)

        return suggestions

    def select_suggestion(self, index: int) -> bool:
        """
        Selecciona y ejecuta una sugerencia por índice.
        index: 0 = mejor, 1 = segunda, 2 = tercera, etc.
        """
        if not self._active:
            return False

        if index < 0 or index >= len(self._current_suggestions):
            self._emit_status(f"Índice de sugerencia inválido: {index}")
            return False

        suggestion = self._current_suggestions[index]
        move_uci = suggestion.move.uci()

        # Determinar si es captura
        is_capture = False
        if self._current_board:
            is_capture = self._current_board.is_capture(suggestion.move)

        san_notation = ""
        if self._current_board:
            try:
                san_notation = self._current_board.san(suggestion.move)
            except Exception:
                san_notation = move_uci

        self._emit_status(
            f"Ejecutando sugerencia #{index+1}: {san_notation} ({suggestion.score_display})"
        )

        # Ejecutar el movimiento (con humanización)
        success = self.controller.execute_move(
            move_uci,
            board=self._current_board,
            is_capture=is_capture
        )

        if success:
            self.reader.update_from_move(move_uci)
            self._emit_status(f"✓ Sugerencia ejecutada: {san_notation}")

            if self._on_move_callback:
                self._on_move_callback(move_uci)

            # Manejar promoción
            if suggestion.move.promotion and self._current_board:
                self.controller.handle_promotion(
                    self.controller.board_config.get_square_center(
                        chess.square_file(suggestion.move.to_square),
                        chess.square_rank(suggestion.move.to_square)
                    ),
                    piece=chess.piece_symbol(suggestion.move.promotion)
                )

            # Actualizar sugerencias para el siguiente turno
            time.sleep(1.0)  # Esperar a que se actualice el tablero
            self.update_suggestions()
        else:
            self._emit_status(f"Error al ejecutar sugerencia: {move_uci}")

        return success

    def select_by_move(self, move_uci: str) -> bool:
        """
        Selecciona y ejecuta una sugerencia por su movimiento UCI.
        """
        for i, suggestion in enumerate(self._current_suggestions):
            if suggestion.move.uci() == move_uci:
                return self.select_suggestion(i)
        return False

    @property
    def suggestions(self) -> List[MoveAnalysis]:
        """Retorna las sugerencias actuales."""
        return self._current_suggestions

    @property
    def is_active(self) -> bool:
        return self._active

    def _emit_status(self, message: str):
        logger.info(f"[Sugerencia] {message}")
        if self._on_status_callback:
            self._on_status_callback(message)

    def set_on_suggestions(self, callback: Callable):
        """Registra callback para cuando se actualizan las sugerencias."""
        self._on_suggestions_callback = callback

    def set_on_move(self, callback: Callable):
        """Registra callback para cuando se ejecuta un movimiento."""
        self._on_move_callback = callback

    def set_on_status(self, callback: Callable):
        """Registra callback para cambios de estado."""
        self._on_status_callback = callback
