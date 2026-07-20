"""
Tema profesional moderno para AutoChess.
Diseño inspirado en aplicaciones profesionales como VS Code, Discord, Slack.
"""


class ProfessionalColors:
    """Paleta de colores profesional."""
    # Fondos
    BG_DARK = "#0d1117"           # GitHub dark
    BG_MEDIUM = "#161b22"         # Cards
    BG_LIGHT = "#21262d"          # Hover states
    BG_INPUT = "#0d1117"          # Inputs
    
    # Acentos
    PRIMARY = "#58a6ff"           # Blue accent
    SECONDARY = "#8b949e"         # Gray accent
    SUCCESS = "#3fb950"           # Green
    WARNING = "#d29922"           # Yellow
    DANGER = "#f85149"            # Red
    INFO = "#58a6ff"              # Blue
    
    # Texto
    TEXT_PRIMARY = "#f0f6fc"      # Main text
    TEXT_SECONDARY = "#8b949e"    # Secondary text
    TEXT_MUTED = "#6e7681"        # Muted text
    TEXT_ON_PRIMARY = "#ffffff"   # Text on primary
    
    # Bordes
    BORDER = "#30363d"
    BORDER_FOCUS = "#58a6ff"
    
    # Sombras
    SHADOW = "rgba(0, 0, 0, 0.5)"


PROFESSIONAL_STYLE = f"""
/* ===== GLOBAL ===== */
* {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', sans-serif;
}}

QWidget {{
    background-color: {ProfessionalColors.BG_DARK};
    color: {ProfessionalColors.TEXT_PRIMARY};
    font-size: 13px;
}}

QMainWindow {{
    background-color: {ProfessionalColors.BG_DARK};
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background-color: {ProfessionalColors.BG_MEDIUM};
    color: {ProfessionalColors.TEXT_PRIMARY};
    border: 1px solid {ProfessionalColors.BORDER};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 13px;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: {ProfessionalColors.BG_LIGHT};
    border-color: {ProfessionalColors.PRIMARY};
}}

QPushButton:pressed {{
    background-color: {ProfessionalColors.BG_DARK};
}}

QPushButton:disabled {{
    color: {ProfessionalColors.TEXT_MUTED};
    background-color: {ProfessionalColors.BG_DARK};
    border-color: {ProfessionalColors.BORDER};
}}

/* Primary button */
QPushButton[objectName="btn_primary"] {{
    background-color: {ProfessionalColors.PRIMARY};
    color: {ProfessionalColors.TEXT_ON_PRIMARY};
    border: none;
    font-weight: 600;
}}

QPushButton[objectName="btn_primary"]:hover {{
    background-color: #79b8ff;
}}

QPushButton[objectName="btn_primary"]:pressed {{
    background-color: #4a90e2;
}}

/* Danger button */
QPushButton[objectName="btn_danger"] {{
    background-color: {ProfessionalColors.DANGER};
    color: {ProfessionalColors.TEXT_ON_PRIMARY};
    border: none;
    font-weight: 600;
}}

QPushButton[objectName="btn_danger"]:hover {{
    background-color: #ff6b6b;
}}

/* ===== GROUP BOX ===== */
QGroupBox {{
    background-color: {ProfessionalColors.BG_MEDIUM};
    border: 1px solid {ProfessionalColors.BORDER};
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px;
    padding-top: 24px;
    font-weight: 600;
    font-size: 12px;
    color: {ProfessionalColors.TEXT_SECONDARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 8px;
    padding: 0 8px;
    background-color: {ProfessionalColors.BG_MEDIUM};
    color: {ProfessionalColors.PRIMARY};
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ===== TABS ===== */
QTabWidget::pane {{
    border: 1px solid {ProfessionalColors.BORDER};
    border-radius: 8px;
    background-color: {ProfessionalColors.BG_MEDIUM};
    padding: 12px;
}}

QTabBar::tab {{
    background-color: {ProfessionalColors.BG_DARK};
    color: {ProfessionalColors.TEXT_SECONDARY};
    border: 1px solid {ProfessionalColors.BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 10px 16px;
    margin-right: 2px;
    font-weight: 500;
    min-width: 80px;
}}

QTabBar::tab:selected {{
    background-color: {ProfessionalColors.BG_MEDIUM};
    color: {ProfessionalColors.TEXT_PRIMARY};
    border-bottom: 2px solid {ProfessionalColors.PRIMARY};
}}

QTabBar::tab:hover:!selected {{
    background-color: {ProfessionalColors.BG_LIGHT};
    color: {ProfessionalColors.TEXT_PRIMARY};
}}

/* ===== INPUTS ===== */
QLineEdit {{
    background-color: {ProfessionalColors.BG_INPUT};
    color: {ProfessionalColors.TEXT_PRIMARY};
    border: 1px solid {ProfessionalColors.BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: {ProfessionalColors.PRIMARY};
}}

QLineEdit:focus {{
    border-color: {ProfessionalColors.PRIMARY};
    background-color: {ProfessionalColors.BG_MEDIUM};
}}

QLineEdit::placeholder {{
    color: {ProfessionalColors.TEXT_MUTED};
}}

QSpinBox {{
    background-color: {ProfessionalColors.BG_INPUT};
    color: {ProfessionalColors.TEXT_PRIMARY};
    border: 1px solid {ProfessionalColors.BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    min-width: 60px;
}}

QSpinBox:focus {{
    border-color: {ProfessionalColors.PRIMARY};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {ProfessionalColors.BG_MEDIUM};
    border: none;
    width: 16px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {ProfessionalColors.BG_LIGHT};
}}

/* ===== SLIDER ===== */
QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background-color: {ProfessionalColors.BG_LIGHT};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background-color: {ProfessionalColors.PRIMARY};
    border: 2px solid {ProfessionalColors.BG_DARK};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 10px;
}}

QSlider::handle:horizontal:hover {{
    background-color: #79b8ff;
    border-color: {ProfessionalColors.PRIMARY};
}}

QSlider::sub-page:horizontal {{
    background-color: {ProfessionalColors.PRIMARY};
    border-radius: 2px;
}}

/* ===== CHECKBOX ===== */
QCheckBox {{
    color: {ProfessionalColors.TEXT_PRIMARY};
    spacing: 8px;
    font-size: 13px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid {ProfessionalColors.BORDER};
    background-color: {ProfessionalColors.BG_INPUT};
}}

QCheckBox::indicator:checked {{
    background-color: {ProfessionalColors.PRIMARY};
    border-color: {ProfessionalColors.PRIMARY};
}}

QCheckBox::indicator:hover {{
    border-color: {ProfessionalColors.PRIMARY};
}}

/* ===== RADIO BUTTON ===== */
QRadioButton {{
    color: {ProfessionalColors.TEXT_PRIMARY};
    spacing: 8px;
    font-size: 13px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 10px;
    border: 2px solid {ProfessionalColors.BORDER};
    background-color: {ProfessionalColors.BG_INPUT};
}}

QRadioButton::indicator:checked {{
    background-color: {ProfessionalColors.PRIMARY};
    border-color: {ProfessionalColors.PRIMARY};
}}

/* ===== TEXT EDIT ===== */
QTextEdit {{
    background-color: {ProfessionalColors.BG_INPUT};
    color: {ProfessionalColors.TEXT_PRIMARY};
    border: 1px solid {ProfessionalColors.BORDER};
    border-radius: 6px;
    padding: 8px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 12px;
    selection-background-color: {ProfessionalColors.PRIMARY};
}}

/* ===== LABELS ===== */
QLabel {{
    color: {ProfessionalColors.TEXT_PRIMARY};
    background-color: transparent;
}}

/* ===== STATUS BAR ===== */
QStatusBar {{
    background-color: {ProfessionalColors.BG_MEDIUM};
    color: {ProfessionalColors.TEXT_SECONDARY};
    border-top: 1px solid {ProfessionalColors.BORDER};
    padding: 4px 12px;
    font-size: 12px;
}}

/* ===== MENU BAR ===== */
QMenuBar {{
    background-color: {ProfessionalColors.BG_MEDIUM};
    color: {ProfessionalColors.TEXT_PRIMARY};
    border-bottom: 1px solid {ProfessionalColors.BORDER};
    padding: 2px;
}}

QMenuBar::item {{
    padding: 6px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {ProfessionalColors.BG_LIGHT};
}}

QMenu {{
    background-color: {ProfessionalColors.BG_MEDIUM};
    color: {ProfessionalColors.TEXT_PRIMARY};
    border: 1px solid {ProfessionalColors.BORDER};
    border-radius: 6px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 32px;
    border-radius: 4px;
}}

QMenu::item:selected {{
    background-color: {ProfessionalColors.PRIMARY};
    color: {ProfessionalColors.TEXT_ON_PRIMARY};
}}

QMenu::separator {{
    height: 1px;
    background-color: {ProfessionalColors.BORDER};
    margin: 4px 8px;
}}

/* ===== SCROLLBAR ===== */
QScrollBar:vertical {{
    background-color: {ProfessionalColors.BG_DARK};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {ProfessionalColors.BORDER};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {ProfessionalColors.SECONDARY};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {ProfessionalColors.BG_DARK};
    height: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {ProfessionalColors.BORDER};
    border-radius: 5px;
    min-width: 30px;
}}

/* ===== TOOLTIP ===== */
QToolTip {{
    background-color: {ProfessionalColors.BG_MEDIUM};
    color: {ProfessionalColors.TEXT_PRIMARY};
    border: 1px solid {ProfessionalColors.BORDER};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}}
"""


def get_professional_style():
    """Retorna el estilo profesional completo."""
    return PROFESSIONAL_STYLE
