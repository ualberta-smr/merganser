

import numpy as np
import json
import pandas as pd


from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV, cross_val_score, KFold
from sklearn.model_selection import cross_val_predict

from imblearn.over_sampling import RandomOverSampler
from imblearn.over_sampling import SMOTE, ADASYN
from imblearn.combine import SMOTETomek
from imblearn.under_sampling import ClusterCentroids
from imblearn.over_sampling import SMOTE


import multiprocessing


import config
#from visualization import *


def binaryDataClassification(data, label, random_seed=0,
                             job_num=multiprocessing.cpu_count()):

    # CV
    inner_cv = KFold(n_splits=config.FOLD_NUM, shuffle=True, random_state=random_seed)
    outer_cv = KFold(n_splits=config.FOLD_NUM, shuffle=True, random_state=random_seed)

    # Hyper-parameters
    tree_param = {'min_samples_leaf': config.MIN_SAMPLE_LEAFES, 'min_samples_split': config.MIN_SAMPLE_SPLIT,
                  'max_depth': config.TREE_MAX_DEPTH}
    forest_param = {'n_estimators': config.ESTIMATOR_NUM, 'min_samples_leaf': config.MIN_SAMPLE_LEAFES,
                    'min_samples_split': config.MIN_SAMPLE_SPLIT}
    boosting_param = {'n_estimators': config.ESTIMATOR_NUM, 'learning_rate': config.LEARNING_RATE}

    # Grid search definition
    grid_searches = [
        # GridSearchCV(DecisionTreeClassifier(class_weight = 'balanced',random_state = random_seed),
        #           tree_param, cv=inner_cv, n_jobs = job_num, scoring = config.SCORING_FUNCTION),
        GridSearchCV(RandomForestClassifier(class_weight = 'balanced',n_jobs = job_num, random_state = random_seed),
                     forest_param, cv=inner_cv, n_jobs = job_num, scoring = config.SCORING_FUNCTION),
        GridSearchCV(ExtraTreesClassifier(n_jobs = job_num, class_weight='balanced', random_state = random_seed),
                     forest_param, cv=inner_cv, n_jobs = job_num, scoring = config.SCORING_FUNCTION),
        GridSearchCV(AdaBoostClassifier(base_estimator=DecisionTreeClassifier(class_weight = 'balanced',
                                                                                random_state = random_seed,
                                                                                max_depth=2),
                                        algorithm='SAMME.R', random_state = random_seed),
                     boosting_param, cv=inner_cv, n_jobs=job_num, scoring=config.SCORING_FUNCTION)
        ]



    # Fitting the classifiers
    classification_results = {}
    for model in grid_searches:

        # Model training
        model.score_sample_weight=True
        model.fit(data, label)
        model_name = str(type(model.best_estimator_)).replace('<class \'', '').replace('\'>', '').split('.')[-1]
        model_best_param = model.best_params_

        predicted_label = cross_val_predict(model.best_estimator_, X=data, y=label, cv=outer_cv, n_jobs=job_num)

        model_accuray = accuracy_score(label, predicted_label)
        model_confusion_matrix = confusion_matrix(label, predicted_label)
        model_classification_report = classification_report(label, predicted_label)
        classification_results[model_name] = {}
        classification_results[model_name]['best_params'] = model_best_param
        classification_results[model_name]['accuracy'] = model_accuray
        classification_results[model_name]['confusion_matrix'] = model_confusion_matrix.tolist()
        classification_results[model_name]['classification_report'] = model_classification_report
        print(model_classification_report)
        importances = model.best_estimator_.feature_importances_
        std = np.std([tree.feature_importances_ for tree in model.best_estimator_.estimators_],  axis=0)
        indices = np.argsort(importances)[::-1]
        print("Feature ranking:")
        for f in range(data.shape[1]):
                print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

    return classification_results

def getBalanceData(data, label):
    return SMOTE(ratio='minority').fit_sample(data, label)


def data_classification(data_raw, label_raw):
    data_train, data_test, label_train, label_test = train_test_split(data_raw, label_raw, test_size=config.TEST_SIZE,
                                                        random_state=config.RANDOM_SEED)
    #data_train, label_train = getBalanceData(data_train, label_train)
    return binaryDataClassification(data_train, label_train, data_test, label_test, random_seed=config.RANDOM_SEED,
                             job_num=multiprocessing.cpu_count())


post_name = ['_CPP','_java', '_PHP', '_Python', '_Ruby']
post_name = '_All2'



for test in post_name:
    print('RUN: {}'.format(test))
    # Read data
    data = pd.read_csv(config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_DATA_NAME + post_name, delimiter=',').values[:,1:]
    label = pd.read_csv(config.PREDICTION_CSV_PATH + config.PREDICTION_CSV_LABEL_NAME + post_name, delimiter=',').values[:,1]




    #vis_TSNE(data,label)
    binaryDataClassification(data, label)
    #data_classification(data, label)
