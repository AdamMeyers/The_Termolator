#!/bin/bash

#RUN FR LANGUAGE MODEL: BACKGROUND

#args
#1: background loc
#2: cutoff
#3: termolator directory

background_location="$1"
cutoff="$2"

background_location_og="${background_location}"

#make new background location to hold all temp/fact files

cp -r "${background_location_og}" "${background_location}_tempfiles/"
background_location="${background_location_og}_tempfiles"

#make list of background files
bash $3/make_file_list.sh "${background_location}/"
#this creates [BACK]_tempfiles_list.txt

python3 $3/make_io_file.py "${background_location}_list.txt" "${background_location_og}_test.internal_prefix_list" BARE
python3 $3/make_termolator_fact_txt_files.py "${background_location_og}_test.internal_prefix_list" .txt
python3 $3/make_io_file.py "${background_location}_list.txt" "${background_location_og}_test.internal_txt_fact_list" .txt3 .fact2
python3 $3/make_io_file.py "${background_location}_list.txt" "${background_location_og}_test.filter_io" .txt3 .fact .fact2
python3 $3/run_make_filtered_fact_files_FR.py "${background_location_og}_test.filter_io" $2

#create filtered documents
python3 $3/make_filtered_doc_fr.py "${background_location_og}_test.filter_io"

#after have filtered docs, place in new "filtered doc" dir
mkdir "${background_location_og}_filtered" 
background_location="${background_location_og}_filtered"

cp "${background_location_og}_tempfiles/"*.txt3.txt "${background_location}/"

#remove tempfiles folder
rm -r "${background_location_og}_tempfiles/" "${background_location_og}_tempfiles_list.txt"





