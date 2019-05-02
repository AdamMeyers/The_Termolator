#!/usr/bin/env python3

import sys
import re
from term_utilities import *
from make_language_model import *

def main(args):
    infile_list = args[1]
    profile_file = DICT_DIRECTORY + 'OANC.profile2'
    model_name = 'generalized_character2'
    model_file = DICT_DIRECTORY + 'gen2_lang.model'
    cutoff = args[2] ## should be -1 or -0.2 ## possibly give fewer choices for final version
    if isinstance(cutoff,str) and re.search('^[-\.0-9]+$',cutoff):
        ## if cutoff is a string that can be converted to a float, convert it to a float
        cutoff = float(cutoff)
    elif cutoff.lower() == 'patent':
        cutoff = -.2
    elif cutoff.lower() == 'normal':
        cutoff = -1
    else:
        cutoff = -1
    filter_fact_files(infile_list,model_name,model_file,profile_file,cutoff=cutoff)
    
if __name__ == '__main__': sys.exit(main(sys.argv))
