
import github3
import argparse

import config


def search_repository(query, star_min, fork_min, language, sort_by, order_by):
    """
    This method search for repositories using GitHub APIs. Read README.md for more information.
    """
    return github3.search_repositories(query + ' stars:>' + star_min + ' forks:>' + fork_min + ' language:' + language,
                                       sort = sort_by, order = order_by, text_match=False, number=-1)


if __name__ == '__main__':
    """
    The main code for searching repositories
    """
    parser = argparse.ArgumentParser(description='Search for repositories by different criteria')
    parser.add_argument('-q', '--query', help='The query of searching', required = True)
    parser.add_argument('-s', '--star', help='The minimum number of stars', required = True)
    parser.add_argument('-f', '--fork', help='The minimum number of forks', required = True)
    parser.add_argument('-l', '--language', help='The language of repositories', required = True)
    parser.add_argument('-o', '--output', help='The name of the output file', required = True)
    args = vars(parser.parse_args())
    repository_list = search_repository(args['query'], args['star'], args['fork'], args['language'], 'stars', 'desc')
    output_file = open(config.REPOSITORY_LIST_PATH + args['output'] + '.txt', 'wt')
    for i in repository_list:
        output_file.write(str(i).split('[')[1].split(']')[0] + '\n')
    output_file.close()
