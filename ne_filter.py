## This assumes that the input file represents entities with offset annotation
## and only one entity is recorded per line.
## The format can be an attribute value format such that:
##                  (1) the start offset is marked as: start="1234"
##                  (2) the end offset is marked as: end="4567"
##                  (3) 1234 and 4567 are the start and end offsets
## Variations allow for any nonnumeric character between = and the number or the absense of a character, e.g.,
## <abc start=1234 end=4567> is permitted. The < and > of sgml is not required.

from term_utilities import *
import os

def read_in_filter_positions(infile):
    output = []
    start_pattern = re.compile('start=[^0-9a-z]*([0-9]+)[^0-9a-z]*',re.I)
    end_pattern = re.compile('end=[^0-9a-z]*([0-9]+)[^0-9a-z]*',re.I)
    with open(infile) as instream:
        for line in instream:
            position = 0
            line = line.strip(os.linesep)
            start_match = start_pattern.search(line,position)
            if start_match:
                position = start_match.end()
                end_match = end_pattern.search(line,position)
            else:
                end_match = False
            if start_match and end_match:
                output.append([int(start_match.group(1)),int(end_match.group(1))])
    output.sort() ## items will be sorted by start positions, which ties settled by order of end positions
    output2=[]
    ## remove cases where a second item is included in the first, e.g., [1, 20] includes [3,7] 
    ## also merge cases that are right next to each other or overlap e.g.,
    ## [1,20] and [16,30] or [1,20] and [21,30]
    previous = False
    for pair in output:
        if not previous:
            previous = pair
        elif pair[1] <=previous[1]:  ## e.g. [1,20] and [3,7]
            pass # ignore current one
        elif pair[0] <=previous[1]+1:  
            ## the overlap case, e.g. [1,20] and [16,30]
            ## or [1,20] and [21,30]
            if pair[0] >=previous[0]:
                previous[1]=max(previous[1],pair[1])
            else:
                print('This should not be possible. NEs should have been sorted.')
        else:
            output2.append(previous)
            previous = pair
    if previous:
        output2.append(previous)    
    return(output2)
