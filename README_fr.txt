- ENGLISH TERMOLATOR: more information can be found in the file README.txt

- FRENCH TERMOLATOR: 

	INSTALLATION:
	- Download all Termolator files (main (English) components as well) from Github repo.
	- The necessary TreeTagger files (by Helmut Schmid 1995, https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/) are provided in FR_Termolator/TreeTaggerLinux/. After having downloaded the Termolator files, inside TreeTaggerLinux/, run install-tagger.sh

	RUNNING:
	The expected arguments are:
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

	For French documents, use run_termolator_fr.sh directly with these arguments or run the general script run_termolator_main.sh to choose language and be prompted for arguments.

	The final list of terms can be found in [3].scored_output.


	FR ONLY COMPONENTS:
	The following scripts contain French-specific elements or have been modified for French:
		filter_term_output_fr.py
		filter_terms_fr.py
		getNounChunks.java
		make_filtered_doc_fr.py
		run_lang_model_background_fr.sh
		run_lang_model_foreground_fr.sh
		run_make_filtered_fact_files_FR.py
		run_termolator_fr.sh
		stage1_driver.py
		tag_back_and_foreground.sh
		term_utilities_fr.py
		webscore_fr.py

		(FR function has been added to make_language_model.py)
		
	Many of the above rely on non French specific scripts used by the English Termolator.
