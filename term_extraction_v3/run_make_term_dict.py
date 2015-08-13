#!/usr/bin/env python3

from find_patent_topic_terms3 import *

def main(args):
    infile = args[1]
    outfile = args[2]
    extra_file = args[3]
    abbrev_full_dict = args[4]
    full_abbrev_dict = args[5]
    if len(args)>6:
        cutoff=float(args[6])
    else:
        cutoff=.5
    if len(args)>7:
        if args[7] in ['T','True','TRUE', 'true', 't']:
            is_old_version=True
        else:
            is_old_version=False
    else:
        is_old_version=True
    make_stat_term_dictionary(infile,outfile,extra_file,\
                                 cutoff2=cutoff,\
                                 abbrev_full_dict_file=abbrev_full_dict,\
                                 full_abbrev_dict_file=full_abbrev_dict, \
                                 terms_on_separate_lines=is_old_version)

if __name__ == '__main__': sys.exit(main(sys.argv))
