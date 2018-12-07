import chess
from .types import *
from .player import Player
from .game import Game, LocalGame, RemoteGame
from .history import GameHistory


def play_local_game(white_player: Player, black_player: Player) -> Tuple[
    Optional[Color], Optional[WinReason], GameHistory]:
    players = [black_player, white_player]

    game = LocalGame()

    white_player.handle_game_start(chess.WHITE, game.board.copy())
    black_player.handle_game_start(chess.BLACK, game.board.copy())
    game.start()

    while not game.is_over():
        play_turn(game, players[game.turn])

    game.end()
    winner_color = game.get_winner_color()
    win_reason = game.get_win_reason()
    game_history = game.get_game_history()

    white_player.handle_game_end(winner_color, win_reason, game_history)
    black_player.handle_game_end(winner_color, win_reason, game_history)

    return winner_color, win_reason, game_history


def play_remote_game(name, game_id, player: Player):
    game = RemoteGame(game_id)

    color = game.get_player_color(name)

    player.handle_game_start(color, game.get_starting_board())
    game.start()

    while not game.is_over():
        game.wait_for_turn(name)
        play_turn(game, player)

    player.handle_game_end(game.get_winner_color(), game.get_game_history())


def play_turn(game: Game, player: Player):
    sense_actions = game.sense_actions()
    move_actions = game.move_actions()

    notify_opponent_move_results(game, player)

    play_sense(game, player, sense_actions, move_actions)

    play_move(game, player, move_actions)

    game.end_turn()


def notify_opponent_move_results(game: Game, player: Player):
    opt_capture_square = game.opponent_move_results()
    player.handle_opponent_move_result(opt_capture_square is not None, opt_capture_square)


def play_sense(game: Game, player: Player, sense_actions: List[Square], move_actions: List[chess.Move]):
    sense = player.choose_sense(game.get_seconds_left(), sense_actions, move_actions)
    sense_result = game.sense(sense)
    player.handle_sense_result(sense_result)


def play_move(game: Game, player: Player, move_actions: List[chess.Move]):
    move = player.choose_move(game.get_seconds_left(), move_actions)
    requested_move, taken_move, opt_enemy_capture_square = game.move(move)
    player.handle_move_result(requested_move, taken_move,
                              opt_enemy_capture_square is not None, opt_enemy_capture_square)
