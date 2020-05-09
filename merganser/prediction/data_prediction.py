
import numpy as np
import pandas as pd
import pymysql

import config
import logging


class DataRetrieval:

    def __init__(self):

        # Read the queries
        self.light_features_query = open(config.QUERY_PATH + 'light_features_query.sql', 'r').read()
        self.commit_density_two_weeks = open(config.QUERY_PATH + 'commit_density_two_weeks.sql', 'r').read()
        self.commit_message_query = open(config.QUERY_PATH + 'commit_message_query.sql', 'r').read()
        self.is_conflict_query = open(config.QUERY_PATH + 'is_conflict_query.sql', 'r').read()
        self.repo_date = open(config.QUERY_PATH + 'merge_scenario_repos_date.sql', 'r').read()

    def get_query_result(self, query):
        """
        This method receives a query and return its result as a Pandas DataFrame
        :param query: A MySQL query to analyze
        :return: The result of the query as a Pandas DataFrame
        """

        mysql_cn= pymysql.connect(host='localhost', 
                        port=3306,user=config.DB_USER_NAME, passwd=config.DB_PASSWORD, 
                        db='Merge_Data')
        df_mysql = pd.read_sql(f'{query}', con=mysql_cn) 
        return df_mysql

    def save_prediction_data(self, languages):
        """
        This method saves the prediction data (for the data nad label) for each programming language
        :param languages: The list of programming languages
        """

        logging.info('Saving data and label of prediction task...')

        repo_date = self.get_repos_date()
        repos_set = set(repo_date['name'].tolist())

        # Data preparation
        messages_features = self.get_commit_message_characteristics()
        d1 = repo_date.merge(self.get_light_features(), on='merge_commit')
        d2 = d1.merge(self.get_commit_density(), on='merge_commit')
        data = d2.merge(messages_features, on='merge_commit')
        data.drop('merge_commit', axis=1, inplace=True)
        label = self.get_query_result(self.is_conflict_query.format()).drop('merge_commit', axis=1)


        # Store the data for each programming language
        for repo in repos_set:
            
            t = data[data['name'] == repo]
            language = t['language'].tolist()[0]
            print(language)

            logging.info('  - Preparing data and label of prediction task for {}'.format(language))

            temp_data = data[data['language'] == language].drop('language', axis=1)
            if len(temp_data) == 0:
                continue
            temp_label = label[label['language'] == language].drop('language', axis=1)

            temp_data = temp_data[temp_data['name'] == repo].drop('name', axis=1)
            temp_label = temp_label[temp_label['name'] == repo].drop('name', axis=1)

            temp_data.to_csv(path_or_buf=config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_DATA_NAME.replace('<LANGUAGE>', language).replace('<REPOSITORY>', repo.replace('/', '-')), index=False)
            temp_label.to_csv(path_or_buf=config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_LABEL_NAME.replace('<LANGUAGE>', language).replace('<REPOSITORY>', repo.replace('/', '-')), index=False)

    def get_light_features(self):
        """
        This method returns the light-weight features
        :return: The light-weight features as a Pandas DataFrame
        """

        logging.info('Extracting light-weight features...')
        return self.get_query_result(self.light_features_query)

    def get_repos_date(self):
        """
        This method returns the repos name and date of merge scenario
        :return: The repo name and date of merge scenarios as a Pandas DataFrame
        """

        logging.info('Extracting commit density...')
        repo_date = pd.DataFrame(self.get_query_result(self.repo_date))
        return repo_date

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
        commit_messages.dropna(inplace=True)
        keywords = sorted(['fix', 'bug', 'feature', 'improve', 'document', 'refactor', 'update', 'add', 'remove', 'use',
                        'delete', 'change'])
        keywords_names = [keyword + '_frequency' for keyword in keywords]
        for keyword in keywords_names:
            commit_messages[keyword] = commit_messages.apply(lambda x: x['commit_messages'].count(keyword), axis=1)

        commit_messages['messages_min'] = commit_messages.apply(lambda x: np.min([len(message) for message in x['commit_messages'].split('|||')] ), axis=1)
        commit_messages['messages_max'] = commit_messages.apply(lambda x: np.max([len(message) for message in x['commit_messages'].split('|||')] ), axis=1)
        commit_messages['messages_mean'] = commit_messages.apply(lambda x: np.mean([len(message) for message in x['commit_messages'].split('|||')] ), axis=1)
        commit_messages['messages_median'] = commit_messages.apply(lambda x: np.median([len(message) for message in x['commit_messages'].split('|||')] ), axis=1)

        commit_messages.drop("commit_messages", axis=1, inplace=True)

        return commit_messages 


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


