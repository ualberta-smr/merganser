
import csv

from utility import *
from code_quality import *
from merge_replay import *


def get_merge_scenario_info(repository_name, merge_technique, exec_compile, exec_tests,
                            exec_conflicting_file, exec_conflicting_region):

    merge_commits = get_merge_commits(repository_name)

    for merge_commit in merge_commits:

        # Extract the SHA-1 of the parents and ancestor
        parents_commit = get_parents(repository_name, merge_commit)
        ancestor_commit = get_ancestor(repository_name, parents_commit)

        # Extract the number of parallel changes
        parallel_changed_files_num = get_parallel_changed_files_num(repository_name, ancestor_commit,
                                                                    parents_commit[0], parents_commit[1])
        # Extracts the date of involved commits
        merge_commit_date = get_commit_date(repository_name, merge_commit)
        ancestor_date = get_commit_date(repository_name, ancestor_commit)
        parent1_date = get_commit_date(repository_name, parents_commit[0])
        parent2_date = get_commit_date(repository_name, parents_commit[1])

        # Compile the code
        if exec_compile:
            merge_commit_can_compile = get_commit_quality(repository_name, merge_commit, 'compile')
            ancestor_can_compile = get_commit_quality(repository_name, ancestor_commit, 'compile')
            parent1_can_compile = get_commit_quality(repository_name, parents_commit[0], 'compile')
            parent2_can_compile = get_commit_quality(repository_name, parents_commit[1], 'compile')
        else:
            merge_commit_can_compile = -1
            ancestor_can_compile = -1
            parent1_can_compile = -1
            parent2_can_compile = -1

        # Test the code
        if exec_tests:
            merge_commit_can_pass_test = get_commit_quality(repository_name, merge_commit, 'test')
            ancestor_can_pass_test = get_commit_quality(repository_name, ancestor_commit, 'test')
            parent1_can_pass_test = get_commit_quality(repository_name, parents_commit[0], 'test')
            parent2_can_pass_test = get_commit_quality(repository_name, parents_commit[1], 'test')
        else:
            merge_commit_can_pass_test = -1
            ancestor_can_pass_test = -1
            parent1_can_pass_test = -1
            parent2_can_pass_test = -1

        # Detec pull requests
        is_pull_request = check_if_pull_request(repository_name, merge_commit)

        # Store the merge scenario data
        merge_scenario_data = [merge_commit, ancestor_commit, parents_commit[0], parents_commit[1],
                               parallel_changed_files_num, merge_commit_can_compile, merge_commit_can_pass_test,
                               ancestor_can_compile, ancestor_can_pass_test,
                               parent1_can_compile, parent1_can_pass_test,
                               parent2_can_compile, parent2_can_pass_test,
                               merge_commit_date, ancestor_date, parent1_date, parent2_date, is_pull_request]
        csv_file = open(config.TEMP_CSV_PATH + 'Merge_Scenario.csv', 'a')
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
        csv_writer.writerow(merge_scenario_data)
        csv_file.close()

        # Merge replay
        merge_replay(repository_name, merge_technique, merge_commit, parents_commit, exec_compile, exec_tests,
                     exec_conflicting_file, exec_conflicting_region)