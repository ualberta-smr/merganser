SELECT merge_commit_hash as 'merge_commit', LOWER(GROUP_CONCAT(message SEPARATOR ' ||| ')) as 'commit_messages'
FROM Merge_Data.Merge_Scenario
JOIN Merge_Data.Merge_Related_Commit
on merge_commit_hash = Merge_Scenario_merge_commit_hash
-- where parallel_changed_file_num > 0
GROUP BY merge_commit_hash;