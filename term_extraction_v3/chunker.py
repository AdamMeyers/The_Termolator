import os
from nltk.corpus import PlaintextCorpusReader
from nltk import pos_tag
from nltk.chunk import RegexpParser
def extractPossibleTerms(root, fileids):
    # get corpus
    #root, filename = os.path.split(path)
    reader = PlaintextCorpusReader(root, fileids)
    # get chunker
    grammar = 'NP: {<JJ>*<NNP>*<NN>*}'
    chunker = RegexpParser(grammar)
    # get terms
    terms = set()
    print len(reader.sents())
    i = 0
    for sent in reader.sents():
        i += 1
        if i%100==0:
            print i
        tree = chunker.parse(pos_tag(sent))
        for t in tree.subtrees(lambda t: t.node!='S'): # exclude Sentence node
            terms.add(' '.join([el[0] for el in t]))
    return terms
            
