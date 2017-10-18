#!/bin/sh

## $1 = 1 foreground infile -- no file type
## $2 = background_infiles -- file listing one text file per line
## $3 = file type of input files (.htm .html or .txt)
## $4 = output_file_name 
## $5 = True or False (do background files need to be processed)
##      If False, stored background cache file will be loaded (see $13).
##      If True, background information will be stored as a cache file (see Argument 13).
## $6 = True or False (run Web-based filter?)
## $7 = Maximum Number of Terms Considered (suggested = 10000)
## $8 = Top N -- number of terms you want to keep in the end (suggested 1000)
## $9 = TERMOLATOR -- can be set as an environment variable
## $10 = names of additional topic areas that should be included:
##       these correspond to dictionaries listed in utilities.py
##       topic names should be of the following format:
##       "topic1 topic2 topic3 topic4" -- topics should be
##       separated by '+, i.e., 'legal+financial'. The value should
##       be False if not used
## refer to as ${10}
## $11 = If True, means skip preprocessing of Foreground
##       This comes in useful if you want to run the same Foreground 
##       with different backgrounds or if for any reason, you have
##	 already preprocessed the foreground file. So usually, this field should just
##	 contain "False".
## $12 = general_file_name (or False), if different from $4 (for reuse of webscores, lemmas, etc.)
## $13 = background cache file (to save to or to load from) or False
##       if False, the default filename: ranking.pkl will be used


echo "The Output File is: $4"
echo "background files processed? $5"
echo "web-based filter $6"
echo "max number of terms? $7"
echo "keep terms? $8"
echo "termolator path $9"
echo "shared general filename (webscore, lemmas, etc.) ${12}"
echo "use previous saved pickel file for terms ${13}"

## Step 1: Finding inline terms for foreground files
echo "Running Step 1: finding inline terms for foreground files"
TERMOLATOR=${9:-$TERMOLATORPATH}

echo $1 > $4.internal_prefix_list
echo "$1.abbr" > $4.internal_abbr_list 
echo "$1.tchunk" > $4.internal_foreground_tchunk_list
$TERMOLATOR/make_io_file.py $2 $4.internal_background_tchunk_list .tchunk

if [ "${12}" = "False" ]; then
   lemma_dict="$4_lemma.dict"
   web_scores="$4.webscore"
else
   lemma_dict="${12}_lemma.dict"
   web_scores="${12}.webscore"
fi

echo "cached dictionary names: ${lemma_dict} and ${web_scores}"


## not sure if this really is necessary
## $TERMOLATOR/possibly_create_abbreviate_dicts.py $4.internal_abbr_list $4.dict_full_to_abbr $4.dict_abbr_to_full

if [ "$5" = "True" ]; then
## Step 2 if not already processed, process the backgound files to find all
## inline terms
    echo "Processing background files"
    $TERMOLATOR/make_io_file.py $2 $4.internal_prefix_list BARE
    $TERMOLATOR/make_io_file.py $2 $4.internal_pos_list .pos
    $TERMOLATOR/make_io_file.py $2 $4.internal_txt_fact_list .txt3 .fact
    $TERMOLATOR/make_io_file.py $2 $4.internal_fact_pos_list .fact .pos
    $TERMOLATOR/make_io_file.py $2 $4.internal_txt_fact_pos_list .txt2 .fact .pos
    $TERMOLATOR/make_io_file.py $2 $4.internal_pos_terms_abbr_list .pos .terms .abbr
    $TERMOLATOR/make_termolator_fact_txt_files.py $4.internal_prefix_list $3
## generates fact, txt2 and txt3 files from input files
    java -Xmx16g -cp ${TERMOLATOR}/TJet.jar FuseJet.Utils.Console ./temporary_TERMOLATOR_POS.properties $4.internal_txt_fact_list $4.internal_pos_list
## generates POS files
    $TERMOLATOR/run_adjust_missing_char_pos.py $4.internal_fact_pos_list
## adjustment for special characters
    $TERMOLATOR/run_find_inline_terms.py $4.internal_prefix_list false ${10}
    $TERMOLATOR/run_make_term_chunk.py $4.internal_pos_terms_abbr_list $4.internal_background_tchunk_list $4.dict_abbr_to_full ${10} ${lemma_dict}
fi

if [ "${11}" = "False" ]; then
    echo "$1.pos" > $4.internal_pos_list 
    echo "$1.txt3;$1.fact" > $4.internal_txt_fact_list 
    echo "$1.fact;$1.pos" > $4.internal_fact_pos_list 
    echo "$1.txt2;$1.fact;$1.pos" > $4.internal_txt_fact_pos_list 
    echo "$1.pos;$1.terms;$1.abbr" > $4.internal_pos_terms_abbr_list
    $TERMOLATOR/make_one_termolator_fact_txt_file.py $1 $3
## generates fact, txt2 and txt3 files from input files
    if test -f temporary_TERMOLATOR_POS.properties; then 
        echo "Using Existing temporary_TERMOLATOR_POS.properties file"
    else
        echo "FuseJet.path1 = ${TERMOLATOR}/models" > temporary_TERMOLATOR_POS.properties
        tail -n +2 ${TERMOLATOR}/TERMOLATOR_POS.properties >> temporary_TERMOLATOR_POS.properties
    fi

    echo "Calling Java Consule TJet jar with properties above"
    java -Xmx16g -cp ${TERMOLATOR}/TJet.jar FuseJet.Utils.Console ./temporary_TERMOLATOR_POS.properties $4.internal_txt_fact_list $4.internal_pos_list
## generates POS files

    echo "Generating POS files"
    $TERMOLATOR/run_adjust_missing_char_pos.py $4.internal_fact_pos_list
    ## adjustment for special characters

    echo "Adjusting for Special Chars"
    $TERMOLATOR/run_find_inline_terms.py $4.internal_prefix_list $4 ${10}
    $TERMOLATOR/possibly_create_abbreviate_dicts.py $4.internal_abbr_list $4.dict_full_to_abbr $4.dict_abbr_to_full
    ## runs inline term detection

    echo "Chunking for inline term detection"
    ## $TERMOLATOR/run_make_term_chunk.py $4.internal_pos_terms_abbr_list $4.internal_foreground_tchunk_list
    $TERMOLATOR/run_make_term_chunk.py $4.internal_pos_terms_abbr_list $4.internal_foreground_tchunk_list $4.dict_abbr_to_full ${10} ${lemma_dict}
else
    $TERMOLATOR/possibly_create_abbreviate_dicts.py $4.internal_abbr_list $4.dict_full_to_abbr $4.dict_abbr_to_full
fi

if [ "$5" = "True" ]; then
    echo "calling distributional_component.py in term_extration using foreground and background tchunk list with output to file $4.all_terms"
    $TERMOLATOR/distributional_component.py NormalRank $4.internal_foreground_tchunk_list $4.all_terms ${13} $4.internal_background_tchunk_list
else
    echo "calling distributional_component.py in term_extration using foreground and stored background statistics with output to file $4.all_terms"
   $TERMOLATOR/distributional_component.py RankFromPrevious $4.internal_foreground_tchunk_list $4.all_terms ${13} $4.internal_background_tchunk_list 
fi

if [ "${12}" = "False" ]; then
   echo "calling filter_term_output.py with filter_term_output.py $4 ${web_scores} $6 $7 ${10}"
   $TERMOLATOR/filter_term_output.py $4 ${web_scores} $6 $7 $4.internal_abbr_list ${10}
else
   echo "calling filter_term_output.py with filter_term_output.py $4 ${web_scores} $6 $7 ${10}"
   $TERMOLATOR/filter_term_output.py $4 ${web_scores} $6 $7 $4.internal_abbr_list ${10}
fi

echo "Final terms can be found in $4.out_term_list from the scored file in $4.scored_output"
## head -$8 $4.scored_output | cut -f 1 > $4.out_term_list

$TERMOLATOR/make_final_output_file.py $4.scored_output ${lemma_dict} $8 $4.out_term_list


echo "Cleaning up files"
rm -f $4.internal_prefix_list $4.internal_pos_list $4.internal_txt_fact_list $4.internal_fact_pos_list
rm -f $4.internal_txt_fact_pos_list $4.internal_pos_terms_abbr_list $4.internal_foreground_tchunk_list
rm -f $4.internal_background_tchunk_list $4.internal_abbr_list

