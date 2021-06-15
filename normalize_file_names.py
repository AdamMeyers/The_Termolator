def minimum_file_check(infile,number):
    import re
    with open(infile) as instream:
        file_string = instream.read()
    length = file_string.count('\n')
    if length >= number:
        return(True)
    else:
        return(False)
    
def normalize_file_names(inlist,outlist,table,prefix,suffix):
    import os
    num = 0
    with open(inlist) as instream,open(outlist,'w') as outstream,open(table,'w') as tablestream:
        for line in instream:
            line = line.strip(os.linesep)
            directory,sep,file_name = line.rpartition(os.sep)
            short_file_name = prefix+str(num)+suffix
            new_file_name = directory+os.sep+prefix+str(num)+suffix
            num +=1
            outstream.write(new_file_name+'\n')
            tablestream.write(new_file_name+'\t'+line+'\n')
            os.symlink(file_name,new_file_name)
