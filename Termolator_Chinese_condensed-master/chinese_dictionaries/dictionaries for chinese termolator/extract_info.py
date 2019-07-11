import re

file = "overlapped_output.txt"
three_words_dic = {}
normalization_dic = {}
with open(file) as in_file:
    for content in in_file:
        if (len(content.strip()) == 3):
            three_words_dic[content.strip()] = 1

        regex = re.compile('.*化$')
        if (re.search(regex,content.strip())):
            normalization_dic[content.strip()] = 1

normalization_set = set(three_words_dic) | set(normalization_dic)
print(normalization_set)