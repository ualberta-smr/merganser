SELECT
merge_scenario.merge_commit_hash as 'merge_commit',
repository.language,
merge_replay.is_conflict as 'is_conflict'

FROM Merge_Data.Merge_Scenario as merge_scenario
JOIN Merge_Data.Merge_Replay as merge_replay ON  merge_scenario.merge_commit_hash = merge_replay.Merge_Scenario_merge_commit_hash
JOIN Merge_Data.Repository as repository ON repository.id = merge_scenario.Repository_id

-- where merge_scenario.parallel_changed_file_num > 0

GROUP BY merge_scenario.merge_commit_hash, merge_replay.is_conflict, repository.language