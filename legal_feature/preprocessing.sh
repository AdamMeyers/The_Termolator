!/bin/sh

## $1 = type of issue (broad or narrow)
## $2 = issue ID

echo "The issue is of type: $1"
echo "The issue ID is: $2"

TERMOLATOR=${3:-$TERMOLATORPATH}

## Step 1: Generate the text cases and classify into broad/narrow issues
echo "Retrieve Supreme Court legal cases in folder 'text_cases'"
python3 $TERMOLATOR/legal_feature/supreme_court.py
python3 $TERMOLATOR/legal_feature/classify_fbground.py

## Step 2: Identify case and legislation names
echo "Generating case and legislation names from text files"
python3 $TERMOLATOR/legal_feature/run_citations_from_dir.py cases

## Step 3: Generate legal term exclusion
echo "Generate legal terms to exclude: case names, legislation names"
python3 $TERMOLATOR/legal_feature/legal_terms_extraction.py
python3 $TERMOLATOR/legal_feature/lower_unique_terms.py

## Step 4: Generating the foreground and background for $1 issue ID $2
echo "Generating the foreground and background for $1 issue ID $2"
python3 $TERMOLATOR/legal_feature/create_fbground.py $2 $1
python3 run_citations_from_dir.py cases
