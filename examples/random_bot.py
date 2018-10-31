import chess
import random
from typing import List, Tuple, Optional
from rbmc import Player, Square, Color


class RandomBot(Player):
    def handle_game_start(self, color: Color, board: chess.Board):
        pass

    def handle_turn_start(self, seconds_left: float):
        pass

    def handle_my_piece_captured(self, my_piece_captured_square: Square):
        pass

    def choose_sense(self, valid_senses: List[Square], valid_moves: List[chess.Move]) -> Square:
        return random.choice(valid_senses)

    def handle_sense_result(self, sense_result: List[Tuple[Square, chess.Piece]]):
        pass

    def choose_move(self, valid_moves: List[chess.Move]) -> chess.Move:
        return random.choice(valid_moves)

    def handle_move_result(self, requested_move: chess.Move, taken_move: chess.Move,
                           enemy_captured_square: Optional[Square]):
        pass

    def handle_turn_end(self):
        pass

    def handle_game_end(self, winner_color: Optional[Color], senses: List[Square], moves: List[chess.Move],
                        opponent_senses: List[Square], opponent_moves: List[chess.Move]):
        pass
