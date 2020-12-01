try:
    # requests uses simplejson if its present, so we need to do the same.
    # see https://github.com/psf/requests/issues/4842
    import simplejson as json
except ImportError:
    import json
import chess
from .types import *

BACK_RANKS = list(chess.SquareSet(chess.BB_BACKRANKS))


def add_pawn_queen_promotion(board: chess.Board, move: chess.Move) -> chess.Move:
    piece = board.piece_at(move.from_square)
    if piece is not None and piece.piece_type == chess.PAWN and move.to_square in BACK_RANKS and move.promotion is None:
        move = chess.Move(move.from_square, move.to_square, chess.QUEEN)
    return move


def is_psuedo_legal_castle(board: chess.Board, move: chess.Move):
    return board.is_castling(move) and not is_illegal_castle(board, move)


def is_illegal_castle(board: chess.Board, move: chess.Move) -> bool:
    if not board.is_castling(move):
        return False

    # illegal without kingside rights
    if board.is_kingside_castling(move) and not board.has_kingside_castling_rights(board.turn):
        return True

    # illegal without queenside rights
    if board.is_queenside_castling(move) and not board.has_queenside_castling_rights(board.turn):
        return True

    # illegal if any pieces are between king & rook
    rook_square = chess.square(7 if board.is_kingside_castling(move) else 0, chess.square_rank(move.from_square))
    between_squares = chess.SquareSet(chess.between(move.from_square, rook_square))
    if any(map(lambda s: board.piece_at(s), between_squares)):
        return True

    # its legal
    return False


def slide_move(board: chess.Board, move: chess.Move) -> Optional[chess.Move]:
    # We iterate longest to shortest so the revised move is the longest pseudo-legal move.
    # If the to-square < from-square then we want our list in sorted order.
    # Otherwise we want it in reverse order.
    # In either case, we need to add the to-square to the front of our list manually.
    squares = chess.SquareSet(chess.between(move.from_square, move.to_square))
    if move.to_square > move.from_square:
        squares = reversed(squares)
    for slide_square in [move.to_square] + list(squares):
        revised = chess.Move(move.from_square, slide_square, move.promotion)
        if board.is_pseudo_legal(revised):
            return revised
    return None


def capture_square_of_move(board: chess.Board, move: Optional[chess.Move]) -> Optional[Square]:
    capture_square = None
    if move is not None and board.is_capture(move):
        if board.is_en_passant(move):
            # taken from :func:`chess.Board.push()`
            down = -8 if board.turn == chess.WHITE else 8
            capture_square = board.ep_square + down
        else:
            capture_square = move.to_square
    return capture_square


def without_opponent_pieces(board: chess.Board) -> chess.Board:
    """Returns a copy of `board` with the opponent's pieces removed."""
    mine = board.occupied_co[board.turn]
    return board.transform(lambda bb: bb & mine)


def moves_without_opponent_pieces(board: chess.Board) -> List[chess.Move]:
    """Generates moves on `board` with the opponent's pieces removed."""
    return list(without_opponent_pieces(board).generate_pseudo_legal_moves())


def pawn_capture_moves_on(board: chess.Board) -> List[chess.Move]:
    """Generates all pawn captures on `board`, even if there is no piece to capture. All promotion moves are included."""
    pawn_capture_moves = []

    for pawn_square in board.pieces(chess.PAWN, board.turn):
        for attacked_square in board.attacks(pawn_square):
            # skip this square if one of our own pieces are on the square
            attacked_piece = board.piece_at(attacked_square)
            if attacked_piece and attacked_piece.color == board.turn:
                continue

            pawn_capture_moves.append(chess.Move(pawn_square, attacked_square))

            # add in promotion moves
            if attacked_square in BACK_RANKS:
                for piece_type in chess.PIECE_TYPES[1:-1]:
                    pawn_capture_moves.append(chess.Move(pawn_square, attacked_square, promotion=piece_type))

    return pawn_capture_moves


def revise_move(board, move):
    # if its a legal move, don't change it at all. note that board.generate_psuedo_legal_moves() does not
    # include psuedo legal castles
    if board.is_pseudo_legal(move) or is_psuedo_legal_castle(board, move):
        return move

    # note: if there are pieces in the way, we DONT capture them
    if is_illegal_castle(board, move):
        return None

    # if the piece is a sliding piece, slide it as far as it can go
    piece = board.piece_at(move.from_square)
    if piece.piece_type in [chess.PAWN, chess.ROOK, chess.BISHOP, chess.QUEEN]:
        move = slide_move(board, move)

    return move if board.is_pseudo_legal(move) else None


def move_actions(board: chess.Board) -> List[chess.Move]:
    """
    :return: List of moves that are possible with only knowledge of your pieces
    """
    return moves_without_opponent_pieces(board) + pawn_capture_moves_on(board)


class ChessJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, chess.Piece):
            return {
                'type': 'Piece',
                'value': o.symbol(),
            }
        elif isinstance(o, chess.Move):
            return {
                'type': 'Move',
                'value': o.uci(),
            }
        elif isinstance(o, chess.Board):
            return {
                'type': 'Board',
                'value': o.fen(),
            }
        elif isinstance(o, WinReason):
            return {
                'type': 'WinReason',
                'value': o.name,
            }
        return super().default(o)


class ChessJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        hook = self._object_hook
        if 'object_hook' in kwargs:
            original_hook = kwargs.pop('object_hook')
            hook = lambda obj: self._object_hook(original_hook(obj))
        super().__init__(object_hook=hook, *args, **kwargs)

    def _object_hook(self, obj):
        if 'type' in obj:
            if obj['type'] == 'Piece':
                return chess.Piece.from_symbol(obj['value'])
            elif obj['type'] == 'Move':
                return chess.Move.from_uci(obj['value'])
            elif obj['type'] == 'Board':
                return chess.Board(fen=obj['value'])
            elif obj['type'] == 'WinReason':
                return WinReason[obj['value']]
        return obj
