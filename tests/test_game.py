import unittest
from reconchess import LocalGame, WinReason
from chess import *
import time
import random

SENSE_BY_SQUARE = {
    A8: [A8, B8, A7, B7],
    B8: [A8, B8, C8, A7, B7, C7],
    C8: [B8, C8, D8, B7, C7, D7],
    D8: [C8, D8, E8, C7, D7, E7],
    E8: [D8, E8, F8, D7, E7, F7],
    F8: [E8, F8, G8, E7, F7, G7],
    G8: [F8, G8, H8, F7, G7, H7],
    H8: [G8, H8, G7, H7],

    A7: [A8, B8, A7, B7, A6, B6],
    B7: [A8, B8, C8, A7, B7, C7, A6, B6, C6],
    C7: [B8, C8, D8, B7, C7, D7, B6, C6, D6],
    D7: [C8, D8, E8, C7, D7, E7, C6, D6, E6],
    E7: [D8, E8, F8, D7, E7, F7, D6, E6, F6],
    F7: [E8, F8, G8, E7, F7, G7, E6, F6, G6],
    G7: [F8, G8, H8, F7, G7, H7, F6, G6, H6],
    H7: [G8, H8, G7, H7, G6, H6],

    A6: [A7, B7, A6, B6, A5, B5],
    B6: [A7, B7, C7, A6, B6, C6, A5, B5, C5],
    C6: [B7, C7, D7, B6, C6, D6, B5, C5, D5],
    D6: [C7, D7, E7, C6, D6, E6, C5, D5, E5],
    E6: [D7, E7, F7, D6, E6, F6, D5, E5, F5],
    F6: [E7, F7, G7, E6, F6, G6, E5, F5, G5],
    G6: [F7, G7, H7, F6, G6, H6, F5, G5, H5],
    H6: [G7, H7, G6, H6, G5, H5],

    A5: [A6, B6, A5, B5, A4, B4],
    B5: [A6, B6, C6, A5, B5, C5, A4, B4, C4],
    C5: [B6, C6, D6, B5, C5, D5, B4, C4, D4],
    D5: [C6, D6, E6, C5, D5, E5, C4, D4, E4],
    E5: [D6, E6, F6, D5, E5, F5, D4, E4, F4],
    F5: [E6, F6, G6, E5, F5, G5, E4, F4, G4],
    G5: [F6, G6, H6, F5, G5, H5, F4, G4, H4],
    H5: [G6, H6, G5, H5, G4, H4],

    A4: [A5, B5, A4, B4, A3, B3],
    B4: [A5, B5, C5, A4, B4, C4, A3, B3, C3],
    C4: [B5, C5, D5, B4, C4, D4, B3, C3, D3],
    D4: [C5, D5, E5, C4, D4, E4, C3, D3, E3],
    E4: [D5, E5, F5, D4, E4, F4, D3, E3, F3],
    F4: [E5, F5, G5, E4, F4, G4, E3, F3, G3],
    G4: [F5, G5, H5, F4, G4, H4, F3, G3, H3],
    H4: [G5, H5, G4, H4, G3, H3],

    A3: [A4, B4, A3, B3, A2, B2],
    B3: [A4, B4, C4, A3, B3, C3, A2, B2, C2],
    C3: [B4, C4, D4, B3, C3, D3, B2, C2, D2],
    D3: [C4, D4, E4, C3, D3, E3, C2, D2, E2],
    E3: [D4, E4, F4, D3, E3, F3, D2, E2, F2],
    F3: [E4, F4, G4, E3, F3, G3, E2, F2, G2],
    G3: [F4, G4, H4, F3, G3, H3, F2, G2, H2],
    H3: [G4, H4, G3, H3, G2, H2],

    A2: [A3, B3, A2, B2, A1, B1],
    B2: [A3, B3, C3, A2, B2, C2, A1, B1, C1],
    C2: [B3, C3, D3, B2, C2, D2, B1, C1, D1],
    D2: [C3, D3, E3, C2, D2, E2, C1, D1, E1],
    E2: [D3, E3, F3, D2, E2, F2, D1, E1, F1],
    F2: [E3, F3, G3, E2, F2, G2, E1, F1, G1],
    G2: [F3, G3, H3, F2, G2, H2, F1, G1, H1],
    H2: [G3, H3, G2, H2, G1, H1],

    A1: [A2, B2, A1, B1],
    B1: [A2, B2, C2, A1, B1, C1],
    C1: [B2, C2, D2, B1, C1, D1],
    D1: [C2, D2, E2, C1, D1, E1],
    E1: [D2, E2, F2, D1, E1, F1],
    F1: [E2, F2, G2, E1, F1, G1],
    G1: [F2, G2, H2, F1, G1, H1],
    H1: [G2, H2, G1, H1],
}


class LocalGameSenseTest(unittest.TestCase):
    def setUp(self):
        self.game = LocalGame()

    def test_senses_actions_content(self):
        sense_actions = self.game.sense_actions()

        for square in SQUARES:
            self.assertIn(square, sense_actions)

    def test_sense_invalid(self):
        for square in [-1, 65, 66, 1023730, -2]:
            with self.assertRaises(ValueError):
                self.game.sense(square)

    def test_sense_squares(self):
        for square in SQUARES:
            sense_result = self.game.sense(square)
            squares = [s for s, p in sense_result]
            self.assertEqual(squares, SENSE_BY_SQUARE[square])

    def test_sense_pieces(self):
        for sense_square in SQUARES:
            sense_result = self.game.sense(sense_square)
            for square, piece in sense_result:
                self.assertEqual(piece, self.game.board.piece_at(square))

    def test_sense_pass(self):
        sense_result = self.game.sense(None)
        self.assertEqual(sense_result, [])


class LocalGameTimeTest(unittest.TestCase):
    def test_time(self, seconds=1, turns=20, phases=3):
        delta = seconds / (turns * phases)

        game = LocalGame(seconds_per_player=seconds)

        turn = True
        time_by_color = game.seconds_left_by_color.copy()

        game.start()
        for i in range(turns):
            for _ in range(phases):
                start = game.get_seconds_left()
                time.sleep(delta)
                end = game.get_seconds_left()

                self.assertAlmostEqual(start - end, delta, places=2)

            time_by_color[turn] = game.get_seconds_left()
            turn = not turn
            game.end_turn()
            self.assertAlmostEqual(game.get_seconds_left(), time_by_color[turn], places=2)
        game.end()
        self.assertAlmostEqual(game.get_seconds_left(), time_by_color[turn], places=2)
        time.sleep(delta)
        self.assertAlmostEqual(game.get_seconds_left(), time_by_color[turn], places=2)


class LocalGameMoveActionsTest(unittest.TestCase):
    STARTING_WHITE_PAWN_CAPTURES = [
        Move(A2, B3),
        Move(B2, A3), Move(B2, C3),
        Move(C2, B3), Move(C2, D3),
        Move(D2, C3), Move(D2, E3),
        Move(E2, D3), Move(E2, F3),
        Move(F2, E3), Move(F2, G3),
        Move(G2, F3), Move(G2, H3),
        Move(H2, G3),
    ]
    BLACK_STARTING_PAWN_CAPTURES = [
        Move(A7, B6),
        Move(B7, A6), Move(B7, C6),
        Move(C7, B6), Move(C7, D6),
        Move(D7, C6), Move(D7, E6),
        Move(E7, D6), Move(E7, F6),
        Move(F7, E6), Move(F7, G6),
        Move(G7, F6), Move(G7, H6),
        Move(H7, G6),
    ]

    def setUp(self):
        self.game = LocalGame()

    def test_starting_pawn_capture_moves(self):
        move_actions = self.game.move_actions()
        for move in self.STARTING_WHITE_PAWN_CAPTURES:
            self.assertIn(move, move_actions)
        self.game.board.turn = BLACK
        move_actions = self.game.move_actions()
        for move in self.BLACK_STARTING_PAWN_CAPTURES:
            self.assertIn(move, move_actions)

    def test_pass(self):
        self.assertNotIn(None, self.game.move_actions())
        self.assertNotIn(Move.null(), self.game.move_actions())

    def test_superset_fuzz(self, max_turns=500):
        turn = 1
        while not self.game.board.is_game_over() and turn < max_turns:
            truth_moves = set(self.game.board.generate_pseudo_legal_moves())
            recon_moves = set(self.game.move_actions())
            self.assertTrue(recon_moves.issuperset(truth_moves))

            self.game.board.push(random.sample(truth_moves, 1)[0])
            turn += 1


class LocalGameMoveTest(unittest.TestCase):
    def setUp(self):
        self.game = LocalGame()

    def test_legal_kingside_castle(self):
        """
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        R . . . K . . R
        """
        self.game.board.set_board_fen('8/8/8/8/8/8/8/R3K2R')
        self.game.board.set_castling_fen('KQkq')
        req, taken, opt_capture = self.game.move(Move(E1, G1))
        self.assertEqual(req, taken)
        self.assertIsNone(opt_capture)
        self.assertEqual(self.game.board.board_fen(), '8/8/8/8/8/8/8/R4RK1')

    def test_legal_queenside_castle(self):
        """
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        R . . . K . . R
        """
        self.game.board.set_board_fen('8/8/8/8/8/8/8/R3K2R')
        self.game.board.set_castling_fen('KQkq')
        req, taken, opt_capture = self.game.move(Move(E1, C1))
        self.assertEqual(req, taken)
        self.assertIsNone(opt_capture)
        self.assertEqual(self.game.board.board_fen(), '8/8/8/8/8/8/8/2KR3R')

    def test_queenside_castle_piece_between(self):
        """
        r . P . k b n r     r . . P k b n r     r P . . k b n r
        p p . p p p p p     p p . p p p p p     p p . p p p p p
        . . . . . . . .     . . . . . . . .     . . . . . . . .
        . . . . . . . .     . . . . . . . .     . . . . . . . .
        . . . . . . . .     . . . . . . . .     . . . . . . . .
        . . . . . . . .     . . . . . . . .     . . . . . . . .
        P P . P P P P P     P P . P P P P P     P P . P P P P P
        R . p . K B N R     R . . p K B N R     R p . . K B N R
        """

        for fen in ['r1P1kbnr/pp1ppppp/8/8/8/8/PP1PPPPP/R1p1KBNR',
                    'r2Pkbnr/pp1ppppp/8/8/8/8/PP1PPPPP/R2pKBNR',
                    'rP2kbnr/pp1ppppp/8/8/8/8/PP1PPPPP/Rp2KBNR']:
            self.game.board.set_board_fen(fen)
            self.game.board.turn = WHITE
            self.game.turn = WHITE
            req, tak, opt_capture = self.game.move(Move(E1, C1))
            self.assertEqual(tak, None)

            self.game.board.turn = BLACK
            self.game.turn = BLACK
            req, tak, opt_capture = self.game.move(Move(E8, C8))
            self.assertEqual(tak, None)

    def test_kingside_castle_piece_between(self):
        """
        r n b q k P . r     r n b q k . P r
        p p p p p . p p     p p p p p . p p
        . . . . . . . .     . . . . . . . .
        . . . . . . . .     . . . . . . . .
        . . . . . . . .     . . . . . . . .
        . . . . . . . .     . . . . . . . .
        P P P P P . P P     P P P P P . P P
        R N B Q K p . R     R N B Q K . p R
        :return:
        """
        for fen in ['rnbqkP1r/ppppp1pp/8/8/8/8/PPPPP1PP/RNBQKp1R',
                    'rnbqk1Pr/ppppp1pp/8/8/8/8/PPPPP1PP/RNBQK1pR']:
            self.game.board.set_board_fen(fen)
            self.game.board.turn = WHITE
            self.game.turn = WHITE
            req, tak, opt_capture = self.game.move(Move(E1, G1))
            self.assertEqual(tak, None)

            self.game.board.turn = BLACK
            self.game.turn = BLACK
            req, tak, opt_capture = self.game.move(Move(E8, G8))
            self.assertEqual(tak, None)

    def test_queenside_castle_no_rights(self):
        """
        r . . . k . . r
        p p p p p p p p
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        P P P P P P P P
        R . . . K . . R
        """
        self.game.board.set_board_fen('r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R')

        self.game.board.turn = WHITE
        self.game.turn = WHITE
        for castling_fen in ['-', 'k', 'q', 'kq', 'Kk', 'Kq', 'Kkq']:
            self.game.board.set_castling_fen(castling_fen)
            with self.assertRaises(ValueError):
                self.game.move(Move(E1, C1))

        self.game.board.turn = BLACK
        self.game.turn = BLACK
        for castling_fen in ['-', 'K', 'Q', 'KQ', 'Kk', 'Qk', 'KQk']:
            self.game.board.set_castling_fen(castling_fen)
            with self.assertRaises(ValueError):
                self.game.move(Move(E8, C8))

    def test_kingside_castle_no_rights(self):
        """
        r . . . k . . r
        p p p p p p p p
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        P P P P P P P P
        R . . . K . . R
        """
        self.game.board.set_board_fen('r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R')

        self.game.board.turn = WHITE
        self.game.turn = WHITE
        for castling_fen in ['-', 'k', 'q', 'kq', 'Qk', 'Qq', 'Qkq']:
            self.game.board.set_castling_fen(castling_fen)
            with self.assertRaises(ValueError):
                self.game.move(Move(E1, G1))

        self.game.board.turn = BLACK
        self.game.turn = BLACK
        for castling_fen in ['-', 'K', 'Q', 'KQ', 'Kq', 'Qq', 'KQq']:
            self.game.board.set_castling_fen(castling_fen)
            with self.assertRaises(ValueError):
                self.game.move(Move(E8, G8))

    def test_castling_into_check(self):
        """
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . q .
        . . . . . . . .
        . . . . . . . .
        . . . . K . . R
        """
        self.game.board.set_board_fen('8/8/8/8/6q1/8/8/4K2R')
        self.assertFalse(self.game.board.is_check())
        move = Move(E1, G1)
        req, taken, opt_capture = self.game.move(move)
        self.assertEqual(req, taken)
        self.assertIsNone(opt_capture)
        self.game.board.turn = WHITE
        self.assertTrue(self.game.board.is_check())

    def test_castling_out_of_check(self):
        """
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        q . . . K . . R
        """
        self.game.board.set_board_fen('8/8/8/8/8/8/8/q3K2R')
        self.assertTrue(self.game.board.is_check())
        move = Move(E1, G1)
        req, taken, opt_capture = self.game.move(move)
        self.assertEqual(req, taken)
        self.assertIsNone(opt_capture)
        self.game.board.turn = WHITE
        self.assertFalse(self.game.board.is_check())

    def test_castling_stay_in_check(self):
        """
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . q .
        . . . . . . . .
        . . . . K . . R
        """
        self.game.board.set_board_fen('8/8/8/8/8/6q1/8/4K2R')
        self.assertTrue(self.game.board.is_check())
        move = Move(E1, G1)
        req, taken, opt_capture = self.game.move(move)
        self.assertEqual(req, taken)
        self.assertIsNone(opt_capture)
        self.game.board.turn = WHITE
        self.assertTrue(self.game.board.is_check())

    def test_en_passant_white(self):
        """
        r n b q k b n r
        p . p p p p p p
        . . . . . . . .
        . . . . . . . .
        P p . . . . . .
        . . . . . . . .
        . P P P P P P P
        R N B Q K B N R
        """
        # test that en passant captures result in the correct capture square
        self.game.board.set_board_fen('rnbqkbnr/p1pppppp/8/8/1p6/8/PPPPPPPP/RNBQKBNR')

        req, taken, opt_capture = self.game.move(Move(A2, A4))
        self.assertEqual(req, taken)
        self.assertIsNone(opt_capture)

        req, taken, opt_capture = self.game.move(Move(B4, A3))
        self.assertEqual(req, taken)
        self.assertIsNotNone(opt_capture)
        self.assertEqual(opt_capture, A4)

    def test_en_passant_black(self):
        """
        r n b q k b n r
        p p p p p . p p
        . . . . . . . .
        . . . . . p P .
        . . . . . . . .
        . . . . . . . .
        P P P P P P . P
        R N B Q K B N R
        """
        # test that en passant captures result in the correct capture square
        self.game.board.set_board_fen('rnbqkbnr/pppppppp/8/6P1/8/8/PPPPPP1P/RNBQKBNR')
        self.game.turn = BLACK
        self.game.board.turn = BLACK

        req, taken, opt_capture = self.game.move(Move(F7, F5))
        self.assertEqual(req, taken)
        self.assertIsNone(opt_capture)

        req, taken, opt_capture = self.game.move(Move(G5, F6))
        self.assertEqual(req, taken)
        self.assertIsNotNone(opt_capture)
        self.assertEqual(opt_capture, F5)

    def test_move_opponent_piece(self):
        # test moving opponent pieces
        b = Board()
        b.turn = BLACK

        for move in b.generate_pseudo_legal_moves():
            with self.assertRaises(ValueError):
                self.game.move(move)

    def test_move_no_piece(self):
        # test a move from a square with no piece
        for from_square in SquareSet(BB_RANK_3 | BB_RANK_4 | BB_RANK_5 | BB_RANK_6):
            for to_square in SQUARES:
                with self.assertRaises(ValueError):
                    m = Move(from_square, to_square)
                    self.game.move(m)

    def test_move_illegal(self):
        for from_square in SquareSet(BB_RANK_1 | BB_RANK_2):
            for to_square in SQUARES:
                move = Move(from_square, to_square)
                if move not in self.game.move_actions():
                    with self.assertRaises(ValueError):
                        self.game.move(move)

    def test_sliding_straight_capture(self):
        """
        . . . . . . . .
        . . . p . . . .
        . . . . . . . .
        . p . R . p . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        """

        result_by_move = {
            Move(D5, C5): (Move(D5, C5), None),
            Move(D5, B5): (Move(D5, B5), B5),
            Move(D5, A5): (Move(D5, B5), B5),
            Move(D5, D6): (Move(D5, D6), None),
            Move(D5, D7): (Move(D5, D7), D7),
            Move(D5, D8): (Move(D5, D7), D7),
            Move(D5, E5): (Move(D5, E5), None),
            Move(D5, F5): (Move(D5, F5), F5),
            Move(D5, G5): (Move(D5, F5), F5),
            Move(D5, H5): (Move(D5, F5), F5),
            Move(D5, D4): (Move(D5, D4), None),
            Move(D5, D3): (Move(D5, D3), None),
            Move(D5, D2): (Move(D5, D2), None),
            Move(D5, D1): (Move(D5, D1), None),
        }
        for expected_req, (expected_taken, expected_capture) in result_by_move.items():
            self.game.board.set_board_fen('8/3p4/8/1p1R1p2/8/8/8/8')
            self.game.board.turn = WHITE
            self.game.turn = WHITE
            req, taken, opt_capture = self.game.move(expected_req)
            self.assertEqual(req, expected_req)
            self.assertEqual(taken, expected_taken)
            self.assertEqual(opt_capture, expected_capture)

    def test_sliding_straight_into_ally(self):
        """
        . . . . . . . .
        . . . p . . . .
        . . . . . . . .
        . p . R . p . .
        . . . . . . . .
        . . . . . . . .
        . . . P . . . .
        . . . . . . . .
        """
        for move in [Move(D5, D2), Move(D5, D1)]:
            self.game.board.set_board_fen('8/3p4/8/1p1R1p2/8/8/3P4/8')
            self.game.board.turn = WHITE
            self.game.turn = WHITE
            with self.assertRaises(ValueError):
                req, taken, opt_capture = self.game.move(move)

    def test_sliding_diagonal_capture(self):
        """
        p . . . . . p .
        . . . . . . . .
        . . . . . . . .
        . . . X . . . .
        . . . . . . . .
        . . . . . . . .
        p . . . . . p .
        . . . . . . . .
        """
        result_by_move = {
            Move(D5, C6): (Move(D5, C6), None),
            Move(D5, B7): (Move(D5, B7), None),
            Move(D5, A8): (Move(D5, A8), A8),
            Move(D5, E6): (Move(D5, E6), None),
            Move(D5, F7): (Move(D5, F7), None),
            Move(D5, G8): (Move(D5, G8), G8),
            Move(D5, E4): (Move(D5, E4), None),
            Move(D5, F3): (Move(D5, F3), None),
            Move(D5, G2): (Move(D5, G2), G2),
            Move(D5, H1): (Move(D5, G2), G2),
            Move(D5, C4): (Move(D5, C4), None),
            Move(D5, B3): (Move(D5, B3), None),
            Move(D5, A2): (Move(D5, A2), A2),
        }

        for expected_req, (expected_taken, expected_capture) in result_by_move.items():
            self.game.board.set_board_fen('p5p1/8/8/3B4/8/8/p5p1/8')
            self.game.board.turn = WHITE
            self.game.turn = WHITE
            req, taken, opt_capture = self.game.move(expected_req)
            self.assertEqual(req, expected_req)
            self.assertEqual(taken, expected_taken)
            self.assertEqual(opt_capture, expected_capture)

    def test_sliding_diagonal_into_ally(self):
        """
        p . . . . . p .
        . . . . . . . .
        . . . . . . . .
        . . . X . . . .
        . . . . . . . .
        . . . . . . . .
        p . . . . . P .
        . . . . . . . .
        """
        for move in [Move(D5, G2), Move(D5, H1)]:
            self.game.board.set_board_fen('p5p1/8/8/3B4/8/8/p5P1/8')
            self.game.board.turn = WHITE
            self.game.turn = WHITE
            with self.assertRaises(ValueError):
                req, taken, opt_capture = self.game.move(move)

    def test_pawn_auto_promotion(self):
        """
        . . . . . . . .
        . . . P . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        """
        self.game.board.set_board_fen('8/3P4/8/8/8/8/8/8')
        req, taken, opt_capture = self.game.move(Move(D7, D8))
        self.assertEqual(Move(D7, D8), req)
        self.assertNotEqual(req, taken)
        self.assertEqual(req.to_square, taken.to_square)
        self.assertEqual(req.from_square, taken.from_square)
        self.assertIsNone(req.promotion)
        self.assertEqual(taken.promotion, QUEEN)

    def test_pass(self):
        req, taken, opt_capture = self.game.move(None)
        self.assertEqual(req, None)
        self.assertEqual(taken, None)
        self.assertIsNone(opt_capture)

        self.game.board.turn = BLACK
        req, taken, opt_capture = self.game.move(None)
        self.assertEqual(req, None)
        self.assertEqual(taken, None)
        self.assertIsNone(opt_capture)

        self.game.board.turn = WHITE
        self.game.board.remove_piece_at(0)
        req, taken, opt_capture = self.game.move(None)
        self.assertEqual(req, None)
        self.assertEqual(taken, None)
        self.assertIsNone(opt_capture)

    def test_legal_fuzz(self, max_turns=500):
        board = Board()

        turn = 1
        while not board.is_game_over() and turn < max_turns:
            move = random.choice(list(board.generate_pseudo_legal_moves()) + [None])

            req, taken, opt_square = self.game.move(move)
            self.assertEqual(req, taken)
            if move is not None and board.is_capture(move):
                self.assertIsNotNone(opt_square)

            board.push(move if move is not None else Move.null())
            self.assertEqual(self.game.board, board)

            turn += 1


class OpponentMoveResultsTestCase(unittest.TestCase):
    def test_no_capture(self):
        game = LocalGame()
        game.start()
        _, _, result1 = game.move(Move(A2, A4))
        self.assertIsNone(result1)
        self.assertEqual(result1, game.opponent_move_results())
        game.end_turn()
        self.assertEqual(result1, game.opponent_move_results())
        game.sense(E5)
        self.assertEqual(result1, game.opponent_move_results())
        _, _, result2 = game.move(Move(F7, F5))
        self.assertIsNone(result2)
        self.assertEqual(result2, game.opponent_move_results())

    def test_capture(self):
        """
        r n b q k b n r
        p p p . . p p p
        . . . . . . . .
        . . . p p . . .
        . . . P P . . .
        . . . . . . . .
        P P P . . P P P
        R N B Q K B N R
        """
        game = LocalGame()
        game.board.set_board_fen('rnbqkbnr/ppp2ppp/8/3pp3/3PP3/8/PPP2PPP/RNBQKBNR')
        game.start()

        _, _, result1 = game.move(Move(D4, E5))
        self.assertEqual(result1, E5)
        self.assertEqual(result1, game.opponent_move_results())
        game.end_turn()

        self.assertEqual(result1, game.opponent_move_results())
        game.sense(E5)
        self.assertEqual(result1, game.opponent_move_results())
        _, _, result2 = game.move(Move(D5, E4))
        self.assertEqual(result2, E4)
        self.assertEqual(result2, game.opponent_move_results())


class IsOverTest(unittest.TestCase):
    def test_not_over(self):
        game = LocalGame()
        game.start()
        self.assertFalse(game.is_over())

    def test_forced_over(self):
        game = LocalGame()
        game.start()
        self.assertFalse(game.is_over())
        game.end()
        self.assertTrue(game.is_over())

    def test_no_time_both(self):
        game = LocalGame(seconds_per_player=0)
        game.start()
        self.assertTrue(game.is_over())

    def test_no_time_white(self):
        game = LocalGame()
        game.seconds_left_by_color[WHITE] = 0
        game.start()
        self.assertTrue(game.is_over())

    def test_no_time_black(self):
        game = LocalGame()
        game.seconds_left_by_color[BLACK] = 0
        game.start()
        self.assertTrue(game.is_over())

    def test_expired_white(self):
        game = LocalGame()
        game.seconds_left_by_color[WHITE] = 0.5
        game.start()
        self.assertFalse(game.is_over())
        time.sleep(1)
        self.assertTrue(game.is_over())

    def test_expired_black(self):
        game = LocalGame()
        game.seconds_left_by_color[BLACK] = 0.5
        game.start()
        self.assertFalse(game.is_over())
        time.sleep(1)
        self.assertFalse(game.is_over())
        game.turn = BLACK
        self.assertTrue(game.is_over())

    def test_white_king_captured(self):
        """
        r n b q k b n r
        p p p p p p p p
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        P P P P P P P P
        R N B Q . B N R
        """
        game = LocalGame()
        game.board.set_board_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQ1BNR')
        game.start()
        self.assertTrue(game.is_over())

    def test_black_king_captured(self):
        """
        r n b q . b n r
        p p p p p p p p
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        P P P P P P P P
        R N B Q K B N R
        """
        game = LocalGame()
        game.board.set_board_fen('rnbq1bnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        game.start()
        self.assertTrue(game.is_over())


class WinnerInfoTestCase(unittest.TestCase):
    def test_not_over(self):
        game = LocalGame()
        game.start()
        self.assertIsNone(game.get_winner_color())
        self.assertIsNone(game.get_win_reason())

    def test_forced_over(self):
        game = LocalGame()
        game.start()
        game.end()
        self.assertIsNone(game.get_winner_color())
        self.assertIsNone(game.get_win_reason())

    def test_no_time_white(self):
        game = LocalGame()
        game.seconds_left_by_color[WHITE] = 0
        game.start()
        self.assertEqual(BLACK, game.get_winner_color())
        self.assertEqual(WinReason.TIMEOUT, game.get_win_reason())

    def test_no_time_black(self):
        game = LocalGame()
        game.seconds_left_by_color[BLACK] = 0
        game.start()
        self.assertEqual(WHITE, game.get_winner_color())
        self.assertEqual(WinReason.TIMEOUT, game.get_win_reason())

    def test_white_king_captured(self):
        """
        r n b q k b n r
        p p p p p p p p
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        P P P P P P P P
        R N B Q . B N R
        """
        game = LocalGame()
        game.board.set_board_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQ1BNR')
        game.start()
        self.assertEqual(BLACK, game.get_winner_color())
        self.assertEqual(WinReason.KING_CAPTURE, game.get_win_reason())

    def test_black_king_captured(self):
        """
        r n b q . b n r
        p p p p p p p p
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        P P P P P P P P
        R N B Q K B N R
        """
        game = LocalGame()
        game.board.set_board_fen('rnbq1bnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
        game.start()
        self.assertEqual(WHITE, game.get_winner_color())
        self.assertEqual(WinReason.KING_CAPTURE, game.get_win_reason())


class GetGameHistoryTestCase(unittest.TestCase):
    def test_no_history_until_game_over(self):
        g = LocalGame()
        g.sense(E2)
        self.assertEqual(g.get_game_history(), None)
        g.move(Move(E2, E4))
        self.assertEqual(g.get_game_history(), None)
        g.sense(A8)
        g.move(Move(E7, E5))
        self.assertEqual(g.get_game_history(), None)
        g.sense(E2)
        g.move(Move(F1, B5))
        g.sense(A8)
        g.move(Move(D7, D5))
        g.sense(E8)
        g.move(Move(B5, E8))
        self.assertTrue(g.is_over())
        self.assertNotEqual(g.get_game_history(), None)
