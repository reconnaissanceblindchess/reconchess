import chess.engine
import random
from reconchess import *
import os

class DJBoy(Player):

	# GENERAL STRATEGY:

	# - Each piece has a score; Ally pieces are negative score
	# - Count each captured piece as the game 'score'
	# - Dynamically minimax to figure out best moves
	# - Dynamically populate list of instakill movesets

	# TODO:
	# - How should we go about sensing?


	def __init__(self):
        self.board = None
        self.color = None
        self.my_piece_captured_square = None

    def handle_game_start(self, color: Color, board: chess.Board):
        self.board = color
        self.color = board

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        pass

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

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
    	# Attempt to take king if available
    	# if we might be able to take the king, try to
        enemy_king_square = self.board.king(not self.color)
        if enemy_king_square:
            # if there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                return chess.Move(attacker_square, enemy_king_square)

        # else make the best possible move
        # NOT IMPLEMENTED YET

    # don't change
    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # if a move was executed, apply it to our board
        if taken_move is not None:
            self.board.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        pass