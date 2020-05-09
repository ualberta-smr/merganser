
import os
import logging

from merganser.config import *


def insert_csv_to_mysql():
    """
    This method insert the temporary CSV files (from config.TEMP_CSV_PATH) into the MySQL database
    """

    # Logging
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s in %(threadName)s - %(asctime)s by %(name)-12s :  %(message)s',
                        datefmt='%y-%m-%d %H:%M:%S')

    cd_to_csv = 'cd {};'.format(TEMP_CSV_PATH)
    table_list = ['Repository',
                'Conflicting_File',
                'Conflicting_Region',
                'Merge_Scenario',
                'Merge_Replay',
                'Code_Style_Violation',
                'Code_Complexity',
                'Merge_Related_Commit']

    # Create tables
    os.system(f'mysql -u {DB_USER_NAME} --password={DB_PASSWORD} < {QUERY_PATH}Merge_Data.sql')

    # Insert the data
    os.system(f'{cd_to_csv}mkdir temp')
    for table in table_list:
        os.system(cd_to_csv + 'cat {}_*  | tr -d "\r" > ./temp/{}.csv'.format(table, table))
        os.system(f'{cd_to_csv}mysqlimport --fields-escaped-by=\'\\\' --fields-optionally-enclosed-by=\'\"\'  '
                  f'--fields-terminated-by="," --lines-terminated-by="\n"  '
                  f'--verbose  --local -u {DB_USER_NAME} --password={DB_PASSWORD} Merge_Data  ./temp/{table}.csv ')
    os.system(f'{cd_to_csv}rm -r temp')


if __name__ == '__main__':
    insert_csv_to_mysql()
    logging.info('The data conversion form CSV to MySQL was finished successfully. '
                 'The database and validate the insertions')
