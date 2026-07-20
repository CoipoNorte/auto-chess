"""
Diálogo de calibración del tablero - Versión simplificada y robusta.
Permite al usuario ingresar las coordenadas manualmente o usar un método visual simple.
"""
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QSpinBox, QGroupBox, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal

from auto_chess.config import BoardConfig

logger = logging.getLogger(__name__)


class CalibrationDialog(QDialog):
    """
    Diálogo para calibrar la posición del tablero en pantalla.
    Versión simplificada que usa entrada manual de coordenadas.
    """

    calibration_done = pyqtSignal(object)  # Emite BoardConfig

    def __init__(self, parent=None, current_config: BoardConfig = None):
        super().__init__(parent)
        self.setWindowTitle("Calibración del Tablero")
        self.setMinimumWidth(500)
        self.setModal(True)

        self.config = current_config or BoardConfig()
        self._setup_ui()
        self._load_current_config()

    def _setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout()

        # Instrucciones
        info_label = QLabel(
            "<h3>Calibración del Tablero</h3>"
            "<p>Ingresa las coordenadas de las esquinas del tablero de ajedrez en tu pantalla.</p>"
            "<p><b>¿Cómo obtener las coordenadas?</b></p>"
            "<ol>"
            "<li>Abre chess.com y entra a una partida contra un bot</li>"
            "<li>Mueve el cursor a la esquina superior-izquierda del tablero (casilla a8)</li>"
            "<li>Usa una herramienta como <b>PowerToys</b> o captura pantalla para ver las coordenadas</li>"
            "<li>Repite para la esquina inferior-derecha (casilla h1)</li>"
            "</ol>"
            "<p><b>Alternativa rápida:</b> Si ya sabes el tamaño del tablero, simplemente ingresa "
            "la posición de la esquina superior-izquierda y el tamaño de cada casilla.</p>"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px;")
        layout.addWidget(info_label)

        # Método 1: Coordenadas manuales
        manual_group = QGroupBox("Método 1: Coordenadas Manuales")
        manual_layout = QVBoxLayout()

        # Esquina superior-izquierda
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Esquina superior-izquierda (a8):"))
        row1.addWidget(QLabel("X:"))
        self.spin_x1 = QSpinBox()
        self.spin_x1.setRange(0, 9999)
        self.spin_x1.setValue(100)
        self.spin_x1.setFixedWidth(80)
        row1.addWidget(self.spin_x1)
        row1.addWidget(QLabel("Y:"))
        self.spin_y1 = QSpinBox()
        self.spin_y1.setRange(0, 9999)
        self.spin_y1.setValue(100)
        self.spin_y1.setFixedWidth(80)
        row1.addWidget(self.spin_y1)
        row1.addStretch()
        manual_layout.addLayout(row1)

        # Esquina inferior-derecha
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Esquina inferior-derecha (h1):"))
        row2.addWidget(QLabel("X:"))
        self.spin_x2 = QSpinBox()
        self.spin_x2.setRange(0, 9999)
        self.spin_x2.setValue(600)
        self.spin_x2.setFixedWidth(80)
        row2.addWidget(self.spin_x2)
        row2.addWidget(QLabel("Y:"))
        self.spin_y2 = QSpinBox()
        self.spin_y2.setRange(0, 9999)
        self.spin_y2.setValue(600)
        self.spin_y2.setFixedWidth(80)
        row2.addWidget(self.spin_y2)
        row2.addStretch()
        manual_layout.addLayout(row2)

        # Checkbox orientación
        self.check_white_bottom = QCheckBox("Blancas abajo (vista normal)")
        self.check_white_bottom.setChecked(True)
        manual_layout.addWidget(self.check_white_bottom)

        # Preview
        self.label_calc = QLabel("Tamaño del tablero: 500x500 px | Tamaño de casilla: ~62 px")
        self.label_calc.setStyleSheet("font-weight: bold; color: blue; padding: 10px;")
        manual_layout.addWidget(self.label_calc)

        # Conectar cambios para actualizar preview
        self.spin_x1.valueChanged.connect(self._update_calc_label)
        self.spin_y1.valueChanged.connect(self._update_calc_label)
        self.spin_x2.valueChanged.connect(self._update_calc_label)
        self.spin_y2.valueChanged.connect(self._update_calc_label)

        btn_apply = QPushButton("Aplicar Coordenadas")
        btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        btn_apply.clicked.connect(self._apply_manual)
        manual_layout.addWidget(btn_apply)

        manual_group.setLayout(manual_layout)
        layout.addWidget(manual_group)

        # Método 2: Tamaño de casilla
        size_group = QGroupBox("Método 2: Posición + Tamaño de Casilla")
        size_layout = QVBoxLayout()

        size_info = QLabel(
            "<i>Si conoces el tamaño de cada casilla en píxeles, "
            "solo necesitas la esquina superior-izquierda.</i>"
        )
        size_info.setWordWrap(True)
        size_layout.addWidget(size_info)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Esquina superior-izquierda:"))
        row3.addWidget(QLabel("X:"))
        self.spin_pos_x = QSpinBox()
        self.spin_pos_x.setRange(0, 9999)
        self.spin_pos_x.setValue(100)
        self.spin_pos_x.setFixedWidth(80)
        row3.addWidget(self.spin_pos_x)
        row3.addWidget(QLabel("Y:"))
        self.spin_pos_y = QSpinBox()
        self.spin_pos_y.setRange(0, 9999)
        self.spin_pos_y.setValue(100)
        self.spin_pos_y.setFixedWidth(80)
        row3.addWidget(self.spin_pos_y)
        row3.addStretch()
        size_layout.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Tamaño de cada casilla:"))
        self.spin_square_size = QSpinBox()
        self.spin_square_size.setRange(30, 200)
        self.spin_square_size.setValue(75)
        self.spin_square_size.setSuffix(" px")
        self.spin_square_size.setFixedWidth(100)
        row4.addWidget(self.spin_square_size)
        row4.addStretch()
        size_layout.addLayout(row4)

        btn_apply_size = QPushButton("Aplicar Tamaño de Casilla")
        btn_apply_size.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_apply_size.clicked.connect(self._apply_size_method)
        size_layout.addWidget(btn_apply_size)

        size_group.setLayout(size_layout)
        layout.addWidget(size_group)

        # Botones finales
        btn_layout = QHBoxLayout()

        self.btn_save = QPushButton("✓ Guardar Calibración")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_save.clicked.connect(self._save_calibration)
        btn_layout.addWidget(self.btn_save)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Actualizar preview inicial
        self._update_calc_label()

    def _load_current_config(self):
        """Carga la configuración actual en los controles."""
        if self.config.is_calibrated:
            self.spin_x1.setValue(self.config.top_left[0])
            self.spin_y1.setValue(self.config.top_left[1])
            self.spin_x2.setValue(self.config.bottom_right[0])
            self.spin_y2.setValue(self.config.bottom_right[1])
            self.check_white_bottom.setChecked(self.config.white_at_bottom)

            # Método 2
            self.spin_pos_x.setValue(self.config.top_left[0])
            self.spin_pos_y.setValue(self.config.top_left[1])
            self.spin_square_size.setValue(self.config.square_size)

    def _update_calc_label(self):
        """Actualiza la etiqueta de información calculada."""
        x1, y1 = self.spin_x1.value(), self.spin_y1.value()
        x2, y2 = self.spin_x2.value(), self.spin_y2.value()
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        sq_size = min(width, height) // 8

        self.label_calc.setText(
            f"Tamaño del tablero: {width}x{height} px | "
            f"Tamaño de casilla: ~{sq_size} px"
        )

        if sq_size < 30:
            self.label_calc.setStyleSheet("font-weight: bold; color: red; padding: 10px;")
        elif sq_size > 150:
            self.label_calc.setStyleSheet("font-weight: bold; color: orange; padding: 10px;")
        else:
            self.label_calc.setStyleSheet("font-weight: bold; color: green; padding: 10px;")

    def _apply_manual(self):
        """Aplica los valores del método manual."""
        try:
            x1 = min(self.spin_x1.value(), self.spin_x2.value())
            y1 = min(self.spin_y1.value(), self.spin_y2.value())
            x2 = max(self.spin_x1.value(), self.spin_x2.value())
            y2 = max(self.spin_y1.value(), self.spin_y2.value())

            self.config.top_left = (x1, y1)
            self.config.bottom_right = (x2, y2)
            self.config.white_at_bottom = self.check_white_bottom.isChecked()
            self.config.calculate()

            logger.info(f"Calibración manual aplicada: {self.config.top_left} -> {self.config.bottom_right}")
            QMessageBox.information(
                self, "Éxito",
                f"Calibración aplicada correctamente.\n"
                f"Tablero: {x1},{y1} a {x2},{y2}\n"
                f"Tamaño de casilla: {self.config.square_size}px"
            )
        except Exception as e:
            logger.error(f"Error al aplicar calibración manual: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo aplicar la calibración:\n{e}")

    def _apply_size_method(self):
        """Aplica los valores del método de tamaño de casilla."""
        try:
            pos_x = self.spin_pos_x.value()
            pos_y = self.spin_pos_y.value()
            square_size = self.spin_square_size.value()

            self.config.top_left = (pos_x, pos_y)
            self.config.bottom_right = (pos_x + square_size * 8, pos_y + square_size * 8)
            self.config.white_at_bottom = True
            self.config.square_size = square_size
            self.config.click_offset = square_size // 2

            # Actualizar método 1 para que coincida
            self.spin_x1.setValue(pos_x)
            self.spin_y1.setValue(pos_y)
            self.spin_x2.setValue(pos_x + square_size * 8)
            self.spin_y2.setValue(pos_y + square_size * 8)

            logger.info(f"Método tamaño aplicado: posición={pos_x},{pos_y}, tamaño={square_size}px")
            QMessageBox.information(
                self, "Éxito",
                f"Calibración aplicada correctamente.\n"
                f"Esquina superior-izquierda: {pos_x},{pos_y}\n"
                f"Tamaño de casilla: {square_size}px"
            )
        except Exception as e:
            logger.error(f"Error al aplicar método de tamaño: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo aplicar la calibración:\n{e}")

    def _save_calibration(self):
        """Guarda la calibración."""
        try:
            if not self.config.is_calibrated:
                QMessageBox.warning(
                    self, "Advertencia",
                    "Primero debes aplicar la calibración usando uno de los métodos."
                )
                return

            if self.config.square_size < 30:
                QMessageBox.warning(
                    self, "Advertencia",
                    f"El tamaño de casilla ({self.config.square_size}px) es muy pequeño.\n"
                    "Verifica que las coordenadas sean correctas."
                )
                return

            if self.config.square_size > 150:
                QMessageBox.warning(
                    self, "Advertencia",
                    f"El tamaño de casilla ({self.config.square_size}px) es muy grande.\n"
                    "Verifica que las coordenadas sean correctas."
                )
                return

            self.calibration_done.emit(self.config)
            logger.info(
                f"Calibración guardada: topLeft={self.config.top_left}, "
                f"bottomRight={self.config.bottom_right}, "
                f"squareSize={self.config.square_size}"
            )
            self.accept()
        except Exception as e:
            logger.error(f"Error al guardar calibración: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo guardar la calibración:\n{e}")

    def get_config(self) -> BoardConfig:
        """Retorna la configuración calibrada."""
        return self.config
