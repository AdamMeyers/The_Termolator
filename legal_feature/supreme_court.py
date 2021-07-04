import textacy.datasets
import os
ds = textacy.datasets.SupremeCourt()
ds.download()
print(ds.info)

filenames = {}
number = 0

if not os.path.isdir('cases'):
    os.mkdir('cases')
os.chdir('cases')

for text, meta in ds.records():
    file_number = str(number)+'.txt'
    casename = meta["case_name"]+' '+meta["decision_date"]
    filenames[file_number] = casename
    number += 1
    with open(file_number, 'w') as outstream:
        outstream.write(text)

with open('file_list.tsv', 'w') as outstream:
    files = list(filenames.keys())
    files.sort()
    for f in files:
        outstream.write(str(f) + '\t' + filenames[f])

os.chdir('..')
