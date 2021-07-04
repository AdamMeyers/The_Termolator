This is the README for legal terminology extraction, created by Nhi Pham and Lachlan Pham in 2020-2021. This work uses the current English version of The Termolator with the following modifications:
* Exclusion of terms which are legislation documents (acts, treaties, Constitutional amendments)
* Exclusion of terms which are case names, which are manually provided as well as identified through search (websearch.py)
* Exclusion of terms with digits or hyphens
* Adjustment of the relevance score calculation using a Federal Court-specific search api (webscore_legal.py)

To run this program, there is a preprocessing step (to obtain the files) and a running step (to run Termolator).

## System Requirements

You must install the Python textacy package before running this program.

## PREPROCESSING
In legal_feature, we provide a shell script preprocessing.sh with command format:

./preprocessing.sh issueType issueID $TERMOLATOR (e.g ./preprocessing.sh broad 8 $TERMOLATOR)

This will handle the following tasks:
- Retrieve the Supreme Court cases and create the database 'cases'
- Generate json files, grouping the cases into their respective broad and narrow issues
- Generate legal terms to be excluded from the result, namely case names and legislation names
- Create the foreground and background sets of the input issue ID and issue type

In order to fully understand the collection of documents for
Termolator, it is necessary to understand the categories.  Note that
we have not yet done a thorough study of the frequencies of files for
each Broad and Narrow topic classification. It is probably the case
that the quality of output depends in part on the frequency of a
category. If there are very few instances of a certain category, we
suspect that Termolator's performance on extracting terms would be
lower for that category than more common categories.  The additional
document: README_legal_issues.txt lists and explains the 14 broad
categories and 260 narrow categories.

These classifications were manually annotated at the University of
Washington (http://scdb.wustl.edu/). We obtain them through the Python
textacy module (https://github.com/chartbeat-labs/textacy).

## RUNNING
To run The Termolator for legal terminology extraction, the command is as follows:

$TERMOLATOR/run_termolator_legal.sh FOREGROUND BACKGROUND EXTENSION OUTPUT_NAME TRUE-OR-FALSE TRUE-OR-FALSE 30000 5000 PROGRAM-DIRECTORY ADDITIONAL_TOPIC_STRING TRUE-OR-FALSE general_file_name_or_FALSE SHARED_BACKGROUND_FILENAME.pkl MINIMUM_PROBABILITY_OR_FALSE

The arguments are the same as in the English version of The Termolator.


## RESULT & EVALUATION
A sample of 100 words are taken from each output, 20 words are randomly selected from each fifth of the 5000 words and manually evaluated as key terminology. In legal_feature/result, run python3 random_selection.py term_cnt issueID issueType to save the sample in an xlsx output file for annotation task


## FILES ADDED TO TERMOLATOR
Directories:
	The_Termolator/legal_feature: 
		- preprocessing.sh
		- classify_fbground.py
		- create_fbground.py
		- supreme_court.py
		- sample_run ## if made executable, this shell command
		                           ## will do all preprocessing and run Termolator
					   ## on the Broad Class 8 (economic activity)
	The_Termolator/legal_feature/legal_terms_exclusion:
		- legal_terms_extraction.py    ## This program extracts case names and legislation names
		- lower_unique_terms.py         ## This program extract unique names + make terms lowercase
		-UWash_scotus_output   ## contains some files with named entity markup
				       ## (citations to court decisions and to pieces of legislation)
				       ## In future versions, we will include the programs for generating this annotation
				       ## rather than the markup
Python files:
	The_Termolator/filter_legal.py
	The_Termolator/filter_term_output_legal.py
	The_Termolator/filter_terms_legal.py
	The_Termolator/inline_terms_legal.py
	The_Termolator/make_final_output_file_legal.py
	The_Termolator/webscore_legal.py
	The_Termolator/websearch.py

Other:
	The_Termolator/README_legal.txt
	The_Termolator/run_termolator_legal.sh
