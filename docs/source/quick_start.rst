Quick Start
===========

After installation you can run all unit tests:

::

    python -m unittest discover tests

You can also run a test game between two of the baseline bots:

::

    rc-bot-match reconchess.baselines.random reconchess.baselines.random

Then replay the game:

::

    rc-replay <game-output-json-file>

Or, play against a bot yourself:

::

    rc-play reconchess.baselines.random

Now you are ready to make your own bot algorithm to play Reconnaissance Chess.