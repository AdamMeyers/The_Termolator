#!/bin/sh

## $1 = foreground_infiles -- file listing one txt file per line
## $2 = background_infiles -- file listing one text file per line
## $3 = file type of input files (.htm .html or .txt)
## $4 = output_file_name
## $5 = True or False (do background files need to be processed)
##      If False, stored background cache file will be loaded (see $13).
##      If True, background information will be stored as a cache file (see Argument 13).
## $6 = True or False (run Web-based filter?)
## $7 = Maximum Number of Terms Considered (suggested = 30000)
## $8 = Top N -- number of terms you want to keep in the end (suggested 5000-10000)
## $9 = TERMOLATOR directory -- can be set as an environment variable
## $10 = names of additional topic areas that should be included:
##       these correspond to dictionaries listed in utilities.py
##       topic names should be of the following format:
##       "topic1 topic2 topic3 topic4" -- topics should be
##       separated by '+, i.e., 'legal+financial'. The value should
##       be False if not used
## refer to as ${10}
## $11 = If True, means skip preprocessing of Foreground
##       This comes in useful if you want to run the same Foreground
##       with different backgrounds or if for any reason, you have
##	 already preprocessed the foreground file. So usually, this field should just
##	 contain "False".
## $12 = general_file_name (or False), if different from $4 (for reuse of webscores, lemmas, etc.)
## $13 = background cache file (to save to or to load from) or False
##       if False, the default filename: ranking.pkl will be used
## $14 = If a number, it is the cutoff for filtering out "bad text";
##       If False, no filtering is assumed; if "good", a cutoff of -1 (standard deviations)
##       is assumed to be the cutoff; if "bad", a cutoff of -.2 is assumed.
##       Further details about the "bad text" filter is in the README
## $15 = the pathname to the case names for exclusion

TERMOLATOR=${9:-$TERMOLATORPATH}

echo 1 $4.scored_output
echo 2 topic_8_lemma.dict
echo 3 $8
echo 4 $4.out_term_list
echo 5 $4.dict_abbr_to_full
echo 6 $4.dict_full_to_abbr
echo 7 $TERMOLATOR

python3 $TERMOLATOR/make_final_output_file_legal.py $4.scored_output topic_8_lemma.dict $8 $4.out_term_list $4.dict_abbr_to_full $4.dict_full_to_abbr $TERMOLATOR

