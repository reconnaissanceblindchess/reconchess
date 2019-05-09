import argparse
import datetime
import traceback
import chess
from reconchess import load_player, play_local_game, LocalGame


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('white_bot_path', help='path to white bot source file')
    parser.add_argument('black_bot_path', help='path to black bot source file')
    parser.add_argument('--seconds_per_player', default=900, type=float,
                        help='number of seconds each player has to play the entire game.')
    args = parser.parse_args()

    white_bot_name, white_player_cls = load_player(args.white_bot_path)
    black_bot_name, black_player_cls = load_player(args.black_bot_path)

    game = LocalGame(args.seconds_per_player)

    try:
        winner_color, win_reason, history = play_local_game(white_player_cls(), black_player_cls(), game=game)

        winner = 'Draw' if winner_color is None else chess.COLOR_NAMES[winner_color]
    except:
        traceback.print_exc()
        game.end()

        winner = 'ERROR'
        history = game.get_game_history()

    print('Game Over!')
    print('Winner: {}!'.format(winner))

    timestamp = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')

    replay_path = '{}-{}-{}-{}.json'.format(white_bot_name, black_bot_name, winner, timestamp)
    print('Saving replay to {}...'.format(replay_path))
    history.save(replay_path)


if __name__ == '__main__':
    main()
