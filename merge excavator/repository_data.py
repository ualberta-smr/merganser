
import os
import csv
import json
from time import gmtime, strftime

import config


def get_repositort_info(repository_name):
    """
    This method retrieves the information of the given repository from GitHub. GITHUB_KEY should be set in config.py
    :param
    repository_url: The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :return: The list of repository data
    """
    github_requerst = os.popen('curl --silent -H "Authorization: token  ' + config.GITHUB_KEY + \
                               '"  https://api.github.com/repos/' + repository_name).read()
    json_data = json.loads(github_requerst)
    if 'message' in json_data.keys():
        raise ValueError('The repository {} does not exists.'.format(repository_name))
    current_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    return json_data['id'], current_time, json_data['full_name'], json_data['description'], json_data['language'], \
           json_data['subscribers_count'], \
           json_data['stargazers_count'], json_data['forks'], json_data['open_issues'], json_data['size']


def store_repository_info(repository_name):
    """
    This method stores the information of the given repository from GitHub. TEMP_CSV_PATH should be set in config.py
    :param
    repository_url: The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :return: The list of repository data
    """
    if repository_name.count('/') != 1:
        raise ValueError('The repositort name should be in <USER_NAME>/<REPOSITORY_NAME> format. \
         {} does not follow this.'.format(repository_name))
    csv_file = open(config.TEMP_CSV_PATH + 'Repository.csv', 'a')
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
    csv_writer.writerow(get_repositort_info(repository_name))
    csv_file.close()
