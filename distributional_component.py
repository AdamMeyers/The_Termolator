#!/usr/bin/env python3
import sys, os, logging, errno
import Document
from Metric import *

LEVEL = logging.DEBUG
MEASURES = ['TFIDF', 'DRDC', 'KLDiv', 'Weighted']
MAX_LEN = 50

def __main__(args):
    """Input an RDG (and background), output a terms list"""
    logging.basicConfig(level=LEVEL)
    working_dir = '.'
    overwrite = True
    try:
        # First argument: RDG folder
        rdgfolder = args[1]
        # test if the folder is real
        if not os.path.isfile(rdgfolder):
            raise
        # Optional arguments:
        i = 2
        while i < len(args):
            # Optionally set measure
            if args[i] == '-m':
                measure = args[i+1]
                # check that the measure is real
                if measure not in MEASURES:
                    raise
                i += 2
            # Optionally set testing file
            elif args[i] ==  '-t':
                testfile = args[i+1]
                # check that the file is real
                if not os.path.isfile(testfile):
                    raise
                i += 2
            elif args[i] ==  '-d':
                working_dir = args[i+1]
                # check that the file is real
                if not os.path.isdir(working_dir):
                    if os.path.isfile(working_dir):
                        raise
                    else:
                        os.mkdir(working_dir)
                i += 2
            elif args[i] == 'False':
                overwrite=False
            else:
                # Optionally set reference folder:
                reffolder = args[i]
                # test if the folder is real
                if not os.path.isfile(reffolder):
                    raise
                i += 1
        # default measure to 'Weighted'
        if 'measure' not in locals():
            measure = 'Weighted'
    except:
        # Remind the user what input is acceptable
        logging.error('Usage: '+args[0]+' rdg_folder [ref_folder] [-m measure] [-t testfile]')
        logging.error('Measures: '+str(MEASURES))
        exit(-1)
    # log parameters
    logging.info('RDG Folder: '+rdgfolder)
    if 'reffolder' in locals():
        logging.info('Reference Folder: '+reffolder)
    else:
        logging.info('Reference Folder: None')
    logging.info('Measure: ' + measure)
    if 'testfile' in locals():
        logging.info('Test Word List File: ' + testfile)
    else:
        logging.info('Test Word List File: None')
    # Set up the measurement class
    logging.debug('Loading Files...')
    if 'reffolder' in locals():
        metric = Metric(rdgfolder, reffolder, working_dir = working_dir,overwrite=overwrite) # reference files given
    else:
        raise
        #metric = Metric(rdgfolder, refcorpus) # reference corpus assumed
    logging.debug('done')
    # Get rankings
    logging.debug('Ranking terms...')
    if 'testfile' in locals():
        ranking = metric.rankWordList(testfile, measure)
    else:
        ranking = metric.rankTerms(measure)
    logging.debug('done')
    # Print rankings
    #for r in ranking:
    #    print r[0]+'\t'+str(r[1])
    try:
        for i in range(len(ranking)):
            if (len(ranking[i][0]) > MAX_LEN):
                continue
            sys.stdout.write(ranking[i][0]+'\t'+str(ranking[i][1])+'\n')
    except IOError as e:
        if e.errno == errno.EPIPE: #no longer printing to stdout
            return

if __name__ == '__main__':
    __main__(sys.argv)
