Quick Start
===========

After installation you can run all unit tests:

::

    python -m unittest discover tests

You can also run a test game between two of the baseline bots:

::

    rbmc-bot-match rbmc.baselines.random rbmc.baselines.random

Then replay the game:

::

    rbmc-replay <game-output-json-file>

Or, play against a bot yourself:

::

    rbmc-play rbmc.baselines.random

Now you are ready to make your own bot algorithm to play Reconnaissance Chess.