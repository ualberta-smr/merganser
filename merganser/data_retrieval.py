
import os
import pandas as pd
import numpy as np
from io import StringIO
import matplotlib.pyplot as plt

from joblib import Parallel, delayed
import multiprocessing

import config
import logging

import pandas as pd
import pymysql
from sqlalchemy import create_engine


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
        self.is_conflict_query = 'SELECT Merge_Replay.Merge_Scenario_merge_commit_hash, Merge_Replay.is_conflict ' \
                           'FROM Merge_Data.Merge_Replay Merge_Replay'
        self.conflict_rate_query = """SELECT scenarios.name AS 'Repository Name'
                                    , scenarios.scenarios AS '# Merge Scenarios', 
                                    conflicts.conflicts AS '# Merge Scenarios with Conflicts', 
                                    100 * conflicts.conflicts/scenarios.scenarios 'Conflict Rate (%)'
                                    FROM
                                    (SELECT Repository.name, 
                                    COUNT(Merge_Replay.Merge_Scenario_merge_commit_hash) AS 'scenarios'
                                    FROM  Merge_Data.Repository  
                                    JOIN  Merge_Data.Merge_Replay 
                                    ON id = Merge_Scenario_Repository_id
                                    GROUP BY name
                                    ORDER BY name) scenarios
                                    INNER JOIN
                                    (SELECT name, COUNT(Merge_Replay.Merge_Scenario_merge_commit_hash)  AS 'conflicts'
                                    FROM  Merge_Data.Repository
                                    JOIN  Merge_Data.Merge_Replay
                                    ON id = Merge_Scenario_Repository_id
                                    WHERE is_conflict = 1
                                    GROUP BY name
                                    ORDER BY name) conflicts 
                                    ON scenarios. name = conflicts.name"""
        self.repository_stat = """(SELECT MIN(star_num) as Min, AVG(star_num) as AVG,MAX(star_num) as Max
                                FROM Merge_Data.Repository)
                                UNION ALL
                                (SELECT MIN(watch_num), AVG(watch_num),MAX(watch_num)
                                FROM Merge_Data.Repository)
                                UNION ALL
                                (SELECT MIN(fork_num), AVG(fork_num),MAX(fork_num)
                                FROM Merge_Data.Repository)
                                UNION ALL
                                (SELECT MIN(issue_num), AVG(issue_num),MAX(issue_num)
                                FROM Merge_Data.Repository)
                                UNION ALL
                                (SELECT MIN(size) / 1024, AVG(size) / 1024,MAX(size) / 1024
                                FROM Merge_Data.Repository)"""
        self.parallel_changed_commits_query = """select merge_commit_hash from Merge_Data.Merge_Scenario sc Where parallel_changed_file_num > 0"""
        self.merge_commits_langs_query = """SELECT language, COUNT(is_conflict) AS "Merge Scnenario No.",SUM(is_conflict) AS "Conflict No."
                FROM Merge_Data.Repository JOIN Merge_Data.Merge_Replay
                ON Repository.id = Merge_Replay.Merge_Scenario_Repository_id
                WHERE language IN ('Java', 'Python', 'PHP', 'RUBY', 'C++')
                GROUP BY language"""
        self.conflict_per_language_query = """SELECT language, COUNT(is_conflict),SUM(is_conflict)
                FROM Merge_Data.Repository JOIN Merge_Data.Merge_Replay
                ON Repository.id = Merge_Replay.Merge_Scenario_Repository_id
                WHERE language IN ('Java', 'Python', 'PHP', 'RUBY', 'C++')
                GROUP BY language"""
        self.repository_per_language_query = """SELECT language, COUNT(name) AS "Repository No."
                FROM Merge_Data.Repository
                WHERE language IN ('Java', 'Python', 'PHP', 'RUBY', 'C++')
                GROUP BY language"""
        self.scenarios_num_of_lang_query = """SELECT COUNT(merge_commit_hash)
            FROM Merge_Data.Repository JOIN Merge_Data.Merge_Scenario on id = Repository_id
            WHERE language = '{}'
            GROUP BY name"""
        self.conflicts_num_of_lang_query = """SELECT COUNT(is_conflict)
            FROM Merge_Data.Repository JOIN Merge_Data.Merge_Replay on id = Merge_Scenario_Repository_id
            WHERE language = '{}' and is_conflict = 1
            GROUP BY name"""

    def get_conflicts_nums_by_lang(self, lang): # TODO: The number of data in two branches is not the same.
        logging.info('Getting all scenarios of lang...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.conflicts_num_of_lang_query.format(lang)))

    def get_scenarios_nums_by_lang(self, lang): # TODO: The number of data in two branches is not the same.
        logging.info('Getting all scenarios of lang...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.scenarios_num_of_lang_query.format(lang)))


    def get_conflict_per_language(self):
        logging.info('Extracting conflicts per language...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.conflict_per_language_query))

    def get_repository_per_language(self):
        logging.info('Extracting conflicts per language...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.repository_per_language_query))

    def get_parallel_changed_commits(self):
        logging.info('Extracting parallel changes...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.parallel_changed_commits_query))

    def get_query_result(self, query):

        engine = create_engine('mysql+pymysql://{}:{}@localhost/{}'.format(config.DB_USER_NAME, config.DB_PASSWORD, config.DB_NAME))
        df = pd.read_sql_query(query, engine)
        return df

        # return os.popen('mysql -u {} -e "{}"'.format(config.DB_USER_NAME, query)).read()

    def get_data_frame_of_query_result(self, query_result):
        return query_result
        if len(query_result) == 0:
            print('Empty result!')
            return -1
        return pd.read_csv(StringIO(query_result), delimiter='\t')

    def get_complexity(self):
        logging.info('Extracting code complexity...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.code_complexity_query))

    def get_code_violation(self):
        logging.info('Extracting code style violation...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.code_violation_query))

    def get_parallel_changes(self):
        logging.info('Extracting code parallel changes...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.parallel_changes_query))

    def get_commit_num(self, parent): # TODO: The number of data in two branches is not the same.
        logging.info('Extracting the number of commits...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.commit_num_query.format(parent)))

    def get_commit_density(self, parent):
        logging.info('Extracting commit density...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.commit_density_two_weeks.format(parent)))

    def get_file_changes(self, parent):
        logging.info('Extracting file changes...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.file_change_query.format(parent)))

    def get_line_changes(self, parent):
        logging.info('Extracting line changes...')
        return self.get_data_frame_of_query_result(self.get_query_result(self.line_change_query.format(parent)))

    def get_developer_num(self, parent):
        logging.info('Extracting developer num...')
        res = self.get_data_frame_of_query_result(self.get_query_result(self.developer_num_query.format(parent))).drop('merge_commit_hash', axis=1).values
        return pd.DataFrame([item for sublist in res for item in sublist], columns=['# Developers'])

    def get_merge_scenarios_in_lang(self, langs):
        logging.info('Extracting merges by language...')
        langs = ','.join(['\'{}\''.format(lang) for lang in langs])
        return self.get_data_frame_of_query_result(self.get_query_result(self.merge_commits_langs_query.format(langs)))

    def get_commit_messege_characteristics(self, parent):
        logging.info('Extracting message characteristics...')
        commit_messages = self.get_query_result(self.commit_message_quey.format(parent))
        commit_messages_list = commit_messages.values[1:]
        commit_messages_list = [item for sublist in commit_messages_list for item in sublist if item is not None]
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
        column_names_frequency = ['# fix', '# bug', '# feature', '# improve', '# document', '# refactor', '# update',
                                  '# add', '# remove', '# use', '# delete', '# change']
        column_names_stats = ['Min Msg Length', 'Mean Msg Length', 'Median Msg Length', 'Max Msg Length']
        return pd.DataFrame(keywords_frequency, columns=column_names_frequency), \
               pd.DataFrame(commit_messege_length_stats, columns=column_names_stats)

    def get_branch_duration(self, parent):
        logging.info('Extracting branch duration...')
        res = self.get_data_frame_of_query_result(self.get_query_result(self.branch_duration.format(parent))).drop(
            'merge_commit_hash', axis=1).values
        return pd.DataFrame([item for sublist in res for item in sublist], columns=['Branch Duration'])

    def get_is_conflict(self):
        res = self.get_data_frame_of_query_result(self.get_query_result(self.is_conflict_query.format())).drop(
            'Merge_Scenario_merge_commit_hash', axis=1).values
        return pd.DataFrame([item for sublist in res for item in sublist], columns=['Is Conflict'])

    def get_merge_scenario_prediction_data(self, langs):
        keywords_frequency1, commit_messege_length_stats1 = self.get_commit_messege_characteristics(1)
        keywords_frequency2, commit_messege_length_stats2 = self.get_commit_messege_characteristics(2)
        git_features_scenario = self.get_parallel_changes()
        features = [git_features_scenario,
            self.get_commit_num(1).drop('merge_commit_hash', axis=1) - self.get_commit_num(2).drop('merge_commit_hash',
                                                                                                   axis=1),
            self.get_commit_density(1).drop('merge_commit_hash', axis=1) - self.get_commit_density(2).drop(
                'merge_commit_hash', axis=1),
            self.get_file_changes(1).drop('merge_commit_hash', axis=1) - self.get_file_changes(2).drop(
                'merge_commit_hash', axis=1),
            self.get_line_changes(1).drop('merge_commit_hash', axis=1) - self.get_line_changes(2).drop(
                'merge_commit_hash', axis=1),
             self.get_developer_num(1) - self.get_developer_num(2),
            keywords_frequency1 - keywords_frequency2,
            commit_messege_length_stats1 - commit_messege_length_stats2,
            self.get_branch_duration(1) - self.get_branch_duration(2)]

        lang_data = self.get_merge_scenarios_in_lang(langs)
        data = pd.concat([pd.concat(features, axis=1).sort_values(by=['merge_commit_hash']), lang_data], axis=1)
        data = data[data['language'].isin(langs)].drop('merge_commit_hash', axis=1).drop('language', axis=1)

        label = self.get_data_frame_of_query_result(self.get_query_result(self.is_conflict_query.format())).sort_values(by=['Merge_Scenario_merge_commit_hash']).drop(
            'Merge_Scenario_merge_commit_hash', axis=1).values
        label = pd.DataFrame([item for sublist in label for item in sublist], columns=['Is Conflict'])
        label = pd.concat([label, lang_data], axis=1)
        label = label[label['language'].isin(langs)].drop('merge_commit_hash', axis=1).drop('language', axis=1)
        return data, label

    def save_prediction_data_to_csv(self, langs, post_name):
        logging.info('Start {}'.format(post_name))
        data, label = self.get_merge_scenario_prediction_data(langs)
        data.to_csv(path_or_buf=config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_DATA_NAME + post_name)
        label.to_csv(path_or_buf=config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_LABEL_NAME + post_name)

    def get_conflict_ratio(self):
        return self.get_data_frame_of_query_result(self.get_query_result(self.conflict_rate_query))

    def get_repository_stats(self):
        return self.get_data_frame_of_query_result(self.get_query_result(self.repository_stat)).rename(index={0:'star', 1:'watch', 2: 'fork', 3: 'issue', 4:'size'})

    def print_df_stats(self, df):
        print('DataFrame Stats:')
        print('  - # Data Points: {}'.format(df.shape[0]))
        print('  - # Features: {}'.format(df.shape[1]))
        print('  - Index: {}'.format(df.index))
        print('  - Columns: {}'.format(df.columns))


def draw_normalized_scenarios_per_lang():
    obj = Data_Retreival()
    conflict_per_language = obj.get_conflict_per_language()
    repository_per_language = obj.get_repository_per_language()
    merges_per_language_normalized= conflict_per_language['COUNT(is_conflict)'].div(repository_per_language['Repository No.'], axis=0)
    conflicts_per_language_normalized= conflict_per_language['SUM(is_conflict)'].div(repository_per_language['Repository No.'], axis=0)
    pd.concat([merges_per_language_normalized, conflicts_per_language_normalized], axis=1).plot(kind='bar')
    langs = ['C++', 'Java', 'PHP', 'Python', 'Ruby']
    y_pos = np.arange(len(langs))
    plt.xticks(y_pos, langs)
    plt.xlabel('Programming Languages')
    plt.ylabel('NN. Merges  / No. Repositories')
    plt.legend(['Total Merge Scenarios', 'Conflicting Merge Scenarios'])
    plt.show()

def draw_likelihood_merges():
    obj = Data_Retreival()
    langs = ['C++', 'Java', 'PHP', 'Python', 'Ruby']
    ax = obj.get_scenarios_nums_by_lang(langs[0]).plot.kde()
    for i, item in enumerate(langs):
        if i == 0:
            continue
        obj.get_scenarios_nums_by_lang(langs[i]).plot.kde(ax=ax)
    plt.xlim((0, 1500))
    plt.legend(langs)
    plt.xlabel('No. Merge Scenarios')
    plt.ylabel('Likelihood')
    plt.show()

def draw_likelihood_conflicts():
    obj = Data_Retreival()
    langs = ['C++', 'Java', 'PHP', 'Python', 'Ruby']
    ax = obj.get_conflicts_nums_by_lang(langs[0]).plot.kde()
    for i, item in enumerate(langs):
        if i == 0:
            continue
        obj.get_scenarios_nums_by_lang(langs[i]).plot.kde(ax=ax)
    plt.xlim((0, 1500))
    plt.legend(langs)
    plt.xlabel('No. Merge Scenarios')
    plt.ylabel('Likelihood')
    plt.show()


def adjacent_values(vals, q1, q3):
    upper_adjacent_value = q3 + (q3 - q1) * 1.5
    upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])

    lower_adjacent_value = q1 - (q3 - q1) * 1.5
    lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
    return lower_adjacent_value, upper_adjacent_value

def draw_violin_scenarios():
    obj = Data_Retreival()
    langs = ['C++', 'Java', 'PHP', 'Python', 'Ruby']
    data = []
    for i, item in enumerate(langs):
        data.append(obj.get_scenarios_nums_by_lang(langs[i]).values)
    fig, ax = plt.subplots()
    parts = ax.violinplot(data, showmeans=True)
    # plt.legend(langs)
    plt.xlabel('Programming Languages')
    plt.ylabel('No. Merge Scenarios')
    ind = np.arange(len(langs)) + 1
    plt.xticks(ind, langs)
    plt.show()

def draw_violin_conflicts():
    obj = Data_Retreival()
    langs = ['C++', 'Java', 'PHP', 'Python', 'Ruby']
    data = []
    for i, item in enumerate(langs):
        data.append(obj.get_conflicts_nums_by_lang(langs[i]).values)
    fig, ax = plt.subplots()
    parts = ax.violinplot(data, showmeans=True)
    # plt.legend(langs)
    plt.xlabel('Programming Languages')
    plt.ylabel('No. Conflicting Merge Scenarios')
    ind = np.arange(len(langs)) + 1
    plt.xticks(ind, langs)
    plt.show()

def draw_violin_scenarios_conflicts():
    obj = Data_Retreival()
    langs = ['C++', 'Java', 'PHP', 'Python', 'Ruby']
    data_scenarios = []
    data_conflicts = []
    for i, item in enumerate(langs):
        data_scenarios.append(obj.get_conflicts_nums_by_lang(langs[i]).values)
        data_conflicts.append(obj.get_scenarios_nums_by_lang(langs[i]).values)
    data2 = data_scenarios
    data1 = data_conflicts
    v1 = plt.violinplot(data1, positions=np.arange(0, len(data1)), widths=1,
                       showmeans=False, showextrema=False, showmedians=False)
    for b in v1['bodies']:
        m = np.mean(b.get_paths()[0].vertices[:, 0])
        b.get_paths()[0].vertices[:, 0] = np.clip(b.get_paths()[0].vertices[:, 0], -np.inf, m)
        b.set_color('r')
        b.set_alpha(0.5)
        b.set_edgecolor('k')
    v2 = plt.violinplot(data2, positions=np.arange(0, len(data2)), widths=1,
                       showmeans=False, showextrema=False, showmedians=False)
    for b in v2['bodies']:
        m = np.mean(b.get_paths()[0].vertices[:, 0])
        b.get_paths()[0].vertices[:, 0] = np.clip(b.get_paths()[0].vertices[:, 0], m, np.inf)
        b.set_color('b')
        b.set_alpha(0.5)
        b.set_edgecolor('k')
    b1, b2 = plt.plot([1],'b'), plt.plot([1],'r')
    # plt.legend([b1[0], b2[0]], ['Conflicting Merge Scenarios', 'Total Merge Scenarios'], loc = 0)
    ind = np.arange(len(langs))
    plt.xticks(ind, langs)
    plt.xlabel('Programming Languages')
    plt.ylabel('No. Merge Scenarios')
    plt.gca().set_ylim([0, 1200])
    plt.show()


if __name__ == "__main__":

    # Logging
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s in %(threadName)s - %(asctime)s by %(name)-12s :  %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S')


    #draw_violin_scenarios()
    #draw_violin_conflicts()
    #exit()

    obj = Data_Retreival()
    print(obj.get_conflict_ratio())
    exit()

    print('Start data saving')

    lang_test = [['Java'], ['Python'], ['PHP'], ['Ruby'], ['C++'], ['Java', 'Python', 'Ruby', 'PHP', 'C++']]
    name_test = ['_JAVA', '_PYTHON', '_PHP', '_RUBY', '_C++', '_ALL']

    # Parallel execution
    core_num = multiprocessing.cpu_count()
    Parallel(n_jobs=core_num)(delayed(obj.save_prediction_data_to_csv)(lang_test[i], name_test[i]) for i in range(len(name_test)))



    print('Finish data saving')

    #print(obj.get_repository_stats())
