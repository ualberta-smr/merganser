
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
        
        -- where merge_scenario.parallel_changed_file_num > 0
        
        GROUP BY merge_scenario.merge_commit_hash, merge_scenario.parallel_changed_file_num, merge_scenario.parent1_developer_num, merge_scenario.parent2_developer_num, merge_scenario.parent1_date, merge_scenario.parent2_date, merge_scenario.ancestor_date

        """

        self.commit_density_two_weeks = """
        SELECT merge_scenario.merge_commit_hash as 'merge_commit', count(Commits.commit_hash) as 'commit_density'
        FROM Merge_Data.Merge_Scenario merge_scenario
        LEFT JOIN Merge_Data.Merge_Related_Commit Commits 
        on merge_scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash 
        AND Commits.merge_commit_parent = {}
        AND TIMESTAMPDIFF(WEEK, merge_scenario.merge_commit_date, Commits.date) < 3
        -- where merge_scenario.parallel_changed_file_num > 0
        GROUP BY merge_scenario.merge_commit_hash;
        """

        self.commit_message_quey = """
        SELECT merge_commit_hash as 'merge_commit', LOWER(GROUP_CONCAT(message SEPARATOR ' ||| ')) as 'commit_messages'
        FROM Merge_Data.Merge_Scenario 
        JOIN Merge_Data.Merge_Related_Commit  
        on merge_commit_hash = Merge_Scenario_merge_commit_hash 
        -- where parallel_changed_file_num > 0
        GROUP BY merge_commit_hash;
       """

        self.is_conflict_query = """
        SELECT  
        merge_scenario.merge_commit_hash as 'merge_commit',
        merge_replay.is_conflict as 'is_conflict'
        
        FROM Merge_Data.Merge_Scenario as merge_scenario 
        JOIN Merge_Data.Merge_Replay as merge_replay ON  merge_scenario.merge_commit_hash = merge_replay.Merge_Scenario_merge_commit_hash
        
        -- where merge_scenario.parallel_changed_file_num > 0
        
        GROUP BY merge_scenario.merge_commit_hash, merge_replay.is_conflict
        """

    def get_query_result(self, query):

        # engine = create_engine('mysql+pymysql://{}:{}@localhost/{}'.format(config.DB_USER_NAME, config.DB_PASSWORD, config.DB_NAME))
        # df = pd.read_sql_query(query, engine)
        # return df

        query_result = os.popen('mysql -u {} -e "{}"'.format(config.DB_USER_NAME, query)).read()
        return pd.read_csv(StringIO(query_result), delimiter='\t')

    def get_merge_scenario_prediction_data(self, post_name):
        logging.info('Preparing data and label of prediction task for {}'.format(post_name.replace('_', '')))
        messages_features = self.get_commit_messege_characteristics()
        data = pd.concat([self.get_light_features(), self.get_commit_density(), messages_features[0], messages_features[1]], axis=1).drop('merge_commit', axis=1)
        label = self.get_query_result(self.is_conflict_query.format()).drop('merge_commit', axis=1)
        return data, label

    def save_prediction_data(self, post_name):
        logging.info('Saving data and label of prediction task for {}'.format(post_name.replace('_', '')))
        data, label = self.get_merge_scenario_prediction_data(post_name)
        data.to_csv(path_or_buf=config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_DATA_NAME + post_name)
        label.to_csv(path_or_buf=config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_LABEL_NAME + post_name)

    def get_light_features(self):
        logging.info('Extracting light-weight features...')
        return self.get_query_result(self.light_features_query)

    def get_commit_density(self):
        logging.info('Extracting commit density...')
        density_paren1 = pd.DataFrame(self.get_query_result(self.commit_density_two_weeks.format(1)))
        density_paren2 = pd.DataFrame(self.get_query_result(self.commit_density_two_weeks.format(2)))
        density_diff =  density_paren2['commit_density'] - density_paren1['commit_density']
        return pd.concat([density_paren1['merge_commit'], density_diff], axis=1)

    def get_commit_messege_characteristics(self):
        logging.info('Extracting message characteristics...')
        commit_messages = self.get_query_result(self.commit_message_quey.format())
        keywords = sorted(['fix', 'bug', 'feature', 'improve', 'document', 'refactor', 'update', 'add', 'remove', 'use',
                        'delete', 'change'])
        keywords_names = [keyword + '_frequency' for keyword in keywords]
        keywords_frequency = np.zeros((commit_messages.shape[0], len(keywords)))
        messages_stats = np.zeros((commit_messages.shape[0], 4))
        for index, merge in commit_messages.iterrows():
            if not isinstance(merge['commit_messages'], str):
                continue
            for keyword_id, keyword in enumerate(keywords):
                keywords_frequency[index, keyword_id] = merge['commit_messages'].count(keyword)
            messagess_len = [len(message) for message in merge['commit_messages'].split('|||')]
            messages_stats[index, :] = [np.min(messagess_len), np.max(messagess_len),
                                        np.mean(messagess_len), np.median(messagess_len)]
        keywords_frequency_df = pd.DataFrame(data=keywords_frequency, columns=keywords_names)
        messages_stats_df =  pd.DataFrame(data=messages_stats, columns=['messages_min', 'messages_max',
                                                                        'messages_mean', 'messages_median'])
        return keywords_frequency_df, messages_stats_df


if __name__ == "__main__":

    # Logging
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s in %(threadName)s - %(asctime)s by %(name)-12s :  %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S')
    obj = Data_Retreival()
    data_df = obj.save_prediction_data('_All2')
    #print(data_df)


