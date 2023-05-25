#!/bin/env bash

##script to get Wikipedia documents for foreground/background corpora as part of Termolator

##ARGS
## $1 = target language (language of the retrieved articles). Name of the language should be in English (e.g.: "French", "English", "Chinese")
## $2 = name of desired category IN TARGET LANGUAGE (e.g.: FR categories "Optique" or "Physique"). Can be subcategory, but not simply an article
## $3 = name of directory to store final extracted articles
## $4 = TRUE if want to recursively retrieve all articles inside all subcategories found under the category
##	FALSE if only want to retrieve articles inside the given category
## $5 = max nbr of articles retrieved
## $6 this directory


recurs=${4,,}
target_lang=${1,,}
rep2="_"
catnamefile=${2// /$rep2}
catnamefile="${catnamefile//'/'/_}"
catnamefile="${catnamefile//'&'/_}"
catnamefile="${catnamefile//'('/_}"
##catnamefile="${catnamefile\//')'/_}"
catnamefile="${catnamefile/\//')'/_}"
#depth=${5,,}
max=${5,,}

##check input

if [ "$#" -ne 6 ] || [ "$recurs" == "true" -a "$max" == "false" ]; then
	echo "Expected parameters:"
	echo "1: name of target language in english"
        echo "2: name of category in target language"
       	echo "3: name of directory to store final results"
       	echo "4: TRUE if retrieve articles in all subcats, FALSE if only in this category"
        echo "	IF 4 = TRUE: specify 5, nbr of articles to be retrieved. IF 4 = FALSE: set 5 to FALSE."
	echo "5: max number of articles retrieved (or FALSE)"
	echo "6: directory with wikipedia search files"
	exit
fi

use_max=false
use_depth=false

if [ "$max" != "false" ]; then
	use_max=true
#else
#	use_depth=true
#	max=0
fi


##final output file
final_outdir=$3
mkdir -p "$final_outdir"

##create file for article ids and file for visited category ids
article_list="${final_outdir}_article_ids.txt"
subcat_list="${final_outdir}_subcat_ids.txt"

if [ ! -e "$article_list" ]; then
       touch "$article_list"
fi

if [ ! -e "$subcat_list" ]; then
       touch "$subcat_list"
fi


echo
echo "The final output dir will be: $final_outdir"
echo "The target language is: $target_lang"
echo "The category to be retrieved is: $2"

if [[ "$recurs" == "true" ]]; then
	echo "Will retrieve articles found in subcategories (breadth-first search)"
else
	echo "Will only retrieve articles found in this category (no recursion)"
fi
echo

#write first category in subcatlist
echo "$2" >> "$subcat_list"

##dict of languages & their Wikipedia code
declare -A lang_codes_dict=(["english"]="en" ["german"]="de" ["french"]="fr" ["spanish"]="es" ["russian"]="ru" ["japanese"]="ja" ["dutch"]="nl" ["italian"]="it" ["swedish"]="sv" ["polish"]="pl" ["vietnamese"]="vi" ["portuguese"]="pt" ["arabic"]="ar" ["chinese"]="zh" ["ukrainian"]="uk" ["catalan"]="ca" ["norwegian"]="no" ["finnish"]="fi" ["czech"]="cs")
##TODO: add more languages later

##retrieve lang code from dict
lang_code="${lang_codes_dict[$target_lang]}"

wiki_url="${lang_code}.wikipedia.org"

##call other parts
$6/get_wiki_corpus_part_1.sh "$wiki_url" "$2" "$final_outdir" "$article_list" "$subcat_list" "$recurs" "$depth" 0 "$max" "$use_max" "$use_depth" $6



## ----------- Step 4: build queries using page ids

##get max nbr of page ids into new file

if [[ "$use_max" == "true" ]]; then
	touch "${catnamefile}_maxids.txt"
	shuf -n $max "$article_list" >> "${catnamefile}_maxids.txt"
else
	cp "$article_list" "${catnamefile}_maxids.txt"
fi


echo
echo "Creating queries"
echo

getarticles1="/w/api.php?action=query&pageids="
getarticles3="&export&exportnowrap"
getarticles2=""

arr=()
count=0
while IFS= read -r line; do
	#echo "text read from file: |$line|"

	line="$(echo -e "${line}" | sed -e 's/[[:space:]]*$//')" ##remove trailing whitespace

	if [[ $count -lt 49 ]]; then
		#echo "id: $id"
		if [[ -n "$line" ]]; then
			if [ "${getarticles2}" = "" ]; then
				getarticles2="$line"
			else
				getarticles2="${getarticles2}|$line"
			fi
		fi
		((count++))

	else
		getarticlesfull="$wiki_url$getarticles1$getarticles2$getarticles3"
		arr+=("$getarticlesfull")
		getarticles2="$line"
		count=0
	fi
done < "${catnamefile}_maxids.txt"

## add last query
getarticlesfull="$wiki_url$getarticles1$getarticles2$getarticles3"
arr+=("$getarticlesfull")


## --------- get articles

outf="${catnamefile}_xml_all.txt"
if [ ! -e "$outf" ]; then
        touch "$outf"
else
	echo "${catnamefile}_xml_all.txt already exists. Appending to end of file."
fi

count=1
for query in "${arr[@]}"; do
	#echo "GETTING QUERY: $query"
	#	echo "query $count"

	wget -a "wget_logfile" -O - $query >> "$outf"
	((count++))
done




## ------------- Step 5: extract text from articles with Wikiextractor

mkdir -p "${catnamefile}_wikiextractor_output/"

echo
echo "Extracting from XML format with WikiExtractor"
echo

python3 $6/WikiExtractor.py -o "${catnamefile}_wikiextractor_output/" "$outf"


## ------------- Step 6: separate articles to use as foreground/background docs for Termolator

echo
echo "Final stage: separating docs"
echo

python3 $6/separate-wikidocs2.py "${catnamefile}_wikiextractor_output/" "$final_outdir"


## ------------ cleanup unwanted files
rm "$outf" "$article_list" "$subcat_list" "${catnamefile}_maxids.txt"

echo "Done"


#cleanup
#comment out if want to keep file containing wikiextractor output
rm -r "${catnamefile}_wikiextractor_output/"
exit
