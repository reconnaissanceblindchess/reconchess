Quick Start
===========

After installation you can run all unit tests:

::

    python -m unittest discover tests

You can also run a test game between two of the baseline bots:

::

    rc-bot-match.py reconchess.bots.random_bot reconchess.bots.random_bot

Then replay the game:

::

    rc-replay.py <game-output-json-file>

Or, play against a bot yourself:

::

    rc-play.py reconchess.bots.random_bot

Now you are ready to make your own bot algorithm to play Reconnaissance Chess.