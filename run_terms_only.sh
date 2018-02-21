#!/bin/sh

## $1 = input files -- file listing one txt file per line
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

## Step 1: Finding inline terms for foreground files
echo "Running Step 1: finding inline terms"
TERMOLATOR=${4:-$TERMOLATORPATH}
$TERMOLATOR/make_io_file.py $1 $3.internal_prefix_list BARE
$TERMOLATOR/make_io_file.py $1 $3.internal_abbr_list .abbr
$TERMOLATOR/make_io_file.py $1 $3.internal_pos_list .pos
$TERMOLATOR/make_io_file.py $1 $3.internal_txt_fact_list .txt3 .fact
$TERMOLATOR/make_io_file.py $1 $3.internal_fact_pos_list .fact .pos
$TERMOLATOR/make_io_file.py $1 $3.internal_txt_fact_pos_list .txt2 .fact .pos
$TERMOLATOR/make_io_file.py $1 $3.internal_pos_terms_abbr_list .pos .terms .abbr

$TERMOLATOR/make_termolator_fact_txt_files.py $3.internal_prefix_list $2
## generates fact, txt2 and txt3 files from input files

if test -f temporary_TERMOLATOR_POS.properties; then 
echo "Using Existing temporary_TERMOLATOR_POS.properties file"
else
echo "FuseJet.path1 = ${TERMOLATOR}/models" > temporary_TERMOLATOR_POS.properties
tail -n +2 ${TERMOLATOR}/TERMOLATOR_POS.properties >> temporary_TERMOLATOR_POS.properties
fi

echo "Calling Java Consule TJet jar with properties above"
java -Xmx16g -cp ${TERMOLATOR}/TJet.jar FuseJet.Utils.Console ./temporary_TERMOLATOR_POS.properties $3.internal_txt_fact_list $3.internal_pos_list
## generates POS files

echo "Generating POS files"
$TERMOLATOR/run_adjust_missing_char_pos.py $3.internal_fact_pos_list
## adjustment for special characters

echo "Adjusting for Special Chars"
$TERMOLATOR/run_find_inline_terms.py $3.internal_prefix_list $3 $5
    ## runs inline term detection

$TERMOLATOR/possibly_create_abbreviate_dicts.py $3.internal_abbr_list $3.dict_full_to_abbr $3.dict_abbr_to_full

echo "Cleaning up files"
rm -f $3.internal_prefix_list $3.internal_pos_list $3.internal_txt_fact_list $3.internal_fact_pos_list
rm -f $3.internal_txt_fact_pos_list $3.internal_pos_terms_abbr_list $3.internal_foreground_tchunk_list
rm -f $3.internal_background_tchunk_list $3.internal_abbr_list

