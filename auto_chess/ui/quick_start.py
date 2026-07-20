"""
Asistente de Inicio Rápido (Quick Start Wizard).
Guía al usuario paso a paso para configurar y usar la herramienta.
"""
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QStackedWidget, QFrame,
                               QRadioButton, QButtonGroup, QCheckBox,
                               QWidget, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

from auto_chess.ui.themes.dark_theme import ThemeColors, get_card_style

logger = logging.getLogger(__name__)


class QuickStartWizard(QDialog):
    """
    Wizard de inicio rápido que guía al usuario en 4 pasos:
    1. Bienvenida
    2. Calibración del tablero
    3. Selección de modo
    4. Consejos de seguridad
    """

    wizard_completed = pyqtSignal(dict)  # Emite configuración elegida

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bienvenido a AutoChess ♟")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        self._result = {
            'calibrate_now': False,
            'preferred_mode': 'suggest',
            'stealth_enabled': True,
            'elo': 1500,
        }

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Header (siempre visible)
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ThemeColors.ACCENT_BLUE},
                    stop:1 {ThemeColors.ACCENT_PURPLE});
            }}
        """)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("♟ AutoChess Assistant")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(title)

        subtitle = QLabel("Tu asistente de accesibilidad para ajedrez")
        subtitle.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent; font-size: 13px;")
        header_layout.addWidget(subtitle)

        header.setLayout(header_layout)
        layout.addWidget(header)

        # Steps indicator
        self.steps_widget = QWidget()
        self.steps_widget.setFixedHeight(50)
        self.steps_widget.setStyleSheet(f"background-color: {ThemeColors.BG_SECONDARY};")
        steps_layout = QHBoxLayout()
        steps_layout.setContentsMargins(24, 8, 24, 8)

        self.step_labels = []
        step_names = ["Bienvenida", "Tablero", "Modo", "Seguridad"]
        for i, name in enumerate(step_names):
            lbl = QLabel(f"  {'●' if i == 0 else '○'} {name}  ")
            lbl.setStyleSheet(f"""
                color: {'white' if i == 0 else ThemeColors.TEXT_MUTED};
                background: {'#3366ff' if i == 0 else 'transparent'};
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: {'bold' if i == 0 else 'normal'};
            """)
            steps_layout.addWidget(lbl)
            self.step_labels.append(lbl)
            if i < len(step_names) - 1:
                line = QFrame()
                line.setStyleSheet(f"background-color: {ThemeColors.BORDER}; max-height: 1px;")
                steps_layout.addWidget(line)

        self.steps_widget.setLayout(steps_layout)
        layout.addWidget(self.steps_widget)

        # Content (stacked pages)
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {ThemeColors.BG_PRIMARY};")

        # Page 1: Bienvenida
        self.stack.addWidget(self._create_welcome_page())
        # Page 2: Tablero
        self.stack.addWidget(self._create_board_page())
        # Page 3: Modo
        self.stack.addWidget(self._create_mode_page())
        # Page 4: Seguridad
        self.stack.addWidget(self._create_security_page())

        layout.addWidget(self.stack, stretch=1)

        # Footer (botones de navegación)
        footer = QWidget()
        footer.setFixedHeight(60)
        footer.setStyleSheet(f"background-color: {ThemeColors.BG_SECONDARY}; border-top: 1px solid {ThemeColors.BORDER};")
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(24, 10, 24, 10)

        self.btn_back = QPushButton("← Anterior")
        self.btn_back.setEnabled(False)
        self.btn_back.clicked.connect(self._go_back)
        footer_layout.addWidget(self.btn_back)

        footer_layout.addStretch()

        self.btn_next = QPushButton("Siguiente →")
        self.btn_next.setObjectName("btn_primary")
        self.btn_next.clicked.connect(self._go_next)
        footer_layout.addWidget(self.btn_next)

        self.btn_finish = QPushButton("✓ Comenzar")
        self.btn_finish.setObjectName("btn_primary")
        self.btn_finish.setVisible(False)
        self.btn_finish.clicked.connect(self._finish)
        footer_layout.addWidget(self.btn_finish)

        self.btn_skip = QPushButton("Omitir wizard")
        self.btn_skip.setStyleSheet(f"color: {ThemeColors.TEXT_MUTED}; border: none;")
        self.btn_skip.clicked.connect(self.reject)
        footer_layout.addWidget(self.btn_skip)

        footer.setLayout(footer_layout)
        layout.addWidget(footer)

    def _create_welcome_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 30, 40, 30)

        # Icono grande
        icon_label = QLabel("♟")
        icon_label.setFont(QFont("Segoe UI", 64))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"color: {ThemeColors.ACCENT_BLUE}; background: transparent;")
        layout.addWidget(icon_label)

        title = QLabel("¡Bienvenido!")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(
            "Esta herramienta te ayudará a jugar ajedrez en chess.com\n"
            "contra bots, con tres modos diferentes para adaptarse\n"
            "a tus necesidades de accesibilidad."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY}; font-size: 14px; line-height: 1.6;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(20)

        # Features
        features = [
            ("🤖", "Modo Auto", "El motor juega solo. Descansa tu mano."),
            ("⌨️", "Modo Teclado", "Escribe jugadas. Mínimo uso del mouse."),
            ("💡", "Modo Sugerencia", "Flechas clickeables. Tú decides cuándo mover."),
        ]

        for icon, title_text, desc_text in features:
            row = QHBoxLayout()
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Segoe UI", 22))
            icon_lbl.setFixedWidth(40)
            icon_lbl.setAlignment(Qt.AlignCenter)
            row.addWidget(icon_lbl)

            text_widget = QVBoxLayout()
            t = QLabel(f"<b>{title_text}</b>")
            t.setStyleSheet(f"color: {ThemeColors.TEXT_PRIMARY}; font-size: 13px;")
            d = QLabel(desc_text)
            d.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY}; font-size: 12px;")
            text_widget.addWidget(t)
            text_widget.addWidget(d)
            row.addLayout(text_widget, stretch=1)

            container = QWidget()
            container.setLayout(row)
            container.setStyleSheet(f"""
                QWidget {{
                    background-color: {ThemeColors.BG_CARD};
                    border: 1px solid {ThemeColors.BORDER};
                    border-radius: 10px;
                    padding: 8px;
                    margin: 2px;
                }}
            """)
            layout.addWidget(container)

        layout.addStretch()
        page.setLayout(layout)
        return page

    def _create_board_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("📐 Paso 1: Calibrar el Tablero")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        desc = QLabel(
            "Para que la herramienta funcione, necesita saber dónde está\n"
            "el tablero en tu pantalla. Esto se hace una sola vez."
        )
        desc.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY}; font-size: 13px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(16)

        steps = [
            "1. Abre chess.com y entra a una partida contra un bot",
            "2. Asegúrate de que el tablero sea completamente visible",
            "3. Al finalizar este wizard, haz click en 'Calibrar Tablero'",
            "4. Haz click en las esquinas superior-izquierda e inferior-derecha del tablero",
        ]

        for step_text in steps:
            step_lbl = QLabel(f"  {step_text}")
            step_lbl.setStyleSheet(f"""
                color: {ThemeColors.TEXT_PRIMARY};
                font-size: 13px;
                padding: 8px;
                background-color: {ThemeColors.BG_CARD};
                border-radius: 6px;
                margin: 2px;
            """)
            step_lbl.setWordWrap(True)
            layout.addWidget(step_lbl)

        layout.addSpacing(16)

        self.check_calibrate_now = QCheckBox("Quiero calibrar ahora al finalizar")
        self.check_calibrate_now.setChecked(True)
        self.check_calibrate_now.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.check_calibrate_now)

        layout.addStretch()
        page.setLayout(layout)
        return page

    def _create_mode_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("🎮 Paso 2: Elige tu Modo")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        desc = QLabel("Selecciona el modo que prefieras para empezar:")
        desc.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY};")
        layout.addWidget(desc)

        layout.addSpacing(16)

        self.mode_group = QButtonGroup()

        modes = [
            ('auto', '🤖 Modo Auto', 
             'El motor juega automáticamente.\nIdeal para descanso total de la mano.\nSelecciona ELO y color, y relájate.',
             ThemeColors.ACCENT_GREEN),
            ('keyboard', '⌨️ Modo Teclado',
             'Escribe tus jugadas (ej: e2e4, Nf3).\nMínimo uso del mouse.\nIdeal con teclado ergonómico.',
             ThemeColors.ACCENT_BLUE),
            ('suggest', '💡 Modo Sugerencia',
             'Flechas aparecen sobre el tablero.\nTú eliges cuál ejecutar con un click.\nMáximo control sobre la partida.',
             ThemeColors.ACCENT_ORANGE),
        ]

        for mode_id, mode_title, mode_desc, color in modes:
            card = QWidget()
            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(16, 12, 16, 12)

            radio = QRadioButton(mode_title)
            radio.setStyleSheet(f"""
                QRadioButton {{ font-size: 14px; font-weight: bold; color: {ThemeColors.TEXT_PRIMARY}; }}
                QRadioButton::indicator {{ width: 22px; height: 22px; }}
            """)
            if mode_id == 'suggest':
                radio.setChecked(True)
            self.mode_group.addButton(radio)
            card_layout.addWidget(radio)

            desc_lbl = QLabel(mode_desc)
            desc_lbl.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY}; font-size: 12px; margin-left: 32px;")
            desc_lbl.setWordWrap(True)
            card_layout.addWidget(desc_lbl)

            card.setLayout(card_layout)
            card.setStyleSheet(f"""
                QWidget {{
                    background-color: {ThemeColors.BG_CARD};
                    border: 2px solid {ThemeColors.BORDER};
                    border-left: 4px solid {color};
                    border-radius: 10px;
                    margin: 4px;
                }}
                QWidget:hover {{
                    border-color: {color};
                }}
            """)
            layout.addWidget(card)

            # Conectar radio al resultado
            radio.toggled.connect(lambda checked, mid=mode_id: self._on_mode_selected(mid, checked))

        layout.addStretch()
        page.setLayout(layout)
        return page

    def _create_security_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("🛡️ Paso 3: Seguridad")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title)

        desc = QLabel(
            "La herramienta incluye medidas de seguridad para proteger tu cuenta.\n"
            "Estas opciones están activadas por defecto."
        )
        desc.setStyleSheet(f"color: {ThemeColors.TEXT_SECONDARY};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(16)

        self.check_stealth = QCheckBox("🛡️ Activar comportamiento humanizado (RECOMENDADO)")
        self.check_stealth.setChecked(True)
        self.check_stealth.setStyleSheet("font-size: 13px; font-weight: bold; padding: 8px;")
        layout.addWidget(self.check_stealth)

        security_features = [
            "✅ Delays de pensamiento aleatorios (no instantáneo)",
            "✅ Clicks con desviación natural (no siempre al centro)",
            "✅ Movimientos de mouse con curvas (no líneas rectas)",
            "✅ Pausas de distracción ocasionales",
            "✅ Rotación de patrones de comportamiento",
            "✅ Tiempo de reacción mínimo configurable",
        ]

        for feature in security_features:
            lbl = QLabel(f"  {feature}")
            lbl.setStyleSheet(f"""
                color: {ThemeColors.SUCCESS};
                font-size: 12px;
                padding: 4px 8px;
            """)
            layout.addWidget(lbl)

        layout.addSpacing(16)

        # Consejo importante
        tip = QLabel(
            "💡 Consejo: Juega solo contra bots, no más de 8-10 partidas\n"
            "seguidas, y haz pausas reales entre sesiones."
        )
        tip.setStyleSheet(f"""
            background-color: #1a1a00;
            color: {ThemeColors.ACCENT_ORANGE};
            border: 1px solid {ThemeColors.ACCENT_ORANGE};
            border-radius: 8px;
            padding: 12px;
            font-size: 12px;
        """)
        tip.setWordWrap(True)
        layout.addWidget(tip)

        layout.addStretch()
        page.setLayout(layout)
        return page

    def _on_mode_selected(self, mode_id: str, checked: bool):
        if checked:
            self._result['preferred_mode'] = mode_id

    def _update_steps(self):
        current = self.stack.currentIndex()
        for i, lbl in enumerate(self.step_labels):
            if i == current:
                lbl.setText(f"  ● {['Bienvenida', 'Tablero', 'Modo', 'Seguridad'][i]}  ")
                lbl.setStyleSheet(f"""
                    color: white;
                    background: {ThemeColors.ACCENT_BLUE};
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-size: 12px;
                    font-weight: bold;
                """)
            elif i < current:
                lbl.setText(f"  ✓ {['Bienvenida', 'Tablero', 'Modo', 'Seguridad'][i]}  ")
                lbl.setStyleSheet(f"""
                    color: {ThemeColors.SUCCESS};
                    background: transparent;
                    font-size: 12px;
                """)
            else:
                lbl.setText(f"  ○ {['Bienvenida', 'Tablero', 'Modo', 'Seguridad'][i]}  ")
                lbl.setStyleSheet(f"""
                    color: {ThemeColors.TEXT_MUTED};
                    background: transparent;
                    font-size: 12px;
                """)

        self.btn_back.setEnabled(current > 0)
        is_last = current == 3
        self.btn_next.setVisible(not is_last)
        self.btn_finish.setVisible(is_last)

    def _go_next(self):
        self._save_current_step()
        self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
        self._update_steps()

    def _go_back(self):
        self.stack.setCurrentIndex(self.stack.currentIndex() - 1)
        self._update_steps()

    def _save_current_step(self):
        current = self.stack.currentIndex()
        if current == 1:
            self._result['calibrate_now'] = self.check_calibrate_now.isChecked()
        elif current == 3:
            self._result['stealth_enabled'] = self.check_stealth.isChecked()

    def _finish(self):
        self._save_current_step()
        self.wizard_completed.emit(self._result)
        self.accept()

    def get_result(self) -> dict:
        return self._result
