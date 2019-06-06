Debugging your bot
==================

Diagnosing Errors
-----------------

When your bot encounters an exception or error during a game, reproducing that error is essential to diagnosing and
fixing it. The built in script :code:`rc-playback` takes a game history, a bot, and the color the bot played as, and
plays back the actions the bot took during the game. This allows you to exactly replicate the error producing
conditions. Built in scripts like :code:`rc-play` and :code:`rc-bot-match` will produce game history files when an error
occurs.

.. code-block:: bash

    rc-playback --help
    rc-playback <game history path> <bot> <color>
    rc-playback bad_game.json src/my_awesome_bot.py white

Use the :code:`--help` flag for more information about the arguments.

Debugging with PyCharm
----------------------

You can create a run configuration to run your bot from PyCharm by targeting one of the scripts provided for running
bots, like :code:`reconchess.scripts.rc-bot-match` or :code:`reconchess.scripts.rc-play`, as a module:

.. image:: _static/pycharm_bot_match_config.gif
    :target: _static/pycharm_bot_match_config.gif

You can then choose to run the configuration you made in debug mode, and PyCharm will hit any breakpoints you set. It
can do this because :code:`rc-bot-match` and :code:`rc-play` load your bot code into the same python process
(see :func:`reconchess.load_player`).

Debugging with output
---------------------

You can use ordinary print statements in your bot, and they will appear on the command line if you use
:code:`reconchess.scripts.rc-bot-match` or :code:`reconchess.scripts.rc-play`. If you want to your output to go to a file,
use a logging library (e.g. the built in logging module).
