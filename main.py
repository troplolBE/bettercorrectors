# This is a sample Python script.
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

import sys
import time

base_url = 'https://api.intra.42.fr'


def get_token(client_id, client_secret):
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url='https://api.intra.42.fr/oauth/token', client_id=client_id,
                              client_secret=client_secret)
    return token["access_token"]


def get_all_pages(url, token):
    response = requests.get(f'{base_url}{url}', params={'page[size]': 30}, headers={"Authorization": f'Bearer {token}'})
    info = response.json()

    for page in range(2, 100):
        print(page)
        if page > 2:
            time.sleep(0.5)
        r = requests.get(f'{base_url}{url}', params={'page[number]': page, 'page[size]': 30}, headers={"Authorization": f'Bearer {token}'})
        if r.text == '[]' or r.text == '{}':
            break
        infos = r.json()
        print(infos)
        for inf in infos:
            info += inf

    return info


def main():
    # Here we make sure there is at least one argument
    if len(sys.argv) < 2:
        print("Please provide some parameters to the program")
        exit(1)

    # for testing purpose
    if len(sys.argv) == 3:
        token = get_token(sys.argv[1], sys.argv[2])
        exit(1)
    else:
        token = sys.argv[1]
    print(token)

    users = get_all_pages('/v2/coalitions/52/users', token)
    print(users)

    for user in users:
        if user['login'] == 'tcastron':
            print(user)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

