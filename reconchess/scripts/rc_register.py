import argparse
import requests
import getpass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='Name to register under')
    parser.add_argument('--server-url', default='https://rbc.jhuapl.edu', help='URL of the server.')
    args = parser.parse_args()

    password = getpass.getpass()

    response = requests.post('{}/api/users/'.format(args.server_url), json={
        'username': args.username,
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
