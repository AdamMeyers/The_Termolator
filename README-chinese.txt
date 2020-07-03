This is the README  for the Chinese version of the Termolator, parts of which 
combines components of the following:

* The English Termolator
* An earlier (original) version of the Chinese Termolator (https://github.com/ivanhe/termolator/) created by Yifan He.
*  A Noun Chunker Generator by Leizhen Shi https://github.com/frank190/NounChunkerGenerator .
* And other work by Yuling Gu and Echo Hong. 

## USAGE

To perform Chinese terminology extraction, run the following command:

bash run_Termolator_chinese.sh True/False desired_output_name foreground_directory background_directory Termolator_directory

* The first variable should be True if the current Chinese dictionary
  is to be used by the system and False otherwise.

* The second variable is the file prefix you would like to use for output.

* The third variable is the directory containing foreground files (xml or txt files)

* The fourth variable is the directory containing background files (xml or txt files)

* The fifth variable is the program directory (that cotains the Termolator python files)

To test this program, we suggest that you look at the sample files in
the subdirectory "sample_chinese_documents". If you run the shell
command "run_sample" in that directory, Termolator will run using the
foreground files ( sampleRDG) and background files (sampleBackground)
in that directory.  These sample files are patents.  Note that this
command sets variables 1 to 5 as follows:

*  The first variable is set to "True", so the dictionary is used
* The prefix for all output files will be "sample", as indicated by
   the second variable
* The third and fourth variables set foreground and background to
   "sampleRDG" and "sampleBackground"
* The fifth variable is set to ".." the superordinate directory, which
   does in fact contain the program files for Termolator.

The script run_Termolator_chinese.sh processes the input files in the
following Steps:

Step 0 : Preparation -- cleaning up text input, e.g., removing xml and creating lists of files.

Step 1 : POS Tagging using the Brandeis tagger (Thank You to Nianwen Xue)

Step 2 : Generating Noun Chunks

Step 3 : Distributional ranking using the same system as the versions
of Termolator for other languages (English and French).

Step 4 : Accessor Variety Filter -- uses the access variety strategy
for removing ill-formed terms. 

Step 5: Create the final term list ("sample.out_term_list") in the
standard Termolator output format.

The Chinese Termolator uses the following files/components that are not used by
the English or the French version:

* accessorvariety.py
* chinese_noun_chunker_generator.py
* remove_xml_chinese.py
* Brandeis-CASIA-LanguageProcesser
* chinese1.txt
* sample_chinese_documents
* run_Termolator_chinese.sh
* README-chinese.txt
