
import os
import numpy as np
from io import StringIO
import pandas as pd

import config
import logging


class DataRetrieval:

    def __init__(self):

        # Read the queries
        self.light_features_query = open(config.QUERY_PATH + 'light_features_query.sql', 'r').read()
        self.commit_density_two_weeks = open(config.QUERY_PATH + 'commit_density_two_weeks.sql', 'r').read()
        self.commit_message_query = open(config.QUERY_PATH + 'commit_message_query.sql', 'r').read()
        self.is_conflict_query = open(config.QUERY_PATH + 'is_conflict_query.sql', 'r').read()

    def get_query_result(self, query):
        """
        This method receives a query and return its result as a Pandas DataFrame
        :param query: A MySQL query to analyze
        :return: The result of the query as a Pandas DataFrame
        """

        query_result = os.popen('mysql -u {} --password={} -e "{}"'.format(config.DB_USER_NAME, config.DB_PASSWORD, query)).read()
        return pd.read_csv(StringIO(query_result), delimiter='\t')

    def save_prediction_data(self, languages):
        """
        This method saves the prediction data (for the data nad label) for each programming language
        :param languages: The list of programming languages
        """

        logging.info('Saving data and label of prediction task...')

        # Data preparation
        messages_features = self.get_commit_message_characteristics()
        data = pd.concat([self.get_light_features(), self.get_commit_density(), messages_features[0], messages_features[1]], axis=1).drop('merge_commit', axis=1)
        label = self.get_query_result(self.is_conflict_query.format()).drop('merge_commit', axis=1)

        # Store the data for each programming language
        for language in languages:
            logging.info('  - Preparing data and label of prediction task for {}'.format(language))
            temp_data = data[data['language'] == language].drop('language', axis=1)
            temp_label = label[label['language'] == language].drop('language', axis=1)
            temp_data.to_csv(path_or_buf=config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_DATA_NAME.replace('<NAME>', language), index=False)
            temp_label.to_csv(path_or_buf=config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_LABEL_NAME.replace('<NAME>', language), index=False)

    def get_light_features(self):
        """
        This method returns the light-weight features
        :return: The light-weight features as a Pandas DataFrame
        """

        logging.info('Extracting light-weight features...')
        return self.get_query_result(self.light_features_query)

    def get_commit_density(self):
        """
        This method returns the commit density features
        :return: The commit density features as a Pandas DataFrame
        """

        logging.info('Extracting commit density...')
        density_paren1 = pd.DataFrame(self.get_query_result(self.commit_density_two_weeks.format(1)))
        density_paren2 = pd.DataFrame(self.get_query_result(self.commit_density_two_weeks.format(2)))
        density_diff =  density_paren2['commit_density'] - density_paren1['commit_density']
        return pd.concat([density_paren1['merge_commit'], density_diff], axis=1)

    def get_commit_message_characteristics(self):
        """
        This method returns the message characteristics features
        :return: The message characteristics features as a Pandas DataFrame
        """

        logging.info('Extracting message characteristics...')
        commit_messages = self.get_query_result(self.commit_message_query.format())
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

    # Data preparation
    languages = config.LANGUAGES
    obj = DataRetrieval()
    obj.save_prediction_data(languages)

    logging.info('The prediction data was extracted successfully.')


