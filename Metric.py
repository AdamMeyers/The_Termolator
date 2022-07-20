#!/usr/bin/env python3
import math, nltk, logging, os
from Document import *
import TestData, Wordlist, Settings
import pickle

class Metric:
    """Metric contains all the functions necessary to score an RDG's terminology."""
    def __init__(self, rdgDir, general, working_dir = '.',overwrite=False,rank_from_previous=False,background_cache_file='ranking.pkl', full_to_abbr = False):
        # available metrics
        global bck_cache_file
        bck_cache_file = background_cache_file
        self.metrics = {'DR':self._calDR, 'DC':self._calDC,
                        'DRDC':self._calDRDC, 'IDF':self._calIDF,
                        'TFIDF':self._calTFIDF, 'TokenDRDC':self._calTokenDRDC,
                        'TokenIDF':self._calTokenIDF, 'Entropy':self._calEntropy,
                        'KLDiv':self._calKLDiv, 'Weighted':self._calWeighted,
                        'TF':self._calTF}
        # used for restoring ranking 
        # from previous
        self.rankingmap = {}
        # input files
        self.genDocs = Document(overwrite=overwrite)
        #for numBackDocs # updates by Y Gu 11/2018 for pkl file type compatibility
        self.genDocsNum = 0
        # General document group is given as files in a directory
        if rank_from_previous:
            pass
        elif type(general)== type(str()):
            logging.debug('Loading general documents from '+general)
            # gen = [Document(general+genFile) for genFile in os.listdir(general) if genFile[-4:]=='.txt']
            gen = map(lambda x: Document(filename=x.strip(),overwrite=overwrite), open(general,encoding="utf-8-sig").readlines())
            ## note that the iterator only lets us calculate this once
            ## this is OK because this is the initialization function
            ## other maps should be cast into lists
            # we only need the sum for the general class
            ## python3 compatibility change
            ## TrueTdf updates by Y Gu 6/2018 (next 2 lines + 5 lines in for loop)
            ## Updated again by Y Gu 11/2018 for type compatibility
            for iterator in gen:
                self.genDocsNum += 1
                for w in iterator.counts:
                    self.genDocs.counts[w] += iterator.counts[w]
                    self.genDocs.token_counts[w] += 1 # updates by Y Gu 11/2018 for pkl file type compatibility
        # General document group is given as a corpus
        else:
            logging.debug('Loading from general corpus...')
            # NGrams in lieu of NPs -- we are storing extra info
            words = general.words()
            logging.debug('Unigrams loading')
            bigrams = nltk.bigrams(words)
            logging.debug('Bigrams loading')
            trigrams = nltk.trigrams(words)
            logging.debug('Trigrams loading')
            #filters = ['abbreviation', 'case', 'stem']
            filters = Settings.getCorpusFilters()
            logging.debug('Filtering unigrams')
            for w in words:
                for filt in filters:
                    # if filt == 'abbreviation':
                    #     w = Filter.criteria[filt](w,full_to_abbr) 
                    #     ## Somewhat of a kludge, the more general approach
                    #     ## would be to allow all filters to take multiple arguments.
                    #     ## If these get expanded, that would be the way to go.
                    # else:
                    w = Filter.criteria[filt](w)
                if w:
                    self.genDocs.counts[w] += 1
                    self.genDocs.token_counts[w] += 1
            logging.debug('Filtering bigrams')
            for gram in bigrams:
                w = ' '.join(gram)
                for filt in filters:
                    w = Filter.criteria[filt](w)
                if w:
                    self.genDocs.counts[w] += 1
            logging.debug('Filtering trigrams')
            for gram in trigrams:
                w = ' '.join(gram)
                for filt in filters:
                    w = Filter.criteria[filt](w)
                if w:
                    self.genDocs.counts[w] += 1
            logging.debug('done')
        # Related Document Group -- we need each document separately
        logging.debug('Loading RDG from '+rdgDir+'...')
        self.rdgDocs = list (map(lambda x: Document(filename=x.strip(),overwrite=overwrite), open(rdgDir,encoding='utf-8-sig').readlines()))
        ## Python 3 compatibility -- rdgDocs needs to be a list and Python3 makes it an iterator
        logging.debug('done')


    def _getTermFreq(self, word):
        """Returns the term frequency in the rdgDocs"""
        if not hasattr(self, '_TermFreq'):
            self._TermFreq = {}
        if word in self._TermFreq:
            freq = self._TermFreq[word]
        else:
            freq = 0
            ## print(0,'Looking for',word)
            for doc in self.rdgDocs:
                ## print(0,doc)
                if word in doc.counts:
                    ## print(1,word,doc.counts[word]) ## 57
                    freq += doc.counts[word]
            self._TermFreq[word] = freq
        return freq
    def _getTermDocFreq(self, word):
        """Returns the document frequency of a term in the rdg"""
        if not hasattr(self, '_TermDocFreq'):
            self._TermDocFreq = {}
        if word in self._TermDocFreq:
            freq = self._TermDocFreq[word]
        else:
            freq = 0
            for doc in self.rdgDocs:
                if word in doc.counts:
                    freq += 1
            self._TermDocFreq[word] = freq
        return freq
    def _calDR(self, word):
        """Returns the document relevance of a proposed term"""
        if not hasattr(self, '_DR'):
            self._DR = {}
        ## check map
        if (word,'DR') in self.rankingmap:
            DR = self.rankingmap[(word,'DR')]
        elif word in self._DR:
            DR = self._DR[word]
        else:
            posFreq = self._getTermFreq(word)
            if word in self.genDocs.counts:
                negFreq = self.genDocs.counts[word]
            else:
                negFreq = 0
            if (negFreq+posFreq) !=0:
                DR = posFreq*math.log(len(word)+2.0)/(negFreq+posFreq)
            else:
                DR = 0 ## AM july 2017 -- assuming 0/0 equals 0
            self._DR[word] = DR
        return DR
    def _calDC(self, word):
        """Returns the document consensus of a proposed term"""
        if not hasattr(self, '_DC'):
            self._DC = {}
        if (word,'DC') in self.rankingmap:
            DC = self.rankingmap[(word,'DC')]
        elif word in self._DC:
            DC = self._DC[word]
        else:
            posFreq = self._getTermFreq(word)
            DC = 0
            for doc in self.rdgDocs:
                if word in doc.counts:
                    if posFreq != 0:
                        ptd = doc.counts[word]/float(posFreq)
                        DC += ptd*math.log(1/ptd)
                    else:
                        ptd = 0
                        DC = 0 ## AM July 2017 -- assumes 0/0 = 0
            self._DC[word] = DC
        return DC
    def _calDRDC(self, word):
        """Returns the document relevance-document consensus \
(DRDC) of a proposed term"""
        if (word,'DRDC') in self.rankingmap:
            return self.rankingmap[(word,'DRDC')]
        else:
            return self._calDR(word)*self._calDC(word)
    # edit to calculate true IDF = log (numBackDocs/numBackDocs(t)) Y. Gu edit 6/2018
    def _calTrueIDF(self,word):
        # +1 in case the count is zero, add-one smoothing
        #updates by Y Gu 11/2018 for pkl file type compatibility
        return math.log((self.genDocsNum + 1)/(self.genDocs.token_counts[word] +1)) 

    def _calIDF(self, word):
        """Returns the document relevance-inverse document frequency \
(DR-IDF) of a proposed term"""
        if (word,'IDF') in self.rankingmap:
            return self.rankingmap[(word,'IDF')]
        else:
            return self._calDR(word)/math.log(self._getTermDocFreq(word)+3.0)
    def _calTF(self, word):
        """Returns the term frequency of a proposed term"""
        #I ADDED THIS ONE FOR REFERENCE
        return self._getTermFreq(word)
    def _calTFIDF(self, word):
        """Returns the term frequency-inverse document frequency (TF-IDF) \
of a proposed term"""
        if not hasattr(self, '_TFIDF'):
            self._TFIDF = {}
        if word in self._TFIDF:
            TFIDF = self._TFIDF[word]
        else:
            maxFreq = 0
            for doc in self.rdgDocs:
                if word in doc.counts and doc.counts[word] > maxFreq:
                    maxFreq = doc.counts[word]
            #edit to use true IDF instad of DR Y. Gu edit 6/2018
            #TFIDF = self._calDR(word)*maxFreq
            TFIDF = self._calTrueIDF(word)*maxFreq
            self._TFIDF[word] = TFIDF
        return TFIDF
    def _calTokenDR(self, word):
        """Token frequency adjustment helper function"""
        if not hasattr(self, '_TokenDR'):
            self._TokenDR = {}
        if word in self._TokenDR:
            tokenDR = self._TokenDR[word]
        else:
            tokenDR = 0.0
            tokens = word.split()
            for t in tokens:
                if not t.isdigit():
                    #the frequencies are based on pure word counts, not NP counts!
                    token_rel = 0.0
                    for doc in self.rdgDocs:
                        token_rel += doc.token_counts[t]
                    token_total = token_rel + self.genDocs.token_counts[t]
                    if token_total!=0: ## AM July 7 -- treating 0 divided by 0 as 0
                        ## changed to !=0 from > 0 on July 10
                        tokenDR += token_rel/float(token_total)
            if len(tokens) == 0:
                tokenDR = 0 ## prevent divide by zero error 3/11/2019
            else:
                tokenDR /= len(tokens)
            self._TokenDR[word] = tokenDR
        return tokenDR
    def _calTokenDRDC(self, word):
        """Returns the document relevance-document consensus (DRDC) of \
a proposed term, adjusted for token frquency"""
        if (word,'TokenDRDC') in self.rankingmap:
            return self.rankingmap[(word,'TokenDRDC')]
        else:
            return self._calDRDC(word)*self._calTokenDR(word)
    def _calTokenIDF(self, word):
        """Returns the document relevance-inverse document frequency \
(DR-TokenIDF) of a proposed term, adjusted for token frequency"""
        if (word,'TokenIDF') in self.rankingmap:
            return self.rankingmap[(word,'TokenIDF')]
        else:
            return self._calIDF(word)*self._calTokenDR(word)
    def _calEntropy(self, word):
        """Return the pseudo-entropy of a proposed term"""
        #-sum(p*log(p)) = -sum((c/N)*log(c/N))
        # = -sum((1/N)*c*(log(c)-log(N)))
        # = -sum((1/N)*c*log(c)) + sum((1/N)*c*log(N))
        # = -(1/N)sum(clog(c))+(log(N)/N)*sum(c)
        # ~ -sum(clog(c)) + A*sum(c)
        # ~ -sum(clog(c)) + A*N
        # ~ -sum(clog(c)) + B
        # ~ -sum(clog(c))
##        # but flip sign since "most negative" here is actually most important
##        #observations+1 to avoid log(0)
        c = (self._getTermFreq(word) + 1)
        return -c*math.log(c)
    def _calKLDiv(self, word):
        """Return the pseudo-log relative entropy of a proposed term"""
        #sum(log(p/q)*p)
        # = sum(log((c1/N1)/(c2/N2))*(c1/N1))
        # = sum(log(c1*N2/(c2*N1))*c1/N1)
        # = sum((log(c1*N2)-log(c2*N1))*c1/N1)
        # = sum((log(c1)+log(N2)-log(c2)-log(N1))c1/N1)
        # = sum((log(c1)-log(c2))*c1/N1) + sum((log(N2)-log(N1))*cl/N1)
        # = (1/N1)sum((log(c1)-log(c2))c1) + (1/N1)log(N2/N1)*sum(c1)
        # = (1/N1)sum((log(c1)-log(c2))c1) + (1/N1)log(N2/N1)*N1
        # = (1/N1)sum((log(c1)-log(c2))c1) + log(N2/N1)
        # ~ sum((log(c1)-log(c2))*c1)
        #q (c2) is gen, p (c1) is rdg
        #observations+1 to avoid log(0)
        c1 = self._getTermFreq(word) + 1
        c2 = (self.genDocs.counts[word] + 1)
        return (math.log(c1) - math.log(c2))*c1
    def _calSectionPrior(self, word):
        """NOT CURRENTLY SUPPORTED"""
        #CURRENTLY, THIS DOESN'T SUM TO ONE!!!!!
        #priors = {'Acknowledgements':0.01, 'Conclusion':0.9, 'Background':0.9,
        #          'Results':0.8, 'Methods':0.25, 'Authors\' contributions':0.1,
        #          'Discussion':0.9, 'Introduction':0.9,
        #          'Results and Discussion':0.8, 'Supplementary Material':0.1,
        #          'Supporting Information':0.1}
        #priors = {'Supplementary Material': 0.001}
        p = 1.0
        return p
    def setWordlistProbs(self, probs):
        """Input dictionary of probabilities for terms in wordlists.
Keys = 'patent', 'science', 'law', 'common', and 'medicine'."""
        self.lstProbs = probs.copy()
    def _calWordlistPrior(self, word):
        ## piece of Zak's code that is not used
        lstfolder = './wordlists/'
        lstfiles = [('patent', 'patents.lst'),('science', 'academic.lst'),
                    ('law','idcourts.lst'), ('law', 'nycourts.lst'),
                    ('law','uscourts.lst'), ('common', 'gsl.lst'),
                    ('medicine','medical_roots.lst')]
        if not hasattr(self, 'lstProbs'):
            self.lstProbs = {'patent':0.75, 'science':0.25, 'law':0.25,
                             'common':0.01, 'medicine':0.75}
        if not hasattr(self, 'wordlistdict'):
            self.wordlistdict = {}
            for item in lstfiles:
                lst = Wordlist.load(lstfolder+item[1])
                if item[0] in self.wordlistdict:
                    self.wordlistdict[item[0]] += lst
                else:
                    self.wordlistdict[item[0]] = lst
            for label in self.wordlistdict:
                pattern = Wordlist.compile_lst(self.wordlistdict[label])
                self.wordlistdict[label] = pattern
        prior = 1.0
        for label in self.wordlistdict:
            ## stems = Filter.unstem(word)
            for s in [word]:
                matches = Wordlist.patternFind(self.wordlistdict[label],w,False)
                if matches:
                    prior *= lstProbs[label]
                    break
        return prior
    def setWeights(self, dictWeights):
        """Input dictionary of weights for weighted measurements.
Keys = 'DC', 'DR', 'DRDC', 'TokenDRDC', 'IDF', 'TFIDF', 'TokenIDF', 'Entropy', 'KLDiv'."""
        self.weights = dictWeights.copy()
    def _calWeighted(self, word):
        """Returns the weighted score of a word over several different metrics"""
        ret = 0.0
        try:
            self.weights
        except:
        #    self.weights = {'DC': -1.1, 'TokenIDF': 0.8, 'TokenDRDC': 0.8,
        #                    'TFIDF': 0.3, 'IDF': 0.1, 'DR': 0.2, 'DRDC': 0.2}
        #    self.weights = {'TFIDF': 0.4, 'KLDiv': 0.4, 'Entropy': 0.1,
        #                    'IDF': 0.6, 'TokenDRDC': 0.3, 'DR': 0.4,
        #                    'DC': -1.8, 'TokenIDF': 1.7, 'DRDC': 0.5}
        #    self.weights = {'DC': -2.0, 'TokenIDF': 0.8, 'TokenDRDC': 0.7,
        #                    'TFIDF': 0.3, 'IDF': 0.1, 'DR': 0.3,
        #                    'DRDC': 0.26,'KLDiv':0.01,'Entropy':0.04}
            self.weights = Settings.getMetricWeights()
        for measure in self.weights:
            ret += self.weights[measure]*self.metrics[measure](word)
        #ret *= self._calSectionPrior(word)
        #ret *= self._calWordlistPrior(word)
        return ret
    def rankTerms(self, measure='DRDC', save=True):
        """Score the RDG, return list of (word, rank) tuples"""
        ranking = []
        ## ranking_map = {} # separate map to not impose
        self.ranking_map = {} # AM change May 27
        logging.debug('Entering rankTerms, loading keys...')
        words = set()
        for d in self.rdgDocs:
            words.update(d.counts.keys())
        logging.debug('Done')
        logging.debug('Measuring ranks...')
        i = 0
        for w in words:
            i += 1
            if i % 1000 == 0:
                logging.debug('Measuring word '+str(i))
            temp = self.metrics[measure](w)
            for s in [w]: 
                ## Filter.unstem(w): #include all word variants
                ranking.append((s, temp))
                if save:
                    #logging.error("Saving word: " + str(s) + " to ranking.pkl  with measurement: " + measure + " and value: " + str(temp))
                    ## ranking_map[(s,measure)]=temp
                    self.ranking_map[(s,measure)]=temp # AM change May 27
            #ranking.append((w, temp))
        logging.debug('Done')
        logging.debug('Sorting...')
        ranking.sort(key=lambda x: x[1], reverse=True)
        #pickle.dump(ranking_map, open(bck_cache_file,'w'))
        f = open(bck_cache_file, 'wb')
        #pickle.dump(ranking_map,f,encoding="utf-8")
        ## pickle.dump(ranking_map,f) ## AM
        print('loading')
        stuff_to_save = (self.genDocsNum,self.genDocs)
        pickle.dump(stuff_to_save,f)
        logging.debug('Done')
        return ranking
    def rankTermsFromPrevious(self, measure='DRDC'):
        """Score the RDG, return list of (word, rank) tuples"""
        # we only need the sum for the general class
        #self.rankingmap = pickle.load(open(bck_cache_file,'r'))
        f = open(bck_cache_file, 'rb')
        self.genDocsNum,self.genDocs = pickle.load(f)
        ranking = [] # this ranking is a local array, not the cached
        self.ranking_map = {} 
        logging.debug('Entering rankTerms, loading keys...')
        words = set()
        for d in self.rdgDocs:
            words.update(d.counts.keys())
        logging.debug('Done')
        logging.debug('Measuring ranks...')
        i = 0
        for w in words:
            i += 1
            if i % 1000 == 0:
                logging.debug('Measuring word '+str(i))
            temp = self.metrics[measure](w)
            for s in [w]:
                ## Filter.unstem(w): #include all word variants
                ranking.append((s, temp))
            #ranking.append((w, temp))
          #logging.debug('Done')
##        # force ranks to be [0,1]
        logging.debug('Sorting...')
        ranking.sort(key=lambda x: x[1], reverse=True)
        #self.rankingmap.sort(key=lambda x: x[1], reverse=True)
        logging.debug('Done')
        return ranking
    def rankFile(self, filename, measure='DRDC'):
        """Score a file rather than an entire RDG. NOT SUPPORTED!"""
        ranking = []
        d = Document(filename=filename,overwrite=overwrite)
        for w in d.counts:
            temp = self.metrics[measure](w)
            for s in [w]:
                ## Filter.unstem(w):
                ranking.append((s, temp))
##        # force ranks to be [0,1]
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking
    def rankWordList(self, filename, measure='DRDC'):
        """Score a word list stored in a file (one word per line)."""
        ranking = []
        words = []
        f = open(filename,encoding="utf-8-sig")
        for line in f:
            w = line.strip()
            if w != '':
                words.append(w)
        f.close()
        ## useStem = 'stem' in Settings.getDocumentFilters() #are words stemmed?
        for w in words:
            temp = self.metrics[measure](w)
            ranking.append((w, temp))
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking
    def scoreByRankSum(self, termfiles, measure='DRDC'):
        """Score a metric on a document against a premade list."""
        terms = set()
        filters = ['case']#['abbreviation', 'case', 'stem']
        for f in termfiles:
            temp = TestData.load(f)
            for w in temp:
                for filt in filters:
                    w = Filter.criteria[filt](w)
                if w:
                    terms.add(w)
        ranking = self.rankTerms(measure)
        score = 0
        for t in terms:
            r = filter(lambda x: x[0]==t, ranking)
            #print t + ': ' + str(r)
            if r:
                r = r[0]
                score += ranking.index(r)
            else:
                score += len(ranking)+1
        #print score
        return score
    def scoreByTop(self, termfiles, measure='DRDC', n=300):
        """Score a metric on a document against a premade list."""
        terms = set()
        filters = ['case'] #['abbreviation', 'case', 'stem']
        for f in termfiles:
            temp = TestData.load(f)
            for w in temp:
                for filt in filters:
                    w = Filter.criteria[filt](w)
                if w:
                    terms.add(w)
        ranking = self.rankTerms(measure)
        score = 0
        for t in terms:
            r = filter(lambda x: x[0]==t, ranking[:n])
            #print t + ': ' + str(r)
            if r:
                score += 1
        #print score
        return score
    def _twiddleWeights(self, termfiles):
        """Use twiddle to find and return a dictionary of weights \
for use in weighted scoring. This method is VERY slow."""
        self.weights = {'DR':0.5, 'DC':0.5, 'DRDC':0.5, 'IDF':0.5,
                        'TFIDF':0.5, 'TokenDRDC':0.5, 'TokenIDF':0.5,
                        'Entropy':0.5, 'KLDiv':0.5}
        #self.weights = {'DR': 0.2, 'DC': -1.1, 'DRDC': 0.2, 'TokenDRDC': 0.8,
        #                'TFIDF': 0.3, 'IDF': 0.1, 'TokenIDF': 0.8,
        #                'Entropy':0.5, 'KLDiv':0.5}
        for i in range(100):
            for w in self.weights:
                print(w, 1)
                currweight = self.weights[w]
                currscore = self.scoreByRankSum(termfiles, measure='Weighted')
                print (w, 2)
                self.weights[w] = currweight - 0.1
                score = self.scoreByRankSum(termfiles, measure='Weighted')
                print (w, 3)
                if score < currscore:
                    continue
                print (w, 4)
                self.weights[w] = currweight + 0.1
                score = self.scoreByRankSum(termfiles, measure='Weighted')
                print (w, 5)
                if score < currscore:
                    continue
                print (w, 6)
                self.weights[w] = currweight
                print (w, 7)
            print (self.weights)
        return self.weights
    def _EMWeights(testfolder, N=300):
        """Use EM to find and return a dictionary of weights for use in \
weighted scoring. Here we are minimizing the perplexity of a held out set."""
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
        # Calculate term hypothesized probability distribution
        print ('Calculating probabilities...',)
        Probs={}
        for measure in measures:
            ranklist = metric.rankTerms(measure)
            # hypothesized probability distribution
            # (of NPs being members of the set of terminology):
            Probs[measure] = {}
            for item in ranklist:
                Probs[measure][item[0]] = 2**item[1]
                if Probs[measure][item[0]]==0.0:
                    raise('Rounding Error! P = 0.0')
            print (measure+' ',)
        print ('done')
        # import test set
        print ('Retrieving test set...',)
        try:
            self.testwords
        except:
            #backup Filter dictionaries, as loading new documents will change them
            ## backupstems = [Filter.stemdict, Filter.unstemdict]
            ### I don't think this code will ever actually be loaded
            ## Filter.stemdict = {}
            ## Filter.unstemdict = {}
            temp = [Document(filename=testfolder+f,overwrite=overwrite) for f in os.listdir(testfolder) if f[-4:]=='.txt']
            testwords = []
            # for i in range(len(temp)):
            #     for w in temp[i].counts:
            #         testwords.extend(Filter.unstem(w))
            # #restore Filter.stemdict
            # Filter.stemdict, Filter.unstemdict = backupstems
        print ('done')
        # set initial weights
        weight = {}
        for measure in measures:
            weight[measure] = 1.0/len(measures)
        # set tolerance
        tolerance = 1e-10
        # E-M loop
        print ('Optimizing weights...',)
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
                N = min(N, len(self.testwords))
                for i in range(N):
                    NP = self.testwords[i]
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
        print ('done')
        # set those weights
        metric.setWeights(weight)
        return weight
    def findWeights(self, testfolder):
        return _EMWeights(self, testfolder, 300)
