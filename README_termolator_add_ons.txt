These programs were developed on some linux machines, but tested on a
few linux machines and one MacBook Air. For the current version of the
program, the MAC (1.7 Core i7, 8 RAM), turned out not to have enough
memory to create shelve (slv) files from a Wikipedia dump, although
this was possible on the linux machines, including one 3.2 i5 machine
with 8gb RAM. My current theory is that the key factor is that the
linux machine had more swap space.

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

4) Sample command inside of patent-test subdirectory:
   ../run_term_map.sh foreground.list surgery.out_term_list surgery . ..
   (where .. refers to the main termolator directory containing patent-test
    and . refers to patent-test).

B. The Summary Creation Program -- this program creates glossary-like
   information for each of a list of terms. Warning: this may require
   a lot of disk space (at least 90 gb on a linux machine).

1) Before using this program, you should first download a current
   wikipedia and two packages for reading in wikipedia into easily
   digestable forms.

   A) Get a Wikipedia .xml file:

I suggest downloading the file from:

https://meta.wikimedia.org/wiki/Data_dump_torrents#English_Wikipedia

I have so far tested the program with the following 2 files:
     enwiki-20190101-pages-articles-multistream.xml
	and
     enwiki-20200401-pages-articles-multistream.xml
In both cases the files were around 16-17gb and I used torrents. There
seem to be some similarly named files that are much smaller 3-6gb and that
do not work. They seem to contain different information. So beware     

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
      the other two files created. This took about 30 minutes to run on a
      a MacBook Air.

   F) Download wikiextractor from
      https://github.com/attardi/wikiextractor (Version: 2.75)(March
      4, 2017) Author: Giuseppe Attardi (attardi@di.unipi.it),
      University of Pisa 

   G) Run the program as follows:
      WikiExtractor.py latest_wikipedia.xml -o wiki-extractor-output
      -- latest_wikipedia file can either be the path of your wikipedia xml file or link to it
      -- wiki-extractor-output is the directory where you will store the wikipedia article text
      	 files.  I suggest using this exact directory name because my programs
	 assume it as a default, e.g., see get_first_paragraph_from_wikipedia_xml_shelve
	 However, it is possible to change this to some other directory name.
      -- This took about 7.5 hours to run on a MacBook Air. All the extracted files take 
         up about 90gb of space on a linux machine and 180gb on an Apple.

2) To run the Summary program, first run Termolator and the term map
program descried above. The output of the term map program will be
input to this program. Then use the script run_summary.sh with the
following arguments:

   -- The first argument is a prefix 
      -- there should be a .term_instance_map file with that prefix to use as input
      -- an output file of the form prefix.summary will be created by the program
   -- The second argument is the directory where the text files referenced in the
      .term_instance_map file are found.
   -- The third argument is the program directory
   -- The fourth argument is the txt file type. .txt3 is typical for Termolator files,
      but .txt2 or .txt is also possible -- but note all file types must begin with a 
      period.

   For example:
       from the patent-test subdirectory (using the surgery.term_instance_map
       created when testing the term map program):

       
       run_summary.sh updated_cancer pubmed_textfiles /home/meyers/Termolator2/working_copy      

   In theory, there could be other parameters that could be set. However, for
   now the shell will assume several defaults.

2.1) Some details about .slv files

   The first time the program is run it will create 2 shelve files:
   swiki.slv and wiki.slv. In subsequent runs the program uses these
   shelve files and the system takes a much shorter time to run. For
   example, on a 3.2 Ghz i5 linux box with 8RAM, the first run took
   2.5 hours and a subsequent run took only 1 minute. For the test case,
   we ran the surgery term example above. It may have run a bit faster
   on a more powerful linux machine (but I have not verified this).

   Once created, the slv files store information about wikipedia in an
   efficient way and are used whenever you run the program again. If
   you end up updating your wikipedia xml file, you should delete
   these files, repeat all the previous steps to create the various files
   derived from wikipedia, including these .slv files.

   Both files .slv files are placed in the DICT_DIRECTORY (assigned in
   term_utilities.py), which I am assuming is also the directory
   containing all Termolator .py files.  It is also assumed that other
   files are in this same DICT_DIRECTORY, including: (a)
   wiki-extract-output (the directory containing the paragraphs
   extracted from the wikipedia xml file); and (b) redirect_file by
   default: (wiki-basic-output/articles.csv) To change these defaults,
   see the definition of the function
   get_first_paragraph_from_wikipedia_xml_shelve in term_summary.py

   Please note that there may be a minimum requirement for the .slv
   files based on wikipedia to be created. We were unsuccessful
   running the above command on an a MacBook with 8gb of RAM. The
   error message was "HASH: Out of overflow pages." I suspect, that my
   MAC did not have sufficient SWAP space (but the linux computers
   did). 

   Another factor that could be important for debugging is that the
   successful test was run using a solid state file system that was
   mounted on a network. It is possible that a lot of the file
   creation would take longer using an old-fashioned SATA drive, due
   to slower read/write times. 

3) The files used by the summary program include:
   term_line_summary.py
   make_language_model.py -- also used by Termolator
      plus the language model and profile files read in by load_language_model
      	   (see the global variables language_model_file and profile_file 
	    in term_line_summary.py)
   term_summary.py
   term_utilities.py
   run_summary.sh
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
  
