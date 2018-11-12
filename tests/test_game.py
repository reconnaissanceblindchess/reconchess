import unittest
from rbmc import LocalGame
from chess import *
import time
import random

INSIDE_SQUARES = [
    B7, C7, D7, E7, F7, G7,
    B6, C6, D6, E6, F6, G6,
    B5, C5, D5, E5, F5, G5,
    B4, C4, D4, E4, F4, G4,
    B3, C3, D3, E3, F3, G3,
    B2, C2, D2, E2, F2, G2,
]

OUTSIDE_SQUARES = [
    A8, B8, C8, D8, E8, F8, G8, H8,
    A7, H7,
    A6, H6,
    A5, H5,
    A4, H4,
    A3, H3,
    A2, H2,
    A1, B1, C1, D1, E1, F1, G1, H1,
]

SENSE_BY_SQUARE = {
    B7: [A8, B8, C8, A7, B7, C7, A6, B6, C6],
    C7: [B8, C8, D8, B7, C7, D7, B6, C6, D6],
    D7: [C8, D8, E8, C7, D7, E7, C6, D6, E6],
    E7: [D8, E8, F8, D7, E7, F7, D6, E6, F6],
    F7: [E8, F8, G8, E7, F7, G7, E6, F6, G6],
    G7: [F8, G8, H8, F7, G7, H7, F6, G6, H6],

    B6: [A7, B7, C7, A6, B6, C6, A5, B5, C5],
    C6: [B7, C7, D7, B6, C6, D6, B5, C5, D5],
    D6: [C7, D7, E7, C6, D6, E6, C5, D5, E5],
    E6: [D7, E7, F7, D6, E6, F6, D5, E5, F5],
    F6: [E7, F7, G7, E6, F6, G6, E5, F5, G5],
    G6: [F7, G7, H7, F6, G6, H6, F5, G5, H5],

    B5: [A6, B6, C6, A5, B5, C5, A4, B4, C4],
    C5: [B6, C6, D6, B5, C5, D5, B4, C4, D4],
    D5: [C6, D6, E6, C5, D5, E5, C4, D4, E4],
    E5: [D6, E6, F6, D5, E5, F5, D4, E4, F4],
    F5: [E6, F6, G6, E5, F5, G5, E4, F4, G4],
    G5: [F6, G6, H6, F5, G5, H5, F4, G4, H4],

    B4: [A5, B5, C5, A4, B4, C4, A3, B3, C3],
    C4: [B5, C5, D5, B4, C4, D4, B3, C3, D3],
    D4: [C5, D5, E5, C4, D4, E4, C3, D3, E3],
    E4: [D5, E5, F5, D4, E4, F4, D3, E3, F3],
    F4: [E5, F5, G5, E4, F4, G4, E3, F3, G3],
    G4: [F5, G5, H5, F4, G4, H4, F3, G3, H3],

    B3: [A4, B4, C4, A3, B3, C3, A2, B2, C2],
    C3: [B4, C4, D4, B3, C3, D3, B2, C2, D2],
    D3: [C4, D4, E4, C3, D3, E3, C2, D2, E2],
    E3: [D4, E4, F4, D3, E3, F3, D2, E2, F2],
    F3: [E4, F4, G4, E3, F3, G3, E2, F2, G2],
    G3: [F4, G4, H4, F3, G3, H3, F2, G2, H2],

    B2: [A3, B3, C3, A2, B2, C2, A1, B1, C1],
    C2: [B3, C3, D3, B2, C2, D2, B1, C1, D1],
    D2: [C3, D3, E3, C2, D2, E2, C1, D1, E1],
    E2: [D3, E3, F3, D2, E2, F2, D1, E1, F1],
    F2: [E3, F3, G3, E2, F2, G2, E1, F1, G1],
    G2: [F3, G3, H3, F2, G2, H2, F1, G1, H1],
}


class LocalGameSenseTest(unittest.TestCase):
    def setUp(self):
        self.game = LocalGame()

    def test_valid_senses_contents(self):
        valid_senses = self.game.valid_senses()

        for square in INSIDE_SQUARES:
            self.assertIn(square, valid_senses)

        for square in OUTSIDE_SQUARES:
            self.assertNotIn(square, valid_senses)

    def test_sense_invalid(self):
        for square in OUTSIDE_SQUARES:
            with self.assertRaises(ValueError):
                self.game.sense(square)

    def test_sense_squares(self):
        for square in INSIDE_SQUARES:
            sense_result = self.game.sense(square)
            squares = [s for s, p in sense_result]
            self.assertEqual(squares, SENSE_BY_SQUARE[square])

    def test_sense_pieces(self):
        for sense_square in INSIDE_SQUARES:
            sense_result = self.game.sense(sense_square)
            for square, piece in sense_result:
                self.assertEqual(piece, self.game.board.piece_at(square))


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
            self.assertAlmostEqual(game.get_seconds_left(), time_by_color[turn])


class LocalGameValidMoveTest(unittest.TestCase):
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
        valid_moves = self.game.valid_moves()
        for move in self.STARTING_WHITE_PAWN_CAPTURES:
            self.assertIn(move, valid_moves)
        self.game.board.push(Move.null())
        valid_moves = self.game.valid_moves()
        for move in self.BLACK_STARTING_PAWN_CAPTURES:
            self.assertIn(move, valid_moves)

    def test_pass(self):
        self.assertIn(Move.null(), self.game.valid_moves())

    def test_superset_fuzz(self, max_turns=500):
        turn = 1
        while not self.game.board.is_game_over() and turn < max_turns:
            truth_moves = set(self.game.board.generate_pseudo_legal_moves())
            recon_moves = set(self.game.valid_moves())
            self.assertTrue(recon_moves.issuperset(truth_moves))

            self.game.board.push(random.sample(truth_moves, 1)[0])
            turn += 1


class LocalGameMoveTest(unittest.TestCase):
    def test_legal_castle(self):
        pass

    def test_queenside_castle_piece_between(self):
        pass

    def test_kingside_castle_piece_between(self):
        pass

    def test_queenside_castle_no_rights(self):
        pass

    def test_kingside_castle_no_rights(self):
        pass

    def test_castling_into_check(self):
        pass

    def test_castling_out_of_check(self):
        pass

    def test_en_passant(self):
        # should make sure the correct square is returned for capture square
        pass

    def test_move_opponent_piece_is_illegal(self):
        # test moving opponent pieces
        pass

    def test_move_no_piece_is_illegal(self):
        # test a move from a square with no piece
        pass

    def test_sliding_pawn(self):
        # mainly just the two move at the beginning
        pass

    def test_sliding_rook(self):
        pass

    def test_sliding_bishop(self):
        pass

    def test_sliding_queen(self):
        pass
