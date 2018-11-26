import chess
import chess.uci
import random
from typing import List, Tuple, Optional
from rbmc import Player, Square, Color, GameHistory


class TroutBot(Player):
    def __init__(self):
        self.board = chess.Board()
        self.color = None
        self.my_piece_captured_square = None

        self.engine = chess.uci.popen_engine('./stockfish-8-64')
        self.engine.uci()

    def handle_game_start(self, color: Color, board: chess.Board):
        self.color = color

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)
            self.my_piece_captured_square = capture_square

    def choose_sense(self, seconds_left: float, sense_actions: List[Square], move_actions: List[chess.Move]) -> Square:
        # sense where our ally piece was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square

        # sense where we may capture an enemy piece
        future_move = self.choose_move(seconds_left, move_actions)
        if self.board.piece_at(future_move.to_square) is not None:
            return future_move.to_square

        # don't sense on a squares where our pieces are located
        for square, piece in self.board.piece_map():
            if piece.color == self.color:
                sense_actions.remove(square)

        # sense at a random square
        return random.choice(sense_actions)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def choose_move(self, seconds_left: float, move_actions: List[chess.Move]) -> Optional[chess.Move]:
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
        return random.choice(move_actions)

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        if taken_move is not None:
            self.board.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], game_history: GameHistory):
        pass
