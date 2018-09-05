

import os

import config

cd_to_csv = 'cd {};'.format(config.TEMP_CSV_PATH)
table_list = ['Repository',
            'Conflicting_File',
            'Conflicting_Region',
            'Merge_Scenario',
            'Merge_Replay',
            'Code_Style_Violation',
            'Code_Complexity',
            'Merge_Related_Commit']

# Create tables
os.system('mysql -u {} < {}Merge_Data.sql'.format(config.DB_USER_NAME, config.QUERY_PATH))

os.system(cd_to_csv + 'mkdir temp')
for table in table_list:
    os.system(cd_to_csv + 'cat {}_*  | tr -d "\r" > ./temp/{}.csv'.format(table, table))
    os.system(cd_to_csv + 'mysqlimport  --fields-escaped-by='' --fields-terminated-by="," --lines-terminated-by="\n"  '
                          '--verbose  --local -u root Merge_Data  ./temp/{}.csv '.format(table))
os.system(cd_to_csv + 'rm -r temp')


