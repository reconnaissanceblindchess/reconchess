import chess
from .types import *
from typing import Callable, TypeVar, Iterable, Mapping
import csv

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
        serializer = GameHistorySerializer(self)
        with open(filename, 'w', newline='') as fp:
            serializer.write(fp)

    @classmethod
    def from_file(cls, filename):
        history = cls()
        serializer = GameHistorySerializer(history)
        with open(filename, newline='') as fp:
            serializer.read(fp)
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

    def sense(self, turn: Turn) -> Square:
        self._validate_turn(turn, self._senses)
        return self._senses[turn.color][turn.turn_number]

    def sense_result(self, turn: Turn) -> List[Tuple[Square, Optional[chess.Piece]]]:
        self._validate_turn(turn, self._sense_results)
        return self._sense_results[turn.color][turn.turn_number]

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


class GameHistorySerializer:
    def __init__(self, history: GameHistory):
        self.history = history

        self.fieldnames = ['turn', 'color', 'sense', 'sense_result_squares', 'sense_result_pieces', 'requested_move',
                           'taken_move', 'capture_square', 'fen_before_move', 'fen_after_move']
        self.fns_by_field = {
            'turn': (lambda turn: turn.turn_number, self._serialize_turn_number, self._deserialize_turn_number),
            'color': (lambda turn: turn.color, self._serialize_color, self._deserialize_color),
            'sense': (self.history.sense, self._serialize_opt_square, self._deserialize_opt_square),
            'sense_result_squares': (self._get_sense_result_squares, self._serialize_sense_result_squares,
                                     self._deserialize_sense_result_squares),
            'sense_result_pieces': (self._get_sense_result_pieces, self._serialize_sense_result_pieces,
                                    self._deserialize_sense_result_pieces),
            'requested_move': (self.history.requested_move, self._serialize_opt_move, self._deserialize_opt_move),
            'taken_move': (self.history.taken_move, self._serialize_opt_move, self._deserialize_opt_move),
            'capture_square': (self.history.capture_square, self._serialize_opt_square, self._deserialize_opt_square),
            'fen_before_move': (self.history.truth_fen_before_move, str, str),
            'fen_after_move': (self.history.truth_fen_after_move, str, str),
        }

    def write(self, fp):
        writer = csv.DictWriter(fp, delimiter='\t', fieldnames=self.fieldnames)
        writer.writeheader()
        for turn in self.history.turns():
            writer.writerow({field: self._serialize_field(field, turn) for field in self.fieldnames})

    def _serialize_field(self, field: str, turn: Turn):
        value = self.fns_by_field[field][0](turn)
        return self.fns_by_field[field][1](value)

    def read(self, fp):
        reader = csv.DictReader(fp, delimiter='\t')
        for row in reader:
            self._deserialize_row(row)
            self.history.store_sense(row['color'], row['sense'],
                                     list(zip(row['sense_result_squares'], row['sense_result_pieces'])))
            self.history.store_move(row['color'], row['requested_move'], row['taken_move'], row['capture_square'])
            self.history.store_fen_before_move(row['color'], row['fen_before_move'])
            self.history.store_fen_after_move(row['color'], row['fen_after_move'])

    def _deserialize_row(self, row):
        for field in row:
            row[field] = self.fns_by_field[field][2](row[field])

    def _get_sense_result_squares(self, turn: Turn) -> List[Square]:
        sense_result = self.history.sense_result(turn)
        squares, pieces = zip(*sense_result)
        return squares

    def _get_sense_result_pieces(self, turn: Turn) -> List[Optional[chess.Piece]]:
        sense_result = self.history.sense_result(turn)
        squares, pieces = zip(*sense_result)
        return pieces

    @staticmethod
    def _serialize_turn_number(turn_number: int) -> str:
        return str(turn_number)

    @staticmethod
    def _deserialize_turn_number(turn_number: str) -> int:
        return int(turn_number)

    @staticmethod
    def _serialize_color(color: Color) -> str:
        return chess.COLOR_NAMES[color]

    @staticmethod
    def _deserialize_color(color: str) -> Color:
        return bool(chess.COLOR_NAMES.index(color))

    @staticmethod
    def _serialize_opt_square(square: Optional[Square]) -> str:
        return chess.SQUARE_NAMES[square] if square is not None else 'None'

    @staticmethod
    def _deserialize_opt_square(square: str) -> Optional[Square]:
        return None if square == 'None' else chess.SQUARE_NAMES.index(square)

    @staticmethod
    def _serialize_opt_move(move: Optional[chess.Move]) -> str:
        return move.uci() if move is not None else 'None'

    @staticmethod
    def _deserialize_opt_move(move: str) -> Optional[chess.Move]:
        return None if move == 'None' else chess.Move.from_uci(move)

    @staticmethod
    def _serialize_opt_piece(piece: Optional[chess.Piece]) -> str:
        return piece.symbol() if piece is not None else '.'

    @staticmethod
    def _deserialize_opt_piece(piece: str) -> Optional[chess.Piece]:
        return None if piece == '.' else chess.Piece.from_symbol(piece)

    @staticmethod
    def _serialize_sense_result_squares(sense_result_squares: List[Square]) -> str:
        return ','.join(map(GameHistorySerializer._serialize_opt_square, sense_result_squares))

    @staticmethod
    def _deserialize_sense_result_squares(sense_result_squares: str) -> List[Square]:
        return list(map(GameHistorySerializer._deserialize_opt_square, sense_result_squares.split(',')))

    @staticmethod
    def _serialize_sense_result_pieces(sense_result_pieces: List[Optional[chess.Piece]]) -> str:
        return ','.join(map(GameHistorySerializer._serialize_opt_piece, sense_result_pieces))

    @staticmethod
    def _deserialize_sense_result_pieces(sense_result_pieces: str) -> List[Optional[chess.Piece]]:
        return list(map(GameHistorySerializer._deserialize_opt_piece, sense_result_pieces.split(',')))
