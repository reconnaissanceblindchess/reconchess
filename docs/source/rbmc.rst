python-rbmc API
===============

Types
-----

.. py:class:: rbmc.Square

    A type alias for an integer.

    See :data:`chess.A1`, :data:`chess.B1`, ..., and :data:`chess.H8` for specifying specific squares.

    See :data:`chess.SQUARES` for referencing all squares.

.. py:class:: rbmc.Color

    A type alias for a boolean.

    See :data:`chess.WHITE` and :data:`chess.BLACK`.

    :data:`chess.WHITE` = True

    :data:`chess.BLACK` = False

.. py:class:: rbmc.PieceType

    A type alias for an integer.

    See :data:`chess.PAWN`, :data:`chess.KNIGHT`, :data:`chess.BISHOP`, :data:`chess.ROOK`,
    :data:`chess.QUEEN`, :data:`chess.KING` for specifying specific piece types

    See :data:`chess.PIECE_TYPES` for referencing all piece types.

.. autoclass:: rbmc.WinReason
    :members:

Player
------

.. autoclass:: rbmc.Player
    :members:

.. autofunction:: rbmc.load_player

Game
----

.. autoclass:: rbmc.Game
    :members:

.. autoclass:: rbmc.LocalGame

.. autoclass:: rbmc.RemoteGame

GameHistory
-----------

.. autoclass:: rbmc.Turn
    :members:

.. autoclass:: rbmc.GameHistory
    :members:

Functions for playing games
---------------------------

.. autofunction:: rbmc.play_local_game

.. autofunction:: rbmc.play_remote_game

.. autofunction:: rbmc.play_turn

.. autofunction:: rbmc.notify_opponent_move_results

.. autofunction:: rbmc.play_sense

.. autofunction:: rbmc.play_move
