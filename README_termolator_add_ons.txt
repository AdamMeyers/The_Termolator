A. Creating term map and edited edited term list file.

1) use script run_term_map.sh with 5 arguments
   -- Argument 1: list of foreground files
   -- Argument 2: The .out_term_list file output from Termolator
   -- Argument 3: The prefix for file output
   -- Argument 4: Input file path -- path of directory containing foreground infiles
   -- Argument 5: TERMOLATOR directory
2) output includes:
   -- A .term_instance_map file (a file indicating where terms and morphological
      variants are located inside of the foreground files) Also provides distributional
      information. By default, all terms not found in at least 3 files are eliminated.
      The script does not currently allow you to modify this parameter, but it would be
      simple to change the scripts so this was possible.
   -- A .edited_term_list file -- this is essentially an edited
      version of .out_term_list. The terms not occuring in 3 or more files are removed.
      -- this is created via the UNIX utility "grep"
3) Files used include:
   -- run_term_map.sh (the shell script to be run with 5 arguments)
   -- make_io_file.py -- program used for getting various input file
      lists (also used by the main run_termolator.sh script)
   -- run_term_map.py -- the main python script for run_term_map
   -- get_term_maps.py -- the main functions used by run_term_map.py

B. The Summary Creation Program -- this program creates glossary-like
   information for each of a list of terms.

1) Before using this program, you should first download a current
   wikipedia and two packages for reading in wikipedia into easily
   digestable forms.

   A) Get a Wikipedia .xml file:

   I downloaded enwiki-20190101-pages-articles-multistream.xml from
   XXX as my main input file, but a more current version (if
   available) would be advisable.

   B) Download the wiki-basic-stream.py from github:
      https://github.com/jeffheaton/article-code/blob/master/python/wikipedia/wiki-basic-stream.py
      There was no version information in the file. But it contained
      the following line about it rights: "Copyright 2017 by Jeff
      Heaton, released under the The GNU Lesser General Public License
      (LGP L)

   C) Modify this file. Set the variables PATH_WIKI_XML and FILENAME_WIKI as appropriate.
      PATH_WIKI_XML should be the path where you have your wikipedia xml file.
      FILENAME_WIKI should be the name of your wikipedia xml file

   D) run the wiki-basic-stream.py

   E) It will create 3 csv files. We will use the "articles.csv" file to
      identify "redirects" in wikipedia, i.e., if we look up term X,
      but the system uses the entry for the related term Y (e.g., if X
      is "html" and Y is "hypertext markup language").  This filename
      and directory (wiki-basic-output/articles.csv) is the default
      file used in get_first_paragraph_from_wikipedia_xml_shelve and
      is currently set in the scripts described below. We will not use 
      the other two files created.

   F) Download wikiextractor from https://github.com/attardi/wikiextractor
      (Version: 2.75)(March 4, 2017)
      Author: Giuseppe Attardi (attardi@di.unipi.it), University of Pisa

   G) Run the program as follows:
      WikiExtractor.py latest_wikipedia.xml -o wiki-extractor-output
      -- latest_wikipedia file can either be the path of your wikipedia xml file or link to it
      -- wiki-extractor-output is the directory where you will store the wikipedia article text
      	 files.  I suggest using this exact directory name because my programs
	 assume it as a default, e.g., see get_first_paragraph_from_wikipedia_xml_shelve
	 However, it is possible to change this to some other directory name.

2) To run the Summary program, use the script run_summary.sh with the following two arguments:
   -- The first argument is a prefix 
      -- there should be a .term_instance_map file with that prefix to use as input
      -- an output file of the form prefix.summary will be created by the program
   -- The second argument is the directory where the text files referenced in the
      .term_instance_map file are found.
   -- The third argument is the program directory

   For example:
       run_summary.sh updated_cancer pubmed_textfiles /home/meyers/Termolator2/working_copy

   In theory, there could be other parameters that could be set. However, for
   now the shell will assume several defaults.

   The first time the program is run it will create 2 shelve files:
   swiki.slv and wiki.slv Both files will be placed in the
   DICT_DIRECTORY (assigned in term_utilities.py), which I am assuming
   is also the directory containing all Termolator .py files.  It is
   also assumed that other files are in this same
   DICT_DIRECTORY, including: (a) wiki-extract-output (the directory
   containing the paragraphs extracted from the wikipedia xml file);
   and (b) redirect_file by default: (wiki-basic-output/articles.csv)
   To change these defaults, see the definition of the function
   get_first_paragraph_from_wikipedia_xml_shelve in term_summary.py

   So the first time you run the summary program will take a little bit more time than
   subsequent runs.

   These files store information about wikipedia in an efficient way and are used
   whenever you run the program again. If you end up updating your wikipedia xml file,
   you should delete these files, repeat step 1 to create new wikipedia files and then
   new .slv files will be created the next time you run this.

3) The files used by the summary program include:
   term_line_summary.py
   make_language_model.py -- also used by Termolator
      plus the language model and profile files read in by load_language_model
      	   (see the global variables language_model_file and profile_file 
	    in term_line_summary.py)
   term_summary.py
   term_utilities.py
   files for representing wikipedia information including:
        * The files in the directory: wiki-extractor-output
	  generated by running WikiExtractor.py (see above_
        * wiki-basic-output/articles.csv  -- the 
	  file generated by running wiki-basic-stream.py
        * The first time you run the summary program, the
	  files wiki.slv and swiki.slv will replace the 
	  above information. These files will be loaded
	  instead.
4) The program calls the following python packages:
       requests, re, math, time, csv, shelve
  
