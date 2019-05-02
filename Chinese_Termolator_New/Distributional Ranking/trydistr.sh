#!/usr/bin/env bash
## $1 = output_file_name 
## Usage: bash trydistr.sh outputNameDesired

ls -1 Chinese_IntermFiles/foreground/ | grep "tchunk$" | awk '{print "Chinese_IntermFiles/foreground/"$1}' > $1.internal_foreground_tchunk_list
ls -1 Chinese_IntermFiles/background/ | grep "tchunk$" | awk '{print "Chinese_IntermFiles/background/"$1}' > $1.internal_background_tchunk_list


./distributional_component.py NormalRank $1.internal_foreground_tchunk_list $1.all_terms False $1.internal_background_tchunk_list