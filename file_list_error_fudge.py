import os
import sys
import time

def name_transform(line):
    return(' '+line)

def main(args):
    infile = args[1]
    output = []
    with open(infile) as instream:
        for line in instream:
            output.append(name_transform(line))
    with open(infile,'w') as outstream:
        for line in output:
            outstream.write(line)
    time.sleep(5)
    print(infile)
    print(os.path.getsize(infile))

   
if __name__ == '__main__': sys.exit(main(sys.argv))
