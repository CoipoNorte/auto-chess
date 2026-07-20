"""
Controlador de mouse humanizado.
Reemplaza los movimientos mecánicos por trayectorias naturales
que simulan el comportamiento de una mano humana.
"""
import time
import random
import logging
from typing import Tuple, List, Optional

import numpy as np

from auto_chess.stealth.humanizer import HumanBehavior, HumanizationConfig

logger = logging.getLogger(__name__)


class HumanizedMouse:
    """
    Controla el mouse con comportamiento humanizado.
    Envuelve pyautogui con movimientos y delays naturales.
    """

    def __init__(self, config: HumanizationConfig = None):
        self.config = config or HumanizationConfig()
        self.behavior = HumanBehavior(self.config)
        self._pyautogui = None
        self._current_pos = (0, 0)  # Última posición conocida del cursor

    def _ensure_pyautogui(self):
        if self._pyautogui is None:
            import pyautogui
            self._pyautogui = pyautogui
            self._pyautogui.PAUSE = 0.01
            self._pyautogui.FAILSAFE = True  # Mover mouse a esquina = abortar

    def human_click(self, target: Tuple[int, int],
                    with_offset: bool = True) -> None:
        """
        Hace click en una posición con offset humano y movimiento natural.
        
        target: coordenadas destino (centro de la casilla)
        with_offset: si True, aplica offset aleatorio al click
        """
        self._ensure_pyautogui()

        # Obtener posición actual del cursor
        try:
            current = self._pyautogui.position()
            start = (current.x, current.y)
        except Exception:
            start = self._current_pos

        # Calcular offset humano
        if with_offset:
            offset = self.behavior.get_click_offset()
            actual_target = (target[0] + offset[0], target[1] + offset[1])
        else:
            actual_target = target

        # Mover el mouse con trayectoria natural
        self._human_move_to(actual_target, start)

        # Pequeña pausa antes del click (humano no es instantáneo)
        pre_click_delay = random.uniform(0.02, 0.08)
        time.sleep(pre_click_delay)

        # Hacer click
        self._pyautogui.click(actual_target[0], actual_target[1])

        self._current_pos = actual_target
        logger.debug(f"Click humanizado en {actual_target} (offset: {offset if with_offset else (0,0)})")

    def human_move_to(self, target: Tuple[int, int]) -> None:
        """Mueve el mouse a una posición con trayectoria natural."""
        self._ensure_pyautogui()

        try:
            current = self._pyautogui.position()
            start = (current.x, current.y)
        except Exception:
            start = self._current_pos

        self._human_move_to(target, start)
        self._current_pos = target

    def _human_move_to(self, target: Tuple[int, int],
                       start: Tuple[int, int]) -> None:
        """
        Mueve el mouse desde start hasta target con trayectoria humanizada.
        Usa curvas de Bézier + micro-temblor.
        """
        self._ensure_pyautogui()

        # Calcular distancia
        dx = target[0] - start[0]
        dy = target[1] - start[1]
        distance = (dx**2 + dy**2) ** 0.5

        # Si la distancia es muy pequeña, mover directamente
        if distance < 5:
            self._pyautogui.moveTo(target[0], target[1])
            return

        # Duración del movimiento (Ley de Fitts)
        duration = self.behavior.get_mouse_duration(int(distance))

        # Generar trayectoria
        num_points = max(int(distance / 10), 10)  # Más puntos = más suave
        path = self.behavior.get_mouse_path(start, target, num_points)

        # Tiempo entre cada punto
        time_per_point = duration / len(path)

        # Mover a lo largo de la trayectoria
        for point in path:
            self._pyautogui.moveTo(point[0], point[1])
            # Pequeña variación en el timing
            actual_delay = time_per_point * random.gauss(1.0, 0.1)
            time.sleep(max(actual_delay, 0.005))

    def human_double_click(self, target: Tuple[int, int]) -> None:
        """Doble click humanizado."""
        self._ensure_pyautogui()
        self.human_click(target)
        time.sleep(random.uniform(0.05, 0.15))
        self.human_click(target, with_offset=True)

    def human_drag(self, start: Tuple[int, int],
                   end: Tuple[int, int]) -> None:
        """
        Arrastra desde start hasta end con comportamiento humano.
        """
        self._ensure_pyautogui()

        # Mover al inicio
        self.human_move_to(start)
        time.sleep(random.uniform(0.05, 0.15))

        # Presionar mouse
        self._pyautogui.mouseDown()
        time.sleep(random.uniform(0.05, 0.12))

        # Mover al final con trayectoria
        self._human_move_to(end, start)
        time.sleep(random.uniform(0.03, 0.08))

        # Soltar mouse
        self._pyautogui.mouseUp()

    def simulate_hover(self, position: Tuple[int, int],
                       duration: float = None) -> None:
        """Simula que el cursor se detiene sobre una posición (hover)."""
        self.human_move_to(position)
        if duration is None:
            duration = self.behavior.get_hover_duration()

        # Durante el hover, hacer micro-movimientos (temblor natural)
        start_time = time.time()
        while time.time() - start_time < duration:
            tremor_x = random.randint(-1, 1)
            tremor_y = random.randint(-1, 1)
            try:
                self._pyautogui.moveRel(tremor_x, tremor_y)
            except Exception:
                pass
            time.sleep(random.uniform(0.05, 0.15))

    def simulate_look_away(self, board_center: Tuple[int, int],
                           board_size: int) -> None:
        """
        Simula que el usuario mira fuera del tablero brevemente.
        Mueve el mouse a una zona fuera del tablero.
        """
        # Elegir un punto fuera del tablero
        offset = board_size // 2 + random.randint(50, 150)
        angle = random.uniform(0, 2 * math.pi)

        import math
        target_x = int(board_center[0] + offset * math.cos(angle))
        target_y = int(board_center[1] + offset * math.sin(angle))

        # Asegurar que esté en pantalla
        target_x = max(0, min(1920, target_x))
        target_y = max(0, min(1080, target_y))

        self.human_move_to((target_x, target_y))
        time.sleep(random.uniform(0.5, 2.0))

    def natural_delay(self, base_seconds: float = 1.0,
                      variance: float = 0.3) -> None:
        """Pausa con duración naturalizada."""
        delay = base_seconds * random.gauss(1.0, variance)
        delay = max(delay, base_seconds * 0.5)
        time.sleep(delay)


class HumanizedClickSequence:
    """
    Orquesta una secuencia completa de clicks para un movimiento de ajedrez,
    con comportamiento humanizado en cada paso.
    """

    def __init__(self, mouse: HumanizedMouse):
        self.mouse = mouse
        self.behavior = mouse.behavior

    def execute_move_click(self, from_pos: Tuple[int, int],
                           to_pos: Tuple[int, int],
                           position_complexity: float = 0.5,
                           is_capture: bool = False) -> None:
        """
        Ejecuta un movimiento completo con comportamiento humano:
        1. Piensa (delay antes de mover)
        2. Posiblemente hace hover sobre la pieza
        3. Click en origen
        4. Delay natural
        5. Mueve a destino
        6. Click en destino
        """
        # Paso 0: ¿Distracción?
        if self.behavior.should_distract():
            distraction_time = self.behavior.get_distraction_duration()
            logger.debug(f"Pausa de distracción: {distraction_time:.1f}s")
            time.sleep(distraction_time)

        # Paso 1: Tiempo de "pensamiento"
        think_time = self.behavior.get_think_delay(position_complexity, is_capture)
        logger.debug(f"Pensando por {think_time:.2f}s...")
        time.sleep(think_time)

        # Paso 2: ¿Hover sobre la pieza antes de moverla?
        if self.behavior.should_hover():
            hover_duration = self.behavior.get_hover_duration()
            logger.debug(f"Hover sobre pieza por {hover_duration:.2f}s")
            self.mouse.simulate_hover(from_pos, hover_duration)

        # Paso 3: Click en origen
        logger.debug("Click en casilla origen")
        self.mouse.human_click(from_pos, with_offset=True)

        # Paso 4: Delay entre clicks
        action_delay = self.behavior.get_action_delay()
        time.sleep(action_delay)

        # Paso 5: Mover a destino (con trayectoria natural)
        logger.debug("Moviendo a casilla destino")
        self.mouse.human_click(to_pos, with_offset=True)

        # Paso 6: Registrar el movimiento
        self.behavior.register_move()

    def execute_drag_move(self, from_pos: Tuple[int, int],
                          to_pos: Tuple[int, int],
                          position_complexity: float = 0.5,
                          is_capture: bool = False) -> None:
        """
        Ejecuta un movimiento con drag-and-drop humanizado.
        """
        # Tiempo de pensamiento
        think_time = self.behavior.get_think_delay(position_complexity, is_capture)
        time.sleep(think_time)

        # Hover opcional
        if self.behavior.should_hover():
            self.mouse.simulate_hover(from_pos)

        # Drag humanizado
        self.mouse.human_drag(from_pos, to_pos)
        self.behavior.register_move()


import math
