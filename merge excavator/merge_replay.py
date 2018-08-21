
import re
import time
import csv
from checksumdir import dirhash

import config
from code_quality import *


CONFLICT_PATTERN_CONTENT = re.compile('CONFLICT \\(((?:content|add\\/add))\\): Merge conflict in \"?([^\"]+)\"?')
CONFLICT_PATTERN_DELETE = re.compile('CONFLICT \\(((?:rename|modify)\\/delete)\\): \"?([^\"]+)\"? deleted in .+ and (?:renamed|modified) .+')
CONFLICT_PATTERN_RENAME_RENAME = re.compile('CONFLICT \\((rename\\/rename)\\): Rename \"?[^\"]+\"?->\"?([^\"]+)\"? in .+ [Rr]ename \"?[^\"]+\"?->\"?[^\"]+\"? in .+')
CONFLICT_PATTERN_RENAME_ADD = re.compile('CONFLICT \\((rename\\/add)\\): Rename \"?[^\"]+\"?->\"?([^\"]+)\"? in \\S+ \"?[^\"]+\"? added in .+')
CONFLICT_PATTERN_REGION = re.compile('\\@\\@\\@ \\-(\\d+),(\\d+) \\-(\\d+),(\\d+) \\+(\\d+),(\\d+) \\@\\@\\@[\\s\\S]*')


def merge_replay(repository_name, merge_technique, merge_commit, parents_commit, exec_compile, exec_tests,
                 exec_conflicting_file, exec_conflicting_region, exec_replay_comparison):

    repository_dir = repository_name.replace('/', '___')
    cd_to_repository = 'cd {};'.format(config.REPOSITORY_PATH + repository_dir)

    # Merge commit/replay comparison (1)
    if exec_replay_comparison:
        os.system(cd_to_repository + 'git checkout --quiet  ' + merge_commit)
        merge_commit_md5 = dirhash(config.REPOSITORY_PATH + repository_dir, 'md5')

    # Merge replay
    t0 = time.time()
    merge_output = os.popen(cd_to_repository + 'git checkout --quiet  ' + parents_commit[0] +
                            ';git merge --quiet --no-commit  ' + parents_commit[1]).readlines()
    execution_time = time.time() - t0
    if exec_replay_comparison:
        replay_md5 = dirhash(config.REPOSITORY_PATH + repository_dir, 'md5')

    # Detect conflicts
    merge_output_concat = ''.join(merge_output)
    if merge_output_concat.count('Automatic merge failed; fix conflicts and then commit the result.') > 0:
        is_conflict = 1
    else:
        is_conflict = 0

    # Compile the code
    if exec_compile:
        replay_can_compile = get_commit_quality(repository_name, -1, 'compile')
    else:
        replay_can_compile = -1

    # Test the code
    if exec_tests:
        replay_can_pass_test = get_commit_quality(repository_name, -1, 'test')
    else:
        replay_can_pass_test = -1

    # Merge commit/replay comparison (2)
    if merge_commit_md5 == replay_md5:
        replay_is_equal_to_merge_commit = 1
    else:
        replay_is_equal_to_merge_commit = 0

    # Store the merge replay information
    merge_replay_data = [merge_technique, is_conflict, replay_can_compile, replay_can_pass_test, execution_time]
    if exec_replay_comparison:
        merge_replay_data.append(replay_is_equal_to_merge_commit)
    csv_file = open(config.TEMP_CSV_PATH + 'Merge_Replay.csv', 'a')
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
    csv_writer.writerow(merge_replay_data)
    csv_file.close()

    # Conflicting files
    if exec_conflicting_file:
        for conflict_report_line in merge_output:
            if 'CONFLICT' in conflict_report_line:
                content_conflict_match = CONFLICT_PATTERN_CONTENT.match(conflict_report_line)
                delete_conflict_match = CONFLICT_PATTERN_DELETE.match(conflict_report_line)
                rename_conflict_match = CONFLICT_PATTERN_RENAME_RENAME.match(conflict_report_line)
                rename_add_conflict_match = CONFLICT_PATTERN_RENAME_ADD.match(conflict_report_line)

                if content_conflict_match:
                    conflict_type = content_conflict_match.group(1)
                    conflicting_file = content_conflict_match.group(2)
                elif delete_conflict_match:
                    conflict_type = delete_conflict_match.group(1)
                    conflicting_file = delete_conflict_match.group(2)
                elif rename_conflict_match:
                    conflict_type = rename_conflict_match.group(1)
                    conflicting_file = rename_conflict_match.group(2)
                elif rename_add_conflict_match:
                    conflict_type = rename_add_conflict_match.group(1)
                    conflicting_file = rename_add_conflict_match.group(2)

                # Store the merge replay information
                conflicting_file_data = [conflicting_file, conflict_type]
                csv_file = open(config.TEMP_CSV_PATH + 'Conflicting_File.csv', 'a')
                csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
                csv_writer.writerow(conflicting_file_data)
                csv_file.close()

    # Conflicting regions
    if exec_conflicting_region:
        diff_replay = os.popen(cd_to_repository + 'git diff -U0').readlines()
        if diff_replay != None:
            for index, diff_line in enumerate(diff_replay):
                if '--- ' in diff_line:
                    parent1_path = diff_line.split()[1]
                    parent2_path = diff_replay[index + 1].split()[1]
                    if '@@@ ' not in diff_replay[index + 2]:
                        continue
                    diff_conflict_match = CONFLICT_PATTERN_REGION.match(diff_replay[index + 2])
                    diff_parent1_start = diff_conflict_match.group(1)
                    diff_parent1_length = diff_conflict_match.group(2)
                    diff_parent2_start = diff_conflict_match.group(3)
                    diff_parent2_length = diff_conflict_match.group(4)

                    # Store the conflicting region information
                    conflicting_region_data = [parent1_path, parent2_path, diff_parent1_start, diff_parent1_length,
                                           diff_parent2_start, diff_parent2_length]
                    csv_file = open(config.TEMP_CSV_PATH + 'Conflicting_Region.csv', 'a')
                    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"')
                    csv_writer.writerow(conflicting_region_data)
                    csv_file.close()

    # Reset the repository
    os.system(cd_to_repository + 'git reset --quiet --hard')

