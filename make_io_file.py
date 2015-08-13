#!/usr/bin/env python3

import re
import sys
import os

def main(args):
    ## infile is the output file from distributional term extraction
    txt_file_list = args[1]
    out_file = args[2]
    ## outfile is the main output dictionary file from this process
    extensions = args[3:]
    if extensions:
        with open(txt_file_list) as instream, open(out_file,'w') as outstream:
            for line in instream:
                line = line.strip()
                ending_pattern = re.compile('\.((txt)|(hml)|(htm)|(html)|(xml)|(sgml))[^a-zA-Z]*$',re.I)
                base = ending_pattern.sub('',line)
                if extensions[0] == 'BARE':
                    outstream.write(base)
                else:
                    outstream.write(base+extensions[0])
                for extension in extensions[1:]:
                    if extension.upper() in ['TRUE','FALSE','T','F']:
                        outstream.write(';'+extension)
                    elif extension.upper() == 'BARE':
                        outstream.write(base)
                    else:
                        outstream.write(';'+base+extension)
                outstream.write(os.linesep)

if __name__ == '__main__': sys.exit(main(sys.argv))
