#!/usr/bin/env python3

import os
import sys

def create_dummy_fact(txt,fact):
    filesize = os.path.getsize(txt)
    with open(fact,'w') as outstream:
        outstream.write('STRUCTURE TYPE="TEXT" START=0 END='+str(filesize-1)+os.linesep)

def main(args):
    ## infile is the output file from distributional term extraction
    txt_file_list = args[1]
    with open(txt_file_list) as instream:
        for line in instream:
            txt,fact = line.strip().split(';')
            create_dummy_fact(txt,fact)

if __name__ == '__main__': sys.exit(main(sys.argv))
