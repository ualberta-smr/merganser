
import github3
import argparse

import config


def search_repository(query, star_min, fork_min, language, sort_by, order_by):
    """
    Search GitHub repositories based on several criteria
    :param query: The terms that should be used for searching, such as 'database', 'java', etc.
    :param star_min: The minimum number of stars the the repositories should have
    :param fork_min: The minimum number of forks the the repositories should have
    :param language: The programming language of repositories
    :param sort_by: the feature that repositories should sort based on
    :param order_by: The ordering type, 'asc' or 'desc'
    :return: A list of repositories as a dictionary
    """
    return github3.search_repositories(query + ' stars:>' + star_min + ' forks:>' + fork_min + ' language:' + language,
                                       sort=sort_by, order=order_by, text_match=False, number=-1)


if __name__ == '__main__':
    """
    This module searches GitHub based on several criteria and store them as a list for the subsequence analysis. It also 
    print the list of repositories on the screen.
    """
    parser = argparse.ArgumentParser(description='Search for repositories by different criteria')
    parser.add_argument('-q', '--query', help='The query of searching', required=True)
    parser.add_argument('-s', '--star', help='The minimum number of stars', required=True)
    parser.add_argument('-f', '--fork', help='The minimum number of forks', required=True)
    parser.add_argument('-l', '--language', help='The language of repositories', required=True)
    parser.add_argument('-o', '--output', help='The name of the output file', required=True)
    args = vars(parser.parse_args())
    repository_list = search_repository(args['query'], args['star'], args['fork'], args['language'], 'stars', 'desc')
    output_file = open(config.REPOSITORY_LIST_PATH + args['output'] + '.txt', 'wt')
    for i in repository_list:
        output_file.write(str(i).split('[')[1].split(']')[0] + '\n')
        print(str(i).split('[')[1].split(']')[0])
    output_file.close()
