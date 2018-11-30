
import os
from joblib import Parallel, delayed
import multiprocessing

import config
import validation


def clone_repository(repository_name):
    """
    Receiving a name of the repository in  <USER_NAME>/<REPOSITORY_NAME> format, this method clone the repository from
    GitHub in REPOSITORY_PATH which is set in config.py
    :param repository_name:   The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    """
    validation.validate_repository_name(repository_name)
    cd_to_repository = 'cd {};'.format(config.REPOSITORY_PATH)
    user_name = repository_name.split('/')[0].strip()
    repo_name = repository_name.split('/')[1].strip()
    os.system(cd_to_repository + 'GIT_TERMINAL_PROMPT=0 git clone  https://github.com/{} {}___{}'
              .format(repository_name.strip(), user_name, repo_name))


def clone_repositories(repository_list, core_num = multiprocessing.cpu_count()):
    """
    This method received a list name and clone all of the repositories in the list. The list <LIST> is '<LIST>.txt' in
     REPOSITORY_LIST_PATH which is set in config.txt
    :param repository_list:    The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :param core_num: The number of parallel threads. Default is all of the available cores
    """
    validation.validate_core_num(core_num)
    repositories = open(config.REPOSITORY_LIST_PATH + repository_list + '.txt', 'rt').readlines()
    Parallel(n_jobs = core_num)(delayed(clone_repository)(i) for i in repositories)
