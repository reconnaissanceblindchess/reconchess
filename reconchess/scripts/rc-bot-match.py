import argparse
import datetime
import chess
from reconchess import load_player, play_local_game

parser = argparse.ArgumentParser()
parser.add_argument('white_bot_path', help='path to white bot source file')
parser.add_argument('black_bot_path', help='path to black bot source file')
args = parser.parse_args()

white_bot_name, white_player_cls = load_player(args.white_bot_path)
black_bot_name, black_player_cls = load_player(args.black_bot_path)

winner_color, win_reason, history = play_local_game(white_player_cls(), black_player_cls())

print('Game Over!')
if winner_color is not None:
    print('{} won because of {}!'.format(white_bot_name if winner_color else black_bot_name, win_reason))
else:
    print('Draw!')

winner = 'Draw' if winner_color is None else chess.COLOR_NAMES[winner_color]
timestamp = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')

replay_path = '{}-{}-{}-{}.json'.format(white_bot_name, black_bot_name, winner, timestamp)
print('Saving replay to {}...'.format(replay_path))
history.save(replay_path)
