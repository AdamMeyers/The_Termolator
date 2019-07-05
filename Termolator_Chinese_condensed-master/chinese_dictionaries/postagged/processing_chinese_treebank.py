import re
import os

def stripxml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

noun_dict = {}
verb_dict = {}
overlap_dict = {}

def extract_chunk(file):
    with open(file) as inFile: 
        data = inFile.read()
        processed_data = stripxml(data)
        processed_data = re.findall(r'.*?_.*',processed_data)
        str_processed_data = ''.join(processed_data)
        list_processed_data = str_processed_data.split()
    #    processed_data = [x.split() for x in str_processed_data]
    #    print(processed_data)

    #add noun and verbs to dictionary
    for chunk in list_processed_data:
        chunk = chunk.split("_")
        if (chunk[1] == 'NN' or chunk[1] == "NR"):
            if (chunk[0] not in noun_dict):
                noun_dict[chunk[0]] = 1
        if (chunk[1] == "VV"):
            if (chunk[0] not in verb_dict):
                verb_dict[chunk[0]] = 1

for file in os.listdir():
    if (file.endswith(".pos")):
        extract_chunk(file)

noun_dict_set = set(noun_dict)
verb_dict_set = set(verb_dict)
overlap_dict = noun_dict_set & verb_dict_set

with open('overlapped_output.txt', 'w') as out_file:
    for word in overlap_dict:
        out_file.write(word)
        out_file.write( "\n")
