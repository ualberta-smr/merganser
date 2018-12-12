SELECT
merge_scenario.merge_commit_hash as 'merge_commit',

repository.language,

merge_scenario.parallel_changed_file_num,

COUNT(commits.commit_hash) as 'commit_num',

SUM(commits.file_added_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'file_added',
SUM(commits.file_removed_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'file_removed',
SUM(commits.file_renamed_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'file_renamed',
SUM(commits.file_modified_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'file_modified',
SUM(commits.file_copied_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'file_copied',

SUM(commits.line_added_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'line_added',
SUM(commits.line_removed_num * ((2*(commits.merge_commit_parent -1 ))-1) )as 'line_removed',

merge_scenario.parent2_developer_num - merge_scenario.parent1_developer_num as 'developer_num',

TIMESTAMPDIFF(HOUR, merge_scenario.parent2_date, merge_scenario.parent1_date)  as 'duration'

FROM Merge_Data.Repository as repository
JOIN Merge_Data.Merge_Scenario as merge_scenario ON repository.id = merge_scenario.Repository_id
JOIN Merge_Data.Merge_Replay as merge_replay ON repository.id = merge_replay.Merge_Scenario_Repository_id AND merge_scenario.merge_commit_hash = merge_replay.Merge_Scenario_merge_commit_hash
JOIN Merge_Data.Merge_Related_Commit as commits ON repository.id = commits.Merge_Scenario_Repository_id and merge_scenario.merge_commit_hash = commits.Merge_Scenario_merge_commit_hash

-- where merge_scenario.parallel_changed_file_num > 0

GROUP BY merge_scenario.merge_commit_hash, merge_scenario.parallel_changed_file_num, merge_scenario.parent1_developer_num, merge_scenario.parent2_developer_num, merge_scenario.parent1_date, merge_scenario.parent2_date, merge_scenario. ancestor_date, repository.language
