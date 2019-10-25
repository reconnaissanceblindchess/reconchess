import chess
from .types import *
from .player import Player
from .game import Game, LocalGame, RemoteGame, MultiprocessingLocalGame
from .history import GameHistory

import multiprocessing as mp


def play_local_game(white_player: Player, black_player: Player, game: LocalGame = None,
                    seconds_per_player: float = 900) -> Tuple[Optional[Color], Optional[WinReason], GameHistory]:
    """
    Plays a game between the two players passed in. Uses :class:`LocalGame` to run the game, and just calls
    :func:`play_turn` until the game is over: ::

        while not game.is_over():
            play_turn(game, player)

    :param white_player: The white :class:`Player`.
    :param black_player: The black :class:`Player`.
    :param game: The :class:`LocalGame` object to use.
    :param seconds_per_player: The time each player has to play. Only used if `game` is not passed in.
    :return: The results of the game, also passed to each player via :meth:`Player.handle_game_end`.
    """
    players = [black_player, white_player]

    if game is None:
        game = LocalGame(seconds_per_player=seconds_per_player)

    white_name = white_player.__class__.__name__
    black_name = black_player.__class__.__name__
    game.store_players(white_name, black_name)

    white_player.handle_game_start(chess.WHITE, game.board.copy(), black_name)
    black_player.handle_game_start(chess.BLACK, game.board.copy(), white_name)
    game.start()

    while not game.is_over():
        play_turn(game, players[game.turn], end_turn_last=True)

    game.end()
    winner_color = game.get_winner_color()
    win_reason = game.get_win_reason()
    game_history = game.get_game_history()

    white_player.handle_game_end(winner_color, win_reason, game_history)
    black_player.handle_game_end(winner_color, win_reason, game_history)

    return winner_color, win_reason, game_history


def play_remote_game(server_url, game_id, auth, player: Player):
    game = RemoteGame(server_url, game_id, auth)

    player.handle_game_start(game.get_player_color(), game.get_starting_board(), game.get_opponent_name())
    game.start()

    while not game.is_over():
        play_turn(game, player, end_turn_last=False)

    winner_color = game.get_winner_color()
    win_reason = game.get_win_reason()
    game_history = game.get_game_history()

    player.handle_game_end(winner_color, win_reason, game_history)

    return winner_color, win_reason, game_history


def play_turn(game: Game, player: Player, end_turn_last=False):
    """
    Coordinates playing a turn for `player` in `game`. Does the following sequentially:

    #. :func:`notify_opponent_move_results`
    #. :func:`play_sense`
    #. :func:`play_move`

    See :func:`play_move` for more info on `end_turn_last`.

    :param game: The :class:`Game` that `player` is playing in.
    :param player: The :class:`Player` whose turn it is.
    :param end_turn_last: Flag indicating whether to call :meth:`Game.end_turn` before or after :meth:`Player.handle_move_result`
    """
    sense_actions = game.sense_actions()
    move_actions = game.move_actions()

    notify_opponent_move_results(game, player)

    play_sense(game, player, sense_actions, move_actions)

    play_move(game, player, move_actions, end_turn_last=end_turn_last)


def notify_opponent_move_results(game: Game, player: Player):
    """
    Passes the opponents move results to the player. Does the following sequentially:

    #. Get the results of the opponents move using :meth:`Game.opponent_move_results`.
    #. Give the results to the player using :meth:`Player.handle_opponent_move_result`.

    :param game: The :class:`Game` that `player` is playing in.
    :param player: The :class:`Player` whose turn it is.
    """
    opt_capture_square = game.opponent_move_results()
    player.handle_opponent_move_result(opt_capture_square is not None, opt_capture_square)


def play_sense(game: Game, player: Player, sense_actions: List[Square], move_actions: List[chess.Move]):
    """
    Runs the sense phase for `player` in `game`. Does the following sequentially:

    #. Get the sensing action using :meth:`Player.choose_sense`.
    #. Apply the sense action using :meth:`Game.sense`.
    #. Give the result of the sense action to player using :meth:`Player.handle_sense_result`.

    :param game: The :class:`Game` that `player` is playing in.
    :param player: The :class:`Player` whose turn it is.
    :param sense_actions: The possible sense actions for `player`.
    :param move_actions: The possible move actions for `player`.
    """
    sense = player.choose_sense(sense_actions, move_actions, game.get_seconds_left())
    sense_result = game.sense(sense)
    player.handle_sense_result(sense_result)


def play_move(game: Game, player: Player, move_actions: List[chess.Move], end_turn_last=False):
    """
    Runs the move phase for `player` in `game`. Does the following sequentially:

    #. Get the moving action using :meth:`Player.choose_move`.
    #. Apply the moving action using :meth:`Game.move`.
    #. Ends the current player's turn using :meth:`Game.end_turn`.
    #. Give the result of the moveaction to player using :meth:`Player.handle_move_result`.

    If `end_turn_last` is True, then :meth:`Game.end_turn` is called last instead of before
    :meth:`Player.handle_move_result`.

    :param game: The :class:`Game` that `player` is playing in.
    :param player: The :class:`Player` whose turn it is.
    :param move_actions: The possible move actions for `player`.
    :param end_turn_last: Flag indicating whether to call :meth:`Game.end_turn` before or after :meth:`Player.handle_move_result`
    """
    move = player.choose_move(move_actions, game.get_seconds_left())
    requested_move, taken_move, opt_enemy_capture_square = game.move(move)

    if not end_turn_last:
        game.end_turn()

    player.handle_move_result(requested_move, taken_move,
                              opt_enemy_capture_square is not None, opt_enemy_capture_square)

    if end_turn_last:
        game.end_turn()


def play_multiprocessing_local_game(white_player_class, black_player_class,
                                    game: LocalGame = None, seconds_per_player: float = 900) \
        -> Tuple[Optional[Color], Optional[WinReason], GameHistory]:
    """
    Plays a game between the two players passed in. Uses :class:`LocalGame` to run the game, but enables behavior
    similar to :class:`RemoteGame` by multiprocessing. Unlike :func:`play_local_game` and :func:`play_remote_game`, the
    players here must be passed as un-initialized classes; TroutBot rather than TroutBot().

    :param white_player_class: The white :class:`Player` un-initialized.
    :param black_player_class: The black :class:`Player` un-initialized.
    :param game: The :class:`LocalGame` object to use.
    :param seconds_per_player: The time each player has to play. Only used if `game` is not passed in.
    :return: The results of the game, also passed to each player via :meth:`Player.handle_game_end`.
    """

    if game is None:
        game = LocalGame(seconds_per_player=seconds_per_player)

    white_name = white_player_class.__name__
    black_name = black_player_class.__name__
    game.store_players(white_name, black_name)

    # Stored player names become inaccessible from game (except by cheating: game._LocalGame__game_history...), instead:
    game.player_names = {
        chess.WHITE: white_name,
        chess.BLACK: black_name
    }

    player_queues = {
        chess.WHITE: {'to player': mp.Queue(), 'to moderator': mp.Queue()},
        chess.BLACK: {'to player': mp.Queue(), 'to moderator': mp.Queue()}
    }

    player_processes = [
        mp.Process(target=_play_in_multiprocessing_local_game, args=(player_queues[chess.BLACK], black_player_class)),
        mp.Process(target=_play_in_multiprocessing_local_game, args=(player_queues[chess.WHITE], white_player_class))
    ]

    [process.start() for process in player_processes]

    game.start()

    while any([process.is_alive() for process in player_processes]):
        _respond_to_requests(game, player_queues)

    winner_color = game.get_winner_color()
    win_reason = game.get_win_reason()
    game_history = game.get_game_history()

    return winner_color, win_reason, game_history


def _play_in_multiprocessing_local_game(queues, player_class):
    """
    Each player in a :class:`MultiprocessingLocalGame` uses this to participate in parallel. It mimics
    :func:`play_remote_game`, but replaces server requests with multiprocessing queues.

    :param queues: This player's dictionary of multiprocessing queues keyed 'to player' and 'to moderator'
    :param player_class: The :class:`Player` un-initialized.
    """
    game = MultiprocessingLocalGame(queues)
    player = player_class()

    player.handle_game_start(game.get_player_color(), game.get_starting_board(), game.get_opponent_name())
    game.start()

    while not game.is_over():
        play_turn(game, player, end_turn_last=False)

    winner_color = game.get_winner_color()
    win_reason = game.get_win_reason()
    game_history = game.get_game_history()

    player.handle_game_end(winner_color, win_reason, game_history)


def _respond_to_requests(game: LocalGame, queues):
    """
    Pass information between the moderator which runs a :class:`LocalGame` and each player which run their own
    :class:`RemoteGame` sub-class, :class:`MultiprocessingLocalGame`.

    :param game: The :class:`LocalGame` object to reference for neutral game-state information.
    :param queues: Multiprocessing Queues for communicating with the players. Stored as a nested dictionary of player
    color and queue direction: queues[chess.WHITE | chess.BLACK]['to player' | 'to moderator'].
    """
    for color in [game.turn, not game.turn]:
        if not queues[color]['to moderator'].empty():
            request = queues[color]['to moderator'].get()
            request_command = request[0]
            on_own_turn = game.turn == color

            if request_command == 'color':
                queues[color]['to player'].put({'color': color})

            elif request_command == 'starting_board':
                queues[color]['to player'].put({'board': chess.Board()})

            elif request_command == 'opponent_name':
                queues[color]['to player'].put({'opponent_name': game.player_names[not color]})
                # This attribute was added in moderate_multiprocessing_local_game, since the names become hard to access

            elif request_command == 'sense_actions':
                if on_own_turn:
                    queues[color]['to player'].put({'sense_actions': game.sense_actions()})
                else:
                    queues[color]['to player'].put(None)

            elif request_command == 'move_actions':
                if on_own_turn:
                    queues[color]['to player'].put({'move_actions': game.move_actions()})
                else:
                    queues[color]['to player'].put(None)

            elif request_command == 'seconds_left':
                if on_own_turn:
                    queues[color]['to player'].put({'seconds_left': game.get_seconds_left()})
                else:
                    queues[color]['to player'].put({'seconds_left': game.seconds_left_by_color[color]})

            elif request_command == 'ready':
                queues[color]['to player'].put({'ready': 'ready'})

            elif request_command == 'is_my_turn':
                queues[color]['to player'].put({'is_my_turn': on_own_turn or game.is_over()})

            elif request_command == 'opponent_move_results':
                if on_own_turn:
                    queues[color]['to player'].put({'opponent_move_results': game.opponent_move_results()})
                else:
                    queues[color]['to player'].put(None)

            elif request_command == 'sense':
                request_value = request[1]
                if on_own_turn:
                    queues[color]['to player'].put({'sense_result': game.sense(request_value['square'])})
                else:
                    queues[color]['to player'].put(None)

            elif request_command == 'move':
                request_value = request[1]
                if on_own_turn:
                    queues[color]['to player'].put({'move_result': game.move(request_value['requested_move'])})
                else:
                    queues[color]['to player'].put(None)

            elif request_command == 'end_turn':
                if on_own_turn:
                    game.end_turn()
                    queues[color]['to player'].put({'end_turn': 'done'})
                else:
                    queues[color]['to player'].put(None)

            elif request_command == 'game_status':
                queues[color]['to player'].put({'is_over': game.is_over(), 'is_my_turn': on_own_turn})

            elif request_command == 'winner_color':
                queues[color]['to player'].put({'winner_color': game.get_winner_color()})

            elif request_command == 'win_reason':
                queues[color]['to player'].put({'win_reason': game.get_win_reason()})

            elif request_command == 'game_history':
                queues[color]['to player'].put({'game_history': game.get_game_history()})

            else:
                raise KeyError(f'Requested command {request_command} is not implemented')

            # After each action, check if the game has ended
            if game.is_over():
                game.end()
