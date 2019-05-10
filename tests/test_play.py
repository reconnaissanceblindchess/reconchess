import unittest
from chess import *
from collections import defaultdict
from reconchess import *
import random


def clean_locals(d):
    del d['self']
    if '__class__' in d:
        del d['__class__']
    return d


class TestGame(LocalGame):
    def __init__(self):
        super().__init__()

        self.params_by_function = defaultdict(list)
        self.call_order = []

    def sense_actions(self) -> List[Square]:
        self.params_by_function['sense_actions'].append(clean_locals(locals()))
        self.call_order.append('sense_actions')
        return super().sense_actions()

    def move_actions(self) -> List[chess.Move]:
        self.params_by_function['move_actions'].append(clean_locals(locals()))
        self.call_order.append('move_actions')
        return super().move_actions()

    def get_seconds_left(self) -> float:
        self.params_by_function['get_seconds_left'].append(clean_locals(locals()))
        self.call_order.append('get_seconds_left')
        return super().get_seconds_left()

    def start(self):
        self.params_by_function['start'].append(clean_locals(locals()))
        self.call_order.append('start')
        super().start()

    def opponent_move_results(self) -> Optional[Square]:
        self.params_by_function['opponent_move_results'].append(clean_locals(locals()))
        self.call_order.append('opponent_move_results')
        return super().opponent_move_results()

    def sense(self, square: Square) -> List[Tuple[Square, Optional[chess.Piece]]]:
        self.params_by_function['sense'].append(clean_locals(locals()))
        self.call_order.append('sense')
        return super().sense(square)

    def move(self, requested_move: Optional[chess.Move]) -> Tuple[
        Optional[chess.Move], Optional[chess.Move], Optional[Square]]:
        self.params_by_function['move'].append(clean_locals(locals()))
        self.call_order.append('move')
        return super().move(requested_move)

    def end_turn(self):
        self.params_by_function['end_turn'].append(clean_locals(locals()))
        self.call_order.append('end_turn')
        super().end_turn()

    def is_over(self) -> bool:
        self.params_by_function['is_over'].append(clean_locals(locals()))
        self.call_order.append('is_over')
        return super().is_over()


class TestPlayer(Player):
    def __init__(self, senses, moves):
        self.senses = senses
        self.moves = moves

        self.params_by_function = defaultdict(list)
        self.call_order = []

    def handle_game_start(self, color: Color, board: Board):
        self.params_by_function['handle_game_start'].append(clean_locals(locals()))
        self.call_order.append('handle_game_start')

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        self.params_by_function['handle_opponent_move_result'].append(clean_locals(locals()))
        self.call_order.append('handle_opponent_move_result')

    def choose_sense(self, sense_actions: List[Square], move_actions: List[Move], seconds_left: float) -> Square:
        self.params_by_function['choose_sense'].append(clean_locals(locals()))
        self.call_order.append('choose_sense')
        if len(self.senses) > 0:
            return self.senses.pop(0)
        else:
            return random.choice(sense_actions)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[Piece]]]):
        self.params_by_function['handle_sense_result'].append(clean_locals(locals()))
        self.call_order.append('handle_sense_result')

    def choose_move(self, move_actions: List[Move], seconds_left: float) -> Optional[Move]:
        self.params_by_function['choose_move'].append(clean_locals(locals()))
        self.call_order.append('choose_move')
        if len(self.moves) > 0:
            return self.moves.pop(0)
        else:
            return random.choice(move_actions)

    def handle_move_result(self, requested_move: Optional[Move], taken_move: Optional[Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        self.params_by_function['handle_move_result'].append(clean_locals(locals()))
        self.call_order.append('handle_move_result')

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        history: GameHistory):
        self.params_by_function['handle_game_end'].append(clean_locals(locals()))
        self.call_order.append('handle_game_end')


class NotifyOpponentMoveResultsTestCase(unittest.TestCase):
    def setUp(self):
        self.game = TestGame()
        self.game.start()
        self.player = TestPlayer([], [])

    def test_call_order(self):
        notify_opponent_move_results(self.game, self.player)
        self.assertEqual(self.player.call_order, ['handle_opponent_move_result'])
        self.assertEqual(self.game.call_order, ['start', 'opponent_move_results'])

    def test_params_no_capture(self):
        notify_opponent_move_results(self.game, self.player)
        self.assertEqual(self.player.params_by_function['handle_opponent_move_result'], [{
            'captured_my_piece': False,
            'capture_square': None,
        }])

    def test_params_capture(self):
        """
        r n b q k b n r
        p p p p p p p p
        . . . . P . . .
        . . . . . . . .
        . . . . . . . .
        . . . . . . . .
        P P P P . P P P
        R N B Q K B N R
        """
        self.game.board.set_board_fen('rnbqkbnr/pppppppp/4P3/8/8/8/PPPP1PPP/RNBQKBNR')
        self.game.move(Move(E6, D7))
        notify_opponent_move_results(self.game, self.player)
        self.assertEqual(self.player.params_by_function['handle_opponent_move_result'], [{
            'captured_my_piece': True,
            'capture_square': D7,
        }])


class PlaySenseTestCase(unittest.TestCase):
    def setUp(self):
        self.game = TestGame()
        self.game.start()
        self.player = TestPlayer([E7], [])
        self.sense_actions = self.game.sense_actions()
        self.move_actions = self.game.move_actions()
        play_sense(self.game, self.player, self.sense_actions, self.move_actions)

    def test_call_order(self):
        self.assertEqual(self.player.call_order, ['choose_sense', 'handle_sense_result'])
        self.assertEqual(self.game.call_order,
                         ['start', 'sense_actions', 'move_actions', 'get_seconds_left', 'sense', 'sense_actions'])

    def test_player_params(self):
        self.assertEqual(self.player.params_by_function['choose_sense'], [{
            'seconds_left': self.player.params_by_function['choose_sense'][0]['seconds_left'],
            'sense_actions': list(chess.SQUARES),
            'move_actions': self.move_actions,
        }])

        self.assertEqual(self.player.params_by_function['handle_sense_result'], [{
            'sense_result': [(D8, Piece(QUEEN, BLACK)), (E8, Piece(KING, BLACK)), (F8, Piece(BISHOP, BLACK)),
                             (D7, Piece(PAWN, BLACK)), (E7, Piece(PAWN, BLACK)), (F7, Piece(PAWN, BLACK)),
                             (D6, None), (E6, None), (F6, None)],
        }])

    def test_game_params(self):
        self.assertEqual(self.game.params_by_function['sense'], [{
            'square': E7
        }])


class PlayMoveTestCase(unittest.TestCase):
    def setUp(self):
        self.game = TestGame()
        self.game.start()
        self.player = TestPlayer([E7], [Move(E2, E4)])
        self.move_actions = self.game.move_actions()
        play_move(self.game, self.player, self.move_actions)

    def test_call_order(self):
        self.assertEqual(self.player.call_order, ['choose_move', 'handle_move_result'])
        self.assertEqual(self.game.call_order,
                         ['start', 'move_actions', 'get_seconds_left', 'move', 'move_actions', 'end_turn'])

    def test_player_params(self):
        self.assertEqual(self.player.params_by_function['choose_move'], [{
            'seconds_left': self.player.params_by_function['choose_move'][0]['seconds_left'],
            'move_actions': self.move_actions,
        }])

        self.assertEqual(self.player.params_by_function['handle_move_result'], [{
            'requested_move': Move(E2, E4),
            'taken_move': Move(E2, E4),
            'captured_opponent_piece': False,
            'capture_square': None,
        }])

    def test_game_params(self):
        self.assertEqual(self.game.params_by_function['move'], [{
            'requested_move': Move(E2, E4)
        }])


class PlayTurnTestCase(unittest.TestCase):
    def setUp(self):
        self.game = TestGame()
        self.game.start()
        self.player = TestPlayer([E7], [Move(E2, E4)])
        self.move_actions = self.game.move_actions()
        play_turn(self.game, self.player)

    def test_call_order(self):
        self.assertEqual(self.player.call_order, ['handle_opponent_move_result', 'choose_sense', 'handle_sense_result',
                                                  'choose_move', 'handle_move_result'])
        self.assertEqual(self.game.call_order,
                         ['start', 'move_actions', 'sense_actions', 'move_actions', 'opponent_move_results',
                          'get_seconds_left', 'sense', 'sense_actions', 'get_seconds_left', 'move', 'move_actions',
                          'end_turn'])

    def test_player_opponent_move_results_params(self):
        self.assertEqual(self.player.params_by_function['handle_opponent_move_result'], [{
            'captured_my_piece': False,
            'capture_square': None,
        }])

    def test_player_sense_params(self):
        self.assertEqual(self.player.params_by_function['choose_sense'], [{
            'seconds_left': self.player.params_by_function['choose_sense'][0]['seconds_left'],
            'sense_actions': list(SQUARES),
            'move_actions': self.move_actions,
        }])

    def test_game_sense_params(self):
        self.assertEqual(self.game.params_by_function['sense'], [{
            'square': E7,
        }])

    def test_player_sense_result_params(self):
        self.assertEqual(self.player.params_by_function['handle_sense_result'], [{
            'sense_result': [(D8, Piece(QUEEN, BLACK)), (E8, Piece(KING, BLACK)), (F8, Piece(BISHOP, BLACK)),
                             (D7, Piece(PAWN, BLACK)), (E7, Piece(PAWN, BLACK)), (F7, Piece(PAWN, BLACK)),
                             (D6, None), (E6, None), (F6, None)],
        }])

    def test_player_move_params(self):
        self.assertEqual(self.player.params_by_function['choose_move'], [{
            'seconds_left': self.player.params_by_function['choose_move'][0]['seconds_left'],
            'move_actions': self.move_actions,
        }])

    def test_game_move_params(self):
        self.assertEqual(self.game.params_by_function['move'], [{
            'requested_move': Move(E2, E4),
        }])

    def test_player_move_result_params(self):
        self.assertEqual(self.player.params_by_function['handle_move_result'], [{
            'requested_move': Move(E2, E4),
            'taken_move': Move(E2, E4),
            'captured_opponent_piece': False,
            'capture_square': None,
        }])


class PlayLocalGameTestCase(unittest.TestCase):
    def setUp(self):
        self.white_player = TestPlayer([], [])
        self.black_player = TestPlayer([], [])
        self.winner_color, self.win_reason, self.history = play_local_game(self.white_player, self.black_player)

    def test_white_call_order(self):
        turns = self.history.num_turns(WHITE)
        turn_order = ['handle_opponent_move_result', 'choose_sense', 'handle_sense_result',
                      'choose_move', 'handle_move_result']

        expected_order = ['handle_game_start'] + turn_order * turns + ['handle_game_end']
        self.assertEqual(self.white_player.call_order, expected_order)

    def test_black_call_order(self):
        turns = self.history.num_turns(BLACK)
        turn_order = ['handle_opponent_move_result', 'choose_sense', 'handle_sense_result',
                      'choose_move', 'handle_move_result']

        expected_order = ['handle_game_start'] + turn_order * turns + ['handle_game_end']
        self.assertEqual(self.black_player.call_order, expected_order)

    def test_white_params(self):
        self.assertEqual(self.white_player.params_by_function['handle_game_start'], [{
            'color': WHITE,
            'board': chess.Board(),
        }])

        self.assertEqual(self.white_player.params_by_function['handle_game_end'], [{
            'winner_color': self.winner_color,
            'win_reason': self.win_reason,
            'history': self.history,
        }])

    def test_black_params(self):
        self.assertEqual(self.black_player.params_by_function['handle_game_start'], [{
            'color': BLACK,
            'board': chess.Board(),
        }])

        self.assertEqual(self.black_player.params_by_function['handle_game_end'], [{
            'winner_color': self.winner_color,
            'win_reason': self.win_reason,
            'history': self.history,
        }])
