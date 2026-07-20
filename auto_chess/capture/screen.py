"""
Módulo de captura de pantalla.
Usa mss para capturas rápidas del área del tablero.
"""
import numpy as np
from typing import Optional, Tuple
import time


class ScreenCapture:
    """Captura regiones de la pantalla usando mss."""

    def __init__(self):
        self._sct = None
        self._monitor = None

    def _ensure_sct(self):
        """Inicializa mss si es necesario."""
        if self._sct is None:
            import mss
            self._sct = mss.mss()

    def capture_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        Captura una región rectangular de la pantalla.
        Retorna un array numpy en formato BGR (OpenCV compatible).
        """
        self._ensure_sct()
        region = {"left": x, "top": y, "width": width, "height": height}
        img = self._sct.grab(region)
        # Convertir a numpy array (mss devuelve BGRA)
        frame = np.array(img)
        # Convertir BGRA a BGR
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]
        return frame

    def capture_full_screen(self) -> np.ndarray:
        """Captura la pantalla completa."""
        self._ensure_sct()
        monitor = self._sct.monitors[0]  # Pantalla completa
        img = self._sct.grab(monitor)
        frame = np.array(img)
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]
        return frame

    def capture_board(self, top_left: Tuple[int, int], size: int) -> np.ndarray:
        """
        Captura solo el área del tablero.
        top_left: esquina superior izquierda
        size: tamaño total del tablero (ancho = alto = size)
        """
        return self.capture_region(top_left[0], top_left[1], size, size)

    def capture_square(self, board_top_left: Tuple[int, int],
                       square_size: int, col: int, row: int,
                       white_at_bottom: bool = True) -> np.ndarray:
        """
        Captura una casilla individual del tablero.
        col: 0-7 (a-h)
        row: 0-7 (1-8)
        """
        if not white_at_bottom:
            col = 7 - col
            row = 7 - row

        x = board_top_left[0] + col * square_size
        y = board_top_left[1] + (7 - row) * square_size
        return self.capture_region(x, y, square_size, square_size)

    def get_window_info(self, title_partial: str) -> Optional[dict]:
        """
        Busca información de una ventana por título parcial.
        Retorna dict con 'left', 'top', 'width', 'height' o None.
        """
        try:
            import subprocess
            import platform

            if platform.system() == "Windows":
                return self._find_window_windows(title_partial)
            elif platform.system() == "Linux":
                return self._find_window_linux(title_partial)
            elif platform.system() == "Darwin":
                return self._find_window_macos(title_partial)
        except Exception:
            pass
        return None

    def _find_window_windows(self, title_partial: str) -> Optional[dict]:
        """Busca una ventana en Windows."""
        try:
            import ctypes
            from ctypes import wintypes
            import json

            # Usar PowerShell para encontrar la ventana
            ps_cmd = f'''
            Get-Process | Where-Object {{$_.MainWindowTitle -like "*{title_partial}*"}} |
            Select-Object Id, MainWindowTitle | ConvertTo-Json
            '''
            # Fallback: retornar None y dejar que el usuario calibre manualmente
            return None
        except Exception:
            return None

    def _find_window_linux(self, title_partial: str) -> Optional[dict]:
        """Busca una ventana en Linux usando xdotool."""
        try:
            import subprocess
            result = subprocess.run(
                ['xdotool', 'search', '--name', title_partial],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                window_id = result.stdout.strip().split('\n')[0]
                geo = subprocess.run(
                    ['xdotool', 'getwindowgeometry', '--shell', window_id],
                    capture_output=True, text=True, timeout=5
                )
                if geo.returncode == 0:
                    info = {}
                    for line in geo.stdout.strip().split('\n'):
                        if '=' in line:
                            k, v = line.split('=', 1)
                            info[k] = int(v)
                    return {
                        'left': info.get('X', 0),
                        'top': info.get('Y', 0),
                        'width': info.get('WIDTH', 0),
                        'height': info.get('HEIGHT', 0),
                    }
        except Exception:
            pass
        return None

    def _find_window_macos(self, title_partial: str) -> Optional[dict]:
        """Busca una ventana en macOS."""
        try:
            import subprocess
            script = f'''
            tell application "System Events"
                set windowList to every window of every process
                repeat with aWindow in windowList
                    if name of aWindow contains "{title_partial}" then
                        set {{x, y}} to position of aWindow
                        set {{w, h}} to size of aWindow
                        return x & "," & y & "," & w & "," & h
                    end if
                end repeat
            end tell
            '''
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and ',' in result.stdout:
                parts = result.stdout.strip().split(',')
                if len(parts) >= 4:
                    return {
                        'left': int(parts[0].strip()),
                        'top': int(parts[1].strip()),
                        'width': int(parts[2].strip()),
                        'height': int(parts[3].strip()),
                    }
        except Exception:
            pass
        return None

    def close(self):
        """Libera recursos."""
        if self._sct:
            self._sct.close()
            self._sct = None
