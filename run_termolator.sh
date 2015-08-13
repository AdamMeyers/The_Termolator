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

## Step 1: Finding inline terms for foreground files
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

java -Xmx16g -cp ${TERMOLATOR}/TJet.jar FuseJet.Utils.Console ./temporary_TERMOLATOR_POS.properties internal_txt_fact_list internal_pos_list
## generates POS files

$TERMOLATOR/run_adjust_missing_char_pos.py internal_fact_pos_list
## adjustment for special characters

$TERMOLATOR/run_find_inline_terms.py internal_prefix_list $4
## runs inline term detection

$TERMOLATOR/run_make_term_chunk.py internal_pos_terms_abbr_list internal_foreground_tchunk_list

if [ "$5" = "True" ]; then
## Step 2 if not already processed, process the backgound files to find all
## inline terms
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
    $TERMOLATOR/run_find_inline_terms.py internal_prefix_list
    $TERMOLATOR/run_make_term_chunk.py internal_pos_terms_abbr_list internal_background_tchunk_list
fi

python $TERMOLATOR/term_extraction_v3/main.py internal_foreground_tchunk_list internal_background_tchunk_list > $4.all_terms

$TERMOLATOR/filter_term_output.py $4 $6 $7 

head -$8 $4.scored_output | cut -f 1 > $4.out_term_list
