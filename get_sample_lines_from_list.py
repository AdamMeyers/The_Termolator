#!/usr/bin/env python3

import sys
from term_utilities import *
import os

def main(args):
    ## infile is the output file from distributional term extraction
    infile = args[1]
    outfile = args[2]
    N = int(args[3])
    get_n_random_lines (infile,outfile,N)

if __name__ == '__main__': sys.exit(main(sys.argv))
