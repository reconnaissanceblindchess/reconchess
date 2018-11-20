import chess
from .types import *


class GameHistory(object):

    def __init__(self):
        self.senses = {chess.WHITE: [], chess.BLACK: []}
        self.moves = {chess.WHITE: [], chess.BLACK: []}
        self.opponent_move_results = {chess.WHITE: [], chess.BLACK: []}

    def store_opponent_move_results(self, color: Color,
            opt_capture_square: Optional[Square]):
        self.opponent_move_results[color].append({
            "opt_capture_square": opt_capture_square
        })

    def store_sense(self, color: Color, square: Square,
                sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        self.senses[color].append({
            "square": square,
            "sense_result": sense_result
        })

    def store_move(self, color: Color, requested_move: chess.Move, 
                taken_move: chess.Move, opt_capture_square: Square):
        self.moves[color].append({
            "requested_move": requested_move,
            "taken_move": taken_move,
            "opt_capture_square": opt_capture_square
        })

    def get_sense_history_for(self, color: Color) -> List[Square]:
        return [item["square"] for item in self.senses[color]]

    def get_move_history_for(self, color: Color) -> List[chess.Move]:
        return [item["requested_move"] for item in self.moves[color]]
