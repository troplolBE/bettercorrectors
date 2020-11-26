# imports related to authentication and requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# general imports
import sys
import time
import json

from rules import detect_bad_eval
from bad_evaluation import *

base_url = 'https://api.intra.42.fr/v2'  # base url for all requests made to the api


def get_session(client_id, client_secret):
    """Method to get the OAuth2 session for all future requests

    :param str client_id: the client_id of the backend application
    :param str client_secret: the secret of the backend application
    :return: session
    """
    client = BackendApplicationClient(client_id=client_id)
    session = OAuth2Session(client=client)
    session.fetch_token(token_url='https://api.intra.42.fr/oauth/token', client_id=client_id,
                        client_secret=client_secret)
    return session


def check_status_code(status_code):
    """Checks the status code of the request and quits if it is not 200.
    Also prints an error message in the console

    :param int status_code: status code of the request
    :return: nothing
    """
    if status_code == 200:
        return True
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


def get_single_page(session, url, size, params=None):
    """Make a request to the api and only grab one page

    :param OAuth2Session session: the authenticated OAuth2 session
    :param str url: endpoint where to do the request
    :param int size: size of the page that you get (1-100)
    :param params: more paramters that you would like to pass to the request
    :return: the response
    """
    parameters = {'page[size]': size}
    if params is not None:
        parameters.update(params)
    response = session.get(f'{base_url}{url}', params=parameters)
    if response.status_code == 429:
        time.sleep(round((60 - datetime.now().second) / 60, 1) + 0.1)
        response = session.get(f'{base_url}{url}', params=parameters)
    check_status_code(response.status_code)
    return response


def get_all_pages(session, url, size, params=None):
    """Get the data on all pages of a specified url with pagesize size

    :param OAuth2Session session: the OAuth2Sesion
    :param str url: url where to do the request
    :param int size: size of the page that gets returned
    :param params: parameters for the url
    :return: all the data from all the requests made
    """
    response = get_single_page(session, url, size, params)
    parameters = {}
    entries = int(response.headers['X-Total'])
    pages = int(entries / size) + (entries % size > 1)
    data = response.json()

    if params is not None:
        parameters.update(params)
    if pages > 1:
        for page in range(2, pages + 1):
            parameters.update({'page[number]': page})
            r = get_single_page(session, url, size, params=parameters)
            try:
                new_data = r.json()
                if new_data == '[]':
                    continue
                data += new_data
            except json.JSONDecodeError:
                print('Error when decoding json, please try again...')
                exit(1)

    return data


def get_campus_students(session, school):
    """Function that returns all the unique ids of all the non-anonymized students of the school
    passed as parameter.

    :param OAuth2Session session: OAuth2 session
    :param int school: unique id of a 42 school
    :return: dict of student ids
    """
    parameters = {'filter[staff?]': False}
    users = get_all_pages(session, f'/campus/{school}/users', 100, params=parameters)
    ids = []

    for user in users:
        if not user['login'].startswith('3b3-'):
            ids.append(user['id'])

    return ids


def get_projects(session):
    """Get all the project ids and related names from certain cursus. Do not put all cursus or you
    may need to wait for several minutes due to api request limitation.

    :param OAuth2Session session: authenticated session to make requests
    :return: dict of id and project names
    """
    cursuses = [1, 21]  # cursus ids from which to get the projects
    project_names = []

    for cursus in cursuses:
        projects = get_all_pages(session, f'/cursus/{cursus}/projects', 100, {'filter[exam]': False})
        for project in projects:
            project_names.append({'id': project['id'], 'name': project['name']})

    return project_names


def get_project_name(projects, project_id):
    """Returns the project name of the given project id

    :param projects: dictionary of all the projects (id and name)
    :param project_id: id of the project name you are seeking
    :return: project name
    """
    for project in projects:
        if project['id'] == project_id:
            return project['name']


def format_range(minval, maxval=None, date=False):
    """Format value of range parameter more easily. Supports date formating to ISO 8601 format if date is set to True.

    :param minval: min value of the range
    :param maxval: max value of the range
    :param bool date: if the parameters are dates or not
    :return: formated string containing min,max
    """
    if date is True:
        mintime = datetime.strptime(minval, '%d/%m/%Y').isoformat()
        if maxval is None:
            maxtime = datetime.now().isoformat()
        else:
            maxtime = datetime.strptime(maxval, '%d/%m/%Y').isoformat()
        return f'{mintime},{maxtime}'
    else:
        return f'{minval},{maxval}'


def show_result(session, bad_evals):
    projects = get_projects(session)

    if not bad_evals:
        print('No bad evaluations, your students are good correctors!')
        exit(1)
    for bad_eval in bad_evals:
        bad_eval.project = get_project_name(projects, bad_eval.project_id)
        bad_eval.print()
        del bad_eval


def check_evaluations(session, dates):
    """Function that is going to iterate over all the evaluations of every student from a give campus
    in the give time period. The evaluations are run against a set of rules that are available
    in the rules.py file.

    :param OAuth2Session session: the session to make requests
    :param dict dates: date interval in which the program needs to search
    :return: dict of bad evaluations
    """
    user_ids = get_campus_students(session, 13)
    bad_evals = []

    print(f'found {len(user_ids)} students !')
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

    bad_evals = check_evaluations(session, dates)
    show_result(session, bad_evals)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
