#NOTE: THE GENIA TAGGER HAS A RESTRICTIVE LICENSE,
#USE AN UNENCUMBERED GENIA-STYLE ALTERNATIVE
import subprocess, os, logging, pickle
from nltk import FreqDist
import Filter

genia_path = './genia/'
### assumes genia tagger -- not currently used

class Word:
    """Each Word contains a string representation, part-of-speech tag, and \
chunk tag."""
    def __init__(self, word, pos, chunk):
        self.word = word
        self.pos = pos
        self.chunk = chunk
    def __str__(self):
        #s = "[" + self.word + ": " + self.pos + ", " + self.chunk + "]"
        s = self.word
        return s

##class NounPhrase:
##    """A NounPhrase is a collection of Word objects."""
##    def __init__(self, *words):
##        self.words = []
##        self.words += words
##    def __len__(self):
##        if self.words:
##            return len(self.words)
##        else:
##            return 0
##    def _wordtype(self, value):
##        if (hasattr(value, 'word') and
##                hasattr(value, 'pos') and
##                hasattr(value, 'chunk')):
##            return True
##        return False
##    # The next two overloads allow use of [] indexing to access phrase words
##    def __getitem__(self, index):
##        return self.words[index]
##    def __setitem__(self, index, value):
##        if not _wordtype(value):
##            raise TypeError
##        self.words[index] = value
##    # The next two overloads allow easy addition of new Words to the NounPhrase
##    def __iadd__(self, word):
##        """Implements NP += Word"""
##        self.append(word)
##        return self
##    def append(self, word):
##        """Implements NP.append(word)"""
##        if not self._wordtype(word):
##            raise TypeError
##        self.words.append(word)

class Genia:
    def load(self, filename):
        """Input a file, return a list of tagged Word objects"""
        words = []
        # only run Genia tagger if not already precomputed
        if not os.path.exists(filename+'.genia'):
            logging.info(filename+'.genia not found. This will slow things down.')
            logging.debug('Computing '+filename+'.genia')
            # change directory, otherwise Genia fails
            wdir = os.getcwd()
            os.chdir(genia_path)
            p = subprocess.Popen(["./geniatagger", filename], stdout=subprocess.PIPE)
            # change directory back
            os.chdir(wdir)
            stdout = p.communicate()[0]
            #print stderr
            logging.debug('done')
            # save to file for next time
            logging.debug('Saving '+filename+'.genia')
            f = open(filename+'.genia','w')
            f.write(stdout)
            f.close()
            logging.debug('done')
        else:
            f = open(filename+'.genia')
            stdout = f.read()
            f.close()
        # get info
        for line in stdout.split('\n'):
            temp = line.split()
            # skip blank lines
            if len(temp) < 4:
                continue
            # get the word (and it's attributes)
            w = Word(temp[0].strip(' '), temp[2], temp[3])
            # add to the list
            words.append(w)
        return words


class GeniaReader:
    def load(self, filename):
        """Input a file, return a list of tagged Word objects"""
        words = []
        # read genia file
        f = open(filename)
        stdout = f.read()
        f.close()
        # get info
        for line in stdout.split('\n'):
            temp = line.split()
            # skip blank lines
            if len(temp) < 4:
                continue
            # get the word (and it's attributes)
            w = Word(temp[0].strip(' '), temp[2], temp[3])
            # add to the list
            words.append(w)
        return words

class NPParser:
    def extractNPs(self, words):
        """Takes a list of Word objects as input, returns a list of NounPhrases."""
        NPs = [] # list of NounPhrases
        NP = [] # NounPhrase is a list of Words
        for i in range(len(words)):
            # B-NP starts a new phrase
            if words[i].chunk == "B-NP":
                # If the previous phrase exists, end it and add to list
                if NP:
                    ## NPs.append(NP)
                    NPs.append(NP)
                # Start a new phrase
                NP = [words[i]]
            # I-NP continues a phrase
            elif words[i].chunk == "I-NP":
                NP.append(words[i])
            # any other tag breaks the phrase
            else:
                if NP:
                    ## NPs.append(NP)
                    NPs.append(NP)
                NP = []
        return NPs
    def extractPossibleTerms(self, NP, relaxed=False, disable_substrings=True):
        """Takes a NounPhrase and outputs a list of strings of possible terms"""
        ## bug fix -- substrings handled when creating tchunk file (after 2017 recoding)
        ## this function may overgenerate
        ## disable_substrings portion of this function to test this
        terms = set()
        # set pos equal to the possible terms' start position
        # (i.e. trim leading words)
        pos = 0
        while pos < len(NP):
            token = NP[pos]
            if (token.pos == "JJ") or (token.pos[:2] == "NN" ) or (token.pos in ['VBG','VBN']):
                break
            else:
                pos += 1
        # if no word in NP is part of a possible term, finish
        if pos >= len(NP):
            return terms
        # if not relaxed, collect all possible terms beginning at pos
        if not relaxed:
            term = ""
            for i in range(pos,len(NP)):
                # add each successive subset to the list
                # i.e. "word1", "word1 word2", "word1 word2 word3"
                term = term + " " + NP[i].word.strip(' ')
                # cannot end on pos tag "JJ"
                if not NP[i].pos == "JJ":
                    terms.add(term.strip())
        # collect all possible terms beginning at the end
        term = ""
        if not disable_substrings:
            for i in range(len(NP)-1, pos-1, -1):
                # add each successive subset to the list
                # i.e. "word3", "word2 word3", "word1 word2 word3"
                if NP[i].pos[:2] in ['NN','JJ','VBG','VBN']:
                    ## added restriction to prevent terms starting with
                    ## weird POS's (like IN)
                    term = NP[i].word.strip(' ') + " " + term
                    terms.add(term.strip())
        return terms
    def getNPs(self, filename):
        """Input a file, output a list of noun phrases"""
        g = GeniaReader()
        words = g.load(filename)
        NPs = self.extractNPs(words)
        return NPs
    def getTerms(self, filename, filters=[], relaxed=False, overwrite=False):
        """Input file, output a FreqDist of terms"""
        ## filterfname = os.path.join(os.path.dirname(filename),'filter.save')
        if os.path.exists(filename+'.nps'):
            f = open(filename+'.nps','rb')
            old_filters, fd = pickle.load(f)
            f.close()
            if old_filters == filters:
                return fd
        NPs = self.getNPs(filename)
        fd = FreqDist()
        for NP in NPs:
            # get the possible terms for each NP
            terms = self.extractPossibleTerms(NP, relaxed)
            # filter each term by some given criteria
            # this requires keeping case information until this point
            #filt = Filter.Filter() # class containing all filters
            for t in terms:
                for f in filters:
                    t = Filter.criteria[f](t)
                if t:
                    fd[t]+=1
        if overwrite or (not os.path.isfile(filename+'.nps')):
            f = open(filename+'.nps','wb')
            pickle.dump((filters, fd), f)
            f.close()
        # if os.path.exists(filterfname):
        #     os.remove(filterfname)
        return fd
