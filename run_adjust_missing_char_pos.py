#!/usr/bin/env python3

import os
import sys
import re

def get_pos_facts(fact_list):
    output = []
    bad_pos_pattern = re.compile('BAD_CHARACTER START=([0-9]*) END=([0-9]*) STRING="([^"]*)"')
    for fact in fact_list:
        bad_match = bad_pos_pattern.search(fact)
        if bad_match:
            output.append([int(bad_match.group(1)),int(bad_match.group(2)),bad_match.group(3)])
    return(output)

def make_fact_pair(triple):
    output = [triple[0],triple[2]+' ||| S:'+str(triple[0])+' E:'+str(triple[1])+' ||| '+'SYM'+os.linesep]
    return(output)

def make_pos_triple(line):
    start_pat = re.compile('S:([0-9]*).*E:([0-9]*)')
    start_match = start_pat.search(line)
    if not start_match:
        print('Warning: Error in POS file')
        return([0,0,line])
    else:
        return([int(start_match.group(1)),int(start_match.group(2)),line])

def modify_pos_end(line,new_end):
    start_pat = re.compile('E:([0-9]*)')
    start_match = start_pat.search(line)
    if start_match:
        output = line[0:start_match.start()]+'E:'+str(new_end)+line[start_match.end():]
        return(output)
    else:
        return(line)

def fix_bad_char_in_file(fact,pos):
    with open(fact) as fact_stream:
        fact_list = get_pos_facts(fact_stream.readlines())
        fact_list.reverse()
    if fact_list:
        with open(pos) as pos_stream:
            pos_list = pos_stream.readlines()
            pos_list.reverse()
        next_fact = False
        next_pos = False
        with open(pos,'w') as outstream:
            while pos_list or fact_list:
                if fact_list and (not next_fact):
                    next_fact = make_fact_pair(fact_list.pop())
                if pos_list and (not next_pos):
                    next_pos = make_pos_triple(pos_list.pop())
                if (next_pos and next_fact and (next_pos[0]>next_fact[0])) or (next_fact and not next_pos):
                    outstream.write(next_fact[1])
                    next_fact = False
                elif next_pos:
                    if next_fact and (next_fact[0]>next_pos[0]) and (next_fact[0]<next_pos[1]):
                        outstream.write(modify_pos_end(next_pos[2],next_fact[0]))
                    else:
                        outstream.write(next_pos[2])
                    next_pos = False

def main(args):
    file_list = args[1]
    lines = []
    with open(file_list) as instream:
        for line in instream:
            fact,pos = line.strip().split(';')
            fix_bad_char_in_file(fact,pos)

if __name__ == '__main__': sys.exit(main(sys.argv))
