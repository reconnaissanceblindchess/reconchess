import unittest
from chess import *
from rbmc.game import LocalGame
from rbmc.history import GameHistory


class GameHistoryTest(unittest.TestCase):
    def setUp(self):
        self.game_history = GameHistory()
        self.senses = {
            WHITE: [E2, A1, A8],
            BLACK: [E4, H1, G8]
        }
        self.moves = {
            WHITE: [Move(E2,E4), None, Move(A2,A4)],
            BLACK: [Move(D7, D5), Move(B8, A6), None]
        }

        g = LocalGame()
        self.colors = [WHITE, BLACK]
        for idx in range(len(self.senses[WHITE])):
            for color in self.colors:
                if idx in range(0, len(self.senses[color])):
                    sense_square = self.senses[color][idx]
                    sense_results = g.sense(sense_square)
                    self.game_history.store_sense(color, sense_square, sense_results)
                if idx in range(0, len(self.moves[color])):
                    requested_move, taken_move, opt_capture_square = g.move(self.moves[color][idx])
                    self.game_history.store_move(color, requested_move, taken_move, opt_capture_square)

    def test_sense_history(self):
        for color in self.colors:
            self.assertEqual(self.senses[color], self.game_history.get_sense_history_for(color))
    
    def test_move_history(self):
        for color in self.colors:
            self.assertEqual(self.moves[color], self.game_history.get_move_history_for(color))
