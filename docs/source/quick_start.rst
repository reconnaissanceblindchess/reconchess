Installation and Quick Start
============================

Install the python package

::

    pip install reconchess

You can also run a test game between two of the baseline bots:

::

    rc-bot-match reconchess.bots.random_bot reconchess.bots.random_bot

Then replay the game:

::

    rc-replay <game-output-json-file>

Or, play against a bot yourself:

::

    rc-play reconchess.bots.random_bot

Now you are ready to make your own bot algorithm to play Reconnaissance Chess.