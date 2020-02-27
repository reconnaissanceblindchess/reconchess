Installation and Quick Start
============================

Install
-------

Install the python package

.. code-block:: bash

    $ pip install reconchess

Quick Start
-----------

You can run a test game between two of the baseline bots:

.. code-block:: bash

    $ rc-bot-match reconchess.bots.random_bot reconchess.bots.random_bot

Then replay the game:

.. code-block:: bash

    $ rc-replay <game-output-json-file>

Or, play against a bot yourself:

.. code-block:: bash

    $ rc-play reconchess.bots.random_bot

Now you are ready to make your own bot algorithm to play Reconnaissance Chess.

Server Quick Start
------------------

Register your account by visiting https://rbc.jhuapl.edu/register.

Then you can play games on the server with :code:`rc-connect` and providing your bot username and password when prompted:

.. code-block:: bash

    $ rc-connect src/my_awesome_bot.py
    Username: MyAwesomeUsername
    Password: ...
    [<time>] Connected successfully to server!

Playing ranked matches on the server is as easy as specifying the :code:`--ranked` flag:

.. code-block:: bash

    $ rc-connect --ranked src/my_awesome_bot.py
    Username: MyAwesomeUsername
    Password: ...
    Are you sure you want to participate in ranked matches as v1 (currently v0)? [y/n]y
    [<time stamp>] Connected successfully to server!
