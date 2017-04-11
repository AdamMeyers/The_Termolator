from term_utilities import *
from abbreviate import *
from inline_terms import *

def find_inline_terms_for_file_list(file_list,dict_prefix=False):
    start = True
    with open(file_list) as instream:
        # if dict_prefix:
        #     unigram_dictionary.clear()
        ## see derive_plurals in term_utilities
        ## and other instances of "unigram_dict" below
        for line in instream:
            file_prefix = line.strip()
            lines = get_lines_from_file(file_prefix+'.txt3') ## add feature to remove xml
            run_abbreviate_on_lines(lines,file_prefix+'.abbr',reset_dictionary=start)
            ## creates abbreviation files and acquires abbreviation --> term
            ## and term --> abbreviation dictionaries
            ## Possibly add alternative which loads existing abbreviation files into
            ## dictionaries for future steps (depends on timing)
            
            # if dict_prefix:
            #     increment_unigram_dict_from_lines(lines)

            find_inline_terms(lines,file_prefix+'.fact',file_prefix+'.pos',file_prefix+'.terms')
            if start:
                start = False
        if dict_prefix:
            save_abbrev_dicts(dict_prefix+".dict_abbr_to_full",dict_prefix+".dict_full_to_abbr")
            ## save_unigram_dict(dict_prefix+".dict_unigram")
        

