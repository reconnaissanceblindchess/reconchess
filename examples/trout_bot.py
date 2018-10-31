import chess
import chess.uci
import random
from typing import List, Tuple, Optional
from rbmc import Player, Square, Color


class TroutBot(Player):
    def __init__(self):
        self.board = chess.Board()
        self.color = None
        self.my_piece_captured_square = None

        self.engine = chess.uci.popen_engine('./stockfish-8-64')
        self.engine.uci()

    def handle_game_start(self, color: Color, board: chess.Board):
        self.color = color

    def handle_turn_start(self, seconds_left: float):
        self.my_piece_captured_square = None

    def handle_my_piece_captured(self, my_piece_captured_square: Square):
        self.board.remove_piece_at(my_piece_captured_square)
        self.my_piece_captured_square = my_piece_captured_square

    def choose_sense(self, valid_senses: List[Square], valid_moves: List[chess.Move]) -> Square:
        # sense where our ally piece was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square

        # sense where we may capture an enemy piece
        future_move = self.choose_move(valid_moves)
        if self.board.piece_at(future_move.to_square) is not None:
            return future_move.to_square

        # don't sense on a squares where our pieces are located
        for square, piece in self.board.piece_map():
            if piece.color == self.color:
                valid_senses.remove(square)

        # sense at a random square
        return random.choice(valid_senses)

    def handle_sense_result(self, sense_result: List[Tuple[Square, chess.Piece]]):
        for square, piece in sense_result:
            if piece is None:
                self.board.remove_piece_at(square)
            else:
                self.board.set_piece_at(square, piece)

    def choose_move(self, valid_moves: List[chess.Move]) -> chess.Move:
        # try to take the king if we know where it might be
        enemy_king_positions = self.board.pieces(chess.KING, not self.color)
        if enemy_king_positions:
            enemy_king_square = enemy_king_positions.pop()
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)

            # if there are any ally pieces that can take king
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                return chess.Move(attacker_square, enemy_king_square)

        # try to move with the stockfish chess engine
        try:
            self.board.turn = self.color
            self.engine.ucinewgame()
            self.engine.position(self.board)
            stockfish_move = self.engine.go(movetime=500)[0]
            self.engine.stop()
            return stockfish_move
        except (chess.uci.EngineTerminatedException, chess.uci.EngineStateException):
            print('Stockfish engine bad state')

        # just make a random move
        return random.choice(valid_moves)

    def handle_move_result(self, requested_move: chess.Move, taken_move: chess.Move,
                           enemy_captured_square: Optional[Square]):
        piece = self.board.remove_piece_at(taken_move.from_square)
        self.board.set_piece_at(taken_move.to_square, piece)

    def handle_turn_end(self):
        pass

    def handle_game_end(self, winner_color: Optional[Color], senses: List[Square], moves: List[chess.Move],
                        opponent_senses: List[Square], opponent_moves: List[chess.Move]):
        pass
