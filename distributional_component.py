#!/usr/bin/env python3
import sys, os, logging, errno
import Document
from Metric import *

LEVEL = logging.DEBUG
MEASURES = ['TFIDF', 'DRDC', 'KLDiv', 'Weighted']
MAX_LEN = 50
## use the ranking.pkl file from before
rank_from_previous=False

def __main__(args):
    """Input an RDG (and background) and other parameters, output a terms list"""
    global rank_from_previous
    global background_cache_file
    logging.basicConfig(level=LEVEL)
    working_dir = '.'
    overwrite = True
    try:
        # First argument: RankFromPrevious uses a pkl file
        if args[1]=="RankFromPrevious":
            rank_from_previous = True
        # First argument: RDG folder
        rdgfolder = args[2]
        # test if the folder is real
        if not os.path.isfile(rdgfolder):
            raise
        outfile = args[3]
        background_cache_file = args[4]
        if background_cache_file.lower() == 'false':
            background_cache_file = 'ranking.pkl'
        if rank_from_previous and not(os.path.isfile(background_cache_file)):
            exception_string = background_cache_file + ' does not exist.\n'
            exception_string += 'Please rerun the system. If you choose the "rank from previous" option, \n'
            exception_string += 'you must choose an existing cached background file. When you rerun,'
            exception_string += 'you may not need to preprocess the foreground on the next run.'
            print(exception_string)
            raise Exception('Exiting')
        # Optional arguments:
        i = 5
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
                if (not os.path.isfile(reffolder)) and (not rank_from_previous):
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
    if ('reffolder' in locals()) and (not rank_from_previous):
        ## if 'reffolder' in locals():
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
    metric = None
    #logging.error("LOCLS:" + str(locals()))
    try:
        if 'reffolder' in locals():
            ## if not rank_from_previous:
            metric = Metric(rdgfolder, reffolder, working_dir = working_dir,overwrite=overwrite,rank_from_previous=rank_from_previous,background_cache_file=background_cache_file) # reference files given
            # Get rankings
            logging.debug('Ranking terms...')
            if 'testfile' in locals():
                ranking = metric.rankWordList(testfile, measure)
            else:
                if rank_from_previous:
                    ranking = metric.rankTermsFromPrevious(measure)
                else:
                    ranking = metric.rankTerms(measure)
            try:
                with open(outfile,'w', encoding='utf-8-sig') as outstream:
                    for i in range(len(ranking)):
                        if (len(ranking[i][0]) > MAX_LEN):
                            continue
                    ## sys.stdout.write(ranking[i][0]+'\t'+str(ranking[i][1])+'\n')
                        outstream.write(ranking[i][0]+'\t'+str(ranking[i][1])+'\n')
            except IOError as e:
                if e.errno == errno.EPIPE: #no longer printing to stdout
                    return
        else:
            logging.error("Ref Folder Not In Locals, or exception in Metric")
    except:
        exc_info = sys.exc_info()
        raise str(exc_info[0]) + str(exc_info[1]) + str(exc_info[2])
    #else:
    #    raise exception
        #metric = Metric(rdgfolder, refcorpus) # reference corpus assumed
    # Print rankings
    #for r in ranking:
    #    print r[0]+'\t'+str(r[1])

if __name__ == '__main__':
    __main__(sys.argv)
