"""
Sistema de temas visuales para AutoChess.
Proporciona estilos modernos y atractivos para toda la interfaz.
"""


class ThemeColors:
    """Paleta de colores del tema."""
    # Fondo principal
    BG_PRIMARY = "#0f1419"
    BG_SECONDARY = "#1a1f2e"
    BG_CARD = "#232b3e"
    BG_CARD_HOVER = "#2a3348"
    BG_INPUT = "#1e2636"

    # Acentos
    ACCENT_GREEN = "#00d68f"
    ACCENT_BLUE = "#3366ff"
    ACCENT_PURPLE = "#7c5cff"
    ACCENT_ORANGE = "#ff9f43"
    ACCENT_RED = "#ff6b6b"
    ACCENT_CYAN = "#00d2d3"

    # Texto
    TEXT_PRIMARY = "#e8eaf0"
    TEXT_SECONDARY = "#8b95a5"
    TEXT_MUTED = "#5a6577"
    TEXT_ON_ACCENT = "#ffffff"

    # Bordes
    BORDER = "#2d3548"
    BORDER_FOCUS = "#3366ff"
    BORDER_SUCCESS = "#00d68f"
    BORDER_ERROR = "#ff6b6b"

    # Estados
    SUCCESS = "#00d68f"
    WARNING = "#ff9f43"
    ERROR = "#ff6b6b"
    INFO = "#3366ff"


# QSS Global - Estilo completo de la aplicación
GLOBAL_STYLE = f"""
/* ===== WIDGETS BASE ===== */
QWidget {{
    background-color: {ThemeColors.BG_PRIMARY};
    color: {ThemeColors.TEXT_PRIMARY};
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {ThemeColors.BG_PRIMARY};
}}

/* ===== BOTONES ===== */
QPushButton {{
    background-color: {ThemeColors.BG_CARD};
    color: {ThemeColors.TEXT_PRIMARY};
    border: 1px solid {ThemeColors.BORDER};
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 500;
    font-size: 13px;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {ThemeColors.BG_CARD_HOVER};
    border-color: {ThemeColors.ACCENT_BLUE};
}}

QPushButton:pressed {{
    background-color: {ThemeColors.BG_SECONDARY};
}}

QPushButton:disabled {{
    color: {ThemeColors.TEXT_MUTED};
    border-color: {ThemeColors.BORDER};
    background-color: {ThemeColors.BG_SECONDARY};
}}

/* Botón primario (verde) */
QPushButton#btn_primary {{
    background-color: {ThemeColors.ACCENT_GREEN};
    color: #000000;
    border: none;
    font-weight: 700;
    font-size: 14px;
    padding: 12px 24px;
}}

QPushButton#btn_primary:hover {{
    background-color: #00e89b;
}}

QPushButton#btn_primary:pressed {{
    background-color: #00b876;
}}

/* Botón peligro (rojo) */
QPushButton#btn_danger {{
    background-color: {ThemeColors.ACCENT_RED};
    color: white;
    border: none;
    font-weight: 700;
}}

QPushButton#btn_danger:hover {{
    background-color: #ff8585;
}}

/* Botón sugerencia (naranja) */
QPushButton#btn_suggest {{
    background-color: {ThemeColors.ACCENT_ORANGE};
    color: #000000;
    border: none;
    font-weight: 700;
}}

QPushButton#btn_suggest:hover {{
    background-color: #ffb066;
}}

/* ===== GROUP BOX ===== */
QGroupBox {{
    background-color: {ThemeColors.BG_CARD};
    border: 1px solid {ThemeColors.BORDER};
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 24px;
    font-weight: 600;
    font-size: 13px;
    color: {ThemeColors.TEXT_SECONDARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    top: 8px;
    padding: 0 8px;
    color: {ThemeColors.ACCENT_BLUE};
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* ===== TABS ===== */
QTabWidget::pane {{
    border: 1px solid {ThemeColors.BORDER};
    border-radius: 10px;
    background-color: {ThemeColors.BG_SECONDARY};
    padding: 12px;
    margin-top: -1px;
}}

QTabBar::tab {{
    background-color: {ThemeColors.BG_SECONDARY};
    color: {ThemeColors.TEXT_SECONDARY};
    border: 1px solid {ThemeColors.BORDER};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 2px;
    font-weight: 500;
    min-width: 80px;
}}

QTabBar::tab:selected {{
    background-color: {ThemeColors.BG_CARD};
    color: {ThemeColors.TEXT_PRIMARY};
    border-bottom: 2px solid {ThemeColors.ACCENT_BLUE};
}}

QTabBar::tab:hover:!selected {{
    background-color: {ThemeColors.BG_CARD_HOVER};
    color: {ThemeColors.TEXT_PRIMARY};
}}

/* ===== INPUTS ===== */
QLineEdit {{
    background-color: {ThemeColors.BG_INPUT};
    color: {ThemeColors.TEXT_PRIMARY};
    border: 1px solid {ThemeColors.BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
    selection-background-color: {ThemeColors.ACCENT_BLUE};
}}

QLineEdit:focus {{
    border-color: {ThemeColors.ACCENT_BLUE};
    background-color: {ThemeColors.BG_SECONDARY};
}}

QLineEdit::placeholder {{
    color: {ThemeColors.TEXT_MUTED};
}}

QSpinBox {{
    background-color: {ThemeColors.BG_INPUT};
    color: {ThemeColors.TEXT_PRIMARY};
    border: 1px solid {ThemeColors.BORDER};
    border-radius: 6px;
    padding: 5px 10px;
    min-width: 60px;
}}

QSpinBox:focus {{
    border-color: {ThemeColors.ACCENT_BLUE};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {ThemeColors.BG_CARD};
    border: none;
    width: 18px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {ThemeColors.BG_CARD_HOVER};
}}

/* ===== SLIDER ===== */
QSlider::groove:horizontal {{
    border: none;
    height: 6px;
    background-color: {ThemeColors.BG_CARD};
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background-color: {ThemeColors.ACCENT_BLUE};
    border: 2px solid {ThemeColors.BG_PRIMARY};
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 12px;
}}

QSlider::handle:horizontal:hover {{
    background-color: #4d82ff;
    border-color: {ThemeColors.ACCENT_BLUE};
}}

QSlider::sub-page:horizontal {{
    background-color: {ThemeColors.ACCENT_BLUE};
    border-radius: 3px;
}}

/* ===== CHECKBOX ===== */
QCheckBox {{
    color: {ThemeColors.TEXT_PRIMARY};
    spacing: 10px;
    font-size: 13px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 5px;
    border: 2px solid {ThemeColors.BORDER};
    background-color: {ThemeColors.BG_INPUT};
}}

QCheckBox::indicator:checked {{
    background-color: {ThemeColors.ACCENT_GREEN};
    border-color: {ThemeColors.ACCENT_GREEN};
}}

QCheckBox::indicator:hover {{
    border-color: {ThemeColors.ACCENT_BLUE};
}}

/* ===== RADIO BUTTON ===== */
QRadioButton {{
    color: {ThemeColors.TEXT_PRIMARY};
    spacing: 10px;
    font-size: 13px;
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 12px;
    border: 2px solid {ThemeColors.BORDER};
    background-color: {ThemeColors.BG_INPUT};
}}

QRadioButton::indicator:checked {{
    background-color: {ThemeColors.ACCENT_BLUE};
    border-color: {ThemeColors.ACCENT_BLUE};
}}

/* ===== TEXT EDIT / LOG ===== */
QTextEdit {{
    background-color: {ThemeColors.BG_INPUT};
    color: {ThemeColors.TEXT_PRIMARY};
    border: 1px solid {ThemeColors.BORDER};
    border-radius: 8px;
    padding: 8px;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 12px;
    selection-background-color: {ThemeColors.ACCENT_BLUE};
}}

/* ===== LABELS ===== */
QLabel {{
    color: {ThemeColors.TEXT_PRIMARY};
    background-color: transparent;
}}

QLabel#title {{
    font-size: 22px;
    font-weight: 700;
    color: {ThemeColors.TEXT_PRIMARY};
}}

QLabel#subtitle {{
    font-size: 12px;
    color: {ThemeColors.TEXT_SECONDARY};
    font-style: italic;
}}

QLabel#status_ok {{
    color: {ThemeColors.SUCCESS};
    font-weight: 600;
}}

QLabel#status_warn {{
    color: {ThemeColors.WARNING};
    font-weight: 600;
}}

QLabel#status_error {{
    color: {ThemeColors.ERROR};
    font-weight: 600;
}}

/* ===== STATUS BAR ===== */
QStatusBar {{
    background-color: {ThemeColors.BG_SECONDARY};
    color: {ThemeColors.TEXT_SECONDARY};
    border-top: 1px solid {ThemeColors.BORDER};
    padding: 4px 12px;
    font-size: 12px;
}}

/* ===== MENU BAR ===== */
QMenuBar {{
    background-color: {ThemeColors.BG_SECONDARY};
    color: {ThemeColors.TEXT_PRIMARY};
    border-bottom: 1px solid {ThemeColors.BORDER};
    padding: 2px;
}}

QMenuBar::item {{
    padding: 6px 14px;
    border-radius: 6px;
}}

QMenuBar::item:selected {{
    background-color: {ThemeColors.BG_CARD};
}}

QMenu {{
    background-color: {ThemeColors.BG_CARD};
    color: {ThemeColors.TEXT_PRIMARY};
    border: 1px solid {ThemeColors.BORDER};
    border-radius: 8px;
    padding: 6px;
}}

QMenu::item {{
    padding: 8px 32px;
    border-radius: 6px;
}}

QMenu::item:selected {{
    background-color: {ThemeColors.ACCENT_BLUE};
    color: white;
}}

QMenu::separator {{
    height: 1px;
    background-color: {ThemeColors.BORDER};
    margin: 4px 12px;
}}

/* ===== SCROLLBAR ===== */
QScrollBar:vertical {{
    background-color: {ThemeColors.BG_SECONDARY};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {ThemeColors.BORDER};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {ThemeColors.TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {ThemeColors.BG_SECONDARY};
    height: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {ThemeColors.BORDER};
    border-radius: 5px;
    min-width: 30px;
}}

/* ===== FRAME ===== */
QFrame#separator {{
    background-color: {ThemeColors.BORDER};
    max-height: 1px;
}}

/* ===== TOOLTIP ===== */
QToolTip {{
    background-color: {ThemeColors.BG_CARD};
    color: {ThemeColors.TEXT_PRIMARY};
    border: 1px solid {ThemeColors.ACCENT_BLUE};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}}
"""


def get_log_style():
    """Estilo específico para el log de actividad."""
    return f"""
    QTextEdit {{
        background-color: #0d1117;
        color: #c9d1d9;
        border: 1px solid {ThemeColors.BORDER};
        border-radius: 10px;
        padding: 12px;
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        font-size: 11px;
        line-height: 1.6;
    }}
    """


def get_card_style(accent_color: str = None):
    """Estilo para tarjetas/cards con borde de acento."""
    color = accent_color or ThemeColors.ACCENT_BLUE
    return f"""
    QGroupBox {{
        background-color: {ThemeColors.BG_CARD};
        border: 1px solid {ThemeColors.BORDER};
        border-left: 3px solid {color};
        border-radius: 10px;
        padding: 16px;
        padding-top: 20px;
    }}
    """


def get_status_badge(status: str = "info"):
    """Estilo para badges de estado."""
    colors = {
        "success": (ThemeColors.SUCCESS, "#001a0f"),
        "warning": (ThemeColors.WARNING, "#1a1200"),
        "error": (ThemeColors.ERROR, "#1a0000"),
        "info": (ThemeColors.INFO, "#000a1a"),
    }
    text_color, bg_color = colors.get(status, colors["info"])
    return f"""
    QLabel {{
        background-color: {bg_color};
        color: {text_color};
        border: 1px solid {text_color};
        border-radius: 12px;
        padding: 4px 12px;
        font-weight: 600;
        font-size: 11px;
    }}
    """
