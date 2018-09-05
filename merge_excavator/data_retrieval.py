
import os
import pandas as pd
import numpy as np
from io import StringIO
from functools import reduce

import config

class Data_Retreival:

    def __init__(self):
        self.code_complexity_query = 'SELECT Merge_Scenario_merge_commit_hash, measure1_diff, measure2_diff, ' \
                                     'measure3_diff, measure4_diff, measure5_diff, measure6_diff, measure7_diff, ' \
                                     'measure8_diff ' \
                                     'FROM Merge_Data.Code_Complexity'
        self.code_violation_query = 'SELECT Code_Violation.Merge_Scenario_merge_commit_hash, ' \
                                    'Code_Violation.parent1_style_violation_num - ' \
                                    ' Code_Violation.parent2_style_violation_num ' \
                                    'FROM Merge_Data.Code_Style_Violation Code_Violation '
        self.parallel_changes_query = 'SELECT merge_commit_hash, parallel_changed_file_num ' \
                                      'FROM Merge_Data.Merge_Scenario'
        self.commit_num_query = 'SELECT Merge_Scenario.merge_commit_hash, count(Commits.commit_hash) ' \
                                        'FROM Merge_Data.Merge_Scenario Merge_Scenario LEFT JOIN ' \
                                        'Merge_Data.Merge_Related_Commit Commits ' \
                                        'on Merge_Scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash' \
                                        ' AND Commits.merge_commit_parent = {} ' \
                                        'GROUP BY Merge_Scenario.merge_commit_hash'
        self.commit_density_two_weeks = 'SELECT Merge_Scenario.merge_commit_hash, count(Commits.commit_hash) FROM ' \
                                       'Merge_Data.Merge_Scenario Merge_Scenario' \
                                       ' LEFT JOIN Merge_Data.Merge_Related_Commit Commits ' \
                                       'on Merge_Scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash ' \
                                       'AND Commits.merge_commit_parent = {} AND ' \
                                       'TIMESTAMPDIFF(WEEK, Merge_Scenario.merge_commit_date, Commits.date) < 3 ' \
                                       'GROUP BY Merge_Scenario.merge_commit_hash'
        self.file_change_query = 'SELECT Merge_Scenario.merge_commit_hash, COALESCE(SUM(file_added_num), 0), ' \
                                 'COALESCE(SUM(file_removed_num), 0), COALESCE(SUM(file_renamed_num), 0), ' \
                                 'COALESCE(SUM(file_copied_num), 0), COALESCE(SUM(file_modified_num), 0) ' \
                                 ' FROM Merge_Data.Merge_Scenario Merge_Scenario  ' \
                                     'LEFT JOIN Merge_Data.Merge_Related_Commit Commits ' \
                                 'on Merge_Scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash' \
                                        ' AND Commits.merge_commit_parent = {} ' \
                                     'GROUP BY Merge_Scenario.merge_commit_hash'
        self.line_change_query = 'SELECT Merge_Scenario.merge_commit_hash, COALESCE(SUM(line_added_num), 0), COALESCE(SUM(line_removed_num), 0) ' \
                                 'FROM Merge_Data.Merge_Scenario Merge_Scenario ' \
                                 'LEFT JOIN Merge_Data.Merge_Related_Commit Commits ' \
                                 'on Merge_Scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash ' \
                                 'AND Commits.merge_commit_parent = {} ' \
                                 'GROUP BY Merge_Scenario.merge_commit_hash'
        self.developer_num_query = 'SELECT merge_commit_hash, parent{}_developer_num ' \
                              'FROM Merge_Data.Merge_Scenario'
        self.commit_message_quey = 'SELECT GROUP_CONCAT(Commits.message SEPARATOR \' ||| \') ' \
                                   'FROM Merge_Data.Merge_Scenario Merge_Scenario ' \
                                   'LEFT JOIN Merge_Data.Merge_Related_Commit Commits ' \
                                   'on Merge_Scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash ' \
                                   'AND Commits.merge_commit_parent = {} ' \
                                   'GROUP BY Merge_Scenario.merge_commit_hash'
        self.branch_duration = 'SELECT Merge_Scenario.merge_commit_hash, TIMESTAMPDIFF(HOUR, ' \
                               'Merge_Scenario.ancestor_date, Merge_Scenario.parent{}_date) ' \
                               'FROM Merge_Data.Merge_Scenario Merge_Scenario'

    def get_query_result(self, query):
        return os.popen('mysql -u {} -e "{}"'.format(config.DB_USER_NAME, query)).read()

    def get_data_frame_of_query_result(self, query_result):
        return pd.read_csv(StringIO(query_result), delimiter='\t')

    def get_complexity(self):
        return self.get_data_frame_of_query_result(self.get_query_result(self.code_complexity_query))

    def get_code_violation(self):
        return self.get_data_frame_of_query_result(self.get_query_result(self.code_violation_query))

    def get_parallel_changes(self):
        return self.get_data_frame_of_query_result(self.get_query_result(self.parallel_changes_query))

    def get_commit_num(self, parent): # TODO: The number of data in two branches is not the same.
        return self.get_data_frame_of_query_result(self.get_query_result(self.commit_num_query.format(parent)))

    def get_commit_density(self, parent):
        return self.get_data_frame_of_query_result(self.get_query_result(self.commit_density_two_weeks.format(parent)))

    def get_file_changes(self, parent):
        return self.get_data_frame_of_query_result(self.get_query_result(self.file_change_query.format(parent)))

    def get_line_changes(self, parent):
        return self.get_data_frame_of_query_result(self.get_query_result(self.line_change_query.format(parent)))

    def get_developer_num(self, parent):
        return self.get_data_frame_of_query_result(self.get_query_result(self.developer_num_query.format(parent)))

    def get_commit_messege_characteristics(self, parent):
        commit_messages = self.get_query_result(self.commit_message_quey.format(parent))
        commit_messages_list = commit_messages.split('\n')[1:-1]
        keywords = sorted(['fix', 'bug', 'feature', 'improve', 'document', 'refactor', 'update', 'add', 'remove', 'use',
                        'delete', 'change'])
        keywords_frequency = []
        commit_messege_length_stats = []
        for merge_scenrio_commits in commit_messages_list:
            keywords_frequency.append([merge_scenrio_commits.lower().count(word) for word in keywords])
            if merge_scenrio_commits != 'NULL':
                seperated_commit_message = merge_scenrio_commits.replace(' ||| ', '\n').split('\n')
                commit_messege_length = [len(msg.split()) for msg in seperated_commit_message]
                commit_messege_length_stats.append([np.min(commit_messege_length), np.mean(commit_messege_length),
                                               np.median(commit_messege_length), np.max(commit_messege_length)])
            else:
                commit_messege_length_stats.append([0.0, 0.0, 0.0, 0.0])
        return pd.DataFrame(keywords_frequency), pd.DataFrame(commit_messege_length_stats)

    def get_branch_duration(self, parent):
        return self.get_data_frame_of_query_result(self.get_query_result(self.branch_duration.format(parent)))

    def get_merge_scenario_data(self):
        keywords_frequency1, commit_messege_length_stats1 = self.get_commit_messege_characteristics(1)
        keywords_frequency2, commit_messege_length_stats2 = self.get_commit_messege_characteristics(2)
        code_features = pd.merge(self.get_complexity(), self.get_code_violation(), on='Merge_Scenario_merge_commit_hash')
        git_features_scenario = self.get_parallel_changes()
        git_features_per_branch_diff_dfs = [self.get_commit_num(1).drop('merge_commit_hash', axis = 1) - self.get_commit_num(2).drop('merge_commit_hash', axis = 1),
                                            self.get_commit_density(1).drop('merge_commit_hash', axis=1) - self.get_commit_density(2).drop('merge_commit_hash', axis=1),
                                            self.get_file_changes(1).drop('merge_commit_hash', axis=1) - self.get_file_changes(2).drop('merge_commit_hash', axis=1),
                                            self.get_line_changes(1).drop('merge_commit_hash', axis=1) - self.get_line_changes(2).drop('merge_commit_hash', axis=1),
                                            pd.DataFrame(self.get_developer_num(1).drop('merge_commit_hash',axis=1).values - self.get_developer_num(2).drop('merge_commit_hash', axis=1).values),
                                            keywords_frequency1 - keywords_frequency2,
                                            commit_messege_length_stats1 - commit_messege_length_stats2,
                                            pd.DataFrame(self.get_branch_duration(1).drop('merge_commit_hash',axis=1).values - self.get_branch_duration(2).drop('merge_commit_hash', axis=1).values)]
        git_features_per_branch_diff = pd.concat(git_features_per_branch_diff_dfs, axis=1)
        return pd.concat([code_features, git_features_scenario, git_features_per_branch_diff], axis=1)

obj = Data_Retreival()
res = obj.get_merge_scenario_data()
print(res)
