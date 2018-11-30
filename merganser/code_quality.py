
import os
import numpy as np

import config


def check_build_status(repository_name, commit, operation):
    """
    Checkout, compile and test a commit. This method reset all changes at the end.
    :param repository_name:   The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :param commit: The commit that should compile ot test
    :param operation: Can be 'compile' or 'test'
    :return: 1 if the code can compile or pass the tests, 0 otherwise
    """
    cd_to_repository = 'cd {};'.format(config.REPOSITORY_PATH + repository_name)
    if commit != -1: # Valid commit SHA-1
        os.system(cd_to_repository + 'git checkout {}'.format(commit))
    if os.path.isfile('{}.pom.xml'.format(config.REPOSITORY_PATH + repository_name)): # Maven
        if operation == 'compile':
            command = 'compile test-compile'
        elif operation == 'test':
            command = 'test'
        else:
            raise ValueError('Operator {} is not defined for {}'.format(operation, repository_name))
        maven_output = os.popen(cd_to_repository + 'mvn ' + command).read()
        os.system(cd_to_repository + 'git reset --hard'.format(commit))
        if maven_output.find('BUILD SUCCESS') > -1 or maven_output.find('BUILD FAILURE') == -1:
            return 1
        elif maven_output.find('BUILD SUCCESS') == -1 or maven_output.find('BUILD FAILURE') > -1:
            return 0
        else:
            raise ValueError('Cannot determine the compile/test status of {}'.format(repository_name))
    else:
        raise ValueError('This tool does not support {}\'s build system'.format(repository_name))


def get_code_violation_num(repository_name, commit):
    """
    Returns the number of code violations by StyleChecker using Google rules
    :param repository_name:   The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :param commit: The commit to checkout
    :return: The number of code violations
    """
    repository_dir = config.REPOSITORY_PATH + repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(repository_dir)
    os.system(cd_to_repository + 'git checkout --quiet {}'.format(commit))
    return os.popen('java -jar ../tools/StyleChecker/checkstyle-8.11-all.jar -c '
                    '../tools/StyleChecker/google_checks.xml ' + repository_dir).read().count('[WARN]')


def get_code_complexity_of_dir(repository_dir):
    """
    Returns the code complexity of the code in a directory using Lizard tool.
    :param repository_dir:   The directory of the code to analyze
    :return: A vector with size of eight as the code complexity
    """
    cd_to_repository = 'cd {};'.format(repository_dir)
    commits = os.popen(cd_to_repository + 'lizard -C 1000').readlines()[-1].split()
    return commits


def get_code_complexity_diff(repository_name, commit_1, commit_2):
    """
    Returns the code complexity difference between two commits using norm-1 operator.
    :param repository_name:   The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :param commit_1: The first commit commit to analyze
    :param commit_2: The second commit commit to analyze

    :return: A vector with size of eight as the code complexity
    """
    repository_dir = config.REPOSITORY_PATH + repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(repository_dir)
    os.system(cd_to_repository + 'git checkout --quiet {}'.format(commit_1))
    complexity1 = get_code_complexity_of_dir(repository_dir)
    os.system(cd_to_repository + 'git checkout --quiet {}'.format(commit_2))
    complexity2 = get_code_complexity_of_dir(repository_dir)
    return np.asarray(complexity1, dtype=float) - np.asarray(complexity2, dtype=float)
