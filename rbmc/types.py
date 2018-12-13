Square = int
Color = bool
PieceType = int
from typing import List, Tuple, Optional, Type
from enum import Enum


class WinReason(Enum):
    KING_CAPTURE = 1
    TIMEOUT = 2
