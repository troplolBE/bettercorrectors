# imports related to authentication and requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# general imports
import sys
import time
import json
from datetime import datetime

base_url = 'https://api.intra.42.fr/v2'  # base url for all requests made to the api

"""
list of needed things to show to user:
- scale id
- login corrector
- login corrected
- number detection rule
- time
"""


class BadEvaluation:
    def __init__(self, scale_id, corrector=None, correctorid=None, corrected=None, correctedid=None, detection=None, time=None, project=None):
        self.scale_id = scale_id
        self.corrector = corrector
        self.correctorid = correctorid
        self.corrected = corrected
        self.correctedid = correctedid
        self.detection = detection
        self.time = time
        self.project = project
        self.date = datetime.fromisoformat(time)

    def print(self):  # bad eval: nsondag corrected tcastron's 42sh on time and it was detected bad by rule number
        print(f'bad evaluation: {self.corrector}({self.correctorid}) ')
        print(f'corrected {self.corrected}({self.correctedid})\'s {self.project} ')
        print(f'on {self.time.month} {self.time.day} {self.time.year} at {self.time.hour}:{self.time.minute} ')
        print(f'and it was considered bad by rule number {self.detection}')


def get_session(client_id, client_secret):
    """Method to get the OAuth2 session for all future requests

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
    print(response.status_code, response.reason)
    if response.status_code != 200:
        print('Not found :/')
        return 'No results in query'
    entries = int(response.headers['X-Total'])
    pages = int(entries / size) + (entries % size > 1)
    data = response.json()

    if pages > 1:
        for page in range(2, pages + 1):
            parameters.update({'page[number]': page})
            r = session.get(f'{base_url}{url}', params=parameters)
            if r.status_code == 429:
                time.sleep(round((60 - datetime.now().second) / 60, 2))
                r = session.get(f'{base_url}{url}', params=parameters)
            new_data = r.json()
            try:
                data += new_data
            except json.JSONDecodeError:
                print('Error when decoding json, please try again...')
                exit(1)

    return data


def get_single_page(session, url, size, params=None):
    """Make a resquest to the api and only grab one page

    :param session: the authenticated OAuth2 session
    :param url: endpoint where to do the request
    :param size: size of the page that you get (1-100)
    :param params: more paramters that you would like to pass to the request
    :return: the data from your request
    """
    parameters = {'page[size]': size}
    if params is not None:
        parameters.update(params)
    response = session.get(f'{base_url}{url}', params=parameters)
    if response.status_code != 200 or response.json() == '[]':
        print('Not found :/', f'\nerror code {response.status_code}')
        return 'No results in query'
    return response.json()


def get_campus_students(session, school):
    """Function that returns all the unique ids of all the non-anonymized students of the school
    passed as parameter.

    :param session: OAuth2 session
    :param school: unique id of a 42 school
    :return: dict of ids
    """
    parameters = {'filter[staff?]': False}
    users = get_all_pages(session, f'/campus/{school}/users', 100, params=parameters)
    ids = []
    for user in users:
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

    session = get_session(sys.argv[1], sys.argv[2])

    corrected = get_single_page(session, '/users/38492/scale_teams/as_corrected', 5, dates)
    print(json.dumps(corrected, indent=4))

    for corr in corrected:
        print('id=', corr['id'])
        print('corrector={}, corrected_id={}'.format(corr['corrector']['login'], corr['corrector']['id']))
        correcteds = corr['correcteds']
        for corrected in correcteds:
            print('corrected={}, corrected_id={}'.format(corrected['login'], corrected['id']))
        print('time=', corr['created_at'])
        print('project=', corr['team']['project_id'])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
