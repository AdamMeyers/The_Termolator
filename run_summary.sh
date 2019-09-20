#!/bin/sh

## $1 = prefix for several filenames including the .term_instance_map being used as input and
##      the .summary file being used as output
## $2 = the directory containing the foreground files referenced in the .term_instance_map file.
##
## $3 = the program directory (where Termolator programs are)
## There are several other possible variations that are possible by altering the code or adding
## key word arguments. We will leave these out for now.

python3 $3/run_summary.py $1 $2
