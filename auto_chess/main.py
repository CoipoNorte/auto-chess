"""
Punto de entrada principal de AutoChess.
"""
import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            os.path.join(os.path.expanduser("~"), ".autochess.log"),
            mode='a'
        )
    ]
)

logger = logging.getLogger(__name__)


def check_dependencies():
    """Verifica que las dependencias necesarias estén instaladas."""
    missing = []

    try:
        import PyQt5
    except ImportError:
        missing.append("PyQt5")

    try:
        import chess
    except ImportError:
        missing.append("python-chess")

    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")

    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    try:
        import mss
    except ImportError:
        missing.append("mss")

    if missing:
        print("=" * 60)
        print("FALTAN DEPENDENCIAS")
        print("=" * 60)
        print(f"\nInstale las siguientes dependencias:\n")
        print(f"  pip install {' '.join(missing)}")
        print(f"\nO instale todo con:")
        print(f"  pip install -r requirements.txt")
        print("=" * 60)
        return False

    return True


def check_stockfish():
    """Verifica que Stockfish esté disponible. Retorna la ruta si lo encuentra."""
    import shutil
    import glob

    # 1. Primero verificar si ya esta configurado en el config
    try:
        from auto_chess.config import AppConfig
        config = AppConfig.load()
        if config.engine.stockfish_path and os.path.exists(config.engine.stockfish_path):
            logger.info(f"Stockfish encontrado (config): {config.engine.stockfish_path}")
            return config.engine.stockfish_path
    except Exception:
        pass

    # 2. Buscar en PATH del sistema
    stockfish_path = shutil.which("stockfish")
    if stockfish_path:
        logger.info(f"Stockfish encontrado (PATH): {stockfish_path}")
        return stockfish_path

    # 3. Buscar en ubicaciones comunes
    user_home = os.path.expanduser("~")
    common_paths = [
        # Windows - ubicaciones estandar
        r"C:\Program Files\Stockfish\stockfish.exe",
        r"C:\Program Files (x86)\Stockfish\stockfish.exe",
        os.path.join(user_home, r"AppData\Local\Programs\Stockfish\stockfish.exe"),
        os.path.join(user_home, r"AppData\Local\Microsoft\WinGet\Links\stockfish.exe"),
        # Windows - busqueda recursiva en WinGet Packages
        os.path.join(user_home, r"AppData\Local\Microsoft\WinGet\Packages"),
        # Descargas (si el usuario lo descargo manualmente)
        os.path.join(user_home, r"Downloads\stockfish.exe"),
        os.path.join(user_home, r"Desktop\stockfish.exe"),
        # macOS
        "/usr/local/bin/stockfish",
        "/opt/homebrew/bin/stockfish",
        # Linux
        "/usr/bin/stockfish",
        "/usr/local/bin/stockfish",
    ]

    for path in common_paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                # Si es un directorio (WinGet Packages), buscar dentro
                found = glob.glob(os.path.join(path, "**", "stockfish*.exe"), recursive=True)
                if found:
                    logger.info(f"Stockfish encontrado (WinGet): {found[0]}")
                    return found[0]
            else:
                logger.info(f"Stockfish encontrado: {path}")
                return path

    # 4. Busqueda amplia en el sistema (Windows)
    if sys.platform == 'win32':
        search_dirs = [
            os.path.join(user_home, "AppData", "Local"),
            os.path.join(user_home, "AppData", "Roaming"),
            r"C:\Program Files",
            r"C:\Program Files (x86)",
        ]
        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                found = glob.glob(os.path.join(search_dir, "**", "stockfish*.exe"), recursive=True)
                if found:
                    logger.info(f"Stockfish encontrado (busqueda): {found[0]}")
                    return found[0]

    logger.warning("Stockfish no encontrado en el sistema")
    return None


def main():
    """Función principal."""
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)

    # Verificar Stockfish (advertencia, no error)
    stockfish_path = check_stockfish()
    if not stockfish_path:
        print("\n⚠ ADVERTENCIA: Stockfish no encontrado.")
        print("  La herramienta necesita Stockfish para funcionar.")
        print("  Descargue desde: https://stockfishchess.org/download/")
        print("  O instale con: ")
        print("    Windows: winget install stockfish")
        print("    macOS:   brew install stockfish")
        print("    Linux:   sudo apt install stockfish")
        print("  (Puede continuar, pero el motor no estara disponible)\n")
    else:
        # Guardar la ruta encontrada en la config
        try:
            from auto_chess.config import AppConfig
            config = AppConfig.load()
            config.engine.stockfish_path = stockfish_path
            config.save()
        except Exception:
            pass

    # Verificar plataforma
    if sys.platform not in ('win32', 'darwin', 'linux'):
        print(f"⚠ Plataforma no soportada: {sys.platform}")
        print("  Esta herramienta está diseñada para Windows, macOS o Linux.")

    # Iniciar la aplicación Qt
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt

    # Habilitar alto DPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("AutoChess Assistant")
    app.setApplicationVersion("1.0.0")

    # Icono de la aplicacion
    from PyQt5.QtGui import QIcon
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Estilo global
    app.setStyle("Fusion")

    from auto_chess.ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    logger.info("AutoChess Assistant iniciado")
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
