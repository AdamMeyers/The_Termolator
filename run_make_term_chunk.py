#!/usr/bin/env python3
import os
import sys

from inline_terms import *

def main(args):
    infile_list = args[1]
    outfile_list = args[2]
    abbr_to_full = args[3]
    special_domain = args[4]
    if special_domain.lower() == 'false':
        special_domain = False
    lemma_dict = args[5]
    make_term_chunk_file_list(infile_list,outfile_list,abbr_to_full,special_domain,lemma_dict)

if __name__ == '__main__': sys.exit(main(sys.argv))
