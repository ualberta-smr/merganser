

import os

import config

cd_to_csv = 'cd {};'.format(config.TEMP_CSV_PATH)
table_list = ['Repository',
            'Merge_Replay',
            'Conflicting_File',
            'Conflicting_Region',
            'Merge_Scenario',
            'Code_style_violation',
            'Code_Complexity',
            'Merge_Related_Commit']

os.system('mysql -u {} -p < {}Merge_Data.sql'.format(config.DB_USER_NAME, config.QUERY_PATH))

for table in table_list:
    os.system(cd_to_csv + 'cat {}_* > {}.csv'.format(table, table))
    os.system(cd_to_csv + 'mysqlimport --fields-terminated-by=,  --verbose  --local'
              ' -u {} -p {}  {}.csv'.format(config.DB_USER_NAME, DB_NAME, table))
