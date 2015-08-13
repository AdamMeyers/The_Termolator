#!/usr/bin/env python3
import os
import sys

from filter_terms import *


def main(args):
    file_prefix = args[1]
    if args[2].lower() in ['true','t']:
        use_web_score = True
    elif args[2].lower() in ['false','f']:
        use_web_score = False
    else:
        print('You set the webscore flag to', args[2], 'but it must be either "True" or "False".')
        print('Use "True" if you want the system to use the webscore function and the system will run slowly and be more accurate.')
        print('Use "False" otherwise.')
    max_term_number = int(args[3])
    input_file = file_prefix + ".all_terms"
    output_file = file_prefix + ".scored_output"
    abbr_full_file = file_prefix + ".dict_abbr_to_full"
    full_abbr_file = file_prefix + ".dict_full_to_abbr"
    reject_file = file_prefix + ".rejected-terms"
    filter_terms(input_file,output_file,abbr_full_file,full_abbr_file,use_web_score,numeric_cutoff=max_term_number,reject_file=reject_file)

if __name__ == '__main__': sys.exit(main(sys.argv))
