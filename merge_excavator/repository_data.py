
import os
import csv
import json
from time import gmtime, strftime

import config
import validation


def store_repository_info(repository_name, merge_scenario_num, is_done):
    """
    This method stores the information of the given repository from GitHub. TEMP_CSV_PATH should be set in config.py
    :param
    repository_url: The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :return: The Nothing
    """
    validation.validate_repository_name(repository_name)

    github_request = os.popen('curl --silent -H "Authorization: token  ' + config.GITHUB_KEY + \
                               '"  https://api.github.com/repos/' + repository_name.replace('___', '/')).read()
    json_data = json.loads(github_request)
    if 'message' in json_data.keys() and json_data['message'] != 'Moved Permanently':
         raise ValueError('The repository {} does not exists.'.format(repository_name))
    if 'message' in json_data.keys() and json_data['message'] == 'Moved Permanently':
         return -1
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
    :return: The Nothing
    """
    validation.validate_repository_name(repository_name)

    github_request = os.popen('curl --silent -H "Authorization: token  ' + config.GITHUB_KEY + \
                               '"  https://api.github.com/repos/' + repository_name.replace('___', '/')).read()
    json_data = json.loads(github_request)
    if 'message' in json_data.keys() and json_data['message'] != 'Moved Permanently':
         raise ValueError('The repository {} does not exists.'.format(repository_name))
    if 'message' in json_data.keys() and json_data['message'] == 'Moved Permanently':
         return -1
    return json_data['id'], json_data['size']
