import chess
from .types import *


class GameHistory(object):

    def __init__(self):
        self.senses = {chess.WHITE: [], chess.BLACK: []}
        self.sense_results = {chess.WHITE: [], chess.BLACK: []}
        self.requested_moves = {chess.WHITE: [], chess.BLACK: []}
        self.taken_moves = {chess.WHITE: [], chess.BLACK: []}
        self.capture_squares = {chess.WHITE: [], chess.BLACK: []}

    def store_sense(self, color: Color, square: Square,
                sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        self.senses[color].append(square)
        self.sense_results[color].append(sense_result)        

    def store_move(self, color: Color, requested_move: chess.Move, 
                taken_move: chess.Move, opt_capture_square: Square):
        self.requested_moves[color].append(requested_move)
        self.taken_moves[color].append(taken_move)
        self.capture_squares[color].append(opt_capture_square)

    def get_sense_history_for(self, color: Color) -> List[Square]:
        return self.senses[color]

    def get_move_history_for(self, color: Color) -> List[chess.Move]:
        return self.requested_moves[color]
