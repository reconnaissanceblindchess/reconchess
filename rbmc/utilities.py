import chess
from .types import *


def without_opponent_pieces(board: chess.Board) -> chess.Board:
    """Returns a copy of `board` with the opponent's pieces removed."""
    b = board.copy()
    for square in chess.SQUARES:
        piece = b.piece_at(square)
        if piece is not None and piece.color != b.turn:
            b.remove_piece_at(square)
    return b


def moves_without_opponent_pieces(board: chess.Board) -> List[chess.Move]:
    """Generates moves on `board` with the opponent's pieces removed."""
    return list(without_opponent_pieces(board).generate_pseudo_legal_moves())


def pawn_capture_moves_on(board: chess.Board) -> List[chess.Move]:
    """Generates all pawn captures on `board`, even if there is no piece to capture. All promotion moves are included."""
    pawn_capture_moves = []

    no_opponents_board = without_opponent_pieces(board)

    for pawn_square in board.pieces(chess.PAWN, board.turn):
        for attacked_square in board.attacks(pawn_square):
            # skip this square if one of our own pieces are on the square
            if no_opponents_board.piece_at(attacked_square):
                continue

            pawn_capture_moves.append(chess.Move(pawn_square, attacked_square))

            # add in promotion moves
            if attacked_square in chess.SquareSet(chess.BB_BACKRANKS):
                for piece_type in chess.PIECE_TYPES[1:-1]:
                    pawn_capture_moves.append(chess.Move(pawn_square, attacked_square, promotion=piece_type))

    return pawn_capture_moves
