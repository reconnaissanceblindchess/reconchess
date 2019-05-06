import random
from reconchess import *

# move sequences from white's perspective, flipped at runtime if playing as black
QUICK_ATTACKS = [
    # queen-side knight attacks
    [chess.Move(chess.B1, chess.C3), chess.Move(chess.C3, chess.B5), chess.Move(chess.B5, chess.D6),
     chess.Move(chess.D6, chess.E8)],
    [chess.Move(chess.B1, chess.C3), chess.Move(chess.C3, chess.E4), chess.Move(chess.E4, chess.F6),
     chess.Move(chess.F6, chess.E8)],

    # king-side knight attacks
    [chess.Move(chess.G1, chess.H3), chess.Move(chess.H3, chess.F4), chess.Move(chess.F4, chess.H5),
     chess.Move(chess.H5, chess.F6), chess.Move(chess.F6, chess.E8)],

    # four move mates
    [chess.Move(chess.E2, chess.E4), chess.Move(chess.F1, chess.C4), chess.Move(chess.D1, chess.H5), chess.Move(
        chess.C4, chess.F7), chess.Move(chess.F7, chess.E8), chess.Move(chess.H5, chess.E8)],
]


def flipped_move(move):
    def flipped(square):
        return chess.square(chess.square_file(square), 7 - chess.square_rank(square))

    return chess.Move(from_square=flipped(move.from_square), to_square=flipped(move.to_square),
                      promotion=move.promotion, drop=move.drop)


class AttackerBot(Player):
    def __init__(self):
        self.move_sequence = random.choice(QUICK_ATTACKS)

    def handle_game_start(self, color: Color, board: chess.Board):
        if color == chess.BLACK:
            self.move_sequence = list(map(flipped_move, self.move_sequence))

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        pass

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        return random.choice(sense_actions)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        pass

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        while len(self.move_sequence) > 0 and self.move_sequence[0] not in move_actions:
            self.move_sequence.pop(0)

        if len(self.move_sequence) == 0:
            # pass... we failed so give up
            return None
        else:
            return self.move_sequence.pop(0)

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        pass

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        pass
