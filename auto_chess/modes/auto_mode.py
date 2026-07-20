"""
Modo Auto: El motor juega automáticamente contra el bot.
Incluye comportamiento humanizado para reducir detección.
"""
import time
import random
import logging
import chess
from typing import Optional, Callable

from auto_chess.engine.chess_engine import ChessEngine
from auto_chess.capture.board_reader import BoardReader
from auto_chess.controller.chess_com import ChessComController
from auto_chess.config import BoardConfig

logger = logging.getLogger(__name__)


class AutoMode:
    """
    Modo automático: el engine juega todas las jugadas.
    
    Flujo:
    1. Lee el tablero de la pantalla
    2. Calcula la mejor jugada
    3. Espera un tiempo "humano" de pensamiento
    4. Ejecuta el movimiento con comportamiento natural
    5. Espera la respuesta del bot (con comportamiento idle)
    6. Repite hasta fin de partida
    """

    def __init__(self, engine: ChessEngine, reader: BoardReader,
                 controller: ChessComController):
        self.engine = engine
        self.reader = reader
        self.controller = controller
        self._running = False
        self._paused = False
        self._on_move_callback: Optional[Callable] = None
        self._on_status_callback: Optional[Callable] = None
        self._on_game_end_callback: Optional[Callable] = None
        self._our_color: Optional[chess.Color] = None
        self._last_position_fen: str = ""

    def start(self, color: chess.Color = chess.WHITE):
        """
        Inicia el modo automático.
        color: el color que jugamos (WHITE o BLACK)
        """
        self._our_color = color
        self._running = True
        self._paused = False
        self.controller.reset_stealth()
        logger.info(f"Modo Auto iniciado. Jugamos con {'blancas' if color == chess.WHITE else 'negras'}")

        self._emit_status("Modo Auto activado. Esperando nuestro turno...")

        while self._running:
            if self._paused:
                time.sleep(0.5)
                continue

            try:
                self._game_loop()
            except Exception as e:
                logger.error(f"Error en el loop del modo auto: {e}")
                self._emit_status(f"Error: {e}")
                time.sleep(2)

        self._emit_status("Modo Auto detenido.")

    def stop(self):
        """Detiene el modo automático."""
        self._running = False
        logger.info("Modo Auto detenido")

    def pause(self):
        """Pausa el modo automático."""
        self._paused = True
        self._emit_status("Modo Auto pausado")

    def resume(self):
        """Reanuda el modo automático."""
        self._paused = False
        self._emit_status("Modo Auto reanudado")

    def _game_loop(self):
        """Loop principal del juego automático."""
        # Leer el tablero actual
        board = self.reader.read_board()

        if board is None:
            self._emit_status("No se puede leer el tablero. Intentando de nuevo...")
            time.sleep(1)
            return

        # Verificar si la posición cambió (el oponente jugó)
        current_fen = board.fen()
        if current_fen != self._last_position_fen:
            self._last_position_fen = current_fen
        else:
            # Posición no cambió - verificar si esperamos al oponente
            if board.turn != self._our_color:
                self._emit_status("Esperando respuesta del bot...")
                # Comportamiento idle mientras esperamos
                if self.controller.stealth_enabled:
                    self.controller.wait_for_opponent(timeout=2.0)
                else:
                    time.sleep(0.5)
                return

        # Verificar si la partida terminó
        if board.is_game_over():
            result = self._get_game_result(board)
            self._emit_status(f"Partida terminada: {result}")
            if self._on_game_end_callback:
                self._on_game_end_callback(result)
            self._running = False
            return

        # Verificar si es nuestro turno
        if board.turn != self._our_color:
            self._emit_status("Esperando turno del bot...")
            if self.controller.stealth_enabled:
                self.controller.wait_for_opponent(timeout=2.0)
            else:
                time.sleep(0.5)
            return

        # Calcular la mejor jugada
        self._emit_status("Analizando posición...")
        best_move = self.engine.get_best_move(board)

        if best_move is None:
            self._emit_status("No se encontró jugada válida")
            time.sleep(1)
            return

        move_uci = best_move.uci()

        # Determinar si es captura (para timing humano)
        is_capture = board.is_capture(best_move)

        # Log del análisis
        if board.is_check():
            self._emit_status(f"¡JAQUE! Jugando: {move_uci}")
        elif is_capture:
            self._emit_status(f"Captura disponible: {move_uci}")
        else:
            self._emit_status(f"Mejor jugada: {move_uci}")

        # Notificar callback
        if self._on_move_callback:
            self._on_move_callback(move_uci)

        # Ejecutar el movimiento (con humanización)
        success = self.controller.execute_move(
            move_uci, board=board, is_capture=is_capture
        )

        if success:
            self.reader.update_from_move(move_uci)
            self._last_position_fen = ""  # Forzar re-lectura

            # Verificar si hubo promoción
            if best_move.promotion:
                self.controller.handle_promotion(
                    self.controller.board_config.get_square_center(
                        chess.square_file(best_move.to_square),
                        chess.square_rank(best_move.to_square)
                    ),
                    piece=chess.piece_symbol(best_move.promotion)
                )

            # Mostrar estadísticas stealth periódicamente
            stats = self.controller.get_stealth_stats()
            if stats and 'num_moves' in stats and stats['num_moves'] % 5 == 0:
                self._emit_status(
                    f"[Stealth] Movimientos: {stats['num_moves']} | "
                    f"Promedio: {stats['avg_time']:.1f}s | "
                    f"Patrón: {stats['pattern']}"
                )
        else:
            self._emit_status("Error al ejecutar movimiento. Reintentando...")

        time.sleep(0.5)

    def _get_game_result(self, board: chess.Board) -> str:
        """Determina el resultado de la partida."""
        if board.is_checkmate():
            winner = "Negras" if board.turn == chess.WHITE else "Blancas"
            return f"Jaque mate - Ganan {winner}"
        elif board.is_stalemate():
            return "Tablas (ahogado)"
        elif board.is_insufficient_material():
            return "Tablas (material insuficiente)"
        elif board.is_seventyfive_moves():
            return "Tablas (75 movimientos)"
        elif board.is_repetition():
            return "Tablas (repetición)"
        return "Partida terminada"

    def _emit_status(self, message: str):
        """Emite un mensaje de estado."""
        logger.info(f"[Auto] {message}")
        if self._on_status_callback:
            self._on_status_callback(message)

    def set_on_move(self, callback: Callable):
        """Registra callback para cuando se ejecuta un movimiento."""
        self._on_move_callback = callback

    def set_on_status(self, callback: Callable):
        """Registra callback para cambios de estado."""
        self._on_status_callback = callback

    def set_on_game_end(self, callback: Callable):
        """Registra callback para fin de partida."""
        self._on_game_end_callback = callback

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused
