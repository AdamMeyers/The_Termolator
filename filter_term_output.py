#!/usr/bin/env python3
import os
import sys
from term_utilities import *
from filter_terms import *

def main(args):
    global special_domains
    special_domains = []
    file_prefix = args[1]
    web_score_dict_file = args[2]
    if args[3].lower() in ['true','t']:
        use_web_score = True
    elif args[3].lower() in ['false','f']:
        use_web_score = False
    else:
        print('You set the webscore flag to', args[3], 'but it must be either "True" or "False".')
        print('Use "True" if you want the system to use the webscore function and the system will run slowly and be more accurate.')
        print('Use "False" otherwise.')
    max_term_number = int(args[4])
    abbr_file_list = args[5]
    if (len(args)>6) and (args[6].lower() != 'false'):        
        special_domains.extend(args[6].split('+'))
    initialize_utilities()
    input_file = file_prefix + ".all_terms"
    output_file = file_prefix + ".scored_output"
    abbr_full_file = file_prefix + ".dict_abbr_to_full"
    full_abbr_file = file_prefix + ".dict_full_to_abbr"
    reject_file = file_prefix + ".rejected-terms"
    filter_terms(input_file,output_file,abbr_full_file,full_abbr_file,use_web_score=use_web_score,numeric_cutoff=max_term_number,reject_file=reject_file,web_score_dict_file=web_score_dict_file,abbr_files=abbr_file_list)

if __name__ == '__main__': sys.exit(main(sys.argv))
