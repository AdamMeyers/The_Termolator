#!/bin/env bash


##args
##$1: wikiurl
##$2: category name
##$3: final output dir name
##$4: article_list
##$5: subcat_list
##$6: recursion option, true or false
##$7: max depth
##$8: current depth so far
##$9: max articles
##$10: use_max
##$11: use_depth
## $12: this directory

wiki_url=$1

##modify category name if contains spaces
rep1="%20"
rep2="_"
catnamewiki="${2// /$rep1}"
catnamefile="${2// /$rep2}"
catnamefile="${2//\//$rep2}"
final_outfile="$3" ##will already have been created
article_list="$4"
subcat_list="$5"
recurs="$6"
max_depth="$7"
curr_depth=$8
max_articles="$9"
use_max=${10}
use_depth=${11}


#echo "Getting category: $catnamefile"
#echo "Current depth: $curr_depth"
#echo "max_articles: "$max_articles""
#echo "use_max: "$use_max", use_depth: "$use_depth""
#echo "max depth: $max_depth"

#Step 1: use php command to get list of categories/pages under desired category

#php_qry="/w/api.php?action=query&list=categorymembers&cmtitle=Category:$catnamewiki&cmlimit=max&format=json"
php_qry1="/w/api.php?action=query&list=categorymembers&cmtitle=Category:"
php_qry2="&cmlimit=max&format=json"

outputfile="${catnamefile}_wiki_apilist"
output_suff="_wiki_apilist"

wget -a "wget_logfile" -O "$outputfile" "${wiki_url}${php_qry1}${catnamewiki}${php_qry2}"

##read file in as string
listfile="$(<"$outputfile")"
listfilecontent="$listfile"

##test if this category exists
if [[ ${#listfilecontent} -lt 70 ]]; then
        echo "This category was not found on Wikipedia."
        exit
fi

if [[ $max_depth == "false" ]]; then
	max_depth=0
fi


while IFS= read -r line; do
	
	rep2="_"
	catnamefile="${line// /$rep2}"
	catnamefile="${line//\//$rep2}"
	
	rep1="%20"
	catnamewiki="${line// /$rep1}"
	outfile="${catnamefile}${output_suff}"
	
	wget -a "wget_logfile" -O "$outfile" "${wiki_url}${php_qry1}${catnamewiki}${php_qry2}"	

	filecont="$(<"$outfile")"
	filecontent="$filecont"		

	## call stages 2 and 3
	${12}/get_wiki_corpus_part_2.sh "$curr_depth" "$article_list" "$subcat_list" "$use_depth" "$use_max" "$max_articles" "$max_depth" "$catnamefile" "$filecontent"

	rm "$outfile"

done < "$subcat_list"



##clean up
#rm "$outputfile" 

exit


