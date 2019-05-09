import argparse
import requests
import multiprocessing
import time
import getpass
from datetime import datetime
from reconchess import load_player, play_remote_game


class RBCServer:
    def __init__(self, server_url, auth):
        self.invitations_url = '{}/api/invitations'.format(server_url)
        self.user_url = '{}/api/users'.format(server_url)
        self.me_url = '{}/api/users/me'.format(server_url)
        self.session = requests.Session()
        self.session.auth = auth

    def is_connected(self):
        try:
            response = self.session.post(self.me_url)
            if response.status_code == 401:
                print('Authentication Error!')
                print(response.text)
                quit()
            return response.status_code == 200 and response.json()['username'] == self.session.auth[0]
        except requests.RequestException:
            pass
        return False

    def set_max_games(self, max_games):
        self.session.post('{}/max_games'.format(self.me_url), json={'max_games': max_games})

    def get_active_users(self):
        response = self.session.get('{}/'.format(self.user_url))
        return response.json()['usernames']

    def send_invitation(self, opponent, color):
        response = self.session.post('{}/'.format(self.invitations_url), json={
            'opponent': opponent,
            'color': color,
        })
        return response.json()['game_id']

    def get_invitations(self):
        response = self.session.get('{}/'.format(self.invitations_url))
        return response.json()['invitations']

    def accept_invitation(self, invitation_id):
        response = self.session.post('{}/{}'.format(self.invitations_url, invitation_id))
        return response.json()['game_id']


def accept_invitation_and_play(server_url, auth, invitation_id, bot_cls):
    print('[{}] Accepting invitation {}.'.format(datetime.now(), invitation_id))

    server = RBCServer(server_url, auth)
    game_id = server.accept_invitation(invitation_id)

    print('[{}] Invitation {} accepted. Playing game {}.'.format(datetime.now(), invitation_id, game_id))

    play_remote_game(server_url, game_id, auth, bot_cls())

    print('[{}] Finished game {}'.format(datetime.now(), game_id))


def listen_for_invitations(server_url, auth, bot_cls, max_concurrent_games):
    server = RBCServer(server_url, auth)

    connected = False
    queued_invitations = set()
    with multiprocessing.Pool(processes=max_concurrent_games) as pool:
        while True:
            while not server.is_connected():
                connected = False
                print('[{}] Could not connect to server... waiting 60 seconds before trying again.'.format(
                    datetime.now()))
                time.sleep(60)

            if not connected:
                print('[{}] Connected successfully to server!'.format(datetime.now()))
                connected = True
                server.set_max_games(max_concurrent_games)

            try:
                invitations = server.get_invitations()
                unqueued_invitations = set(invitations) - queued_invitations
                for invitation_id in unqueued_invitations:
                    print('[{}] Received invitation {}.'.format(datetime.now(), invitation_id))
                    pool.apply_async(accept_invitation_and_play, args=(server_url, auth, invitation_id, bot_cls))
                    queued_invitations.add(invitation_id)
            except requests.RequestException as e:
                print(e)

            time.sleep(5)


def ask_for_auth():
    username = input('Username: ')
    password = getpass.getpass()
    return username, password


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('bot_path', help='Path to bot source or bot module name.')
    parser.add_argument('--server-url', default='https://rbc.jhuapl.edu', help='URL of the server.')
    parser.add_argument('--max-concurrent-games', type=int, default=4,
                        help='The maximum number of games to play at the same time.')
    args = parser.parse_args()

    bot_name, bot_cls = load_player(args.bot_path)

    auth = ask_for_auth()

    listen_for_invitations(args.server_url, auth, bot_cls, args.max_concurrent_games)


if __name__ == '__main__':
    main()
