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
