
import os
import math
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
def isNaN(num):
    return num != num

class Data_Retreival:

    def __init__(self):
        self.light_features_query = """
        SELECT  
        merge_scenario.merge_commit_hash as 'merge_commit',
        
        merge_scenario.parallel_changed_file_num,
        
        COUNT(commits.commit_hash) as 'commit_num',
        
        SUM(commits.file_added_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'file_added',
        SUM(commits.file_removed_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'file_removed',
        SUM(commits.file_renamed_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'file_renamed',
        SUM(commits.file_modified_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'file_modified',
        SUM(commits.file_copied_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'file_copied',
        
        SUM(commits.line_added_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'line_added',
        SUM(commits.line_removed_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'line_removed',
        
        merge_scenario.parent2_developer_num - merge_scenario.parent1_developer_num as 'developer_num',
        
        TIMESTAMPDIFF(HOUR, merge_scenario.parent2_date, merge_scenario.parent1_date)  as 'duration'
        
        FROM Merge_Data.Repository as repository
        JOIN Merge_Data.Merge_Scenario as merge_scenario ON repository.id = merge_scenario.Repository_id
        JOIN Merge_Data.Merge_Replay as merge_replay ON repository.id = merge_replay.Merge_Scenario_Repository_id AND merge_scenario.merge_commit_hash = merge_replay.Merge_Scenario_merge_commit_hash
        JOIN Merge_Data.Merge_Related_Commit as commits ON repository.id = commits.Merge_Scenario_Repository_id and merge_scenario.merge_commit_hash = commits.Merge_Scenario_merge_commit_hash
        
        where merge_scenario.parallel_changed_file_num > 0
        
        GROUP BY merge_scenario.merge_commit_hash, merge_scenario.parallel_changed_file_num, merge_scenario.parent1_developer_num, merge_scenario.parent2_developer_num, merge_scenario.parent1_date, merge_scenario.parent2_date, merge_scenario.ancestor_date

        """

        self.commit_density_two_weeks = """
        SELECT merge_scenario.merge_commit_hash as 'merge_commit', count(Commits.commit_hash) as 'commit_density'
        FROM Merge_Data.Merge_Scenario merge_scenario
        LEFT JOIN Merge_Data.Merge_Related_Commit Commits 
        on merge_scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash 
        AND Commits.merge_commit_parent = {}
        AND TIMESTAMPDIFF(WEEK, merge_scenario.merge_commit_date, Commits.date) < 3
        where merge_scenario.parallel_changed_file_num > 0
        GROUP BY merge_scenario.merge_commit_hash;
        """

        self.commit_message_quey = """
        SELECT Merge_Scenario.merge_commit_hash as 'merge_commit', GROUP_CONCAT(Commits.message SEPARATOR \' ||| \') 
        FROM Merge_Data.Merge_Scenario merge_scenario 
        LEFT JOIN Merge_Data.Merge_Related_Commit Commits 
        on merge_scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash 
        AND Commits.merge_commit_parent = {}
        GROUP BY merge_scenario.merge_commit_hash
       """

        self.is_conflict_query = """
        SELECT  
        merge_scenario.merge_commit_hash as 'merge_commit',
        
        merge_replay.is_conflict
        
        FROM Merge_Data.Merge_Scenario as merge_scenario 
        JOIN Merge_Data.Merge_Replay as merge_replay ON  merge_scenario.merge_commit_hash = merge_replay.Merge_Scenario_merge_commit_hash
        
        where merge_scenario.parallel_changed_file_num > 0
        
        GROUP BY merge_scenario.merge_commit_hash, merge_replay.is_conflict
        """

    def get_query_result(self, query):

        # engine = create_engine('mysql+pymysql://{}:{}@localhost/{}'.format(config.DB_USER_NAME, config.DB_PASSWORD, config.DB_NAME))
        # df = pd.read_sql_query(query, engine)
        # return df

        query_result = os.popen('mysql -u {} -e "{}"'.format(config.DB_USER_NAME, query)).read()
        return pd.read_csv(StringIO(query_result), delimiter='\t')

    def get_merge_scenario_prediction_data(self):
        data = self.get_light_features()

        label = self.get_query_result(self.is_conflict_query.format())

        label = label.drop('merge_commit', axis=1)
        return data, label

    def save_prediction_data(self, post_name):
        logging.info('Start {}'.format(post_name))
        data, label = self.get_merge_scenario_prediction_data()
        data.to_csv(path_or_buf=config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_DATA_NAME + post_name)
        label.to_csv(path_or_buf=config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_LABEL_NAME + post_name)

    def get_light_features(self):
        logging.info('Extracting code complexity...')
        return self.get_query_result(self.light_features_query)

    def get_commit_density(self):
        logging.info('Extracting commit density...')
        density_paren1 = pd.DataFrame(self.get_query_result(self.commit_density_two_weeks.format(1)))
        density_paren2 = pd.DataFrame(self.get_query_result(self.commit_density_two_weeks.format(2)))
        density_diff =  density_paren2['commit_density'] - density_paren1['commit_density']
        return pd.concat([density_paren1['merge_commit'], density_diff], axis=1)

    def get_commit_messege_characteristics(self, parent):
        logging.info('Extracting message characteristics...')
        commit_messages = self.get_query_result(self.commit_message_quey.format(parent))
        commit_messages_list = commit_messages.values[1:]
        commit_messages_list = [item for sublist in commit_messages_list for item in sublist if not isNaN(item)]
        print((commit_messages_list))
        exit()
        keywords = sorted(['fix', 'bug', 'feature', 'improve', 'document', 'refactor', 'update', 'add', 'remove', 'use',
                        'delete', 'change'])
        keywords_frequency = []
        commit_messege_length_stats = []
        for merge_scenrio_commits in commit_messages_list:
            print(commit_messages_list)
            keywords_frequency.append([word.lower().count(word) for word in keywords])
            print(keywords_frequency)
            exit()
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

    def get_commit_message_features(self):
        keywords_frequency1, commit_messege_length_stats1 = self.get_commit_messege_characteristics(1)
        keywords_frequency2, commit_messege_length_stats2 = self.get_commit_messege_characteristics(2)
        keywords_frequency2 - keywords_frequency1,
        commit_messege_length_stats2 - commit_messege_length_stats1

if __name__ == "__main__":

    # Logging
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s in %(threadName)s - %(asctime)s by %(name)-12s :  %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S')
    obj = Data_Retreival()
    data_df = obj.save_prediction_data('_all')
    #print(data_df)


