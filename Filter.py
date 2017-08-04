import re, pickle, logging, os
from nltk.stem import PorterStemmer as Stemmer # NLTK's license, Apache
from nltk.corpus import stopwords # not encumbered by license, see stopwords.readme()

abbreviations={}
stops = []
stemmer = None
stemdict = {} # stemming dictionary
unstemdict = {} # reverse stemming dictionary
dir_name = os.path.dirname(os.path.realpath(__file__)) + os.sep
logger = logging.getLogger()

def _get_abbreviations(filename='./jargon.out'):
    """Import abbreviations from jargon file"""
    f = open(filename)
    for line in f:
        temp = line.split('|||')
        fullword = temp[0]
        shortwords = temp[1].split('||')
        for w in shortwords:
            abbreviations[w] = fullword
    f.close()
def _get_stops(filename=dir_name + 'patentstops.txt'):
    """Import stop words either from a text file or stopwords corpus"""
    global stops
    if filename:
        f = open(filename)
        for line in f:
            stops += line.split()
        f.close()
    else:
        stops = stopwords.words('english')
def _get_stemdict(filename):
    logger.debug('Loading stemming dictionary...')
    f = open(filename, 'rb')
    global stemdict
    global unstemdict
    stemdict, unstemdict = pickle.load(f,encoding="utf-8")
    f.close()
def _save_stemdict(filename):
    logger.debug('Saving stemming dictionary...')
    f = open(filename, 'wb')
    global stemdict
    global unstemdict
    pickle.dump((stemdict, unstemdict),f,encoding="utf-8")
    f.close()
def _reGlue(words):
    """Helper function to turn a list of words into a string"""
    ret = ""
    for i in range(len(words)):
        ret += words[i] + " "
    ret = ret.strip()
    return ret
def expand(string):
    """Expand abbreviations within string"""
    global abbreviations
    if not abbreviations:
        _get_abbreviations()
    words = string.split()
    for i in range(len(words)):
        temp = abbreviations.get(words[i])
        if temp:
            words[i] = temp
    string = _reGlue(words)
    return string
def removeStops(string): #NOT NEEDED AS NP EXTRACTING REMOVES THEM
    """Strip stop words off the beginning and ending of a phrase"""
    global stops
    if not stops:
        _get_stops()
    # entire phrase in stops
    if string in stops:
        return ""
    words = string.split()
    if not words:
        return ""
    # beginning stops (loses case of multiword stops)
    while words[0] in stops:
        words.pop(0)
        if not words:
            return ""
    # ending stops (loses case of multiword stops)
    while words[-1] in stops:
        words.pop(0)
        if not words:
            return ""
    string = _reGlue(words)
    return string

def bad_unicode(string):
    for char in string:
        if ord(char)>127:
            ## print(char)
            return(True) 
            
def remove_non_unicode(string):
    output = ''
    for char in string:
        if ord(char)>127:
            output=output+' '
        else:
            output=output+char
    output = output.strip(' ')
    return(output)
    
def stem(string):
    """Stem a phrase"""
    global stemmer
    if not stemmer:
        stemmer = Stemmer()
    #words = string.split()
    #for i in range(len(words)):
    #    words[i] = self.stemmer.stem(words[i])
    # stemming last word only
    #string = self._reGlue(words)
    #
    #string2 = stemmer.stem(string)
    #if string2 not in stemdict:
    #    stemdict[string2] = string
    # FIX ME
    if string not in stemdict:
        if bad_unicode(string):
            ## added A. Meyers 8/28/15
            string = remove_non_unicode(string)
            if len(string)>3:
                temp = stemmer.stem(string)
            else:
                temp = string
        elif len(string)>3:
            ## print('***',string,'***')
            temp = stemmer.stem(string)
        else:
            temp = string
        if temp:
            stemdict[string] = temp
        if not temp:
            pass
        elif temp not in unstemdict:
            unstemdict[temp] = [string]
        elif string not in unstemdict[temp]:
            unstemdict[temp].append(string)
    else:
        temp = stemdict[string]
    return temp

def unstem(string):
    """Undo stemming of a phrase"""
    global stemdict
    #if string in stemdict:
    #    return stemdict[string]
    #else:
    #    return string
    if string in unstemdict:
        return unstemdict[string]
    else:
        return [string]
def lowercase(string):
    """Return an all lowercase representation of a string"""
    return string.lower()
def isWord(string):
    """Test the legitimacy of the proposed phrase. Taken from Shasha's implementation"""
    #criteria:
    pattern = re.compile(r"""
(
&lt
|%
|/
|\\
|&\ lt
|\)
|\(
|\.
|\+
|and\
|\ and
|\ and\
)
""", re.I | re.VERBOSE | re.UNICODE)
    if len(string) < 2:
        return ''
    elif re.findall(pattern, string):
        return ''
    #must contain at least one letter
    for i in range(len(string)):
        if string[i].isalpha():
            return string
    return ''

# available filters:    
criteria={'abbreviation': expand,
          'stops': removeStops,
          'stem': stem,
          'case': lowercase,
          'isWord': isWord}
