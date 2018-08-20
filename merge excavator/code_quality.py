
import os

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
