import os

import config


def remove_dir():
    """
    Remove the temp directories in config.py
    :return:
    """
    os.system('rm -r -f {}'.format(config.REPOSITORY_PATH))
    os.system('rm -r -f {}'.format(config.TEMP_CSV_PATH))
    os.system('rm -r -f {}'.format(config.LOG_PATH))
    os.system('rm -r -f {}'.format(config.PREDICTION_CSV_PATH))


def create_dir():
    """
    create the temp directories in config.py
    :return:
    """
    os.system('mkdir {}'.format(config.REPOSITORY_PATH))
    os.system('mkdir {}'.format(config.TEMP_CSV_PATH))
    os.system('mkdir {}'.format(config.LOG_PATH))
    os.system('mkdir {}'.format(config.PREDICTION_CSV_PATH))
