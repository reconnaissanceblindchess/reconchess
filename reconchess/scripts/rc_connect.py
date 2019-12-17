import argparse
import requests
import multiprocessing
import time
import getpass
import traceback
from datetime import datetime
from reconchess import load_player, play_remote_game


class RBCServer:
    def __init__(self, server_url, auth):
        self.invitations_url = '{}/api/invitations'.format(server_url)
        self.user_url = '{}/api/users'.format(server_url)
        self.me_url = '{}/api/users/me'.format(server_url)
        self.game_url = '{}/api/games'.format(server_url)
        self.session = requests.Session()
        self.session.auth = auth

    def _get(self, endpoint):
        response = self.session.get(endpoint)
        while response.status_code >= 500:
            time.sleep(0.5)
            response = self.session.get(endpoint)
        if response.status_code == 401:
            print('Authentication Error!')
            print(response.text)
            quit()
        return response.json()

    def _post(self, endpoint, json=None):
        response = self.session.post(endpoint, json=json)
        while response.status_code >= 500:
            time.sleep(0.5)
            response = self.session.post(endpoint, json=json)
        if response.status_code == 401:
            print('Authentication Error!')
            print(response.text)
            quit()
        return response.json()

    def set_max_games(self, max_games):
        self._post('{}/max_games'.format(self.me_url), json={'max_games': max_games})

    def get_active_users(self):
        return self._get('{}/'.format(self.user_url))['usernames']

    def send_invitation(self, opponent, color):
        return self._post('{}/'.format(self.invitations_url), json={
            'opponent': opponent,
            'color': color,
        })['game_id']

    def get_invitations(self):
        return self._get('{}/'.format(self.invitations_url))['invitations']

    def accept_invitation(self, invitation_id):
        return self._post('{}/{}'.format(self.invitations_url, invitation_id))['game_id']

    def finish_invitation(self, invitation_id):
        self._post('{}/{}/finish'.format(self.invitations_url, invitation_id))

    def error_resign(self, game_id):
        return self._post('{}/{}/error_resign'.format(self.game_url, game_id))


def accept_invitation_and_play(server_url, auth, invitation_id, bot_cls):
    print('[{}] Accepting invitation {}.'.format(datetime.now(), invitation_id))

    server = RBCServer(server_url, auth)
    game_id = server.accept_invitation(invitation_id)

    print('[{}] Invitation {} accepted. Playing game {}.'.format(datetime.now(), invitation_id, game_id))

    try:
        play_remote_game(server_url, game_id, auth, bot_cls())
        print('[{}] Finished game {}'.format(datetime.now(), game_id))
    except:
        print('[{}] Fatal error in game {}:'.format(datetime.now(), game_id))
        traceback.print_exc()
        server.error_resign(game_id)

    server.finish_invitation(invitation_id)


def listen_for_invitations(server_url, auth, bot_cls, max_concurrent_games):
    server = RBCServer(server_url, auth)

    connected = False
    process_by_invitation = {}
    while True:
        try:
            # get unaccepted invitations
            invitations = server.get_invitations()

            # set max games on server if this is the first successful connection after being disconnected
            if not connected:
                print('[{}] Connected successfully to server!'.format(datetime.now()))
                connected = True
                server.set_max_games(max_concurrent_games)

            # filter out finished processes
            process_by_invitation = {i: p for i, p in process_by_invitation.items() if p.is_alive()}

            # accept invitations until we have #max_concurrent_games processes alive
            for invitation in invitations:
                # only accept the invitation if we have room and the invite doesn't have a process already
                if len(process_by_invitation) < max_concurrent_games and invitation not in process_by_invitation:
                    print('[{}] Received invitation {}.'.format(datetime.now(), invitation))

                    # start the process for playing a game
                    process = multiprocessing.Process(
                        target=accept_invitation_and_play, args=(server_url, auth, invitation, bot_cls))
                    process.start()

                    # store the process so we can check when it finishes
                    process_by_invitation[invitation] = process

        except requests.RequestException as e:
            connected = False
            print('[{}] Failed to connect to server'.format(datetime.now()))
            print(e)
        except Exception:
            print("Error in invitation processing: ")
            traceback.print_exc()

        time.sleep(5)


def ask_for_username():
    return input('Username: ')


def ask_for_password():
    return getpass.getpass()


def ask_for_auth():
    return ask_for_username(), ask_for_password()


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('bot_path', help='Path to bot source or bot module name.')
    parser.add_argument('--username', default=None, help='Username for login. Enter with prompt if not specified.')
    parser.add_argument('--password', default=None, help='Password for login. Enter with prompt if not specified.')
    parser.add_argument('--server-url', default='https://rbc.jhuapl.edu', help='URL of the server.')
    parser.add_argument('--max-concurrent-games', type=int, default=4,
                        help='The maximum number of games to play at the same time.')
    args = parser.parse_args()

    bot_name, bot_cls = load_player(args.bot_path)

    username = ask_for_username() if args.username is None else args.username
    password = ask_for_password() if args.password is None else args.password
    auth = username, password

    listen_for_invitations(args.server_url, auth, bot_cls, args.max_concurrent_games)


if __name__ == '__main__':
    main()
