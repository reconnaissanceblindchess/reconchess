import chess
from .types import *
from typing import Callable, TypeVar, Iterable, Mapping
import json
import math
from .utilities import ChessJSONEncoder, ChessJSONDecoder

T = TypeVar('T')


class Turn(object):
    """
    The representation of a single turn in a game. Contains the color of the player who played this turn, as well
    as the number of turns the player has taken so far.
    """

    def __init__(self, color: Color, turn_number: int):
        self.color = color
        self.turn_number = turn_number

    @property
    def next(self):
        """
        :return: The :class:`Turn` that happens immediately after this, which is the other player's next turn.
        """
        return Turn(not self.color, self.turn_number + (0 if self.color == chess.WHITE else 1))

    @property
    def previous(self):
        """
        :return: The :class: `Turn` that happens immediately before this, which is the other player's previous turn.
        """
        return Turn(not self.color, self.turn_number - (1 if self.color == chess.WHITE else 0))

    def __eq__(self, other):
        if not isinstance(other, Turn):
            return NotImplemented

        return self.color == other.color and self.turn_number == other.turn_number

    def __lt__(self, other):
        if not isinstance(other, Turn):
            return NotImplemented

        if self.turn_number < other.turn_number:
            return True
        elif self.turn_number > other.turn_number:
            return False
        else:
            return self.color == chess.WHITE and other.color == chess.BLACK

    def __le__(self, other):
        if not isinstance(other, Turn):
            return NotImplemented

        return self == other or self < other

    def __str__(self):
        return 'Turn({}, {})'.format(chess.COLOR_NAMES[self.color], self.turn_number)

    def __repr__(self):
        return str(self)


class GameHistory(object):
    """
    Implements method for processing and querying a Game.

    Here are some example uses:

    Extracting data to train a sensing policy to sense opponent: ::

        opponent_moves = history.collect(history.taken_move, history.turns(not self.color))
        target_senses = [move.to_square for move in opponent_moves]

    Extracting data to train a movement policy: ::

        for turn in history.turns(self.color):
            if history.has_move(turn):
                move = history.requested_move(turn)
                board = history.truth_board_before_move(turn)
                # do something with move and board...

    Randomly sampling from the turns instead of using them in sequential order: ::

        for turn in random.sample(history.turns(self.color), N):
            ...

    Giving rewards based on validity of the move: ::

        for turn in history.turns(self.color):
            if history.has_move(turn):
                if history.requested_move(turn) != history.taken_move(turn):
                    reward = -1
                else:
                    reward = 1

    Giving rewards for moving out of check: ::

        for turn in history.turns(self.color):
            if history.has_move(turn):
                board_before = history.truth_board_before_move(turn)
                board_after = history.truth_board_after_move(turn)

                if board_before.is_check() and not board_after.is_check()
                    reward = 1
                else:
                    reward = -1

    """

    def __init__(self):
        self._white_name = None
        self._black_name = None
        self._senses = {chess.WHITE: [], chess.BLACK: []}
        self._sense_results = {chess.WHITE: [], chess.BLACK: []}
        self._requested_moves = {chess.WHITE: [], chess.BLACK: []}
        self._taken_moves = {chess.WHITE: [], chess.BLACK: []}
        self._capture_squares = {chess.WHITE: [], chess.BLACK: []}
        self._fens_before_move = {chess.WHITE: [], chess.BLACK: []}
        self._fens_after_move = {chess.WHITE: [], chess.BLACK: []}
        self._winner_color = None
        self._win_reason = None

    def save(self, filename):
        """
        Save the game history to a json file.

        :param filename: The file to save to.
        """
        with open(filename, 'w', newline='') as fp:
            json.dump(self, fp, cls=GameHistoryEncoder)

    @classmethod
    def from_file(cls, filename):
        """
        :param filename: The json file to load the :class:`GameHistory` object from.
        :return: The :class:`GameHistory` object that was originally saved to the file using :meth:`save`.
        """
        with open(filename, newline='') as fp:
            return json.load(fp, cls=GameHistoryDecoder)

    def store_players(self, white_name: str, black_name: str):
        self._white_name = white_name
        self._black_name = black_name

    def store_sense(self, color: Color, square: Optional[Square],
                    sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        self._senses[color].append(square)
        self._sense_results[color].append(sense_result)

    def store_move(self, color: Color, requested_move: Optional[chess.Move],
                   taken_move: Optional[chess.Move], opt_capture_square: Optional[Square]):
        self._requested_moves[color].append(requested_move)
        self._taken_moves[color].append(taken_move)
        self._capture_squares[color].append(opt_capture_square)

    def store_fen_before_move(self, color: Color, fen: str):
        self._fens_before_move[color].append(fen)

    def store_fen_after_move(self, color: Color, fen: str):
        self._fens_after_move[color].append(fen)

    def store_results(self, winner_color: Optional[Color], win_reason: Optional[WinReason]):
        self._winner_color = winner_color
        self._win_reason = win_reason

    def get_white_player_name(self) -> str:
        """
        Get the name of white.
        :return: str
        """
        return self._white_name

    def get_black_player_name(self) -> str:
        """
        Get the name of black.
        :return: str
        """
        return self._black_name

    def is_empty(self) -> bool:
        """
        Get whether or not the game had any turns in it.

        Examples:
            >>> history.is_empty()
            False

        :return: `True` if there are no turns to query in this object, `False` otherwise.
        """
        return len(self._senses[chess.WHITE]) == 0

    def num_turns(self, color: Color = None) -> int:
        """
        Get the number of turns taken in the game. Optionally specify the color of the player to get the number of turns
        for.

        Examples:
            >>> history.num_turns()
            9

            >>> history.num_turns(WHITE)
            5

            >>> history.num_turns(BLACK)
            4

        :param color: Optional player color indicating which player's number of turns to return.
        :return: The number of turns saved in this object. If `color` is specified, get the number of turns for that
            player.
        """
        return len(list(self.turns(color=color)))

    def turns(self, color: Color = None, start=0, stop=math.inf) -> Iterable[Turn]:
        """
        Get all the turns that happened in the game in order. Optionally specify a single player to get only that
        player's turns.

        Examples:
            >>> list(history.turns())
            [Turn(WHITE, 0), Turn(BLACK, 0), Turn(WHITE, 1), ..., Turn(BLACK, 23)]

            >>> list(history.turns(WHITE))
            [Turn(WHITE, 0), Turn(WHITE, 1), ..., Turn(WHITE, 22)]

            >>> list(history.turns(BLACK))
            [Turn(BLACK, 0), Turn(BLACK, 1), ..., Turn(BLACK, 23)]

            >>> list(history.turns(start=1))
            [Turn(WHITE, 1), Turn(BLACK, 1), Turn(WHITE, 2), ..., Turn(BLACK, 23)]

            >>> list(history.turns(stop=2))
            [Turn(WHITE, 0), Turn(BLACK, 0), Turn(WHITE, 1), Turn(BLACK, 1)]

            >>> list(history.turns(WHITE, stop=2))
            [Turn(WHITE, 0), Turn(WHITE, 1)]

            >>> list(history.turns(start=1, stop=2))
            [Turn(WHITE, 1), Turn(BLACK, 1)]

        :param color: Optional player color indicating which player's turns to return.
        :param start: Optional starting turn number.
        :param stop: Optional stopping turn number.
        :return: An iterable of :class:`Turn` objects that are in the same order as they occurred in the game. If
            `color` is specified, gets the turns only for that player.
        """
        if self.is_empty():
            return

        turn = Turn(color if color is not None else chess.WHITE, start)
        stop_turn = Turn(color if color is not None else chess.WHITE, stop)
        last_turn = self.last_turn()
        while turn <= last_turn and turn < stop_turn:
            if color is None or turn.color == color:
                yield turn
            turn = turn.next

    def is_first_turn(self, turn: Turn):
        """
        Checks whether `turn` is the first turn of the game.

        Examples:
            >>> history.is_first_turn(Turn(BLACK, 0))
            False

            >>> history.is_first_turn(Turn(WHITE, 0))
            True

        :param turn: the :class:`Turn` in question.
        :return: `True` if `turn` is the first turn in the game, `False` otherwise.
        """
        return turn == self.first_turn()

    def first_turn(self, color: Color = None) -> Turn:
        """
        Gets the first turn of the game.

        Examples:
            >>> history.first_turn()
            Turn(WHITE, 0)

            >>> history.first_turn(WHITE)
            Turn(WHITE, 0)

            >>> history.first_turn(BLACK)
            Turn(BLACK, 0)

        :param color: Optional color indicating which player's first turn to return.
        :return: The :class:`Turn` that is the first turn in the game.
        """
        if self.is_empty():
            raise ValueError('GameHistory is empty')

        return Turn(color if color is not None else chess.WHITE, 0)

    def is_last_turn(self, turn: Turn):
        """
        Checks whether `turn` is the last turn of the game.

        Examples:
            >>> history.is_last_turn(Turn(BLACK, 23))
            False

            >>> history.is_last_turn(Turn(WHITE, 24))
            True

        :param turn: the :class:`Turn` in question.
        :return: `True` if `turn` is the last turn in the game, `False` otherwise.
        """
        return turn == self.last_turn()

    def last_turn(self, color: Color = None) -> Turn:
        """
        Gets the last turn of the game.

        Examples:
            >>> history.last_turn()
            Turn(WHITE, 24)

            >>> history.first_turn(WHITE)
            Turn(WHITE, 24)

            >>> history.first_turn(BLACK)
            Turn(BLACK, 23)

        :param color: Optional color indicating which player's last turn to return.
        :return: The :class:`Turn` that is the last turn in the game.
        """
        if self.is_empty():
            raise ValueError('GameHistory is empty')

        if color is not None:
            return Turn(color, len(self._senses[color]) - 1)
        else:
            num_white_turns = len(self._senses[chess.WHITE])
            num_black_turns = len(self._senses[chess.BLACK])
            if num_white_turns > num_black_turns:
                return Turn(chess.WHITE, num_white_turns - 1)
            else:
                return Turn(chess.BLACK, num_black_turns - 1)

    def get_winner_color(self) -> Optional[Color]:
        """
        Returns the color of the player who won the game. If the game is not over, or is over but does not have a winner
         then this will return `None`.

        :return: :class:`Color` of the winner if the game has ended and has a winner, otherwise `None`.
        """
        return self._winner_color

    def get_win_reason(self) -> Optional[WinReason]:
        """
        Returns the reason the player who won won the game. If the game is not over, or is over but does not have a
        winner, then this will return `None`.

        :return: :class:`WinReason` of the winner if the game has ended and has a winner, otherwise `None`.
        """
        return self._win_reason

    def _validate_turn(self, turn: Turn, collection: Mapping[Color, List[T]]):
        if turn.turn_number < 0 or turn.turn_number >= len(collection[turn.color]):
            raise ValueError('{} did not happen in this game.'.format(turn))

    def has_sense(self, turn: Turn) -> bool:
        """
        Checks to see if the game has a sense action for the specified turn. The game may not if it ended because of
        timeout.

        This intended use is to call this before calling :meth:`sense` and :meth:`sense_result`, to verify that there
        is a sense before querying for it.

        Examples:
            >>> history.has_sense(Turn(WHITE, 0))
            True

            >>> history.has_sense(Turn(WHITE, 432))
            False

        :param turn: The :class:`Turn` in question.
        :return: `True` if there is a sense action, `False` otherwise.
        """
        return 0 <= turn.turn_number < len(self._senses[turn.color])

    def sense(self, turn: Turn) -> Optional[Square]:
        """
        Get the sense action on the given turn.

        Examples:
            >>> history.sense(Turn(WHITE, 0))
            E7

            >>> history.sense(Turn(BLACK, 0))
            E2

            >>> history.sense(Turn(WHITE, 1))
            None

        :param turn: The :class:`Turn` in question.
        :return: The executed sense action as a :class:`Square`.
        """
        self._validate_turn(turn, self._senses)
        return self._senses[turn.color][turn.turn_number]

    def sense_result(self, turn: Turn) -> List[Tuple[Square, Optional[chess.Piece]]]:
        """
        Get the result of the sense action on the given turn.

        Examples:
            >>> history.sense(Turn(WHITE, 0))
            B7
            >>> history.sense_result(Turn(WHITE, 0))
            [
                (A8, Piece(ROOK, BLACK)), (B8, Piece(KNIGHT, BLACK)), (C8, Piece(BISHOP, BLACK)),
                (A7, Piece(PAWN, BLACK)), (B7, Piece(PAWN, BLACK)), (C7, Piece(PAWN, BLACK)),
                (A6, None), (B6, None), (C8, None)
            ]
            >>> history.sense(Turn(BLACK, 0))
            None
            >>> history.sense_result(Turn(BLACK, 0))
            []

        :param turn: The :class:`Turn` in question.
        :return: The result of the executed sense action.
        """
        self._validate_turn(turn, self._sense_results)
        return self._sense_results[turn.color][turn.turn_number]

    def has_move(self, turn: Turn) -> bool:
        """
        Checks to see if the game has a move action for the specified turn. The game may not if it ended because of
        timeout.

        This intended use is to call this before calling :meth:`requested_move`, :meth:`taken_move`,
        :meth:`capture_square`, and :meth:`move_result` to verify that there is a move before querying for it.

        Examples:
            >>> history.has_move(Turn(WHITE, 0))
            True

            >>> history.has_move(Turn(WHITE, 432))
            False

        :param turn: The :class:`Turn` in question.
        :return: `True` if there is a move action, `False` otherwise.
        """
        return 0 <= turn.turn_number < len(self._requested_moves[turn.color])

    def requested_move(self, turn: Turn) -> Optional[chess.Move]:
        """
        Get the requested move action on the given turn.

        Examples:
            >>> history.requested_move(Turn(WHITE, 0))
            Move(E2, E4)

            >>> history.requested_move(Turn(BLACK, 0))
            Move(E7, E5)

            >>> history.requested_move(Turn(WHITE, 1))
            None

        :param turn: The :class:`Turn` in question.
        :return: If the player requested to move, then the requested move action as a :class:`chess.Move`, otherwise
            `None` if the player requested to pass.
        """
        self._validate_turn(turn, self._requested_moves)
        return self._requested_moves[turn.color][turn.turn_number]

    def taken_move(self, turn: Turn) -> Optional[chess.Move]:
        """
        Get the executed move action on the given turn. This may be different than the requested move, as the requested
        move may not be legal.

        Examples:
            >>> history.requested_move(Turn(WHITE, 0))
            Move(E2, D3)
            >>> history.taken_move(Turn(WHITE, 0))
            None

            >>> history.requested_move(Turn(WHITE, 1))
            Move(E2, E4)
            >>> history.taken_move(Turn(WHITE, 1))
            Move(E2, E3)

        :param turn: The :class:`Turn` in question.
        :return: `None` if the player requested to pass or made an illegal move, the executed move action as a
            :class:`chess.Move` otherwise.
        """
        self._validate_turn(turn, self._taken_moves)
        return self._taken_moves[turn.color][turn.turn_number]

    def capture_square(self, turn: Turn) -> Optional[Square]:
        """
        Get the square of the opponent's captured piece on the given turn. A capture may not have occurred, in which
        case `None` will be returned.

        Examples:
            >>> history.capture_square(Turn(WHITE, 0))
            None

            >>> history.capture_square(Turn(WHITE, 4))
            E4

        :param turn: The :class:`Turn` in question.
        :return: If a capture occurred, then the :class:`Square` where it occurred, otherwise `None`.
        """
        self._validate_turn(turn, self._capture_squares)
        return self._capture_squares[turn.color][turn.turn_number]

    def move_result(self, turn: Turn) -> Tuple[Optional[chess.Move], Optional[chess.Move], Optional[Square]]:
        """
        Get the full move result in one function. Calls :meth:`requested_move`, :meth:`taken_move`, and
        :meth:`capture_square`.

        Examples:
            >>> history.move_result(Turn(WHITE, 0))
            (Move(E2, E4), Move(E2, E3), None)

        :param turn: The :class:`Turn` in question.
        :return: The requested move, the executed move, and a capture square if there was one.
        """
        return self.requested_move(turn), self.taken_move(turn), self.capture_square(turn)

    def truth_fen_before_move(self, turn: Turn) -> str:
        """
        Get the truth state of the board as a fen string before the move was executed on the given turn. Use
        :meth:`truth_board_before_move` if you want the truth board as a :class:`chess.Board` object.

        Examples:
            >>> history.truth_fen_before_move(Turn(WHITE, 0))
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
            >>> history.taken_move(Turn(WHITE, 0))
            Move(E2, E4)
            >>> history.truth_fen_before_move(Turn(BLACK, 0))
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -"

        :param turn: The :class:`Turn` in question.
        :return: The fen of the truth board.
        """
        self._validate_turn(turn, self._fens_before_move)
        return self._fens_before_move[turn.color][turn.turn_number]

    def truth_board_before_move(self, turn: Turn) -> chess.Board:
        """
        Get the truth state of the board as a :class:`chess.Board` before the move was executed on the given turn. Use
        :meth:`truth_fen_before_move` if you want the truth board as a fen string.

        Examples:
            >>> history.truth_board_before_move(Turn(WHITE, 0))
            Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")
            >>> history.taken_move(Turn(WHITE, 0))
            Move(E2, E4)
            >>> history.truth_fen_before_move(Turn(BLACK, 0))
            Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -")

        :param turn: The :class:`Turn` in question.
        :return: A :class:`chess.Board` object.
        """
        self._validate_turn(turn, self._fens_before_move)
        board = chess.Board(self._fens_before_move[turn.color][turn.turn_number])
        board.turn = turn.color
        return board

    def truth_fen_after_move(self, turn: Turn) -> str:
        """
        Get the truth state of the board as a fen string after the move was executed on the given turn. Use
        :meth:`truth_board_after_move` if you want the truth board as a :class:`chess.Board` object.

        Examples:
            >>> history.truth_fen_before_move(Turn(WHITE, 0))
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"
            >>> history.taken_move(Turn(WHITE, 0))
            Move(E2, E4)
            >>> history.truth_fen_after_move(Turn(WHITE, 0))
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -"

        :param turn: The :class:`Turn` in question.
        :return: The fen of the truth board.
        """
        self._validate_turn(turn, self._fens_after_move)
        return self._fens_after_move[turn.color][turn.turn_number]

    def truth_board_after_move(self, turn: Turn) -> chess.Board:
        """
        Get the truth state of the board as a :class:`chess.Board` after the move was executed on the given turn. Use
        :meth:`truth_fen_after_move` if you want the truth board as a fen string.

        Examples:
            >>> history.truth_board_before_move(Turn(WHITE, 0))
            Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -")
            >>> history.taken_move(Turn(WHITE, 0))
            Move(E2, E4)
            >>> history.truth_fen_after_move(Turn(WHITE, 0))
            Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -")

        :param turn: The :class:`Turn` in question.
        :return: A :class:`chess.Board` object.
        """
        self._validate_turn(turn, self._fens_after_move)
        board = chess.Board(self._fens_after_move[turn.color][turn.turn_number])
        board.turn = turn.color
        return board

    def collect(self, get_turn_data_fn: Callable[[Turn], T], turns: Iterable[Turn]) -> Iterable[T]:
        """
        Collect data from multiple turns using any of :meth:`sense`, :meth:`sense_result`, :meth:`requested_move`,
        :meth:`taken_move`, :meth:`capture_square`, :meth:`move_result`, :meth:`truth_fen_before_move`,
        :meth:`truth_board_before_move`, :meth:`truth_fen_after_move`, or :meth:`truth_board_after_move`.

        Examples:
            >>> history.collect(history.sense, [Turn(WHITE, 0), Turn(BLACK, 0)])
            [E7, E2]

            >>> history.collect(history.requested_move, history.turns(WHITE))
            [Move(E2, E4), Move(D1, H5), ...]

        :param get_turn_data_fn: One of the getter functions of the history object.
        :param turns: The turns in question.
        :return: A list of the data, where each element is the value of the getter function on the corresponding turn.
        """
        if get_turn_data_fn not in [self.sense, self.sense_result, self.requested_move, self.taken_move,
                                    self.capture_square, self.move_result, self.truth_board_before_move,
                                    self.truth_board_after_move, self.truth_fen_before_move, self.truth_fen_after_move]:
            raise ValueError('get_turn_data_fn must be one of the history getter functions')
        for turn in turns:
            yield get_turn_data_fn(turn)

    def __eq__(self, other):
        if not isinstance(other, GameHistory):
            return NotImplemented

        senses_equal = self._senses == other._senses and self._sense_results == other._sense_results
        moves_equal = self._requested_moves == other._requested_moves and self._taken_moves == other._taken_moves and self._capture_squares == other._capture_squares
        fens_equal = self._fens_before_move == other._fens_before_move and self._fens_after_move == other._fens_after_move
        results_equal = self._win_reason == other._win_reason and self._winner_color == other._winner_color

        return senses_equal and moves_equal and fens_equal and results_equal


class GameHistoryEncoder(ChessJSONEncoder):
    def default(self, o):
        if isinstance(o, GameHistory):
            return {
                'type': 'GameHistory',
                'white_name': o._white_name,
                'black_name': o._black_name,
                'senses': o._senses,
                'sense_results': o._sense_results,
                'requested_moves': o._requested_moves,
                'taken_moves': o._taken_moves,
                'capture_squares': o._capture_squares,
                'fens_before_move': o._fens_before_move,
                'fens_after_move': o._fens_after_move,
                'winner_color': o._winner_color,
                'win_reason': o._win_reason,
            }
        return super().default(o)


class GameHistoryDecoder(ChessJSONDecoder):
    def _object_hook(self, obj):
        if 'type' in obj and obj['type'] == 'GameHistory':
            for key in ['senses', 'sense_results', 'requested_moves', 'taken_moves', 'capture_squares',
                        'fens_before_move', 'fens_after_move']:
                obj[key] = {True: obj[key]['true'], False: obj[key]['false']}
            history = GameHistory()
            history._white_name = obj['white_name']
            history._black_name = obj['black_name']
            history._senses = obj['senses']
            history._sense_results = obj['sense_results']
            history._requested_moves = obj['requested_moves']
            history._taken_moves = obj['taken_moves']
            history._capture_squares = obj['capture_squares']
            history._fens_before_move = obj['fens_before_move']
            history._fens_after_move = obj['fens_after_move']
            history._winner_color = obj['winner_color']
            history._win_reason = obj['win_reason']

            for color, sense_results in history._sense_results.items():
                for result in sense_results:
                    for i in range(len(result)):
                        result[i] = tuple(result[i])
            return history

        return super()._object_hook(obj)
