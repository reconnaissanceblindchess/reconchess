import chess
from .types import *


class GameHistory(object):

    def __init__(self):
        self.history = {}

    def __get_history_item_for(self, move_number: int, color: Color):
        if move_number not in self.history:
            self.history[move_number] = {}
        if color not in self.history[move_number]:
            self.history[move_number][color] = {}
        return self.history[move_number][color]

    def store_sense(self, move_number: int, color: Color, square: Square,
                sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        self.__get_history_item_for(move_number, color)["sense"] = {
            "square": square,
            "sense_result": sense_result
        }

    def store_move(self, move_number: int, color: Color, 
                requested_move: chess.Move, taken_move: chess.Move, 
                opt_capture_square: Square):
        self.__get_history_item_for(move_number, color)["move"] = {
            "requested_move": requested_move,
            "taken_move": taken_move,
            "opt_capture_square": opt_capture_square
        }

    def get_sense_history_for(self, color: Color) -> List[Square]:
        return [self.history[move_number][color]["sense"]["square"] for
            move_number in sorted(self.history.keys())]

    def get_move_history_for(self, color: Color) -> List[chess.Move]:
        return [self.history[move_number][color]["move"]["requested_move"] for
            move_number in sorted(self.history.keys())]
