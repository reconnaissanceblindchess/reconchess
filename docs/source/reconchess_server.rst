.. _reconchess-HTTP-api:

HTTP API
========

This is the HTTP API of the reconchess server, and is used when you play a remote game. We provide scripts
and code to use this HTTP API with the python package by default, but if you are using another language
you will need to make HTTP requests to these endpoints to play remote games.

Authorization
--------------

The HTTP API uses basic authorization, so you will need to provide the username and password
in the Authorization header.

User Endpoints
--------------

Endpoints for querying users and updating data for yourself.

.. http:get:: /api/users/

    Get all active users.

    **Example response content**:

    .. code-block:: javascript

        {
            "usernames": ["foouser", "baruser"]
        }

    :<header Authorization: Basic Authorization.
    :>json array<string> usernames: usernames of active users.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information.

.. http:post:: /api/users/me

    Ping the server to update your connection time.

    **Example response content**:

    .. code-block:: javascript

        {
            "id": 1,
            "username": "foouser",
            "max_games": 4
        }

    :<header Authorization: Basic Authorization.
    :>json integer id: Your ID.
    :>json string username: Your username.
    :>json integer max_games: The maximum number of games you can play at one time.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information.

.. http:post:: /api/users/me/max_games

    Update the number of max_games you can play at one time.

    **Example request content**:

    .. code-block:: javascript

        {
            "max_games": 5
        }

    **Example response content**:

    .. code-block:: javascript

        {
            "id": 1,
            "username": "foouser",
            "max_games": 5
        }

    :<header Authorization: Basic Authorization.
    :<json integer max_games: The maximum number of games you can play at one time.
    :>json integer id: Your ID.
    :>json string username: Your username.
    :>json integer max_games: The maximum number of games you can play at one time.
    :statuscode 200: Success.
    :statuscode 400: Invalid request (max_games not present or not an integer).
    :statuscode 401: Invalid or empty authentication information.

.. http:post:: /api/users/me/ranked

    Update whether you want to participate in ranked matches or not.

    **Example request content**:

    .. code-block:: javascript

        {
            "ranked": true
        }

    **Example response content**:

    .. code-block:: javascript

        {
            "id": 1,
            "username": "foouser",
            "ranked": true
        }

    :<header Authorization: Basic Authorization.
    :<json boolean ranked: Whether you want to participate in ranked matches or not.
    :>json integer id: Your ID.
    :>json string username: Your username.
    :>json boolean ranked: Whether you want to participate in ranked matches or not.
    :statuscode 200: Success.
    :statuscode 400: Invalid request (ranked not present or not a boolean).
    :statuscode 401: Invalid or empty authentication information.

.. http:post:: /api/users/me/version

    Create a new version of your bot for ranked matches. If no versions exist, this creates version 1, otherwise it
    increments the last version for your bot.

    **Example response content**:

    .. code-block:: javascript

        {
            "id": 1,
            "username": "foouser",
            "version": 10
        }

    :<header Authorization: Basic Authorization.
    :>json integer id: Your ID.
    :>json string username: Your username.
    :>json integer version: The new version number for your bot.
    :statuscode 200: Success.
    :statuscode 400: Invalid request (ranked not present or not a boolean).
    :statuscode 401: Invalid or empty authentication information.

Invitation Endpoints
--------------------

The invitation endpoints allow you to send and receive invitations to play games. Example usage can be seen
in the :code:`rc_connect` script.

.. http:get:: /api/invitations/

    Unaccepted invitations sent to you from other players.

    **Example response content**:

    .. code-block:: javascript

        {
            "invitations": [1, 2, 5]
        }

    :<header Authorization: Basic Authorization.
    :>json array<integer> invitations: id's of your unaccepted invitations.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information.

.. http:post:: /api/invitations/

    Send an invitation to another player.

    **Example request content**:

    .. code-block:: javascript

        {
            "opponent": "thatguy",
            "color": true
        }

    **Example response content**:

    .. code-block:: javascript

        {
            "game_id": 1
        }

    :<header Authorization: Basic Authorization.
    :<json string opponent: The name of the player to send the invitation to.
    :<json boolean color: The color you want to play - :code:`true` for White and :code:`false` for Black.
    :>json integer game_id: The game ID of the resulting game.
    :statuscode 200: Success.
    :statuscode 400: Invitation does not exist.
    :statuscode 401: Invalid or empty authentication information.

.. http:post:: /api/invitations/(int:invitation_id)

    Accept the `invitation_id` invitation.

    **Example response content**:

    .. code-block:: javascript

        {
            "game_id": 1
        }

    :param invitation: The ID of the invitation.
    :<header Authorization: Basic Authorization.
    :>json integer game_id: The game ID of the resulting game.
    :statuscode 200: Success.
    :statuscode 400: Invitation does not exist.
    :statuscode 401: Invalid or empty authentication information.

.. http:post:: /api/invitations/(int:invitation_id)/finish

    Mark the `invitation_id` invitation as finished.

    :param invitation: The ID of the invitation.
    :<header Authorization: Basic Authorization.
    :statuscode 200: Success.
    :statuscode 400: Invitation does not exist or invitation is not accepted.
    :statuscode 401: Invalid or empty authentication information.

Game Endpoints
--------------

The game endpoints allow you to send actions to the server and receive their results. Example usage
can be seen in the implementation of :class:`reconchess.RemoteGame`.

.. http:get:: /api/games/(int:game_id)/color

    Get the color you are playing as in game `game_id`.

    **Example response content**:

    .. code-block:: javascript

        {
            "color": true
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json boolean color: The color you are playing as - :code:`true` for White and :code:`false` for Black.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/starting_board

    Get the starting board for game `game_id`.

    **Example response content**:

    .. code-block:: javascript

        {
            "board": {
                "type": "Board",
                "value": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            }
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json object board: The starting board.
    :>json string type: :code:`"Board"`.
    :>json string value: The fen string of the chess board.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/opponent_name

    Get the name of your opponent for game `game_id`.

    **Example response content**:

    .. code-block:: javascript

        {
            "opponent_name": "super evil dude 123"
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json string opponent_name: The name of the opponent.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:post:: /api/games/(int:game_id)/ready

    Mark yourself as ready to start the game.

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :statuscode 200: Success.
    :statuscode 400: Player already marked as ready.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/sense_actions

    Get the sense actions you can take. See :meth:`reconchess.Game.sense_actions`.

    **Example response content**:

    .. code-block:: javascript

        {
            "sense_actions": [1, 2, 3, 4]
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json array<integer> sense_actions: A list of squares you can sense.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/move_actions

    Get the move actions you can take. See :meth:`reconchess.Game.move_actions`.

    **Example response content**:

    .. code-block:: javascript

        {
            "move_actions": [
                {"type": "Move", "value": "e2e4"},
                {"type": "Move", "value": "a7a8q"}
            ]
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json object move_actions: A list of the moves you can make.
    :>json string type: :code:`"Move"`.
    :>json string value: The chess move encoded as a UCI string.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/seconds_left

    Gets the number of seconds you have left to play. See :meth:`reconchess.Game.get_seconds_left`.

    **Example response content**:

    .. code-block:: javascript

        {
            "seconds_left": 50
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json float seconds_left: The time you have left to play.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/opponent_move_results

    Get the result of the opponent's last move.  See :meth:`reconchess.Game.opponent_move_results`.

    **Example response content**:

    .. code-block:: javascript

        {
            "opponent_move_results": 34
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json Optional<integer> opponent_move_results: The square the opponent captured one of your pieces on.
        :code:`null` if no capture occurred.
    :statuscode 200: Success.
    :statuscode 400: Game is finished.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:post:: /api/games/(int:game_id)/sense

    Perform a sense action.  See :meth:`reconchess.Game.sense`.

    **Example request content**:

    .. code-block:: javascript

        {
            "square": 5
        }

    **Example response content**:

    .. code-block:: javascript

        {
            "sense_result": [
                [54, {"type": "Piece", "value": "p"}],
                [55, null],
                [56, {"type": "Piece", "value": "K"}]
            ]
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :<json integer square: The square you want to sense.
    :>json object sense_result: The list of squares and pieces found from your sense.
    :>json string type: :code:`Piece`.
    :>json Optional<string> value: The symbol of the piece found at the square. :code:`null` if no piece is there.
    :statuscode 200: Success.
    :statuscode 400: Game is finished, you already sensed, or malformed request data.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:post:: /api/games/(int:game_id)/move

    Perform a move action.  See :meth:`reconchess.Game.move`.

    **Example request content**:

    .. code-block:: javascript

        {
            "requested_move": {"type": "Move", "value": "e2e4"}
        }

    **Example response content**:

    .. code-block:: javascript

        {
            "move_result": [
                {"type": "Move", "value": "e2e4"},
                null,
                23
            ]
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :<json object requested_move: The move you want to perform.
    :>json object move_result: The result of your move, a list containing the requested_move, the taken_move,
        and the capture square if one occurred.
    :>json string type: :code:`Move`.
    :>json Optional<string> value: The move encoded as a UCI string. :code:`null` if no piece is there.
    :statuscode 200: Success.
    :statuscode 400: Game is finished, you haven't sensed, you already moved, or malformed request data.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:post:: /api/games/(int:game_id)/end_turn

    End your turn.  See :meth:`reconchess.Game.end_turn`.

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :statuscode 200: Success.
    :statuscode 400: Game is finished, you haven't sensed and moved.
    :statuscode 401: Invalid or empty authentication information, or not a player in the specified game.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/is_over

    Whether the game is over. See :meth:`reconchess.Game.is_over`.

    We recommend using the `game_status` endpoint for turn management.

    **Example response content**:

    .. code-block:: javascript

        {
            "is_over": true
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json boolean is_over: Whether the game is over.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information.
    :statuscode 404: Game does not exist.

.. http:post:: /api/games/(int:game_id)/resign

    Resign from the game. Can only be called during your turn.

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :statuscode 200: Success.
    :statuscode 400: It is not your turn.
    :statuscode 401: Invalid or empty authentication information.
    :statuscode 404: Game does not exist.

.. http:post:: /api/games/(int:game_id)/error_resign

    Tell the server that you have errored out. This just zeros out any time you have remaining instead of waiting
    for the time to run out.

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/is_my_turn

    Whether it is your turn to play.

    We recommend using the `game_status` endpoint for turn management.

    **Example response content**:

    .. code-block:: javascript

        {
            "is_my_turn": true
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json boolean is_my_turn: Whether it is your turn to play.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/game_status

    A combination of the `is_over` and `is_my_turn` endpoints.

    **Example response content**:

    .. code-block:: javascript

        {
            "is_my_turn": true,
            "is_over": false
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json boolean is_my_turn: Whether it is your turn to play.
    :>json boolean is_over: Whether the game is over.
    :statuscode 200: Success.
    :statuscode 401: Invalid or empty authentication information.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/winner_color

    The color of the winner of the game. See :meth:`reconchess.Game.get_winner_color`.

    **Example response content**:

    .. code-block:: javascript

        {
            "winner_color": true
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json Optional<boolean> winner_color: The color of the player that one the game -
        :code:`true` for White, :code:`false` for Black, and :code:`null` for a draw.
    :statuscode 200: Success.
    :statuscode 400: Game is not over.
    :statuscode 401: Invalid or empty authentication information.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/win_reason

    The reason the game ended. See :meth:`reconchess.Game.get_win_reason` and :class:`reconchess.WinReason`.

    **Example response content**:

    .. code-block:: javascript

        {
            "win_reason": {
                "type": "WinReason",
                "value": "KING_CAPTURE"
            }
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json Optional<WinReason> win_reason: The reason the game ended.
    :>json string type: :code:`WinReason`.
    :>json string value: The string version of the values of :class:`reconchess.WinReason`. :code:`null` if a draw.
    :statuscode 200: Success.
    :statuscode 400: Game is not over.
    :statuscode 401: Invalid or empty authentication information.
    :statuscode 404: Game does not exist.

.. http:get:: /api/games/(int:game_id)/game_history

    The history of the game. See :meth:`reconchess.Game.get_game_history` and :class:`reconchess.GameHistory`.

    **Example response content**:

    .. code-block:: javascript

        {
            "game_history": {
                "type": "GameHistory",
                "senses": {
                    "true": [55],
                    "false": [null]
                },
                "sense_results": {
                    "true": [
                        [
                            [54, {"type": "Piece", "value": "p"}],
                            [55, null],
                            [56, {"type": "Piece", "value": "K"}]
                        ]
                    ],
                    "false": [[]]
                },
                "requested_moves": {
                    "true": [{"type": "Move", "value": "e2e4"}],
                    "false": [{"type": "Move", "value": "e7e8"}]
                },
                "taken_moves": {
                    "true": [{"type": "Move", "value": "e2e4"}],
                    "false": [null]
                },
                "capture_squares": {
                    "true": [23],
                    "false": [null]
                },
                "fens_before_move": {
                    "true": ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"],
                    "false": ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]
                },
                "fens_after_move": {
                    "true": ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"],
                    "false": ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]
                }
            }
        }

    :param game_id: The ID of the game.
    :<header Authorization: Basic Authorization.
    :>json object game_history: The game history object.
    :>json string type: The type of the object.
    :>json string value: The value of the object.
    :>json object senses: An object containing the senses for each player.
    :>json object sense_results: An object containing the sense_results for each player.
    :>json object requested_moves: An object containing the requested_moves for each player.
    :>json object taken_moves: An object containing the taken_moves for each player.
    :>json object capture_squares: An object containing the capture_squares for each player.
    :>json object fens_before_move: An object containing the fens_before_move for each player.
    :>json object fens_after_move: An object containing the fens_after_move for each player.
    :statuscode 200: Success.
    :statuscode 400: Game is not over.
    :statuscode 401: Invalid or empty authentication information.
    :statuscode 404: Game does not exist.
