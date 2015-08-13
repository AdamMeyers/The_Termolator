#!/usr/bin/env python3

## This program gets automatically generated abbreviation tuples
## The programs used are of a general format for printing any automatically
## generated tuples. Currently two types are generated, but only
## 1 type (ABBREVIATE) is printed out. Future versions of this program
## may be made more efficient by only producing the type being generated.
##

## from preprocess_annotation3 import *
from abbreviate4 import *

import os
import sys


def main (args):
    if len(args) < 4:
        print('3 Arguments are Required')
        return -1
    acquire_and_print_out_dictionary3(args[1], args[2],args[3],patent=True,tally=True)

if __name__ == '__main__': sys.exit(main(sys.argv))
