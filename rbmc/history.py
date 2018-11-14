import chess
from .types import *


class GameHistory(object):

    def __init__(self):
        self.history = {}

    def store_sense(self, move_number: int, color: Color, square: Square,
                sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        pass

    def store_move(self, move_number: int, color: Color, 
                requested_move: chess.Move, taken_move: chess.Move, 
                opt_capture_square: Square):
        pass

    def get_sense_history_for(self, color: Color) -> List[Square]:
        pass

    def get_move_history_for(self, color: Color) -> List[chess.Move]:
        pass
