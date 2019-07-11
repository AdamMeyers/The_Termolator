'''
Author: Yuling Gu
Date: Jul 18, 2018
Description: 
Take in a list of filenames for .xml format files as first argument, 
and produces a list of output files. The prcoessing involves parsing,
removing xml tags, clearing ampersand characters, and removing 
whitespaces. Makes use of termUtilitiesEng.py which is term_utilities.py
in the English Termolator system.
Usage: python name_of_thisFile.py background_filelist.txt outputTag
e.g. python remove_xml_chinese.py backgroundList.txt testing
'''

#!/usr/bin/env python3
import re
import sys
import xml.etree.ElementTree as ET
from termUtilitiesEng import *

# make use of ElementTree module to parse xml 
def remove_tags(text):
    return(ET.fromstringlist(text, parser=None))

def main():
    # open input file list (first argument)
    input_file  = sys.argv[1];
    infilelist  = get_my_string_list(input_file)
    # loop through file names
    for file in infilelist :
        # determine ouput file name
        with open(file[:-4] + sys.argv[2] + ".xml", "w") as wId:
            file = file.replace('\n', '')
            file_lines = get_my_string_list(file)
            # process lines in each file
            lines = []
            # parse xml
            for line  in remove_tags(file_lines) : 
                lines.append(ET.tostring(line, encoding="UTF-8").decode("UTF-8"))
            # cleaning
            for i in lines:
                # remove xml
                x = remove_xml(i).strip()
                # clear ampersand
                x = clean_string_of_ampersand_characters(x)
                # clear whitespace
                x = interior_white_space_trim(x)
                if(len(x) > 0):
                    wId.write(x)


if __name__ == '__main__':
    main()