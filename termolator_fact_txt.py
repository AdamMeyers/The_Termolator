#!/usr/bin/env python3

import os
import sys
from term_utilities import *
initialize_utilities()

def modify_paragraph_delimiters(paragraph_starts,paragraph_ends,paragraph_non_starts,paragraph_non_ends,input_file):
    matched_outstarts = []
    matched_outends = []
    next_start = 'Empty'
    while (len(paragraph_starts)>0):
        next_start = paragraph_starts.pop(0)
        matched_outstarts.append(next_start)
        if (len(paragraph_ends)>0):
            if (len(paragraph_starts)>0) and (paragraph_starts[0] < paragraph_ends[0]):
                matched_outends.append(paragraph_starts[0])
            else:
                matched_outends.append(paragraph_ends.pop(0))
        elif len(paragraph_starts)>0:
            matched_outends.append(paragraph_starts[0])
    paragraph_starts = matched_outstarts
    paragraph_ends = matched_outends
    out_starts = []
    out_ends = []
    current_start,current_end,current_non_start,current_non_end = 'Empty','Empty','Empty','Empty'
    ## First step, use paragraph starts and ends to block unprintable sections (as per paragraph_non_starts,paragraph_non_ends)
    ## 'Empty' means no value -- cannot use 0 because 0 is a possible file position; cannot use False, because False == 0 in Python
    if ((paragraph_non_ends)==0) or (len(paragraph_non_starts)==0):
        out_starts = paragraph_starts
        out_ends = paragraph_ends
    else:
        while (len(paragraph_ends)>0) or (current_end !='Empty'):
            if (current_start=='Empty') and (len(paragraph_starts)>0):
                current_start = paragraph_starts.pop(0)
            if (current_end=='Empty'):
                current_end = paragraph_ends.pop(0)
            if (current_non_start=='Empty') and (len(paragraph_non_starts)>0):
                current_non_start = paragraph_non_starts.pop(0)
            if (current_non_end=='Empty') and (len(paragraph_non_ends)>0):
                current_non_end = paragraph_non_ends.pop(0)
            if (current_non_start != 'Empty') and (current_non_end != 'Empty') and (current_non_start <= current_start) and (current_non_end >= current_end):
                current_non_start = current_end
                current_start = 'Empty'
                current_end = 'Empty'
            if (current_non_end != 'Empty') and (current_start != 'Empty') and (current_non_end <= current_start):
                current_non_start = 'Empty'
                current_non_end = 'Empty'
            if (current_non_start != 'Empty') and (current_start != 'Empty') and (current_non_end != 'Empty') and (current_non_start <= current_start) \
              and (current_non_end >= current_start) and (current_non_end <= current_end):
              current_non_start = current_start
            if (current_start == 'Empty'):
                pass
            elif (current_non_start == 'Empty')  or  ((current_end != 'Empty') and (current_non_start >= current_end)) or \
              ((current_non_end != 'Empty') and (current_non_end <= current_start)):
                if current_start !='Empty':
                    out_starts.append(current_start)
                out_ends.append(current_end)
                current_start = 'Empty'
                current_end = 'Empty'
            elif (current_non_start != 'Empty') and (current_non_end != 'Empty') and (current_non_start <= current_start) and (current_end != 'Empty') and (current_non_end >= current_end):
                current_start = 'Empty'
                current_end = 'Empty'
            elif (current_end != 'Empty') and (current_non_start <= current_end) and (current_non_start>=current_start):
                out_starts.append(current_start)
                out_ends.append(current_non_start)
                last_start = current_start
                current_start = 'Empty'
                current_non_start = 'Empty'
                if (current_non_end != 'Empty') and (current_non_end <= current_end):
                    if current_non_end>=last_start:
                        current_start = current_non_end
                    current_non_end = 'Empty'
                elif (len(paragraph_starts)>0) and (current_non_end != 'Empty') and (paragraph_starts[0]<=current_non_end):
                    current_end = 'Empty'
                    num = 0
                    while (num < len(paragraph_starts)) and (paragraph_starts[num]<=current_non_end):
                        paragraph_starts[num] = current_non_end
                        num = 1 + num
                    num = 0
                    while (num < len(paragraph_ends)) and (paragraph_ends[num]<=current_non_end):
                        paragraph_ends[num] = current_non_end
                        num = 1 + num
                    current_end = 'Empty'  
                    current_non_end = 'Empty'                  
                else:
                    current_end = 'Empty'
                    current_non_end = 'Empty'
            elif (current_non_end != 'Empty') and (current_end != 'Empty') and (current_non_end >= current_start) and (current_non_end<=current_end):
                current_start = current_non_end
                current_non_end = 'Empty'
                current_non_start = 'Empty'
            elif (current_end != 'Empty') and (current_non_end == 'Empty') and (current_end >=current_start):
                out_starts.append(current_start )
                out_ends.append(current_end)
                last_start = current_end
                current_start = 'Empty'
                current_end = 'Empty'                
            elif (len(paragraph_ends)>0) or (current_end !='Empty'):
                print('starts',current_start,current_non_start)
                print('ends',current_non_end,current_end)
                print('outstarts',out_starts)
                print('ends',out_ends)
                print('possible error processing xml for file',input_file)
                return(out_starts,out_ends)
    return(out_starts,out_ends)

def create_termolotator_fact_txt_files(input_file,txt2_file,txt3_file,fact_file):
    global paragraph_starts
    global paragraph_ends
    paragraph_starts = [0]
    paragraph_ends = []
    nonprint_starts = []
    nonprint_ends = []
    bad_chars = []
    inlinelist  = get_my_string_list(input_file)
    with open(txt2_file,'w') as txt2_stream,open(txt3_file,'w') as txt3_stream:
        start = 0
        length = 0
        for line in merge_multiline_and_fix_xml(inlinelist):
            string2,starts1,ends1,nonprint_starts1,nonprint_ends1 = remove_xml_spit_out_paragraph_start_end(line,start)
            string3, bad1 = replace_less_than_with_positions(string2,start)
            if (len(paragraph_ends) == 0) and (len(starts1)>0) and (len(paragraph_ends) == 0):
                hypothetical_end = (starts1[0]-1)
                if not hypothetical_end in ends1:
                    ends1.append(hypothetical_end)
                    ends1.sort()
                    ## balances the addition of 0 as a start
            length = length+len(string2)
            start = start+len(string2)
            txt2_stream.write(string2)
            txt3_stream.write(string3)
            paragraph_starts.extend(starts1)
            paragraph_ends.extend(ends1)
            nonprint_starts.extend(nonprint_starts1)
            nonprint_ends.extend(nonprint_ends1)
            bad_chars.extend(bad1)
        if len(paragraph_ends)>0:
            paragraph_starts.append(1 + paragraph_ends[-1])
        paragraph_ends.append(length)
    paragraph_starts,paragraph_ends=modify_paragraph_delimiters(paragraph_starts,paragraph_ends,nonprint_starts,nonprint_ends,input_file)
    with open(fact_file,'w') as factstream:
        if len(paragraph_starts) == len(paragraph_ends):
            for item_num in range(len(paragraph_starts)):
                factstream.write('STRUCTURE TYPE="TEXT" START='+str(paragraph_starts[item_num])+' END='+str(paragraph_ends[item_num])+os.linesep)
        elif (len(paragraph_starts)>1) and len(paragraph_ends) == 1:
            last_start = 0
            for start in paragraph_starts:
                if start != 0:
                    factstream.write('STRUCTURE TYPE="TEXT" START='+str(last_start)+' END='+str(start)+os.linesep)
                last_start = start
            factstream.write('STRUCTURE TYPE="TEXT" START='+str(last_start)+' END='+str(paragraph_ends[0])+os.linesep)
        else:
            factstream.write('STRUCTURE TYPE="TEXT" START=0 END='+str(paragraph_ends[0])+os.linesep)
        for bad_char in bad_chars:
            factstream.write('BAD_CHARACTER START='+str(bad_char[0])+' END='+str(bad_char[1])+' STRING="<"'+os.linesep)
        
