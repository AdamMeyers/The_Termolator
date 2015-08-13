from nltk.corpus import brown as refcorpus
import cPickle as pickle
import os
import Document
from Metric import *

rdgfolder = '/home/zg440/Documents/test/patents/US_out/train/'
testfolder = '/home/zg440/Documents/test/patents/US_out/test/'
#termfolder = ''

def run():
    global metric
    global ranking
    print 'Loading RDG...',
    metric = Metric(rdgfolder, refcorpus)
    print 'done'
    print 'Ranking terms...',
    ranking = []
    ranking = metric.rankTerms(measure='Weighted')
    print 'done'
    #Now done by design:
    #ranking2 = [(Filter.unstem(r[0]), r[1]) for r in ranking]
    #ranking2.sort(key=lambda x: x[1], reverse=True) #not necessary?
    #return ranking

def score(measure='Weighted', n=300):
    #FIX ME:
    termfiles = [f for f in os.listdir(termfolder)]
    score = scoreByTop(termfiles,measure,n)
    return score

def load(filename):
    global metric
    global ranking
    metric = Metric('.','.')
    ranking = []
##    f = open('./out/patent.dump')
##    (metric.rdgDocs, metric.genDocs, ranking) = pickle.load(f)
##    f.close()
##    f = open('./out/hiddendata.dump')
##    (metric._DC, metric._DR, metric._TFIDF, metric._TermDocFreq, \
##     metric._TermFreq, metric._TokenDR) = pickle.load(f)
##    f.close()
##    f = open('./out/stem.dump')
##    Filter.stemdict = pickle.load(f)
##    f.close()
    f = open(filename)
    #(metric.rdgDocs, metric.genDocs, metric._DC, metric._DR, \
    # metric._TFIDF, metric._TermDocFreq, metric._TermFreq, \
    # metric._TokenDR, Filter.stemdict, ranking) = pickle.load(f)
    (metric.rdgDocs, metric.genDocs, metric._DC, metric._DR, \
     metric._TFIDF, metric._TermDocFreq, metric._TermFreq, \
     metric._TokenDR, Filter.stemdict, Filter.unstemdict) = pickle.load(f)
    f.close()

def save(filename):
    global metric
    f = open(filename, 'w')
    #pickle.dump((metric, ranking), f) #FIX THIS, YOU CAN'T JUST DUMP A CLASS
    data = (metric.rdgDocs, metric.genDocs, metric._DC, metric._DR, \
            metric._TFIDF, metric._TermDocFreq, metric._TermFreq, \
            metric._TokenDR, Filter.stemdict, Filter.unstemdict)
    pickle.dump(data, f)
    f.close()

def perplexity(testfolder, measure, N=300):
    # NEED TO:
    # 1) CALCULATE PROBABILITIES
    # 2) CALCULATE RANKINGS FOR HELD OUT RDG
    # 3) CALCULATE PERPLEXITY OVER TOP N (300?) TERMS OF HELD OUT RANKINGS
    # THIS IS LIKE SAYING "HOW GOOD IS THE FIT FOR
    # OBSERVING TERMS CONSISTING OF THE TOP N IN THE HELD OUT SET"
    #
    # Calculate term hypothesized probability distribution
    print 'Calculating probabilities...',
    ranklist = metric.rankTerms(measure)
    # scale ranks to be 0 < rank <= 1, with sum(ranks)=1
    #min_rank = abs(ranklist[-1][1]) # last score in the list
    #fudgefactor = 0.01*min_rank # to ensure rank > 0 and that unknown NPs have p>0
    #scalefactor = sum(map(lambda x: x[1], ranklist)) \
    #              + len(ranklist)*(min_rank+fudgefactor) \
    #              + fudgefactor
    #scalefactor = sum(map(lambda x: x[1], ranklist)) + (len(ranklist)+1)*fudgefactor
    # hypothesized probability distribution
    # (of NPs being members of the set of terminology):
    logProbs = {}
    #for item in ranklist:
    #    #logProbs[item[0]]=math.log(item[1]+min_rank+fudgefactor,2)-math.log(scalefactor,2)
    #    #logProbs[item[0]]=math.log(item[1]+fudgefactor,2)-math.log(scalefactor,2)
    #    logProbs[item[0]] = item[1]
    for i in range(len(ranklist)):
        #logProbs[ranklist[i][0]] = math.log(float(i+1.0)/len(ranklist))
        if i < N:
            logProbs[ranklist[i][0]] = math.log((1.0/N - 0.001/N),2)
        else:
            logProbs[ranklist[i][0]] = math.log((0.001/(len(ranklist)-N)),2)
    #logProbs['[UNK]'] = math.log(fudgefactor,2)-math.log(scalefactor,2) # probability of a new NP
    print 'done'
    # Create test document set
    print 'Retrieving test set...',
    global testwords
    try:
        testwords
    except:
        #backup Filter.stemdict, as loading new documents will change it
        backupstems = [Filter.stemdict, Filter.unstemdict]
        Filter.stemdict = {}
        Filter.unstemdict = {}
        #testDocs = Document()
        temp = [Document(testfolder+f) for f in os.listdir(testfolder) if f[-4:]=='.txt']
        testwords = []
        for i in range(len(temp)):
            for w in temp[i].counts:
                #testDocs.counts[w] += temp[i].counts[w]
                testwords.extend(Filter.unstem(w))
        #testwords = [Filter.unstem(w) for w in testDocs.counts.keys()]
        #restore Filter.stemdict
        Filter.stemdict, Filter.unstemdict = backupstems
    print 'done'
    # Calculate rankings for held out RDG
    print 'Calculating test rankings...',
    ranks = []
    for w in testwords:
        if w in logProbs:
            temp = logProbs[w]
        else:
            temp = logProbs['[UNK]']
        ranks.append((w, temp))
    ranks.sort(key=lambda x: x[1], reverse=True)
    print 'done'
    # Calculate perplexity
    print 'Calculating perplexity...',
    l = 0.0
    for i in range(N):
        l += ranks[i][1]
    l /= N
    perplexity = 2**(-l)
    print 'done'
    return perplexity

def EMWeights(testfolder, N=300):
    # Need to:
    # 1) calculate probability distributions for each measure
    # 2) import test set
    # 3) set initial weights
    # 4) set tolerance
    # Loop until delta_w < tolerance:
    # E: c_i = (1/N)SUM_j(w_i*q_i(NP_j)/SUM_n(w_n*q_n(NP_j)))
    # M: w_i = c_i/SUM_n(c_n)
    #---------------------------
    # Which measures to use:
    measures = ['TFIDF', 'IDF', 'TokenIDF', 'DRDC', 'TokenDRDC', 'KLDiv']
    #            'Entropy', 'DR', 'DC', 'TF']
    # Calculate term hypothesized probability distribution
    print 'Calculating probabilities...',
    Probs={}
    for measure in measures:
        ranklist = metric.rankTerms(measure)
##        # scale ranks to be 0 < rank <= 1, with sum(ranks)=1
##        min_rank = abs(ranklist[-1][1]) # last score in the list
##        fudgefactor = 0.01*min_rank # to ensure rank > 0 and that unknown NPs have p>0
##        scalefactor = sum(map(lambda x: x[1], ranklist)) + (len(ranklist)+1)*fudgefactor
        # hypothesized probability distribution
        # (of NPs being members of the set of terminology):
        Probs[measure] = {}
        #for item in ranklist:
        #    Probs[measure][item[0]] = 2**item[1]
        #    if Probs[measure][item[0]]==0.0:
        #        print 'Rounding Error! P = 0.0'
        for i in range(len(ranklist)):
            #Probs[measure][ranklist[i][0]] = float(i+1.0)/len(ranklist)
            if i < N:
                Probs[measure][ranklist[i][0]] = 1.0/N - 0.001/N
            else:
                Probs[measure][ranklist[i][0]] = 0.001/(len(ranklist)-N)
##            Probs[measure][item[0]]=(item[1]+fudgefactor)/scalefactor
##        Probs[measure]['[UNK]'] = fudgefactor/scalefactor # probability of a new NP
        print measure+' ',
    print 'done'
    # import test set
    print 'Retrieving test set...',
    global testwords
    try:
        testwords
    except:
        #backup Filter.stemdict, as loading new documents will change it
        backupstems = [Filter.stemdict, Filter.unstemdict]
        Filter.stemdict = {}
        Filter.unstemdict = {}
        #testDocs = Document()
        temp = [Document(testfolder+f) for f in os.listdir(testfolder) if f[-4:]=='.txt']
        testwords = []
        for i in range(len(temp)):
            for w in temp[i].counts:
                #testDocs.counts[w] += temp[i].counts[w]
                testwords.extend(Filter.unstem(w))
        #testwords = [Filter.unstem(w) for w in testDocs.counts.keys()]
        #restore Filter.stemdict
        Filter.stemdict, Filter.unstemdict = backupstems
    print 'done'
    # set initial weights
    weight = {}
    for measure in measures:
        weight[measure] = 1.0/len(measures)
    # set tolerance
    tolerance = 1e-10
    # E-M loop
    print 'Optimizing weights...',
    delta = 1.0
    weight_old = weight.copy()
    while delta > tolerance:
        #print 'Squared change in weight: '+str(delta)
        #E:
        c = {}
        # go through measures
        for j in weight:
            c[j] = 0.0
            # sum through lessor of N words or all of them
            N = min(N, len(testwords))
            for i in range(N):
                NP = testwords[i]
                if not NP in Probs[j]:
                    NP = '[UNK]'
                numer = weight[j]*Probs[j][NP]
                denom = 0.0
                # sum through all the measures
                for n in weight:
                    denom += weight[n]*Probs[n][NP]
                c[j] += numer/denom
            c[j] *= (1.0/N)
        #M:
        delta = 0.0
        for j in weight:
            weight_old[j] = weight[j]
            weight[j] = c[j]/sum(c.values())
            delta += (weight[j]-weight_old[j])**2
    print 'done'
    # set those weights
    metric.setWeights(weight)
    return weight
