import os
import re


def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))


def generate_names_to_exclude(path, citation, file):
    names = set()
    for filename in os.listdir(path):
        with open(f'{path}/{filename}', 'r') as f:

            for line in f:
                if citation in line.lower():
                    start = False
                    first = False
                    s = ''
                    for char in line:
                        if char == '>':
                            start = True
                        elif char == '<' and start:
                            start = False
                            first = True
                        elif start and not first:
                            s += char
                    names.add(s)

    fwrite = open(f'./{file}', 'w')
    for a in names:
        fwrite.write(a.strip() + '\n')
        for b in a.split():
            if not hasNumbers(b):
                fwrite.write(re.sub(r'[^\w\s]', '', b).strip() + '\n')
        if len(a.split('v.')) == 2:
            for c in a.split('v.'):
                fwrite.write(c.strip() + '\n')
    fwrite.close()


## path = "./legal_terms_exclusion/UWash_scotus_output"
path = "./cases"
generate_names_to_exclude(path,"<citation","./case_names.txt")

# generate_names_to_exclude(path + "/citations", "<citation",
#                           "./legal_terms_exclusion/legislation_names.txt")
# generate_names_to_exclude(path + "/references", "<CITATION",
#                           "./legal_terms_exclusion/case_names.txt")
