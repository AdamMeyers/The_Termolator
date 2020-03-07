#!/bin/env bash 

#make list of files in a dir

dir=${1%/}  

touch "${dir}_list.txt"

for entry in "$dir"/*
do
  entry_without_ext="${entry%.*}"
  ext="${entry##*.}"  
  for i in "$entry_without_ext" ; do
    
    if [[ $i == *.* || $i == *\;* ]]; then
      newname="${entry_without_ext//./_}"
      newname="${newname//;/_}"
      newname="${newname}.${ext}"
      
      echo "Renaming $entry to $newname"

      
      mv "$entry" "$newname"
      entry=$newname  
    fi
  done

  echo "$entry" >> "${dir}_list.txt"
done

exit

































