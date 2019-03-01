Creating a bot
==============

To create a reconchess bot, extend the :class:`reconchess.Player` base class and implement the abstract methods that it has. In
order to use the reconchess scripts, the main python file you pass into the scripts must contain exactly 1 sub class of
:class:`reconchess.Player`.

For more information on the API see the :class:`reconchess.Player` section on the :ref:`reconchess-api` page.

Example bot: Random bot
-----------------------

The random bot takes random actions each turn, for both sensing and moving. It only really implements the
:meth:`reconchess.Player.choose_sense` and :meth:`reconchess.Player.choose_move` methods.

.. literalinclude:: ../../reconchess/bots/random_bot.py


Example bot: Trout bot
----------------------

The trout bot is a baseline that you can test your bot against. It keeps track of a single :class:`chess.Board`
and uses the `Stockfish <https://stockfishchess.org/>`_ engine to make a move. When it gets information back from the game,
it naively applies that information to its :class:`chess.Board`.

**NOTE** You will need to download Stockfish and create an environment variable called `STOCKFISH_EXECUTABLE` that has
the path to the Stockfish executable to use TroutBot.

.. literalinclude:: ../../reconchess/bots/trout_bot.py