
import csv

from config import *
from utility import *


def store_commit_info_between_two_commits(repository_name, commit1, commit2, parent_num):
    commit_list = get_commit_list_between_two_commits(repository_name, commit1, commit2)
    for commit in commit_list:
        commit_date  = get_commit_date(repository_name, commit)
        commit_message = get_commit_message(repository_name, commit)
        branch_name = get_branch_of_commit(repository_name, commit)
        file_changes = get_changed_files_between_two_commits(repository_name, commit1, commit2)
        line_changes = getChangedLineNumBetweenTwoCommits(repository_name, commit1, commit2)

        # Store the merge related commits
        merge_related_commits_data = [commit, commit_date, commit_message, branch_name, parent_num] + \
                                      file_changes + list(line_changes)
        csv_file = open(config.TEMP_CSV_PATH + 'Merge_Related_Commit.csv', 'a')
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
        csv_writer.writerow(merge_related_commits_data)
        csv_file.close()
