#!/usr/bin/env python3
import os
import sys
from get_term_maps import *

def main(args):
    term_list = args[1] ## file containing list of terms
    term_file_list = args[2] ## file containing list of ".terms" files
    term_map = args[3] ## output file name
    input_file_path = args[4]
    if os.path.isfile(term_list) and (not os.path.isfile(term_map)):
        get_term_maps(term_list,term_file_list,term_map,input_file_path)

    
if __name__ == '__main__': sys.exit(main(sys.argv))
