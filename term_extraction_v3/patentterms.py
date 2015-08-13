import re, os, sys, logging
from nltk.corpus import stopwords
from nltk.corpus import brown as corpus
from nltk import FreqDist
import NPParser, Filter, Settings

LEVEL = logging.DEBUG

def isPatentTerm(phrase):
    """Inputs a potential term, returns a list of nested terms"""
    ret = set()
    words = phrase.split()
    # get stops
    if 'stops' not in locals():
        global stops
        stops = stopwords.words('english')
        stops = set(stops+[s.capitalize() for s in stops])
    # no stops allowed
    if stops.intersection(words):
        return ret
    # last word triggers
    last_triggers = ['assembly', 'assemblies', 'element', 'elements',
                     'device', 'devices']
    if words[-1] in last_triggers:
        if phrase.replace(' ','').isalpha():
            ret.add(phrase)
        temp = ' '.join(words[:-1])
        if temp.replace(' ','').isalpha():
            ret.add(temp)
    # first word triggers
    first_triggers = ['first', 'second', 'third', 'fourth']
    if words[0] in first_triggers:
        if phrase.replace(' ','').isalpha():
            ret.add(phrase)
        temp = ' '.join(words[1:])
        if temp.replace(' ','').isalpha():
            ret.add(temp)
    # numbered terms
    if not words[-1].isalpha() and words[-1].isalnum():
        temp = ' '.join(words[:-1])
        if temp.replace(' ','').isalpha():
            ret.add(temp)
    return ret
def getDNA(filename='../test/patents/US_out/full/US_Xml_1980_US4192770A.txt'):
    f = open(filename)
    text = f.read()
    f.close()
    pattern = re.compile(r'''
        \b([atcg]{3,})\b
        |\b([ATCG]{3,})\b
        |\b([aucg]{3,})\b
        |\b([AUCG]{3,})\b
        ''', re.VERBOSE)
    temp = re.findall(pattern, text)
    ret = set()
    for t in temp:
        for el in t:
            ret.add(el)
    if '' in ret:
        ret.remove('')
    return ret
def getChemicals(filename='../test/patents/US_out/full/US_Xml_1980_US4192770A.txt'):
    f = open(filename)
    text = f.read()
    f.close()
    pattern = re.compile(r'((?:\w+-){2,}\w+)')
    temp = re.findall(pattern, text)
    ret = set()
    if 'bgdwords' not in globals():
        global bgdwords
        bgdwords = FreqDist(corpus.words())
        logging.debug('Corpus loaded')
    for t in temp:
        common = False
        for word in t.split('-'):
            if len(word)>2 and bgdwords[word.lower()]>3:
                common = True
                break
        if not common:
            ret.add(t)
    return ret

def getPatentTerms(filename='../test/patents/US_out/full/US_Xml_1981_US4254395A.txt'):
    parser = NPParser.NPParser()
    filters = ['isWord', 'case', 'stops', 'stem']
    nps = parser.getTerms(filename, filters)
    retlist = []
    for phrase in nps:
        lst = isPatentTerm(phrase)
        retlist.extend(lst)
    return set(retlist)

def getGroupWide(folder='../test/patents/US_out/full/'):
    """Return a set of terms used across an entire set of files."""
    parser = NPParser.NPParser()
    filters = Settings.getDocumentFilters()
    if 'stops' in filters:
        filters.remove('stops')
    termlist = []
    filenames = [f for f in os.listdir(folder) if f[-4:]=='.txt']
    filtfname = os.path.join(folder, 'filter.save')
    if os.path.exists(filtfname):
            Filter._get_stemdict(filtfname)
    for f in filenames:
        nps = parser.getTerms(os.path.join(folder,f), filters)
        termlist.append(nps)
#    if not os.path.exists(filtfname):
#        Filter._save_stemdict(filtfname)
    all_terms = set()
    for termset in termlist:
        all_terms.update(termset)
    retlist = set()
    for term in all_terms:
        count = 0
        for termset in termlist:
            if term in termset:
                count += 1
        if count > len(filenames)*0.2:
            if 'stem' in filters:
                retlist.update(Filter.unstem(term))
            else:
                retlist.add(term)
    return retlist

def run(args):
    usage = 'Usage: ' + args[0] + ' path [-terms|-chem|-dna|-group]'
    logging.basicConfig(level=LEVEL)
    if len(args) < 2 or len(args) > 3:
        print usage
        return None
    path = None
    getFunc = None
    for arg in args[1:]:
        if os.path.isdir(arg):
            path = arg
        elif arg == '-terms':
            getFunc = getPatentTerms
        elif arg == '-chem':
            getFunc = getChemicals
        elif arg == '-dna':
            getFunc = getDNA
        elif arg == '-group':
            getFunc = getGroupWide
    if not path or not getFunc:
        print usage
        return None
    path = os.path.abspath(path)
    logging.info('RDG path: '+path)
    logging.info('Get Function: '+getFunc.func_name)
    if getFunc.func_name == 'getGroupWide':
        terms = getFunc(path)
    else:
        logging.debug('Collecting File ids...')
        filenames = [f for f in os.listdir(path) if f[-4:]=='.txt']
        terms = []
        logging.debug('Finding terms...')
        filtfname = os.path.join(path, 'filter.save')
        if getFunc.func_name == 'getPatentTerms' and os.path.exists(filtfname):
            Filter._get_stemdict(filtfname)
        for f in filenames:
            logging.debug('...'+f+'...')
            terms.extend(getFunc(os.path.join(path,f)))
#        if getFunc.func_name == 'getPatentTerms' and not os.path.exists(filtfname):
#            Filter._save_stemdict(filtfname)
        logging.debug('Clean up...')
        if getFunc.func_name == 'getPatentTerms':
            temp = set()
            for t in terms:
                temp.update(Filter.unstem(t))
            terms = temp
        terms = set(terms)
    return terms

def __main__(args):
    terms = run(args)
    if terms:
        for t in terms:
            print t

if __name__ == '__main__':
    __main__(sys.argv)
