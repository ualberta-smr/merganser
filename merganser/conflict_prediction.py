
import logging
import os
import json
import glob
import pandas as pd
import multiprocessing
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.model_selection import cross_val_predict
from sklearn.decomposition import IncrementalPCA
from scipy.stats import spearmanr

import config


def store_classification_result(model_name, language, model_classification_report, classification_results):
    """
    Stores the result of the classifier
    :param model_name: the classification type
    :param language: programming language
    :param model_classification_report: results
    :param classification_results: results
    """

    open('{}classification_result_raw_{}_{}.txt'.format(config.PREDICTION_RESULT_PATH, model_name, language), 'w')\
        .write(model_classification_report)
    open('{}classification_result_json_{}_{}.json'.format(config.PREDICTION_RESULT_PATH, model_name, language), 'w')\
        .write(json.dumps(classification_results))


def data_classification_wo_cv(language, data_train, label_train, data_test, label_test, random_seed=config.RANDOM_SEED, job_num=multiprocessing.cpu_count()):
    """
    Trains the classifier
    :param language: programming language
    :param data: input data
    :param label: input labels
    :param random_seed: the random_seed
    :param job_num: the number of cores to use
    """

    # CV
    inner_cv = KFold(n_splits=config.FOLD_NUM, shuffle=True, random_state=random_seed)
    outer_cv = KFold(n_splits=config.FOLD_NUM, shuffle=True, random_state=random_seed)

    # Hyper-parameters
    tree_param = {'min_samples_leaf': config.MIN_SAMPLE_LEAVES, 'min_samples_split': config.MIN_SAMPLE_SPLIT,
                  'max_depth': config.TREE_MAX_DEPTH}
    forest_param = {'n_estimators': config.ESTIMATOR_NUM, 'min_samples_leaf': config.MIN_SAMPLE_LEAVES,
                    'min_samples_split': config.MIN_SAMPLE_SPLIT}
    boosting_param = {'n_estimators': config.ESTIMATOR_NUM, 'learning_rate': config.LEARNING_RATE}

    # Grid search definition
    grid_searches = [
        GridSearchCV(DecisionTreeClassifier(class_weight='balanced', random_state = random_seed),
                  tree_param, cv=inner_cv, n_jobs=job_num, scoring=config.SCORING_FUNCTION),
        GridSearchCV(RandomForestClassifier(class_weight='balanced', n_jobs=job_num, random_state = random_seed),
                     forest_param, cv=inner_cv, n_jobs=job_num, scoring=config.SCORING_FUNCTION),
        GridSearchCV(ExtraTreesClassifier(n_jobs=job_num, class_weight='balanced', random_state = random_seed),
                     forest_param, cv=inner_cv, n_jobs=job_num, scoring=config.SCORING_FUNCTION),
        GridSearchCV(AdaBoostClassifier(base_estimator=DecisionTreeClassifier(class_weight = 'balanced',
                                                                                random_state = random_seed,
                                                                                max_depth=2),
                                        algorithm='SAMME.R', random_state=random_seed),
                     boosting_param, cv=inner_cv, n_jobs=job_num, scoring=config.SCORING_FUNCTION)
        ]

    # Fitting the classifiers
    classification_results = {}
    for model in grid_searches:

        # Model training/testing
        model.score_sample_weight = True
        model.fit(data_train, label_train)
        model_name = str(type(model.best_estimator_)).replace('<class \'', '').replace('\'>', '').split('.')[-1]
        model_best_param = model.best_params_
        predicted_label = model.best_estimator_.predict(data_test)

        # print(data_train.shape)
        # print(data_test.shape)
        # print(len(label_test))
        # print(len(predicted_label))
        # exit()


        model_accuracy = accuracy_score(label_test, predicted_label)
        model_confusion_matrix = confusion_matrix(label_test, predicted_label)
        model_classification_report = classification_report(label_test, predicted_label)
        classification_results[model_name] = {}
        classification_results[model_name]['best_params'] = model_best_param
        classification_results[model_name]['accuracy'] = model_accuracy
        classification_results[model_name]['confusion_matrix'] = model_confusion_matrix.tolist()
        classification_results[model_name]['classification_report'] = model_classification_report

        print(model_classification_report)

        ## Save the classification result
        #store_classification_result(model_name, language, model_classification_report, classification_results)


def data_classification(language, data, label, random_seed=config.RANDOM_SEED, job_num=multiprocessing.cpu_count()):
    """
    Trains the classifier
    :param language: programming language
    :param data: input data
    :param label: input labels
    :param random_seed: the random_seed
    :param job_num: the number of cores to use
    """

    # CV
    inner_cv = KFold(n_splits=config.FOLD_NUM, shuffle=True, random_state=random_seed)
    outer_cv = KFold(n_splits=config.FOLD_NUM, shuffle=True, random_state=random_seed)

    # Hyper-parameters
    tree_param = {'min_samples_leaf': config.MIN_SAMPLE_LEAVES, 'min_samples_split': config.MIN_SAMPLE_SPLIT,
                  'max_depth': config.TREE_MAX_DEPTH}
    forest_param = {'n_estimators': config.ESTIMATOR_NUM, 'min_samples_leaf': config.MIN_SAMPLE_LEAVES,
                    'min_samples_split': config.MIN_SAMPLE_SPLIT}
    boosting_param = {'n_estimators': config.ESTIMATOR_NUM, 'learning_rate': config.LEARNING_RATE}

    # Grid search definition
    grid_searches = [
        GridSearchCV(DecisionTreeClassifier(class_weight='balanced', random_state = random_seed),
                  tree_param, cv=inner_cv, n_jobs=job_num, scoring=config.SCORING_FUNCTION),
        GridSearchCV(RandomForestClassifier(class_weight='balanced', n_jobs=job_num, random_state = random_seed),
                     forest_param, cv=inner_cv, n_jobs=job_num, scoring=config.SCORING_FUNCTION),
        GridSearchCV(ExtraTreesClassifier(n_jobs=job_num, class_weight='balanced', random_state = random_seed),
                     forest_param, cv=inner_cv, n_jobs=job_num, scoring=config.SCORING_FUNCTION),
        GridSearchCV(AdaBoostClassifier(base_estimator=DecisionTreeClassifier(class_weight = 'balanced',
                                                                                random_state = random_seed,
                                                                                max_depth=2),
                                        algorithm='SAMME.R', random_state=random_seed),
                     boosting_param, cv=inner_cv, n_jobs=job_num, scoring=config.SCORING_FUNCTION)
        ]

    # Fitting the classifiers
    classification_results = {}
    for model in grid_searches:

        # Model training/testing
        model.score_sample_weight = True
        model.fit(data, label)
        model_name = str(type(model.best_estimator_)).replace('<class \'', '').replace('\'>', '').split('.')[-1]
        model_best_param = model.best_params_
        predicted_label = cross_val_predict(model.best_estimator_, X=data, y=label, cv=outer_cv, n_jobs=job_num)
        model_accuracy = accuracy_score(label, predicted_label)
        model_confusion_matrix = confusion_matrix(label, predicted_label)
        model_classification_report = classification_report(label, predicted_label)
        classification_results[model_name] = {}
        classification_results[model_name]['best_params'] = model_best_param
        classification_results[model_name]['accuracy'] = model_accuracy
        classification_results[model_name]['confusion_matrix'] = model_confusion_matrix.tolist()
        classification_results[model_name]['classification_report'] = model_classification_report

        print(model_classification_report)

        ## Save the classification result
        #store_classification_result(model_name, language, model_classification_report, classification_results)


def get_best_decision_tree(data, label, random_seed=config.RANDOM_SEED, job_num=multiprocessing.cpu_count()):
    """
    Trains the best decision tree
    :param data: the data
    :param label: the labels
    :param random_seed: the random seed
    :param job_num:
    :return: the number of cores to use
    """
    # CV
    inner_cv = KFold(n_splits=config.FOLD_NUM, shuffle=True, random_state=random_seed)

    # Train/test
    tree_param = {'min_samples_leaf': config.MIN_SAMPLE_LEAVES, 'min_samples_split': config.MIN_SAMPLE_SPLIT,
                  'max_depth': config.TREE_MAX_DEPTH}
    grid_search = GridSearchCV(DecisionTreeClassifier(class_weight='balanced', random_state=random_seed),
                               tree_param, cv=inner_cv, n_jobs=job_num, scoring=config.SCORING_FUNCTION)
    grid_search.score_sample_weight = True
    grid_search.fit(data, label)
    return grid_search.best_estimator_


def get_feature_importance_by_model(model):
    """
    Returns the features importance of a model
    :param model: the classifier
    :return: The list of feature importance
    """
    return model.feature_importances_


def get_feature_set(data):
    """
    Returns the feature sets separately
    :param data: The input data
    """
    # Data separation of feature sets
    parallel_changes = data[:, 0].reshape(-1, 1)
    commit_num = data[:, 1].reshape(-1, 1)
    commit_density = data[:, 2].reshape(-1, 1)
    file_edits = IncrementalPCA(n_components=1).fit_transform(data[:, 3:8])
    line_edits = IncrementalPCA(n_components=1).fit_transform(data[:, 8:10])
    dev_num = data[:, 10].reshape(-1, 1)
    keywords = IncrementalPCA(n_components=1).fit_transform(data[:, 11:23])
    message = IncrementalPCA(n_components=1).fit_transform(data[:, 23:27])
    duration = data[:, 27].reshape(-1, 1)

    feature_sets = ['prl_changes', 'commit_num', 'commit_density', 'file_edits', 'line_edits', 'dev_num',
                    'keywords', 'message', 'duration']

    return feature_sets, parallel_changes, commit_num, commit_density, file_edits, line_edits, dev_num, keywords\
        , message, duration


def save_feature_correlation(language, data, label):
    """
    Store the feature correlation of the data with the label
    :param language: the programming language
    :param data: the data
    :param label: the label
    """
    feature_sets, parallel_changes, commit_num, commit_density, file_edits, line_edits, dev_num, keywords, message\
        , duration = get_feature_set(data)
    features = [parallel_changes, commit_num, commit_density, file_edits, line_edits, dev_num, keywords, message
        , duration]
    for i, feature in enumerate(features):
        corr, p_value = spearmanr(feature, label)
        open('{}feature_correlation_{}.txt'.format(config.PREDICTION_RESULT_PATH, language), 'a') \
            .write('{}:\t\t{} \t {}\n'.format(feature_sets[i], round(corr, 2), round(p_value, 2)))


def save_feature_importance(language, data, label):
    """
    Store the feature importance
    :param language: the programming language
    :param data: the data
    :param label: the label
    """
    feature_sets, parallel_changes, commit_num, commit_density, file_edits, line_edits, dev_num, keywords, message, duration \
        = get_feature_set(data)

    feature_data = np.concatenate((parallel_changes, commit_num, commit_density, file_edits, line_edits,
                                   dev_num, keywords, message, duration), axis=1)
    feature_importances = get_feature_importance_by_model(get_best_decision_tree(feature_data, label))

    for i, item in enumerate(feature_importances):
        open('{}feature_importance_{}.txt'.format(config.PREDICTION_RESULT_PATH, language), 'a') \
            .write('{}:\t\t{}\n'.format(feature_sets[i], round(item, 2)))


def baseline_classification(language, data, label):
    """
    Classify the baseline data (parallel changed files)
    :param language: The programming language
    :param data: The data
    :param label: The labels
    """
    feature_sets, parallel_changes, commit_num, commit_density, file_edits, line_edits, dev_num, keywords, message \
        , duration = get_feature_set(data)
    language = language + '__baseline'
    data_classification(language, parallel_changes, label)


############################################
############################################




from sklearn import metrics
import autosklearn.classification
from sklearn.svm import SVC

def get_metrics(label_test, predicted_labels):
    result = {}
    result['accuracy_score'] = metrics.accuracy_score(label_test, predicted_labels)
    result['roc_curve'] = metrics.roc_curve(label_test, predicted_labels)
    result['roc_auc_score'] = metrics.roc_auc_score(label_test, predicted_labels)
    result['confusion_matrix'] = metrics.confusion_matrix(label_test, predicted_labels)
    result['precision_score'] = metrics.precision_score(label_test, predicted_labels)
    result['recall_score'] = metrics.recall_score(label_test, predicted_labels)
    result['average_precision_score'] = metrics.precision_score(label_test, predicted_labels, average='weighted')
    result['average_recall_score'] = metrics.recall_score(label_test, predicted_labels, average='weighted')
    result['f1_score'] = metrics.f1_score(label_test, predicted_labels, average='weighted')
    result['classification_report'] = metrics.classification_report(label_test, predicted_labels)
    print(result['classification_report'])
    print(result['confusion_matrix'])
    return result

def get_decision_tree_result(data_train, label_train, data_test, label_test):

    clf = DecisionTreeClassifier(class_weight='balanced').fit(data_train, label_train)
    predicted_labels = clf.predict(data_test)

    return get_metrics(label_test, predicted_labels)


def get_random_forest_result(data_train, label_train, data_test, label_test):
    clf = RandomForestClassifier(class_weight='balanced').fit(data_train, label_train)
    predicted_labels = clf.predict(data_test)

    return get_metrics(label_test, predicted_labels)

def get_svm_result(data_train, label_train, data_test, label_test):
    clf = SVC(C=1.0, kernel='linear', class_weight='balanced').fit(data_train, label_train)
    predicted_labels = clf.predict(data_test)

    return get_metrics(label_test, predicted_labels)

def get_auto_scikit_result(data_train, label_train, data_test, label_test):


    automl = autosklearn.classification.AutoSklearnClassifier(
        time_left_for_this_task= 60 * 60,
        per_run_time_limit=300,
        tmp_folder='/tmp/autosklearn_sequential_example_tmp1111',
        output_folder='/tmp/autosklearn_sequential_example_out1111',
    )
    automl.fit(data_train, label_train, metric=autosklearn.metrics.roc_auc)
    predicted_labels = automl.predict(data_test)
    result = get_metrics(label_test, predicted_labels)

    result['show_models'] = automl.show_models()
    result['sprint_statistics'] = automl.sprint_statistics()

    return result



if __name__ == "__main__":

    # Logging
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s in %(threadName)s - %(asctime)s by %(name)-12s :  %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S')
    logging.info('Train/test of merge conflict prediction')

    # Data classification

    data_files = glob.glob(config.PREDICTION_CSV_PATH + 'data_*')
    label_files = glob.glob(config.PREDICTION_CSV_PATH + 'label_*')

    lang_set = set([files.split('/')[-1].split('_')[2] for files in data_files])
    repos_set = set([files.split('/')[-1].split('_')[3].replace('.csv', '') for files in data_files])


    print(lang_set)
    print(repos_set)
    print(data_files)

    for data_path in data_files:

        data_tmp = pd.read_csv(data_path).sort_values(by=['merge_commit_date'])
        label_tmp = pd.read_csv(data_path.replace('data_prediction', 'label_prediction')).sort_values(by=['merge_commit_date'])

        data_tmp = data_tmp.drop('merge_commit_date', axis=1)
        label_tmp = label_tmp.drop('merge_commit_date', axis=1)

        train_ind = int(data_tmp.shape[0] * config.TRAIN_RATE)

        data_train = data_tmp.iloc[0:train_ind, :]
        data_test = data_tmp.iloc[train_ind:-1, :]

        label_train = label_tmp.iloc[0:train_ind, :]['is_conflict'].tolist()
        label_test = label_tmp.iloc[train_ind:-1, :]['is_conflict'].tolist()

        # if data_train.shape[0] < 50 or len(label_train) != len(label_test):
        #     continue


        # print(train_ind)

        # print(set(label_test))
        print(data_path)

        print(data_train.shape)
        print(data_test.shape)
        print(len(label_train))
        print(len(label_test))
        # exit()



        if len(set(label_test)) != 2 or len(set(label_train)) != 2 or len(label_test) != data_test.shape[0]:
            continue

        #
        get_decision_tree_result(data_train, label_train, data_test, label_test)
        # get_random_forest_result(data_train, label_train, data_test, label_test)
        #get_auto_scikit_result(data_train, label_train, data_test, label_test)
        #get_svm_result(data_train, label_train, data_test, label_test)

        # try:
        #     data_classification_wo_cv('language', data_train, label_train, data_test, label_test)
        # except:
        #     continue



        print(data_path)

        print('***********************************************')

