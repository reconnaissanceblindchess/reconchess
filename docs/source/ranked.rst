Playing Ranked matches
======================

Ranked matches allow you to quickly compare your bot to other bots with an ELO score based on the ranked matches you
play.

Pass the :code:`--ranked` flag to the built in script :code:`rc-connect` to notify the server that you want to play
ranked matches:

.. code-block:: bash

    rc-connect --help
    rc-connect --ranked <bot path>
    rc-connect --ranked --keep-version <bot path>
    rc-connect --ranked reconchess.bots.random_bot

Use the :code:`--help` flag for more information about the arguments.

Versioning
^^^^^^^^^^

When you use the :code:`--ranked` flag of :code:`rc-connect`, it will prompt you about the version of your bot.
Versions give you a way to track different updates to your bot.

The server tracks the ELO of each of your versions separately, so your old version's performance will not impact a new
version's performance. In fact, when you create a new version the ELO starts from scratch to give you better accuracy.

There are two prompts you will have to answer when using the :code:`--ranked` flag:

The first prompt asks whether you want to connect as a new version. Answer with :code:`y` if you want to create a new
version, and :code:`n` otherwise.

.. code-block:: bash

    > rc-connect --ranked <my bot>
    ...
    Is this a new version of your bot? [y/n]

The second prompt is a confirmation prompt and indicates the last version you connected as, and what version you will
connect to the server as currently. Answer with :code:`y` if you want to connect, and answering with :code:`n` will
exit the script.

.. code-block:: bash

    > rc-connect --ranked <my bot>
    ...
    Are you sure you want to participate in ranked matches as v<new version> (currently v<old version>)? [y/n]

Example of connecting to the server in ranked mode using the same version as last time:

.. code-block:: bash

    > rc-connect --ranked <my bot>
    ...
    Is this a new version of your bot? [y/n]n
    Are you sure you want to participate in ranked matches as v1 (currently v1)? [y/n]y
    [<time stamp>] Connected successfully to server!

Example of connecting to the server in ranked mode as a new version:

.. code-block:: bash

    > rc-connect --ranked <my bot>
    ...
    Is this a new version of your bot? [y/n]y
    Are you sure you want to participate in ranked matches as v2 (currently v1)? [y/n]y
    [<time stamp>] Connected successfully to server!

Other languages
^^^^^^^^^^^^^^^

If you are not using python or not using the reconchess package, you will need to implement logic to handle talking to
the server. This is done through a RESTful HTTP API, and should be straightforward to implement.

See the :ref:`reconchess-HTTP-api` page for more information

If this applies to you please send us an email at **neurips_rbc_comp@listserv.jhuapl.edu** for help.
