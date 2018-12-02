
import os
import csv
import random

rep_list = []

# Download dataset
os.system('wget https://reporeapers.github.io/static/downloads/dataset.csv.gz -P ../tools/reaper')

with open('dataset.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if (row['language'].lower() == 'java' or row['language'].lower() == 'python' or row['language'].lower() == 'ruby' or row['language'].lower() == 'php' or row['language'].lower() == 'c++') and row['stars'] != 'None' and int(row['stars']) >= 100 and (row['randomforest_org'] == '1' or row['randomforest_utl'] == '1'):
        	rep_list.append(row['repository'])
random.shuffle(rep_list)
for item in rep_list:
	print(item)

#https://octoverse.github.com/
