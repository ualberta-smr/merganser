
# -*- coding: utf-8 -*-

import csv
import numpy as np

from config import *
from GitUtil import *

def store_commit_info_between_two_commits(git_utility, commit1, commit2, parent_num, merge_commit, repository_id):
    commit_list = git_utility.get_commit_list_between_two_commits(commit1, commit2) # The first commit (index zero)
    for commit in commit_list:
        commit = commit.strip()
        if commit == merge_commit or commit == commit1:
            continue
        commit_date  = git_utility.get_commit_date(commit)
        commit_message = git_utility.get_commit_message(commit)
        branch_name = git_utility.get_branch_of_commit(commit)
        file_changes = git_utility.get_changed_files_in_commit(commit)
        line_changes = git_utility.get_changed_lines_in_commit(commit)

        branch_name = 'TEMP'

        # Store the merge related commits
        merge_related_commits_data = [commit.strip(), commit_date, commit_message, branch_name, parent_num] + \
                                     file_changes + list(line_changes) + [merge_commit, repository_id]
        csv_file = open(config.TEMP_CSV_PATH + 'Merge_Related_Commit_{}.csv'.format(git_utility.repository_name), 'a')
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
        csv_writer.writerow(merge_related_commits_data)
        csv_file.close()
