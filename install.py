#!/usr/bin/env python3
"""
Script de instalación rápida para AutoChess.
Detecta el sistema operativo e instala las dependencias necesarias.
"""
import os
import sys
import subprocess
import platform
import shutil


def print_header():
    print("""
╔══════════════════════════════════════════════════════╗
║           ♟ AutoChess Assistant - Instalador         ║
║                                                      ║
║   Herramienta de accesibilidad para ajedrez          ║
╚══════════════════════════════════════════════════════╝
    """)


def check_python_version():
    """Verifica la versión de Python."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} no es suficiente.")
        print("   Se requiere Python 3.8 o superior.")
        print("   Descargue desde: https://www.python.org/downloads/")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_requirements():
    """Instala las dependencias Python."""
    print("\n📦 Instalando dependencias Python...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencias instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False


def check_stockfish():
    """Verifica e intenta instalar Stockfish."""
    print("\n🔍 Buscando Stockfish...")

    # Verificar si ya está instalado
    stockfish_path = shutil.which("stockfish")
    if stockfish_path:
        print(f"✅ Stockfish encontrado: {stockfish_path}")
        return True

    system = platform.system()

    if system == "Windows":
        print("   Stockfish no encontrado.")
        print("   Opciones de instalación:")
        print("   1. winget install stockfish")
        print("   2. Descargar de: https://stockfishchess.org/download/")
        print("   3. chocolatey: choco install stockfish")

        # Intentar con winget
        try:
            print("\n   Intentando instalar con winget...")
            subprocess.check_call(["winget", "install", "stockfish", "--accept-package-agreements"])
            print("✅ Stockfish instalado con winget")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    elif system == "Darwin":  # macOS
        print("   Stockfish no encontrado.")
        print("   Instale con: brew install stockfish")

        try:
            print("\n   Intentando instalar con Homebrew...")
            subprocess.check_call(["brew", "install", "stockfish"])
            print("✅ Stockfish instalado con Homebrew")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    elif system == "Linux":
        print("   Stockfish no encontrado.")

        # Detectar distribución
        if shutil.which("apt"):
            try:
                print("   Intentando con apt...")
                subprocess.check_call(["sudo", "apt", "install", "-y", "stockfish"])
                print("✅ Stockfish instalado con apt")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        elif shutil.which("dnf"):
            try:
                print("   Intentando con dnf...")
                subprocess.check_call(["sudo", "dnf", "install", "-y", "stockfish"])
                print("✅ Stockfish instalado con dnf")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        elif shutil.which("pacman"):
            try:
                print("   Intentando con pacman...")
                subprocess.check_call(["sudo", "pacman", "-S", "--noconfirm", "stockfish"])
                print("✅ Stockfish instalado con pacman")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

    print("\n⚠ Stockfish no se pudo instalar automáticamente.")
    print("  Descargue desde: https://stockfishchess.org/download/")
    print("  La herramienta puede ejecutarse sin Stockfish,")
    print("  pero los modos de análisis no funcionarán.")
    return False


def verify_installation():
    """Verifica que todo esté correcto."""
    print("\n🔎 Verificando instalación...")

    checks = {
        "PyQt5": "PyQt5",
        "python-chess": "chess",
        "OpenCV": "cv2",
        "numpy": "numpy",
        "mss": "mss",
        "PyAutoGUI": "pyautogui",
        "pynput": "pynput",
    }

    all_ok = True
    for name, module in checks.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - NO INSTALADO")
            all_ok = False

    return all_ok


def create_shortcut():
    """Crea un acceso directo en el escritorio (Windows)."""
    system = platform.system()
    if system != "Windows":
        return

    try:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        script_path = os.path.abspath("run.py")

        # Crear un .bat simple
        bat_path = os.path.join(desktop, "AutoChess.bat")
        with open(bat_path, "w") as f:
            f.write(f'@echo off\nstart /b pythonw "{script_path}"\n')

        print(f"✅ Acceso directo creado: {bat_path}")
    except Exception:
        pass


def main():
    print_header()

    # Verificar Python
    if not check_python_version():
        sys.exit(1)

    # Instalar dependencias
    if not install_requirements():
        print("\n❌ No se pudieron instalar las dependencias.")
        sys.exit(1)

    # Verificar
    if not verify_installation():
        print("\n⚠ Algunas dependencias faltan.")
        print("  Intente: pip install -r requirements.txt")

    # Stockfish
    check_stockfish()

    # Crear acceso directo
    create_shortcut()

    print("""
╔══════════════════════════════════════════════════════╗
║                   INSTALACIÓN COMPLETE               ║
║                                                      ║
║  Para ejecutar:                                      ║
║    python -m auto_chess.main                         ║
║  o                                                   ║
║    python run.py                                     ║
║                                                      ║
║  Para generar ejecutable:                            ║
║    python build.py                                   ║
╚══════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
