@echo off
title AutoChess - Generador de Ejecutable

echo.
echo  ================================================
echo      AutoChess - Generador de Ejecutable
echo  ================================================
echo.

REM Verificar Python primero
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python no esta instalado.
    echo  Descargalo de: https://www.python.org/downloads/
    echo  IMPORTANTE: Marca "Add Python to PATH" al instalar.
    echo.
    pause
    exit /b 1
)

echo  [1/4] Python encontrado:
python --version
echo.

REM Buscar la raiz del proyecto (donde esta requirements.txt)
REM Intentar desde la ubicacion del .bat
set "PROJECT_ROOT=%~dp0.."

if exist "%PROJECT_ROOT%\requirements.txt" (
    cd /d "%PROJECT_ROOT%"
    goto :found
)

REM Intentar un nivel mas arriba
set "PROJECT_ROOT=%~dp0..\.."
if exist "%PROJECT_ROOT%\requirements.txt" (
    cd /d "%PROJECT_ROOT%"
    goto :found
)

REM Intentar desde el directorio actual
if exist "requirements.txt" (
    goto :found
)

REM Si no lo encuentra, mostrar error detallado
echo  [ERROR] No se encuentra requirements.txt
echo.
echo  El script intento buscarlo en:
echo    - %~dp0..
echo    - %~dp0..\..
echo    - %CD%
echo.
echo  Estructura esperada:
echo    auto-chess/
echo      ejecutable/
echo        GENERAR_EXE.bat  (este archivo)
echo      requirements.txt   (debe estar aqui)
echo      auto_chess/
echo.
echo  Si descargaste el ZIP de GitHub, asegurate de que
echo  la estructura de carpetas sea correcta.
echo.
pause
exit /b 1

:found
echo  [2/4] Instalando dependencias...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo  [ERROR] No se pudieron instalar las dependencias.
    echo.
    echo  Intenta ejecutar manualmente:
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo          Dependencias instaladas OK
echo.

echo  [3/4] Instalando PyInstaller...
pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo  [ERROR] No se pudo instalar PyInstaller.
    pause
    exit /b 1
)
echo          PyInstaller instalado OK
echo.

echo  [4/4] Generando AutoChess.exe (puede tardar 2-5 min)...
echo.

pyinstaller --name AutoChess --onefile --windowed --noconfirm --clean --hidden-import chess --hidden-import chess.engine --hidden-import cv2 --hidden-import numpy --hidden-import mss --collect-all chess --collect-all mss auto_chess\main.py

if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] No se pudo generar el ejecutable.
    echo.
    echo  Posibles causas:
    echo    - Faltan dependencias (ejecuta: pip install -r requirements.txt)
    echo    - Python no tiene permisos suficientes
    echo    - Hay un proceso usando archivos en dist/ o build/
    echo.
    pause
    exit /b 1
)

echo.
echo  ================================================
echo     EJECUTABLE GENERADO EXITOSAMENTE
echo  ================================================
echo.
echo   Ubicacion: dist\AutoChess.exe
echo.
echo   Copia AutoChess.exe a donde quieras y ejecutalo.
echo   Necesitas Stockfish instalado.
echo.
echo   Para instalar Stockfish:
echo     winget install stockfish
echo.
echo  ================================================
echo.

explorer dist

pause
