import unittest
from rbmc import LocalGame
from chess import *


class LocalGameTest(unittest.TestCase):
    def test_valid_senses(self):
        g = LocalGame()
        valid_senses = g.valid_senses()

        inside_squares = [
            B7, C7, D7, E7, F7, G7,
            B6, C6, D6, E6, F6, G6,
            B5, C5, D5, E5, F5, G5,
            B4, C4, D4, E4, F4, G4,
            B3, C3, D3, E3, F3, G3,
            B2, C2, D2, E2, F2, G2,
        ]

        outside_squares = [
            A8, B8, C8, D8, E8, F8, G8, H8,
            A7, H7,
            A6, H6,
            A5, H5,
            A4, H4,
            A3, H3,
            A2, H2,
            A1, B1, C1, D1, E1, F1, G1, H1,
        ]

        for square in inside_squares:
            self.assertIn(square, valid_senses)

        for square in outside_squares:
            self.assertNotIn(square, valid_senses)


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
