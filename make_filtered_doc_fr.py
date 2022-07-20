#!/usr/bin/env python3

import sys
import re

def __main__(args):
#args: [test_name].filter_io
	with open(args[1], "r", encoding='utf-8') as infile:
		for line in infile:
			og_txt,fact,fact2 = line.rstrip().split(";")

	#		print("got og file:",og_txt,"fact:",fact,"fact2:",fact2)

			with open(fact2, "r", encoding='utf-8') as fact2:
				with open(og_txt+".txt", "w",encoding='utf-8') as outfile:
					
					good_intervals = []
					#get intervals to keep from fact2 file
					for line in fact2:
						this_int = [int(s) for s in re.findall(r'\b\d+\b', line)]

						good_intervals.append(this_int)

					#read in og txt as one list
					og_list = list(open(og_txt).read())

					#write good intervals to outfile
					for interval in good_intervals:						 
						outfile.write(''.join(og_list[interval[0]:interval[1]+1])+" ")
						


if __name__ == '__main__':
	__main__(sys.argv)
