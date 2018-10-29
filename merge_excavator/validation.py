
import multiprocessing


def validate_repository_name(repository_name):
    """
    Check if repository_name follows the right format.
    :param repository_name: The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    """
    if repository_name.count('___') + repository_name.count('/') != 1:
        raise ValueError('The repository name should be in <USER_NAME>/<REPOSITORY_NAME> format. {} is invalid.'.
                         format(repository_name))


def validate_core_num(core_num):
    """
    Check if the code_num follows the right format. This variable should be an integer between one and the number of
    cores on the machine.
    :param core_num: The maximum number of cores to use in processing
    """
    if core_num < 1:
        raise ValueError('The number of cores should be greater than zero. {} is not a valid value.'.format(core_num))
    elif core_num > multiprocessing.cpu_count():
        raise ValueError('The number of cores cannot be greater that the number of system cores ({}), {} is invalid'
                         .format(multiprocessing.cpu_count(), core_num))
