
import os
import pandas as pd
from io import StringIO

import config

class Data_Retreival:

    def __init__(self):
        self.code_complexity_query = 'SELECT Merge_Scenario_merge_commit_hash, measure1_diff, measure2_diff, ' \
                                     'measure3_diff, measure4_diff, measure5_diff, measure6_diff, measure7_diff, ' \
                                     'measure8_diff ' \
                                     'FROM Merge_Data.Code_Complexity'
        self.code_violation_query = 'SELECT Code_Violation.Merge_Scenario_merge_commit_hash, ' \
                                    'Code_Violation.parent1_style_violation_num,' \
                                    ' Code_Violation.parent2_style_violation_num ' \
                                    'FROM Merge_Data.Code_Style_Violation Code_Violation '
        self.parallel_changes_query = 'SELECT merge_commit_hash, parallel_changed_file_num ' \
                                      'FROM Merge_Data.Merge_Scenario'
        self.commit_num_query = 'SELECT Merge_Scenario.merge_commit_hash, count(Commits.commit_hash) ' \
                                        'FROM Merge_Data.Merge_Scenario Merge_Scenario JOIN ' \
                                        'Merge_Data.Merge_Related_Commit Commits ' \
                                        'on Merge_Scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash' \
                                        ' WHERE Commits.merge_commit_parent = {} ' \
                                        'GROUP BY Merge_Scenario.merge_commit_hash'
        self.commit_density_two_weeks = 'SELECT Merge_Scenario.merge_commit_hash, count(Commits.commit_hash) FROM ' \
                                       'Merge_Data.Merge_Scenario Merge_Scenario' \
                                       ' JOIN Merge_Data.Merge_Related_Commit Commits ' \
                                       'on Merge_Scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash ' \
                                       'WHERE Commits.merge_commit_parent = {} AND ' \
                                       'TIMESTAMPDIFF(WEEK, Merge_Scenario.merge_commit_date, Commits.date) < 3 ' \
                                       'GROUP BY Merge_Scenario.merge_commit_hash'
        self.file_change_query = 'SELECT Merge_Scenario.merge_commit_hash, SUM(file_added_num), ' \
                                     'SUM(file_removed_num) , SUM(file_renamed_num) , SUM(file_copied_num) , ' \
                                     'SUM(file_modified_num)  FROM Merge_Data.Merge_Scenario Merge_Scenario  ' \
                                     'JOIN Merge_Data.Merge_Related_Commit Commits on Merge_Scenario.merge_commit_hash = ' \
                                     'Commits.Merge_Scenario_merge_commit_hash ' \
                                     'WHERE Commits.merge_commit_parent = {} ' \
                                     'GROUP BY Merge_Scenario.merge_commit_hash'
        self.line_change_query = 'SELECT Merge_Scenario.merge_commit_hash, SUM(line_added_num), SUM(line_removed_num) ' \
                                 'FROM Merge_Data.Merge_Scenario Merge_Scenario ' \
                                 'JOIN Merge_Data.Merge_Related_Commit Commits ' \
                                 'on Merge_Scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash ' \
                                 'WHERE Commits.merge_commit_parent = 2 ' \
                                 'GROUP BY Merge_Scenario.merge_commit_hash'
        self.developer_num_query = 'SELECT merge_commit_hash, developer_num_parent{} ' \
                              'FROM Merge_Data.Merge_Scenario'

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







obj = Data_Retreival()
res = obj.get_developer_num(1)
print(res)
