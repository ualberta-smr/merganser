
import os
import numpy as np

import config


def get_commit_quality(repository_name, commit, operation):
    """
    Checkout, compile and test a commit. This method reset all changes at the end.
    :param repository_name:   The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :param commit: The commit that should compile ot test
    :param operation: Can be 'compile' or 'test'
    :return: 1 if the code can compile or pass the tests, 0 otherwise
    """
    cd_to_repository = 'cd {};'.format(config.REPOSITORY_PATH + repository_name)
    if commit != -1:
        os.system(cd_to_repository + 'git checkout {}'.format(commit))
    repository_dir = config.REPOSITORY_PATH + repository_name
    if os.path.isfile(repository_dir + '/pom.xml'): # Maven
        if operation == 'compile':
            command = 'compile test-compile'
        elif operation == 'test':
            command = 'test'
        else:
            raise ValueError('Operator {} is not defined'.format(operation))
        maven_output = os.popen(cd_to_repository + 'mvn ' + command).read()
        os.system(cd_to_repository + 'git reset --hard'.format(commit))
        if maven_output.find('BUILD SUCCESS') > -1 or maven_output.find('BUILD FAILURE') == -1:
            return 1
        elif maven_output.find('BUILD SUCCESS') == -1 or maven_output.find('BUILD FAILURE') > -1:
            return 0
        else:
            raise ValueError('Cannot determine the compile/test status of {}'.format(repository_name))
    else:
        raise ValueError('This tool does not support {} build system'.format(repository_name))


def get_code_violation_num(repository_name, commit):
    repository_dir = config.REPOSITORY_PATH + repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(repository_dir)
    os.system(cd_to_repository + 'git checkout --quiet {}'.format(commit))
    return os.popen('java -jar ../tools/StyleChecker/checkstyle-8.11-all.jar -c '
                    '../tools/StyleChecker/google_checks.xml ' + repository_dir).read().count('[WARN]')


def get_code_complexity_of_dir(repository_dir):
    cd_to_repository = 'cd {};'.format(repository_dir)
    commits = os.popen(cd_to_repository + 'lizard -C 1000').readlines()[-1].split()
    return commits


def get_code_complexity_diff(repository_name, commit1, commit2):
    repository_dir = config.REPOSITORY_PATH + repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(repository_dir)
    os.system(cd_to_repository + 'git checkout --quiet {}'.format(commit1))
    complexity1 = get_code_complexity_of_dir(repository_dir)
    os.system(cd_to_repository + 'git checkout --quiet {}'.format(commit2))
    complexity2 = get_code_complexity_of_dir(repository_dir)
    return np.asarray(complexity1, dtype=float) - np.asarray(complexity2, dtype=float)