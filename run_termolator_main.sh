#!/bin/sh

#MAIN SCRIPT for all languages of Termolator

echo "Enter language of documents: ENG or FR"

read lang

if [ "${lang,,}" == "eng" ]; then
	echo "Enter parameters for ENG all on the same line:"
	echo "
	## 1 = foreground_infiles -- file listing one txt file per line
	## 2 = background_infiles -- file listing one text file per line
	## 3 = file type of input files (.htm .html or .txt)
	## 4 = output_file_name 
	## 5 = True or False (do background files need to be processed)
	##      If False, stored background cache file will be loaded (see 13).
	##      If True, background information will be stored as a cache file (see Argument 13).
	## 6 = True or False (run Web-based filter?)
	## 7 = Maximum Number of Terms Considered (suggested = 30000)
	## 8 = Top N -- number of terms you want to keep in the end (suggested 5000-10000)
	## 9 = TERMOLATOR directory -- can be set as an environment variable
	## 10 = names of additional topic areas that should be included:
	##       these correspond to dictionaries listed in utilities.py
	##       topic names should be of the following format:
	##       'opic1 topic2 topic3 topic4' -- topics should be
	##       separated by '+, i.e., 'legal+financial'. The value should
	##       be False if not used refer to as {10}
	## 11 = If True, means skip preprocessing of Foreground
	##       This comes in useful if you want to run the same Foreground 
	##       with different backgrounds or if for any reason, you have
	##	 already preprocessed the foreground file. So usually, this field should just
	##	 contain 'False'.
	## 12 = general_file_name (or False), if different from $4 (for reuse of webscores, lemmas, etc.)
	## 13 = background cache file (to save to or to load from) or False
	##       if False, the default filename: ranking.pkl will be used
	## 14 = If a number, it is the cutoff for filtering out 'bad text';
	##       If False, no filtering is assumed; if 'good', a cutoff of -1 (standard deviations)
	##       is assumed to be the cutoff; if 'bad', a cutoff of -.2 is assumed.
	##       Further details about the 'bad text' filter is in the README
	"
	echo "ENTER ALL ON SAME LINE separated by SPACE and press ENTER when finished."

	read eng_args
	
	bash run_termolator.sh "$eng_args"

elif [ "${lang,,}" == "fr" ]; then
	echo "Enter parameters for FR all on the same line:"
	echo "
	## 1 = foreground directory -- directory containing all foreground documents
	## 2 = background directory -- directory containing all background documents
	## 3 = output_file_name 
	## 4 = True or False (do background files need to be processed?)
	##      If False, background documents matching name given in 2 will be used,
	##		assuming that they are the result of a previous run.
	## 5 = True or False (do foreground files need to be processed?)
	## 6 = True or False (run web filter?)
	## 7 = Maximum Number of Terms Considered (suggested = 30000)
	## 8 = Top N -- number of terms you want to keep in the end (suggested 5000-10000)
	## 9 = TERMOLATOR directory -- can be set as an environment variable
	## 10 = TreeTagger directory -- from this dir, where is TreeTagger installed
	## 11 = If a number, it is the cutoff for filtering out 'bad text';
	##       If False, no filtering is assumed; if 'good', a cutoff of -1 (standard deviations)
	##       is assumed to be the cutoff; if 'bad', a cutoff of -.2 is assumed.
	##       Further details about the 'bad text' filter is in the README
	"
	echo "ENTER ALL ON SAME LINE separated by SPACE and press ENTER when finished."

	read fr_args
	
	bash run_termolator_fr.sh $fr_args
else
	echo "Language should be ENG or FR."
	exit
fi
