import multiprocessing


# Keys
GITHUB_KEY = 'fc76875417cb60f7b61a969753d7cc98a1ef3099'

# Paths
REPOSITORY_PATH = '../working_dir/repository/'
TEMP_CSV_PATH = '../working_dir/csv_files/'
REPOSITORY_LIST_PATH = '../working_dir/repository_lists/'
LOG_PATH = '../working_dir/logs/'
QUERY_PATH = '../queries/'
PREDICTION_RESULT_PATH = '../working_dir/prediction_result/'
PREDICTION_CSV_PATH = '../working_dir/prediction_data/'
REAPER_DATASET_PATH = '../tools/reaper/dataset.csv'
PREDICTION_CSV_DATA_NAME = 'data_prediction_<LANGUAGE>_<REPOSITORY>.csv'
PREDICTION_CSV_LABEL_NAME = 'label_prediction_<LANGUAGE>_<REPOSITORY>.csv'

# Constants
MAX_MERGE_SCENARIOS = 5000
MAX_ANALYZING_DAY = 7
MAX_REPO_SIZE_TO_ANALYZE = 10 * 1024 * 1024
MAX_CPU_CORES = int(multiprocessing.cpu_count() / 2)

# DB information
DB_HOST = 'localhost'
DB_NAME = 'Merge_Data'
DB_USER_NAME = 'moein'
DB_PASSWORD = '123'

# Visualization
VIS_S = 100
VIS_ALPHA = 0.4

# Prediction
MIN_SAMPLE_LEAVES = [2, 5, 10]
MIN_SAMPLE_SPLIT = [2, 3, 5, 10]
ESTIMATOR_NUM = [2, 5, 10, 30, 50]
LEARNING_RATE = [0.7, 0.9, 1.0, 1.1, 1.5]
FOLD_NUM = 10
SCORING_FUNCTION = 'f1'
TREE_MAX_DEPTH = [1, 2, 3, 5, 7, 11]
TEST_SIZE = 0.25
RANDOM_SEED = 17
TREE_FILE_NAME = 'tree.dot'
TRAIN_RATE = 0.75

# REAPER repository search
STARS_MIN = 100
TOP_REPOS_NUM = 100
LANGUAGES = ['C', 'C#', 'C++', 'Java', 'PHP', 'Python', 'Ruby']
