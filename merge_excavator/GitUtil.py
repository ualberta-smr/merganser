
import os

import config

class GitUtil:

    def __init__(self, repository_name):
        self.repository_name = repository_name
        self.repository_dir = config.REPOSITORY_PATH + self.repository_name.replace('/', '___')
        self.cd_to_repository = 'cd {};'.format(self.repository_dir)

    def get_merge_commits(self):
        """
        Returns the list of all merge SHA-1
        :param   repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
        :return:  List of merge SHA-1
        """
        return os.popen(self.cd_to_repository + 'git log --all --pretty=%H --merges').read().split()

    def get_parents(self, commit):
        """
        Returns the parents in a merge scenario
        :param  repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
        commit: The SHA-1 of the merge commit
        :return:
        Two parents of the merge commit
        """
        return os.popen(self.cd_to_repository + 'git log --pretty=%P -n 1 {}'.format(commit)).read().split()

    def get_ancestor(self, parents):
        """
        Returns the ancestor of two parents in a merge scenario
        :param  repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
        parents: The list of SHA-1 od parents
        :return:
        The ancestor of two parents
        """
        return os.popen(self.cd_to_repository + 'git merge-base {} {}'.format(parents[0], parents[1])).read().rstrip()

    def get_commit_date(self, commit):
        """
        Returns the local date of a commit
        :param repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
        commit: The SHA-1 of the commit
        :return:
        The date of the input commit
        """
        return ' '.join(os.popen(self.cd_to_repository + 'git show -s --format=%ci {}'.format(commit)).read().rstrip()
                        .split()[0:2])

    def get_parallel_changed_files_num(self, ancestor, parent1, parent2):
        """
        Returns the number of files that are changed in both parents in parallel
        :param repository_name: The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
        :param ancestor: The ancestor SHA-1
        :param parent1: The parent 1 SHA-1
        :param parent2: The parent 2 SHA-1
        :return: The number of files that are changed in both parents in parallel
        """
        changes_ancestor_parent1 = set([item.strip() for item in os.popen(
            self.cd_to_repository + 'git diff --name-only {} {}'.format(ancestor, parent1)).readlines()])
        changes_ancestor_parent2 = set([item.strip() for item in os.popen(
            self.cd_to_repository + 'git diff --name-only {} {}'.format(ancestor, parent2)).readlines()])
        return len(changes_ancestor_parent1.intersection(changes_ancestor_parent2))

    def get_commit_message(self, commit):
        """
        Extracts the commit message of the given SHA-1
        :param repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
        :param commit: The SHA-1 of the commit
        :return: The commit message
        """
        return os.popen(self.cd_to_repository + 'git log --pretty=format:"%s" -1  {}'.format(commit)).read().rstrip()

    def check_if_pull_request(self, commit):
        """
        Determine whther the commit was a pull request
        :param repository_name:  The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
        :param commit: The SHA-1 of the commit
        :return: 1 if the commit was a pull request, 0 otherwise
        """
        if 'Merge pull request' in self.get_commit_message(self.repository_name, commit):
            return 1
        else:
            return 0

    def get_commit_list_between_two_commits(self, commit1, commit2):
        return os.popen(self.cd_to_repository + 'git log --pretty=format:"%H" {}..{}'.format(commit1, commit2))\
            .readlines()

    def get_branch_of_commit(self, commit):
        branches = [item for item in os.popen(self.cd_to_repository + 'git branch --contains  {}'.format(commit)).read()
            .split('\n') if '* (HEAD detached at' not in item]
        return branches[0].strip()

    def get_changed_files_between_two_commits_for_type(self, commit1, commit2, changeType):

        changed_files = os.popen(self.cd_to_repository + 'git diff --stat --diff-filter={} {}..{}'
                                 .format(changeType, commit1, commit2) +
                                 '|tr -s \' \'|awk \'{print $3}\'|awk \'{s+=$1} END {print s}\'').read().strip()
        if changed_files == '':
            return 0
        else:
            return changed_files

    def get_changed_files_between_two_commits(self, commit1, commit2):
        types = ['A', 'D', 'R', 'C', 'M']
        return [self.get_changed_files_between_two_commits_for_type(commit1, commit2, changeType)
                for changeType in types]

    def getChangedLineNumBetweenTwoCommits(self, commit1, commit2):
        res = os.popen(self.cd_to_repository + 'git log {}..{}'.format(commit1, commit2) +
                       ' --numstat --pretty="%H"  | awk \'NF==3 {plus+=$1; minus+=$2} NF==1 {total++} END'
                       ' {printf(\"lines'
                       ' added: +%d\\nlines deleted: -%d\\ntotal commits: %d\\n\", plus, minus, total)}\'').readlines()
        added = res[0].split()[2][1:]
        deleted = res[1].split()[2][1:]
        return added, deleted