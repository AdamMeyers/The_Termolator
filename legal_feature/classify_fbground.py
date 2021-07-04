import textacy.datasets
import json


def add_to_dict(dict, issue, case_number):
    if issue not in dict:
        dict[issue] = []
    dict[issue].append(case_number)


ds = textacy.datasets.SupremeCourt()
ds.download()

i = 1
case_name_to_number = {}
broad_issue_to_cases = {}
narrow_issue_to_cases = {}


for text, meta in ds.records():
    f = open(f'cases/{i}.txt', 'w')
    f.write(text)
    f.close()

    add_to_dict(broad_issue_to_cases, meta["issue_area"], i)
    add_to_dict(narrow_issue_to_cases, meta["issue"], i)

    i += 1

with open('broadissues.json', 'w') as fp:
    json.dump(broad_issue_to_cases, fp)
with open('narrowissues.json', 'w') as fp:
    json.dump(narrow_issue_to_cases, fp)
