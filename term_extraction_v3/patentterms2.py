import re, os
import nltk
from nltk.corpus import PlaintextCorpusReader, stopwords
import chunker

def getSpecificTerms(path):
    """Outputs a list of terms in a given path."""
    # get corpus
    #root, filename = os.path.split(path)
    reader = PlaintextCorpusReader(path, '.*\.txt')
    words = reader.words()
    bigrams = nltk.bigrams(words)
    trigrams = nltk.trigrams(words)
    quadgrams = nltk.ngrams(words, 4)
    nps = bigrams+trigrams+quadgrams
##    nps = chunker.extractPossibleTerms(path, '.*\.txt')
    # get stops
    stops = stopwords.words('english')
    stops = set(stops+[s.capitalize() for s in stops])
    ret = set()
    for np in nps:
        last_triggers = ['assembly', 'assemblies', 'element', 'elements',
                         'device', 'devices']
        first_triggers = ['first', 'second', 'third', 'fourth']
        # no stops allowed
        if stops.intersection(np):
            continue
        # last word triggers
        if np[-1] in last_triggers:
            temp = ' '.join(np)
            if temp.replace(' ','').isalpha():
                ret.add(temp)
            temp = ' '.join(np[:-1])
            if temp.replace(' ','').isalpha(): # also disallows ''
                ret.add(temp)
        # first word triggers
        if np[0] in first_triggers:
            temp = ' '.join(np)
            if temp.replace(' ','').isalpha():
                ret.add(temp)
            temp = ' '.join(np[1:])
            if temp.replace(' ','').isalpha():
                ret.add(temp)
        # numbered (and optionally lettered) terms
        if not np[-1].isalpha() and np[-1].isalnum():
            temp = ' '.join(np[:-1])
            if temp.replace(' ','').isalpha():
                ret.add(temp)
    return ret
