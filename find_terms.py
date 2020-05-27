from term_utilities import *
from abbreviate import *
from inline_terms import *
from ne_filter import *

def find_inline_terms_for_file_list(file_list,dict_prefix=False,ne_filter_ending=False,fact_suffix='.fact',txt_suffix='.txt3',overwrite=True):
    start = True
    with open(file_list) as instream:
        # if dict_prefix:
        #     unigram_dictionary.clear()
        ## see derive_plurals in term_utilities
        ## and other instances of "unigram_dict" below
        for line in instream:
            file_prefix = line.strip()
            if (not overwrite) and os.path.isfile(file_prefix+'.terms'):
                skip = True
            else:
                skip = False
            if not skip:
                lines = get_lines_from_file(file_prefix+txt_suffix) ## add feature to remove xml
                run_abbreviate_on_lines(lines,file_prefix+'.abbr',reset_dictionary=start)
            ## creates abbreviation files and acquires abbreviation --> term
            ## and term --> abbreviation dictionaries
            ## Possibly add alternative which loads existing abbreviation files into
            ## dictionaries for future steps (depends on timing)
            
            # if dict_prefix:
            #     increment_unigram_dict_from_lines(lines)
            if skip:
                pass
            elif ne_filter_ending and os.path.isfile(file_prefix+ne_filter_ending):
                start_end_filter_positions = read_in_filter_positions(file_prefix+ne_filter_ending)
            else:
                start_end_filter_positions = False
            if not skip:
                find_inline_terms(lines,file_prefix+fact_suffix,file_prefix+'.pos',file_prefix+'.terms',start_end_filters=start_end_filter_positions)
            if start:
                start = False
        if dict_prefix:
            save_abbrev_dicts(dict_prefix+".dict_abbr_to_full",dict_prefix+".dict_full_to_abbr")
            ## save_unigram_dict(dict_prefix+".dict_unigram")

def increment_lemma_dict(infile,dictionary):
    with open(infile) as instream:
        ## this allows each phrase to have multiple corresponding lemmas, but
        ## in practice, we will only really assume one lemma per phrase
        for line in instream:
            line = line.strip(os.linesep)
            line_entry = get_integrated_line_attribute_value_structure_no_list(line,'TERM') 
            if line_entry:
                lemma = line_entry['LEMMA'].lower()
                lemma = lemma.strip('\'"()')
                phrase = line_entry['STRING'].lower()
                phrase = phrase.strip('\'"()')
                if phrase in dictionary:
                    if not lemma in dictionary[phrase]:
                        dictionary[phrase].append(lemma)
                else:
                    dictionary[phrase]=[lemma]
            ## eliminates detected NEs: URL, ORGANIZATION, LOCATION, ...
            

def make_lemma_dict(terms_files,lemma_dict):
    lemma_dictionary = {}
    with open(terms_files) as instream:
        for line in instream:
            line = line.strip(os.linesep)
            increment_lemma_dict(line,lemma_dictionary)
    with open(lemma_dict,'w',) as outstream:
        keys = list(lemma_dictionary.keys())
        keys.sort()
        for key in keys:
            outstream.write(key)
            for value in lemma_dictionary[key]:
                outstream.write('\t'+value)
            outstream.write('\n')
