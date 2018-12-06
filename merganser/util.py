
import os

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
