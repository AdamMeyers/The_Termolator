#!/usr/bin/env python3
import os
import sys

from normalize_file_names import *

def main(args):
    file_list = args[1]
    prefix = args[2]
    suffix = args[3]
    program_directory = args[4]
    ## if minimum_file_check(file_list,50):
    if minimum_file_check(file_list,1):
            normalized = file_list + '_2'
            table = file_list + '_table.tsv'
            normalize_file_names(file_list,normalized,\
            table, prefix,suffix)
    else:
        print('Not enough files. You  may need to change your search terms.')

if __name__ == '__main__': sys.exit(main(sys.argv))

