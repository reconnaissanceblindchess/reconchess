import argparse
import datetime
import chess
from rbmc import load_player, play_local_game

parser = argparse.ArgumentParser()
parser.add_argument('white_bot_path', help='path to white bot source file')
parser.add_argument('black_bot_path', help='path to black bot source file')
args = parser.parse_args()

white_bot_name, white_player_cls = load_player(args.white_bot_path)
black_bot_name, black_player_cls = load_player(args.black_bot_path)

winner_color, win_reason, history = play_local_game(white_player_cls(), black_player_cls())

winner = 'Draw' if winner_color is None else chess.COLOR_NAMES[winner_color]
timestamp = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')

history.save('{}-{}-{}-{}.json'.format(white_bot_name, black_bot_name, winner, timestamp))
