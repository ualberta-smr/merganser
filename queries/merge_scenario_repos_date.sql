SELECT
repository.name,
merge_scenario.merge_commit_date

FROM Merge_Data.Merge_Scenario as merge_scenario
JOIN Merge_Data.Repository as repository ON repository.id = merge_scenario.Repository_id

where merge_scenario.parallel_changed_file_num > 0

-- Shouldn't be required
-- GROUP BY merge_scenario.merge_commit_hash, merge_replay.is_conflict, repository.language
