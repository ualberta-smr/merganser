SELECT
repository.name,
merge_scenario.merge_commit_date,
merge_scenario.merge_commit_hash as 'merge_commit'
FROM Merge_Data.Merge_Scenario as merge_scenario
JOIN Merge_Data.Repository as repository ON repository.id = merge_scenario.Repository_id
