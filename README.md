Organized in the following way:

examples contains example bots. they are made for tinkering. there is NO hidden code, all the code in the examples
is everything that gets called.
* easy to modify/play around with
* straightforward interface

recon_chess is the library
* game.py implements the game object, both locally and for connecting a bot to a remote server
* players.py implements the Player object, the main object for this api

scripts
* connect_player_to_server.py is the script that people would run if they wanted to connect their bot to a server
* play_local_game.py is the script that people would run if they wanted to test out code locally

advanced:
* can still use gambit, will just set up the sensors/movers/estimators in the player class
    * will need to update, but most can stay the same

use cases:
* someone who has never done recon chess before
* people who have done recon chess before & have made a bot before
* people who are doing ML


# milestones
- finalize player API
- local play implemented
    - implement LocalGame
    - test examples & try to make an AYK bot
- server designed
    - tournaments
    - bot vs human play
    - human vs human play
    - auth
- remote play implemented
    - implement Server
    - implement RemoteGame
    - implement server connection script for a bot
    - auth
- frontend updated
    - updated the api points that it talks to
- installation
    - make it really easy to install
- documentation
    - installation
    - first bot
    - player api
    - local play
    - debugging player
    - connecting to a server
        - auth


- extra goals:
    - local play viewer
    - update frontend
    - update gambit, and add examples