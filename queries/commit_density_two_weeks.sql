SELECT merge_scenario.merge_commit_hash as 'merge_commit', count(Commits.commit_hash) as 'commit_density'
FROM Merge_Data.Merge_Scenario merge_scenario
LEFT JOIN Merge_Data.Merge_Related_Commit Commits
on merge_scenario.merge_commit_hash = Commits.Merge_Scenario_merge_commit_hash
AND Commits.merge_commit_parent = {}
AND TIMESTAMPDIFF(WEEK, merge_scenario.merge_commit_date, Commits.date) < 3
-- where merge_scenario.parallel_changed_file_num > 0
GROUP BY merge_scenario.merge_commit_hash;