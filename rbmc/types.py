from typing import List, Tuple, Optional, Type
from enum import Enum, auto

Square = int
Color = bool
PieceType = int


class WinReason(Enum):
    """The reason the game ended"""

    KING_CAPTURE = auto()
    """The game ended because one player captured the other's king."""

    TIMEOUT = auto()
    """The game ended because one player ran out of time"""
