"""
Overlay transparente para mostrar sugerencias de jugadas sobre chess.com.
"""
import logging
import chess
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import (QPainter, QPen, QBrush, QColor, QFont,
                          QPolygon, QLinearGradient, QPainterPath)
from typing import List, Tuple, Optional

from auto_chess.engine.chess_engine import MoveAnalysis
from auto_chess.config import BoardConfig, DisplayConfig

logger = logging.getLogger(__name__)


class ChessOverlay(QWidget):
    """
    Ventana transparente que se superpone sobre el tablero de chess.com.
    Muestra flechas de sugerencia y botones clickeables para cada jugada sugerida.
    """

    move_selected = pyqtSignal(int)  # Emite el índice de la sugerencia seleccionada

    def __init__(self, board_config: BoardConfig, display_config: DisplayConfig):
        super().__init__()
        self.board_config = board_config
        self.display_config = display_config

        self._suggestions: List[MoveAnalysis] = []
        self._click_zones: List[Tuple[QRect, int]] = []  # (rectángulo, índice)
        self._hover_zone: int = -1
        self._showing = False

        self._setup_window()

    def _setup_window(self):
        """Configura la ventana como transparente y always-on-top."""
        # Flags de ventana
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # No mostrar en taskbar
        self.setWindowOpacity(1.0)

    def update_position(self):
        """Actualiza la posición del overlay para que cubra el tablero."""
        if not self.board_config.is_calibrated:
            return

        x, y = self.board_config.top_left
        size = self.board_config.square_size * 8

        self.setGeometry(x, y, size, size)

    def show_suggestions(self, suggestions: List[MoveAnalysis]):
        """Muestra las sugerencias en el overlay."""
        self._suggestions = suggestions
        self._click_zones = []

        if not self.board_config.is_calibrated:
            return

        # Calcular zonas de click para cada sugerencia
        for i, suggestion in enumerate(suggestions):
            move = suggestion.move
            to_col = chess.square_file(move.to_square)
            to_row = chess.square_rank(move.to_square)

            # Zona de click en la casilla destino
            rect = self._get_square_rect(to_col, to_row)
            # Expandir un poco la zona para facilitar el click
            expanded = rect.adjusted(-5, -5, 5, 5)
            self._click_zones.append((expanded, i))

        if not self._showing:
            self.update_position()
            self.show()
            self._showing = True
        else:
            self.update()

    def clear_suggestions(self):
        """Limpia las sugerencias del overlay."""
        self._suggestions = []
        self._click_zones = []
        self.update()

    def hide_overlay(self):
        """Oculta el overlay."""
        self._showing = False
        self.hide()

    def show_overlay(self):
        """Muestra el overlay."""
        if self.board_config.is_calibrated:
            self.update_position()
            self.show()
            self._showing = True

    def _get_square_rect(self, col: int, row: int) -> QRect:
        """Obtiene el rectángulo de una casilla en coordenadas del overlay."""
        if not self.board_config.white_at_bottom:
            col = 7 - col
            row = 7 - row

        x = col * self.board_config.square_size
        y = (7 - row) * self.board_config.square_size
        size = self.board_config.square_size
        return QRect(x, y, size, size)

    def _get_square_center(self, col: int, row: int) -> QPoint:
        """Obtiene el centro de una casilla en coordenadas del overlay."""
        rect = self._get_square_rect(col, row)
        return rect.center()

    def paintEvent(self, event):
        """Dibuja las sugerencias (flechas y highlights)."""
        if not self._suggestions:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        sq_size = self.board_config.square_size

        for i, suggestion in enumerate(self._suggestions):
            move = suggestion.move
            from_col = chess.square_file(move.from_square)
            from_row = chess.square_rank(move.from_square)
            to_col = chess.square_file(move.to_square)
            to_row = chess.square_rank(move.to_square)

            # Seleccionar color según posición
            if i == 0:
                color = QColor(*self.display_config.arrow_color_best)
            elif i == 1:
                color = QColor(*self.display_config.arrow_color_second)
            else:
                color = QColor(*self.display_config.arrow_color_third)

            # Resaltar casilla destino
            dest_rect = self._get_square_rect(to_col, to_row)
            highlight_color = QColor(color)
            highlight_color.setAlpha(60)
            painter.fillRect(dest_rect, QBrush(highlight_color))

            # Resaltar casilla origen (más sutil)
            orig_rect = self._get_square_rect(from_col, from_row)
            orig_color = QColor(color)
            orig_color.setAlpha(30)
            painter.fillRect(orig_rect, QBrush(orig_color))

            # Dibujar flecha
            start = self._get_square_center(from_col, from_row)
            end = self._get_square_center(to_col, to_row)

            self._draw_arrow(painter, start, end, color,
                           self.display_config.arrow_width, i == (self._hover_zone))

            # Dibujar etiqueta de evaluación
            if self.display_config.show_evaluation:
                label_pos = dest_rect.topLeft() + QPoint(2, 2)
                self._draw_eval_label(painter, label_pos, suggestion, color)

            # Dibujar número de sugerencia
            num_pos = dest_rect.bottomRight() + QPoint(-18, -18)
            painter.setPen(QPen(Qt.white, 2))
            painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
            painter.drawEllipse(num_pos, 10, 10)
            painter.setPen(QPen(Qt.white))
            font = QFont()
            font.setBold(True)
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(
                QRect(num_pos.x()-10, num_pos.y()-10, 20, 20),
                Qt.AlignCenter, str(i + 1)
            )

        painter.end()

    def _draw_arrow(self, painter: QPainter, start: QPoint, end: QPoint,
                    color: QColor, width: int, highlighted: bool = False):
        """Dibuja una flecha de ajedrez (estilo chess.comlichess)."""
        # Si está highlighted, hacerla más brillante
        draw_color = QColor(color)
        if highlighted:
            draw_color.setAlpha(min(255, draw_color.alpha() + 50))

        pen = QPen(draw_color, width)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QBrush(draw_color))

        # Calcular dirección
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = (dx**2 + dy**2) ** 0.5

        if length < 1:
            return

        # Normalizar
        ndx = dx / length
        ndy = dy / length

        # Acortar la flecha para que no sobresalga de la casilla
        margin = self.board_config.square_size * 0.3
        arrow_start = QPoint(
            int(start.x() + ndx * margin),
            int(start.y() + ndy * margin)
        )
        arrow_end = QPoint(
            int(end.x() - ndx * margin),
            int(end.y() - ndy * margin)
        )

        # Dibujar línea principal
        line_width = width * 1.5
        painter.setPen(QPen(draw_color, line_width, Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(arrow_start, arrow_end)

        # Dibujar cabeza de flecha
        head_size = width * 3
        head_angle = 0.5  # ~30 grados

        # Puntos de la cabeza
        perp_x = -ndy
        perp_y = ndx

        tip = arrow_end
        left = QPoint(
            int(arrow_end.x() - ndx * head_size + perp_x * head_size * 0.5),
            int(arrow_end.y() - ndy * head_size + perp_y * head_size * 0.5)
        )
        right = QPoint(
            int(arrow_end.x() - ndx * head_size - perp_x * head_size * 0.5),
            int(arrow_end.y() - ndy * head_size - perp_y * head_size * 0.5)
        )

        arrow_head = QPolygon([tip, left, right])
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(draw_color))
        painter.drawPolygon(arrow_head)

    def _draw_eval_label(self, painter: QPainter, pos: QPoint,
                         suggestion: MoveAnalysis, color: QColor):
        """Dibuja la etiqueta de evaluación junto a la flecha."""
        text = suggestion.score_display
        font = QFont()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)

        # Fondo semitransparente
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text) + 8
        text_height = metrics.height() + 4

        bg_rect = QRect(pos.x(), pos.y(), text_width, text_height)
        bg_color = QColor(0, 0, 0, 180)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(bg_rect, 3, 3)

        # Texto
        painter.setPen(QPen(Qt.white))
        painter.drawText(bg_rect, Qt.AlignCenter, text)

    def mousePressEvent(self, event):
        """Maneja clicks en las sugerencias."""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            for rect, index in self._click_zones:
                if rect.contains(pos):
                    self.move_selected.emit(index)
                    return

        # Click fuera de sugerencias - no hacer nada (overlay transparente)
        # O cerrar si se hace click derecho
        if event.button() == Qt.RightButton:
            self.hide_overlay()

    def mouseMoveEvent(self, event):
        """Maneja hover sobre las sugerencias."""
        pos = event.pos()
        new_hover = -1
        for rect, index in self._click_zones:
            if rect.contains(pos):
                new_hover = index
                break

        if new_hover != self._hover_zone:
            self._hover_zone = new_hover
            self.update()  # Redibujar para mostrar highlight

    def enterEvent(self, event):
        """El mouse entró al overlay - habilitar interacción."""
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

    def leaveEvent(self, event):
        """El mouse salió del overlay."""
        self._hover_zone = -1
        self.update()


class MoveButton(QPushButton):
    """
    Botón individual para una sugerencia de movimiento.
    Se coloca sobre la casilla destino y es clickeable.
    """

    def __init__(self, suggestion: MoveAnalysis, index: int,
                 board_config: BoardConfig, parent=None):
        super().__init__(parent)
        self.suggestion = suggestion
        self.index = index
        self.board_config = board_config

        move = suggestion.move
        to_col = chess.square_file(move.to_square)
        to_row = chess.square_rank(move.to_square)

        # Posicionar sobre la casilla destino
        pos = board_config.get_square_center(to_col, to_row)
        btn_size = board_config.square_size // 2

        self.setFixedSize(btn_size, btn_size)
        self.move(pos[0] - btn_size // 2, pos[1] - btn_size // 2)

        # Estilo
        self.setText(f"{index+1}")
        self.setToolTip(
            f"Sugerencia {index+1}: {move.uci()} ({suggestion.score_display})\n"
            f"Click para ejecutar"
        )

        if index == 0:
            self.setStyleSheet(
                "QPushButton { background-color: rgba(0, 200, 0, 180); "
                "color: white; font-weight: bold; border-radius: 50%; "
                "border: 2px solid white; }"
                "QPushButton:hover { background-color: rgba(0, 255, 0, 220); }"
            )
        elif index == 1:
            self.setStyleSheet(
                "QPushButton { background-color: rgba(0, 100, 255, 150); "
                "color: white; font-weight: bold; border-radius: 50%; "
                "border: 2px solid white; }"
                "QPushButton:hover { background-color: rgba(0, 120, 255, 200); }"
            )
        else:
            self.setStyleSheet(
                "QPushButton { background-color: rgba(255, 165, 0, 120); "
                "color: white; font-weight: bold; border-radius: 50%; "
                "border: 2px solid white; }"
                "QPushButton:hover { background-color: rgba(255, 180, 0, 180); }"
            )

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
