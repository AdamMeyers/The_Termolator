#!/bin/env bash

#use TreeTagger to tag all docs in background and foreground corpora

#get name from input to this script
dirname=${1%/}
treetag_loc="$2"
#echo "got dirname: $dirname"

newdir="${dirname}_tagged"
mkdir -p "$newdir" 
count=0

#for each doc in given dir, run TreeTagger chunker
for filename in "$dirname"/*; do
	
	#[ -e "$filename" ] || continue
	#echo "og filename: $filename"
	stripped_filename="${filename##*/}"
	#echo "stripped filename: $stripped_filename"
	stripped_filename="${stripped_filename// /_}"
	#echo "stripped filename: $stripped_filename"
	newname="$dirname/$stripped_filename"

	if [ "$filename" != "$newname" ]; then
		echo "Renaming $filename to $newname"
		mv "$filename" "$newname"	
	fi

	./$treetag_loc/cmd/tagger-chunker-french "$newname" > "${newdir}/${stripped_filename}_tagged"
	
	
	((count++))
	
	if ! (( $count % 5 )) ; then
		echo "Tagging doc: $count"
	fi
done

echo "Done tagging docs in $dirname"
