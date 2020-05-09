from pathlib import Path
from joblib import Parallel, delayed
import argparse
import logging
from time import gmtime, strftime

from merganser.clone_repositories import *
from merganser.merge_scenario_data import *
from merganser.config import *
from merganser.util import *
from merganser.validation import *


if __name__ == '__main__':
    """
    This is the starting point of the execution of this tool. We strongly suggest to read the README.md first to set the
     arguments correctly.
    """

    # Create directories
    create_dir()

    # Arguments
    parser = argparse.ArgumentParser(description='The main script for analyzing merge scenarios')
    parser.add_argument('-r', '--repository-list', help='The list of GitHub repositories', required=True)
    parser.add_argument('-c', '--compile',
                        help='If set, the merged code (if successfully merged using the given tool) will be compiled'
                             ' afterwards', action='store_true', required=False)
    parser.add_argument('-t', '--test', help='If set, the repository\'s test suite will be run after a successful merge',
                        action='store_true', required=False)
    parser.add_argument('-cf', '--conflicting-file', help='If set, the information of conflicting files is stored',
                        action='store_true', required=False)
    parser.add_argument('-cr', '--conflicting-region', help='If set, the information of conflicting regions is stored',
                        action='store_true', required=False)
    parser.add_argument('-cd', '--commit-details',
                        help='If set, the information of all commits that are involved in merge scenarios are extracted',
                        action='store_true', required=False)
    parser.add_argument('-cores', '--cpu-cores', help='The number of threads', required=False)
    parser.add_argument('-sd', '--start-date', help='The the date the merge scenarios should be analyzed after that',
                        required=False)
    parser.add_argument('-ro', '--repository-only', help='If set, only the Repository data is extracted', action='store_true',
                        required=False)
    args = vars(parser.parse_args())

    # CPU cores
    if args['cpu_cores'] is None:
        core_num = MAX_CPU_CORES
    else:
        core_num = args['cpu_cores']
    validate_core_num(core_num)

    # Start date
    if args['start_date'] is None:
        start_date = '1900-01-01'
    else:
        start_date = args['start_date']

    # Temp variables
    repository_urls = open(REPOSITORY_LIST_PATH / Path(f'{args["repository_list"]}.txt'), 'rt').readlines()
    user_name = [i.split('/')[0].strip() for i in repository_urls]
    repo_name = [i.split('/')[1].strip() for i in repository_urls]

    # Parallel execution
    Parallel(n_jobs = core_num)(delayed(get_merge_scenario_info)('{}___{}'.
                                                             format(user_name[i].strip(), repo_name[i].strip()), 'git',
                                                             args['repository_only'], args['compile'], args['test'],
                                                             args['conflicting_file'],
                                                             args['conflicting_region'],
                                                             args['replay_compare'], args['commit_details'],
                                                             start_date)
                                 for i in range(len(repository_urls)))

    logging.info('The executing is finish')
