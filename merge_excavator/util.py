import os

import config


def remove_dir():
    os.system('rm -r -f {}'.format(config.REPOSITORY_PATH))
    os.system('rm -r -f {}'.format(config.TEMP_CSV_PATH))
    os.system('rm -r -f {}'.format(config.LOG_PATH))


def create_dir():
    os.system('mkdir {}'.format(config.REPOSITORY_PATH))
    os.system('mkdir {}'.format(config.TEMP_CSV_PATH))
    os.system('mkdir {}'.format(config.LOG_PATH))
