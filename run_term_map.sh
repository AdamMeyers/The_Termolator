#!/bin/sh

## $1 = foreground infiles -- file listing one txt file per line (same as input to Termolator)
## $2 = The .out_term_list file output from Termolator
## $3 = prefix for file output
## $4 = input file path -- path of directory containing foreground infiles
##      Example: 1 of the files listed in foreground_infile is dir1/dir2/blah.txt
##               the full path for that file is /home/meyers/stuff/dir1/dir2/blah.txt
##               Then $4 is /home/meyers/stuff
## $5  = TERMOLATOR directory -- can be set as an environment variable
## $6  = language acronym

$5/make_io_file.py $1 $3.internal_terms_list .terms

if [ "$6" = "zh" ]; then
   $5/summary/term_generator.py $3
fi

if [ "$6" = "fr" ]; then
   $5/summary/term_generator.py $3
fi
   
$5/run_term_map.py $2 $3.internal_terms_list $3.term_instance_map $4

grep "<term" $3.term_instance_map | sed 's/.*variants="//' |sed 's/".*//' > $3.edited_term_list
