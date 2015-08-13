import os, sys
from patentterms import *

def __main__(args):
    if len(args) !=2 or not os.path.isdir(args[1]):
        print 'Usage: '+args[0]+' folder'
        return
    path = args[1]
    filenames = os.listdir(path)
    filenames = [f for f in filenames if f[-4:] == '.txt' and f+'.terms' not in filenames]
    for fname in filenames:
        print fname+', ',
        lst = getPatentTerms(os.path.join(args[1],fname))
        f = open(os.path.join(path,fname+'.terms'),'w')
        for l in lst:
            temp = Filter.unstem(l)
            for t in temp:
                f.write(t+'\n')
        f.close()
    print 'done'

if __name__ == '__main__':
    __main__(sys.argv)
