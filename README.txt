The Termolator Program 0.1 is licensed under the Apache license 2.0
(http://www.apache.org/licenses/LICENSE-2.0). It was created by Adam
Meyers, Yifan He, Zachary Glass and Shasha Liao and released in July,
2015.

The Termolator Program 0.2 is also licensed under the Apache license
2.0 (http://www.apache.org/licenses/LICENSE-2.0). It is a revision of
the original program. It was revised by Adam Meyers, John Ortega and
Vlad Tyshkevich. The main changes are: (i) bug fixes; (ii) The
new version uses Python 3 exclusively -- the Python 2 portions of the
original code have all been changed; (iii) additional features have
been added so the program will work better with legal text; (iv) changes
to the abbreviation program intended to improve precision and (v)
the capability to store web search based scores and look them up on
subsequent runs rather than recalculating them.

The Termolator takes two sets of documents as input a FOREGROUND set
and a BACKGROUND set and finds instances of terminology that are more
characteristic of the FOREGROUND than the background.  Input files can
be either .txt, .html or .xml (the latter only working if it uses HTML
style markup to delimit text). UTF-8 encoding (which includes ASCII)
is preferred, but ISO-8859-1 will work as well.

Details of the original system are described in
the accompanying paper (termolator-paper-2015.pdf):

	A. Meyers, Y. He, Z. Glass and O. Babko-Malaya (2015). The
	Termolator: Terminology Recognition based on Chunking-,
	Statistical- and Search-based Scores.  Workshop on Mining
	Scientific Papers: Computational Linguistics and
	Bibliometrics.

We have modified the system somewhat for this distribution to make it
easier to use.

Dependencies: If you have not already done so, you should install the
   python 3 version of the NLTK (see http://www.nltk.org/install.html). 
   To see if it is already installed, attempt to "import nltk" in 
   Python 3. If you get an error, than install it.

Instructions for Using program:

1) We will assume that $TERMOLATOR is the path containing the
   TERMOLATOR program. Setting an environmental variable (called
   TERMOLATOR) is suggested. 

2) To run the system, the command is

   $TERMOLATOR/run_termolator.sh FOREGROUND BACKGROUND EXTENSION OUTPUT_NAME TRUE-OR-FALSE TRUE-OR-FALSE 30000 5000 PROGRAM-DIRECTORY ADDITIONAL_TOPIC_STRING

The arguments are defined as follows:

   Argument 1 (FOREGROUND) = a file listing the documents in the foreground set
   Argument 2 (BACKGROUND) = a file listing the documents in the background set
   Argument 3 (EXTENSION) = the extension of input files
   Argument 4 (OUTPUT_NAME) = name of output file (without extension)
   Argument 5 (TRUE-OR-FALSE) = True or False (do background files need to be processed)
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

To test the program, we suggest going to one of our 3 test directories and running the command from there. Note that we will shorly 
be adding a corpus of court decisions, for which the legal topic features are useful. We have not yet tested whether these same features
are useful for the patent directory provided here.

   a) subdirectory: gutenberg-test
      command:      $TERMOLATOR/run_termolator.sh foreground.list background.list .htm knitting True True 30000 5000 $TERMOLATOR false
      
      -- The "True" setting will make this run take an extra 10 minutes to run about 600 
       	 web searches, but the results are more accurate as a result.

      -- These texts are taken from the English portion of Project Gutenberg, a repository of public 
      	 domain texts. The FOREGROUND is a set of chapters of "The Project Gutenberg eBook of Encyclopedia 
	 of Needlework", by Therese De Dillmont. The BACKGROUND is a random selection of documents from the 
	 same repository. Thus the resulting terminology list consists of terms in the domain of "knitting".
	 For more information of Project Gutenberg, go to: https://www.gutenberg.org/

   b) subdirectory: OANC-test
      command:      $TERMOLATOR/run_termolator.sh foreground.list background.list .txt biology True False 30000 5000 $TERMOLATOR false

      -- This run will be faster than the previous run per term generated. If False is replaced by True, 
      	 the system will take an extra 3 hours (about 1 second for each of 10,000 terms),
      	 but the results will be better.

      -- These texts are taken from the Open American National Corpus (OANC), a project devoted to collecting 
      	 freely available text for processing by computational linguistics. The FOREGROUND consists of 100 
	 biology related documents and the background consists of 100 random documents.  The resulting terminology 
	 are all about biology. For more information about the OANC, go to: http://www.anc.org/data/oanc/

   c) subdirectory: patent-test
      command:	    $TERMOLATOR/run_termolator.sh foreground.list background.list .XML surgery True False 30000 5000 $TERMOLATOR false

      -- This run should generate about 4700 terms. If False is changed to True, it will take an additional 
      	 1.5 hours, but  achieve better results.

      -- These documents are taken from Google patents. We downloaded files and divided them by the US patent 
      	 classes encoded in the documents. The foreground is a set of patents in class 606 (see the 
	 main_classification field in the XML), which are all about "Surgery".  The background is a set of 
	 randomly selected patents. The resulting terminology are all in the domain of "Surgery".

3) Choice of foreground and background documents. Different choices will effect the sort of terminology the system 
will recognize. We recommend between 500 and 5000 small files for both foreground and background or fewer large 
files. The example documents should give you some idea of what is possible. As the examples show, different numbers 
of files are possible.

We suggest creating directories which have only the input (foreground and background) files in them and then none of the 
files have any of the following file extensions, as these may be overwritten by the system: .abbr .fact .pos .tchunk 
.tchunk.nps .terms .txt2 .txt3 .

4) The output produce by the file includes the following, based on the OUTPUT_NAME:

   OUTPUT_NAME.out_term_list --- This is the final output, a list of the top N terms in order of rank, 
   			     	 where N = Argument 8 above

   OUTPUT_NAME.scored_output --- This is a superset of the previous list, approximately the top 30% of the terms
   			     	 considered by the system or the top K terms, if K is lower than 30%, and 
				 where K = Argument 7 above. If Argument 6 is set to True, a .8 seconds-long
				 web search is used to score each of the elements in this list. Thus 30,000 terms
				 will take around 24,000 seconds or just under 7 hours.

   		             --- There are several columns on each line, divided by tabs, as follows: 
			     	 Column 1 -- the term
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
   FILE.tchunk and FILE.tchunk.nps -- these are files that organize the terms from FILE.terms 
   	       	   		      into a form that the distributional system can process

6) Runtime

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
approximately the same size, we estimate that foreground corpora it
will take about 6 hours to do preprocessing on both.  The
distributional processing will take about 11 hours for files of this
size.

Thirdly, as we have already demonstrated, use of the Relevance score
as determined by Arguments 6 and 7 effect total processing time.  Each
web search takes about .8 seconds and there is one web search per
term, so 30K terms can take about 7 hours. For this reason, we
currently set a hard limit on the total number of terms in the output
to the minimum of: a) 30% of the terms produced by the previous stage
(these tend to be higher quality) and b) 30K terms (we assume it is
not worth it to wait longer than this for the results). When run on
5000 foreground and background files, the system typically ends up
generating relevance scores for 20-30K terms. Also variable $4 is used
to create a dictionary of Relevance Scores for particular terms. If
you call the program a second time with the same $4 value, this
dictionary will be loaded and relevance scores in for terms in the
dictionary will be looked up rather than calculated. This can speed up
run time significantly. It is of course possible to change the way the
system is run to store all relevance scores in one central
dictionary. We have not provided a script for this, but it is fairly
straight-forward to do.

In summary, the example described here would take about 24 hours to
run. However, the following factors could lead to substantially
shorter runtimes: (a) reusing preprocessed background data; (b) using
fewer than 5000 files; (c) opting for fewer than 30K terms for using
the websearch metric (see below); and (d) reusing relevance scores via
a dictionary.

7) Known Issues relating to the Relevance Score (arguments 6 and 7)
   A) Internet Outages can cause the cause the system to fail.
   B) The score is based on free Yahoo! web searches. If Yahoo! changes
      the way search results are printed out, this can result in the 
      system not working. In particular, the function "get_top_ten" in
      webscore.py may need to be changed to reflect such future changes.
   C) If extensive use is made of the system, Yahoo! may ban you from using
      their search engine. We have used 40K or so searches at a time and not had
      this happen. However, if it did, a different way of accessing the
      search engine would be necessary and the setting up of a Yahoo
      account would be needed. It would cost approximately .08 cents
      per search through https://yboss.yahooapis.com/ysearch/web
      and further adjustments to the code would be required to make this work.
      
8) Known Issues with the POS tagger. We currently assume a maximum
   file size of 500000 bytes. This can be changed by editing the
   TERMOLATOR_POS.properties file. However, our current POS tagger
   uses lots of memory for large files. So it is not advisable to
   raise this amount by a lot. An alternative is to shorten or split
   very large files when using them with this system.

9) We experienced the following issue with version 0.1 which used
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

  Once again, we have not tested the all-python-3 version to know whether or not
  this is still an issue.

