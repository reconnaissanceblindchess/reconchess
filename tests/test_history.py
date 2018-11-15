import unittest
from chess import *
from rbmc.game import LocalGame
from rbmc.history import GameHistory


class GameHistoryTest(unittest.TestCase):
    def setUp(self):
        self.game_history = GameHistory()
        self.senses = [
            {
                WHITE: E2,
                BLACK: E4
            },
            {
                WHITE: A1,
                BLACK: H1,
            },
            {
                WHITE: A8,
                BLACK: G8
            }
        ]
        self.moves = [
            {
                WHITE: Move(E2,E4),
                BLACK: Move(D7, D5)
            },
            {
                WHITE: None,
                BLACK: Move(B8, A6)
            },
            {
                WHITE: Move(A2, A4),
                BLACK: None
            }
        ]
        self.sense_results = []
        self.move_results = []

        g = LocalGame()
        self.colors = [WHITE, BLACK]
        for idx in range(len(self.senses)):
            move_number = idx + 1
            for color in self.colors:
                if color in self.senses[idx]:
                    sense_square = self.senses[idx][color]
                    sense_results = g.sense(sense_square)
                    self.game_history.store_sense(move_number, color, sense_square, sense_results)
                if idx in range(0, len(self.moves)) and color in self.moves[idx]:
                    requested_move, taken_move, opt_capture_square = g.move(self.moves[idx][color])
                    self.game_history.store_move(move_number, color, requested_move, taken_move, opt_capture_square)
                    self.game_history.store_opponent_move_results(move_number, not color, opt_capture_square)

    def test_sense_history(self):
        for color in self.colors:
            sense_history = [s[color] for s in self.senses]
            self.assertEqual(sense_history, self.game_history.get_sense_history_for(color))
    
    def test_move_history(self):
        for color in self.colors:
            move_history = [m[color] for m in self.moves]
            self.assertEqual(move_history, self.game_history.get_move_history_for(color))
