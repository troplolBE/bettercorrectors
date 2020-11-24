# imports related to authentication and requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# general imports
import sys
import time
import json

from rules import *
from bad_evaluation import *

base_url = 'https://api.intra.42.fr/v2'  # base url for all requests made to the api


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


def check_status_code(status_code):
    """Checks the status code of the request and quits if it is not 200.
    Also prints an error message in the console

    :param status_code: status code of the request
    :return: nothing
    """
    if status_code == 200:
        return
    elif status_code == 400:
        print('ERROR: The request is malformed.')
    elif status_code == 404:
        print('ERROR: Page or ressource not found, check endpoint and request.')
    elif status_code == 500:
        print('ERROR: server had an error.')
    else:
        print('ERROR: unknow error.')
    print(f'ERROR: code is {status_code}')
    print('ERROR: program stopped because of request errors.')
    exit(1)


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
    if response.status_code == 429:
        time.sleep(round((60 - datetime.now().second) / 60, 1) + 0.1)
        response = session.get(f'{base_url}{url}', params=parameters)
    check_status_code(response.status_code)
    entries = int(response.headers['X-Total'])
    pages = int(entries / size) + (entries % size > 1)
    data = response.json()

    if pages > 1:
        for page in range(2, pages + 1):
            parameters.update({'page[number]': page})
            r = session.get(f'{base_url}{url}', params=parameters)
            if r.status_code == 429:
                time.sleep(round((60 - datetime.now().second) / 60, 1) + 0.1)
                r = session.get(f'{base_url}{url}', params=parameters)
            check_status_code(r.status_code)
            try:
                new_data = r.json()
                if new_data == '[]':
                    continue
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
    check_status_code(response.status_code)
    if response.status_code == 429:
        time.sleep(round((60 - datetime.now().second) / 60, 1) + 0.1)
        response = session.get(f'{base_url}{url}', params=parameters)
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


def detect_bad_eval(evaluation):
    rules = [rule1, rule2]

    for index, rule in enumerate(rules, 1):
        if rule(evaluation):
            return create_bad_eval(evaluation, index)
    return False


def check_evaluations(session, dates):
    user_ids = get_campus_students(session, 13)
    bad_evals = []

    for user_id in user_ids:
        evaluations = get_all_pages(session, f'/users/{user_id}/scale_teams/as_corrected', 100, params=dates)
        if evaluations == '[]':
            continue
        for evaluation in evaluations:
            bad = detect_bad_eval(evaluation)
            if isinstance(bad, BadEvaluation):
                bad_evals.append(bad)

    return bad_evals


def main():
    # Here we make sure there is at least one argument
    if len(sys.argv) != 3:
        print("Please provide client_id and client_secret.")
        exit(1)

    session = get_session(sys.argv[1], sys.argv[2])

    dates = {'range[begin_at]': format_range('18/10/2018', '19/10/2018', True)}
    dates.update({'sort[]': '-created_at'})

    # corrected = get_single_page(session, '/users/38492/scale_teams/as_corrected', 5, dates)
    # print(json.dumps(corrected, indent=4))

    bad_evals = check_evaluations(session, dates)
    if bad_evals is []:
        print('No bad evaluations, your students are good correctors!')
    else:
        for bad_eval in bad_evals:
            bad_eval.print()
            del bad_eval


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
