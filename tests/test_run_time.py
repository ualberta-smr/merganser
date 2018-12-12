
import os
import unittest
import sys
sys.path.append('./merganser')
import pandas as pd

import config


class MyTest(unittest.TestCase):

    def test_check_if_paths_exist(self):
        os.system('./runPredict.sh samplemerge')
        self.assertTrue(os.path.exists(config.TEMP_CSV_PATH.replace('..', '.')))
        self.assertTrue(os.path.exists(config.TEMP_CSV_PATH.replace('..', '.')))
        self.assertTrue(os.path.exists(config.REPOSITORY_LIST_PATH.replace('..', '.')))
        self.assertTrue(os.path.exists(config.LOG_PATH.replace('..', '.')))
        self.assertTrue(os.path.exists(config.QUERY_PATH.replace('..', '.')))

    def test_check_repository_csv_file(self):
        os.system('./runPredict.sh samplemerge')
        df = pd.read_csv(config.TEMP_CSV_PATH.replace('..', '.') + 'Repository_owhadi___sample-merge.csv', header=None)
        self.assertEqual(df.values[0][0], 156289982)
        self.assertEqual(df.values[0][-1], 1)
        self.assertEqual(df.values[0][-2], 2)

    def test_check_merge_scenario_csv_file(self):
        os.system('./runPredict.sh samplemerge')
        df = pd.read_csv(config.TEMP_CSV_PATH.replace('..', '.') + 'Merge_Scenario_owhadi___sample-merge.csv', header=None)
        self.assertEqual(df.values[0][0], '18a168ea05b242d61f51cf1b51ac98feb205e337')
        self.assertEqual(df.values[0][-1], 156289982)
        self.assertEqual(df.values[0][-2], 0)

    def test_check_merge_replay_csv_file(self):
        os.system('./runPredict.sh samplemerge')
        df = pd.read_csv(config.TEMP_CSV_PATH.replace('..', '.') + 'Merge_Replay_owhadi___sample-merge.csv', header=None)
        self.assertEqual(df.values[0][1], 1)
        self.assertEqual(df.values[0][-1], 156289982)
        self.assertEqual(df.values[0][-2], '18a168ea05b242d61f51cf1b51ac98feb205e337')

    def test_check_merge_related_commit_csv_file(self):
        os.system('./runPredict.sh samplemerge')
        df = pd.read_csv(config.TEMP_CSV_PATH.replace('..', '.') + 'Merge_Related_Commit_owhadi___sample-merge.csv', header=None)
        self.assertEqual(df.values[1][0], '3619eb024f00aa9d4e753df4d76784ec0209315a')
        self.assertEqual(df.values[1][-1], 156289982)
        self.assertEqual(df.values[1][-2], '18a168ea05b242d61f51cf1b51ac98feb205e337')


if __name__ == '__main__':
    unittest.main(verbosity=2)
