"""
Controlador anti-patrón: evita patrones mecánicos detectables.
Implementa variaciones en el comportamiento que rompen patrones
estadísticos que los sistemas anti-trampa podrían detectar.
"""
import random
import time
import logging
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class BehaviorPattern(Enum):
    """Patrones de comportamiento para variar el estilo."""
    AGGRESSIVE = "aggressive"     # Tiende a mover rápido
    CAREFUL = "careful"          # Tiende a tomarse más tiempo
    INCONSISTENT = "inconsistent" # Varía mucho entre rápido y lento
    METHODICAL = "methodical"     # Tiempo consistente pero con pausas


class AntiPatternEngine:
    """
    Previene que el comportamiento sea estadísticamente detectable.
    
    Los sistemas anti-trampa de chess.com buscan:
    1. Tiempos de movimiento demasiado consistentes (desviación estándar muy baja)
    2. Precisión perfecta en clicks (siempre al centro exacto)
    3. Patrones repetitivos (mismo delay entre cada acción)
    4. Ausencia de comportamiento idle (movimientos cuando no es tu turno)
    5. Movimientos siempre óptimos sin variación
    """

    def __init__(self):
        self._move_times: list = []
        self._current_pattern = BehaviorPattern.INCONSISTENT
        self._pattern_change_counter = 0
        self._pattern_change_threshold = random.randint(5, 15)
        self._session_start = time.time()

    def get_behavior_pattern(self) -> BehaviorPattern:
        """
        Retorna el patrón de comportamiento actual.
        Cambia periódicamente para no ser predecible.
        """
        self._pattern_change_counter += 1

        if self._pattern_change_counter >= self._pattern_change_threshold:
            # Cambiar patrón
            self._current_pattern = random.choice(list(BehaviorPattern))
            self._pattern_change_counter = 0
            self._pattern_change_threshold = random.randint(5, 15)
            logger.debug(f"Cambio de patrón a: {self._current_pattern.value}")

        return self._current_pattern

    def apply_pattern_to_think_time(self, base_time: float) -> float:
        """
        Modifica el tiempo de pensamiento según el patrón actual.
        """
        pattern = self.get_behavior_pattern()

        if pattern == BehaviorPattern.AGGRESSIVE:
            # Más rápido, con menos variación
            return base_time * random.uniform(0.6, 1.0)

        elif pattern == BehaviorPattern.CAREFUL:
            # Más lento, especialmente en jugadas importantes
            return base_time * random.uniform(1.2, 2.0)

        elif pattern == BehaviorPattern.INCONSISTENT:
            # Muy variable
            multiplier = random.choice([
                random.uniform(0.3, 0.7),  # Rápido
                random.uniform(1.0, 1.5),  # Normal
                random.uniform(2.0, 4.0),  # Lento
            ])
            return base_time * multiplier

        elif pattern == BehaviorPattern.METHODICAL:
            # Consistente pero con pausas ocasionales
            return base_time * random.gauss(1.0, 0.1)

        return base_time

    def should_make_suboptimal_move(self, elo_factor: float) -> bool:
        """
        Determina si debería hacer un movimiento subóptimo.
        Los humanos no siempre hacen la mejor jugada.
        
        elo_factor: qué tan fuerte debería jugar (0.0 = débil, 1.0 = fuerte)
        """
        # En ELOs bajos, más probabilidad de errores
        if elo_factor < 0.3:
            return random.random() < 0.25  # 25% de "errores" en ELO bajo
        elif elo_factor < 0.5:
            return random.random() < 0.10
        elif elo_factor < 0.7:
            return random.random() < 0.05
        else:
            return random.random() < 0.02  # Casi siempre óptimo en ELO alto

    def simulate_idle_behavior(self, board_center, board_size) -> bool:
        """
        Simula comportamiento idle cuando es turno del oponente.
        Los humanos no se quedan perfectamente quietos.
        
        Retorna True si realizó algún movimiento idle.
        """
        # 20% de probabilidad de hacer algo idle por cada segundo de espera
        if random.random() > 0.20:
            return False

        idle_action = random.choice([
            'micro_movement',   # Pequeño movimiento del mouse
            'scroll_chat',      # Scrollea el chat (si existe)
            'look_at_clock',    # Mira el reloj
            'none',             # No hacer nada (también es humano)
        ])

        if idle_action == 'none':
            return False

        logger.debug(f"Comportamiento idle: {idle_action}")
        return True

    def get_pre_move_delay(self) -> float:
        """
        Delay antes de hacer el primer click en un turno.
        Los humanos necesitan un momento para procesar la posición.
        """
        pattern = self.get_behavior_pattern()

        if pattern == BehaviorPattern.AGGRESSIVE:
            return random.uniform(0.5, 1.5)
        elif pattern == BehaviorPattern.CAREFUL:
            return random.uniform(2.0, 5.0)
        elif pattern == BehaviorPattern.INCONSISTENT:
            return random.choice([
                random.uniform(0.3, 1.0),
                random.uniform(1.5, 3.0),
                random.uniform(4.0, 8.0),
            ])
        else:  # METHODICAL
            return random.gauss(2.0, 0.5)

    def track_move_time(self, move_time: float):
        """Registra el tiempo de un movimiento para análisis estadístico."""
        self._move_times.append(move_time)

        # Mantener solo los últimos 50 movimientos
        if len(self._move_times) > 50:
            self._move_times = self._move_times[-50:]

    def get_stats(self) -> dict:
        """Retorna estadísticas del comportamiento actual."""
        if not self._move_times:
            return {
                'avg_time': 0,
                'std_dev': 0,
                'min_time': 0,
                'max_time': 0,
                'num_moves': 0,
                'pattern': self._current_pattern.value,
            }

        import statistics
        return {
            'avg_time': statistics.mean(self._move_times),
            'std_dev': statistics.stdev(self._move_times) if len(self._move_times) > 1 else 0,
            'min_time': min(self._move_times),
            'max_time': max(self._move_times),
            'num_moves': len(self._move_times),
            'pattern': self._current_pattern.value,
            'session_duration': time.time() - self._session_start,
        }

    def reset(self):
        """Reinicia las estadísticas."""
        self._move_times = []
        self._pattern_change_counter = 0
        self._session_start = time.time()
