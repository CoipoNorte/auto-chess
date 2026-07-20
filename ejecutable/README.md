# ♟ AutoChess - Generar Ejecutable

## Método Rápido (1 click)

1. **Doble click** en `GENERAR_EXE.bat`
2. Espera 2-5 minutos
3. El `.exe` se genera en `dist/AutoChess.exe`

## Requisitos previos

- **Python 3.8+** → [Descargar](https://www.python.org/downloads/)
  - ⚠️ Marca **"Add Python to PATH"** al instalar
- **Stockfish** → `winget install stockfish` o [descargar](https://stockfishchess.org/download/)
- **Git** (opcional, para clonar el repo)

## Método Manual

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Instalar PyInstaller
pip install pyinstaller

# 3. Generar ejecutable
python build.py
```

## Después de generar

1. Copia `dist/AutoChess.exe` donde quieras
2. Ejecútalo
3. ¡Calibra el tablero y juega!

## Stockfish

Antes de usar AutoChess, instala Stockfish:

```
winget install stockfish
```

O descárgalo de: https://stockfishchess.org/download/

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `python no encontrado` | Instala Python y marca "Add to PATH" |
| `pip no encontrado` | Reinstala Python marcando la opción |
| `Stockfish no encontrado` | Ejecuta `winget install stockfish` |
| `Error al generar` | Ejecuta `pip install -r requirements.txt` primero |
| `El .exe no abre` | Verifica que Python y Stockfish estén instalados |
