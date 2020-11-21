# imports related to authentication and requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# general imports
import sys
import time

base_url = 'https://api.intra.42.fr'  # base url for all requests made to the api


def get_token(client_id, client_secret):
    """Method to get the OAuth2 session for further requests

    :param client_id: the client_id of the backend application
    :param client_secret: the secret of the backend application
    :return session
    """
    client = BackendApplicationClient(client_id=client_id)
    session = OAuth2Session(client=client)
    session.fetch_token(token_url='https://api.intra.42.fr/oauth/token', client_id=client_id,
                        client_secret=client_secret)
    return session


def get_all_pages(session, url, size):
    """Get the data on all pages of a specified url with pagesize size

    :param session: the OAuth2Sesion
    :param url: url where to do the request
    :param size: size of the page that gets returned
    :return: info
    """
    response = session.request('GET', f'{base_url}{url}', params={'page[size]': size})
    info = response.json()

    for page in range(2, 100):
        print(page)
        if page > 2:
            time.sleep(0.5)
        r = session.request('GET', f'{base_url}{url}', params={'page[number]': page, 'page[size]': size})
        if r.text == '[]' or r.text == '{}':
            break
        infos = r.json()
        print(infos)
        for inf in infos:
            info += inf

    return info


def main():
    # Here we make sure there is at least one argument
    if len(sys.argv) != 3:
        print("Please provide client_id and client_secret.")
        exit(1)

    # for testing purpose
    if len(sys.argv) == 3:
        session = get_token(sys.argv[1], sys.argv[2])

    users = get_all_pages(session, '/v2/coalitions/52/users', 100)
    print(users)

    for user in users:
        if user['login'] == 'tcastron':
            print(user)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

