
import os
import csv
import time
import random
import logging
from dateutil.relativedelta import relativedelta as rd
from time import gmtime, strftime

from merganser.config import *
from merganser.util import *
from merganser.GitUtil import *
from merganser.merge_replay import *
from merganser.related_commits import *
from merganser.repository_data import *
from merganser.clone_repositories import *


def get_merge_scenario_info(repository_name, merge_technique, repository_only, exec_compile, exec_tests,
                            exec_conflicting_file, exec_conflicting_region, exec_replay_comparison, exec_related_commits,
                            start_date):

    try:

        # clone the repository
        clone_repository(repository_name)

        # Exit if the repository doesn't exist
        if os.path.exists(REPOSITORY_PATH / Path(repository_name.replace('/', '___'))) is False:
            logging.info('Could not clone: {}'.format(repository_name))
            return 1

        t0 = time.time()

        # local variables
        git_utility = GitUtil(repository_name.replace('/', '___'))
        merge_replay = Merge_Replay()

        # extract all merge scenarios after the start_date
        merge_commits = [commit for commit in git_utility.get_merge_commits()
                         if git_utility.get_commit_date(commit).split()[0] > start_date]

        # eliminate the data extracted if there is no enough merges
        if len(merge_commits) < MIN_MERGE_SCENARIO:
            remove_repository(repository_name)
            logging.info('Error - {} has only {} merge scenarios.'.format(repository_name, len(merge_commits)))
            return 1

        # set the maximum number of merges to analyze
        if len(merge_commits) < MAX_MERGE_SCENARIOS:
            merge_commit_to_analyze = merge_commits
        else:
            random.shuffle(merge_commits)
            merge_commit_to_analyze = merge_commits[0:MAX_MERGE_SCENARIOS]

        # repository id
        repository_id, repository_size = get_repository_id(repository_name)
        if repository_id == -1:
            logging.info(f'NO FOUND REPOSITORY: {repository_name}')
            return 1

        # repo size
        if int(repository_size) > MAX_REPO_SIZE_TO_ANALYZE:
            logging.info(f'HUGE REPOSITORY: {repository_name}')
            return 1

        # analyze the merges
        if not repository_only:
            for commit_num, merge_commit in enumerate(merge_commit_to_analyze):

                # aime limitation for running each repository
                if (time.time() - t0) / 86400.0 > MAX_ANALYZING_DAY:
                    logging.info(f'{repository_name} terminated since it couldn\'t finish in {MAX_ANALYZING_DAY}')
                    break

                # extract the SHA-1 of the parents and ancestor
                parents_commit = git_utility.get_parents(merge_commit)
                ancestor_commit = git_utility.get_ancestor(parents_commit)

                # extract the number of parallel changes
                parallel_changed_files_num = git_utility.get_parallel_changed_files_num(ancestor_commit,
                                                                                        parents_commit[0],
                                                                                        parents_commit[1])

                # extracts the date of involved commits
                merge_commit_date = git_utility.get_commit_date(merge_commit)
                ancestor_date = git_utility.get_commit_date(ancestor_commit)
                parent1_date = git_utility.get_commit_date(parents_commit[0])
                parent2_date = git_utility.get_commit_date(parents_commit[1])

                # Detect pull requests
                is_pull_request = git_utility.check_if_pull_request(merge_commit)

                # Extract developers num
                developer_num_parent1 = git_utility.get_develoeprs_num(ancestor_commit, parents_commit[0])
                developer_num_parent2 = git_utility.get_develoeprs_num(ancestor_commit, parents_commit[1])

                # Store the merge scenario data
                merge_scenario_data = [merge_commit, ancestor_commit, parents_commit[0], parents_commit[1],
                                       parallel_changed_files_num,
                                       merge_commit_date, ancestor_date, parent1_date, parent2_date,
                                       developer_num_parent1, developer_num_parent2,
                                       is_pull_request,
                                       repository_id]
                csv_file = open(TEMP_CSV_PATH / Path(f'Merge_Scenario_{repository_name}.csv'), 'a')
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

        #logging.warning('{} error: {}.'.format(e, repository_name))
