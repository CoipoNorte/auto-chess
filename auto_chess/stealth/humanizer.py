"""
Módulo de humanización de comportamiento.
Implementa técnicas para que la interacción con chess.com se asemeje
al comportamiento humano natural, reduciendo la probabilidad de detección.

NOTA: Estas medidas NO garantizan indetectabilidad. Su propósito es
hacer que la herramienta de accesibilidad funcione de forma más natural
para el caso de uso legítimo contra bots.
"""
import random
import time
import math
import logging
from typing import Tuple, Optional, List
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class HumanizationConfig:
    """Configuración del comportamiento humano."""
    # === Delays ===
    # Delay base entre acciones (ms)
    base_delay_min: int = 200
    base_delay_max: int = 800
    # Delay adicional después de pensar (ms)
    think_extra_delay_min: int = 100
    think_extra_delay_max: int = 2000
    # Pausa ocasional larga (como si el usuario se distrae) (ms)
    distraction_pause_chance: float = 0.05  # 5% de probabilidad por jugada
    distraction_pause_min: int = 3000
    distraction_pause_max: int = 15000

    # === Clicks ===
    # Desviación máxima del centro de la casilla (píxeles)
    click_offset_max: int = 8
    # El offset sigue una distribución normal (más probable cerca del centro)
    click_offset_sigma: float = 3.0

    # === Movimiento del mouse ===
    # Velocidad del movimiento (no instantáneo)
    mouse_speed_min: float = 0.2  # segundos mínimos para cruzar el tablero
    mouse_speed_max: float = 0.6
    # Curvatura del movimiento (no línea recta perfecta)
    mouse_curve_factor: float = 0.15
    # Micro-temblor en el cursor (simula mano humana)
    mouse_tremor_amplitude: int = 2  # píxeles
    mouse_tremor_frequency: float = 0.3  #Hz

    # === Tiempo de pensamiento ===
    # Variación en el tiempo de "pensamiento" antes de mover
    think_time_variance: float = 0.4  # ±40% del tiempo base
    # Tiempo extra en posiciones complejas
    complex_position_multiplier: float = 1.5
    # Mínimo tiempo de reacción (no mover instantáneamente)
    min_reaction_time: float = 0.8  # segundos
    # Tiempo extra para capturas (los humanos se fijan más)
    capture_extra_time: float = 0.5

    # === Comportamiento general ===
    # A veces hacer un "hover" sobre una pieza antes de moverla
    hover_before_move_chance: float = 0.3  # 30% de probabilidad
    hover_duration_min: float = 0.3
    hover_duration_max: float = 1.5
    # A veces mover el mouse fuera del tablero brevemente
    look_away_chance: float = 0.1  # 10% de probabilidad entre jugadas
    # A veces hacer scroll o moverse por la ventana
    idle_movement_chance: float = 0.15


class HumanBehavior:
    """
    Genera timings y movimientos que simulan comportamiento humano.
    """

    def __init__(self, config: HumanizationConfig = None):
        self.config = config or HumanizationConfig()
        self._move_count = 0
        self._last_think_time = 0
        self._fatigue_factor = 1.0  # Aumenta con el tiempo (se vuelve más lento)

    def get_think_delay(self, position_complexity: float = 0.5,
                        is_capture: bool = False) -> float:
        """
        Calcula un delay realista de "pensamiento" antes de mover.
        
        position_complexity: 0.0 (simple) a 1.0 (muy compleja)
        is_capture: si el movimiento es una captura
        """
        # Tiempo base con variación
        base_time = self.config.min_reaction_time
        variance = base_time * self.config.think_time_variance
        think_time = base_time + random.gauss(0, variance)

        # Posiciones complejas toman más tiempo
        complexity_bonus = position_complexity * 2.0 * self.config.complex_position_multiplier
        think_time += complexity_bonus

        # Capturas toman un poco más (el humano nota la captura)
        if is_capture:
            think_time += self.config.capture_extra_time

        # Fatiga: después de muchas jugadas, se vuelve un poco más lento
        fatigue_bonus = min(self._move_count * 0.02, 1.0) * 0.3
        think_time += fatigue_bonus

        # Variación natural (distribución normal)
        think_time *= random.gauss(1.0, 0.15)

        # Nunca menos que el mínimo
        think_time = max(think_time, self.config.min_reaction_time * 0.7)

        self._last_think_time = think_time
        return think_time

    def get_action_delay(self) -> float:
        """Delay entre acciones dentro de un mismo movimiento (ej: entre clicks)."""
        delay = random.uniform(
            self.config.base_delay_min / 1000.0,
            self.config.base_delay_max / 1000.0
        )
        # Pequeña variación gaussiana
        delay *= random.gauss(1.0, 0.2)
        return max(delay, 0.05)

    def get_click_offset(self) -> Tuple[int, int]:
        """
        Genera un offset aleatorio para el click.
        No siempre se hace click exactamente en el centro.
        Usa distribución normal (más probable cerca del centro).
        """
        sigma = self.config.click_offset_sigma
        max_offset = self.config.click_offset_max

        dx = random.gauss(0, sigma)
        dy = random.gauss(0, sigma)

        # Limitar al máximo
        dx = max(-max_offset, min(max_offset, dx))
        dy = max(-max_offset, min(max_offset, dy))

        return (int(dx), int(dy))

    def get_mouse_path(self, start: Tuple[int, int],
                       end: Tuple[int, int],
                       num_points: int = 20) -> List[Tuple[int, int]]:
        """
        Genera una trayectoria de mouse naturalizada.
        Usa curvas de Bézier en vez de líneas rectas,
        con micro-temblor añadido.
        """
        points = []

        # Punto de control para curva de Bézier (desvía ligeramente)
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2

        # Desviación perpendicular a la línea
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx**2 + dy**2)

        if length > 0:
            # Vector perpendicular normalizado
            perp_x = -dy / length
            perp_y = dx / length

            # Punto de control: desviación aleatoria perpendicular
            curve_offset = length * self.config.mouse_curve_factor * random.gauss(0, 0.5)
            ctrl_x = mid_x + perp_x * curve_offset
            ctrl_y = mid_y + perp_y * curve_offset
        else:
            ctrl_x, ctrl_y = mid_x, mid_y

        # Generar puntos en curva cuadrática de Bézier
        for i in range(num_points + 1):
            t = i / num_points

            # Easing: aceleración y desaceleración natural
            # Usar ease-in-out (suave al inicio y final)
            t_eased = self._ease_in_out(t)

            # Curva cuadrática de Bézier: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
            x = (1-t_eased)**2 * start[0] + 2*(1-t_eased)*t_eased * ctrl_x + t_eased**2 * end[0]
            y = (1-t_eased)**2 * start[1] + 2*(1-t_eased)*t_eased * ctrl_y + t_eased**2 * end[1]

            # Añadir micro-temblor (simula pulso de la mano)
            tremor_x = random.gauss(0, self.config.mouse_tremor_amplitude * 0.5)
            tremor_y = random.gauss(0, self.config.mouse_tremor_amplitude * 0.5)

            points.append((int(x + tremor_x), int(y + tremor_y)))

        # Asegurar que el último punto sea exactamente el destino
        points[-1] = end

        return points

    def get_mouse_duration(self, distance: int) -> float:
        """
        Calcula la duración del movimiento del mouse.
        Basado en la Ley de Fitts: tiempo proporcional a la distancia.
        """
        # Normalizar distancia respecto al tamaño del tablero (aprox 600px)
        normalized_distance = distance / 600.0

        # Tiempo base escalado por distancia
        duration = (self.config.mouse_speed_min +
                   normalized_distance * (self.config.mouse_speed_max - self.config.mouse_speed_min))

        # Variación natural
        duration *= random.gauss(1.0, 0.15)
        duration = max(duration, 0.1)  # Mínimo 100ms

        return duration

    def should_hover(self) -> bool:
        """¿Debería el cursor hacer hover sobre la pieza antes de moverla?"""
        return random.random() < self.config.hover_before_move_chance

    def get_hover_duration(self) -> float:
        """Duración del hover sobre la pieza."""
        return random.uniform(
            self.config.hover_duration_min,
            self.config.hover_duration_max
        )

    def should_distract(self) -> bool:
        """¿Debería simular una distracción (pausa larga)?"""
        return random.random() < self.config.distraction_pause_chance

    def get_distraction_duration(self) -> float:
        """Duración de la distracción simulada."""
        return random.uniform(
            self.config.distraction_pause_min / 1000.0,
            self.config.distraction_pause_max / 1000.0
        )

    def should_look_away(self) -> bool:
        """¿Debería mover el mouse fuera del tablero brevemente?"""
        return random.random() < self.config.look_away_chance

    def register_move(self):
        """Registra que se hizo un movimiento (para tracking de fatiga)."""
        self._move_count += 1

    def _ease_in_out(self, t: float) -> float:
        """Función de easing suave (aceleración y desaceleración)."""
        # Suave ease-in-out usando interpolación cúbica
        if t < 0.5:
            return 4 * t**3
        else:
            return 1 - (-2 * t + 2)**3 / 2

    def estimate_position_complexity(self, board) -> float:
        """
        Estima la complejidad de la posición actual.
        Retorna un valor entre 0.0 y 1.0.
        
        Factores:
        - Número de piezas atacadas/defendidas
        - Si hay jaque
        - Número de movimientos legales (más = más complejo)
        - Si hay piezas colgando
        """
        try:
            import chess

            complexity = 0.0

            # Número de movimientos legales (promedio ~30 en apertura, menos en final)
            legal_moves = len(list(board.legal_moves))
            complexity += min(legal_moves / 80.0, 0.3)  # Max 0.3 por esto

            # Jaque = más complejo
            if board.is_check():
                complexity += 0.2

            # Número de piezas en el tablero
            piece_count = len(board.piece_map())
            # Más piezas = posición más compleja (en general)
            complexity += min(piece_count / 32.0, 0.3)

            # Si hay capturas disponibles (el humano evalúa las capturas)
            captures = [m for m in board.legal_moves if board.is_capture(m)]
            complexity += min(len(captures) / 10.0, 0.2)

            return min(complexity, 1.0)

        except Exception:
            return 0.5  # Default: complejidad media

    def reset(self):
        """Reinicia el contador de movimientos."""
        self._move_count = 0
        self._last_think_time = 0
        self._fatigue_factor = 1.0
