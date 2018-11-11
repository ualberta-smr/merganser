
# Keys
GITHUB_KEY = 'f7789a850c830ed5812237123e2a77fbe2d98a20'

# Paths
REPOSITORY_PATH = '../working_dir/repository/'
TEMP_CSV_PATH = '../working_dir/csv_files/'
REPOSITORY_LIST_PATH = '../working_dir/repository_lists/'
LOG_PATH = '../working_dir/logs/'
QUERY_PATH = '../queries/'
PREDICTION_CSV_PATH = '../working_dir/prediction_data/'
PREDICTION_CSV_DATA_NAME = 'data.csv'
PREDICTION_CSV_LABEL_NAME = 'label.csv'

# Constants
MAX_MERGE_SCENARIOS = 1000
MAX_ANALYZING_DAY = 2
MAX_REPO_SIZE_TO_ANALYZE = 100 * 1024

# DB information
DB_HOST = 'localhost'
DB_NAME = 'Merge_Data'
DB_USER_NAME = 'root'
DB_PASSWORD = ''

# Visualization
VIS_S = 100
VIS_ALPHA = 0.4

# Prediction
MIN_SAMPLE_LEAFES = [2, 5, 10, 20, 50, 70, 100]
MIN_SAMPLE_SPLIT = [2, 3, 5, 10, 15, 20, 50]
ESTIMATOR_NUM = [1, 2, 3, 5, 10, 15, 20, 30, 80, 100, 150, 200]
LEARNING_RATE = [0.9, 1.0, 1.1]
FOLD_NUM = 10
SCORING_FUNCTION = 'f1'
TREE_MAX_DEPTH = [1, 3, 5, 7, 11]
TEST_SIZE = 0.25
RANDOM_SEED = 17
TREE_FILE_NAME = 'tree.dot'

