"""
Motor de ajedrez (Stockfish) integrado.
Proporciona análisis y sugerencias de jugadas con ELO configurable.
"""
import chess
import chess.engine
import random
import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass

from auto_chess.config import EngineConfig, get_engine_params_for_elo

logger = logging.getLogger(__name__)


@dataclass
class MoveAnalysis:
    """Resultado del análisis de una posición."""
    move: chess.Move
    score: float  # En centipeones (positivo = blanco mejor)
    depth: int
    is_mate: bool
    mate_in: Optional[int] = None  # Si es mate, en cuántos movimientos
    pv: List[chess.Move] = None  # Línea principal

    def __post_init__(self):
        if self.pv is None:
            self.pv = []

    @property
    def score_display(self) -> str:
        """Representación legible de la evaluación."""
        if self.is_mate:
            return f"M{self.mate_in}" if self.mate_in > 0 else f"-M{abs(self.mate_in)}"
        return f"+{self.score/100:.1f}" if self.score >= 0 else f"{self.score/100:.1f}"


class ChessEngine:
    """
    Wrapper de Stockfish para análisis de ajedrez.
    Soporta configuración de ELO (300-3000).
    """

    def __init__(self, config: EngineConfig = None):
        self.config = config or EngineConfig()
        self._engine: Optional[chess.engine.SimpleEngine] = None
        self._is_running = False

    def start(self) -> bool:
        """Inicia el motor de ajedrez."""
        try:
            if self.config.stockfish_path:
                self._engine = chess.engine.SimpleEngine.popen_uci(
                    self.config.stockfish_path
                )
            else:
                # Buscar stockfish en PATH
                self._engine = chess.engine.SimpleEngine.popen_uci("stockfish")

            self._is_running = True
            self._configure_engine()
            logger.info("Motor Stockfish iniciado correctamente")
            return True

        except FileNotFoundError:
            logger.error(
                "Stockfish no encontrado. Instale Stockfish o configure la ruta "
                "en la configuración."
            )
            return False
        except Exception as e:
            logger.error(f"Error al iniciar Stockfish: {e}")
            return False

    def _configure_engine(self):
        """Configura Stockfish con los parámetros del ELO seleccionado."""
        if not self._engine:
            return

        params = get_engine_params_for_elo(self.config.elo)

        try:
            # Configurar skill level (0-20)
            self._engine.configure({"Skill Level": params['skill_level']})
            logger.info(
                f"Engine configurado: ELO={self.config.elo}, "
                f"Skill={params['skill_level']}, Depth={params['depth']}"
            )
        except Exception as e:
            logger.warning(f"No se pudo configurar Skill Level: {e}")

    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Obtiene la mejor jugada para la posición actual.
        Aplica el factor de aleatoriedad según el ELO configurado.
        """
        if not self._is_running or not self._engine:
            return None

        params = get_engine_params_for_elo(self.config.elo)

        try:
            # Limitar tiempo y profundidad
            result = self._engine.analyse(
                board,
                chess.engine.Limit(
                    time=self.config.think_time,
                    depth=params['depth']
                )
            )

            # Obtener el mejor movimiento (ponderado por aleatoriedad)
            best_move = result.get('pv', [None])[0]

            if best_move is None:
                # Fallback: movimiento legal aleatorio
                legal_moves = list(board.legal_moves)
                return random.choice(legal_moves) if legal_moves else None

            # Aplicar factor de aleatoriedad: a veces hacer un movimiento subóptimo
            if params['random_move_chance'] > 0 and random.random() < params['random_move_chance']:
                legal_moves = list(board.legal_moves)
                if len(legal_moves) > 1:
                    # Elegir un movimiento del top 5 (no el mejor)
                    result_top = self._engine.analyse(
                        board,
                        chess.engine.Limit(
                            time=self.config.think_time * 0.5,
                            depth=max(params['depth'] - 2, 3),
                        ),
                        multipv=min(5, len(legal_moves))
                    )
                    if 'pv' in result_top and result_top['pv']:
                        alternatives = [r.get('pv', [None])[0]
                                       for r in (result_top if isinstance(result_top, list) else [result_top])
                                       if r.get('pv')]
                        alternatives = [m for m in alternatives if m is not None]
                        if alternatives:
                            # Elegir uno aleatorio de las alternativas
                            return random.choice(alternatives[1:]) if len(alternatives) > 1 else best_move

            return best_move

        except Exception as e:
            logger.error(f"Error al analizar posición: {e}")
            return None

    def get_top_moves(self, board: chess.Board,
                      num_moves: int = 3) -> List[MoveAnalysis]:
        """
        Obtiene los mejores N movimientos con su análisis.
        Usado para el modo sugerencia.
        """
        if not self._is_running or not self._engine:
            return []

        results = []
        params = get_engine_params_for_elo(self.config.elo)

        try:
            analysis = self._engine.analyse(
                board,
                chess.engine.Limit(
                    time=self.config.think_time,
                    depth=params['depth']
                ),
                multipv=num_moves
            )

            # analysis puede ser un dict (1 resultado) o list (múltiples)
            if isinstance(analysis, dict):
                analysis = [analysis]

            for i, info in enumerate(analysis[:num_moves]):
                pv = info.get('pv', [])
                if not pv:
                    continue

                move = pv[0]
                score_info = info.get('score', chess.engine.PovScore(
                    chess.engine.Cp(0), chess.WHITE
                ))

                # Convertir score a perspectiva de las blancas
                relative_score = score_info.relative

                is_mate = relative_score.is_mate()
                if is_mate:
                    mate_in = relative_score.mate()
                    score = 10000 if mate_in > 0 else -10000
                    results.append(MoveAnalysis(
                        move=move,
                        score=score,
                        depth=info.get('depth', 0),
                        is_mate=True,
                        mate_in=mate_in,
                        pv=pv
                    ))
                else:
                    cp = relative_score.score()
                    # Ajustar signo según el turno
                    if board.turn == chess.BLACK:
                        cp = -cp
                    results.append(MoveAnalysis(
                        move=move,
                        score=cp,
                        depth=info.get('depth', 0),
                        is_mate=False,
                        pv=pv
                    ))

        except Exception as e:
            logger.error(f"Error al analizar jugadas: {e}")

        return results

    def evaluate_position(self, board: chess.Board) -> float:
        """
        Evalúa la posición actual en centipeones.
        Positivo = ventaja blanca, negativo = ventaja negra.
        """
        if not self._is_running or not self._engine:
            return 0.0

        try:
            info = self._engine.analyse(
                board,
                chess.engine.Limit(depth=10, time=0.5)
            )
            score = info.get('score')
            if score:
                relative = score.relative
                if relative.is_mate():
                    return 10000 if relative.mate() > 0 else -10000
                cp = relative.score()
                if board.turn == chess.BLACK:
                    cp = -cp
                return cp
        except Exception:
            pass
        return 0.0

    def set_elo(self, elo: int):
        """Cambia el ELO del motor."""
        self.config.elo = max(300, min(3000, elo))
        if self._is_running:
            self._configure_engine()

    @property
    def is_running(self) -> bool:
        return self._is_running

    def stop(self):
        """Detiene el motor."""
        if self._engine:
            try:
                self._engine.quit()
            except Exception:
                pass
            self._engine = None
        self._is_running = False

    def __del__(self):
        self.stop()
