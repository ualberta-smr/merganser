
import os
import csv
import json
from time import gmtime, strftime

from util import *
import config
import validation


def store_repository_info(repository_name, merge_scenario_num, is_done):
    """
    Stores the information of the given repository from GitHub. TEMP_CSV_PATH should be set in config.py
    :param repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :param merge_scenario_num: The number of merge scenarios
    :param is_done: whether the analyzing of the repository is done
    :return: The id of the given repository
    """
    validation.validate_repository_name(repository_name)

    github_request = os.popen('curl --silent -H "Authorization: token  ' + config.GITHUB_KEY + \
                               '"  https://api.github.com/repos/' + repository_name.replace('___', '/')).read()

    # Check if the repository was available or invalid to analyze
    json_data = json.loads(github_request)
    if 'message' in json_data.keys() and json_data['message'] != 'Moved Permanently':
        # Remove the temporary repository directory
        remove_repository(repository_name)
        raise ValueError('The repository {} is unavailable.'.format(repository_name))

    if 'message' in json_data.keys() and json_data['message'] == 'Moved Permanently':
        # Remove the temporary repository directory
        remove_repository(repository_name)
        raise ValueError('The repository {} permanently moved.'.format(repository_name))

    if json_data['fork'] == True:
        # Remove the temporary repository directory
        remove_repository(repository_name)
        raise ValueError('The repository {} is forked.'.format(repository_name))


    # Store the data
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    repository_data = [json_data['id'], current_time, json_data['full_name'], json_data['description'], \
                      json_data['language'], json_data['subscribers_count'], \
                      json_data['stargazers_count'], json_data['forks'], json_data['open_issues'], json_data['size'],
                       merge_scenario_num, is_done]
    csv_file = open(config.TEMP_CSV_PATH + 'Repository_{}.csv'.format(repository_name), 'a')
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
    csv_writer.writerow(repository_data)
    csv_file.close()

    return json_data['id']



def get_repository_id(repository_name):
    """
    This method stores the information of the given repository from GitHub. TEMP_CSV_PATH should be set in config.py
    :param
    repository_url: The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :return: The id and size of the given repository
    """
    validation.validate_repository_name(repository_name)

    github_request = os.popen('curl --silent -H "Authorization: token  ' + config.GITHUB_KEY + \
                               '"  https://api.github.com/repos/' + repository_name.replace('___', '/')).read()
    json_data = json.loads(github_request)

    # Check if the repository was available or invalid to analyze
    json_data = json.loads(github_request)
    if 'message' in json_data.keys() and json_data['message'] != 'Moved Permanently':
        # Remove the temporary repository directory
        remove_repository(repository_name)
        raise ValueError('The repository {} is unavailable.'.format(repository_name))

    if 'message' in json_data.keys() and json_data['message'] == 'Moved Permanently':
        # Remove the temporary repository directory
        remove_repository(repository_name)
        raise ValueError('The repository {} permanently moved.'.format(repository_name))

    if json_data['fork'] == True:
        # Remove the temporary repository directory
        remove_repository(repository_name)
        raise ValueError('The repository {} is forked.'.format(repository_name))

    return json_data['id'], json_data['size']
