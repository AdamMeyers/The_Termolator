#!/usr/bin/env python3
import os
import sys

from inline_terms import *

def main(args):
    global lemma_dict
    infile_list = args[1]
    abbr_to_full = args[2]
    special_domain = args[3]
    lemma_dict_file = args[4]
    initialized = False
    if special_domain.lower() == 'false':
        special_domain = False
    with open(infile_list) as instream:
        for line in instream:
            line = line.strip(os.linesep)            
            term_file,abbr_file,substring_file = line.split(';')
            make_term_and_substring_list(term_file,abbr_file,substring_file,abbr_to_full=abbr_to_full,special_domain=special_domain,lemma_dict_file=lemma_dict_file,initialized=initialized)
            if not initialized:
                initialized = True
        record_lemma_dict(lemma_dict_file)


if __name__ == '__main__': sys.exit(main(sys.argv))
