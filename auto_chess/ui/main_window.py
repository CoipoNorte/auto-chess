"""
Ventana principal de AutoChess - Rediseñada con tema moderno.
"""
import sys
import logging
import random
import chess
from typing import Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QSlider, QSpinBox,
                               QGroupBox, QTextEdit, QTabWidget, QLineEdit,
                               QCheckBox, QRadioButton, QButtonGroup,
                               QMessageBox, QStatusBar, QMenuBar, QAction,
                               QFrame, QComboBox, QApplication, QSizePolicy,
                               QProgressBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QIcon, QColor, QTextCursor

from auto_chess.config import AppConfig, BoardConfig, SecurityConfig
from auto_chess.engine.chess_engine import ChessEngine, MoveAnalysis
from auto_chess.capture.board_reader import BoardReader
from auto_chess.controller.chess_com import ChessComController
from auto_chess.modes.auto_mode import AutoMode
from auto_chess.modes.keyboard_mode import KeyboardMode
from auto_chess.modes.suggest_mode import SuggestMode
from auto_chess.ui.overlay import ChessOverlay
from auto_chess.ui.calibration_dialog import CalibrationDialog
from auto_chess.ui.themes.professional_theme import get_professional_style, ProfessionalColors
from auto_chess.stealth.security import SecurityManager

logger = logging.getLogger(__name__)


class WorkerThread(QThread):
    status_update = pyqtSignal(str)
    move_made = pyqtSignal(str)
    game_ended = pyqtSignal(str)

    def __init__(self, target, *args, **kwargs):
        super().__init__()
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._target(*self._args, **self._kwargs)


class MainWindow(QMainWindow):
    """Ventana principal con tema moderno oscuro."""

    def __init__(self):
        super().__init__()
        fake_titles = [
            "System Settings", "Display Preferences", "Network Monitor",
            "Audio Configuration", "File Manager", "System Utility",
        ]
        self.config = AppConfig.load()
        title = random.choice(fake_titles) if self.config.security.randomize_window_title else "AutoChess"
        self.setWindowTitle(f"♟ {title}")
        self.setMinimumSize(620, 780)
        self.resize(620, 820)
        self.setStyleSheet(get_professional_style())
        # Cargar icono
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.engine = None
        self.reader = None
        self.controller = None
        self.overlay = None
        self.security = None
        self.auto_mode = None
        self.keyboard_mode = None
        self.suggest_mode = None
        self._auto_thread = None
        self._suggest_timer = None
        self._security_timer = None

        self._setup_ui()
        self._init_components()
        self._start_engine()
        self._start_security_monitor()
        if not self.config.board.is_calibrated:
            QTimer.singleShot(500, self._show_quick_start)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(16, 12, 16, 12)
        central.setLayout(main_layout)

        # HEADER
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #1a1f3a, stop:1 #2a1f3a);
                border-radius: 12px; border: 1px solid {ProfessionalColors.BORDER}; }}""")
        hl = QHBoxLayout()
        hl.setContentsMargins(20, 12, 20, 12)
        icon = QLabel("♟")
        icon.setFont(QFont("Segoe UI", 28))
        icon.setStyleSheet(f"color: {ProfessionalColors.PRIMARY}; background: transparent;")
        hl.addWidget(icon)
        tb = QVBoxLayout()
        tb.setSpacing(2)
        t = QLabel("AutoChess Assistant")
        t.setFont(QFont("Segoe UI", 18, QFont.Bold))
        t.setStyleSheet("color: white; background: transparent;")
        s = QLabel("Herramienta de accesibilidad para ajedrez")
        s.setStyleSheet(f"color: {ProfessionalColors.TEXT_MUTED}; background: transparent; font-size: 11px;")
        tb.addWidget(t); tb.addWidget(s)
        hl.addLayout(tb); hl.addStretch()
        bl = QVBoxLayout()
        self.badge_engine = QLabel("⏳ Engine")
        self.badge_engine.setAlignment(Qt.AlignRight)
        self.badge_engine.setStyleSheet("background-color: #1a1500; color: " + ProfessionalColors.WARNING + "; border: 1px solid " + ProfessionalColors.WARNING + "; border-radius: 12px; padding: 4px 12px; font-weight: 600; font-size: 11px;")
        bl.addWidget(self.badge_engine)
        self.badge_security = QLabel("🛡️ Seguridad ON")
        self.badge_security.setAlignment(Qt.AlignRight)
        self.badge_security.setStyleSheet("background-color: #0d2818; color: " + ProfessionalColors.SUCCESS + "; border: 1px solid " + ProfessionalColors.SUCCESS + "; border-radius: 12px; padding: 4px 12px; font-weight: 600; font-size: 11px;")
        bl.addWidget(self.badge_security)
        hl.addLayout(bl)
        header.setLayout(hl)
        main_layout.addWidget(header)

        # ENGINE CARD
        ec = QGroupBox("MOTOR DE ANÁLISIS")
        ec.setStyleSheet("background-color: " + ProfessionalColors.INFO + "; border: 1px solid " + ProfessionalColors.BORDER + "; border-left: 3px solid " + ProfessionalColors.INFO + "; border-radius: 8px; padding: 12px;")
        el = QVBoxLayout()
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("ELO:"))
        self.slider_elo = QSlider(Qt.Horizontal)
        self.slider_elo.setRange(300, 3000)
        self.slider_elo.setValue(self.config.engine.elo)
        r1.addWidget(self.slider_elo, stretch=1)
        self.spin_elo = QSpinBox()
        self.spin_elo.setRange(300, 3000)
        self.spin_elo.setValue(self.config.engine.elo)
        self.spin_elo.setSingleStep(100)
        self.spin_elo.setFixedWidth(80)
        r1.addWidget(self.spin_elo)
        el.addLayout(r1)
        r2 = QHBoxLayout()
        self.label_elo_desc = QLabel(self._get_elo_description(self.config.engine.elo))
        self.label_elo_desc.setStyleSheet(f"color: {ProfessionalColors.INFO}; font-weight: bold; font-size: 12px;")
        r2.addWidget(self.label_elo_desc)
        r2.addStretch()
        r2.addWidget(QLabel("Análisis:"))
        self.spin_think = QSpinBox()
        self.spin_think.setRange(1, 30)
        self.spin_think.setValue(int(self.config.engine.think_time))
        self.spin_think.setSuffix("s")
        self.spin_think.setFixedWidth(60)
        r2.addWidget(self.spin_think)
        r2.addWidget(QLabel("Sugerencias:"))
        self.spin_suggestions = QSpinBox()
        self.spin_suggestions.setRange(1, 5)
        self.spin_suggestions.setValue(self.config.engine.multi_pv)
        self.spin_suggestions.setFixedWidth(50)
        r2.addWidget(self.spin_suggestions)
        el.addLayout(r2)
        ec.setLayout(el)
        main_layout.addWidget(ec)
        self.slider_elo.valueChanged.connect(self._on_elo_slider_changed)
        self.spin_elo.valueChanged.connect(self._on_elo_spin_changed)

        # TABS
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_auto_tab(), "🤖  Auto")
        self.tabs.addTab(self._create_keyboard_tab(), "⌨️  Teclado")
        self.tabs.addTab(self._create_suggest_tab(), "💡  Sugerencia")
        self.tabs.addTab(self._create_stealth_tab(), "🛡️  Seguridad")
        main_layout.addWidget(self.tabs, stretch=1)

        # QUICK ACTIONS
        qa = QHBoxLayout()
        bc = QPushButton("📐 Calibrar Tablero")
        bc.clicked.connect(self._open_calibration)
        qa.addWidget(bc)
        br = QPushButton("🔄 Leer Tablero")
        br.clicked.connect(self._refresh_board)
        qa.addWidget(br)
        self.label_cal_status = QLabel("✓ Calibrado" if self.config.board.is_calibrated else "⚠ Sin calibrar")
        self.label_cal_status.setStyleSheet("background-color: #0d2818; color: " + ProfessionalColors.SUCCESS + "; border: 1px solid " + ProfessionalColors.SUCCESS + "; border-radius: 12px; padding: 4px 12px; font-weight: 600; font-size: 11px;" if self.config.board.is_calibrated else "background-color: #1a1500; color: " + ProfessionalColors.WARNING + "; border: 1px solid " + ProfessionalColors.WARNING + "; border-radius: 12px; padding: 4px 12px; font-weight: 600; font-size: 11px;")
        qa.addWidget(self.label_cal_status)
        qa.addStretch()
        main_layout.addLayout(qa)

        # LOG
        lc = QGroupBox("REGISTRO DE ACTIVIDAD")
        lc.setStyleSheet("background-color: " + ProfessionalColors.TEXT_MUTED + "; border: 1px solid " + ProfessionalColors.BORDER + "; border-left: 3px solid " + ProfessionalColors.TEXT_MUTED + "; border-radius: 8px; padding: 12px;")
        ll = QVBoxLayout()
        ll.setContentsMargins(4, 4, 4, 4)
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setFixedHeight(120)
        self.text_log.setStyleSheet("background-color: #0d1117; color: #c9d1d9; border: 1px solid " + ProfessionalColors.BORDER + "; border-radius: 8px; padding: 12px; font-family: Consolas, Monaco, monospace; font-size: 11px;")
        ll.addWidget(self.text_log)
        lc.setLayout(ll)
        main_layout.addWidget(lc)

        self.statusBar().showMessage("✓ Listo. Calibra el tablero para comenzar.")
        self._setup_menu()

    def _setup_menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("Archivo")
        for t, s in [("📐 Calibrar Tablero", self._open_calibration), ("🚀 Asistente de Inicio", self._show_quick_start),
                     ("---", None), ("💾 Guardar", self._save_config), ("📂 Recargar", self._reload_config), ("---", None), ("❌ Salir", self.close)]:
            if t == "---": fm.addSeparator()
            else:
                a = QAction(t, self); a.triggered.connect(s); fm.addAction(a)
        hm = mb.addMenu("Ayuda")
        for t, s in [("ℹ️ Acerca de", self._show_about), ("📊 Estadísticas", self._show_stealth_stats)]:
            a = QAction(t, self); a.triggered.connect(s); hm.addAction(a)

    def _create_auto_tab(self):
        w = QWidget(); l = QVBoxLayout(); l.setSpacing(12); l.setContentsMargins(16, 16, 16, 16)
        d = QLabel("El motor juega automáticamente contra el bot."); d.setWordWrap(True)
        d.setStyleSheet(f"color: {ProfessionalColors.TEXT_SECONDARY}; font-size: 12px;"); l.addWidget(d)
        cc = QWidget(); cc.setStyleSheet("background-color: " + ProfessionalColors.PRIMARY + "; border: 1px solid " + ProfessionalColors.BORDER + "; border-left: 3px solid " + ProfessionalColors.PRIMARY + "; border-radius: 8px; padding: 12px;"); cl = QHBoxLayout()
        cl.addWidget(QLabel("Color:")); self.radio_white = QRadioButton("♔ Blancas"); self.radio_white.setChecked(True)
        self.radio_black = QRadioButton("♚ Negras"); cl.addWidget(self.radio_white); cl.addWidget(self.radio_black); cl.addStretch()
        cc.setLayout(cl); l.addWidget(cc)
        bl = QHBoxLayout()
        self.btn_auto_start = QPushButton("▶  INICIAR"); self.btn_auto_start.setObjectName("btn_primary"); self.btn_auto_start.clicked.connect(self._start_auto)
        bl.addWidget(self.btn_auto_start)
        self.btn_auto_stop = QPushButton("⏹  DETENER"); self.btn_auto_stop.setObjectName("btn_danger"); self.btn_auto_stop.setEnabled(False); self.btn_auto_stop.clicked.connect(self._stop_auto)
        bl.addWidget(self.btn_auto_stop)
        self.btn_auto_pause = QPushButton("⏸"); self.btn_auto_pause.setFixedWidth(50); self.btn_auto_pause.setEnabled(False); self.btn_auto_pause.clicked.connect(self._pause_auto)
        bl.addWidget(self.btn_auto_pause); l.addLayout(bl)
        self.label_auto_status = QLabel("● Inactivo"); self.label_auto_status.setStyleSheet(f"color: {ProfessionalColors.TEXT_MUTED};")
        l.addWidget(self.label_auto_status)
        si = QLabel("🛡️ Seguridad activa: delays humanos, clicks imperfectos, pausas, rotación de patrones")
        si.setWordWrap(True); si.setStyleSheet(f"background:#0a1a0a; color:{ProfessionalColors.SUCCESS}; border:1px solid #1a3a1a; border-radius:8px; padding:8px; font-size:11px;")
        l.addWidget(si); l.addStretch(); w.setLayout(l); return w

    def _create_keyboard_tab(self):
        w = QWidget(); l = QVBoxLayout(); l.setSpacing(12); l.setContentsMargins(16, 16, 16, 16)
        d = QLabel("Escribe la jugada y se ejecuta en chess.com.\nFormatos: e2e4 · Nf3 · e4"); d.setWordWrap(True)
        d.setStyleSheet(f"color: {ProfessionalColors.TEXT_SECONDARY}; font-size: 12px;"); l.addWidget(d)
        ic = QWidget(); ic.setStyleSheet("background-color: " + ProfessionalColors.PRIMARY + "; border: 1px solid " + ProfessionalColors.BORDER + "; border-left: 3px solid " + ProfessionalColors.PRIMARY + "; border-radius: 8px; padding: 12px;"); il = QVBoxLayout()
        r = QHBoxLayout(); r.addWidget(QLabel("Jugada:"))
        self.input_move = QLineEdit(); self.input_move.setPlaceholderText("e2e4, Nf3, e4...")
        self.input_move.setFont(QFont("Consolas", 16)); self.input_move.returnPressed.connect(self._execute_keyboard_move)
        r.addWidget(self.input_move, stretch=1)
        be = QPushButton("▶ Ejecutar"); be.setObjectName("btn_primary"); be.clicked.connect(self._execute_keyboard_move); r.addWidget(be)
        il.addLayout(r); ic.setLayout(il); l.addWidget(ic)
        br = QHBoxLayout()
        self.btn_keyboard_activate = QPushButton("⌨  Activar"); self.btn_keyboard_activate.clicked.connect(self._activate_keyboard); br.addWidget(self.btn_keyboard_activate)
        self.btn_keyboard_deactivate = QPushButton("Desactivar"); self.btn_keyboard_deactivate.setEnabled(False); self.btn_keyboard_deactivate.clicked.connect(self._deactivate_keyboard); br.addWidget(self.btn_keyboard_deactivate)
        l.addLayout(br)
        self.btn_show_legal = QPushButton("📋 Ver movimientos legales"); self.btn_show_legal.clicked.connect(self._show_legal_moves); l.addWidget(self.btn_show_legal)
        self.text_legal_moves = QTextEdit(); self.text_legal_moves.setReadOnly(True); self.text_legal_moves.setFixedHeight(80); self.text_legal_moves.setVisible(False); l.addWidget(self.text_legal_moves)
        l.addStretch(); w.setLayout(l); return w

    def _create_suggest_tab(self):
        w = QWidget(); l = QVBoxLayout(); l.setSpacing(12); l.setContentsMargins(16, 16, 16, 16)
        d = QLabel("Flechas de colores sobre el tablero. Click en la que prefieras.\n🟢 Mejor · 🔵 Segunda · 🟠 Tercera"); d.setWordWrap(True)
        d.setStyleSheet(f"color: {ProfessionalColors.TEXT_SECONDARY}; font-size: 12px;"); l.addWidget(d)
        br = QHBoxLayout()
        self.btn_suggest_start = QPushButton("💡 MOSTRAR"); self.btn_suggest_start.setObjectName("btn_suggest"); self.btn_suggest_start.clicked.connect(self._start_suggest); br.addWidget(self.btn_suggest_start)
        self.btn_suggest_refresh = QPushButton("🔄"); self.btn_suggest_refresh.setFixedWidth(40); self.btn_suggest_refresh.clicked.connect(self._refresh_suggestions); br.addWidget(self.btn_suggest_refresh)
        self.btn_suggest_stop = QPushButton("⏹ Ocultar"); self.btn_suggest_stop.setEnabled(False); self.btn_suggest_stop.clicked.connect(self._stop_suggest); br.addWidget(self.btn_suggest_stop)
        l.addLayout(br)
        ar = QHBoxLayout(); self.check_auto_refresh = QCheckBox("Auto cada"); self.check_auto_refresh.setChecked(True); ar.addWidget(self.check_auto_refresh)
        self.spin_refresh = QSpinBox(); self.spin_refresh.setRange(1, 30); self.spin_refresh.setValue(3); self.spin_refresh.setSuffix("s"); ar.addWidget(self.spin_refresh); ar.addStretch(); l.addLayout(ar)
        self.label_suggestions = QLabel("Sin sugerencias"); self.label_suggestions.setStyleSheet(f"background:{ProfessionalColors.BG_MEDIUM}; border:1px solid {ProfessionalColors.BORDER}; border-radius:8px; padding:12px; font-family:Consolas;"); self.label_suggestions.setWordWrap(True); self.label_suggestions.setMinimumHeight(60); l.addWidget(self.label_suggestions)
        sr = QHBoxLayout(); sr.addWidget(QLabel("Ejecutar #")); self.spin_select = QSpinBox(); self.spin_select.setRange(1, 5); sr.addWidget(self.spin_select)
        bs = QPushButton("Ejecutar"); bs.clicked.connect(self._execute_suggestion); sr.addWidget(bs); sr.addStretch(); l.addLayout(sr)
        l.addStretch(); w.setLayout(l); return w

    def _create_stealth_tab(self):
        w = QWidget(); l = QVBoxLayout(); l.setSpacing(10); l.setContentsMargins(16, 12, 16, 12)
        sc = QWidget(); sc.setStyleSheet(f"QWidget{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0a1a0a,stop:1 #0a1a15);border:1px solid #1a3a2a;border-radius:10px;padding:10px;}}")
        sl = QVBoxLayout()
        self.check_stealth_enabled = QCheckBox("🛡️  COMPORTAMIENTO HUMANIZADO ACTIVO")
        self.check_stealth_enabled.setChecked(self.config.stealth.enabled)
        self.check_stealth_enabled.setStyleSheet(f"QCheckBox{{font-size:14px;font-weight:bold;color:{ProfessionalColors.SUCCESS};}}QCheckBox::indicator{{width:24px;height:24px;border-radius:6px;}}QCheckBox::indicator:checked{{background-color:{ProfessionalColors.SUCCESS};}}")
        sl.addWidget(self.check_stealth_enabled); sc.setLayout(sl); l.addWidget(sc)
        hc = QGroupBox("HUMANIZACIÓN"); hc.setStyleSheet("background-color: " + ProfessionalColors.SUCCESS + "; border: 1px solid " + ProfessionalColors.BORDER + "; border-left: 3px solid " + ProfessionalColors.SUCCESS + "; border-radius: 8px; padding: 12px;"); hcl = QVBoxLayout()
        for label, attr, val, mn, mx in [
            ("Reacción mín (x0.1s):", 'spin_reaction_time', int(self.config.stealth.min_reaction_time*10), 1, 100),
            ("Variación pensam (%):", 'spin_think_variance', int(self.config.stealth.think_time_variance*100), 10, 100),
            ("Distracción (%):", 'spin_distraction_chance', int(self.config.stealth.distraction_pause_chance*100), 0, 30),
            ("Desviación click (px):", 'spin_click_offset', self.config.stealth.click_offset_max, 0, 30),
            ("Hover antes de mover (%):", 'spin_hover_chance', int(self.config.stealth.hover_before_move_chance*100), 0, 100),
            ("Curvatura mouse (%):", 'spin_curve', int(self.config.stealth.mouse_curve_factor*100), 0, 50),
            ("Micro-temblor (px):", 'spin_tremor', self.config.stealth.mouse_tremor_amplitude, 0, 10)]:
            r = QHBoxLayout(); r.addWidget(QLabel(label))
            sp = QSpinBox(); sp.setRange(mn, mx); sp.setValue(val); sp.setFixedWidth(70); setattr(self, attr, sp); r.addWidget(sp); r.addStretch(); hcl.addLayout(r)
        hc.setLayout(hcl); l.addWidget(hc)

        sec = QGroupBox("SEGURIDAD AVANZADA"); sec.setStyleSheet("background-color: " + ProfessionalColors.WARNING + "; border: 1px solid " + ProfessionalColors.BORDER + "; border-left: 3px solid " + ProfessionalColors.WARNING + "; border-radius: 8px; padding: 12px;"); secl = QVBoxLayout()
        lr = QHBoxLayout(); lr.addWidget(QLabel("Máx partidas:")); self.spin_max_games = QSpinBox(); self.spin_max_games.setRange(1,50); self.spin_max_games.setValue(self.config.security.max_games_per_session); self.spin_max_games.setFixedWidth(60); lr.addWidget(self.spin_max_games)
        lr.addWidget(QLabel("Máx horas:")); self.spin_max_hours = QSpinBox(); self.spin_max_hours.setRange(1,12); self.spin_max_hours.setValue(int(self.config.security.max_session_hours)); self.spin_max_hours.setFixedWidth(50); lr.addWidget(self.spin_max_hours); lr.addStretch(); secl.addLayout(lr)
        rr = QHBoxLayout(); rr.addWidget(QLabel("Descanso entre partidas:")); self.spin_rest_min = QSpinBox(); self.spin_rest_min.setRange(0,30); self.spin_rest_min.setValue(self.config.security.rest_between_games_min); self.spin_rest_min.setSuffix(" min"); self.spin_rest_min.setFixedWidth(70); rr.addWidget(self.spin_rest_min); rr.addStretch(); secl.addLayout(rr)
        self.check_chess_active = QCheckBox("Verificar ventana chess.com activa"); self.check_chess_active.setChecked(self.config.security.require_chess_active); secl.addWidget(self.check_chess_active)
        self.check_vary_elo = QCheckBox("Variar ELO entre partidas"); self.check_vary_elo.setChecked(self.config.security.vary_elo_between_games); secl.addWidget(self.check_vary_elo)
        self.check_verify = QCheckBox("Verificar movimientos ejecutados"); self.check_verify.setChecked(self.config.security.verify_move_executed); secl.addWidget(self.check_verify)
        sec.setLayout(secl); l.addWidget(sec)

        stc = QGroupBox("ESTADÍSTICAS"); stc.setStyleSheet("background-color: " + ProfessionalColors.PRIMARY + "; border: 1px solid " + ProfessionalColors.BORDER + "; border-left: 3px solid " + ProfessionalColors.PRIMARY + "; border-radius: 8px; padding: 12px;"); stl = QVBoxLayout()
        self.label_stealth_stats = QLabel("Inicia una partida para ver estadísticas."); self.label_stealth_stats.setWordWrap(True); stl.addWidget(self.label_stealth_stats)
        bst = QPushButton("📊 Actualizar"); bst.clicked.connect(self._show_stealth_stats); stl.addWidget(bst)
        stc.setLayout(stl); l.addWidget(stc)
        tip = QLabel("💡 No +10 partidas seguidas · Varía ELO · Pausas reales · A veces pierde")
        tip.setWordWrap(True); tip.setStyleSheet(f"background:#1a1a00;color:{ProfessionalColors.WARNING};border:1px solid #3a3a00;border-radius:8px;padding:8px;font-size:11px;")
        l.addWidget(tip); l.addStretch(); w.setLayout(l); return w

    def _init_components(self):
        self.reader = BoardReader(self.config.board)
        self.controller = ChessComController(self.config.board, self.config.automation, self.config.stealth)
        self.overlay = ChessOverlay(self.config.board, self.config.display)
        self.overlay.move_selected.connect(self._on_overlay_move_selected)
        self.security = SecurityManager(self.config.security)

    def _start_engine(self):
        self.engine = ChessEngine(self.config.engine)
        if self.engine.start():
            self.badge_engine.setText("✅ Engine OK"); self.badge_engine.setStyleSheet("background-color: #0d2818; color: " + ProfessionalColors.SUCCESS + "; border: 1px solid " + ProfessionalColors.SUCCESS + "; border-radius: 12px; padding: 4px 12px; font-weight: 600; font-size: 11px;"); self._log("Motor Stockfish iniciado")
        else:
            self.badge_engine.setText("❌ Sin Stockfish"); self.badge_engine.setStyleSheet("background-color: #1a0000; color: " + ProfessionalColors.DANGER + "; border: 1px solid " + ProfessionalColors.DANGER + "; border-radius: 12px; padding: 4px 12px; font-weight: 600; font-size: 11px;"); self._log("ERROR: Stockfish no encontrado")

    def _start_security_monitor(self):
        self._security_timer = QTimer(); self._security_timer.timeout.connect(self._check_security); self._security_timer.start(30000)

    def _check_security(self):
        if self.security:
            ok, reason = self.security.can_play()
            if not ok: self._log(f"🛡️ {reason}"); self.statusBar().showMessage(f"⚠ {reason}", 10000)

    def _get_elo_description(self, elo):
        for th, d in [(500,"Principiante"),(800,"Muy Fácil"),(1000,"Fácil"),(1200,"Normal-Bajo"),(1400,"Normal"),(1600,"Normal-Alto"),(1800,"Intermedio"),(2000,"Avanzado"),(2200,"Experto"),(2500,"Maestro"),(3001,"Máximo")]:
            if elo < th: return f"ELO {elo} · {d}"
        return f"ELO {elo} · Máximo"

    def _on_elo_slider_changed(self, v):
        self.spin_elo.setValue(v); self.label_elo_desc.setText(self._get_elo_description(v))

    def _on_elo_spin_changed(self, v):
        self.slider_elo.setValue(v); self.label_elo_desc.setText(self._get_elo_description(v))
        if self.engine: self.engine.set_elo(v)

    def _show_quick_start(self):
        from auto_chess.ui.quick_start import QuickStartWizard
        wiz = QuickStartWizard(self); wiz.wizard_completed.connect(self._on_wizard_completed); wiz.exec_()

    def _on_wizard_completed(self, r):
        if r.get('calibrate_now'): self._open_calibration()
        if r.get('stealth_enabled'): self.config.stealth.enabled = True; self.check_stealth_enabled.setChecked(True)

    def _open_calibration(self):
        d = CalibrationDialog(self, self.config.board); d.calibration_done.connect(self._on_calibration_done); d.exec_()

    def _on_calibration_done(self, bc):
        self.config.board = bc; self.config.save(); self.reader.config = bc; self.controller.board_config = bc
        self.overlay.board_config = bc; self.overlay.update_position()
        self.label_cal_status.setText("✓ Calibrado"); self.label_cal_status.setStyleSheet("background-color: #0d2818; color: " + ProfessionalColors.SUCCESS + "; border: 1px solid " + ProfessionalColors.SUCCESS + "; border-radius: 12px; padding: 4px 12px; font-weight: 600; font-size: 11px;")
        self._log(f"Tablero calibrado: {bc.square_size}px/casilla")

    def _refresh_board(self):
        if not self.config.board.is_calibrated: self._log("⚠ Calibra primero"); return
        self._log("Leyendo tablero..."); board = self.reader.read_board()
        if board: self._log(f"✓ {board.fen()}")
        else: self._log("⚠ No se pudo leer")

    def _start_auto(self):
        if not self.engine or not self.engine.is_running: QMessageBox.warning(self,"Error","Motor no activo."); return
        if not self.config.board.is_calibrated: QMessageBox.warning(self,"Error","Calibra el tablero."); return
        ok, reason = self.security.can_play()
        if not ok: QMessageBox.warning(self,"Seguridad",reason); return
        self.security.register_game_start(); color = chess.WHITE if self.radio_white.isChecked() else chess.BLACK
        self.auto_mode = AutoMode(self.engine, self.reader, self.controller)
        self.auto_mode.set_on_status(self._on_auto_status); self.auto_mode.set_on_move(self._on_auto_move); self.auto_mode.set_on_game_end(self._on_auto_game_end)
        self.btn_auto_start.setEnabled(False); self.btn_auto_stop.setEnabled(True); self.btn_auto_pause.setEnabled(True)
        self.label_auto_status.setText("● Ejecutando..."); self.label_auto_status.setStyleSheet(f"color:{ProfessionalColors.SUCCESS};font-weight:bold;")
        self._auto_thread = WorkerThread(self.auto_mode.start, color); self._auto_thread.status_update.connect(self._on_auto_status); self._auto_thread.start()
        self._log("🤖 Modo Auto INICIADO")

    def _stop_auto(self):
        if self.auto_mode: self.auto_mode.stop()
        if self._auto_thread: self._auto_thread.wait(5000); self._auto_thread = None
        self.btn_auto_start.setEnabled(True); self.btn_auto_stop.setEnabled(False); self.btn_auto_pause.setEnabled(False)
        self.label_auto_status.setText("● Inactivo"); self.label_auto_status.setStyleSheet(f"color:{ProfessionalColors.TEXT_MUTED};")
        self._log("⏹ Modo Auto DETENIDO")

    def _pause_auto(self):
        if self.auto_mode:
            if self.auto_mode.is_paused: self.auto_mode.resume(); self.btn_auto_pause.setText("⏸"); self.label_auto_status.setText("● Ejecutando..."); self.label_auto_status.setStyleSheet(f"color:{ProfessionalColors.SUCCESS};")
            else: self.auto_mode.pause(); self.btn_auto_pause.setText("▶"); self.label_auto_status.setText("● Pausado"); self.label_auto_status.setStyleSheet(f"color:{ProfessionalColors.WARNING};")

    def _on_auto_status(self, m): self._log(f"[Auto] {m}"); self.label_auto_status.setText(f"● {m}")
    def _on_auto_move(self, u):
        self._log(f"  ↳ {u}")
        if self.security: self.security.register_move()
    def _on_auto_game_end(self, r):
        self._log(f"🏁 {r}"); self._stop_auto()
        if self.security: self.security.register_game_end()

    def _activate_keyboard(self):
        if not self.config.board.is_calibrated: QMessageBox.warning(self,"Error","Calibra primero."); return
        self.keyboard_mode = KeyboardMode(self.engine, self.reader, self.controller)
        self.keyboard_mode.set_on_status(self._log); self.keyboard_mode.set_on_error(lambda m: self._log(f"⚠ {m}")); self.keyboard_mode.activate()
        self.btn_keyboard_activate.setEnabled(False); self.btn_keyboard_deactivate.setEnabled(True); self.input_move.setFocus()

    def _deactivate_keyboard(self):
        if self.keyboard_mode: self.keyboard_mode.deactivate()
        self.btn_keyboard_activate.setEnabled(True); self.btn_keyboard_deactivate.setEnabled(False)

    def _execute_keyboard_move(self):
        if not self.keyboard_mode: self._activate_keyboard()
        t = self.input_move.text().strip()
        if not t or not self.keyboard_mode: return
        ok = self.keyboard_mode.process_input(t)
        if ok:
            self.input_move.clear()
            if self.security: self.security.register_move()
        QTimer.singleShot(500, lambda: self.input_move.setStyleSheet(""))

    def _show_legal_moves(self):
        v = not self.text_legal_moves.isVisible(); self.text_legal_moves.setVisible(v)
        if v and self.reader:
            b = self.reader.read_board_with_fallback(); self.text_legal_moves.setText(", ".join([f"{b.san(m)} ({m.uci()})" for m in b.legal_moves][:25]))

    def _start_suggest(self):
        if not self.engine or not self.engine.is_running: QMessageBox.warning(self,"Error","Motor no activo."); return
        if not self.config.board.is_calibrated: QMessageBox.warning(self,"Error","Calibra primero."); return
        self.engine.config.multi_pv = self.spin_suggestions.value()
        self.suggest_mode = SuggestMode(self.engine, self.reader, self.controller)
        self.suggest_mode.set_on_suggestions(self._on_suggestions_update); self.suggest_mode.set_on_status(self._log); self.suggest_mode.activate()
        self.overlay.show_overlay()
        if self.check_auto_refresh.isChecked(): self._suggest_timer = QTimer(); self._suggest_timer.timeout.connect(self._refresh_suggestions); self._suggest_timer.start(self.spin_refresh.value()*1000)
        self._refresh_suggestions(); self.btn_suggest_start.setEnabled(False); self.btn_suggest_stop.setEnabled(True); self._log("💡 Sugerencias ACTIVAS")

    def _stop_suggest(self):
        if self._suggest_timer: self._suggest_timer.stop()
        if self.suggest_mode: self.suggest_mode.deactivate()
        self.overlay.hide_overlay(); self.btn_suggest_start.setEnabled(True); self.btn_suggest_stop.setEnabled(False)

    def _refresh_suggestions(self):
        if self.suggest_mode and self.suggest_mode.is_active: self.suggest_mode.update_suggestions()

    def _on_suggestions_update(self, sugs):
        if not sugs: self.label_suggestions.setText("Sin sugerencias"); self.overlay.clear_suggestions(); return
        colors = [ProfessionalColors.SUCCESS, ProfessionalColors.PRIMARY, ProfessionalColors.WARNING]
        self.label_suggestions.setText("<br>".join([f'<span style="color:{colors[i] if i<3 else ProfessionalColors.TEXT_SECONDARY}">  {i+1}. {s.move.uci()} → {s.score_display}</span>' for i,s in enumerate(sugs)]))
        self.overlay.show_suggestions(sugs)

    def _on_overlay_move_selected(self, i):
        self._log(f"Click #{i+1}")
        if self.suggest_mode: self.suggest_mode.select_suggestion(i)
        if self.security: self.security.register_move()

    def _execute_suggestion(self):
        if self.suggest_mode: self.suggest_mode.select_suggestion(self.spin_select.value()-1)
        if self.security: self.security.register_move()

    def _show_stealth_stats(self):
        if self.controller:
            st = self.controller.get_stealth_stats()
            if st and st.get('num_moves',0)>0:
                ss = self.security.get_session_summary() if self.security else {}
                self.label_stealth_stats.setText(f"Movs: {st['num_moves']} · Avg: {st['avg_time']:.1f}s · Std: {st['std_dev']:.1f}s · Patrón: {st['pattern']}\nPartidas: {ss.get('games_played',0)}/{ss.get('max_games',10)} · Sesión: {ss.get('session_minutes',0):.0f}min")
            else: self.label_stealth_stats.setText("Sin movimientos registrados.")

    def _save_config(self):
        self.config.engine.elo = self.spin_elo.value(); self.config.engine.think_time = float(self.spin_think.value()); self.config.engine.multi_pv = self.spin_suggestions.value()
        self.config.stealth.enabled = self.check_stealth_enabled.isChecked()
        self.config.stealth.min_reaction_time = self.spin_reaction_time.value()/10.0; self.config.stealth.think_time_variance = self.spin_think_variance.value()/100.0
        self.config.stealth.distraction_pause_chance = self.spin_distraction_chance.value()/100.0; self.config.stealth.click_offset_max = self.spin_click_offset.value()
        self.config.stealth.hover_before_move_chance = self.spin_hover_chance.value()/100.0; self.config.stealth.mouse_curve_factor = self.spin_curve.value()/100.0
        self.config.stealth.mouse_tremor_amplitude = self.spin_tremor.value()
        self.config.security.max_games_per_session = self.spin_max_games.value(); self.config.security.max_session_hours = float(self.spin_max_hours.value())
        self.config.security.rest_between_games_min = self.spin_rest_min.value(); self.config.security.require_chess_active = self.check_chess_active.isChecked()
        self.config.security.vary_elo_between_games = self.check_vary_elo.isChecked(); self.config.security.verify_move_executed = self.check_verify.isChecked()
        self.config.save()
        if self.controller: self.controller.stealth_config = self.config.stealth; self.controller._init_stealth()
        if self.security: self.security.config = self.config.security
        self._log("💾 Guardado"); self.statusBar().showMessage("✓ Guardado", 3000)

    def _reload_config(self): self.config = AppConfig.load(); self.spin_elo.setValue(self.config.engine.elo); self._log("📂 Recargado")
    def _show_about(self): QMessageBox.about(self,"AutoChess","♟ AutoChess v1.0\nHerramienta de accesibilidad.\n\n🛡️ Humanizado + Seguro\nSolo contra bots.")

    def _log(self, msg):
        from datetime import datetime
        self.text_log.append(f'<span style="color:{ProfessionalColors.TEXT_MUTED}">[{datetime.now().strftime("%H:%M:%S")}]</span> {msg}')
        c = self.text_log.textCursor(); c.movePosition(QTextCursor.End); self.text_log.setTextCursor(c)

    def closeEvent(self, event):
        if self.auto_mode and self.auto_mode.is_running: self.auto_mode.stop()
        if self._suggest_timer: self._suggest_timer.stop()
        if self._security_timer: self._security_timer.stop()
        if self.suggest_mode: self.suggest_mode.deactivate()
        if self.overlay: self.overlay.close()
        if self.engine: self.engine.stop()
        if self.reader: self.reader.close()
        if self.security: self.security.clear_session_logs()
        self._save_config(); event.accept()
