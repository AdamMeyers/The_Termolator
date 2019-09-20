#!/usr/bin/env python3
import os
import sys
from term_line_summary import *

def main(args):
    prefix = args[1]
    directory = args[2]
    input_file = prefix+'.term_instance_map'
    output_file = prefix+'.summary'
    cluster_strategy='big_centroid_max'
    generate_summaries_from_term_file_map(input_file,output_file,directory,cluster_sample_strategy=cluster_strategy)
    
if __name__ == '__main__': sys.exit(main(sys.argv))
