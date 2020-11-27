# imports related to authentication and requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# general imports
import time
import json
import argparse

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


def check_status_code(response):
    """Check the status code of the response in case it is not 200. Program exits after this.

    :param Response response: status code of the request
    """
    if response.status_code == 400:
        print('ERROR: The request is malformed.')
    elif response.status_code == 404:
        print('ERROR: Page or resource not found, check endpoint and request.')
    elif response.status_code == 500:
        print('ERROR: server had an error.')
    else:
        print('ERROR: unknow error.')
        print('request = |', response.url, '|')
        print(response.headers)
    print(f'ERROR: code is {response.status_code}')
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
    if response.status_code != 200:
        check_status_code(response)
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


def show_result(session, bad_evals):
    projects = get_projects(session)

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


def parse_parameters():
    """Function that setup the ArgumentParser to parse all the arguments we need to make the program run properly.

    :return ArgumentParser: returns the arguments of the program
    """
    parser = argparse.ArgumentParser(description='Program that checks for bad evaluations.')
    parser.usage = 'bettercorrectors [-h] client_id client_secret start_date [end_date] [--sql file]'
    parser.add_argument('client_id', help='the client_id of your intranet application', type=str)
    parser.add_argument('client_secret', help='the client_secret of your intra application', type=str)
    parser.add_argument('start_date', help='the latest date in iso format', type=datetime.fromisoformat)
    parser.add_argument('end_date', help='the closest date in iso format (optional)', type=datetime.fromisoformat,
                        default=datetime.now(), nargs='?')
    parser.add_argument('--sql', dest='file', help='''name of the database file in case you want to save results in a 
                        sqlite database''', type=str)
    args = parser.parse_args()
    return args


def main():
    # In this function we check that all required parameters are present.
    # An error message is displayed if not all parameters are present.
    args = parse_parameters()

    # Generate token using OAuth2 Workflow
    session = get_session(args.client_id, args.client_secret)

    dates = {'range[begin_at]': f'{args.start_date.isoformat()},{args.end_date.isoformat()}'}
    parameters = {'sort[]': '-created_at'}
    parameters.update(parameters)

    # Get al evaluations and process them
    bad_evals = check_evaluations(session, dates)
    # Check if any processed evals are bad
    if not bad_evals:
        print('No bad evaluations, your students are good correctors!')
        exit(1)
    # Print results
    show_result(session, bad_evals)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
