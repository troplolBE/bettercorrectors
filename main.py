# imports related to authentication and requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# general imports
import time
import json
import argparse
import os

from rules import detect_bad_eval
from bad_evaluation import *
from database import *

base_url = 'https://api.intra.42.fr/v2'  # base url for all requests made to the api


def get_session(client_id, client_secret):
    """Method that uses given client_id and client_secret to authenticate to the api server
    using the OAuth2 BackendApplication workflow.

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
    """Make a request to a 42 endpoint with the optional parameters params and by setting the parameter page[siz] to
    size in order to control how much indexes are returned. Ex: set size to 1 to get 1 index from request.

    :param OAuth2Session session: the authenticated OAuth2 session
    :param str url: endpoint where to do the request
    :param int size: size of the page that you get (1-100)
    :param params: more paramters that you would like to pass to the request
    :return: the response
    """
    # Parameter to control number of returned indexes
    parameters = {'page[size]': size}
    # Add argument parameters to page parameter if exists
    if params is not None:
        parameters.update(params)
    # Make the request
    response = session.get(f'{base_url}{url}', params=parameters)
    # Check fi we didn't exceed the request limit rate -> 429
    if response.status_code == 429:
        # Calculate miliseconds needed to sleep until next second (fails in some cases, was optimization attempt)
        time.sleep(round((60 - datetime.now().second) / 60, 1) + 0.1)
        # Do request again after waiting
        response = session.get(f'{base_url}{url}', params=parameters)
    # Check for other status codes if request not complete
    if response.status_code != 200:
        check_status_code(response)
    return response


def get_all_pages(session, url, size, params=None):
    """Make a request to a 42 endpoint with the function get_single_age. Because the 42 api uses a pagination system
    this function get the first page and the detects how many pages there are by reading the X-Total header which gives
    the number indexes on an endpoint with a specific query. It then cycles through all the pages to return all the data
    available.

    :param OAuth2Session session: the OAuth2Sesion
    :param str url: url where to do the request
    :param int size: size of the page that gets returned
    :param params: parameters for the url
    :return: all the data from all the requests made
    """
    # Get first page to get results and detect number fo pages
    response = get_single_page(session, url, size, params)
    parameters = {}
    # Get number of indexes for this request
    entries = int(response.headers['X-Total'])
    # Calculate amount of pages that need to be requested
    pages = int(entries / size) + (entries % size > 1)
    # Data retrived by the request
    data = response.json()

    # Add params if custom parameters
    if params is not None:
        parameters.update(params)
    # Detect if more than 1 page
    if pages > 1:
        # Range between 2 and pages + 1 to get the last one as well
        for page in range(2, pages + 1):
            # Update parameters with page[number] parameter
            parameters.update({'page[number]': page})
            # Make the request
            r = get_single_page(session, url, size, params=parameters)
            try:
                # Merge data from request with already received data
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
    passed as parameter. We also filter the request to avoid staff acoounts, may reduce the number
    of requests by 1.

    :param OAuth2Session session: OAuth2 session
    :param int school: unique id of a 42 school
    :return: dict of student ids
    """
    # Parameter to avoid getting staff users
    parameters = {'filter[staff?]': False}
    users = get_all_pages(session, f'/campus/{school}/users', 100, params=parameters)
    ids = []

    for user in users:
        # Check that the user is not anonymized by checking first letters of login
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
        # Get all the projects from 1 cursus, very slow process because projects endpoint contains
        # a lot of information
        projects = get_all_pages(session, f'/cursus/{cursus}/projects', 100, {'filter[exam]': False})
        for project in projects:
            # Create dictionary containing project id and project name ans set in bigger dict
            project_names.append({'id': project['id'], 'name': project['name']})

    return project_names


def get_project_name(projects, project_id):
    """Runs through all projects to find a matching id and return the corresponding name

    :param projects: dictionary of all the projects (id and name)
    :param project_id: id of the project name you are seeking
    :return: name of the project
    """
    for project in projects:
        if project['id'] == project_id:
            return project['name']


def print_evaluations(session, bad_evals):
    """Print all the bad evaluations in the console with a pretty string.

    :param OAuth2Session session: session to gather the projects
    :param bad_evals: the bad evaluations that need to be printed
    """
    # Gather all the project ids and names, this is a very very slow process
    projects = get_projects(session)

    # Print all bad evaluations
    for bad_eval in bad_evals:
        # project_name is set here and not in create_bad_eval to make program faster in
        # case there are no bad evaluations. (less requests, less processing)
        bad_eval.project_name = get_project_name(projects, bad_eval.project_id)
        bad_eval.print()
        del bad_eval


def save_evaluations(session, database, bad_evals):
    """Store all the bad evaluations in a sqlite file.

    :param OAuth2Session session: the oauth 2 session for the projects
    :param str database: name of the database file
    :param bad_evals: all the bad evaluations
    """
    # Create result directory and go in it
    os.makedirs('result', exist_ok=True)
    os.chdir('result')
    # Create database file
    conn = create_connection(database)
    # Gather all the project ids and names, this is a very very slow process
    projects = get_projects(session)

    print(f'saving results in results\\{database}...')
    # Save each bad eval in the database file
    for bad_eval in bad_evals:
        # project_name is set here and not in create_bad_eval to make program faster in
        # case there are no bad evaluations. (less requests, less processing)
        bad_eval.project_name = get_project_name(projects, bad_eval.project_id)
        insert_evaluation(conn, bad_eval.sql_tuple())
        del bad_eval

    print('results saved !')


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
        # Get all evaluations from student id in selected timeframe
        evaluations = get_all_pages(session, f'/users/{user_id}/scale_teams/as_corrected', 100, params=dates)
        if evaluations == '[]':
            continue
        # Check each returned evaluation if bad or not
        for evaluation in evaluations:
            # Object BadEvaluation is returned if rules come back True
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
    print('Authentication successful !')

    # Prepare fate parameters for evaluations query
    dates = {'range[begin_at]': f'{args.start_date.isoformat()},{args.end_date.isoformat()}'}
    parameters = {'sort[]': '-created_at'}
    parameters.update(parameters)

    # Get al evaluations and process them
    bad_evals = check_evaluations(session, dates)
    # Check if any processed evals are bad
    if not bad_evals:
        print('No bad evaluations, your students are good correctors!')
        exit(1)
    # Show how much bad evaluations were found
    print(f'found {len(bad_evals)} bad evaluations !')
    # Check if need to save in database
    if args.file:
        save_evaluations(session, args.file, bad_evals)
    else:
        print_evaluations(session, bad_evals)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
