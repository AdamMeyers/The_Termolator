from nltk import NaiveBayesClassifier
import random
import re
import data
from positivenaivebayes import *

def word_features(word):
    """Return a dictionary of letter-wise ngrams as features"""
    featureset = {}
    # case-insensitive:
    word = word.lower()
##    # length
##    featureset['LENGTH'] = len(word)
    # 1-grams
    for i in range(len(word)):
##        featureset[word[i]] = True
## OR:
       if word[i] in featureset:
           featureset[word[i]] += 1
       else:
           featureset[word[i]] = 1
    # pad with X's to represent word boundaries
    word = 'X' + word + 'X'
    # 2-grams
    for i in range(len(word)-1):
##        featureset[word[i:i+2]] = True
## OR:
        if word[i:i+2] in featureset:
            featureset[word[i:i+2]] += 1
        else:
            featureset[word[i:i+2]] = 1
    # 3-grams
    for i in range(len(word)-2):
##        featureset[word[i:i+3]] = True
## OR:
        if word[i:i+3] in featureset:
            featureset[word[i:i+3]] += 1
        else:
            featureset[word[i:i+3]] = 1
    # 4-grams
    for i in range(len(word)-3):
##        featureset[word[i:i+4]] = True
## OR:
        if word[i:i+4] in featureset:
            featureset[word[i:i+4]] += 1
        else:
            featureset[word[i:i+4]] = 1
    # 5-grams
    for i in range(len(word)-4):

##        featureset[word[i:i+5]] = True
## OR:
        if word[i:i+5] in featureset:
            featureset[word[i:i+5]] += 1
        else:
            featureset[word[i:i+5]] = 1
    return(featureset)

def get_classifier(**paths):#filename1, filename2, label1, label2):
    """Import word list files and build a classifier to distinguish between \
them. The keys associated with **paths are the labels and the values are \
the word list file locations.
"""
##    # get the words
##    words1 = []
##    words2 = []
##    f = open(filename1, 'r')
##    for line in f:
##        words1.extend(line.split())
##    f.close()
##    f = open(filename2, 'r')
##    for line in f:
##        words2.extend(line.split())
##    f.close()
##    # shuffle the words together
##    words = ([(word, label1) for word in words1] + [(word, label2) for word in words2])
##    random.shuffle(words)
##    # get the features
##    features = [(word_features(word), label) for (word, label) in wordlist]
    # get the words
    words = {}
    for label in paths:
        words[label]=[]
        f = open(paths[label])
        for line in f:
            words[label].extend(line.split())
        f.close()
    # get the features
    features = []
    for label in words:
        features += [(word_features(w), label) for w in words[label]]
    # shuffle
    random.shuffle(features)
    # train a Naive Bayes classifier and return it
    classifier = NaiveBayesClassifier.train(features)
    return classifier

def get_positive_classifier(posPaths, unkPaths):
    #posWords = data.import_wordlist(posPath).keys()
    #unkWords = data.import_wordlist(unkPath).keys()
    posWords = []
    for path in posPaths:
        f = open(path)
        for line in f:
            posWords.extend(line.split())
        f.close()
    unkWords = []
    for path in unkPaths:
        f = open(path)
        for line in f:
            unkWords.extend(line.split())
        f.close()
    positive_features = [word_features(word) for word in posWords]
    unlabeled_features = [word_features(word) for word in unkWords]
    classifier = PositiveNaiveBayesClassifier.train(positive_features, unlabeled_features)
    return classifier

def get_tokens(filename, classifier, label):
    """Get all tokens classified as label from a particular file"""
    # read the file
    f = open(filename)
    text = f.read()
    f.close()
    # cut out anything that is not alphanumeric or '-'
    pattern = re.compile('[^\w-]+')
    text = pattern.sub(' ', text)
    # classify the words - ADD CONCATENATION OF CONTIGUOUS BLOCKS?
    words = text.split()
    classes = [(w, classifier.classify(word_features(w))) for w in words]
    labeledset=set(classes)
    # return tokens classified with label
    tokens=[word for (w, l) in labeledset if l==label]
    return tokens
