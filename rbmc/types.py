Square = int
Color = bool
PieceType = int
from typing import List, Tuple, Optional, Type
from enum import Enum, auto


class WinReason(Enum):
    KING_CAPTURE = auto()
    TIMEOUT = auto()
