
import multiprocessing


def validation_repository_name(repository_name):
    """
    Check if repository_name follows the right format.
    :param repository_name: The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
    :return:
    """
    if repository_name.count('___') + repository_name.count('/') != 1:
        raise ValueError('The repository name should be in <USER_NAME>/<REPOSITORY_NAME> format. {} does not'
                         ' follow this.'.format(repository_name))


def validation_core_num(core_num):
    """
    Check if the code_num follows the regiht format. This variable should be an integer beteen one and the number of
    cores on the machine.
    :param core_num: The maximum number of cores to use in processing
    :return:
    """
    if core_num < 1:
        raise ValueError('The number of cores should be greater than zero. {} is not a valid value.'.format(core_num))
    elif core_num > multiprocessing.cpu_count():
        raise ValueError('The number of cores cannot be greater that the number of system cores ({}), {} is not valid'
                         .format(multiprocessing.cpu_count(), core_num))
