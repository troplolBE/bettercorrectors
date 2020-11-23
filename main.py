# imports related to authentication and requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# general imports
import sys
import time
from datetime import datetime

base_url = 'https://api.intra.42.fr/v2'  # base url for all requests made to the api


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


def get_all_pages(session, url, size, params=None):
    """Get the data on all pages of a specified url with pagesize size

    :param session: the OAuth2Sesion
    :param url: url where to do the request
    :param size: size of the page that gets returned
    :param params: parameters for the url
    :return: info
    """
    parameters = {'page[size]': size}
    if params is not None:
        parameters.update(params)
    response = session.get(f'{base_url}{url}', params=parameters)
    if response.status_code == 404:
        print('Not found :/')
        return 'No results in query'
    entries = int(response.headers['X-Total'])
    pages = int(entries / size) + (entries % size > 1)
    info = response.json()

    if pages > 1:
        for page in range(2, pages + 1):
            parameters.update({'page[number]': page})
            r = session.get(f'{base_url}{url}', params=parameters)
            if r.status_code == 429:
                time.sleep(round((60 - datetime.now().second) / 60, 2))
                r = session.get(f'{base_url}{url}', params=parameters)
            info += r.json()

    return info


def get_single_page(session, url, size, params=None):
    parameters = {'page[size]': size}
    if params is not None:
        parameters.update(params)
    response = session.get(f'{base_url}{url}', params=parameters)
    print(response.request.url)
    if response.status_code == 404:
        print('Not found :/', f'\nerror code {response.status_code}')
        return 'No results in query'
    info = response.json()

    return info


def get_campus_students(session, id):
    parameters = {'filter[staff?]': False}
    allusers = get_all_pages(session, f'/campus/{id}/users', 100, params=parameters)
    ids = []
    for user in allusers:
        if not user['login'].startswith('3b3-'):
            print(user)
            ids.append(user['id'])

    return ids


def format_dates(start, end=None):
    """Function that returns the dates given by the user in ISO 8601 formato be passed as parameter in the request
    to the api.

    :param start: min value for the range, the latest date in xx/xx/xx format
    :param end: max value for the range, the closest date in xx/xx/xx format
    :return: dates formated in string for range parameter
    """
    mintime = datetime.strptime(start, '%d/%m/%Y').isoformat()
    if end is None:
        maxtime = datetime.now().isoformat()
    else:
        maxtime = datetime.strptime(end, '%d/%m/%Y').isoformat()
    return f'{mintime},{maxtime}'


def format_range(minval, maxval=None, date=False):
    """Format value of range parameter more easily. Supports date formating to ISO 8601 format if date is set to True.

    :param minval: min value of the range
    :param maxval: max value of the range
    :param date: if the parameters are dates or not
    :return: formated string containing min,max
    """
    if date is True:
        return format_dates(minval, maxval)
    else:
        return f'{minval},{maxval}'


def main():
    # Here we make sure there is at least one argument
    if len(sys.argv) != 3:
        print("Please provide client_id and client_secret.")
        exit(1)

    session = get_token(sys.argv[1], sys.argv[2])
    dates = {'range[created_at]': format_range('22/10/2020', '22/11/2020', True)}
    dates2 = {'range[created_at]': format_range('22/02/2020', '22/11/2020', True)}

    scales = get_all_pages(session, '/users/38492/scale_teams/as_corrector', 30, dates)
    corrected = get_single_page(session, '/users/38492/scale_teams/as_corrected', 1)
    print(scales)
    print(corrected)

    #for user in scales:
    #    if user['login'] == 'tcastron':
    #        print(user)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

