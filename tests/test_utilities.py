import unittest
from rbmc import *
from chess import *
import random


class CastlingTestCase(unittest.TestCase):
    def test_legal_castle(self):
        board = Board()
        board.set_board_fen('8/8/8/8/8/8/8/R3K2R')
        self.assertTrue(is_psuedo_legal_castle(board, Move(E1, C1)))
        self.assertFalse(is_illegal_castle(board, Move(E1, C1)))
        self.assertTrue(is_psuedo_legal_castle(board, Move(E1, G1)))
        self.assertFalse(is_illegal_castle(board, Move(E1, G1)))

    def test_non_castle(self):
        board = Board()
        self.assertFalse(is_illegal_castle(board, Move(A2, A3)))
        self.assertFalse(is_psuedo_legal_castle(board, Move(A2, A3)))

    def test_queenside_castle_piece_between(self):
        board = Board()

        board.set_board_fen('8/8/8/8/8/8/8/R2pK2R')
        self.assertFalse(is_psuedo_legal_castle(board, Move(E1, C1)))
        self.assertTrue(is_illegal_castle(board, Move(E1, C1)))

        board.set_board_fen('8/8/8/8/8/8/8/R1p1K2R')
        self.assertFalse(is_psuedo_legal_castle(board, Move(E1, C1)))
        self.assertTrue(is_illegal_castle(board, Move(E1, C1)))

        board.set_board_fen('8/8/8/8/8/8/8/Rp2K2R')
        self.assertFalse(is_psuedo_legal_castle(board, Move(E1, C1)))
        self.assertTrue(is_illegal_castle(board, Move(E1, C1)))

    def test_kingside_castle_piece_between(self):
        board = Board()

        board.set_board_fen('8/8/8/8/8/8/8/R3Kp1R')
        self.assertFalse(is_psuedo_legal_castle(board, Move(E1, G1)))
        self.assertTrue(is_illegal_castle(board, Move(E1, G1)))

        board.set_board_fen('8/8/8/8/8/8/8/R3K1pR')
        self.assertFalse(is_psuedo_legal_castle(board, Move(E1, G1)))
        self.assertTrue(is_illegal_castle(board, Move(E1, G1)))

    def test_castle_no_rights(self):
        board = Board()
        board.set_board_fen('8/8/8/8/8/8/8/R3K2R')

        board.set_castling_fen('-')
        self.assertFalse(is_psuedo_legal_castle(board, Move(E1, G1)))
        self.assertTrue(is_illegal_castle(board, Move(E1, G1)))
        self.assertFalse(is_psuedo_legal_castle(board, Move(E1, C1)))
        self.assertTrue(is_illegal_castle(board, Move(E1, C1)))

        board.set_castling_fen('Q')
        self.assertFalse(is_psuedo_legal_castle(board, Move(E1, G1)))
        self.assertTrue(is_illegal_castle(board, Move(E1, G1)))
        self.assertTrue(is_psuedo_legal_castle(board, Move(E1, C1)))
        self.assertFalse(is_illegal_castle(board, Move(E1, C1)))

        board.set_castling_fen('K')
        self.assertTrue(is_psuedo_legal_castle(board, Move(E1, G1)))
        self.assertFalse(is_illegal_castle(board, Move(E1, G1)))
        self.assertFalse(is_psuedo_legal_castle(board, Move(E1, C1)))
        self.assertTrue(is_illegal_castle(board, Move(E1, C1)))

        board.set_castling_fen('KQ')
        self.assertTrue(is_psuedo_legal_castle(board, Move(E1, G1)))
        self.assertFalse(is_illegal_castle(board, Move(E1, G1)))
        self.assertTrue(is_psuedo_legal_castle(board, Move(E1, C1)))
        self.assertFalse(is_illegal_castle(board, Move(E1, C1)))

    def test_castling_into_check(self):
        board = Board()
        board.set_board_fen('8/8/8/8/6q1/8/8/4K2R')
        self.assertFalse(board.is_check())
        self.assertTrue(is_psuedo_legal_castle(board, Move(E1, G1)))
        self.assertFalse(is_illegal_castle(board, Move(E1, G1)))
        board.push(Move(E1, G1))
        board.turn = WHITE
        self.assertTrue(board.is_check())

    def test_castling_out_of_check(self):
        board = Board()
        board.set_board_fen('8/8/8/8/8/8/8/q3K2R')
        self.assertTrue(board.is_check())
        self.assertTrue(is_psuedo_legal_castle(board, Move(E1, G1)))
        self.assertFalse(is_illegal_castle(board, Move(E1, G1)))
        board.push(Move(E1, G1))
        board.turn = WHITE
        self.assertFalse(board.is_check())

    def test_castling_stay_in_check(self):
        board = Board()
        board.set_board_fen('8/8/8/8/8/6q1/8/4K2R')
        self.assertTrue(board.is_check())
        self.assertTrue(is_psuedo_legal_castle(board, Move(E1, G1)))
        self.assertFalse(is_illegal_castle(board, Move(E1, G1)))
        board.push(Move(E1, G1))
        board.turn = WHITE
        self.assertTrue(board.is_check())


class SlidingMoveTestCase(unittest.TestCase):
    def test_sliding_pawn(self):
        """Tests a pawn moving forwards 1 and 2 spaces through enemy pawns"""
        board = Board()

        board.set_board_fen('8/8/8/8/8/3p4/3P4/8')
        for to_square in [D2, D3, D4, D5, D6, D7, D8]:
            self.assertEqual(Move.null(), slide_move(board, Move(D2, to_square)))

        board.set_board_fen('8/8/8/8/3p4/8/3P4/8')
        self.assertEqual(Move(D2, D3), slide_move(board, Move(D2, D3)))
        self.assertEqual(Move(D2, D3), slide_move(board, Move(D2, D4)))
        self.assertEqual(Move(D2, D3), slide_move(board, Move(D2, D5)))

        board.set_board_fen('8/8/8/3p4/8/8/3P4/8')
        self.assertEqual(Move(D2, D3), slide_move(board, Move(D2, D3)))
        self.assertEqual(Move(D2, D4), slide_move(board, Move(D2, D4)))
        self.assertEqual(Move(D2, D4), slide_move(board, Move(D2, D5)))

        board.set_board_fen('8/8/3p4/8/8/8/3P4/8')
        self.assertEqual(Move(D2, D3), slide_move(board, Move(D2, D3)))
        self.assertEqual(Move(D2, D4), slide_move(board, Move(D2, D4)))
        self.assertEqual(Move(D2, D4), slide_move(board, Move(D2, D5)))
        self.assertEqual(Move(D2, D4), slide_move(board, Move(D2, D6)))

    def test_sliding_straight_captures(self, piece_type=ROOK):
        """Tests a rook moving through enemy pieces and capturing them"""
        board = Board()

        moves = [Move(D5, C5), Move(D5, B5), Move(D5, A5), Move(D5, D6), Move(D5, D7), Move(D5, D8), Move(D5, E5),
                 Move(D5, F5), Move(D5, G5), Move(D5, H5), Move(D5, D4), Move(D5, D3), Move(D5, D2), Move(D5, D1)]

        board.set_board_fen('8/8/3p4/2pRp3/8/8/8/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C5), Move(D5, C5), Move(D5, C5), Move(D5, D6), Move(D5, D6), Move(D5, D6), Move(D5, E5),
                   Move(D5, E5), Move(D5, E5), Move(D5, E5), Move(D5, D4), Move(D5, D3), Move(D5, D2), Move(D5, D1)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('8/3p4/8/1p1R1p2/8/8/8/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C5), Move(D5, B5), Move(D5, B5), Move(D5, D6), Move(D5, D7), Move(D5, D7), Move(D5, E5),
                   Move(D5, F5), Move(D5, F5), Move(D5, F5), Move(D5, D4), Move(D5, D3), Move(D5, D2), Move(D5, D1)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('3p4/8/8/p2R2p1/8/8/8/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C5), Move(D5, B5), Move(D5, A5), Move(D5, D6), Move(D5, D7), Move(D5, D8), Move(D5, E5),
                   Move(D5, F5), Move(D5, G5), Move(D5, G5), Move(D5, D4), Move(D5, D3), Move(D5, D2), Move(D5, D1)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('8/8/8/3R3p/8/8/8/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C5), Move(D5, B5), Move(D5, A5), Move(D5, D6), Move(D5, D7), Move(D5, D8), Move(D5, E5),
                   Move(D5, F5), Move(D5, G5), Move(D5, H5), Move(D5, D4), Move(D5, D3), Move(D5, D2), Move(D5, D1)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('8/8/8/3R4/8/8/8/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C5), Move(D5, B5), Move(D5, A5), Move(D5, D6), Move(D5, D7), Move(D5, D8), Move(D5, E5),
                   Move(D5, F5), Move(D5, G5), Move(D5, H5), Move(D5, D4), Move(D5, D3), Move(D5, D2), Move(D5, D1)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

    def test_sliding_straight_allies(self, piece_type=ROOK):
        """Tests a rook moving through a ally piece"""
        board = Board()

        moves = [Move(A1, A2), Move(A1, A3), Move(A1, A4), Move(A1, A5), Move(A1, A6), Move(A1, A7), Move(A1, A8),
                 Move(A1, B1), Move(A1, C1), Move(A1, D1), Move(A1, E1), Move(A1, F1), Move(A1, G1), Move(A1, H1)]

        board.set_board_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        board.set_piece_at(A1, Piece(piece_type, WHITE))
        results = [Move.null(), Move.null(), Move.null(), Move.null(), Move.null(), Move.null(), Move.null(),
                   Move.null(), Move.null(), Move.null(), Move.null(), Move.null(), Move.null(), Move.null()]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR')
        board.set_piece_at(A1, Piece(piece_type, WHITE))
        results = [Move(A1, A2), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3),
                   Move.null(), Move.null(), Move.null(), Move.null(), Move.null(), Move.null(), Move.null()]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('rnbqkbnr/pppppppp/8/8/P7/2N5/1PPPPPPP/R1BQKBNR')
        board.set_piece_at(A1, Piece(piece_type, WHITE))
        results = [Move(A1, A2), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3),
                   Move(A1, B1), Move(A1, B1), Move(A1, B1), Move(A1, B1), Move(A1, B1), Move(A1, B1), Move(A1, B1)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('rnbqkbnr/pppppppp/8/8/P7/2NP4/1PPBPPPP/R2QKBNR')
        board.set_piece_at(A1, Piece(piece_type, WHITE))
        results = [Move(A1, A2), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3),
                   Move(A1, B1), Move(A1, C1), Move(A1, C1), Move(A1, C1), Move(A1, C1), Move(A1, C1), Move(A1, C1)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('rnbqkbnr/pppppppp/8/8/P7/2NPPN2/1PPBKPPP/R2Q1B1R')
        board.set_piece_at(A1, Piece(piece_type, WHITE))
        results = [Move(A1, A2), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3), Move(A1, A3),
                   Move(A1, B1), Move(A1, C1), Move(A1, C1), Move(A1, C1), Move(A1, C1), Move(A1, C1), Move(A1, C1)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

    def test_sliding_diagonal_captures(self, piece_type=BISHOP):
        """Tests moving a bishop diagonally through enemy pieces and capturing them"""
        board = Board()

        moves = [Move(D5, C6), Move(D5, B7), Move(D5, A8), Move(D5, E6), Move(D5, F7), Move(D5, G8),
                 Move(D5, E4), Move(D5, F3), Move(D5, G2), Move(D5, C4), Move(D5, B3), Move(D5, A2)]

        board.set_board_fen('8/8/2p1p3/3B4/2p1p3/8/8/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C6), Move(D5, C6), Move(D5, C6), Move(D5, E6), Move(D5, E6), Move(D5, E6),
                   Move(D5, E4), Move(D5, E4), Move(D5, E4), Move(D5, C4), Move(D5, C4), Move(D5, C4)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('8/1p3p2/8/3B4/8/1p3p2/8/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C6), Move(D5, B7), Move(D5, B7), Move(D5, E6), Move(D5, F7), Move(D5, F7),
                   Move(D5, E4), Move(D5, F3), Move(D5, F3), Move(D5, C4), Move(D5, B3), Move(D5, B3)]

        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('p5p1/8/8/3B4/8/8/p5p1/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C6), Move(D5, B7), Move(D5, A8), Move(D5, E6), Move(D5, F7), Move(D5, G8),
                   Move(D5, E4), Move(D5, F3), Move(D5, G2), Move(D5, C4), Move(D5, B3), Move(D5, A2)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('8/8/8/3B4/8/8/8/7p')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C6), Move(D5, B7), Move(D5, A8), Move(D5, E6), Move(D5, F7), Move(D5, G8),
                   Move(D5, E4), Move(D5, F3), Move(D5, G2), Move(D5, C4), Move(D5, B3), Move(D5, A2)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

    def test_sliding_diagonal_allies(self, piece_type=BISHOP):
        """Tests moving a bishop diagonally through allies and stopping before them"""
        board = Board()

        moves = [Move(D5, C6), Move(D5, B7), Move(D5, A8), Move(D5, E6), Move(D5, F7), Move(D5, G8),
                 Move(D5, E4), Move(D5, F3), Move(D5, G2), Move(D5, C4), Move(D5, B3), Move(D5, A2)]

        board.set_board_fen('8/8/2P1P3/3B4/2P1P3/8/8/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move.null(), Move.null(), Move.null(), Move.null(), Move.null(), Move.null(),
                   Move.null(), Move.null(), Move.null(), Move.null(), Move.null(), Move.null()]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('8/1P3P2/8/3B4/8/1P3P2/8/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C6), Move(D5, C6), Move(D5, C6), Move(D5, E6), Move(D5, E6), Move(D5, E6),
                   Move(D5, E4), Move(D5, E4), Move(D5, E4), Move(D5, C4), Move(D5, C4), Move(D5, C4)]

        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('P5P1/8/8/3B4/8/8/P5P1/8')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C6), Move(D5, B7), Move(D5, B7), Move(D5, E6), Move(D5, F7), Move(D5, F7),
                   Move(D5, E4), Move(D5, F3), Move(D5, F3), Move(D5, C4), Move(D5, B3), Move(D5, B3)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

        board.set_board_fen('8/8/8/3B4/8/8/8/7P')
        board.set_piece_at(D5, Piece(piece_type, WHITE))
        results = [Move(D5, C6), Move(D5, B7), Move(D5, A8), Move(D5, E6), Move(D5, F7), Move(D5, G8),
                   Move(D5, E4), Move(D5, F3), Move(D5, G2), Move(D5, C4), Move(D5, B3), Move(D5, A2)]
        self.assertEqual(results, list(map(lambda m: slide_move(board, m), moves)))

    def test_sliding_queen_allies(self):
        """Tests queens sliding through allies and stopping before them"""
        self.test_sliding_straight_allies(piece_type=QUEEN)
        self.test_sliding_diagonal_allies(piece_type=QUEEN)

    def test_sliding_queen_captures(self):
        """Tests sliding queen through enemies and capturing them"""
        self.test_sliding_straight_captures(piece_type=QUEEN)
        self.test_sliding_diagonal_captures(piece_type=QUEEN)


class CaptureSquareTestCase(unittest.TestCase):
    def test_white_en_passant(self):
        board = Board()
        board.set_board_fen('rnbqkbnr/pppppppp/8/1P6/8/8/P1PPPPPP/RNBQKBNR')
        board.turn = BLACK
        board.push(Move(A7, A5))
        self.assertEqual(capture_square_of_move(board, Move(B5, A6)), A5)

    def test_black_en_passant(self):
        board = Board()
        board.set_board_fen('rnbqkbnr/p1pppppp/8/8/1p6/8/PPPPPPPP/RNBQKBNR')
        board.turn = WHITE
        board.push(Move(A2, A4))
        self.assertEqual(capture_square_of_move(board, Move(B4, A3)), A4)

    def test_fuzz_capture(self, max_turns=500):
        board = Board()
        turn = 1
        while not board.is_game_over() and turn < max_turns:
            move = random.choice(list(board.generate_pseudo_legal_moves()))
            if board.is_en_passant(move):
                self.assertNotEqual(capture_square_of_move(board, move), move.to_square)
            elif board.is_capture(move):
                self.assertEqual(capture_square_of_move(board, move), move.to_square)
            else:
                self.assertEqual(capture_square_of_move(board, move), None)

            board.push(move)
            turn += 1


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
