import chess
from .types import *

BACK_RANKS = list(chess.SquareSet(chess.BB_BACKRANKS))


def add_pawn_queen_promotion(board: chess.Board, move: chess.Move) -> chess.Move:
    piece = board.piece_at(move.from_square)
    if piece.piece_type == chess.PAWN and move.to_square in BACK_RANKS and move.promotion is None:
        move.promotion = chess.QUEEN
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
    between_squares = chess.SquareSet(chess.BB_BETWEEN[move.from_square][rook_square])
    if any(map(lambda s: board.piece_at(s), between_squares)):
        return True

    # its legal
    return False


def slide_move(board: chess.Board, move: chess.Move) -> chess.Move:
    psuedo_legal_moves = list(board.generate_pseudo_legal_moves())
    squares = list(chess.SquareSet(chess.BB_BETWEEN[move.from_square][move.to_square])) + [move.to_square]
    squares = sorted(squares, key=lambda s: chess.square_distance(s, move.from_square), reverse=True)
    for slide_square in squares:
        revised = chess.Move(move.from_square, slide_square, move.promotion)
        if revised in psuedo_legal_moves:
            return revised
    return chess.Move.null()


def capture_square_of_move(board: chess.Board, move: chess.Move) -> Optional[Square]:
    capture_square = None
    if board.is_capture(move):
        if board.is_en_passant(move):
            # taken from :func:`chess.Board.push()`
            down = -8 if board.turn == chess.WHITE else 8
            capture_square = board.ep_square + down
        else:
            capture_square = move.to_square
    return capture_square
