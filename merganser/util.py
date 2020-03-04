
import os

import pandas as pd

import config


def remove_repository(repository_name):
    """
    Clean up the repository directory
    :param repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :return: -
    """
    os.system('rm -r -f {}'.format(os.getcwd() + '/' + config.REPOSITORY_PATH + repository_name))


def remove_dir():
    """
    Remove the temp directories in config.py
    :return: -
    """
    os.system('rm -r -f {}'.format(config.REPOSITORY_PATH))
    os.system('rm -r -f {}'.format(config.TEMP_CSV_PATH))
    os.system('rm -r -f {}'.format(config.LOG_PATH))
    os.system('rm -r -f {}'.format(config.PREDICTION_CSV_PATH))


def create_dir():
    """
    create the temp directories in config.py
    :return: -
    """
    os.system('mkdir {}'.format(config.REPOSITORY_PATH))
    os.system('mkdir {}'.format(config.TEMP_CSV_PATH))
    os.system('mkdir {}'.format(config.LOG_PATH))
    os.system('mkdir {}'.format(config.PREDICTION_CSV_PATH))

class Repository_language:

    def __init__(self):
        self.repo_langs = pd.read_csv(config.REPOSITORY_LIST_PATH + 'reaper_languages' + '.csv')
        self.repo_langs['repository'] = [str(i).lower().replace('/', '-') for i in self.repo_langs['repository']] 

        self.repo_langs.set_index('repository', inplace=True)

    def get_lang(self, repo_name):
        return self.repo_langs.loc[repo_name][0]

