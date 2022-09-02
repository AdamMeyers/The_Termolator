#!/usr/bin/env bash

# Author: Yuling Gu
# Date: Jun 21, 2020
# Description: Bash script with the current implementations of the
# Chinese Termolator organized.
# Usage format : run_Termolator_chinese.sh $1 $2 $3 $4 $5
# $1 = True or False (do we want to use the chinese dictionary?)
# $2 = The prefix of desired_output_name
# $3 = foreground directory
# $4 = background directory
# $5 = Termolator directory
# $6 = True or False (Are foreground/background files in plain text format?)
# Usage example: bash run_Termolator_chinese.sh True desired_output_name foreground directory, background directory Termolator directory

# Using the xml files in "sample_chinese_documents" folder (sampleBackground, sampleRDG) as test cases,
# steps for running the updated Chinese termolator from  scratch:

## see test_sample/run_sample

echo -e "Step 0 : Preparation work\nCleaning up foreground and foreground text input..."

if [ ${6^^} = "FALSE" ]; then
  # Note: Makes use of term_utilities.py

  # Generate foreground and background filelists
  ls -1 $3 | sed -e "s/^/$3\//" > foregroundList.txt
  ls -1 $4 | sed -e "s/^/$4\//" > backgroundList.txt

  # Remove xml tags and clean up the file of unwanted tags non-characters
  python3 $5/remove_xml_chinese.py backgroundList.txt cleaned
  python3 $5/remove_xml_chinese.py foregroundList.txt cleaned

  # Create directories to organize cleaned xml files
  DIR=test_cleaned
  if [ -d "$DIR" ]; then
      rm -r $DIR
      echo "Old $DIR removed!"
  fi
  mkdir $2_cleaned
  mkdir $2_cleaned/background/
  mkdir $2_cleaned/foreground/

  for file in "$3/*cleaned.xml"; do
    mv "$file" "$2_cleaned/foreground/$(basename "$file" .xml).txt"
  done
  for file in "$4/*cleaned.xml"; do
    mv "$file" "$2_cleaned/background/$(basename "$file" .xml).txt"
  done

  ls -1 $2_cleaned/background/ | sed -e "s/^/$2_cleaned\/background\//" > cleaned_backgroundList.txt
  ls -1 $2_cleaned/foreground/ | sed -e "s/^/$2_cleaned\/foreground\//" >  cleaned_foregroundList.txt
else
  mkdir $2_cleaned
  mkdir $2_cleaned/background/
  mkdir $2_cleaned/foreground/
  mv $3/* $2_cleaned/foreground/
  mv $4/* $2_cleaned/background/
fi

echo
echo -e "Step 1 : Tagging using Brandeis tagger\nRunning Brandeis Chinese word segmenter and part-of-speech tagger..."
# create directories for POS tagged files
DIR=$2_tagged
if [ -d "$DIR" ]; then
    rm -r $DIR
    echo "Old $DIR removed!"
fi
mkdir $2_tagged
mkdir $2_tagged/background/
mkdir $2_tagged/foreground/

# Run Brandeis Chinese word segmenter and part-of-speech tagger
## cd $5/Brandeis-CASIA-LanguageProcesser
java -Xmx25000m -cp "$5/Brandeis-CASIA-LanguageProcesser/WS_POS_brandeis.jar" brandeis.transition.wordseg.WordSegmentToolkit -mode test -model $5/Brandeis-CASIA-LanguageProcesser/model/train_brandeis.model.gz -test $2_cleaned/background/ -out $2_tagged/background
java -Xmx25000m -cp "$5/Brandeis-CASIA-LanguageProcesser/WS_POS_brandeis.jar" brandeis.transition.wordseg.WordSegmentToolkit -mode test -model $5/Brandeis-CASIA-LanguageProcesser/model/train_brandeis.model.gz -test $2_cleaned/foreground/ -out $2_tagged/foreground

echo -e "Step 2 : Noun Chunker Generator\nGenerating .tchunk and .pos files for the distributional ranking..."
# noun_chunker_generator.py implemented by Leizhen
python3 $5/chinese_noun_chunker_generator.py -f $2_tagged/foreground -b $2_tagged/background -d $1 -p $5
echo

echo -e "Step 3 : Distributional ranking\nGenerating .tchunk and .pos files for the distributional ranking...\n"
# MEASURES = ['TFIDF', 'DRDC', 'KLDiv', 'Weighted'] , same as English version
ls -1 output_foreground/ | grep "tchunk$" | awk '{print "output_foreground/"$1}' > $2.internal_foreground_tchunk_list
ls -1 output_background/ | grep "tchunk$" | awk '{print "output_background/"$1}' > $2.internal_background_tchunk_list
python3 $5/distributional_component.py NormalRank $2.internal_foreground_tchunk_list $2.all_terms False $2.internal_background_tchunk_list

echo -e "Step 4 : Accessor Variety Filter\nFiltering all terms obtained previously...\n"
python3 $5/accessorvariety.py $2.all_terms foreground_tchunk_list > $2.AV_filtered_terms
echo -e "All steps completed! Final output file: $2.AV_filtered_terms"

cut -f 1 $2.AV_filtered_terms > $2.out_term_list
