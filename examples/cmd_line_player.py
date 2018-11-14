import chess
from typing import List, Tuple, Optional
from rbmc import Player, Square, Color


class CmdLinePlayer(Player):
    def __init__(self):
        self.board = None
        self.color = None

    def handle_game_start(self, color: Color, board: chess.Board):
        self.board = board
        self.color = color
        for square in chess.SQUARES:
            if self.board.piece_at(square) and self.board.piece_at(square).color == (not color):
                self.board.remove_piece_at(square)

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        if captured_my_piece:
            print('One of your pieces was captured at {}!'.format(chess.SQUARE_NAMES[capture_square]))

    def choose_sense(self, seconds_left: float, valid_senses: List[Square], valid_moves: List[chess.Move]) -> Square:
        while True:
            square_name = input('Sense phase, where to sense (input senses as [a-h][1-8])?').lower()
            if square_name in chess.SQUARE_NAMES:
                return chess.SQUARE_NAMES.index(square_name)
            else:
                print('Invalid square, input like "a1"')

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        sense_board = self.board.copy()
        for square, piece in sense_result:
            sense_board.set_piece_at(square, piece)

        print('Sense result:')
        print(sense_board)

    def choose_move(self, seconds_left: float, valid_moves: List[chess.Move]) -> Optional[chess.Move]:
        while True:
            print('Move phase. Valid moves are: {}'.format(valid_moves))
            move_uci = input('Where to move (input moves as UCI)?').lower()
            try:
                move = chess.Move.from_uci(move_uci)
                if move in valid_moves:
                    return move
                else:
                    print('Invalid move chosen.')
            except ValueError:
                print('Invalid UCI move, input like "a1a2"')

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        print('Requested move: {}'.format(requested_move))
        print('Taken move: {}'.format(taken_move))
        if captured_opponent_piece:
            print('Captured a piece at: {}'.format(chess.SQUARE_NAMES[capture_square]))

        if taken_move is not None:
            self.board.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], senses: List[Square], moves: List[Optional[chess.Move]],
                        opponent_senses: List[Square], opponent_moves: List[Optional[chess.Move]]):
        pass
