#!/usr/bin/env python3
import os
import sys

from abbreviate import *

def main(args):
    abbr_files = args[1]
    full_abbr_file = args[2]
    abbr_full_file = args[3]
    if (not os.path.isfile(full_abbr_file)) or (not os.path.isfile(abbr_full_file)):
        make_abbr_dicts_from_abbr(abbr_files,full_abbr_file,abbr_full_file)

if __name__ == '__main__': sys.exit(main(sys.argv))
