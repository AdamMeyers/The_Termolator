#!/bin/bash

#GIVEN BY MAIN
#1: foreground dir
#2: background dir
#3: outname
#4: true or false process background files
#5: true or false process fore files
#6: true or false run web filter
#7: max nbr terms considered
#8: top n terms kept in the end
#9: termolator dir
#10: treetagger dir
#11: cutoff for lang model

foreground_location="${1%/}"
background_location="${2%/}"
outname="$3"
termolator_location="${9}"
treetagger_location="${10}"



echo "Foreground folder location: $foreground_location"
echo "Background folder location: $background_location"
echo "Treetagger location: $treetagger_location"
echo "Termolator location: $termolator_location"

#process background
if [ "${4,,}" = "true" ]; then
	#language model
	bash $termolator_location/run_lang_model_background_fr.sh "$background_location" $11 $9

	echo
	echo "Running TreeTagger to tag background documents."
	echo

	#tag documents
	bash $termolator_location/tag_back_and_foreground.sh "$background_location" "$treetagger_location/"
	#this creates [BACK]_tagged/, containing docs w title format [og_title]_tagged
	echo "$termolator_location/make_file_list.sh"

	bash $termolator_location/make_file_list.sh "${background_location}_tagged/"
	#this creates BACK_tagged_list.txt 
	python3 $termolator_location/file_list_error_fudge.py "${background_location}_tagged_list.txt"
	
	echo
	echo "Retrieving noun chunks from background documents."
	echo

	#get noun chunks
	echo "$termolator_location/getNounChunks ${background_location}_tagged_list.txt"
	
	## java $termolator_location/getNounChunks.java "${background_location}_tagged_list.txt"
	## ran javac getNounChunks.java
	## before making this change
	java $termolator_location/getNounChunks.java "${background_location}_tagged_list.txt"

	#this creates BACK_tagged_list.chunklist files and puts all docs.chunks back into BACK/
	
	echo
	echo "Running first stage filter on background documents."
	echo

	#stage 1
	python3 $termolator_location/stage1_driver.py "${background_location}_tagged_list.chunklist"
	#this writes docs.chunks.substring files to BACK/
	#creates BACK_tagged_list.chunklist.substring_list

fi

#process foreground	
if [ "${5,,}" = "true" ]; then
	#language model
	bash $termolator_location/run_lang_model_foreground_fr.sh "$foreground_location" $11
	
	echo
	echo "Running TreeTagger to tag foreground documents."
	echo

	#tag documents
	bash $termolator_location/tag_back_and_foreground.sh "$foreground_location" "$treetagger_location"
	#this creates [FORE]_tagged/, containing docs w title format [og_title]_tagged 

	echo "$termolator_location/make_file_list.sh"	
	bash $termolator_location/make_file_list.sh "${foreground_location}_tagged/"
	python3 $termolator_location/file_list_error_fudge.py "${foreground_location}_tagged_list.txt"
	#this creates FORE_tagged_list.txt
	
	echo
	echo "Retrieving noun chunks from foreground documents."
	echo

	#get noun chunks
	java $termolator_location/getNounChunks.java "${foreground_location}_tagged_list.txt"
	## java $termolator_location/getNounChunks "${foreground_location}_tagged_list.txt"	
	
	#this creates FORE_tagged_list.chunklist files and puts all docs.chunks back into FORE/

	echo
	echo "Running first stage filter on foreground documents."	
	echo

	#stage 1
	python3 $termolator_location/stage1_driver.py "${foreground_location}_tagged_list.chunklist"
	#this writes docs.chunks.substring files to FORE/
	#creates FORE_tagged_list.chunklist.substring_list

fi

echo
echo "Running distributional component."
echo

#stage 2
python3 $termolator_location/distributional_component.py NormalRank "${foreground_location}_tagged_list.chunklist.substring_list" "${outname}.all_terms" False "${background_location}_tagged_list.chunklist.substring_list"

echo 
echo "Running last stage filter."
echo

#stage 3
python3 $termolator_location/filter_term_output_fr.py $outname ${outname}.webscore $6 $7 ${outname}.internal_foreground_abbr_list False

echo
echo "Final list of terms can be found in ${outname}.scored_output."
echo "Done."
echo

head -$8 $3.scored_output | cut -f 1 > $3.out_term_list


