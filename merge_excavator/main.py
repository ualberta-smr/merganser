
from joblib import Parallel, delayed
import multiprocessing
import argparse

from clone_repositories import *
from merge_scenario_data import *


if __name__ == '__main__':

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
    parser.add_argument('-pr', '--pull-request', help='If set, pull requests are detected', action='store_true',
                        required=False)
    parser.add_argument('-rc', '--replay-compare', help='If set, the replays and merge commits are compared',
                        action='store_true', required=False)
    parser.add_argument('-cd', '--commit-details',
                        help='If set, the information of all commits that are involved in merge scenarios are extracted',
                        action='store_true', required=False)
    parser.add_argument('-sv', '--style-violation', help='If set, the code style violations are extracted',
                        action='store_true', required=False)
    parser.add_argument('-cc', '--code-complexity', help='If set, the code complexity are extracted', action='store_true',
                        required=False)
    parser.add_argument('-cores', '--cpu-cores', help='The number of threads', required = False)
    args = vars(parser.parse_args())

    # CPU cores
    if args['cpu_cores'] is None:
        core_num = multiprocessing.cpu_count()
    else:
        core_num = args['cpu_cores']

    # Clone the repositories
    clone_repositories(args['repository_list'], core_num)

    repository_urls = open(config.REPOSITORY_LIST_PATH + args['repository_list'] + '.txt', 'rt').readlines()
    user_name = [i.split('/')[0].strip() for i in repository_urls]
    repo_name = [i.split('/')[1].strip() for i in repository_urls]


    # Parallel execution
    Parallel(n_jobs = core_num)(delayed(get_merge_scenario_info)('{}___{}'.
                                                             format(user_name[i].strip(), repo_name[i].strip()), 'git',
                                                             args['compile'], args['test'], args['conflicting_file'],
                                                             args['conflicting_region'], args['pull_request'],
                                                             args['replay_compare'], args['commit_details'],
                                                             args['style_violation'], args['code_complexity'])
                                 for i in range(len(repository_urls)))
