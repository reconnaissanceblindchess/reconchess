import chess
import random
from typing import List, Tuple, Optional
from rbmc import Player, Square, Color, GameHistory


class RandomBot(Player):
    def handle_game_start(self, color: Color, board: chess.Board):
        pass

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        pass

    def choose_sense(self, seconds_left: float, valid_senses: List[Square], valid_moves: List[chess.Move]) -> Square:
        return random.choice(valid_senses)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        pass

    def choose_move(self, seconds_left: float, valid_moves: List[chess.Move]) -> Optional[chess.Move]:
        return random.choice(valid_moves + [None])

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        pass

    def handle_game_end(self, winner_color: Optional[Color], game_history: GameHistory):
        pass
