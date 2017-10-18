#!/usr/bin/env python3

import re
import sys
import os
from inline_terms import *

def main(args):
    ## make output file consting of the first N lemmas and their
    ## alternative forms
    scored_output_file = args[1]
    lemma_dictionary_file = args[2]
    cutoff = int(args[3])
    output_file = args[4]
    make_top_terms_with_lemma_output_file(scored_output_file,lemma_dictionary_file,cutoff,output_file)


if __name__ == '__main__': sys.exit(main(sys.argv))
