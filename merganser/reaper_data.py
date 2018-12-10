
import os
import csv
import random
import pandas as pd

import config

rep_list = []


def save_selected_repositories(language, stars_min, top_repos, repos_list_name):

    gfFile = config.REAPER_DATASET_PATH + '.gz'

    # Download dataset
    if os.path.exists('../tools/reaper/dataset.csv') == False:
        os.system('wget https://reporeapers.github.io/static/downloads/dataset.csv.gz -P'
                  ' ../tools/reaper; gunzip {}'.format(gfFile))

    # Read the dataframe
    reaper_df = pd.read_csv(config.REAPER_DATASET_PATH, low_memory=False)

    # Select the repositories
    reaper_df = reaper_df[reaper_df['scorebased_org'] == 1]
    reaper_df = reaper_df[reaper_df['randomforest_org'] == 1]
    reaper_df = reaper_df[reaper_df['scorebased_utl'] == 1]
    reaper_df = reaper_df[reaper_df['randomforest_utl'] == 1]
    reaper_df = reaper_df[reaper_df['language'] == language]
    reaper_df = reaper_df.dropna()
    reaper_df = reaper_df[reaper_df['stars'] != 'None']
    reaper_df = reaper_df.astype({'stars': 'int64'})
    reaper_df = reaper_df.sort_values('stars', ascending=False)
    reaper_df = reaper_df[reaper_df['stars'] > stars_min]
    reaper_df = reaper_df.head(top_repos)
    reaper_df = reaper_df['repository']

    file_name = config.REPOSITORY_LIST_PATH + repos_list_name + '.txt'

    # Remove the olf file
    os.system('rm -f {}'.format(file_name))

    # Save the results
    reaper_df.to_csv(file_name, index=False)


if __name__ == "__main__":

    # Basic file name
    file_name = 'reaper_top_' + str(config.TOP_REPOS_NUM) + '_more_than_' + str(config.STARS_MIN) + '_stars_'

    # Save the repositories for each language
    for language in config.LANGUAGES:
        save_selected_repositories(language, config.STARS_MIN, config.TOP_REPOS_NUM, file_name + language)
