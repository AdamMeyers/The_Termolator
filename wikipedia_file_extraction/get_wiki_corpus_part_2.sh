#!/bin/env bash

## args
#1 = current depth
#2 = article list
#3 = subcat list
#4 = use depth
#5 = use max
#6 = max articles
#7 = max depth
#8 = catfilename
#9 = listfilecontent

curr_depth="$1"
article_list="$2"
subcat_list="$3"
use_depth="$4"
use_max="$5"
max_articles="$6"
max_depth="$7"
catnamefile="$8"
listfilecontent="$9"


## ----------- Step 2: extract pageid, ns, title from json format and print to new file

##create new file to write in format: pageid \t ns \t title on each line
outfile="${catnamefile}_categorylist.txt"
if [ ! -e "$outfile" ]; then
       touch "$outfile"
fi

echo $listfilecontent | python3 -c '
import sys, json
dict=json.load(sys.stdin)
ln=len(dict["query"]["categorymembers"])
for i in range(ln):
        print(dict["query"]["categorymembers"][i]["pageid"], "\t", \
        dict["query"]["categorymembers"][i]["ns"], "\t", \
        dict["query"]["categorymembers"][i]["title"], flush=True)' | tee "$outfile"


## ------------ Step 3: gather article ids and subcategory ids in files

((curr_depth++))

while IFS= read -r line; do
        #echo "lines in article_list: $(wc -l < "$article_list")"
        #echo "max articles: $max_articles"

        if [ "$use_depth" == "true" ] || [ "$max_articles" != "false" -a $(wc -l < "$article_list") -lt "$max_articles" ]; then
                
                ns=$( echo "$line" | cut -d $'\t' -f2 )

                if [[ $ns -eq 0 ]]; then
                        id=$( echo "$line" | cut -d $'\t' -f1 )
                        #echo "article id: $id"

                        if grep -Fxq "$id" "$article_list"; then
                                :
                                #echo "article already found. skipping."
                        else
                                echo "$id" >> "$article_list"
                        fi

                elif [[ $ns -eq 14 ]]; then  ## if ns = 14: subcategory
                        id=$( echo "$line" | cut -d $'\t' -f1 )
                        title=$( echo "$line" | cut -d $'\t' -f3 )
                        #echo "subcategory: $title"
			title="${title//'/'/"_"}"

                        if grep -Fxq "$id" "$subcat_list"; then
                                :
                                #echo "visited category already"
                        else
                                #echo "going into subcat and writnig to file"
                                ##echo "$id" >> "$subcat_list"
                                title="$(echo -e "${title}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
                                srch=":"
                                title=${title#*$srch}

                                echo "$title" >> "$subcat_list"
                                ## add category to list without going into it immediately
                        fi

                fi
        else
                break
        fi

done < "$outfile"

#cleanup
rm "$outfile"

exit
