import chess.engine
import random
from reconchess import *
import os
from stockfish import Stockfish




class DJBot(Player):

    # GENERAL STRATEGY:

    # - Each piece has a score; Ally pieces are negative score
    # - Count each captured piece as the game 'score'
    # - Dynamically minimax to figure out best moves
    # - Dynamically populate list of instakill movesets

    # TODO:
    # - maintain belief state of pieces


    def __init__(self):
        self.board = None
        self.belief = chess.Board( chess.STARTING_FEN )
        self.color = None
        self.my_piece_captured_square = None
        self.stockfish = Stockfish()
        self.space_conversions = {
        'a1': chess.A1,
        'a2': chess.A2,
        'a3': chess.A3,
        'a4': chess.A4,
        'a5': chess.A5,
        'a6': chess.A6,
        'a7': chess.A7,
        'a8': chess.A8,
        'b1': chess.B1,
        'b2': chess.B2,
        'b3': chess.B3,
        'b4': chess.B4,
        'b5': chess.B5,
        'b6': chess.B6,
        'b7': chess.B7,
        'b8': chess.B8,
        'c1': chess.C1,
        'c2': chess.C2,
        'c3': chess.C3,
        'c4': chess.C4,
        'c5': chess.C5,
        'c6': chess.C6,
        'c7': chess.C7,
        'c8': chess.C8,
        'd1': chess.D1,
        'd2': chess.D2,
        'd3': chess.D3,
        'd4': chess.D4,
        'd5': chess.D5,
        'd6': chess.D6,
        'd7': chess.D7,
        'd8': chess.D8,
        'e1': chess.E1,
        'e2': chess.E2,
        'e3': chess.E3,
        'e4': chess.E4,
        'e5': chess.E5,
        'e6': chess.E6,
        'e7': chess.E7,
        'e8': chess.E8,
        'f1': chess.F1,
        'f2': chess.F2,
        'f3': chess.F3,
        'f4': chess.F4,
        'f5': chess.F5,
        'f6': chess.F6,
        'f7': chess.F7,
        'f8': chess.F8,
        'g1': chess.G1,
        'g2': chess.G2,
        'g3': chess.G3,
        'g4': chess.G4,
        'g5': chess.G5,
        'g6': chess.G6,
        'g7': chess.G7,
        'g8': chess.G8,
        'h1': chess.H1,
        'h2': chess.H2,
        'h3': chess.H3,
        'h4': chess.H4,
        'h5': chess.H5,
        'h6': chess.H6,
        'h7': chess.H7,
        'h8': chess.H8,
        }

    def handle_game_start(self, color: Color, board: chess.Board):
        self.board = color
        self.color = board
        self.stockfish.set_fen_position(self.belief.fen());

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # if the opponent captured our piece, remove it from our board.
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    # basically what stockfish does. 
    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        # if our piece was just captured, sense where it was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square

        # if we might capture a piece when we move, sense where the capture will occur
        future_move = self.choose_move(move_actions, seconds_left)
        if future_move is not None and self.board.piece_at(future_move.to_square) is not None:
            return future_move.to_square

        # otherwise, just randomly choose a sense action, but don't sense on a square where our pieces are located
        for square, piece in self.board.piece_map().items():
            if piece.color == self.color:
                sense_actions.remove(square)
        return random.choice(sense_actions)

    # register where we see other pieces
    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def stockfish_move_conversion(self, move):
        source = move[:2]
        dest = move[2:]

        return chess.Move( self.space_conversions[source], self.space_conversions[dest] )
        

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        stock_move = self.stockfish_move_conversion(self.stockfish.get_best_move())
        return stock_move 


    def update_beliefs(self, sense_results):
        pass


    # don't change
    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # if a move was executed, apply it to our board
        if taken_move is not None:
            self.board.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        pass
