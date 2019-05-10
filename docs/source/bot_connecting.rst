Connecting your bot to the server
=================================

Registering on the server
-------------------------

Before connecting your bot to the server, you'll need to register on the server. You can do this through the server's
website, or by using one of the built in scripts.

**Note: The server will not be active until sometime in June, so registration will not work until then.**

Website registration
^^^^^^^^^^^^^^^^^^^^

Visit https://rbc.jhuapl.edu/register to register.

Command Line registration
^^^^^^^^^^^^^^^^^^^^^^^^^

Use the built in script :code:`rc-register` (it will prompt you for the password to use):

.. code-block:: bash

    rc-register --help
    rc-register <username>


Connecting to the server
------------------------

python
^^^^^^

Use the built in script :code:`rc-connect` to connect to the server and let your bot play games:

.. code-block:: bash

    rc-connect --help
    rc-connect <bot path>
    rc-connect reconchess.bots.random_bot
    rc-connect src/my_awesome_bot.py

Use the :code:`--help` flag for more information about the arguments.

This script will prompt you for your username and password after you run it:

.. code-block:: bash

    $ rc-connect src/my_awesome_bot.py
    Username: my_awesome_bot
    Password: ...
    [<time>] Connected successfully to server!

Other languages
^^^^^^^^^^^^^^^

If you are not using python or not using the reconchess package, you will need to implement logic to handle talking to
the server. This is done through a RESTful HTTP API, and should be straightforward to implement.

If this applies to you please send us an email at **neurips_rbc_comp@listserv.jhuapl.edu.**
