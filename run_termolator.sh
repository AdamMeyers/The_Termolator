#!/bin/sh

## $1 = foreground_infiles -- file listing one txt file per line
## $2 = background_infiles -- file listing one text file per line
## $3 = file type of input files (.htm .html or .txt)
## $4 = output_file_name 
## $5 = True or False (do background files need to be processed)
## $6 = True or False (run Web-based filter?)
## $7 = Maximum Number of Terms Considered (suggested = 30000)
## $8 = Top N -- number of terms you want to keep in the end (suggested 5000-10000)
## $9 = TERMOLATOR -- can be set as an environment variable
## $10 = names of additional topic areas that should be included:
##       these correspond to dictionaries listed in utilities.py
##       topic names should be of the following format:
##       "topic1 topic2 topic3 topic4" -- topics should be
##       separated by '+, i.e., 'legal+financial'. The value should
##       be False if not used
## refer to as ${10}

echo "The Output File is: $4"
echo "background files processed? $5"
echo "web-based filter $6"
echo "max number of terms? $7"
echo "keep terms? $8"
echo "termolator path $9"

## Step 1: Finding inline terms for foreground files
echo "Running Step 1: finding inline terms for foreground files"
TERMOLATOR=${9:-$TERMOLATORPATH}
$TERMOLATOR/make_io_file.py $1 internal_prefix_list BARE
$TERMOLATOR/make_io_file.py $1 internal_pos_list .pos
$TERMOLATOR/make_io_file.py $1 internal_txt_fact_list .txt3 .fact
$TERMOLATOR/make_io_file.py $1 internal_fact_pos_list .fact .pos
$TERMOLATOR/make_io_file.py $1 internal_txt_fact_pos_list .txt2 .fact .pos
$TERMOLATOR/make_io_file.py $1 internal_pos_terms_abbr_list .pos .terms .abbr
$TERMOLATOR/make_io_file.py $1 internal_foreground_tchunk_list .tchunk
$TERMOLATOR/make_io_file.py $2 internal_background_tchunk_list .tchunk
$TERMOLATOR/make_termolator_fact_txt_files.py internal_prefix_list $3
## generates fact, txt2 and txt3 files from input files

echo "FuseJet.path1 = ${TERMOLATOR}/models" > temporary_TERMOLATOR_POS.properties
tail -n +2 ${TERMOLATOR}/TERMOLATOR_POS.properties >> temporary_TERMOLATOR_POS.properties

echo "Calling Java Consule TJet jar with properties above"
java -Xmx16g -cp ${TERMOLATOR}/TJet.jar FuseJet.Utils.Console ./temporary_TERMOLATOR_POS.properties internal_txt_fact_list internal_pos_list
## generates POS files

echo "Generating POS files"
$TERMOLATOR/run_adjust_missing_char_pos.py internal_fact_pos_list
## adjustment for special characters

echo "Adjusting for Special Chars"
$TERMOLATOR/run_find_inline_terms.py internal_prefix_list $4 ${10}
## runs inline term detection

echo "Chunking for inline term detection"
$TERMOLATOR/run_make_term_chunk.py internal_pos_terms_abbr_list internal_foreground_tchunk_list

if [ "$5" = "True" ]; then
## Step 2 if not already processed, process the backgound files to find all
## inline terms
    echo "Processing background files"
    $TERMOLATOR/make_io_file.py $2 internal_prefix_list BARE
    $TERMOLATOR/make_io_file.py $2 internal_pos_list .pos
    $TERMOLATOR/make_io_file.py $2 internal_txt_fact_list .txt3 .fact
    $TERMOLATOR/make_io_file.py $2 internal_fact_pos_list .fact .pos
    $TERMOLATOR/make_io_file.py $2 internal_txt_fact_pos_list .txt2 .fact .pos
    $TERMOLATOR/make_io_file.py $2 internal_pos_terms_abbr_list .pos .terms .abbr
    $TERMOLATOR/make_termolator_fact_txt_files.py internal_prefix_list $3
## generates fact, txt2 and txt3 files from input files
    java -Xmx16g -cp ${TERMOLATOR}/TJet.jar FuseJet.Utils.Console ./temporary_TERMOLATOR_POS.properties internal_txt_fact_list internal_pos_list
## generates POS files
    $TERMOLATOR/run_adjust_missing_char_pos.py internal_fact_pos_list
## adjustment for special characters
    $TERMOLATOR/run_find_inline_terms.py internal_prefix_list false ${10}
    $TERMOLATOR/run_make_term_chunk.py internal_pos_terms_abbr_list internal_background_tchunk_list
fi

echo "calling distributional_component.py in term_extration using foreground and background tchunk list with output to file $4.all_terms"

python $TERMOLATOR/distributional_component.py internal_foreground_tchunk_list internal_background_tchunk_list > $4.all_terms

echo "calling filter_term_output.py with filter_term_output.py $4 $4.outputweb.score $6 $7 ${10}"
$TERMOLATOR/filter_term_output.py $4 $4.outputweb.score $6 $7 ${10}

echo "Final terms can be found in $4.out_term_list from the scored file in $4.scored_output"
head -$8 $4.scored_output | cut -f 1 > $4.out_term_list
