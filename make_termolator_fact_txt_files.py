#!/usr/bin/env python3

from termolator_fact_txt import *
        
def main(args):
    ## infile is the output file from distributional term extraction
    txt_file_list = args[1]
    file_type = args[2]
    if not file_type.lower() in ['.htm','.html','.txt','.hml','.xml','.xhtml','.sgm','.sgml','.xhml']:
        print('Warning: File type must be a member of the list',['.htm','.html','.txt','.hml','.xml','.xhtml','.sgm','.sgml','.xhml'])
        print('Halting Program. Choose a member of this list and run this function again.')
        return('Fail')
    with open(txt_file_list) as instream:
        for line in instream:
            infile = line.strip()
            input_file = infile+file_type
            txt2_file =  infile+'.txt2'
            txt3_file =  infile+'.txt3'
            fact_file = infile+'.fact'
            create_termolotator_fact_txt_files(input_file,txt2_file,txt3_file,fact_file)

if __name__ == '__main__': sys.exit(main(sys.argv))
