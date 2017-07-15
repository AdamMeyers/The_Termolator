#!/usr/bin/env python3
import sys

from inline_terms import *


## @func comp_termChunker
def main(args):
    infile_list = args[1]
    outfile_list = args[2]
    make_term_chunk_file_list(infile_list, outfile_list)


if __name__ == '__main__': sys.exit(main(sys.argv))
