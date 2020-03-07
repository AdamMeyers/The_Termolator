#!/usr/bin/env python3

#RUN FR LANGUAGE MODEL: FOREGROUND

#args:
#1: foreground loc
#2: cutoff for lang model

foreground_location="$1"
cutoff="$2"

foreground_location_og="${foreground_location}"

#make new background location to hold all temp/fact files

cp -r "${foreground_location_og}" "${foreground_location}_tempfiles/"
foreground_location="${foreground_location_og}_tempfiles"

#make list of foreground files
bash make_file_list.sh "${foreground_location}/"
#this creates [FORE]_tempfiles_list.txt

./make_io_file.py "${foreground_location}_list.txt" "${foreground_location_og}_test.internal_prefix_list" BARE
./make_termolator_fact_txt_files.py "${foreground_location_og}_test.internal_prefix_list" .txt
./make_io_file.py "${foreground_location}_list.txt" "${foreground_location_og}_test.internal_txt_fact_list" .txt3 .fact2
./make_io_file.py "${foreground_location}_list.txt" "${foreground_location_og}_test.filter2_io" .txt3 .fact .fact2
./run_make_filtered_fact_files_FR.py "${foreground_location_og}_test.filter2_io" $2

#create filtered documents
./make_filtered_doc_fr.py "${foreground_location_og}_test.filter2_io"

#after have filtered docs, place in new "filtered doc" dir
mkdir "${foreground_location_og}_filtered" 
foreground_location="${foreground_location_og}_filtered"

cp "${foreground_location_og}_tempfiles/"*.txt3.txt "${foreground_location}/"

#remove tempfiles folder
rm -r "${foreground_location_og}_tempfiles/" "${foreground_location_og}_tempfiles_list.txt"




