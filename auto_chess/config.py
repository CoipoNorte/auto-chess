"""
Configuración global de AutoChess.
"""
import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Tuple


DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".autochess_config.json")


@dataclass
class BoardConfig:
    """Configuración del tablero (calibración)."""
    # Esquina superior-izquierda del tablero en coordenadas de pantalla (x, y)
    top_left: Tuple[int, int] = (0, 0)
    # Esquina inferior-derecha del tablero en coordenadas de pantalla (x, y)
    bottom_right: Tuple[int, int] = (0, 0)
    # Tamaño de cada casilla en píxeles
    square_size: int = 0
    # ¿Las blancas están abajo? (True = vista normal para blancas)
    white_at_bottom: bool = True
    # Offset del centro de la casilla para clicks
    click_offset: int = 0  # Se calcula automáticamente como square_size // 2
    # Ventana de chess.com (título parcial para identificación)
    window_title: str = "Chess"

    def calculate(self):
        """Recalcula valores derivados."""
        width = self.bottom_right[0] - self.top_left[0]
        height = self.bottom_right[1] - self.top_left[1]
        self.square_size = min(width, height) // 8
        self.click_offset = self.square_size // 2

    def get_square_center(self, col: int, row: int) -> Tuple[int, int]:
        """
        Obtiene el centro en píxeles de una casilla del tablero.
        col: 0-7 (a=0, h=7)
        row: 0-7 (1=0, 8=7)
        """
        if not self.white_at_bottom:
            col = 7 - col
            row = 7 - row

        x = self.top_left[0] + col * self.square_size + self.click_offset
        y = self.top_left[1] + (7 - row) * self.square_size + self.click_offset
        return (x, y)

    def get_square_rect(self, col: int, row: int) -> Tuple[int, int, int, int]:
        """
        Obtiene el rectángulo (x, y, w, h) de una casilla.
        """
        if not self.white_at_bottom:
            col = 7 - col
            row = 7 - row

        x = self.top_left[0] + col * self.square_size
        y = self.top_left[1] + (7 - row) * self.square_size
        return (x, y, self.square_size, self.square_size)

    @property
    def is_calibrated(self) -> bool:
        return self.square_size > 0


@dataclass
class EngineConfig:
    """Configuración del motor de ajedrez."""
    # Ruta al ejecutable de Stockfish (None = buscar en PATH)
    stockfish_path: Optional[str] = None
    # ELO objetivo (300-3000)
    elo: int = 1500
    # Tiempo máximo de pensamiento en segundos
    think_time: float = 2.0
    # Profundidad máxima de búsqueda
    max_depth: int = 12
    # Número de líneas principales a calcular (para sugerencias)
    multi_pv: int = 3


@dataclass
class DisplayConfig:
    """Configuración de visualización."""
    # Color de las flechas de sugerencia (RGBA)
    arrow_color_best: Tuple[int, int, int, int] = (0, 200, 0, 180)
    arrow_color_second: Tuple[int, int, int, int] = (0, 100, 255, 150)
    arrow_color_third: Tuple[int, int, int, int] = (255, 165, 0, 120)
    # Grosor de las flechas
    arrow_width: int = 4
    # Opacidad del overlay (0-255)
    overlay_opacity: int = 100
    # Mostrar evaluación numérica
    show_evaluation: bool = True
    # Frecuencia de captura de pantalla (ms)
    capture_interval: int = 500


@dataclass
class AutomationConfig:
    """Configuración de automatización."""
    # Delay entre clicks (ms)
    click_delay: int = 150
    # Delay después de mover (ms)
    move_delay: int = 300
    # Usar drag-and-drop en vez de click-to-move
    use_drag: bool = False
    # Tiempo de espera para respuesta del oponente (s)
    opponent_timeout: float = 30.0


@dataclass
class StealthConfig:
    """
    Configuración de humanización/stealth.
    Controla qué tan "humano" se comporta la herramienta.
    """
    # Activar humanización de comportamiento
    enabled: bool = True

    # === Delays ===
    # Delay base entre acciones (ms)
    base_delay_min: int = 200
    base_delay_max: int = 800
    # Tiempo mínimo de reacción antes de mover (s)
    min_reaction_time: float = 0.8
    # Variación en tiempo de pensamiento (0.0-1.0, fracción del base)
    think_time_variance: float = 0.4
    # Tiempo extra para capturas (s)
    capture_extra_time: float = 0.5
    # Multiplicador para posiciones complejas
    complex_position_multiplier: float = 1.5

    # === Pausas naturales ===
    # Probabilidad de pausa de distracción por jugada (0.0-1.0)
    distraction_pause_chance: float = 0.05
    # Duración de pausa de distracción (ms)
    distraction_pause_min: int = 3000
    distraction_pause_max: int = 15000

    # === Clicks ===
    # Desviación máxima del centro de la casilla (píxeles)
    click_offset_max: int = 8
    # Sigma para distribución normal del offset
    click_offset_sigma: float = 3.0

    # === Mouse ===
    # Velocidad del movimiento del mouse
    mouse_speed_min: float = 0.2
    mouse_speed_max: float = 0.6
    # Curvatura del movimiento (0.0 = recto, 1.0 = muy curvo)
    mouse_curve_factor: float = 0.15
    # Micro-temblor (píxeles)
    mouse_tremor_amplitude: int = 2

    # === Comportamiento ===
    # Probabilidad de hacer hover antes de mover (0.0-1.0)
    hover_before_move_chance: float = 0.3
    # Probabilidad de mirar fuera del tablero (0.0-1.0)
    look_away_chance: float = 0.1
    # Probabilidad de comportamiento idle entre jugadas (0.0-1.0)
    idle_movement_chance: float = 0.15


@dataclass
class SecurityConfig:
    """Configuración de seguridad avanzada."""
    # Límites de sesión
    max_games_per_session: int = 10
    max_session_hours: float = 2.0
    rest_between_games_min: int = 3
    rest_between_games_max: int = 8
    long_rest_every_n_games: int = 5
    long_rest_min: int = 10
    long_rest_max: int = 20
    # Detección de ventana
    require_chess_active: bool = True
    wait_for_chess: bool = True
    chess_wait_timeout: float = 60.0
    # Anti-pattern avanzado
    vary_elo_between_games: bool = True
    elo_variation_range: int = 200
    intentional_suboptimal_chance: float = 0.05
    limit_opening_strength: bool = True
    # Limpieza
    clear_log_on_exit: bool = False
    sanitize_config: bool = True
    randomize_window_title: bool = True
    # Verificación
    verify_move_executed: bool = True
    opponent_response_timeout: float = 45.0
    patient_waiting: bool = True


@dataclass
class AppConfig:
    """Configuración principal de la aplicación."""
    board: BoardConfig = field(default_factory=BoardConfig)
    engine: EngineConfig = field(default_factory=EngineConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    stealth: StealthConfig = field(default_factory=StealthConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    def save(self, path: str = DEFAULT_CONFIG_PATH):
        """Guarda la configuración en un archivo JSON."""
        data = {
            'board': {
                'top_left': list(self.board.top_left),
                'bottom_right': list(self.board.bottom_right),
                'square_size': self.board.square_size,
                'white_at_bottom': self.board.white_at_bottom,
                'click_offset': self.board.click_offset,
                'window_title': self.board.window_title,
            },
            'engine': asdict(self.engine),
            'display': {
                'arrow_color_best': list(self.display.arrow_color_best),
                'arrow_color_second': list(self.display.arrow_color_second),
                'arrow_color_third': list(self.display.arrow_color_third),
                'arrow_width': self.display.arrow_width,
                'overlay_opacity': self.display.overlay_opacity,
                'show_evaluation': self.display.show_evaluation,
                'capture_interval': self.display.capture_interval,
            },
            'automation': asdict(self.automation),
            'stealth': asdict(self.stealth),
            'security': asdict(self.security),
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str = DEFAULT_CONFIG_PATH) -> 'AppConfig':
        """Carga la configuración desde un archivo JSON."""
        config = cls()
        if not os.path.exists(path):
            return config

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            if 'board' in data:
                b = data['board']
                config.board.top_left = tuple(b.get('top_left', [0, 0]))
                config.board.bottom_right = tuple(b.get('bottom_right', [0, 0]))
                config.board.square_size = b.get('square_size', 0)
                config.board.white_at_bottom = b.get('white_at_bottom', True)
                config.board.click_offset = b.get('click_offset', 0)
                config.board.window_title = b.get('window_title', 'Chess')

            if 'engine' in data:
                e = data['engine']
                config.engine.stockfish_path = e.get('stockfish_path')
                config.engine.elo = e.get('elo', 1500)
                config.engine.think_time = e.get('think_time', 2.0)
                config.engine.max_depth = e.get('max_depth', 12)
                config.engine.multi_pv = e.get('multi_pv', 3)

            if 'display' in data:
                d = data['display']
                config.display.arrow_color_best = tuple(d.get('arrow_color_best', [0, 200, 0, 180]))
                config.display.arrow_color_second = tuple(d.get('arrow_color_second', [0, 100, 255, 150]))
                config.display.arrow_color_third = tuple(d.get('arrow_color_third', [255, 165, 0, 120]))
                config.display.arrow_width = d.get('arrow_width', 4)
                config.display.overlay_opacity = d.get('overlay_opacity', 100)
                config.display.show_evaluation = d.get('show_evaluation', True)
                config.display.capture_interval = d.get('capture_interval', 500)

            if 'automation' in data:
                a = data['automation']
                config.automation.click_delay = a.get('click_delay', 150)
                config.automation.move_delay = a.get('move_delay', 300)
                config.automation.use_drag = a.get('use_drag', False)
                config.automation.opponent_timeout = a.get('opponent_timeout', 30.0)

            if 'stealth' in data:
                s = data['stealth']
                config.stealth.enabled = s.get('enabled', True)
                config.stealth.base_delay_min = s.get('base_delay_min', 200)
                config.stealth.base_delay_max = s.get('base_delay_max', 800)
                config.stealth.min_reaction_time = s.get('min_reaction_time', 0.8)
                config.stealth.think_time_variance = s.get('think_time_variance', 0.4)
                config.stealth.capture_extra_time = s.get('capture_extra_time', 0.5)
                config.stealth.complex_position_multiplier = s.get('complex_position_multiplier', 1.5)
                config.stealth.distraction_pause_chance = s.get('distraction_pause_chance', 0.05)
                config.stealth.distraction_pause_min = s.get('distraction_pause_min', 3000)
                config.stealth.distraction_pause_max = s.get('distraction_pause_max', 15000)
                config.stealth.click_offset_max = s.get('click_offset_max', 8)
                config.stealth.click_offset_sigma = s.get('click_offset_sigma', 3.0)
                config.stealth.mouse_speed_min = s.get('mouse_speed_min', 0.2)
                config.stealth.mouse_speed_max = s.get('mouse_speed_max', 0.6)
                config.stealth.mouse_curve_factor = s.get('mouse_curve_factor', 0.15)
                config.stealth.mouse_tremor_amplitude = s.get('mouse_tremor_amplitude', 2)
                config.stealth.hover_before_move_chance = s.get('hover_before_move_chance', 0.3)
                config.stealth.look_away_chance = s.get('look_away_chance', 0.1)
                config.stealth.idle_movement_chance = s.get('idle_movement_chance', 0.15)

            if 'security' in data:
                sec = data['security']
                config.security.max_games_per_session = sec.get('max_games_per_session', 10)
                config.security.max_session_hours = sec.get('max_session_hours', 2.0)
                config.security.rest_between_games_min = sec.get('rest_between_games_min', 3)
                config.security.rest_between_games_max = sec.get('rest_between_games_max', 8)
                config.security.long_rest_every_n_games = sec.get('long_rest_every_n_games', 5)
                config.security.long_rest_min = sec.get('long_rest_min', 10)
                config.security.long_rest_max = sec.get('long_rest_max', 20)
                config.security.require_chess_active = sec.get('require_chess_active', True)
                config.security.wait_for_chess = sec.get('wait_for_chess', True)
                config.security.chess_wait_timeout = sec.get('chess_wait_timeout', 60.0)
                config.security.vary_elo_between_games = sec.get('vary_elo_between_games', True)
                config.security.elo_variation_range = sec.get('elo_variation_range', 200)
                config.security.intentional_suboptimal_chance = sec.get('intentional_suboptimal_chance', 0.05)
                config.security.clear_log_on_exit = sec.get('clear_log_on_exit', False)
                config.security.randomize_window_title = sec.get('randomize_window_title', True)
                config.security.verify_move_executed = sec.get('verify_move_executed', True)
                config.security.opponent_response_timeout = sec.get('opponent_response_timeout', 45.0)

        except (json.JSONDecodeError, KeyError, TypeError):
            pass  # Usar valores por defecto

        return config


# Mapeo de ELO a parámetros de Stockfish
ELO_TO_ENGINE = {
    # (elo_min, elo_max): (skill_level, depth, random_move_chance)
    (300, 500): (0, 2, 0.4),
    (500, 800): (2, 4, 0.3),
    (800, 1000): (4, 5, 0.25),
    (1000, 1200): (6, 6, 0.2),
    (1200, 1400): (8, 8, 0.15),
    (1400, 1600): (10, 9, 0.1),
    (1600, 1800): (12, 10, 0.08),
    (1800, 2000): (14, 12, 0.05),
    (2000, 2200): (16, 14, 0.03),
    (2200, 2500): (18, 16, 0.01),
    (2500, 3001): (20, 20, 0.0),
}


def get_engine_params_for_elo(elo: int) -> dict:
    """Obtiene los parámetros del engine para un ELO dado."""
    for (elo_min, elo_max), params in ELO_TO_ENGINE.items():
        if elo_min <= elo < elo_max:
            return {
                'skill_level': params[0],
                'depth': params[1],
                'random_move_chance': params[2],
            }
    # Fallback
    return {'skill_level': 10, 'depth': 8, 'random_move_chance': 0.1}
