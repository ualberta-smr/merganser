
import os
import csv
import time
import random
import logging
from dateutil.relativedelta import relativedelta as rd
from time import gmtime, strftime

import config
from util import *
from GitUtil import *
from code_quality import *
from merge_replay import *
from related_commits import *
from repository_data import *
from clone_repositories import *


def get_merge_scenario_info(repository_name, merge_technique, repository_only, exec_compile, exec_tests,
                            exec_conflicting_file, exec_conflicting_region, exec_replay_comparison, exec_related_commits,
                            exec_code_style_violation, exec_complexity, start_date='1900-01-01'):
    # Logging
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s in %(threadName)s - %(asctime)s by %(name)-12s :  %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S',
                        filename='{}{}_{}.log'.format(config.LOG_PATH, repository_name,
                                                      strftime('%Y-%m-%d_%H:%M:%S', gmtime())),
                        filemode='w')

    try:
        logging.info('START: {}'.format(repository_name))  # TODO: Temp

        # Clone the repository
        clone_repository(repository_name.replace('___', '/'))

        # Exit if the repository doesn't exist
        if os.path.exists(os.getcwd() + '/' + config.REPOSITORY_PATH + repository_name) is False:
            return 1

        t0 = time.time()

        # Local variables
        git_utility = GitUtil(repository_name)
        merge_replay = Merge_Replay()

        # Extract all merge scenarios after the start_date
        merge_commits = [commit for commit in git_utility.get_merge_commits() if git_utility.get_commit_date(commit).split()[0] > start_date]
        if len(merge_commits) < config.MAX_MERGE_SCENARIOS:
            merge_commit_to_analyze = merge_commits
        else:
            random.shuffle(merge_commits)
            merge_commit_to_analyze = merge_commits[0:config.MAX_MERGE_SCENARIOS]

        # Repository id
        repository_id, repository_size = get_repository_id(repository_name)
        if repository_id == -1:
            logging.info('NOT FOUND REPOSITORY: {}'.format(repository_name))  # TODO: Temp
            return 1
        if int(repository_size) > config.MAX_REPO_SIZE_TO_ANALYZE:
            logging.info('HUGE REPOSITORY: {}'.format(repository_name))  # TODO: Temp
            open(config.REPOSITORY_LIST_PATH + '__HUGE.txt', 'a').write(repository_name)
            return 1

        # Analyze the merges
        if not repository_only:
            for commit_num, merge_commit in enumerate(merge_commit_to_analyze):

                # logging.info('[STEP]: Analyzing {} / {} -  {}'.format(commit_num, len(merge_commit_to_analyze), repository_name))

                # Time limitation for running each repository
                if (time.time() - t0) / 86400.0 > config.MAX_ANALYZING_DAY:
                    logging.info('{} terminated since it couldn\'t finish in {}'.format(repository_name,
                                                                                        config.MAX_ANALYZING_DAY))
                    return 1

                # Extract the SHA-1 of the parents and ancestor
                parents_commit = git_utility.get_parents(merge_commit)
                ancestor_commit = git_utility.get_ancestor(parents_commit)

                # Extract the number of parallel changes
                parallel_changed_files_num = git_utility.get_parallel_changed_files_num(ancestor_commit,
                                                                            parents_commit[0], parents_commit[1])
                # Extracts the date of involved commits
                merge_commit_date = git_utility.get_commit_date(merge_commit)
                ancestor_date = git_utility.get_commit_date(ancestor_commit)
                parent1_date = git_utility.get_commit_date(parents_commit[0])
                parent2_date = git_utility.get_commit_date(parents_commit[1])

                # Compile the code
                if exec_compile:
                    merge_commit_can_compile = check_build_status(repository_name, merge_commit, 'compile')
                    ancestor_can_compile = check_build_status(repository_name, ancestor_commit, 'compile')
                    parent1_can_compile = check_build_status(repository_name, parents_commit[0], 'compile')
                    parent2_can_compile = check_build_status(repository_name, parents_commit[1], 'compile')
                else:
                    merge_commit_can_compile = -1
                    ancestor_can_compile = -1
                    parent1_can_compile = -1
                    parent2_can_compile = -1

                # Test the code
                if exec_tests:
                    merge_commit_can_pass_test = check_build_status(repository_name, merge_commit, 'test')
                    ancestor_can_pass_test = check_build_status(repository_name, ancestor_commit, 'test')
                    parent1_can_pass_test = check_build_status(repository_name, parents_commit[0], 'test')
                    parent2_can_pass_test = check_build_status(repository_name, parents_commit[1], 'test')
                else:
                    merge_commit_can_pass_test = -1
                    ancestor_can_pass_test = -1
                    parent1_can_pass_test = -1
                    parent2_can_pass_test = -1

                # Detect pull requests
                is_pull_request = git_utility.check_if_pull_request(merge_commit)

                # Extract developers num
                developer_num_parent1 = git_utility.get_develoeprs_num(ancestor_commit, parents_commit[0])
                developer_num_parent2 = git_utility.get_develoeprs_num(ancestor_commit, parents_commit[1])

                # Store the merge scenario data
                merge_scenario_data = [merge_commit, ancestor_commit, parents_commit[0], parents_commit[1],
                                       parallel_changed_files_num, merge_commit_can_compile, merge_commit_can_pass_test,
                                       ancestor_can_compile, ancestor_can_pass_test,
                                       parent1_can_compile, parent1_can_pass_test,
                                       parent2_can_compile, parent2_can_pass_test,
                                       merge_commit_date, ancestor_date, parent1_date, parent2_date,
                                       developer_num_parent1, developer_num_parent2,
                                       is_pull_request,
                                       repository_id]
                csv_file = open(config.TEMP_CSV_PATH + 'Merge_Scenario_{}.csv'.format(repository_name), 'a')
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
                csv_writer.writerow(merge_scenario_data)
                csv_file.close()

                # Merge replay
                merge_replay.merge_replay(repository_name, merge_technique, merge_commit, parents_commit, exec_compile, exec_tests,
                             exec_conflicting_file, exec_conflicting_region, exec_replay_comparison, repository_id)

                # Store the related commits information
                if exec_related_commits:
                    for index, parent in enumerate(parents_commit):
                        if parent == ancestor_commit or parent == merge_commit:
                            continue
                        store_commit_info_between_two_commits(git_utility, ancestor_commit, parent, index + 1,
                                                              merge_commit, repository_id)

                # Store code style violation
                if exec_code_style_violation:
                    merge_commit_style_violations = get_code_violation_num(repository_name, merge_commit)
                    ancestor_style_violations = get_code_violation_num(repository_name, ancestor_commit)
                    parent1_style_violations = get_code_violation_num(repository_name, parents_commit[0])
                    parent2_style_violations = get_code_violation_num(repository_name, parents_commit[1])
                    code_style_violation_data = [merge_commit_style_violations, ancestor_style_violations,
                                                 parent1_style_violations, parent2_style_violations,
                                                 merge_commit, repository_id]
                    csv_file = open(config.TEMP_CSV_PATH + 'Code_Style_Violation_{}.csv'.format(repository_name), 'a')
                    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
                    csv_writer.writerow(code_style_violation_data)
                    csv_file.close()

                # Store code complexity
                if exec_complexity:
                    code_complexity_data = get_code_complexity_diff(repository_name, parents_commit[0], parents_commit[1])\
                                               .tolist()\
                                           +[merge_commit, repository_id]
                    csv_file = open(config.TEMP_CSV_PATH + 'Code_Complexity_{}.csv'.format(repository_name), 'a')
                    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
                    csv_writer.writerow(code_complexity_data)
                    csv_file.close()

        # Repository Data
        is_done = 1
        store_repository_info(repository_name, len(merge_commits), is_done)

        # Remove the temporary repository directory
        remove_repository(repository_name)

        # Logging
        execution_time = time.time() - t0
        fmt = '{0.days} days {0.hours} hours {0.minutes} minutes {0.seconds} seconds'
        logging.info('{} finishes in {}'.format(repository_name, fmt.format(rd(seconds = execution_time))))

    except Exception as e:

        # Remove the temporary repository directory
        remove_repository(repository_name)

        logging.warning('{} error: {}.'.format(e, repository_name))
