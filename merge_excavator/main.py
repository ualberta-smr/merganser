
from joblib import Parallel, delayed
import multiprocessing
import argparse
from extractMerges import *
from cloneProjects import *

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='The main script for analyzing merge scenarios')
	parser.add_argument('-r','--repository-list', help='The list of GitHub repositories', required = True)
	parser.add_argument('-m','--merge-method', help='The merge method ("uns", "strc", "at", and "semiStrc" for unstructured, structured, auto-tuning, and semi-structured)', required = True)	
	parser.add_argument('-c','--compile', help='This flags determine whether the repositories should compile', required = False)
	parser.add_argument('-t','--test', help='This flags determine whether the repositories should test', required = False)
	parser.add_argument('-fc','--file-compile', help='This flags determine whether the repositories should compile in file level', required = False)
	parser.add_argument('-s','--semantic-changes', help='This flags determine whether the semantics changes should be extracted', required = False)
	parser.add_argument('-sc','--save-conflicts', help='This flags determine whether the conflict regions should be stored', required = False)
	parser.add_argument('-f','--file-level', help='This flags determine whether the conflict in file-level should be stored', required = False)	
	parser.add_argument('-p','--extract-prediction', help='This flags determine whether the prediction features should be extracted', required = False)	


	args = vars(parser.parse_args())
	cloneProjects(args['repository_list'])
	num_cores = multiprocessing.cpu_count()
	reposURLs = open('../reposList/' + args['repository_list'] + 'List.txt', 'rt').readlines()
	userName = [i.split('/')[0].strip() for i in reposURLs]
	reposName = [i.split('/')[1].strip() for i in reposURLs]
	Parallel(n_jobs=num_cores)(delayed(extractMergingData)(reposURLs[i].rstrip(), userName[i].strip() +'___' + reposName[i].strip(), args['merge_method'], \
		args['compile'] != None, args['test'] != None, args['file_compile'] != None, args['semantic_changes'] != None, args['save_conflicts'] != None, args['file_level'] != None, args['extract_prediction'] != None) for i in range(len(reposURLs)))
saveConflicts