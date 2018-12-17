Creating a bot
==============

To create a python-rbmc bot, extend the :class:`rbmc.Player` base class and implement the abstract methods that it has. In
order to use the rbmc scripts, the main python file you pass into the scripts must contain exactly 1 sub class of
:class:`rbmc.Player`.

Example bot: Random bot
-----------------------

The random bot takes random actions each turn, for both sensing and moving. It only really implements the
:meth:`rbmc.Player.choose_sense` and :meth:`rbmc.Player.choose_move` methods.

.. literalinclude:: ../../examples/random_bot.py


Example bot: Trout bot
----------------------

The trout bot is a baseline that you can test your bot against. It keeps track of a single :class:`chess.Board`
and uses the `Stockfish <https://stockfishchess.org/>`_ engine to make a move. When it gets information back from the game,
it naively applies that information to its :class:`chess.Board`.

.. literalinclude:: ../../examples/trout_bot.py