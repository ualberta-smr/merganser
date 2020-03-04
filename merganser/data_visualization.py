
import os
import glob

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import config
from util import *
from data_retrieval import *

repo_lang = Repository_language()
data_ret = Data_Retreival()

os.system('mkdir -p {}'.format(config.PREDICTION_RES_PATH))

metric_list = ['precision_score_not_conflict', 'recall_score_not_conflict', 'f1_score_not_conflict'
    , 'precision_score_conflict', 'recall_score_conflict', 'f1_score_conflict', 'precision_score_average', 'recall_score_average', 'f1_score_average', 'roc_auc_score']

classifier_list = ['DecisionTreeClassifier', 'RandomForestClassifier']

items_results = ['P(NC)',  'R(NC)', 'F1(NC)', 'P(C)'
    , 'R(C)', 'F1(C)', 'P(A)', 'R(A)', 'F1(A)', 'AUC-ROC']

def remove_min_max(inp_list, k=0.05):
    k = int(k * len(inp_list))
    for i in range(k):
        inp_list.remove(max(inp_list))
        inp_list.remove(min(inp_list))
    return inp_list

def plt_single_violin(data, title, file_name):
    plt.violinplot(data, showmeans=False, showmedians=True)
    plt.title(title)
    plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        labelbottom=False) # labels along the bottom edge are off)
    plt.savefig(config.PREDICTION_RES_PATH + file_name, format='pdf')



def plt_violin_items(data, title, xlabel, ylabel, file_name, items, rotation='horizontal'):
    
    if rotation == 'horizontal':
        items = [''] + items

    x_pos = [i for i, _ in enumerate(items)] 

    if rotation != 'horizontal':
        items = [''] + items
        x_pos = x_pos + [10]
        axes = plt.gca()
        axes.set_ylim([0.0,1.05])
        axes.xaxis.grid()
        axes.yaxis.grid()

    plt.violinplot(data, showmeans=False, showmedians=True)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x_pos, items, rotation=rotation)
    
    plt.savefig(config.PREDICTION_RES_PATH + file_name, format='pdf', bbox_inches='tight')
    plt.clf()


def plt_bar_langs(data, title, xlabel, ylabel, file_name):
    x_pos = [i for i, _ in enumerate(config.LANGUAGES)]
    plt.bar(x_pos, data)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x_pos, config.LANGUAGES)
    plt.savefig(config.PREDICTION_RES_PATH + file_name, format='pdf')
    plt.clf()

# # Correlation
# corr_df = pd.read_csv('corr.csv')
# corr_df = corr_df.drop('repository', axis = 1)
# corr_agg_df = corr_df.groupby('langugae').agg('median')
# corr_agg_df.to_csv('corr_agg_df.csv')
# exit()

def get_aggregated_results():

    res_files = glob.glob('res_*.csv')
    classification_result_df_list = []
    res_val = np.zeros((14, 6))

    for res_file in res_files:

        result_df = pd.read_csv(res_file)
        

        classification_result_list = []

        for lang in config.LANGUAGES:
            res_lang_df = result_df[result_df['language'] == lang] 
            for classifier in classifier_list:
                res_df = res_lang_df[res_lang_df['model_name'] == classifier]
                classification_result_list.append(
                    {
                        'item': f'{classifier}_{lang}'
                        , 'precision (not conflcit)': np.median(res_df.precision_score_not_conflict)
                        , 'recall (not conflcit)': np.median(res_df.recall_score_not_conflict)
                        , 'F1 (not conflcit)': np.median(res_df.f1_score_not_conflict)
                        , 'precision (conflcit)': np.median(res_df.precision_score_conflict)
                        , 'recall (conflcit)': np.median(res_df.recall_score_conflict)
                        , 'F1 (conflcit)': np.median(res_df.f1_score_conflict)
                    }
                )
        temp_df = pd.DataFrame(classification_result_list)
        res_val = res_val + temp_df.iloc[0:, 1:]
        classification_result_df_list.append(temp_df)
        temp_df.to_csv(res_file.replace('res_', 'result_summary_'))

    res_val = res_val / len(classification_result_df_list)
    res_agg = pd.DataFrame()
    res_agg['item'] = classification_result_df_list[0]['item']
    res_agg = pd.concat([res_agg, res_val], axis=1, sort=False)
    res_agg.to_csv('res_summary_aggregated.csv')





    
get_aggregated_results()

exit()

# Basic stats
result_df = pd.read_csv('res.csv')
classification_result_df_list = []

classification_result_list = []
for lang in config.LANGUAGES:
    res_lang_df = result_df[result_df['language'] == lang] 
    print(f'>>>>>>>> language: {lang}')
    for classifier in classifier_list:

        print(f'>>>> classifier: {classifier}')

        res_df = res_lang_df[res_lang_df['model_name'] == classifier]

        repository_list = list(set(res_df['repository'].tolist()))
        language_list = list(set(res_df['language'].tolist()))
        conflict_rate_list = res_df['conflict_rate'].tolist()
        roc_auc_list =  res_df['roc_auc_score'].tolist()

        print('****')
        # print(f'The number of repositories: {len(repository_list)}')
        # print(f'The number of languages: {len(language_list)}')
        # print(f'The list of languages: {language_list}')
        # print('****')

        # print(f'The min of conflict rate: {np.min(conflict_rate_list):0.2f}')
        # print(f'The median of conflict rate: {np.median(conflict_rate_list):0.2f}')
        # print(f'The max of conflict rate: {np.max(conflict_rate_list):0.2f}')
        # print('****')

        # print(f'The median of AUC-ROC: {np.median(roc_auc_list):0.2f}')
        # print(f'The median of average recall: {np.median(res_df.recall_score_average):0.2f}')
        # print(f'The median of average precision: {np.median(res_df.precision_score_average):0.2f}')
        # print(f'The median of average F1: {np.median(res_df.f1_score_average):0.2f}')
        # print('****')

        print(f'The median of recall (conflcit): {np.median(res_df.recall_score_conflict):0.2f}')
        print(f'The median of precision (conflcit): {np.median(res_df.precision_score_conflict):0.2f}')
        print(f'The median of F1 (conflcit): {np.median(res_df.f1_score_conflict):0.2f}')
        print('****')

        print(f'The median of recall (not conflcit): {np.median(res_df.recall_score_not_conflict):0.2f}')
        print(f'The median of precision (not conflcit): {np.median(res_df.precision_score_not_conflict):0.2f}')
        print(f'The median of F1 (not conflcit): {np.median(res_df.f1_score_not_conflict):0.2f}')
        print('****')


        # classification_result_dict[f'{classifier}_{lang}'] = [np.median(res_df.recall_score_not_conflict)
        #                                                     , np.median(res_df.recall_score_not_conflict)
        #                                                     , np.median(res_df.f1_score_not_conflict)
        #                                                     , np.median(res_df.precision_score_conflict)
        #                                                     , np.median(res_df.recall_score_conflict)
        #                                                     ,  np.median(res_df.f1_score_conflict)]
        classification_result_list.append(
            {
                'item': f'{classifier}_{lang}'
                , 'precision (not conflcit)': np.median(res_df.precision_score_not_conflict)
                , 'recall (not conflcit)': np.median(res_df.recall_score_not_conflict)
                , 'F1 (not conflcit)': np.median(res_df.f1_score_not_conflict)
                , 'precision (conflcit)': np.median(res_df.precision_score_conflict)
                , 'recall (conflcit)': np.median(res_df.recall_score_conflict)
                , 'F1 (conflcit)': np.median(res_df.f1_score_conflict)
            }
        )

# print(classification_result_dict)
classification_result_df_list.append(pd.DataFrame(classification_result_list))
# print('****')
# print('The statistics of repositories:')
# print(data_ret.get_repository_stats())
# print('****')


# lang_stats = {}

# for lang in config.LANGUAGES:
#     stats = {}
#     # stats['merge_num'] = np.array([i[0] for i in data_ret.get_scenarios_nums_by_lang(lang).values])
#     # stats['conflict_num'] = np.array([i[0] for i in data_ret.get_conflicts_nums_by_lang(lang).values])
#     stats['star_num'] = np.array([i[0] for i in data_ret.get_star_nums_by_lang(lang).values])
#     # stats['conflict_rate'] = 100 * stats['conflict_num'] / stats['merge_num']
#     # stats['repos_num'] = len(stats['merge_num'])
#     lang_stats[lang] = stats

# # Bar plot: star num num per lang
# t = []
# for lang in config.LANGUAGES:
#     t.append(lang_stats[lang]['star_num'])
# plt_violin_items(t, title='', xlabel='Programming Languages', ylabel='Number of Stars', file_name='num_star_per_lang', items=config.LANGUAGES)
# exit()

# # Bar plot: repos num per lang
# t = []
# for lang in config.LANGUAGES:
#     t.append(lang_stats[lang]['repos_num'])
# plt_bar_langs(t, title='', xlabel='Programming Languages', ylabel='Number of Repositories', file_name='num_repos_per_lang')


# # Violin plot: merge distribution
# t = []
# for lang in config.LANGUAGES:
#     t.append(lang_stats[lang]['merge_num'])
# plt_violin_items(t, title='', xlabel='Programming Languages', ylabel='Number of Merge Scenarios', file_name='dist_merges_per_lang', items=config.LANGUAGES)

# # Violin plot: conflict distribution
# t = []
# for lang in config.LANGUAGES:
#     t.append(lang_stats[lang]['conflict_num'])
# plt_violin_items(t, title='', xlabel='Programming Languages', ylabel='Number of Merge Conflicts', file_name='dist_conflicts_per_lang', items=config.LANGUAGES)

# # Violin plot: conflict rate distribution
# t = []
# for lang in config.LANGUAGES:
#     t.append(lang_stats[lang]['conflict_rate'])
# plt_violin_items(t, title='', xlabel='Programming Languages', ylabel='Rate of Merge Conflicts', file_name='dist_conflicts_rate_per_lang', items=config.LANGUAGES)

# # Feature Importance
# importance_df = pd.read_csv('feature_importance_summery.csv')
# print(f'The feature importance:')
# print(importance_df)
# print('****')
# print(f'The mean of feature importance for different programming languages:')
# print(importance_df.mean(axis=0))
# print('****')

# Prediction results

# for classifier in classifier_list:
#     temp_df = result_df[result_df['model_name'] == classifier]
#     res_list = []
#     for metric in metric_list:
#         res_list.append((temp_df[metric].tolist()))
#     plt_violin_items(res_list, title='', xlabel='Evaluation Metrics', ylabel='', file_name=f'res_overal_{classifier}', items=items_results, rotation=45.0)

# res_df = result_df[result_df['model_name'] == 'RandomForestClassifier']

# for lang in config.LANGUAGES:
#     temp_df = res_df[res_df['language'] == lang]   
#     res_list = []
#     for metric in metric_list:
#         res_list.append((temp_df[metric].tolist()))
#     plt_violin_items(res_list, title='', xlabel='Evaluation Metrics', ylabel='', file_name=f'res_{lang}_', items=items_results, rotation=45.0)

