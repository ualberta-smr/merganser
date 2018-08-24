
import csv

from config import *
from GitUtil import *


def store_commit_info_between_two_commits(git_utility, commit1, commit2, parent_num):
    commit_list = git_utility.get_commit_list_between_two_commits(commit1, commit2)
    for commit in commit_list:
        commit_date  = git_utility.get_commit_date(commit)
        commit_message = git_utility.get_commit_message(commit)
        branch_name = git_utility.get_branch_of_commit(commit)
        file_changes = git_utility.get_changed_files_between_two_commits(commit1, commit2)
        line_changes = git_utility.getChangedLineNumBetweenTwoCommits(commit1, commit2)

        # Store the merge related commits
        merge_related_commits_data = [commit, commit_date, commit_message, branch_name, parent_num] + \
                                      file_changes + list(line_changes)
        csv_file = open(config.TEMP_CSV_PATH + 'Merge_Related_Commit.csv', 'a')
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
        csv_writer.writerow(merge_related_commits_data)
        csv_file.close()
