"""
Detector de piezas por análisis de imagen.
Usa técnicas de visión por computador para identificar piezas en el tablero.
"""
import cv2
import numpy as np
from typing import Optional, Dict, Tuple, List
import chess


class PieceDetector:
    """
    Detecta piezas de ajedrez en una captura del tablero.
    
    Estrategia:
    1. Calibración: Extrae plantillas de piezas desde una posición conocida
    2. Detección: Usa template matching + análisis de contorno para identificar piezas
    3. Fallback: Si no hay plantillas, usa análisis de forma básico
    """

    # Piezas representadas por caracteres FEN
    PIECES = ['p', 'n', 'b', 'r', 'q', 'k', 'P', 'N', 'B', 'R', 'Q', 'K']

    def __init__(self):
        self.templates: Dict[str, np.ndarray] = {}
        self.empty_square_colors: Dict[str, np.ndarray] = {}
        self.calibrated = False
        self._light_square_color = None
        self._dark_square_color = None

    def calibrate_from_position(self, board_image: np.ndarray,
                                 square_size: int,
                                 fen: str = chess.STARTING_FEN):
        """
        Calibra el detector desde una imagen del tablero con posición conocida.
        Extrae plantillas de cada tipo de pieza.
        
        board_image: imagen BGR del tablero completo
        square_size: tamaño de cada casilla
        fen: posición FEN conocida
        """
        board = chess.Board(fen)
        self.templates = {}
        self.empty_square_colors = {'light': [], 'dark': []}

        for row in range(8):
            for col in range(8):
                # Extraer la casilla
                x = col * square_size
                y = (7 - row) * square_size
                square_img = board_image[y:y+square_size, x:x+square_size]

                piece = board.piece_at(chess.square(col, row))

                # Determinar si la casilla es clara u oscura
                is_light = (col + row) % 2 == 0

                if piece is None:
                    # Casilla vacía - guardar color de referencia
                    center = square_img[square_size//4:3*square_size//4,
                                       square_size//4:3*square_size//4]
                    avg_color = np.mean(center, axis=(0, 1))
                    if is_light:
                        self.empty_square_colors['light'].append(avg_color)
                    else:
                        self.empty_square_colors['dark'].append(avg_color)
                else:
                    # Hay pieza - extraer como plantilla
                    piece_char = piece.symbol()
                    if piece_char not in self.templates:
                        # Usar la región central de la casilla como plantilla
                        margin = max(square_size // 8, 2)
                        piece_img = square_img[margin:square_size-margin,
                                              margin:square_size-margin]
                        self.templates[piece_char] = piece_img

        # Promediar colores de casillas vacías
        if self.empty_square_colors['light']:
            self._light_square_color = np.mean(self.empty_square_colors['light'], axis=0)
        if self.empty_square_colors['dark']:
            self._dark_square_color = np.mean(self.empty_square_colors['dark'], axis=0)

        self.calibrated = len(self.templates) > 0
        return self.calibrated

    def detect_board(self, board_image: np.ndarray, square_size: int) -> chess.Board:
        """
        Detecta la posición completa del tablero.
        Retorna un objeto chess.Board con la posición detectada.
        """
        if not self.calibrated:
            return self._detect_by_contour(board_image, square_size)

        board = chess.Board()
        board.clear_board()

        for row in range(8):
            for col in range(8):
                x = col * square_size
                y = (7 - row) * square_size
                square_img = board_image[y:y+square_size, x:x+square_size]

                piece = self._detect_square(square_img, col, row)
                if piece is not None:
                    board.set_piece_at(chess.square(col, row), piece)

        return board

    def _detect_square(self, square_img: np.ndarray,
                       col: int, row: int) -> Optional[chess.Piece]:
        """
        Detecta la pieza en una casilla individual.
        """
        if not self.calibrated:
            return self._detect_by_contour_single(square_img)

        # Primero verificar si la casilla está vacía
        if self._is_empty_square(square_img, col, row):
            return None

        # Template matching contra todas las plantillas
        best_match = None
        best_score = -1

        # Convertir a grayscale para matching
        gray_square = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)

        for piece_char, template in self.templates.items():
            gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

            # Redimensionar template si es necesario
            if gray_template.shape[0] > gray_square.shape[0] or \
               gray_template.shape[1] > gray_square.shape[1]:
                scale = min(gray_square.shape[0] / gray_template.shape[0],
                           gray_square.shape[1] / gray_template.shape[1])
                gray_template = cv2.resize(gray_template, None,
                                          fx=scale, fy=scale)

            if gray_template.shape[0] < 5 or gray_template.shape[1] < 5:
                continue

            result = cv2.matchTemplate(gray_square, gray_template,
                                       cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val > best_score:
                best_score = max_val
                best_match = piece_char

        if best_match and best_score > 0.3:
            return chess.Piece.from_symbol(best_match)

        # Fallback: detección por contorno
        return self._detect_by_contour_single(square_img)

    def _is_empty_square(self, square_img: np.ndarray,
                         col: int, row: int) -> bool:
        """Determina si una casilla está vacía comparando con el color esperado."""
        if self._light_square_color is None and self._dark_square_color is None:
            return False

        is_light = (col + row) % 2 == 0
        expected_color = self._light_square_color if is_light else self._dark_square_color

        if expected_color is None:
            return False

        # Comparar el centro de la casilla con el color esperado
        h, w = square_img.shape[:2]
        center = square_img[h//4:3*h//4, w//4:3*w//4]
        avg_color = np.mean(center, axis=(0, 1))

        diff = np.abs(avg_color - expected_color)
        mean_diff = np.mean(diff)

        # Umbral: si la diferencia es pequeña, la casilla está vacía
        return mean_diff < 25

    def _detect_by_contour(self, board_image: np.ndarray,
                           square_size: int) -> chess.Board:
        """
        Detección de piezas por análisis de contorno (fallback).
        Menos preciso pero no requiere calibración.
        """
        board = chess.Board()
        board.clear_board()

        gray = cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY)
        # Aplicar umbral adaptativo
        _, thresh = cv2.threshold(gray, 0, 255,
                                   cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        for row in range(8):
            for col in range(8):
                x = col * square_size
                y = (7 - row) * square_size
                square_thresh = thresh[y:y+square_size, x:x+square_size]

                piece = self._analyze_contour(square_thresh, square_size)
                if piece is not None:
                    board.set_piece_at(chess.square(col, row), piece)

        return board

    def _detect_by_contour_single(self, square_img: np.ndarray) -> Optional[chess.Piece]:
        """Analiza una casilla individual por contorno."""
        gray = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255,
                                   cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return self._analyze_contour(thresh, gray.shape[0])

    def _analyze_contour(self, thresh: np.ndarray,
                         square_size: int) -> Optional[chess.Piece]:
        """
        Analiza un contorno para determinar el tipo de pieza.
        Nota: Solo puede determinar si hay una pieza y su color.
        Para el tipo, se necesita template matching u otra técnica.
        """
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Filtrar contornos pequeños (ruido)
        min_area = (square_size * 0.15) ** 2
        max_area = (square_size * 0.85) ** 2

        valid_contours = [c for c in contours
                         if min_area < cv2.contourArea(c) < max_area]

        if not valid_contours:
            return None

        # Tomar el contorno más grande
        contour = max(valid_contours, key=cv2.contourArea)
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / max(h, 1)
        extent = area / max(w * h, 1)

        # Determinar color de la pieza (blanca o negra)
        # Las piezas claras tienen más píxeles blancos en el original
        # Esto es un heurística simple
        is_white = self._determine_piece_color(contour, thresh, square_size)

        # Clasificar por forma (heurística basada en propiedades del contorno)
        piece_type = self._classify_piece_by_shape(contour, area, aspect_ratio,
                                                    extent, square_size)

        color = chess.WHITE if is_white else chess.BLACK
        return chess.Piece(piece_type, color)

    def _determine_piece_color(self, contour: np.ndarray,
                                thresh: np.ndarray,
                                square_size: int) -> bool:
        """
        Determina si la pieza es blanca o negra.
        Heurística: crear máscara de la pieza y analizar brillo promedio.
        """
        mask = np.zeros(thresh.shape, dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)

        # Analizar la silueta - piezas negras en temas claros
        # aparecen más "llenas" en la umbralización
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        contour_area = cv2.contourArea(contour)
        solidity = contour_area / max(hull_area, 1)

        # Heurística basada en la posición vertical del centro de masa
        moments = cv2.moments(contour)
        if moments['m00'] > 0:
            cy = moments['m01'] / moments['m00']
            cx = moments['m10'] / moments['m00']

            # Centro de masa más alto = pieza más "alta" (posiblemente más blanca en algunos temas)
            # Esto es muy dependiente del tema, así que usamos un fallback
            pass

        # Por defecto, asumir que la pieza es del color que contrasta con
        # el fondo del tablero. Esto es imperfecto pero funcional.
        return solidity > 0.6  # Heurística muy básica

    def _classify_piece_by_shape(self, contour: np.ndarray, area: float,
                                  aspect_ratio: float, extent: float,
                                  square_size: int) -> int:
        """
        Clasifica el tipo de pieza por análisis de forma.
        Retorna chess.PAWN, chess.KNIGHT, etc.
        """
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / max(hull_area, 1)

        # Altura relativa de la pieza
        x, y, w, h = cv2.boundingRect(contour)
        height_ratio = h / square_size
        width_ratio = w / square_size

        # Momentos de Hu (invariantes a escala y rotación)
        moments = cv2.moments(contour)
        hu = cv2.HuMoments(moments).flatten()

        # Clasificación heurística basada en propiedades de forma
        # Estas reglas son aproximadas y pueden necesitar ajuste

        if height_ratio < 0.4:
            # Pieza muy baja = probablemente un peón
            return chess.PAWN
        elif width_ratio > 0.6 and height_ratio > 0.7:
            # Pieza ancha y alta = probablemente dama o rey
            if solidity > 0.7:
                return chess.QUEEN
            return chess.KING
        elif aspect_ratio < 0.7:
            # Pieza estrecha = probablemente alfil o caballo
            # El caballo tiene una forma irregular (solidez menor)
            if solidity < 0.6:
                return chess.KNIGHT
            return chess.BISHOP
        else:
            # Ancho normal = torre o peón
            if height_ratio > 0.6:
                return chess.ROOK
            return chess.PAWN

    def save_templates(self, path: str):
        """Guarda las plantillas calibradas en disco."""
        import json
        data = {
            'calibrated': self.calibrated,
            'templates': {},
            'light_color': self._light_square_color.tolist() if self._light_square_color is not None else None,
            'dark_color': self._dark_square_color.tolist() if self._dark_square_color is not None else None,
        }
        for piece_char, template in self.templates.items():
            # Guardar templates como archivos de imagen
            template_path = f"{path}_{piece_char}.png"
            cv2.imwrite(template_path, template)
            data['templates'][piece_char] = template_path

        with open(f"{path}_meta.json", 'w') as f:
            json.dump(data, f, indent=2)

    def load_templates(self, path: str) -> bool:
        """Carga plantillas previamente guardadas."""
        import json
        meta_path = f"{path}_meta.json"
        try:
            with open(meta_path, 'r') as f:
                data = json.load(f)

            self.calibrated = data.get('calibrated', False)
            self.templates = {}

            for piece_char, template_path in data.get('templates', {}).items():
                template = cv2.imread(template_path)
                if template is not None:
                    self.templates[piece_char] = template

            if data.get('light_color'):
                self._light_square_color = np.array(data['light_color'])
            if data.get('dark_color'):
                self._dark_square_color = np.array(data['dark_color'])

            return self.calibrated
        except Exception:
            return False
