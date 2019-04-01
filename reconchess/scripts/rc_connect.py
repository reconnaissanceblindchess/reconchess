import argparse
import multiprocessing
from reconchess import load_player
from reconchess import play_remote_game

parser = argparse.ArgumentParser()
parser.add_argument('server', help='url to the server')
parser.add_argument('auth_file', help='path to the file that contains auth information')
parser.add_argument('bot_path', help='path to white bot source file')
parser.add_argument('--max_games', type=int, help='the maximum number of bots to start up')
args = parser.parse_args()

bot_name, bot_cls = load_player(args.white_bot_path)


def spawn_bot(game_id):
    player = bot_cls()
    multiprocessing.Process(target=play_remote_game, args=(bot_name, game_id, player))

# TODO make requests to server to see if any games are open for this player. if so, call spawn_bot()
