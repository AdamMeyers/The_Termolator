The Termolator Program 0.1 is licensed under the Apache license 2.0
(http://www.apache.org/licenses/LICENSE-2.0). It was created by Adam
Meyers, Yifan He, Zachary Glass and Shasha Liao and released in July,
2015.

The Termolator Program 0.2 (including 0.21, 0.22, 0.23, etc.) is also
licensed under the Apache license
2.0(http://www.apache.org/licenses/LICENSE-2.0).  It is a revision of
the original program. It was revised by Adam Meyers, John Ortega, Vlad
Tyshkevich, Yuling Gu and Leizhen Shi. The main changes are: (i) bug
fixes; (ii) The new version uses Python 3 exclusively -- the Python 2
portions of the original code have all been changed; (iii) additional
features have been added so the program will work better with legal
text; (iv) changes to the abbreviation program intended to improve
precision, (v) the capability to store web search based scores and
look them up on subsequent runs rather than recalculating them; and
(vi) a caching feature has been added to make runs with different
foregrounds, but the same background file more efficient; (vi) The
tchunk component of the previous system has been replaced (later
versions) with a substring component. The main effect of this is that
the substrings of noun chunks that are tested by the system are
linguistically motivated -- they must be legitimate noun groups
themselves and they must be observed in other contexts; (vii) a n-gram
filter (later versions) has been added so that unusually formatted
text (bibliographies, tables, charts, etc.) are likely to be ignored
as input; (vii) a version of the Chinese Termolator is incorporated
that is more closely connected to the English version (the import of
this feature is not complete as of this writing)

There are some additional features, many experimental that we will be
adding to this website and will describe in separate READMEs for
now. These include: 

     README_termolator_add_ons.txt -- This currently describes 4
     programs: (a) term map creation: a program for producing a "term
     map", a file that details how each term in termolator output that
     occurs in the foreground documents with some minimum frequency
     (default = occurs in at least 3 files).; (b) a summary creation
     program: a program which takes each term listed in the term map
     just described and produces a glossary of sorts. The glossary
     provides first paragraphs of corresponding wikipedia entries,
     when they exist, as well as a sample of (by default 3) texts
     containing the term (or variants thereof). These texts are
     sampled from the foreground documents with an emphasis on finding
     samples that are both well-formed (according to a language model)
     and different from each other (distance measured as cosine
     similarity). (c) A Question-based front-end to termolator and the
     summary program that gets foreground and background documents
     automatically from wikipedia. (d) A command line based program for
     extracting text files from Wikipedia for use in Termolator.

     README_fr.txt -- This describes the French version of Termolator,
     including installation instructions (which presume first
     installing the English version), as well as how to run the French system.
     The French version was created by Sandra Burlaud.

     README-chinese.txt -- This describes the Chinese version of
     Termolator, including installation instructions (which presume
     first installing the English version), as well as how to run the
     Chinese system. The original Chinese system has a separate code
     base (https://github.com/ivanhe/termolator/) and was created by
     Yifan He. The current system, that is more closely integrated
     with the English system is based on Yifan He's system, but
     includes the work of Yuling Gu, Leizhen Shi and Echo Hong.

     README_legal.txt -- describes some extra steps required to
     process court decision documents using the Python textacy module
     (https://github.com/chartbeat-labs/textacy), which encodes of
     some Supreme court decisions that have been manually classified
     at the University of Washington (http://scdb.wustl.edu/).

This document is primarily about the English version of Termolator.

The Termolator takes two sets of documents as input a FOREGROUND set
and a BACKGROUND set and finds instances of terminology that are more
characteristic of the FOREGROUND than the BACKGROUND.  Input files can
be either .txt, .html or .xml (the latter only working if it uses HTML
style markup to delimit text). UTF-8 encoding (which includes ASCII)
is preferred, but ISO-8859-1 will work as well.

The biggest difference in running the system as of May 2019 is the
need for an extra parameter (parameter number 14), described below.

The essential details of the June 2018 system are described in the
following paper:

	A. Meyers, Y. He, Z. Glass, J. Ortega, S. Liao,
	A. Grieve-Smith, R. Grishman and O. Babko-Malaya (2018).  The
	Termolator: Terminology Recognition Based on Chunking,
	Statistical and Search-Based Scores Research Metrics and
	Analytics (RMA).

This can be downloaded at:

https://www.frontiersin.org/articles/10.3389/frma.2018.00019/full

We will continue to modify the system over time.

Dependencies: If you have not already done so, you should install the
   python 3 version of the NLTK (see http://www.nltk.org/install.html). 
   To see if it is already installed, attempt to "import nltk" in 
   Python 3. If you get an error, than install it.

Instructions for Using program:

1) We will assume that $TERMOLATOR is the path containing the
   TERMOLATOR program. Setting an environmental variable (called
   TERMOLATOR) is suggested. 

2) To run the main system, the command is as follows (an additional
   way of running the system will be described in section 7):

   $TERMOLATOR/run_termolator.sh FOREGROUND BACKGROUND EXTENSION OUTPUT_NAME TRUE-OR-FALSE TRUE-OR-FALSE 30000 5000 PROGRAM-DIRECTORY ADDITIONAL_TOPIC_STRING TRUE-OR-FALSE general_file_name_or_FALSE SHARED_BACKGROUND_FILENAME.pkl MINIMUM_PROBABILITY_OR_FALSE

The arguments are defined as follows:

   Argument 1 (FOREGROUND) = a file listing the documents in the foreground set
   Argument 2 (BACKGROUND) = a file listing the documents in the background set
   Argument 3 (EXTENSION) = the extension of input files
   Argument 4 (OUTPUT_NAME) = name of output file (without extension)
   Argument 5 (TRUE-OR-FALSE) = True or False (do background files need to be processed?)
   	      If False, stored background cache will be loaded (see Argument 13).
	      If True, background information will be stored as a cache file (see Argument 13).
   Argument 6 (TRUE-OR-FALSE) = True if you want the system to use the relevance 
   	      	score for determining rankings and False otherwise.
   Argument 7 Maximum Number of Terms Considered (suggested = 30000)
   Argument 8 Top N -- number of terms you want to keep in the end (suggested 5000-10000)
   Argument 9 (PROGRAM-DIRECTORY) = the directory where the program is, e.g., 
   	        $TERMOLATOR if you set this variable.
   Argument 10 (ADDITIONAL_TOPIC_STRING) = topics connected with a plus sign, e.g., legal+finance.
   	       These topics are split by plus signs. The resulting topics correspond to key words 
	       in the dictionary_table variable in term_utilities.py. Currently, only the "legal"
	       topic is supported. If there are no additional topics, this variable should have
	       "false" as a value. If you add the legal topic, a dictionary of legal terms will
	       be downloaded and some specialized rules will be invoked for abbreviations. Other
	       topic specific features may be added in the future.
   Argument 11 If True, skip preprocessing for Foreground. This comes in useful if you want to
   	       run the same Foreground with different backgrounds or if for any reason, you have
	       already preprocessed the foreground file. So usually, this field should just
	       contain "False".
   Argument 12 The name of some of the shared cached data to be used in multiple runs. This is currently
   	       being used as a prefix for both webscore files and for lemma dictionary files, e.g., if
               argument 12 is 'biology', the files will either be created or updated when the program
	       is run. If the value of argument 12 is False, Argument 4 will be used instead, i.e., the files 
	       $4_lemma.dict and $4.webscore will be used. Of course a webscore file will only be generated
	       in either case if Argument 6 is True. These cached files make it unnecessary to recalculate
	       webscores for terms that have previously been looked up (saving as much as .75 seconds per
	       term). It also allows different forms of a lemma to be saved over a larger amount of documents
	       (both foreground and background) so that more forms of a lemma are likely to be found.
   Argument 13 The name of the background cache file associated with Argument 5. If you list False as the background
               file, a default name (ranking.pkl) will be used (info will be saved to or loaded from this file). It
	       is suggested that you use the .pkl file type, since this is a Python pickle file.
   Argument 14 Is either a number, the string "patent", "normal" or "False". This argument is used by the language 
               model to cause the program to eliminate some blocks of text. The intension is that "abnormal" text
	       such as bibliographies, tables or charts will be ignored because terms extracted from such text are
	       likely to be of low quality. "False" causes this component not to do anything. The number should be a
	       negative number between 0 and -2.  We are currently using -.2 (negative 2/10) for patent text and -1 for
	       other texts. You can also use the strings "patent" and "normal" in place of these 2 values. The meaning
	       is that text that the language model classifies as having a probability of less than some number of standard
	       deviations from the mean probability is ignored, whereas higher probability text is processed. Patents tend
	       to have more tables and in-text bibliographies than "normal" text and therefore we assume a higher
	       threshold.

IMPORTANT PATH INFORMATION: If FOREGROUND and BACKGROUND files contain absolute paths, this command will work from anywhere.  Otherwise, you should run from the directory containing FOREGROUND and BACKGROUND. We will call this the DATA_DIRECTORY.  The files listed in FOREGROUND andBACKGROUND should be paths relative to the DATA_DIRECTORY.

To test the program, we suggest going to one of our 3 test directories and running the command from there. Note that 
we will shorly be adding a corpus of court decisions, for which the legal topic features are useful. We have not 
yet tested whether these same features are useful for the patent directory provided here.

   a) subdirectory: gutenberg-test
      command:      $TERMOLATOR/run_termolator.sh foreground.list background.list .htm knitting True True 30000 5000 $TERMOLATOR False False False gutenberg.pkl -1
      
      -- The "True" setting in field 6 will make this run take an extra 10 minutes to run about 600 
       	 web searches, but the results are more accurate as a result. 

      -- After this run, the background statistics will be stored in gutenberg.pkl. Thus, for a 
      	 second run, possibly with a different foreground, setting the fifth parameter to False
         will make run time be somewhat faster, especially if the sixth parameter is set to False and
	 the websearch score is not used.

      -- These texts are taken from the English portion of Project Gutenberg, a repository of public 
      	 domain texts. The FOREGROUND is a set of chapters of "The Project Gutenberg eBook of Encyclopedia 
	 of Needlework", by Therese De Dillmont. The BACKGROUND is a random selection of documents from the 
	 same repository. Thus the resulting terminology list consists of terms in the domain of "knitting".
	 For more information of Project Gutenberg, go to: https://www.gutenberg.org/

      -- The threshold probability is set to -1 standard deviations below the mean probability.

   b) subdirectory: OANC-test
      command:      $TERMOLATOR/run_termolator.sh foreground.list background.list .txt biology True False 30000 5000 $TERMOLATOR False False False OANC.pkl -1

      -- This run will be faster than the previous run per term generated. If the False in field in field 6 is 
      	 replaced by True, the system will take an extra 3 hours (about 1 second for each of 10,000 terms),
      	 but the results will be better.

      -- These texts are taken from the Open American National Corpus (OANC), a project devoted to collecting 
      	 freely available text for processing by computational linguistics. The FOREGROUND consists of 100 
	 biology related documents and the background consists of 100 random documents.  The resulting terminology 
	 are all about biology. For more information about the OANC, go to: http://www.anc.org/data/oanc/

      -- The threshold probability is set to -1 standard deviations below the mean probability.

   c) subdirectory: patent-test
      command:	  $TERMOLATOR/run_termolator.sh foreground.list background.list .XML surgery True False 30000 5000 $TERMOLATOR False False False patent.pk  -.2

      -- This run should generate about 4700 terms. If False in field 6 is changed to True, it will take an additional 
      	 1.5 hours, but  achieve better results.

      -- These documents are taken from Google patents. We downloaded files and divided them by the US patent 
      	 classes encoded in the documents. The foreground is a set of patents in class 606 (see the 
	 main_classification field in the XML), which are all about "Surgery".  The background is a set of 
	 randomly selected patents. The resulting terminology are all in the domain of "Surgery".

      -- The threshold probability is set to -.2 standard deviations below the mean probability.  Blocks of text are
      	 likely to be ignored if they are too different from the norm (based on the OANC text).

3) Choice of foreground and background documents. Different choices will effect the sort of terminology the system 
will recognize. We recommend between 500 and 5000 small files for both foreground and background or fewer large 
files. The example documents should give you some idea of what is possible. As the examples show, different numbers 
of files are possible.

We suggest creating directories which have only the input (foreground and background) files in them and then none of the 
files have any of the following file extensions, as these may be overwritten by the system: .abbr .fact .pos .substring .terms .txt2 .txt3 .

4) The output produce by the file includes the following, based on the OUTPUT_NAME:

   OUTPUT_NAME.out_term_list --- This is the final output, a list of the top N terms in order of rank, 
   			     	 where N = Argument 8 above. Each line consists of the term lemma 
				 followed by variants of that lemma, separated by tabs. Consider the
				 following 2 lines from the sample OANC-test biology.out_term_list file:

				 glucocorticoid receptor\tglucocorticoid receptors\tgr
				 p53 activation\tactivation of p53

				 As these examples show, the lemma appears first. Then alternative forms 
				 appear including plurals, abbreviations and/or noun phrases with 
				 prepositional phrase right modifiers (we assume that the left modified noun
				 noun compounds are the lemmas).

   OUTPUT_NAME.scored_output --- This is a superset of the previous list, approximately the top 30% of the terms
   			     	 considered by the system or the top K terms, if K is lower than 30%, and 
				 where K = Argument 7 above. If Argument 6 is set to True, a .8 seconds-long
				 web search is used to score each of the elements in this list. Thus 30,000 terms
				 will take around 24,000 seconds or just under 7 hours.

   		             --- There are several columns on each line, divided by tabs, as follows: 
			     	 Column 1 -- the term (just the lemma)
			     	 Column 2 -- a rule classification (used to determine if the term is well-formed)
				 Column 3 -- a value Good, Medium, Neutral (measuring the quality of the term by some set of rules)
				 Column 4 -- a score between 0 and 1 measuring term quality
				 Column 5 -- a score between 0 and 1 measuring the term rank
				 Column 6 -- column 4 X column 5
				 Column 7 -- the relevance score (if being used)
				 Column 8 -- column 4 X column 5 X column 7 (if relevance score is used)

   OUTPUT_NAME.dict_abbr_to_full -- This is a dictionary taken from the Foreground that maps abbreviations to their 
   				    full forms, e.g., HTML --> Hypertext Markup Language. It is used for determining
				    if a sequence of words is a valid term.

   OUTPUT_NAME.dict_full_to_abbr -- This is a dictionary going in the opposite direction, from full forms to terms, e.g.,
   				    Hypertext Markup Language --> HTML

   OUTPUT_NAME.rejected-terms -- These are terms generated by the system, but rejected either because they are deemed to be
   			      	 ill-formed or they were not ranked sufficiently highly to by the initial steps to be
				 considered (top 30% or top 30K if argument 7 is set to 30,000).

                              -- There are several columns, similar to OUTPUT_NAME.scored_output
			         Column 1 -- the term
				 Column 2 -- "FILTERED_OUT" if removed due to a well-formedness rule or "BEYOND-CUTOFF", if 
				 	     removed because the term was ranked lower than 30% or 30K as discussed above.
				 Column 3 --  a rule classification (used to determine if the term is well-formed)
				 Column 4 -- a value Good, Medium, Neutral (measuring the quality of the term by some set of rules)
				 Column 5 -- a score between 0 and 1 measuring term quality
				 Column 6 -- a score between 0 and 1 measuring the term rank
				 Column 7 -- column 5 X column 6

   OUTPUT_NAME.all_terms     --  This is the intermediate list of terms that is generated before 30% or 30K terms are 
   			     	 rejected. The scores are based on a distributional component of our system.

5) For each file processed, the following intermediate files are generated:

   FILE.fact -- this identifies where blocks of text start and end (e.g., paragraphs in html)
   FILE.txt3 -- the .fact file is pointing to start and end character offsets in this file
   FILE.pos -- this provides part of speech tags for each token and is used in processing.
      	       the start and end numbers point to character offsets in the .txt3 file
   FILE.terms -- this identifies terms inline, by means of our chunking program. The start 
   	         and end positions point to character offsets in the .txt3 file.
   FILE.abbr -- this file identifies relations between abbreviations and full forms in text
   FILE.subtring -- this file includes both terms from FILE.terms and well-formed 
   		    substrings  of those words used by the distributional system.
		    Note that in earlier versions of Termolator, .tchunk and 
		    .tchunk.nps files were used for a similar purpose.

6) In addition the following files are created for purposes of speeding up processing in multiple runs:

   $13 -- a pickled file storing the background component of the distributional score
   $12_lemma.dict -- a lemma dictionary, used to generate the non-initial columns in 
   		     the .out_term_list files
   $12.webscore -- A file saving webscores for terms

7) In addition to the "main" way of running the system, there are three additional options.

   A. Single File as foregound. It is possible to run using a single
      file as foreground.  We are currently generating one set of terms
      using each supreme court decision as foreground and the full set of
      supreme court decisions as background. In future versions, we will
      provide an example from this run. To do this, we use the following
      script with the following arguments:

      run_termolator_with_1_file_foreground.sh FOREGROUND BACKGROUND EXTENSION OUTPUT_NAME TRUE-OR-FALSE TRUE-OR-FALSE 10000 1000 PROGRAM-DIRECTORY ADDITIONAL_TOPIC_STRING TRUE_OR_FALSE general_file_name_or_FALSE SHARED_BACKGROUND_FILENAME.pkl MINIMUM_PROBABILITY_OR_FALSE

      This takes all the same arguments as run_termolator.sh, with the following exceptions:

      Argument 1 (FOREGROUND) is one foreground file, rather than a file
         containing a list of files. The filetype is left out
      Arguments 7 and 8 -- lower numbers are recommended for single
         files. Intially we assume 10000 and 1000, but these numbers are
         probably too high

      For the first run, Arguments 5 and 11 should both be True and True
      if the foreground file is part of the background. If not, then
      Argument 11 should be False.  For subsequent runs Argument 5 should
      be False (assuming the same background is being used).

    B. Phase 1 Only -- Suppose you do not want to run the full
       Termolator system. Suppose you are only interested identifying
       the technical noun groups that we use as input to the
       distributional system. 

       The script run_terms_only.sh takes only five arguments, a subset of the arguments of the full
       run_termolator.sh script.
       	   Argument 1: input files -- a file listing the input txt, or hml (or xml) files
	   Argument 2: file type of input files
	   Argument 3: output_file_name (mainly used for creating dictionary/caching files)
	   Argument 4: directory of termlolator (like run_termolator.sh)
	   Argumeng 5: name of special topic area  (like run_termolator.sh)

       The program creates some of the same preprocessing files that run_termolator.sh creates, but does
       not continue to produce a term list. I suspect that the most useful output files are the .terms
       and .abbr files.  The .terms files are the files listing the technical noun groups found in each
       of the input files and the .abbr files are the list of abbreviation relations found.

    C. There is a more experimental option. This has only been partially implemented and not completely 
       tested. Suppose, you want to run Phase 1, but you find that there is some other type of constituent,
       e.g., named entities, that you can detect by some other means. Furthermore, suppose that Termolator is
       making errors whereever there are named entities and you would like to eliminate terms that "conflict" 
       with these NEs. There is an additional python file that will remove any term from the "terms" files.
       We have not tested this a lot yet, so it is not currently used in any of the shell scripts, so you
       may have to customize a shell script if you want to incorporate this in a run (either with 
       run_termolator.sh or with run_terms_only.sh).

       In find_terms.py, there is a function find_inline_terms_for_file_list, which is called by 
       run_find_inline_terms.py (by the shell scripts). That function takes an optional keyword argument
       "ne_filter_ending".  If you set that ending to a file type, e.g., ".ne" or the like. The program
       will look for files of that type. Those files will be assumed to include lines of XML with "start" 
       and "end" values, e.g., 
       <citation id="108713_1" entry_type="standard_case" start="1" end="20" reporter="U.S." standard_reporter="U.S." volume="410" page_number="113" year="1973" line="2">410 U.S. 113 (1973)</citation>
       The values other than start and end do not matter.  The terms collected will not be constrained so
       they do not include any strings between instances of "start" and "end" found in that file.

8) Runtime

There are the following factors to consider. 

First of all, increasing the number of foreground and background files
above can slow down the system, especially above 5000 files. We have
so far not found it to be noticeably advantageous to exceed 5000
files. Good results can also be obtained with fewer files, but we have
not identified an ideal amount of data to use -- we suspect that may
depend on a wide range of factors including how different your
foreground are.

Secondly, the preprocessing and distributional stages can take longer
with larger file sizes. If you use the same background files for
different sets of terms, you can save processing time, by not
processing these files more than once. The first time you run with a
set of background files, you set Argument 5 to True (as in all the
examples above). However, for subsequent uses of these background
files, you can set Argument 5 to False (provided your list of
background files point to files that have been processed). We have
found that preprocessing takes about 120 megabytes per hour on our
current PCs (2.53 ghz Xenon) or 3 hours for 360 megabytes (5000
patents). Assuming that the foreground and background corpora are
approximately the same size, we estimate that foreground corpora will
take about 6 hours to do preprocessing on both.  The distributional
processing will take about 11 hours for files of this size. Note that
the distributional processing will be shorter (we have not measured
this yet) if you are running on a previously processed background
corpus and use the associated cache (.pkl) file.

Thirdly, as we have already demonstrated, use of the Relevance score
as determined by Arguments 6 and 7 effect total processing time.  Each
web search takes about .8 seconds and there is one web search per
term, so 30K terms can take about 7 hours. For this reason, we
currently set a hard limit on the total number of terms in the output
to the minimum of: a) 30% of the terms produced by the previous stage
(these tend to be higher quality) and b) 30K terms (we assume it is
not worth it to wait longer than this for the results). When run on
5000 foreground and background files, the system typically ends up
generating relevance scores for 20-30K terms. Also the system will
create a dictionary of Relevance Scores for terms. You can keep one
such dictionary for all runs of termolator and send it to Termolator
via Argument 12. Each run will update this dictionary of Relevance
scores and prevent terms from being web-searched more than
once. Alternatively, if you set Argument 12 to False, variable $4 will
be used to create a dictionary of Relevance scores called
$4.outputweb.score. Either way, re-using relevance scores can result
in a significant speed-up.

In summary, the example described here would take about 24 hours to
run. However, the following factors could lead to substantially
shorter runtimes: (a) reusing preprocessed background data; (b) using
fewer than 5000 files; (c) opting for fewer than 30K terms for using
the websearch metric (see below); and (d) reusing relevance scores via
a dictionary.

9) Known Issues relating to the Relevance Score (arguments 6 and 7)
   A) Internet Outages can cause the cause the system to fail.
   B) The score is based on free Yahoo! web searches. If Yahoo! changes
      the way search results are printed out, this can result in the 
      system not working. In particular, the function "get_top_ten" in
      webscore.py may need to be changed to reflect such future changes.
   C) If extensive use is made of the system, Yahoo! may ban you from
      using their search engine for a time. We have used 40K or so
      searches at a time and not had this happen. However, if it did,
      a different way of accessing the search engine would be
      necessary and the setting up of a Yahoo account would be
      needed. Last time we checked, it would cost approximately .08
      cents per search through https://yboss.yahooapis.com/ysearch/web
      and further adjustments to the code would be required to make
      this work.
      
10) Known Issues with the POS tagger. We currently assume a maximum
   file size of 500000 bytes. This can be changed by editing the
   TERMOLATOR_POS.properties file. However, our current POS tagger
   uses lots of memory for large files. So it is not advisable to
   raise this amount by a lot. An alternative is to shorten or split
   very large files when using them with this system.

11) We experienced the following issue with version 0.1 which used
   Python 2 for nltk. We have not experienced it yet with version 0.2
   (which only uses Python 3) and do not currently know whether it is
   still an issue. The distributional system seems to clash with some
   instances of NLTK, but not others. We suspect that there may be
   some default encoding settings somewhere, which could default to
   ascii, rather than utf-8 for some setups. 

   For problematic setups, we have gotten the following error messages
   during the distributional phase of the system:

      "/usr/local/lib/python2.7/dist-packages/nltk/stem/porter.py", line 289, in _step1ab
      	if word.endswith("ied"):
	   UnicodeDecodeError: 'ascii' codec can't decode byte 0xc2 in position 7: ordinal not in range(128)

  Once again, we have not seen this error yet with the current all-python-3 version.

12) One of the newest features is the argument 14 (MINIMUM_PROBABILITY_OR_FALSE) feature. This feature is used to cause the system to ignore text that is too different from "normal" text.  Normal text is defined according to an N-gram character-based language model.  A number of character-based language models were tested, but the one that worked the best so far, assumed exactly 5 distinctions between characters: LETTER, WHITESPACE, DIGIT, PUNCTUATION, OTHER and looked for the average probability of 5-grams of these characters within a block of text. This, for example, tended to rule out text with an excess of punctuation and spaces. This language model was run on the Open American National Corpus text (see http://www.anc.org/) in the file all-OANC.txt. The average 5-gram probability is calculated for each segment in that corpus. The results are averaged and the standard deviation is calculated. This information is then used to classify sections in other text. 

The files gen2_lang.model and OANC.profile2 are derived in this manner and currently used to classify input to Termolator.  The function "train_on_OANC" in "make_language_model.py" can be used to derive the files and  "print_OANC_demo" can be used to gain some insight into how this works. Other language models which we did not end up using are also present in "make_language_model.py".
