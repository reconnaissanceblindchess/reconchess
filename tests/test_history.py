import unittest
from chess import *
from reconchess import *
import tempfile
import os
import random


class RandomBot(Player):
    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        return random.choice(sense_actions)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        return random.choice(move_actions + [None])


class TurnEqualityTestCase(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(Turn(WHITE, 5), Turn(WHITE, 5))
        self.assertNotEqual(Turn(WHITE, 5), Turn(WHITE, 4))
        self.assertNotEqual(Turn(WHITE, 5), Turn(BLACK, 5))

        self.assertEqual(Turn(BLACK, 5), Turn(BLACK, 5))
        self.assertNotEqual(Turn(BLACK, 5), Turn(BLACK, 4))
        self.assertNotEqual(Turn(BLACK, 5), Turn(WHITE, 5))

    def test_order(self):
        self.assertTrue(Turn(WHITE, 5) < Turn(BLACK, 5))
        self.assertFalse(Turn(WHITE, 5) < Turn(BLACK, 4))
        self.assertTrue(Turn(WHITE, 5) < Turn(WHITE, 6))
        self.assertTrue(Turn(WHITE, 5) < Turn(BLACK, 6))

        self.assertTrue(Turn(WHITE, 5) > Turn(BLACK, 4))
        self.assertFalse(Turn(WHITE, 5) > Turn(BLACK, 5))
        self.assertFalse(Turn(WHITE, 5) > Turn(WHITE, 6))
        self.assertFalse(Turn(WHITE, 5) > Turn(BLACK, 6))

    def test_equality_order(self):
        self.assertTrue(Turn(WHITE, 5) <= Turn(BLACK, 5))
        self.assertFalse(Turn(WHITE, 5) <= Turn(BLACK, 4))
        self.assertTrue(Turn(WHITE, 5) <= Turn(WHITE, 6))
        self.assertTrue(Turn(WHITE, 5) <= Turn(BLACK, 6))

        self.assertTrue(Turn(WHITE, 5) >= Turn(BLACK, 4))
        self.assertFalse(Turn(WHITE, 5) >= Turn(BLACK, 5))
        self.assertFalse(Turn(WHITE, 5) >= Turn(WHITE, 6))
        self.assertFalse(Turn(WHITE, 5) >= Turn(BLACK, 6))

        self.assertTrue(Turn(WHITE, 5) >= Turn(WHITE, 5))
        self.assertTrue(Turn(BLACK, 5) >= Turn(BLACK, 5))


class TurnNeighborsTestCase(unittest.TestCase):
    def test_next(self):
        self.assertEqual(Turn(WHITE, 0).next, Turn(BLACK, 0))
        self.assertEqual(Turn(BLACK, 0).next, Turn(WHITE, 1))
        self.assertEqual(Turn(WHITE, 1).next, Turn(BLACK, 1))

    def test_previous(self):
        self.assertEqual(Turn(WHITE, 5).previous, Turn(BLACK, 4))
        self.assertEqual(Turn(BLACK, 4).previous, Turn(WHITE, 4))
        self.assertEqual(Turn(WHITE, 4).previous, Turn(BLACK, 3))
        self.assertEqual(Turn(BLACK, 3).previous, Turn(WHITE, 3))


class HistoryEmptyTurnsTestCase(unittest.TestCase):
    def setUp(self):
        self.history = GameHistory()

    def test_empty_turns(self):
        self.assertEqual(list(self.history.turns()), [])
        self.assertEqual(list(self.history.turns(WHITE)), [])
        self.assertEqual(list(self.history.turns(BLACK)), [])
        self.assertEqual(list(self.history.turns(start=1)), [])
        self.assertEqual(list(self.history.turns(stop=5)), [])
        self.assertEqual(list(self.history.turns(start=1, stop=5)), [])

    def test_empty_num_turns(self):
        self.assertEqual(self.history.num_turns(), 0)
        self.assertEqual(self.history.num_turns(WHITE), 0)
        self.assertEqual(self.history.num_turns(BLACK), 0)

    def test_first_turn(self):
        with self.assertRaises(ValueError):
            self.history.first_turn()

        with self.assertRaises(ValueError):
            self.history.first_turn(WHITE)

        with self.assertRaises(ValueError):
            self.history.first_turn(BLACK)

        with self.assertRaises(ValueError):
            self.assertFalse(self.history.is_first_turn(Turn(WHITE, 0)))

        with self.assertRaises(ValueError):
            self.assertFalse(self.history.is_first_turn(Turn(BLACK, 0)))

    def test_last_turn(self):
        with self.assertRaises(ValueError):
            self.history.last_turn()

        with self.assertRaises(ValueError):
            self.history.last_turn(WHITE)

        with self.assertRaises(ValueError):
            self.history.last_turn(BLACK)

        with self.assertRaises(ValueError):
            self.assertFalse(self.history.is_last_turn(Turn(WHITE, 0)))

        with self.assertRaises(ValueError):
            self.assertFalse(self.history.is_last_turn(Turn(BLACK, 0)))


class HistoryTurnsTestCase(unittest.TestCase):
    def setUp(self):
        self.history = GameHistory()

        self.history.store_sense(WHITE, E7, [])
        self.history.store_move(WHITE, Move(B1, C3), Move(B1, C3), None)
        self.history.store_fen_before_move(WHITE, 'a1')
        self.history.store_fen_after_move(WHITE, 'a2')

        self.history.store_sense(BLACK, E2, [])
        self.history.store_move(BLACK, Move(B8, C6), Move(B8, C6), None)
        self.history.store_fen_before_move(BLACK, 'b1')
        self.history.store_fen_after_move(BLACK, 'b2')

        self.history.store_sense(WHITE, E7, [])
        self.history.store_move(WHITE, Move(C3, B5), Move(C3, B5), None)
        self.history.store_fen_before_move(WHITE, 'c1')
        self.history.store_fen_after_move(WHITE, 'c2')

        self.history.store_sense(BLACK, E2, [])
        self.history.store_move(BLACK, Move(C6, B4), Move(C6, B4), None)
        self.history.store_fen_before_move(BLACK, 'd1')
        self.history.store_fen_after_move(BLACK, 'd2')

        self.history.store_sense(WHITE, E7, [])
        self.history.store_move(WHITE, Move(B5, D6), Move(B5, D6), None)
        self.history.store_fen_before_move(WHITE, 'e1')
        self.history.store_fen_after_move(WHITE, 'e2')

        self.history.store_sense(BLACK, E2, [])
        self.history.store_move(BLACK, Move(B4, D3), Move(B4, D3), None)
        self.history.store_fen_before_move(BLACK, 'f1')
        self.history.store_fen_after_move(BLACK, 'f2')

        self.history.store_sense(WHITE, E7, [])
        self.history.store_move(WHITE, Move(D6, E8), Move(D6, E8), None)
        self.history.store_fen_before_move(WHITE, 'g1')
        self.history.store_fen_after_move(WHITE, 'g2')

    def test_first_turn(self):
        self.assertEqual(self.history.first_turn(), Turn(WHITE, 0))
        self.assertEqual(self.history.first_turn(WHITE), Turn(WHITE, 0))
        self.assertEqual(self.history.first_turn(BLACK), Turn(BLACK, 0))
        self.assertTrue(self.history.is_first_turn(Turn(WHITE, 0)))
        self.assertFalse(self.history.is_first_turn(Turn(BLACK, 0)))
        self.assertFalse(self.history.is_first_turn(Turn(WHITE, 1)))

    def test_last_turn(self):
        self.assertEqual(self.history.last_turn(), Turn(WHITE, 3))
        self.assertEqual(self.history.last_turn(WHITE), Turn(WHITE, 3))
        self.assertEqual(self.history.last_turn(BLACK), Turn(BLACK, 2))
        self.assertTrue(self.history.is_last_turn(Turn(WHITE, 3)))
        self.assertFalse(self.history.is_last_turn(Turn(BLACK, 2)))
        self.assertFalse(self.history.is_last_turn(Turn(BLACK, 3)))

        self.history.store_sense(BLACK, E2, [])
        self.history.store_move(BLACK, Move(D3, E1), Move(D3, E1), None)
        self.history.store_fen_before_move(BLACK, 'h1')
        self.history.store_fen_after_move(BLACK, 'h2')

        self.assertEqual(self.history.last_turn(), Turn(BLACK, 3))
        self.assertEqual(self.history.last_turn(WHITE), Turn(WHITE, 3))
        self.assertEqual(self.history.last_turn(BLACK), Turn(BLACK, 3))
        self.assertFalse(self.history.is_last_turn(Turn(WHITE, 3)))
        self.assertFalse(self.history.is_last_turn(Turn(BLACK, 2)))
        self.assertTrue(self.history.is_last_turn(Turn(BLACK, 3)))

    def test_all_turns(self):
        self.assertEqual(list(self.history.turns()), [
            Turn(WHITE, 0), Turn(BLACK, 0),
            Turn(WHITE, 1), Turn(BLACK, 1),
            Turn(WHITE, 2), Turn(BLACK, 2),
            Turn(WHITE, 3)
        ])

        self.history.store_sense(BLACK, E2, [])
        self.history.store_move(BLACK, Move(D3, E1), Move(D3, E1), None)
        self.history.store_fen_before_move(BLACK, 'h1')
        self.history.store_fen_after_move(BLACK, 'h2')

        self.assertEqual(list(self.history.turns()), [
            Turn(WHITE, 0), Turn(BLACK, 0),
            Turn(WHITE, 1), Turn(BLACK, 1),
            Turn(WHITE, 2), Turn(BLACK, 2),
            Turn(WHITE, 3), Turn(BLACK, 3),
        ])

    def test_white_turns(self):
        self.assertEqual(list(self.history.turns(WHITE)), [
            Turn(WHITE, 0),
            Turn(WHITE, 1),
            Turn(WHITE, 2),
            Turn(WHITE, 3)
        ])

        self.history.store_sense(BLACK, E2, [])
        self.history.store_move(BLACK, Move(D3, E1), Move(D3, E1), None)
        self.history.store_fen_before_move(BLACK, 'h1')
        self.history.store_fen_after_move(BLACK, 'h2')

        self.assertEqual(list(self.history.turns(WHITE)), [
            Turn(WHITE, 0),
            Turn(WHITE, 1),
            Turn(WHITE, 2),
            Turn(WHITE, 3),
        ])

    def test_black_turns(self):
        self.assertEqual(list(self.history.turns(BLACK)), [
            Turn(BLACK, 0),
            Turn(BLACK, 1),
            Turn(BLACK, 2),
        ])

        self.history.store_sense(BLACK, E2, [])
        self.history.store_move(BLACK, Move(D3, E1), Move(D3, E1), None)
        self.history.store_fen_before_move(BLACK, 'h1')
        self.history.store_fen_after_move(BLACK, 'h2')

        self.assertEqual(list(self.history.turns(BLACK)), [
            Turn(BLACK, 0),
            Turn(BLACK, 1),
            Turn(BLACK, 2),
            Turn(BLACK, 3),
        ])

        self.history.store_sense(WHITE, E7, [])
        self.history.store_move(WHITE, Move(A2, A3), Move(A2, A3), None)
        self.history.store_fen_before_move(WHITE, 'h1')
        self.history.store_fen_after_move(WHITE, 'h2')

        self.assertEqual(list(self.history.turns(BLACK)), [
            Turn(BLACK, 0),
            Turn(BLACK, 1),
            Turn(BLACK, 2),
            Turn(BLACK, 3),
        ])

    def test_turns_range(self):
        self.assertEqual(list(self.history.turns(start=1)), [
            Turn(WHITE, 1), Turn(BLACK, 1),
            Turn(WHITE, 2), Turn(BLACK, 2),
            Turn(WHITE, 3)
        ])

        self.assertEqual(list(self.history.turns(stop=2)), [
            Turn(WHITE, 0), Turn(BLACK, 0),
            Turn(WHITE, 1), Turn(BLACK, 1),
        ])

        self.assertEqual(list(self.history.turns(start=1, stop=2)), [
            Turn(WHITE, 1), Turn(BLACK, 1),
        ])

        self.assertEqual(list(self.history.turns(start=1, stop=5)), [
            Turn(WHITE, 1), Turn(BLACK, 1),
            Turn(WHITE, 2), Turn(BLACK, 2),
            Turn(WHITE, 3)
        ])

        self.assertEqual(list(self.history.turns(start=1, stop=3)), [
            Turn(WHITE, 1), Turn(BLACK, 1),
            Turn(WHITE, 2), Turn(BLACK, 2),
        ])

    def test_turns_range_white(self):
        self.assertEqual(list(self.history.turns(WHITE, start=1)), [
            Turn(WHITE, 1),
            Turn(WHITE, 2),
            Turn(WHITE, 3)
        ])

        self.assertEqual(list(self.history.turns(WHITE, stop=2)), [
            Turn(WHITE, 0),
            Turn(WHITE, 1),
        ])

        self.assertEqual(list(self.history.turns(WHITE, start=1, stop=2)), [
            Turn(WHITE, 1),
        ])

        self.assertEqual(list(self.history.turns(WHITE, start=1, stop=5)), [
            Turn(WHITE, 1),
            Turn(WHITE, 2),
            Turn(WHITE, 3)
        ])

        self.assertEqual(list(self.history.turns(WHITE, start=1, stop=3)), [
            Turn(WHITE, 1),
            Turn(WHITE, 2),
        ])

    def test_turns_range_black(self):
        self.assertEqual(list(self.history.turns(BLACK, start=1)), [
            Turn(BLACK, 1),
            Turn(BLACK, 2),
        ])

        self.assertEqual(list(self.history.turns(BLACK, stop=2)), [
            Turn(BLACK, 0),
            Turn(BLACK, 1),
        ])

        self.assertEqual(list(self.history.turns(BLACK, start=1, stop=2)), [
            Turn(BLACK, 1),
        ])

        self.assertEqual(list(self.history.turns(BLACK, start=1, stop=5)), [
            Turn(BLACK, 1),
            Turn(BLACK, 2),
        ])

        self.assertEqual(list(self.history.turns(BLACK, start=1, stop=3)), [
            Turn(BLACK, 1),
            Turn(BLACK, 2),
        ])

    def test_num_turns(self):
        self.assertEqual(self.history.num_turns(), 7)
        self.assertEqual(self.history.num_turns(WHITE), 4)
        self.assertEqual(self.history.num_turns(BLACK), 3)


class HistoryEqualityTestCase(unittest.TestCase):
    def setUp(self):
        self.g1 = GameHistory()
        self.g2 = GameHistory()

    def test_empty(self):
        self.assertEqual(self.g1, self.g2)

    def test_same_sense(self):
        self.g1.store_sense(WHITE, E7, [(D8, Piece(QUEEN, BLACK)), (F6, None)])
        self.g2.store_sense(WHITE, E7, [(D8, Piece(QUEEN, BLACK)), (F6, None)])
        self.assertEqual(self.g1, self.g2)

    def test_diff_sense(self):
        self.g1.store_sense(WHITE, E7, [(D8, Piece(QUEEN, BLACK)), (F6, None)])
        self.g2.store_sense(WHITE, E6, [(D8, Piece(QUEEN, BLACK)), (F6, None)])
        self.assertNotEqual(self.g1, self.g2)

    def test_diff_sense_result_square(self):
        self.g1.store_sense(WHITE, E7, [(D8, Piece(QUEEN, BLACK)), (F6, None)])
        self.g2.store_sense(WHITE, E7, [(D7, Piece(QUEEN, BLACK)), (F6, None)])
        self.assertNotEqual(self.g1, self.g2)

    def test_diff_sense_result_piece(self):
        self.g1.store_sense(WHITE, E7, [(D8, Piece(QUEEN, BLACK)), (F6, None)])
        self.g2.store_sense(WHITE, E7, [(D8, Piece(QUEEN, WHITE)), (F6, None)])
        self.assertNotEqual(self.g1, self.g2)

    def test_diff_sense_color(self):
        self.g1.store_sense(WHITE, E7, [(D8, Piece(QUEEN, BLACK)), (F6, None)])
        self.g2.store_sense(BLACK, E7, [(D8, Piece(QUEEN, BLACK)), (F6, None)])
        self.assertNotEqual(self.g1, self.g2)

    def test_same_move(self):
        self.g1.store_move(WHITE, Move(E2, E3), Move(E2, E3), None)
        self.g2.store_move(WHITE, Move(E2, E3), Move(E2, E3), None)
        self.assertEqual(self.g1, self.g2)

    def test_diff_move_requested(self):
        self.g1.store_move(WHITE, Move(E2, E3), Move(E2, E3), None)
        self.g2.store_move(WHITE, Move(E2, E4), Move(E2, E3), None)
        self.assertNotEqual(self.g1, self.g2)

    def test_diff_move_taken(self):
        self.g1.store_move(WHITE, Move(E2, E3), Move(E2, E3), None)
        self.g2.store_move(WHITE, Move(E2, E3), Move(E2, E4), None)
        self.assertNotEqual(self.g1, self.g2)

    def test_diff_move_capture(self):
        self.g1.store_move(WHITE, Move(E2, E3), Move(E2, E3), None)
        self.g2.store_move(WHITE, Move(E2, E3), Move(E2, E3), E7)
        self.assertNotEqual(self.g1, self.g2)

    def test_diff_move_color(self):
        self.g1.store_move(WHITE, Move(E2, E3), Move(E2, E3), None)
        self.g2.store_move(BLACK, Move(E2, E3), Move(E2, E3), None)
        self.assertNotEqual(self.g1, self.g2)

    def test_same_before_fen(self):
        self.g1.store_fen_before_move(WHITE, 'asdf')
        self.g2.store_fen_before_move(WHITE, 'asdf')
        self.assertEqual(self.g1, self.g2)

    def test_diff_before_fen_color(self):
        self.g1.store_fen_before_move(WHITE, 'asdf')
        self.g2.store_fen_before_move(BLACK, 'asdf')
        self.assertNotEqual(self.g1, self.g2)

    def test_diff_before_fen(self):
        self.g1.store_fen_before_move(WHITE, 'asdf')
        self.g2.store_fen_before_move(WHITE, 'qwer')
        self.assertNotEqual(self.g1, self.g2)

    def test_same_after_fen(self):
        self.g1.store_fen_after_move(WHITE, 'asdf')
        self.g2.store_fen_after_move(WHITE, 'asdf')
        self.assertEqual(self.g1, self.g2)

    def test_diff_after_fen_color(self):
        self.g1.store_fen_after_move(WHITE, 'asdf')
        self.g2.store_fen_after_move(BLACK, 'asdf')
        self.assertNotEqual(self.g1, self.g2)

    def test_diff_after_fen(self):
        self.g1.store_fen_after_move(WHITE, 'asdf')
        self.g2.store_fen_after_move(WHITE, 'qwer')
        self.assertNotEqual(self.g1, self.g2)


class HistoryGettersTestCase(unittest.TestCase):
    def setUp(self):
        self.history = GameHistory()

        self.history.store_sense(WHITE, E7, [(E7, None)])
        self.history.store_move(WHITE, Move(B1, C3), Move(B1, C3), None)
        self.history.store_fen_before_move(WHITE, 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -')
        self.history.store_fen_after_move(WHITE, 'rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq -')

        self.history.store_sense(BLACK, E2, [(E2, None)])
        self.history.store_move(BLACK, Move(B8, C6), Move(B8, C6), None)
        self.history.store_fen_before_move(BLACK, 'rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq -')
        self.history.store_fen_after_move(BLACK, 'r1bqkbnr/pppppppp/2n5/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq -')

        self.history.store_sense(WHITE, F7, [(F7, None)])
        self.history.store_move(WHITE, Move(C3, B5), Move(C3, B5), B5)
        self.history.store_fen_before_move(WHITE, 'r1bqkbnr/pppppppp/2n5/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq -')
        self.history.store_fen_after_move(WHITE, 'r1bqkbnr/pppppppp/2n5/1N6/8/8/PPPPPPPP/R1BQKBNR w KQkq -')

        self.history.store_sense(BLACK, F2, [(F2, None)])
        self.history.store_move(BLACK, Move(C6, B4), Move(C6, B4), B4)
        self.history.store_fen_before_move(BLACK, 'r1bqkbnr/pppppppp/2n5/1N6/8/8/PPPPPPPP/R1BQKBNR w KQkq -')
        self.history.store_fen_after_move(BLACK, 'r1bqkbnr/pppppppp/8/1N6/1n6/8/PPPPPPPP/R1BQKBNR w KQkq -')

        self.history.store_sense(WHITE, G7, [(G7, None)])
        self.history.store_move(WHITE, Move(B5, D6), Move(B5, D6), None)
        self.history.store_fen_before_move(WHITE, 'r1bqkbnr/pppppppp/8/1N6/1n6/8/PPPPPPPP/R1BQKBNR w KQkq -')
        self.history.store_fen_after_move(WHITE, 'r1bqkbnr/pppppppp/3N4/8/1n6/8/PPPPPPPP/R1BQKBNR w KQkq -')

        self.history.store_sense(BLACK, G2, [(G2, None)])
        self.history.store_move(BLACK, Move(B4, D3), Move(B4, D2), None)
        self.history.store_fen_before_move(BLACK, 'r1bqkbnr/pppppppp/3N4/8/1n6/8/PPPPPPPP/R1BQKBNR w KQkq -')
        self.history.store_fen_after_move(BLACK, 'r1bqkbnr/pppppppp/3N4/8/8/3n4/PPPPPPPP/R1BQKBNR w KQkq -')

        self.history.store_sense(WHITE, H7, [(H7, None)])
        self.history.store_move(WHITE, Move(D6, E8), Move(D6, E8), E8)
        self.history.store_fen_before_move(WHITE, 'r1bqkbnr/pppppppp/3N4/8/8/3n4/PPPPPPPP/R1BQKBNR w KQkq -')
        self.history.store_fen_after_move(WHITE, 'r1bqNbnr/pppppppp/8/8/8/3n4/PPPPPPPP/R1BQKBNR w KQkq -')

    def test_has_sense(self):
        self.assertTrue(self.history.has_sense(Turn(WHITE, 0)))
        self.assertTrue(self.history.has_sense(Turn(BLACK, 0)))
        self.assertTrue(self.history.has_sense(Turn(WHITE, 1)))
        self.assertTrue(self.history.has_sense(Turn(BLACK, 1)))
        self.assertTrue(self.history.has_sense(Turn(WHITE, 2)))
        self.assertTrue(self.history.has_sense(Turn(BLACK, 2)))
        self.assertTrue(self.history.has_sense(Turn(WHITE, 3)))

    def test_sense(self):
        self.assertEqual(self.history.sense(Turn(WHITE, 0)), E7)
        self.assertEqual(self.history.sense(Turn(BLACK, 0)), E2)
        self.assertEqual(self.history.sense(Turn(WHITE, 1)), F7)
        self.assertEqual(self.history.sense(Turn(BLACK, 1)), F2)
        self.assertEqual(self.history.sense(Turn(WHITE, 2)), G7)
        self.assertEqual(self.history.sense(Turn(BLACK, 2)), G2)
        self.assertEqual(self.history.sense(Turn(WHITE, 3)), H7)

    def test_invalid_sense(self):
        self.assertFalse(self.history.has_sense(Turn(WHITE, -1)))
        self.assertFalse(self.history.has_sense(Turn(WHITE, 4)))
        self.assertFalse(self.history.has_sense(Turn(BLACK, 3)))
        with self.assertRaises(ValueError):
            self.history.sense(Turn(WHITE, -1))
        with self.assertRaises(ValueError):
            self.history.sense(Turn(WHITE, 4))
        with self.assertRaises(ValueError):
            self.history.sense(Turn(BLACK, 3))

    def test_sense_result(self):
        self.assertEqual(self.history.sense_result(Turn(WHITE, 0)), [(E7, None)])
        self.assertEqual(self.history.sense_result(Turn(BLACK, 0)), [(E2, None)])
        self.assertEqual(self.history.sense_result(Turn(WHITE, 1)), [(F7, None)])
        self.assertEqual(self.history.sense_result(Turn(BLACK, 1)), [(F2, None)])
        self.assertEqual(self.history.sense_result(Turn(WHITE, 2)), [(G7, None)])
        self.assertEqual(self.history.sense_result(Turn(BLACK, 2)), [(G2, None)])
        self.assertEqual(self.history.sense_result(Turn(WHITE, 3)), [(H7, None)])

    def test_invalid_sense_result(self):
        with self.assertRaises(ValueError):
            self.history.sense_result(Turn(WHITE, -1))
        with self.assertRaises(ValueError):
            self.history.sense_result(Turn(WHITE, 4))
        with self.assertRaises(ValueError):
            self.history.sense_result(Turn(BLACK, 3))

    def test_has_move(self):
        self.assertTrue(self.history.has_move(Turn(WHITE, 0)))
        self.assertTrue(self.history.has_move(Turn(BLACK, 0)))
        self.assertTrue(self.history.has_move(Turn(WHITE, 1)))
        self.assertTrue(self.history.has_move(Turn(BLACK, 1)))
        self.assertTrue(self.history.has_move(Turn(WHITE, 2)))
        self.assertTrue(self.history.has_move(Turn(BLACK, 2)))
        self.assertTrue(self.history.has_move(Turn(WHITE, 3)))

    def test_requested_move(self):
        self.assertEqual(self.history.requested_move(Turn(WHITE, 0)), Move(B1, C3))
        self.assertEqual(self.history.requested_move(Turn(BLACK, 0)), Move(B8, C6))
        self.assertEqual(self.history.requested_move(Turn(WHITE, 1)), Move(C3, B5))
        self.assertEqual(self.history.requested_move(Turn(BLACK, 1)), Move(C6, B4))
        self.assertEqual(self.history.requested_move(Turn(WHITE, 2)), Move(B5, D6))
        self.assertEqual(self.history.requested_move(Turn(BLACK, 2)), Move(B4, D3))
        self.assertEqual(self.history.requested_move(Turn(WHITE, 3)), Move(D6, E8))

    def test_invalid_requested_move(self):
        self.assertFalse(self.history.has_move(Turn(WHITE, -1)))
        self.assertFalse(self.history.has_move(Turn(WHITE, 4)))
        self.assertFalse(self.history.has_move(Turn(BLACK, 3)))
        with self.assertRaises(ValueError):
            self.history.requested_move(Turn(WHITE, -1))
        with self.assertRaises(ValueError):
            self.history.requested_move(Turn(WHITE, 4))
        with self.assertRaises(ValueError):
            self.history.requested_move(Turn(BLACK, 3))

    def test_taken_move(self):
        self.assertEqual(self.history.taken_move(Turn(WHITE, 0)), Move(B1, C3))
        self.assertEqual(self.history.taken_move(Turn(BLACK, 0)), Move(B8, C6))
        self.assertEqual(self.history.taken_move(Turn(WHITE, 1)), Move(C3, B5))
        self.assertEqual(self.history.taken_move(Turn(BLACK, 1)), Move(C6, B4))
        self.assertEqual(self.history.taken_move(Turn(WHITE, 2)), Move(B5, D6))
        self.assertEqual(self.history.taken_move(Turn(BLACK, 2)), Move(B4, D2))
        self.assertEqual(self.history.taken_move(Turn(WHITE, 3)), Move(D6, E8))

    def test_invalid_taken_move(self):
        with self.assertRaises(ValueError):
            self.history.taken_move(Turn(WHITE, -1))
        with self.assertRaises(ValueError):
            self.history.taken_move(Turn(WHITE, 4))
        with self.assertRaises(ValueError):
            self.history.taken_move(Turn(BLACK, 3))

    def test_capture_square(self):
        self.assertEqual(self.history.capture_square(Turn(WHITE, 0)), None)
        self.assertEqual(self.history.capture_square(Turn(BLACK, 0)), None)
        self.assertEqual(self.history.capture_square(Turn(WHITE, 1)), B5)
        self.assertEqual(self.history.capture_square(Turn(BLACK, 1)), B4)
        self.assertEqual(self.history.capture_square(Turn(WHITE, 2)), None)
        self.assertEqual(self.history.capture_square(Turn(BLACK, 2)), None)
        self.assertEqual(self.history.capture_square(Turn(WHITE, 3)), E8)

    def test_invalid_capture_square(self):
        with self.assertRaises(ValueError):
            self.history.capture_square(Turn(WHITE, -1))
        with self.assertRaises(ValueError):
            self.history.capture_square(Turn(WHITE, 4))
        with self.assertRaises(ValueError):
            self.history.capture_square(Turn(BLACK, 3))

    def test_move_result(self):
        self.assertEqual(self.history.move_result(Turn(WHITE, 0)), (Move(B1, C3), Move(B1, C3), None))
        self.assertEqual(self.history.move_result(Turn(BLACK, 0)), (Move(B8, C6), Move(B8, C6), None))
        self.assertEqual(self.history.move_result(Turn(WHITE, 1)), (Move(C3, B5), Move(C3, B5), B5))
        self.assertEqual(self.history.move_result(Turn(BLACK, 1)), (Move(C6, B4), Move(C6, B4), B4))
        self.assertEqual(self.history.move_result(Turn(WHITE, 2)), (Move(B5, D6), Move(B5, D6), None))
        self.assertEqual(self.history.move_result(Turn(BLACK, 2)), (Move(B4, D3), Move(B4, D2), None))
        self.assertEqual(self.history.move_result(Turn(WHITE, 3)), (Move(D6, E8), Move(D6, E8), E8))

    def test_invalid_move_result(self):
        with self.assertRaises(ValueError):
            self.history.move_result(Turn(WHITE, -1))
        with self.assertRaises(ValueError):
            self.history.move_result(Turn(WHITE, 4))
        with self.assertRaises(ValueError):
            self.history.move_result(Turn(BLACK, 3))

    def test_fen_before(self):
        self.assertEqual(self.history.truth_fen_before_move(Turn(WHITE, 0)),
                         'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_before_move(Turn(BLACK, 0)),
                         'rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_before_move(Turn(WHITE, 1)),
                         'r1bqkbnr/pppppppp/2n5/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_before_move(Turn(BLACK, 1)),
                         'r1bqkbnr/pppppppp/2n5/1N6/8/8/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_before_move(Turn(WHITE, 2)),
                         'r1bqkbnr/pppppppp/8/1N6/1n6/8/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_before_move(Turn(BLACK, 2)),
                         'r1bqkbnr/pppppppp/3N4/8/1n6/8/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_before_move(Turn(WHITE, 3)),
                         'r1bqkbnr/pppppppp/3N4/8/8/3n4/PPPPPPPP/R1BQKBNR w KQkq -')

    def test_invalid_fen_before(self):
        with self.assertRaises(ValueError):
            self.history.truth_fen_before_move(Turn(WHITE, -1))
        with self.assertRaises(ValueError):
            self.history.truth_fen_before_move(Turn(WHITE, 4))
        with self.assertRaises(ValueError):
            self.history.truth_fen_before_move(Turn(BLACK, 3))

    def test_fen_after(self):
        self.assertEqual(self.history.truth_fen_after_move(Turn(WHITE, 0)),
                         'rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_after_move(Turn(BLACK, 0)),
                         'r1bqkbnr/pppppppp/2n5/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_after_move(Turn(WHITE, 1)),
                         'r1bqkbnr/pppppppp/2n5/1N6/8/8/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_after_move(Turn(BLACK, 1)),
                         'r1bqkbnr/pppppppp/8/1N6/1n6/8/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_after_move(Turn(WHITE, 2)),
                         'r1bqkbnr/pppppppp/3N4/8/1n6/8/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_after_move(Turn(BLACK, 2)),
                         'r1bqkbnr/pppppppp/3N4/8/8/3n4/PPPPPPPP/R1BQKBNR w KQkq -')
        self.assertEqual(self.history.truth_fen_after_move(Turn(WHITE, 3)),
                         'r1bqNbnr/pppppppp/8/8/8/3n4/PPPPPPPP/R1BQKBNR w KQkq -')

    def test_invalid_fen_after(self):
        with self.assertRaises(ValueError):
            self.history.truth_fen_after_move(Turn(WHITE, -1))
        with self.assertRaises(ValueError):
            self.history.truth_fen_after_move(Turn(WHITE, 4))
        with self.assertRaises(ValueError):
            self.history.truth_fen_after_move(Turn(BLACK, 3))

    def test_collect(self):
        self.assertEqual(list(self.history.collect(self.history.sense, self.history.turns(WHITE))), [E7, F7, G7, H7])
        self.assertEqual(list(self.history.collect(self.history.sense, self.history.turns(BLACK))), [E2, F2, G2])
        self.assertEqual(list(self.history.collect(self.history.sense, [Turn(WHITE, 0), Turn(BLACK, 0)])), [E7, E2])

    def test_invalid_collect(self):
        with self.assertRaises(ValueError):
            list(self.history.collect(id, self.history.turns()))


class HistorySaveTestCase(unittest.TestCase):
    def test_empty(self):
        history = GameHistory()
        with tempfile.TemporaryDirectory() as d:
            history.save(os.path.join(d, 'history.tsv'))
            restored_history = GameHistory.from_file(os.path.join(d, 'history.tsv'))
        self.assertEqual(history, restored_history)

    def test_one_turn(self):
        history = GameHistory()
        history.store_sense(WHITE, E7, [(D8, Piece(QUEEN, BLACK)), (F6, None)])
        history.store_move(WHITE, Move(E2, E3), Move(E2, E3), None)
        history.store_fen_before_move(WHITE, 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -')
        history.store_fen_after_move(WHITE, 'rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq -')

        with tempfile.TemporaryDirectory() as d:
            history.save(os.path.join(d, 'history.tsv'))
            restored_history = GameHistory.from_file(os.path.join(d, 'history.tsv'))

        self.assertEqual(restored_history._senses, {WHITE: [E7], BLACK: []})
        self.assertEqual(restored_history._sense_results, {WHITE: [[(D8, Piece(QUEEN, BLACK)), (F6, None)]], BLACK: []})
        self.assertEqual(restored_history._requested_moves, {WHITE: [Move(E2, E3)], BLACK: []})
        self.assertEqual(restored_history._taken_moves, {WHITE: [Move(E2, E3)], BLACK: []})
        self.assertEqual(restored_history._capture_squares, {WHITE: [None], BLACK: []})
        self.assertEqual(restored_history._fens_before_move,
                         {WHITE: ['rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'], BLACK: []})
        self.assertEqual(restored_history._fens_after_move,
                         {WHITE: ['rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq -'], BLACK: []})
        self.assertEqual(history, restored_history)

    def test_fuzz(self):
        winner_color, win_reason, history = play_local_game(RandomBot(), RandomBot())

        with tempfile.TemporaryDirectory() as d:
            history.save(os.path.join(d, 'history.tsv'))
            restored_history = GameHistory.from_file(os.path.join(d, 'history.tsv'))
        self.assertEqual(history, restored_history)
