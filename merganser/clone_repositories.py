
import os
from joblib import Parallel, delayed

from merganser.config import *
from merganser.validation import *


def clone_repository(repository_name: str):
    """
    Receiving the repository's in the <USER_NAME>/<REPOSITORY_NAME> format, this method clone the repository from
    GitHub in REPOSITORY_PATH which is set in config.py
    :param repository_name: The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    """
    validate_repository_name(repository_name)
    repository_name = repository_name.strip()
    user_name = repository_name.split('/')[0]
    repo_name = repository_name.split('/')[1]
    os.system(f'cd {REPOSITORY_PATH};'
              f'GIT_TERMINAL_PROMPT=0 git clone  https://github.com/{repository_name} {user_name}___{repo_name}')


def clone_repositories(repository_list: str, core_num: int = multiprocessing.cpu_count()):
    """
    This method received a list name and clone all of the repositories in the list. The list <LIST> is '<LIST>.txt' in
     REPOSITORY_LIST_PATH which is set in config.txt
    :param repository_list: The list of the repositories in <USER_NAME>/<REPOSITORY_NAME> format
    :param core_num: The number of parallel threads. Default is half of the available cores
    """
    validate_core_num(core_num)
    Parallel(n_jobs=core_num)(delayed(clone_repository)(i) for i in repository_list)
