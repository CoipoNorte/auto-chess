"""
Lector de tablero de alto nivel.
Combina captura de pantalla con detección de piezas para leer el estado del tablero.
"""
import numpy as np
import chess
from typing import Optional, Tuple

from auto_chess.capture.screen import ScreenCapture
from auto_chess.recognition.piece_detector import PieceDetector
from auto_chess.config import BoardConfig


class BoardReader:
    """
    Lee el estado del tablero de ajedrez desde la pantalla.
    """

    def __init__(self, board_config: BoardConfig):
        self.config = board_config
        self.screen = ScreenCapture()
        self.detector = PieceDetector()
        self._last_known_board: Optional[chess.Board] = None
        self._move_history: list = []

    def calibrate(self, fen: str = chess.STARTING_FEN) -> bool:
        """
        Calibra el lector capturando el tablero actual y extrayendo plantillas.
        Debe hacerse cuando el tablero está en la posición inicial (o una posición conocida).
        """
        if not self.config.is_calibrated:
            return False

        size = self.config.square_size * 8
        board_img = self.screen.capture_board(self.config.top_left, size)

        return self.detector.calibrate_from_position(
            board_img, self.config.square_size, fen
        )

    def read_board(self) -> Optional[chess.Board]:
        """
        Lee el tablero actual de la pantalla.
        Retorna chess.Board con la posición detectada, o None si falla.
        """
        if not self.config.is_calibrated:
            return None

        size = self.config.square_size * 8
        try:
            board_img = self.screen.capture_board(self.config.top_left, size)
        except Exception:
            return None

        board = self.detector.detect_board(board_img, self.config.square_size)

        if board.is_valid():
            self._last_known_board = board.copy()
            return board

        return None

    def read_board_with_fallback(self) -> Optional[chess.Board]:
        """
        Lee el tablero. Si la lectura de imagen falla, retorna la última
        posición conocida actualizada con los movimientos registrados.
        """
        board = self.read_board()
        if board is not None:
            return board

        # Fallback: usar la última posición conocida
        if self._last_known_board is not None:
            return self._last_known_board.copy()

        # Sin información: retornar posición inicial
        return chess.Board()

    def get_board_as_fen(self) -> Optional[str]:
        """Lee el tablero y retorna la posición en formato FEN."""
        board = self.read_board()
        if board is not None:
            return board.fen()
        return None

    def capture_board_image(self) -> Optional[np.ndarray]:
        """Captura la imagen actual del tablero."""
        if not self.config.is_calibrated:
            return None

        size = self.config.square_size * 8
        try:
            return self.screen.capture_board(self.config.top_left, size)
        except Exception:
            return None

    def update_from_move(self, move_uci: str):
        """
        Actualiza el tablero conocido con un movimiento.
        move_uci: movimiento en formato UCI (e.g., "e2e4")
        """
        if self._last_known_board is None:
            self._last_known_board = chess.Board()

        try:
            move = chess.Move.from_uci(move_uci)
            if move in self._last_known_board.legal_moves:
                self._last_known_board.push(move)
                self._move_history.append(move_uci)
        except ValueError:
            pass

    def set_position(self, fen: str):
        """Establece manualmente la posición del tablero."""
        try:
            self._last_known_board = chess.Board(fen)
        except ValueError:
            pass

    def reset(self):
        """Reinicia el estado del lector."""
        self._last_known_board = None
        self._move_history = []

    @property
    def last_known_board(self) -> Optional[chess.Board]:
        if self._last_known_board:
            return self._last_known_board.copy()
        return None

    @property
    def move_history(self) -> list:
        return self._move_history.copy()

    def close(self):
        """Libera recursos."""
        self.screen.close()
