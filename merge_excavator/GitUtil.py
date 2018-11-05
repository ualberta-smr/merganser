
import os

import config
import validation


class GitUtil:
    """
    This class is a collection of methods that executes several useful native git commands.
    """

    def __init__(self, repository_name):
        """
        :param repository_name: The name of the repository in <USER_NAME>/<REPOSITORY_NAME> format
        """
        validation.validate_repository_name(repository_name)
        self.repository_name = repository_name
        self.repository_dir = config.REPOSITORY_PATH + self.repository_name.replace('/', '___')
        self.cd_to_repository = 'cd {};'.format(self.repository_dir)

    def get_merge_commits(self):
        """
        Returns the list of all merges' SHA-1 of the repository
        :return:  List of merge SHA-1
        """
        return os.popen(self.cd_to_repository + 'git log --all --pretty=%H --merges').read().split()

    def get_parents(self, commit):
        """
        Returns the parents of the merge scenario
        :param commit: The SHA-1 of the merge commit
        :return: Two parents as a list
        """
        return os.popen(self.cd_to_repository + 'git log --pretty=%P -n 1 {}'.format(commit)).read().split()

    def get_ancestor(self, parents):
        """
        Returns the ancestor SHA-1 of two parents in a merge scenario
        :param parents: The list of SHA-1 of parents
        :return: The ancestor of two parents
        """
        return os.popen(self.cd_to_repository + 'git merge-base {} {}'.format(parents[0], parents[1])).read().rstrip()

    def get_commit_date(self, commit):
        """
        Returns the local date of a commit
        :param commit: The SHA-1 of the commit
        :return: The date of the input commit
        """
        return ' '.join(os.popen(self.cd_to_repository + 'git show -s --format=%ci {}'.format(commit)).read().rstrip()
                        .split()[0:2])

    def get_parallel_changed_files_num(self, ancestor, parent1, parent2):
        """
        Returns the number of files that are changed in both parents in parallel
        :param ancestor: The ancestor SHA-1
        :param parent1: The parent 1 SHA-1
        :param parent2: The parent 2 SHA-1
        :return: The number of files that are changed in both parents in parallel
        """
        changes_ancestor_parent1 = set([item.strip() for item in os.popen(
            self.cd_to_repository + 'git diff --name-only {}..{}'.format(ancestor, parent1)).readlines()])
        changes_ancestor_parent2 = set([item.strip() for item in os.popen(
            self.cd_to_repository + 'git diff --name-only {}..{}'.format(ancestor, parent2)).readlines()])
        return len(changes_ancestor_parent1.intersection(changes_ancestor_parent2))

    def get_commit_message(self, commit): # TODO: replacing ',' with ' ' should be changed
        """
        Extracts the commit message of the given SHA-1
        :param commit: The SHA-1 of the commit
        :return: The commit message
        """
        return ''.join([i if ord(i) < 128 else ' ' for i in os.popen(self.cd_to_repository +
                                                                     'git log --pretty=format:"%s" -1  {}'
                                                    .format(commit)).read().rstrip()]).replace(',', ' ')

    def check_if_pull_request(self, commit):
        """
        Determine whether the commit was a pull request
        :param commit: The SHA-1 of the commit
        :return: 1 if the commit was a pull request, 0 otherwise
        """
        if 'Merge pull request' in self.get_commit_message(commit):
            return 1
        else:
            return 0

    def get_commit_list_between_two_commits(self, commit1, commit2):
        """
        Returns the list of commits between two commits
        :param commit1: The SHA-1 of the first commit
        :param commit2: The SHA-1 of the second commit
        :return: The list of commits between two given commits
        """
        return os.popen(self.cd_to_repository + 'git log --pretty=format:"%H" {}..{}'.format(commit1, commit2))\
            .readlines()

    def get_branch_of_commit(self, commit):
        """
        Returns the branch name of the given commit
        :param commit: The SHA-1 of the commit
        :return: The branch name
        """
        branches = [item for item in os.popen(self.cd_to_repository + 'git branch --contains  {}'.format(commit)).read()
            .split('\n') if '* (HEAD detached at' not in item]
        if branches == '':
            return 'None'
        else:
            return ','.join(branches) + '.'

    def get_changed_files_in_commit_type(self, commit, changeType):
        """
        Returns the number of the ChangeType (A, D, R, C, and M) in a commit
        :param commit: The SHA-1 of the commit
        :return: The number of changes
        """

        return max(0, len([line for line in os.popen(self.cd_to_repository + 'git show --oneline --numstat --diff-filter={}  {}'
                                 .format(changeType, commit)).readlines() if line != '\n']) - 1)

    def get_changed_files_in_commit(self, commit):
        """
        Returns a vector with size five consists the number of file changes (A, D, R, C, and M) in a commit
        :param commit1: The SHA-1 of the first commit
        :param commit2: The SHA-1 of the second commit
        :return: The file changes
        """
        types = ['A', 'D', 'R', 'C', 'M']
        return [self.get_changed_files_in_commit_type(commit, changeType)
                for changeType in types]

    def get_changed_files_between_two_commits_for_type(self, commit1, commit2, changeType):
        """
        Returns the number of the ChangeType (A, D, R, C, and M) between two commits
        :param commit1: The SHA-1 of the first commit
        :param commit2: The SHA-1 of the second commit
        :return: The number of the ChangeType
        """
        changed_files = os.popen(self.cd_to_repository + 'git diff --stat --diff-filter={} {}..{}'
                                 .format(changeType, commit1, commit2) +
                                 '|tr -s \' \'|awk \'{print $3}\'|awk \'{s+=$1} END {print s}\'').read().strip()
        if changed_files == '':
            return 0
        else:
            return changed_files

    def get_changed_files_between_two_commits(self, commit1, commit2):
        """
        Returns a vector with size five consists the number of file changes (A, D, R, C, and M) between two commits
        :param commit1: The SHA-1 of the first commit
        :param commit2: The SHA-1 of the second commit
        :return: The vector of five ChangeTypes
        """
        types = ['A', 'D', 'R', 'C', 'M']
        return [self.get_changed_files_between_two_commits_for_type(commit1, commit2, changeType)
                for changeType in types]

    def get_changed_lines_between_two_commits(self, commit1, commit2):
        """
        Returns a list which consists of all added and removed lines between two commits
        :param commit1: The SHA-1 of the first commit
        :param commit2: The SHA-1 of the second commit
        :return: The number of line changes
        """
        res = os.popen(self.cd_to_repository + 'git log {}..{}'.format(commit1, commit2) +
                       ' --numstat --pretty="%H"  | awk \'NF==3 {plus+=$1; minus+=$2} NF==1 {total++} END'
                       ' {printf(\"lines'
                       ' added: +%d\\nlines deleted: -%d\\ntotal commits: %d\\n\", plus, minus, total)}\'').readlines()
        added = res[0].split()[2][1:]
        deleted = res[1].split()[2][1:]
        return added, deleted

    def get_changed_lines_in_commit(self, commit):
        """
        Returns a list which consists of all added and removed lines in a commit
        :param commit1: The SHA-1 of the first commit
        :param commit2: The SHA-1 of the second commit
        :return: The number of line changes
        """
        res = os.popen(self.cd_to_repository + 'git show {}'.format(commit) +
                       ' --numstat --pretty="%H"  | awk \'NF==3 {plus+=$1; minus+=$2} NF==1 {total++} END'
                       ' {printf(\"lines'
                       ' added: +%d\\nlines deleted: -%d\\ntotal commits: %d\\n\", plus, minus, total)}\'').readlines()
        added = res[0].split()[2][1:]
        deleted = res[1].split()[2][1:]
        return added, deleted

    def get_develoeprs_num(self, commit1, commit2):
        """
        Returns the number of active developers between two commits
        :param commit1: The SHA-1 of the first commit
        :param commit2: The SHA-1 of the second commit
        :return: The number developers
        """
        return os.popen(self.cd_to_repository + 'git log {}..{} --format=\'%aN\' | sort -u|wc -l'
                       .format(commit1, commit2)).read().strip()
