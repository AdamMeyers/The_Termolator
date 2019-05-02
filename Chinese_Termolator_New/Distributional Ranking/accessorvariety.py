'''
Author: Yuling Gu
Date: Sept 27, 2018
Description:
This program implements Feng et al. 2004, "Accessor Variety Criteria
for Chinese Word Extraction". Computational Linguistics 30(1).
Using the accessor variety criteria as a filter, we filter out terms with
less then 3 unique left and right contexts.
Usage: python3 accessorvariety.py unfiltered_ouput.txt foreground.filelist
Example : python3 accessorvariety.py ../../Downloads/outfile.txt chinese_term_extraction_binaryRelease/sample.pos.filelist

'''

#!/usr/bin/env python3
import re
import sys


def main(args):
    # open unfiltered file list (first argument)
    input_file  = sys.argv[1]
    # list of files in CoNLL format
    conll_filelist = sys.argv[2]
    with open(conll_filelist, "r") as filenames:
    	conll_files = filenames.readlines()
    with open(input_file, "r") as f:
    	unfiltered = f.readlines()
    for term in unfiltered:
    	left_context = []
    	left_count = 0
    	right_context = []
    	right_count = 0
    	term_word = term.split("\t")
    	current_term = []
    	for i in range(0, len(term_word) - 1):
    		current_term. append(term_word[i])

    	for conll_file in conll_files:
    		# modify according to where the conll format files are
    		conll_file =  "chinese_term_extraction_binaryRelease/" + conll_file.strip("\n")
	    	with open(conll_file, "r") as f2:
	    		conll = f2.readlines()
	    		current_term_vec = current_term[0].split(" ")
    			#print(current_term[0])
    			for token in range(0, len(conll)):
    				word2_tag_BIO = conll[token].split("\t")
    				# term matched
    				if current_term[0] == word2_tag_BIO[0]:
	    				left = conll[token-1].split("\t")[0]
	    				# if target word length 1
    					if len(current_term_vec) == 1:
    						right = conll[token+1].split("\t")[0]
    					else:
    						right = conll[token + len(current_term_vec) -1].split("\t")[0]
    					left = re.sub(r'[，。!\?\-\/\(\)\\]', '', left)
    					right = re.sub(r'[，。!\?\-\/\(\)\\"]', '', right)
    					if left != "" and left not in left_context:
    						left_context.append(left)
    					if right != "" and right not in right_context:
    						right_context.append(right)
    		# check context count
    		if (len(left_context) >= 3) and (len(right_context) >= 3):
    			break # if reach target, no need open another file

    	if len(left_context) >= 3 and len(right_context) >= 3:
    		print (term, end = "")




if __name__ == '__main__':
	main(sys.argv[1:])