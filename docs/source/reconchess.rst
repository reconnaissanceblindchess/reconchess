.. _reconchess-api:

reconchess API
===============

Types
-----

.. py:class:: reconchess.Square

    A type alias for an integer.

    See :data:`chess.A1`, :data:`chess.B1`, ..., and :data:`chess.H8` for specifying specific squares.

    See :data:`chess.SQUARES` for referencing all squares.

.. py:class:: reconchess.Color

    A type alias for a boolean.

    See :data:`chess.WHITE` and :data:`chess.BLACK`.

    :data:`chess.WHITE` = True

    :data:`chess.BLACK` = False

.. py:class:: reconchess.PieceType

    A type alias for an integer.

    See :data:`chess.PAWN`, :data:`chess.KNIGHT`, :data:`chess.BISHOP`, :data:`chess.ROOK`,
    :data:`chess.QUEEN`, :data:`chess.KING` for specifying specific piece types

    See :data:`chess.PIECE_TYPES` for referencing all piece types.

.. autoclass:: reconchess.WinReason
    :members:

Player
------

.. autoclass:: reconchess.Player
    :members:

.. autofunction:: reconchess.load_player

Game
----

.. autoclass:: reconchess.Game
    :members:

.. autoclass:: reconchess.LocalGame

.. autoclass:: reconchess.RemoteGame

GameHistory
-----------

.. autoclass:: reconchess.Turn
    :members:

.. autoclass:: reconchess.GameHistory
    :members:

Functions for playing games
---------------------------

.. autofunction:: reconchess.play_local_game

.. autofunction:: reconchess.play_remote_game

.. autofunction:: reconchess.play_turn

.. autofunction:: reconchess.notify_opponent_move_results

.. autofunction:: reconchess.play_sense

.. autofunction:: reconchess.play_move
