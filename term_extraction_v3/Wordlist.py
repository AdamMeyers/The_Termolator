import os, re
from nltk.corpus import brown # Probably an unencumbered license
from nltk import FreqDist

fd = None

def load(filename):
    """Load wordlist file, return a list of words.
Wordlist file format:
...
[Start]
WORD/REGEX
WORD/REGEX
...
EOF
"""
    if not os.path.exists(filename):
        raise OSError(2, 'Error reading from file')
    lst = []
    f = open(filename)
    #skip header
    for line in f:
        if line == '[Start]\n':
            break
    #get words
    for line in f:
        lst.append(line[:-1])
    f.close()
    return lst

def compile_lst(lst):
    """Compile a list of words into one regular expression."""
    string = '\\b('+'|'.join(lst)+')\\b'
    pattern = re.compile(string, re.VERBOSE | re.IGNORECASE)
    return pattern
        
def stripAbbrevations(lst):
    """Strip abbrieviations from a list of words (ie. "WORD (WRD)" -> "WORD")\
, return a dictionary with key=abbreviation and value=full word."""
    pattAbbrev = re.compile(r'\((.*)\)')
    pattFull = re.compile(r'(.*)\(')
    ret = {}
    for i in range(len(lst)):
        abbrev = re.findall(pattAbbrev, lst[i])
        full = re.findall(pattFull, lst[i])
        if abbrev:
            abbrev=abbrev[0]
            full=full[0].strip()
            ret[abbrev] = full
            lst[i] = full
    return ret

def patternFind(pattern, text, uncommon_only=True):
    """Find all matches of a pattern in a text, \
optionally restricting matches to uncommon words only."""
    text = text.lower()
    matches = re.findall(pattern, text)
    if uncommon_only:
        global fd
        if not fd:
            words = brown.words()
            fd = FreqDist(words)
        matches = [m for m in matches if fd[m]<3] #3 is handwavy, but decent
    return set(matches)

def listFind(lst, text):
    """Return the set of all elements of a list that are found in a given text."""
    matches = [l for l in lst if l in text]
    return set(matches)
