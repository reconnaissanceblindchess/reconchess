import argparse
import requests
from reconchess.scripts.rc_connect import ask_for_username, ask_for_password


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--username', default=None, help='Name to register under. Enter with prompt if not specified.')
    parser.add_argument('--email', default=None, help='Email to associate with account. Enter with prompt if not specified.')
    parser.add_argument('--password', default=None, help='Password to use. Enter with prompt if not specified.')
    parser.add_argument('--server-url', default='https://rbc.jhuapl.edu', help='URL of the server.')
    args = parser.parse_args()

    try:
        requests.get('{}/api/users'.format(args.server_url))
    except:
        print('No server found at {} - it may not be available yet.'.format(args.server_url))
        quit()

    username = ask_for_username() if args.username is None else args.username
    email = input('Email: ') if args.email is None else args.email
    password = ask_for_password() if args.password is None else args.password

    response = requests.post('{}/api/users/'.format(args.server_url), json={
        'username': username,
        'email': email,
        'password': password,
    })

    if response.status_code == 200:
        username = response.json()['username']
        print('Successfully registered with username "{}".'.format(username))
    elif response.status_code == 409:
        print('Unsuccessful... "{}" is already in use! Choose a different name.'.format(args.username))
    else:
        print('Unsuccessful... returncode={}'.format(response.status_code))


if __name__ == '__main__':
    main()
