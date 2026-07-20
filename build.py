"""
Script de build para generar el ejecutable con PyInstaller.
Ejecutar: python build.py
"""
import os
import sys
import subprocess
import platform


def build():
    """Construye el ejecutable con PyInstaller."""

    # Determinar plataforma
    system = platform.system()

    # Configurar PyInstaller
    name = "AutoChess"

    if system == "Windows":
        icon_path = "assets/icon.ico"
        if not os.path.exists(icon_path):
            icon_path = None
    else:
        icon_path = "assets/icon.png"
        if not os.path.exists(icon_path):
            icon_path = None

    # Comando de PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", name,
        "--windowed",  # No mostrar consola
        "--onefile",   # Un solo archivo
        "--noconfirm",
        "--clean",
    ]

    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])

    # Agregar datos adicionales
    cmd.extend([
        "--add-data", f"auto_chess{os.pathsep}auto_chess",
    ])

    # Ocultar consola en Windows
    if system == "Windows":
        cmd.append("--noconsole")

    # Entry point
    cmd.append("auto_chess/main.py")

    print("=" * 60)
    print("CONSTRUYENDO AutoChess")
    print("=" * 60)
    print(f"Plataforma: {system}")
    print(f"Python: {sys.version}")
    print(f"Comando: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, check=True)
        print()
        print("=" * 60)
        print("✅ BUILD EXITOSO")
        print("=" * 60)

        # Determinar ubicación del ejecutable
        if system == "Windows":
            exe_path = f"dist/{name}.exe"
        else:
            exe_path = f"dist/{name}"

        print(f"\nEjecutable generado: {exe_path}")
        print("\nNOTAS:")
        print("- Stockfish debe instalarse por separado")
        print("  Windows: winget install stockfish")
        print("  macOS:   brew install stockfish")
        print("  Linux:   sudo apt install stockfish")
        print()
        print("Para ejecutar:")
        print(f"  {exe_path}")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERROR EN EL BUILD: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ PyInstaller no encontrado. Instale con:")
        print("  pip install pyinstaller")
        sys.exit(1)


if __name__ == "__main__":
    build()
