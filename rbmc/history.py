import chess
from .types import *


class GameHistory(object):

    def __init__(self):
        self.senses = {chess.WHITE: [], chess.BLACK: []}
        self.sense_results = {chess.WHITE: [], chess.BLACK: []}
        self.moves = {chess.WHITE: [], chess.BLACK: []}
        self.move_results = {chess.WHITE: [], chess.BLACK: []}

    def store_sense(self, color: Color, square: Square,
                sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        self.senses[color].append(square)
        self.sense_results[color].append(sense_result)        

    def store_move(self, color: Color, requested_move: chess.Move, 
                taken_move: chess.Move, opt_capture_square: Square):
        self.moves[color].append(requested_move)
        self.move_results[color].append({
            "taken_move": taken_move,
            "opt_capture_square": opt_capture_square
        })

    def get_sense_history_for(self, color: Color) -> List[Square]:
        return self.senses[color]

    def get_move_history_for(self, color: Color) -> List[chess.Move]:
        return self.moves[color]
