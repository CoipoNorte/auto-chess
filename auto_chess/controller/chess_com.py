"""
Controlador de chess.com.
Automatiza la interacción con el tablero de chess.com mediante clicks.
Incluye humanización de comportamiento para reducir detección.
"""
import time
import random
import logging
import chess
from typing import Tuple, Optional

from auto_chess.config import BoardConfig, AutomationConfig, StealthConfig
from auto_chess.stealth.humanizer import HumanBehavior, HumanizationConfig
from auto_chess.stealth.mouse_controller import HumanizedMouse
from auto_chess.stealth.anti_pattern import AntiPatternEngine

logger = logging.getLogger(__name__)


class ChessComController:
    """
    Controla chess.com mediante automatización de mouse.
    Soporta click-to-move y drag-and-drop.
    Incluye comportamiento humanizado para parecer un jugador real.
    """

    def __init__(self, board_config: BoardConfig,
                 automation_config: AutomationConfig = None,
                 stealth_config: StealthConfig = None):
        self.board_config = board_config
        self.auto_config = automation_config or AutomationConfig()
        self.stealth_config = stealth_config or StealthConfig()

        # Componentes de humanización
        self._human_behavior: Optional[HumanBehavior] = None
        self._humanized_mouse: Optional[HumanizedMouse] = None
        self._anti_pattern: Optional[AntiPatternEngine] = None

        self._pyautogui = None
        self._init_stealth()

    def _init_stealth(self):
        """Inicializa los componentes de humanización."""
        if not self.stealth_config.enabled:
            return

        # Convertir StealthConfig a HumanizationConfig
        hc = HumanizationConfig(
            base_delay_min=self.stealth_config.base_delay_min,
            base_delay_max=self.stealth_config.base_delay_max,
            think_extra_delay_min=int(self.stealth_config.min_reaction_time * 1000),
            think_extra_delay_max=int(self.stealth_config.min_reaction_time * 3000),
            distraction_pause_chance=self.stealth_config.distraction_pause_chance,
            distraction_pause_min=self.stealth_config.distraction_pause_min,
            distraction_pause_max=self.stealth_config.distraction_pause_max,
            click_offset_max=self.stealth_config.click_offset_max,
            click_offset_sigma=self.stealth_config.click_offset_sigma,
            mouse_speed_min=self.stealth_config.mouse_speed_min,
            mouse_speed_max=self.stealth_config.mouse_speed_max,
            mouse_curve_factor=self.stealth_config.mouse_curve_factor,
            mouse_tremor_amplitude=self.stealth_config.mouse_tremor_amplitude,
            hover_before_move_chance=self.stealth_config.hover_before_move_chance,
            look_away_chance=self.stealth_config.look_away_chance,
        )

        self._human_behavior = HumanBehavior(hc)
        self._humanized_mouse = HumanizedMouse(hc)
        self._anti_pattern = AntiPatternEngine()

    def _ensure_pyautogui(self):
        """Inicializa pyautogui si es necesario."""
        if self._pyautogui is None:
            import pyautogui
            self._pyautogui = pyautogui
            self._pyautogui.PAUSE = 0.01  # Mínimo para no bloquear

    def execute_move(self, move_uci: str,
                     board: chess.Board = None,
                     is_capture: bool = False) -> bool:
        """
        Ejecuta un movimiento en chess.com con comportamiento humanizado.
        move_uci: movimiento en formato UCI (e.g., "e2e4")
        board: posición actual para evaluar complejidad (opcional)
        is_capture: si el movimiento es una captura
        Retorna True si se ejecutó correctamente.
        """
        if not self.board_config.is_calibrated:
            logger.error("Tablero no calibrado")
            return False

        try:
            move = chess.Move.from_uci(move_uci)
        except ValueError:
            logger.error(f"Movimiento inválido: {move_uci}")
            return False

        from_square = move.from_square
        to_square = move.to_square

        from_col = chess.square_file(from_square)
        from_row = chess.square_rank(from_square)
        to_col = chess.square_file(to_square)
        to_row = chess.square_rank(to_square)

        from_pos = self.board_config.get_square_center(from_col, from_row)
        to_pos = self.board_config.get_square_center(to_col, to_row)

        # Determinar si es captura
        if board and not is_capture:
            is_capture = board.is_capture(move)

        # Calcular complejidad de la posición
        complexity = 0.5
        if board and self._anti_pattern:
            complexity = self._anti_pattern.__class__.__name__  # Fallback
            try:
                complexity = self._human_behavior.estimate_position_complexity(board)
            except Exception:
                pass

        # Ejecutar con o sin humanización
        if self.stealth_config.enabled and self._humanized_mouse:
            return self._humanized_move(from_pos, to_pos, complexity, is_capture)
        else:
            if self.auto_config.use_drag:
                return self._drag_move(from_pos, to_pos)
            else:
                return self._click_move(from_pos, to_pos)

    def _humanized_move(self, from_pos: Tuple[int, int],
                        to_pos: Tuple[int, int],
                        complexity: float = 0.5,
                        is_capture: bool = False) -> bool:
        """
        Ejecuta un movimiento con comportamiento completamente humanizado.
        """
        self._ensure_pyautogui()
        start_time = time.time()

        try:
            # Paso 0: ¿Distracción/pausa larga?
            if self._human_behavior.should_distract():
                distraction_time = self._human_behavior.get_distraction_duration()
                logger.debug(f"Pausa de distracción: {distraction_time:.1f}s")
                time.sleep(distraction_time)

            # Paso 1: Tiempo de "pensamiento"
            think_time = self._human_behavior.get_think_delay(complexity, is_capture)

            # Aplicar patrón anti-detección
            if self._anti_pattern:
                think_time = self._anti_pattern.apply_pattern_to_think_time(think_time)
                pre_move_delay = self._anti_pattern.get_pre_move_delay()
                think_time += pre_move_delay

            logger.debug(f"Pensando por {think_time:.2f}s (complejidad={complexity:.2f})")
            time.sleep(think_time)

            # Paso 2: ¿Hover sobre la pieza?
            if self._human_behavior.should_hover():
                hover_duration = self._human_behavior.get_hover_duration()
                logger.debug(f"Hover sobre pieza por {hover_duration:.2f}s")
                self._humanized_mouse.simulate_hover(from_pos, hover_duration)

            # Paso 3: Click en origen (con offset humano)
            logger.debug(f"Click origen: {from_pos}")
            self._humanized_mouse.human_click(from_pos, with_offset=True)

            # Paso 4: Delay entre clicks (natural)
            action_delay = self._human_behavior.get_action_delay()
            time.sleep(action_delay)

            # Paso 5: Click en destino (con trayectoria curva)
            logger.debug(f"Click destino: {to_pos}")
            self._humanized_mouse.human_click(to_pos, with_offset=True)

            # Paso 6: Registrar el timing
            total_time = time.time() - start_time
            if self._anti_pattern:
                self._anti_pattern.track_move_time(total_time)

            # Paso 7: Delay post-movimiento
            post_delay = random.uniform(0.1, 0.4)
            time.sleep(post_delay)

            logger.info(f"Movimiento ejecutado (humanizado): {total_time:.2f}s total")
            return True

        except Exception as e:
            logger.error(f"Error al ejecutar movimiento humanizado: {e}")
            return False

    def _click_move(self, from_pos: Tuple[int, int],
                    to_pos: Tuple[int, int]) -> bool:
        """
        Ejecuta un movimiento con click-to-move (sin humanización).
        """
        self._ensure_pyautogui()

        try:
            # Click en casilla origen
            self._pyautogui.click(from_pos[0], from_pos[1])
            time.sleep(self.auto_config.click_delay / 1000.0)

            # Click en casilla destino
            self._pyautogui.click(to_pos[0], to_pos[1])
            time.sleep(self.auto_config.move_delay / 1000.0)

            logger.info(f"Movimiento ejecutado (click): {from_pos} -> {to_pos}")
            return True

        except Exception as e:
            logger.error(f"Error al ejecutar movimiento: {e}")
            return False

    def _drag_move(self, from_pos: Tuple[int, int],
                   to_pos: Tuple[int, int]) -> bool:
        """
        Ejecuta un movimiento con drag-and-drop (sin humanización).
        """
        self._ensure_pyautogui()

        try:
            duration = 0.3

            self._pyautogui.moveTo(from_pos[0], from_pos[1])
            time.sleep(0.05)
            self._pyautogui.mouseDown()
            time.sleep(0.05)
            self._pyautogui.moveTo(to_pos[0], to_pos[1], duration=duration)
            time.sleep(0.05)
            self._pyautogui.mouseUp()
            time.sleep(self.auto_config.move_delay / 1000.0)

            logger.info(f"Movimiento ejecutado (drag): {from_pos} -> {to_pos}")
            return True

        except Exception as e:
            logger.error(f"Error al ejecutar drag: {e}")
            try:
                self._pyautogui.mouseUp()
            except Exception:
                pass
            return False

    def handle_promotion(self, to_pos: Tuple[int, int],
                        piece: str = 'q') -> bool:
        """
        Maneja el diálogo de promoción en chess.com.
        piece: 'q' (dama), 'r' (torre), 'b' (alfil), 'n' (caballo)
        """
        self._ensure_pyautogui()

        try:
            promotion_pieces = ['q', 'r', 'b', 'n']
            if piece not in promotion_pieces:
                piece = 'q'

            piece_index = promotion_pieces.index(piece)
            sq_size = self.board_config.square_size
            offset_y = -(piece_index + 0.5) * (sq_size * 0.6)

            promo_x = to_pos[0]
            promo_y = to_pos[1] + offset_y

            # Humanizar el click de promoción
            if self.stealth_config.enabled and self._humanized_mouse:
                # Pequeño delay antes de promocionar (humano lee el diálogo)
                time.sleep(random.uniform(0.3, 0.8))
                self._humanized_mouse.human_click((promo_x, promo_y))
            else:
                time.sleep(0.1)
                self._pyautogui.click(promo_x, promo_y)

            return True

        except Exception as e:
            logger.error(f"Error en promoción: {e}")
            return False

    def wait_for_opponent(self, timeout: float = None):
        """
        Espera el turno del oponente con comportamiento humano.
        Los humanos no se quedan perfectamente quietos.
        """
        if not self.stealth_config.enabled:
            time.sleep(timeout or 1.0)
            return

        timeout = timeout or self.auto_config.opponent_timeout
        start = time.time()

        while time.time() - start < timeout:
            # Comportamiento idle ocasional
            if self._anti_pattern:
                board_center = self.board_config.get_square_center(3, 3)
                board_size = self.board_config.square_size * 8
                self._anti_pattern.simulate_idle_behavior(board_center, board_size)

            time.sleep(random.uniform(0.5, 1.5))

    def move_to_square(self, col: int, row: int):
        """Mueve el cursor al centro de una casilla."""
        pos = self.board_config.get_square_center(col, row)
        if self.stealth_config.enabled and self._humanized_mouse:
            self._humanized_mouse.human_move_to(pos)
        else:
            self._ensure_pyautogui()
            self._pyautogui.moveTo(pos[0], pos[1])

    def get_stealth_stats(self) -> dict:
        """Retorna estadísticas de comportamiento stealth."""
        if self._anti_pattern:
            return self._anti_pattern.get_stats()
        return {}

    def reset_stealth(self):
        """Reinicia las estadísticas stealth."""
        if self._anti_pattern:
            self._anti_pattern.reset()
        if self._human_behavior:
            self._human_behavior.reset()

    @property
    def stealth_enabled(self) -> bool:
        return self.stealth_config.enabled

    @staticmethod
    def parse_move_input(move_str: str) -> Optional[str]:
        """
        Convierte una entrada de teclado a formato UCI.
        
        Formatos aceptados:
        - "e2e4" -> "e2e4" (formato UCI directo)
        - "e2 e4" -> "e2e4" (con espacio)
        - "Nf3" -> busca la jugada algebraica y la convierte
        - "nf3" -> igual, case-insensitive para piezas
        
        Retorna el movimiento en formato UCI o None si es inválido.
        """
        move_str = move_str.strip().lower().replace(' ', '')

        # Formato UCI directo (e.g., "e2e4")
        if len(move_str) == 4 and move_str[0] in 'abcdefgh' and \
           move_str[1] in '12345678' and \
           move_str[2] in 'abcdefgh' and \
           move_str[3] in '12345678':
            return move_str

        # Formato UCI con promoción (e.g., "e7e8q")
        if len(move_str) == 5 and move_str[0] in 'abcdefgh' and \
           move_str[1] in '12345678' and \
           move_str[2] in 'abcdefgh' and \
           move_str[3] in '12345678' and \
           move_str[4] in 'qrbn':
            return move_str

        return None

    @staticmethod
    def square_to_notation(col: int, row: int) -> str:
        """Convierte coordenadas (0-7, 0-7) a notación algebraica."""
        return f"{chr(ord('a') + col)}{row + 1}"

    @staticmethod
    def notation_to_square(notation: str) -> Optional[Tuple[int, int]]:
        """Convierte notación algebraica (e.g., 'e4') a (col, row)."""
        if len(notation) != 2:
            return None
        col = ord(notation[0].lower()) - ord('a')
        row = int(notation[1]) - 1
        if 0 <= col <= 7 and 0 <= row <= 7:
            return (col, row)
        return None
