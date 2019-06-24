from typing import List, Tuple, Optional, Type
from enum import Enum

Square = int
Color = bool
PieceType = int


class WinReason(Enum):
    """The reason the game ended"""

    KING_CAPTURE = 1
    """The game ended because one player captured the other's king."""

    TIMEOUT = 2
    """The game ended because one player ran out of time."""

    RESIGN = 3
    """The game ended because one player resigned."""
