#!/usr/bin/env python

##S Burlaud 
##separates one big file of wiki articles text (WikiExtractor output)
##into separate documents: one article per document to be used as foreground/background set of files for Termolator
##takes 2 args: 1: WikiExtractor output DIRECTORY, 2: name of directory where all docs should be placed
##takes into account case in which WikiExtractor creates more than one output file, and more than one subdir
##NOTE for running: run with python3 if error: TypeError: 'encoding' is an invalid keyword argument for this function

import os
import sys


def main(args):

    ##print expected input if error detected
    if len(args) < 3:
        print("Expected input: 1st arg = WikiExtractor output directory to process, 2nd arg = name of directory \
        where processed docs should be stored")
        sys.exit()
    else:
        alldocs = args[1]
        directory = args[2]

    print("Separating documents; placing in folder: " + directory)

    if not os.path.exists(directory):
        os.makedirs(directory)

    for subdir in os.listdir(alldocs):

        ##print("this subdir:", subdir)
        for filename in os.listdir(alldocs+"/"+subdir):

                with open(alldocs+"/"+subdir+"/"+filename, "r", encoding="utf-8-sig") as mainfile:

                    for l in mainfile:
                        if l[0:4] == "<doc":
                    ##print("First line:" + l)
                            doctitle_idx = l.find("title=")
                            doctitle = l[(doctitle_idx + 7):len(l)-3:]
                            

                            if "/" in doctitle:
                                doctitle = doctitle.replace("/","_")

                            docfile = open(directory+"/"+doctitle+".txt", "w+", encoding="utf-8-sig")

                        else:
                                if l[0:6] != "</doc>":
                                        docfile.write(l)


if __name__ == '__main__': sys.exit(main(sys.argv))
 




















