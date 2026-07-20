"""
Módulo de seguridad avanzada.
Implementa medidas adicionales para proteger la cuenta del usuario:
- Detección de ventana activa
- Límites de sesión
- Timer de descanso obligatorio
- Limpieza de rastros
- Verificación de estado de partida
- Detección de patrones sospechosos
"""
import time
import random
import logging
import os
from typing import Optional, Callable

from auto_chess.config import SecurityConfig

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Gestiona la seguridad de la sesión de juego.
    Aplica límites, verifica estado, y protege la cuenta.
    """

    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self._session_start = time.time()
        self._games_played = 0
        self._moves_this_game = 0
        self._last_game_end = 0
        self._is_resting = False
        self._rest_end_time = 0
        self._on_limit_reached: Optional[Callable] = None
        self._on_rest_required: Optional[Callable] = None
        self._on_security_warning: Optional[Callable] = None

    def can_play(self) -> tuple:
        """
        Verifica si se puede seguir jugando.
        Retorna (allowed: bool, reason: str)
        """
        # Verificar límite de partidas
        if self._games_played >= self.config.max_games_per_session:
            return False, f"Límite de {self.config.max_games_per_session} partidas por sesión alcanzado"

        # Verificar tiempo de sesión
        session_hours = (time.time() - self._session_start) / 3600
        if session_hours >= self.config.max_session_hours:
            return False, f"Sesión de {self.config.max_session_hours}h alcanzada. Descansa un poco."

        # Verificar si estamos en descanso obligatorio
        if self._is_resting:
            if time.time() < self._rest_end_time:
                remaining = int(self._rest_end_time - time.time())
                return False, f"Descanso obligatorio. Espera {remaining}s más."
            else:
                self._is_resting = False

        return True, "OK"

    def register_game_start(self):
        """Registra el inicio de una nueva partida."""
        # Verificar si necesita descanso largo
        if (self._games_played > 0 and
            self._games_played % self.config.long_rest_every_n_games == 0 and
            not self._is_resting):
            self._require_long_rest()
            return

        # Verificar descanso entre partidas
        if self._last_game_end > 0:
            time_since_last = time.time() - self._last_game_end
            required_rest = random.uniform(
                self.config.rest_between_games_min,
                self.config.rest_between_games_max
            )
            if time_since_last < required_rest:
                wait_time = required_rest - time_since_last
                self._require_rest(wait_time)
                return

        self._moves_this_game = 0
        logger.info(f"Partida #{self._games_played + 1} iniciada")

    def register_game_end(self):
        """Registra el fin de una partida."""
        self._games_played += 1
        self._last_game_end = time.time()
        logger.info(
            f"Partida #{self._games_played} terminada. "
            f"Movimientos: {self._moves_this_game}. "
            f"Tiempo sesión: {(time.time() - self._session_start)/60:.0f}min"
        )

    def register_move(self):
        """Registra un movimiento en la partida actual."""
        self._moves_this_game += 1

    def _require_rest(self, duration: float):
        """Requiere un descanso antes de continuar."""
        self._is_resting = True
        self._rest_end_time = time.time() + duration
        logger.info(f"Descanso requerido: {duration:.0f}s")
        if self._on_rest_required:
            self._on_rest_required(duration)

    def _require_long_rest(self):
        """Requiere un descanso largo."""
        duration = random.uniform(
            self.config.long_rest_min * 60,
            self.config.long_rest_max * 60
        )
        logger.info(f"Descanso LARGO requerido: {duration/60:.0f} minutos")
        self._require_rest(duration)

    def is_chess_window_active(self) -> bool:
        """
        Verifica si la ventana de chess.com está en primer plano.
        """
        try:
            import platform
            system = platform.system()

            if system == "Windows":
                return self._check_window_windows()
            elif system == "Linux":
                return self._check_window_linux()
            elif system == "Darwin":
                return self._check_window_macos()
        except Exception as e:
            logger.debug(f"No se pudo verificar ventana activa: {e}")
            return True  # Si no podemos verificar, asumir OK

    def _check_window_windows(self) -> bool:
        """Verifica ventana activa en Windows."""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buff, length + 1)
                title = buff.value.lower()
                return 'chess' in title or 'chrome' in title or 'firefox' in title or 'edge' in title or 'brave' in title
        except Exception:
            pass
        return True

    def _check_window_linux(self) -> bool:
        """Verifica ventana activa en Linux."""
        try:
            import subprocess
            result = subprocess.run(
                ['xdotool', 'getactivewindow', 'getwindowname'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                title = result.stdout.strip().lower()
                return 'chess' in title or 'chrome' in title or 'firefox' in title
        except Exception:
            pass
        return True

    def _check_window_macos(self) -> bool:
        """Verifica ventana activa en macOS."""
        try:
            import subprocess
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
            end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                app_name = result.stdout.strip().lower()
                return 'chrome' in app_name or 'firefox' in app_name or 'safari' in app_name
        except Exception:
            pass
        return True

    def wait_for_chess_window(self) -> bool:
        """
        Espera a que la ventana de chess.com esté activa.
        Retorna True si se activó, False si timeout.
        """
        if not self.config.require_chess_active:
            return True

        timeout = self.config.chess_wait_timeout
        start = time.time()

        while time.time() - start < timeout:
            if self.is_chess_window_active():
                return True
            time.sleep(1.0)

        logger.warning("Timeout esperando ventana de chess.com")
        return False

    def get_varied_elo(self, base_elo: int) -> int:
        """
        Retorna un ELO variado para la partida actual.
        Evita patrones predecibles de ELO.
        """
        if not self.config.vary_elo_between_games:
            return base_elo

        variation = random.randint(
            -self.config.elo_variation_range,
            self.config.elo_variation_range
        )
        varied = base_elo + variation
        varied = max(300, min(3000, varied))
        logger.debug(f"ELO variado: {base_elo} -> {varied}")
        return varied

    def should_play_suboptimal(self) -> bool:
        """¿Debería esta jugada ser subóptima intencionalmente?"""
        return random.random() < self.config.intentional_suboptimal_chance

    def clear_session_logs(self):
        """Limpia los logs de la sesión."""
        log_path = os.path.join(os.path.expanduser("~"), ".autochess.log")
        if self.config.clear_log_on_exit and os.path.exists(log_path):
            try:
                os.remove(log_path)
                logger.info("Log de sesión limpiado")
            except Exception as e:
                logger.warning(f"No se pudo limpiar log: {e}")

    def get_session_summary(self) -> dict:
        """Retorna resumen de la sesión actual."""
        session_time = time.time() - self._session_start
        return {
            'games_played': self._games_played,
            'session_minutes': session_time / 60,
            'moves_this_game': self._moves_this_game,
            'is_resting': self._is_resting,
            'rest_remaining': max(0, self._rest_end_time - time.time()) if self._is_resting else 0,
            'games_until_long_rest': (
                self.config.long_rest_every_n_games -
                (self._games_played % self.config.long_rest_every_n_games)
            ) if self._games_played > 0 else self.config.long_rest_every_n_games,
            'max_games': self.config.max_games_per_session,
            'max_hours': self.config.max_session_hours,
        }

    def set_on_limit_reached(self, callback: Callable):
        self._on_limit_reached = callback

    def set_on_rest_required(self, callback: Callable):
        self._on_rest_required = callback

    def set_on_security_warning(self, callback: Callable):
        self._on_security_warning = callback

    def reset(self):
        """Reinicia la sesión."""
        self._session_start = time.time()
        self._games_played = 0
        self._moves_this_game = 0
        self._last_game_end = 0
        self._is_resting = False
