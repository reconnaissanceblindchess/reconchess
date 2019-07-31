import argparse
import chess
from reconchess import load_player, LocalGame, GameHistory, Player, Color, play_local_game


def playback(game_history: GameHistory, player: Player, color: Color):
    game = LocalGame()

    opponent_name = game_history.get_white_player_name()
    if color == chess.WHITE:
        opponent_name = game_history.get_black_player_name()
    player.handle_game_start(color, game.board.copy(), opponent_name)
    game.start()

    turn = game_history.first_turn()

    while not game.is_over() and turn < game_history.last_turn():
        opt_capture_square = game.opponent_move_results()
        if game.turn == color:
            player.handle_opponent_move_result(opt_capture_square is not None, opt_capture_square)

        sense_actions = game.sense_actions()
        move_actions = game.move_actions()

        sense = game_history.sense(turn)
        player_sense = player.choose_sense(sense_actions, move_actions, game.get_seconds_left())
        if game.turn == color and sense != player_sense:
            print('Warning: Sense action did not match history on turn {}. Using the sense action from history.'.format(
                turn))
        sense_result = game.sense(sense)
        if game.turn == color:
            player.handle_sense_result(sense_result)

        move = game_history.requested_move(turn)
        player_move = player.choose_move(move_actions, game.get_seconds_left())
        if game.turn == color and move != player_move:
            print('Warning: Move action did not match history on turn {}. Using the move action from history.'.format(
                turn))
        requested_move, taken_move, opt_enemy_capture_square = game.move(move)
        if game.turn == color:
            player.handle_move_result(requested_move, taken_move,
                                      opt_enemy_capture_square is not None, opt_enemy_capture_square)

        game.end_turn()
        turn = turn.next

    game.end()
    winner_color = game.get_winner_color()
    win_reason = game.get_win_reason()
    game_history = game.get_game_history()

    player.handle_game_end(winner_color, win_reason, game_history)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('game_history_path', help='Path to game history JSON file.')
    parser.add_argument('bot_path', help='The path to bot source file or module.')
    parser.add_argument('color', default='random', choices=['white', 'black'],
                        help='The color of the player to playback.')
    args = parser.parse_args()

    game_history = GameHistory.from_file(args.game_history_path)
    white_bot_name, white_player_cls = load_player(args.bot_path)
    color = chess.WHITE if args.color == 'white' else chess.BLACK

    playback(game_history, white_player_cls(), color)


if __name__ == '__main__':
    main()
