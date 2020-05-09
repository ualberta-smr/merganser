from pathlib import Path

import multiprocessing
import numpy as np
from numpy.random import randint
import time

# Keys
GITHUB_KEY = '60fe91bab0512c3a6221ec0b8741318965315b00'

# Paths
REPOSITORY_PATH = Path('./working_dir/repository/')
TEMP_CSV_PATH = Path('./working_dir/csv_files/')
REPOSITORY_LIST_PATH = Path('./working_dir/repository_lists/')
LOG_PATH = Path('./working_dir/logs/')
QUERY_PATH = Path('./queries/')
PREDICTION_RESULT_PATH = Path('./working_dir/prediction_result/')
PREDICTION_CSV_PATH = Path('./working_dir/prediction_data/')
REAPER_DATASET_PATH = Path('./tools/reaper/dataset.csv')
PREDICTION_RES_PATH = Path('./working_dir/prediction_result/')
PREDICTION_CSV_DATA_NAME = 'data_prediction_<LANGUAGE>_<REPOSITORY>.csv'
PREDICTION_CSV_LABEL_NAME = 'label_prediction_<LANGUAGE>_<REPOSITORY>.csv'

# Constants
MAX_MERGE_SCENARIOS = 5000
MAX_ANALYZING_DAY = 7
MAX_REPO_SIZE_TO_ANALYZE = 10 * 1024 * 1024
MAX_CPU_CORES = int(multiprocessing.cpu_count() / 2)
MIN_MERGE_SCENARIO = 1

# DB information
DB_HOST = 'localhost'
DB_NAME = 'Merge_Data'
DB_USER_NAME = 'moein'
DB_PASSWORD = '123'

# Visualization
VIS_S = 100
VIS_ALPHA = 0.4

# Prediction
MIN_SAMPLE_LEAVES = np.random.randint(low=2, high=36, size=5)
MIN_SAMPLE_SPLIT = np.random.randint(low=2, high=36, size=5)
ESTIMATOR_NUM = np.random.randint(low=1, high=11, size=5)
LEARNING_RATE = [0.7, 0.9, 1.0, 1.1, 1.5]
FOLD_NUM = 10
SCORING_FUNCTION = 'f1'
TREE_MAX_DEPTH = np.random.randint(low=1, high=9, size=5)
TEST_SIZE = 0.25
RANDOM_SEED = int(time.time())
np.random.seed(RANDOM_SEED)
TREE_FILE_NAME = 'tree.dot'
TRAIN_RATE = 0.75

# REAPER repository search
STARS_MIN = 100
TOP_REPOS_NUM = 100
LANGUAGES = ['C', 'C#', 'C++', 'Java', 'PHP', 'Python', 'Ruby']
