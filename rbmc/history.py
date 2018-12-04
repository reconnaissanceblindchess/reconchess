import chess
from .types import *
from typing import Callable, TypeVar, Iterable, Mapping
import json

T = TypeVar('T')


class Turn(object):
    def __init__(self, color: Color, turn_number: int):
        self.color = color
        self.turn_number = turn_number

    @property
    def next(self):
        return Turn(not self.color, self.turn_number + (0 if self.color == chess.WHITE else 1))

    @property
    def previous(self):
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

    def __str__(self):
        return 'Turn({}, {})'.format(chess.COLOR_NAMES[self.color], self.turn_number)

    def __repr__(self):
        return str(self)


class GameHistory(object):
    def __init__(self):
        self._senses = {chess.WHITE: [], chess.BLACK: []}
        self._sense_results = {chess.WHITE: [], chess.BLACK: []}
        self._requested_moves = {chess.WHITE: [], chess.BLACK: []}
        self._taken_moves = {chess.WHITE: [], chess.BLACK: []}
        self._capture_squares = {chess.WHITE: [], chess.BLACK: []}
        self._fens_before_move = {chess.WHITE: [], chess.BLACK: []}
        self._fens_after_move = {chess.WHITE: [], chess.BLACK: []}

    def save(self, filename):
        with open(filename, 'w', newline='') as fp:
            json.dump(self, fp, cls=GameHistoryEncoder)

    @classmethod
    def from_file(cls, filename):
        with open(filename, newline='') as fp:
            obj = json.load(fp, cls=GameHistoryDecoder)
        if 'type' not in obj or obj['type'] != 'GameHistory':
            raise ValueError('No GameHistory object found in {}'.format(filename))
        history = cls()
        history._senses = obj['senses']
        history._sense_results = obj['sense_results']
        history._requested_moves = obj['requested_moves']
        history._taken_moves = obj['taken_moves']
        history._capture_squares = obj['capture_squares']
        history._fens_before_move = obj['fens_before_move']
        history._fens_after_move = obj['fens_after_move']

        for color, sense_results in history._sense_results.items():
            for result in sense_results:
                for i in range(len(result)):
                    result[i] = tuple(result[i])
        return history

    def store_sense(self, color: Color, square: Square,
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

    def is_empty(self) -> bool:
        return len(self._senses[chess.WHITE]) == 0

    def num_turns(self, color: Color = None) -> int:
        return len(list(self.turns(color=color)))

    def turns(self, color: Color = None) -> Iterable[Turn]:
        if self.is_empty():
            return

        turn = Turn(color if color is not None else chess.WHITE, 0)
        while True:
            if color is None or turn.color == color:
                yield turn
            if self.is_last_turn(turn):
                return
            turn = turn.next

    def is_first_turn(self, turn: Turn):
        return turn == self.first_turn()

    def first_turn(self, color: Color = None) -> Turn:
        if self.is_empty():
            raise ValueError('GameHistory is empty')

        return Turn(color if color is not None else chess.WHITE, 0)

    def is_last_turn(self, turn: Turn):
        return turn == self.last_turn()

    def last_turn(self, color: Color = None) -> Turn:
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

    def _validate_turn(self, turn: Turn, collection: Mapping[Color, List[T]]):
        if turn.turn_number < 0 or turn.turn_number >= len(collection[turn.color]):
            raise ValueError('{} did not happen in this game.'.format(turn))

    def has_sense(self, turn: Turn) -> bool:
        return 0 <= turn.turn_number < len(self._senses[turn.color])

    def sense(self, turn: Turn) -> Square:
        self._validate_turn(turn, self._senses)
        return self._senses[turn.color][turn.turn_number]

    def sense_result(self, turn: Turn) -> List[Tuple[Square, Optional[chess.Piece]]]:
        self._validate_turn(turn, self._sense_results)
        return self._sense_results[turn.color][turn.turn_number]

    def has_move(self, turn: Turn) -> bool:
        return 0 <= turn.turn_number < len(self._requested_moves[turn.color])

    def requested_move(self, turn: Turn) -> Optional[chess.Move]:
        self._validate_turn(turn, self._requested_moves)
        return self._requested_moves[turn.color][turn.turn_number]

    def taken_move(self, turn: Turn) -> Optional[chess.Move]:
        self._validate_turn(turn, self._taken_moves)
        return self._taken_moves[turn.color][turn.turn_number]

    def capture_square(self, turn: Turn) -> Optional[chess.Move]:
        self._validate_turn(turn, self._capture_squares)
        return self._capture_squares[turn.color][turn.turn_number]

    def move_result(self, turn: Turn) -> Tuple[Optional[chess.Move], Optional[chess.Move], Optional[Square]]:
        return self.requested_move(turn), self.taken_move(turn), self.capture_square(turn)

    def truth_fen_before_move(self, turn: Turn) -> str:
        self._validate_turn(turn, self._fens_before_move)
        return self._fens_before_move[turn.color][turn.turn_number]

    def truth_board_before_move(self, turn: Turn) -> chess.Board:
        self._validate_turn(turn, self._fens_before_move)
        return chess.Board(self._fens_before_move[turn.color][turn.turn_number])

    def truth_fen_after_move(self, turn: Turn) -> str:
        self._validate_turn(turn, self._fens_after_move)
        return self._fens_after_move[turn.color][turn.turn_number]

    def truth_board_after_move(self, turn: Turn) -> chess.Board:
        self._validate_turn(turn, self._fens_after_move)
        return chess.Board(self._fens_after_move[turn.color][turn.turn_number])

    def collect(self, get_turn_data_fn: Callable[[Turn], T], turns: Iterable[Turn]) -> List[T]:
        if get_turn_data_fn not in [self.sense, self.sense_result, self.requested_move, self.taken_move,
                                    self.capture_square, self.move_result, self.truth_board_before_move,
                                    self.truth_board_after_move, self.truth_fen_before_move, self.truth_fen_after_move]:
            raise ValueError('get_turn_data_fn must be one of the history getter functions')
        return list(map(get_turn_data_fn, turns))

    def __eq__(self, other):
        if not isinstance(other, GameHistory):
            return NotImplemented

        senses_equal = self._senses == other._senses and self._sense_results == other._sense_results
        moves_equal = self._requested_moves == other._requested_moves and self._taken_moves == other._taken_moves and self._capture_squares == other._capture_squares
        fens_equal = self._fens_before_move == other._fens_before_move and self._fens_after_move == other._fens_after_move

        return senses_equal and moves_equal and fens_equal


class GameHistoryEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, GameHistory):
            return {
                'type': 'GameHistory',
                'senses': o._senses,
                'sense_results': o._sense_results,
                'requested_moves': o._requested_moves,
                'taken_moves': o._taken_moves,
                'capture_squares': o._capture_squares,
                'fens_before_move': o._fens_before_move,
                'fens_after_move': o._fens_after_move,
            }
        elif isinstance(o, chess.Piece):
            return {
                'type': 'Piece',
                'value': o.symbol(),
            }
        elif isinstance(o, chess.Move):
            return {
                'type': 'Move',
                'value': o.uci(),
            }
        return super().default(o)


class GameHistoryDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if 'type' in obj:
            if obj['type'] == 'Piece':
                return chess.Piece.from_symbol(obj['value'])
            elif obj['type'] == 'Move':
                return chess.Move.from_uci(obj['value'])
        elif 'true' in obj and 'false' in obj and len(obj) == 2:
            return {True: obj['true'], False: obj['false']}
        return obj
