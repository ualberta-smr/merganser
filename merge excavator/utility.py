
import os

import config

def get_merge_commits(repository_name):
    """
    Returns the list of all merge SHA-1
    :param
    repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :return:
    List of merge SHA-1
    """
    repository_dir = repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(config.REPOSITORY_PATH + repository_dir)
    return os.popen(cd_to_repository + 'git log --pretty=%H --merges').read().split()


def get_parents(repository_name, commit):
    """
    Returns the parents in a merge scenario
    :param
    repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    commit: The SHA-1 of the merge commit
    :return:
    Two parents of the merge commit
    """
    repository_dir = repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(config.REPOSITORY_PATH + repository_dir)
    return os.popen(cd_to_repository + 'git log --pretty=%P -n 1 {}'.format(commit)).read().split()


def get_ancestor(repository_name, parents):
    """
    Returns the ancestor of two parents in a merge scenario
    :param
    repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    parents: The list of SHA-1 od parents
    :return:
    The ancestor of two parents
    """
    repository_dir = repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(config.REPOSITORY_PATH + repository_dir)
    return os.popen(cd_to_repository + 'git merge-base {} {}'.format(parents[0], parents[1])).read().rstrip()

def get_commit_date(repository_name, commit):
    """
    Returns the local date of a commit
    :param repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    commit: The SHA-1 of the commit
    :return:
    The date of the input commit
    """
    repository_dir = repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(config.REPOSITORY_PATH + repository_dir)
    return ' '.join(os.popen(cd_to_repository + 'git show -s --format=%ci {}'.format(commit)).read().rstrip().split()[0:2])


def get_parallel_changed_files_num(repository_name, ancestor, parent1, parent2):
    """
    Returns the number of files that are changed in both parents in parallel
    :param repository_name: The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :param ancestor: The ancestor SHA-1
    :param parent1: The parent 1 SHA-1
    :param parent2: The parent 2 SHA-1
    :return: The number of files that are changed in both parents in parallel
    """
    repository_dir = repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(config.REPOSITORY_PATH + repository_dir)
    changes_ancestor_parent1 = set([item.strip() for item in os.popen(cd_to_repository + 'git diff --name-only {} {}'.format(ancestor, parent1)).readlines()])
    changes_ancestor_parent2 = set([item.strip() for item in os.popen(cd_to_repository + 'git diff --name-only {} {}'.format(ancestor, parent2)).readlines()])
    return len(changes_ancestor_parent1.intersection(changes_ancestor_parent2))


def get_commit_message(repository_name, commit):
    """
    Extracts the commit message of the given SHA-1
    :param repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :param commit: The SHA-1 of the commit
    :return: The commit message
    """
    repository_dir = repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(config.REPOSITORY_PATH + repository_dir)
    return os.popen(cd_to_repository + 'git log --pretty=format:"%s" {}'.format(commit)).read().rstrip()


def check_if_pull_request(repository_name, commit):
    """
    Determine whther the commit was a pull request
    :param repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :param commit: The SHA-1 of the commit
    :return: 1 if the commit was a pull request, 0 otherwise
    """
    if 'Merge pull request' in get_commit_message(repository_name, commit):
        return 1
    else:
        return 0
