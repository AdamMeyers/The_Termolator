#!/usr/bin/env python3
import os
import sys
from term_line_summary import *

def main(args):
    prefix = args[1]
    directory = args[2]
    txt_type = args[3]
    if len(args)> 4:
        confidence_order = args[4].lower()
    else:
        confidence_order = 'false'
    ## possibly implement confidence_order later
    input_file = prefix+'.term_instance_map'
    output_file = prefix+'.summary'
    cluster_strategy='big_centroid_max'
    if confidence_order == 'true':
        breakdown_by_log_10 = True
    else:
        breakdown_by_log_10 = False
    generate_summaries_from_term_file_map(input_file,output_file,directory,cluster_sample_strategy=cluster_strategy,txt_file_type=txt_type,breakdown_by_log_10=breakdown_by_log_10)

    
if __name__ == '__main__': sys.exit(main(sys.argv))
