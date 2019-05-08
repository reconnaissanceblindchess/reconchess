import argparse
import chess
import datetime
import random
from reconchess import play_remote_game
from reconchess.scripts.rc_connect import RBCServer, ask_for_auth
from reconchess.scripts.rc_play import UIPlayer


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--color', default='random', choices=['white', 'black', 'random'],
                        help='The color you want to play as.')
    parser.add_argument('--server-url', default='https://rbc.jhuapl.edu', help='URL of the server.')
    args = parser.parse_args()

    auth = ask_for_auth()

    server = RBCServer(args.server_url, auth)

    usernames = server.get_active_users()

    if auth[0] in usernames:
        usernames.remove(auth[0])

    if len(usernames) == 0:
        print('No active users.')
        quit()

    for i, username in enumerate(usernames):
        print('[{}] {}'.format(i, username))
    i = int(input('Choose opponent: '))

    color = chess.WHITE
    if args.color == 'black' or (args.color == 'random' and random.uniform(0, 1) < 0.5):
        color = chess.BLACK

    game_id = server.send_invitation(usernames[i], color)

    winner_color, win_reason, game_history = play_remote_game(args.server_url, game_id, auth, UIPlayer())

    winner = 'Draw' if winner_color is None else chess.COLOR_NAMES[winner_color]
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    game_history.save('{}_{}_{}.json'.format(timestamp, game_id, winner))


if __name__ == '__main__':
    main()
