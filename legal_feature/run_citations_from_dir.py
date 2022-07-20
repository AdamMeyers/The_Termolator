#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from find_legal_citations_for_termolator import *
import sys
import os

def get_base_file(infile):
    if os.sep in infile:
        inpath,slash,short_file = infile.rpartition(os.sep)
    else:
        short_file = infile
    if "." in short_file:
        short_file,period,extension = short_file.rpartition('.')
    return(short_file)

## 
def main (args):
    import os
    if len(args)<2:
        print('This function requires one argument: an io_file list')
    else:
        indirectory  = args[1]
        for infile in os.listdir(indirectory):
            if infile.endswith('.txt'):
                base_file =  indirectory+os.sep+get_base_file(infile)
                outfile = base_file+'.references'
                infile = indirectory +os.sep+infile
                case_and_legislative_citations_to_file(infile,base_file,outfile)

if __name__ == '__main__': sys.exit(main(sys.argv))
