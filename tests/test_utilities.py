import unittest
from rbmc import without_opponent_pieces, pawn_capture_moves_on
from chess import *
import random


class NoOpponentsPiecesTestCase(unittest.TestCase):
    def test_white(self, board=Board()):
        board.turn = WHITE
        no_opponents_board = without_opponent_pieces(board)
        for piece_type in PIECE_TYPES:
            self.assertEqual(board.pieces(piece_type, WHITE), no_opponents_board.pieces(piece_type, WHITE))
            self.assertEqual(SquareSet(), no_opponents_board.pieces(piece_type, BLACK))

    def test_black(self, board=Board()):
        board.turn = BLACK
        no_opponents_board = without_opponent_pieces(board)
        for piece_type in PIECE_TYPES:
            self.assertEqual(board.pieces(piece_type, BLACK), no_opponents_board.pieces(piece_type, BLACK))
            self.assertEqual(SquareSet(), no_opponents_board.pieces(piece_type, WHITE))

    def test_fuzz(self, turns=500):
        board = Board()
        turn = 1
        while not board.is_game_over() and turn < turns:
            if board.turn == WHITE:
                self.test_white(board)
            else:
                self.test_black(board)
            board.push(random.choice(list(board.generate_legal_moves())))
            turn += 1


class PawnCaptureMovesTestCase(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.board.set_board_fen('rnbq1bnr/3k1P1P/1ppPp1p1/p2p1p1p/PPP1P1P1/8/8/RNBQKBNR')

    def test_white_moves(self):
        moves = set(pawn_capture_moves_on(self.board))
        expected = {Move(A4, B5), Move(B4, A5), Move(B4, C5), Move(C4, B5), Move(C4, D5),
                    Move(D6, C7), Move(D6, E7), Move(E4, D5), Move(E4, F5), Move(G4, F5), Move(G4, H5),
                    Move(F7, E8), Move(F7, E8, ROOK), Move(F7, E8, KNIGHT), Move(F7, E8, BISHOP), Move(F7, E8, QUEEN),
                    Move(F7, G8), Move(F7, G8, ROOK), Move(F7, G8, KNIGHT), Move(F7, G8, BISHOP), Move(F7, G8, QUEEN),
                    Move(H7, G8), Move(H7, G8, ROOK), Move(H7, G8, KNIGHT), Move(H7, G8, BISHOP), Move(H7, G8, QUEEN)}
        self.assertSetEqual(moves, expected)

    def test_black_moves(self):
        self.board.turn = BLACK
        moves = set(pawn_capture_moves_on(self.board))
        expected = {Move(A5, B4), Move(B6, C5), Move(C6, B5), Move(D5, C4), Move(D5, E4),
                    Move(F5, E4), Move(F5, G4), Move(H5, G4)}
        self.assertSetEqual(moves, expected)
