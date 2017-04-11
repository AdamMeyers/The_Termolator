#!/bin/sh

## $1 = input infiles -- file listing one txt file per line
## $2 = file type of input files (.htm .html or .txt)
## $3 = output_file_name 
## $4 = TERMOLATOR -- can be set as an environment variable
## $5 = names of additional topic areas that should be included:
##       these correspond to dictionaries listed in utilities.py
##       topic names should be of the following format:
##       "topic1 topic2 topic3 topic4" -- topics should be
##       separated by '+, i.e., 'legal+financial'. The value should
##       be False if not used

echo "The Output File is: $3"
echo "termolator path $4"

TERMOLATOR=${4:-$TERMOLATORPATH}
$TERMOLATOR/make_io_file.py $1 internal_prefix_list BARE
$TERMOLATOR/make_termolator_fact_txt_files.py internal_prefix_list $2
## generates fact, txt2 and txt3 files from input files

$TERMOLATOR/run_abbreviate.py internal_prefix_list $3 ${5}
## runs inline term detection

