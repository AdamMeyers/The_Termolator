#!/bin/sh

## $1 = type of issue (broad or narrow)
## $2 = issue ID

echo "The issue is of type: $1"
echo "The issue ID is: $2"

TERMOLATOR=${3:-$TERMOLATORPATH}

## Step 1: Generate the text cases and classify into broad/narrow issues
echo "Retrieve Supreme Court legal cases in folder 'text_cases'"
python3 $TERMOLATOR/legal_feature/supreme_court.py
python3 $TERMOLATOR/legal_feature/classify_fbground.py

## Step 2: Generate legal term exclusion
echo "Generate legal terms to exclude: case names, legislation names"
python3 $TERMOLATOR/legal_feature/legal_terms_exclusion/legal_terms_extraction.py
python3 $TERMOLATOR/legal_feature/legal_terms_exclusion/lower_unique_terms.py

## Step 3: Generating the foreground and background for $1 issue ID $2
echo "Generating the foreground and background for $1 issue ID $2"
python3 $TERMOLATOR/legal_feature/create_fbground.py $2 $1
