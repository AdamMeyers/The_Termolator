#!/bin/env bash

##script to get Wikipedia documents for foreground/background corpora as part of Termolator
## By Sandra Burlaud

##ARGS
## $1 = target language (language of the retrieved articles). Name of the language should be in English (e.g.: "French", "English", "Chinese")
## $2 = name of desired category IN TARGET LANGUAGE (e.g.: FR categories "Optique" or "Physique"). Can be subcategory, but not simply an article
## $3 = name of directory to store final extracted articles
## $4 = TRUE if want to recursively retrieve all articles inside all subcategories found under the category
##	FALSE if only want to retrieve articles inside the given category
## $5 = depth of recursion
## $6 = max nbr of articles retrieved
## (if both depth and max are specified, will ignore depth)


recurs=${4,,}
target_lang=${1,,}
rep2="_"
catnamefile=${2// /$rep2}
catnamefile="${catnamefile//'/'/_}"
catnamefile="${catnamefile//'&'/_}"
catnamefile="${catnamefile//'('/_}"
catnamefile="${catnamefile\//')'/_}"
depth=${5,,}
max=${6,,}

##check input

if [ "$#" -ne 6 ] || [ "$recurs" == "true" -a "$depth" == "false" -a "$max" == "false" ]; then
	echo "Expected parameters:"
	echo "1: name of target language in english"
        echo "2: name of category in target language"
       	echo "3: name of directory to store final results"
       	echo "4: TRUE if retrieve articles in all subcats, FALSE if only in this category"
        echo "IF 4 = TRUE: specify either 5 or 6. IF 4 = FALSE: set 5 and 6 to FALSE."
	echo "5: depth of recursion (or FALSE)"
        echo "6: max number of articles retrieved (or FALSE)"
	exit
fi

use_max=false
use_depth=false

if [ "$max" != "false" ]; then
	use_max=true
else
	use_depth=true
	max=0
fi
	
#echo "ok params: use max: $use_max and use depth: $use_depth"

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
	echo "Will retrieve all articles found in subcategories"
else
	echo "Will only retrieve articles found in this category (no recursion)"
fi


#write first category in subcatlist
echo "$2" >> "$subcat_list"
#echo "wrote $2"

echo

##dict of languages & their Wikipedia code
declare -A lang_codes_dict=(["english"]="en" ["german"]="de" ["french"]="fr" ["spanish"]="es" ["russian"]="ru" ["japanese"]="ja" ["dutch"]="nl" ["italian"]="it" ["swedish"]="sv" ["polish"]="pl" ["vietnamese"]="vi" ["portuguese"]="pt" ["arabic"]="ar" ["chinese"]="zh" ["ukrainian"]="uk" ["catalan"]="ca" ["norwegian"]="no" ["finnish"]="fi" ["czech"]="cs") 
##TODO: add more languages later

##retrieve lang code from dict
lang_code="${lang_codes_dict[$target_lang]}"

wiki_url="$lang_code.wikipedia.org"

##call other script with Stages 1, 2, 3 
#echo "passing params:
#wikiurl: $wiki_url, 2: $2, final_outdir: $final_outdir, article_list: $article_list, subcat_list: $subcat_list, recurs: $recurs, depth: $depth, 0: 0, max: $max, use_max: $use_max, usedepth: $use_depth"

./get_wiki_corpus_stage123_new.sh "$wiki_url" "$2" "$final_outdir" "$article_list" "$subcat_list" "$recurs" "$depth" 0 "$max" "$use_max" "$use_depth"

#echo "back to main"


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
	##ns=$( echo "$line" | cut -d $'\t' -f2 )4
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
		#echo "added to array: $getarticlesfull"
		#echo "action: started new query"		
		getarticles2="$line"
		count=0
	fi
done < "${catnamefile}_maxids.txt"

## add last query by hand
getarticlesfull="$wiki_url$getarticles1$getarticles2$getarticles3"
arr+=("$getarticlesfull")


## ----------- Step 4: get articles 

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

python3 WikiExtractor.py -o "${catnamefile}_wikiextractor_output/" "$outf"


## ------------- Step 6: separate articles to use as foreground/background docs for Termolator

echo
echo "Final stage: separating docs"
echo

python3 separate-wikidocs2.py "${catnamefile}_wikiextractor_output/" "$final_outdir" 


## ------------ cleanup unwanted files
rm "$outf" "$article_list" "$subcat_list" "${catnamefile}_maxids.txt"

echo "Done"

exit





