# ♟ AutoChess Assistant

> **Herramienta de accesibilidad** para jugar ajedrez en chess.com contra bots.
> Diseñada para personas con túnel carpiano u otras condiciones que dificultan el uso del mouse.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Security](https://img.shields.io/badge/Security-Humanized-green)

---

## ⚠️ Aviso Importante

Esta herramienta está diseñada **exclusivamente para uso personal contra bots** en chess.com como herramienta de accesibilidad. Su uso contra jugadores humanos viola los Términos de Servicio de chess.com.

---

## 📋 Características

### Tres Modos de Juego

| Modo | Descripción | Uso |
|------|-------------|-----|
| 🤖 **Auto** | El motor juega automáticamente | Seleccione ELO y color, la tool hace el resto |
| ⌨️ **Teclado** | Escriba sus jugadas y la tool las ejecuta | Escriba "e2e4", "Nf3", etc. |
| 💡 **Sugerencia** | Flechas clickeables sobre el tablero | Click en la flecha que prefiera |

### 🎨 Interfaz Moderna
- **Tema oscuro** profesional con colores vibrantes
- **Asistente de inicio rápido** (wizard) para primer uso
- **Badges de estado** en tiempo real (engine, seguridad)
- **Cards con bordes de acento** por sección
- **Tipografía Segoe UI** moderna y legible

### 🛡️ Seguridad Avanzada (Protección de Cuenta)

| Característica | Descripción |
|----------------|-------------|
| ⏱️ **Delays naturales** | Tiempo de "pensamiento" variable, gaussiano |
| 🖱️ **Clicks imperfectos** | Distribución normal, no siempre al centro |
| 🔄 **Mouse con curvas** | Bézier + micro-temblor (mano humana) |
| 👆 **Hover natural** | A veces "duda" sobre la pieza antes de mover |
| 😴 **Pausas de distracción** | 5% probabilidad de pausa larga (3-15s) |
| 📊 **Rotación de patrones** | Alterna agresivo/cauteloso/inconsistente/metódico |
| 🌊 **Fatiga simulada** | Se vuelve más lento con el tiempo |
| 🔒 **Límites de sesión** | Máx 10 partidas / 2 horas (configurable) |
| 🕐 **Descansos obligatorios** | 3-8 min entre partidas, 10-20 min cada 5 partidas |
| 🪟 **Detección de ventana** | Solo mueve si chess.com está activa |
| 🎲 **Variación de ELO** | ±200 ELO aleatorio entre partidas |
| 🏷️ **Título aleatorio** | La ventana se muestra como "System Settings" |
| 🧹 **Limpieza de logs** | Opción de borrar rastros al cerrar |

---

## 🚀 Instalación Rápida

### Requisitos Previos

1. **Python 3.8+** instalado ([descargar](https://www.python.org/downloads/))
2. **Stockfish** instalado:
   - Windows: `winget install stockfish` o [descargar](https://stockfishchess.org/download/)
   - macOS: `brew install stockfish`
   - Linux: `sudo apt install stockfish`

### Instalación desde código fuente

```bash
# Clonar el repositorio
git clone https://github.com/CoipoNorte/auto-chess.git
cd auto-chess

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python -m auto_chess.main
```

### Instalación como paquete

```bash
pip install -e .
auto-chess
```

---

## 📦 Generar Ejecutable (.exe)

Para crear un ejecutable que no requiera Python instalado:

```bash
# Instalar dependencias de build
pip install pyinstaller

# Generar ejecutable
python build.py

# El ejecutable estará en:
# Windows: dist/AutoChess.exe
# macOS:   dist/AutoChess
# Linux:   dist/AutoChess
```

> **Nota:** El ejecutable generado puede pesar 100-300 MB debido a OpenCV y PyQt.

---

## 📖 Uso

### 1. Calibración del Tablero

Antes de usar cualquier modo, debe calibrar la posición del tablero:

1. Abra chess.com en su navegador
2. Inicie una partida contra un bot
3. En AutoChess, haga click en **"📐 Calibrar Tablero"**
4. Haga click en **"Seleccionar esquina SUPERIOR-IZQUIERDA"** y luego click en la esquina superior-izquierda del tablero (casilla a8)
5. Haga click en **"Seleccionar esquina INFERIOR-DERECHA"** y luego click en la esquina inferior-derecha (casilla h1)
6. Verifique que el tamaño de casilla sea razonable (60-120 px)
7. Haga click en **"Guardar Calibración"**

> **Tip:** La calibración se guarda automáticamente. Solo necesita recalibrar si cambia la resolución o el tamaño del navegador.

### 2. Modo Auto (🤖)

1. Inicie una partida contra un bot en chess.com
2. Seleccione el ELO del bot (300-3000)
3. Elija su color (blancas o negras)
4. Haga click en **"▶ INICIAR Auto-Juego"**
5. La herramienta jugará automáticamente

**Controles:**
- **Pausar/Reanudar**: Pausa temporal sin detener
- **Detener**: Finaliza el modo auto

### 3. Modo Teclado (⌨️)

1. Active el modo haciendo click en **"⌨ Activar Modo Teclado"**
2. Escriba su jugada en el campo de texto
3. Presione **Enter** o click en **"Ejecutar"**

**Formatos aceptados:**

| Formato | Ejemplo | Descripción |
|---------|---------|-------------|
| UCI | `e2e4` | Casilla origen + destino |
| Algebraica | `Nf3` | Notación estándar de ajedrez |
| Simplificada | `e4` | Solo destino (sin ambigüedad) |
| Con promoción | `e7e8q` | UCI + pieza de promoción |

**Piezas en notación algebraica:**
- `K` = Rey (King)
- `Q` = Dama (Queen)
- `R` = Torre (Rook)
- `B` = Alfil (Bishop)
- `N` = Caballo (kNight)
- Sin letra = Peón

### 4. Modo Sugerencia (💡)

1. Haga click en **"💡 MOSTRAR Sugerencias"**
2. El overlay mostrará flechas sobre el tablero:
   - 🟢 **Verde** = Mejor jugada
   - 🔵 **Azul** = Segunda opción
   - 🟠 **Naranja** = Tercera opción
3. Haga click en la flecha que desee ejecutar
4. La jugada se realiza automáticamente

**Configuración:**
- Número de sugerencias (1-5)
- Auto-actualización cada N segundos
- Evaluación numérica visible

---

## 🎯 Configuración de ELO

| ELO | Nivel | Descripción |
|-----|-------|-------------|
| 300-500 | Principiante | Errores frecuentes, muy débil |
| 500-800 | Muy Fácil | Principiante avanzado |
| 800-1200 | Fácil | Jugador casual |
| 1200-1600 | Normal | Jugador intermedio-bajo |
| 1600-2000 | Intermedio | Buen jugador de club |
| 2000-2500 | Avanzado | Experto / Candidato a Maestro |
| 2500-3000 | Máximo | Nivel Gran Maestro |

---

## 🏗️ Arquitectura

```
auto_chess/
├── main.py                  # Punto de entrada
├── config.py                # Configuración y persistencia
├── ui/
│   ├── main_window.py       # Ventana principal de control
│   ├── overlay.py           # Overlay transparente (flechas)
│   └── calibration_dialog.py # Diálogo de calibración
├── capture/
│   ├── screen.py            # Captura de pantalla (mss)
│   └── board_reader.py      # Lector de tablero de alto nivel
├── engine/
│   └── chess_engine.py      # Integración con Stockfish
├── controller/
│   └── chess_com.py         # Automatización de clicks en chess.com
├── modes/
│   ├── auto_mode.py         # Modo automático
│   ├── keyboard_mode.py     # Modo teclado
│   └── suggest_mode.py      # Modo sugerencia
└── recognition/
    └── piece_detector.py    # Detección de piezas por visión
```

### Tecnologías

- **PyQt5**: Interfaz gráfica (ventana principal + overlay transparente)
- **python-chess**: Representación del tablero y validación de movimientos
- **Stockfish**: Motor de ajedrez para cálculo de jugadas
- **OpenCV (cv2)**: Reconocimiento de piezas por imagen
- **mss**: Captura de pantalla rápida
- **PyAutoGUI**: Automatización de clicks del mouse
- **pynput**: Detección de clicks globales (para calibración)

---

## 🛡️ Modo Stealth (Anti-Detección)

> **Importante**: Esta herramienta debe usarse **solo contra bots** y como herramienta de accesibilidad. Aún así, se incluyen medidas de humanización para mayor seguridad.

### ¿Qué hace el modo Stealth?

El modo stealth implementa múltiples técnicas de humanización para que la interacción con chess.com se asemeje al comportamiento de un jugador humano real:

| Técnica | Descripción |
|---------|-------------|
| ⏱️ **Delays naturales** | Tiempo de "pensamiento" variable antes de cada jugada |
| 🖱️ **Clicks imperfectos** | No siempre al centro exacto de la casilla (distribución normal) |
| 🔄 **Mouse con curvas** | Movimientos en curvas Bézier, no líneas rectas |
| 👆 **Hover natural** | A veces el cursor "duda" sobre una pieza antes de moverla |
| 😴 **Pausas de distracción** | Ocasionalmente pausas largas (como si miraras el celular) |
| 📊 **Patrones variables** | Alterna entre estilos: agresivo, cauteloso, inconsistente |
| 🌊 **Micro-temblor** | Simula el pulso natural de la mano en el cursor |
| 🎯 **Fatiga simulada** | Se vuelve ligeramente más lento conforme avanza la partida |

### Configuración Recomendada

- **Tiempo de reacción mínimo**: 0.8s - 1.5s (nunca instantáneo)
- **Desviación de click**: 5-10px (parece humano pero acierta)
- **Pausas de distracción**: 3-8% de probabilidad por jugada
- **Hover antes de mover**: 20-40% de las jugadas

### Consejos de Seguridad

1. **No juegue más de 8-10 partidas seguidas** - haga descansos reales
2. **Varíe el ELO del bot** - no siempre al máximo
3. **A veces pierda** - jugar solo aperturas y dejar que el bot gane
4. **Use el modo Sugerencia** - más control sobre cuándo ejecutar
5. **No use 24/7** - patrones de uso consistentes son detectables
6. **Cambie de tema de tablero** ocasionalmente
7. **No juegue en horarios exactos** todos los días

### Estadísticas de Sesión

El tab "🛡️ Stealth" muestra estadísticas en tiempo real:
- Tiempo promedio entre movimientos
- Desviación estándar (más alta = más humano)
- Patrón de comportamiento actual
- Número de movimientos registrados

> Un jugador humano típico tiene:
> - Tiempo promedio: 3-15s por movimiento
> - Desviación estándar: 2-8s (muy variable)
> - Capturas: tiempo ligeramente mayor

---

## 🔧 Resolución de Problemas

### "Stockfish no encontrado"
- Verifique que Stockfish esté instalado: `stockfish --help`
- En Windows, reinicie después de instalar
- Puede configurar la ruta manualmente editando `~/.autochess_config.json`

### "No se puede leer el tablero"
- Recalibre el tablero (la posición puede haber cambiado)
- Verifique que chess.com sea visible (no minimizado)
- Asegúrese de que el tema del tablero no haya cambiado drásticamente

### "Movimiento no ejecutado"
- Verifique que la calibración sea correcta
- Asegúrese de que no haya diálogos superpuestos en chess.com
- Aumente el delay entre clicks en la configuración

### El overlay no aparece
- Verifique que el tablero esté calibrado
- En algunos sistemas, las ventanas "siempre encima" pueden ser bloqueadas
- Intente hacer click en la ventana de AutoChess primero

---

## 📝 Notas de Accesibilidad

Esta herramienta fue diseñada específicamente para:
- Minimizar el uso del mouse (modo teclado)
- Eliminar la necesidad de precisión en clicks (modo auto)
- Proporcionar asistencia visual clara (modo sugerencia)
- Funcionar como aplicación independiente superpuesta

### Consejos de uso con túnel carpiano:

1. **Modo Auto**: Ideal para descanso completo de la mano
2. **Modo Teclado**: Use un teclado ergonómico; escriba las jugadas cómodamente
3. **Modo Sugerencia**: Solo necesita hacer un click amplio (las flechas son grandes)
4. **Pausas**: La herramienta incluye delays configurables entre movimientos
5. **Postura**: Coloque el monitor a la altura de los ojos para reducir tensión

---

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles.

---

## 🙏 Agradecimientos

- [Stockfish](https://stockfishchess.org/) - Motor de ajedrez de código abierto
- [python-chess](https://python-chess.readthedocs.io/) - Librería de ajedrez para Python
- [Chess.com](https://www.chess.com/) - Plataforma de ajedrez

---

*Hecho con ❤️ para la comunidad de ajedrez accesible*
