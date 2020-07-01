This is the README for the French version of Termolator, created by
Sandra Burlaud in 2019 and 2020.

- ENGLISH TERMOLATOR: more information can be found in the file README.txt

- FRENCH TERMOLATOR: 

	INSTALLATION:
	- Download all Termolator files (main (English) components as well) from Github repo.
	- The necessary TreeTagger files (by Helmut Schmid 1995, https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/) are provided as TreeTaggerLinux.zip
	- In order to use the French version of the Termolator, you should you unzip this file, creating a  a TreeTaggerLinux/ subdirectory (under your Termolator directory). FR_Termolator/TreeTaggerLinux/.  Then you should run  install-tagger.sh inside this subdirectory.

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
	
	The following scripts and dictionaries contain French-specific
	elements or have been modified for French:
		
		run_termolator_fr.sh run_lang_model_background_fr.sh
		run_lang_model_foreground_fr.sh
		tag_back_and_foreground.sh
		make_file_list.sh
		getNounChunks.java
		filter_term_output_fr.py
		filter_terms_fr.py
		make_filtered_doc_fr.py
		run_make_filtered_fact_files_FR.py
		stage1_driver.py
		term_utilities_fr.py
		webscore_fr.py
		english_dict_list.txt
		person_name_list_simple.dict
		verb_dict_fr.txt
		cities_eng.dict
		leipzigFR.profile
		modelFRinput-leipzig.list
		nationality_dict_fr.txt
		orgs_abbrev_dict_fr.txt
		dictionary_full_fr.txt
		french_gazetteer.txt

		(FR function has been added to make_language_model.py)
		
	Many of the above rely on non French specific scripts used by
	the English Termolator.

	TESTING THE PROGRAM:

	There are sets of sample files in the french_test_docs_june_2020
	subdirectory for testing the French system. There are two
	shell scripts: run_foret and run_inform which can be run to
	test the system.  Structuring directories in a similar manner
	is suggested for running on other data.
