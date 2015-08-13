import sys, os, logging, errno
import Document
from Metric import *

rdgpath = '/misc/proteus107/zg440/test2/emerging/'
genpath = '/misc/proteus107/zg440/test2/random/'

measures = ['TFIDF', 'DRDC', 'KLDiv']

oldpath = os.path.abspath('.')
os.chdir(rdgpath)
temppath = 'temp1234'
os.makedirs(temppath)
metric = Metric(temppath, temppath)
os.remove(os.path.join(temppath, 'filter.save'))
os.rmdir(temppath)
os.chdir(oldpath)
print 'Getting stemming dictionary'
Filter._get_stemdict(os.path.join(genpath, 'filter.save'))
print 'Getting background'
metric.genDocs = Document()
genfiles = [genFile for genFile in os.listdir(genpath) if genFile[-4:]=='.txt']
for f in genfiles:
    d = Document(os.path.join(genpath, f))
    for w in d.counts:
        metric.genDocs.counts[w] += d.counts[w]
print 'Getting all RDG subfolders'
rdgdirs = [d for d in os.listdir(rdgpath) if os.path.isdir(os.path.join(rdgpath, d))]
for d in rdgdirs:
    print 'Computing metrics for '+d
    if os.path.exists(os.path.join(rdgpath, d, 'TFIDF.out')):
        print "Skip"
        continue
    metric.rdgDocs = []
    metric._TermFreq, metric._DR, metric._DC, metric._TFIDF = [None]*4
    del metric._TermFreq, metric._DR, metric._DC, metric._TFIDF
    rdgfiles = [rdgFile for rdgFile in os.listdir(os.path.join(rdgpath,d)) if rdgFile[-4:]=='.txt']
    for f in rdgfiles:
        metric.rdgDocs.append(Document(os.path.join(rdgpath,d,f)))
    for m in measures:
        ranking = metric.rankTerms(m)
        f = open(os.path.join(rdgpath,d,m+'.out'), 'w')
        for i in range(len(ranking)):
            f.write(ranking[i][0]+'\t'+str(ranking[i][1])+'\n')
        f.close()
print 'Done'
