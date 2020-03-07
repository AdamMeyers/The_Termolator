import os, pickle
from nltk import FreqDist
import NPParser, Filter, Section, Settings

class Document:
    """A Document object contains: filename - file location, and \
words - a dict with words as keys and word counts as values."""
    def __init__(self, filename=None,overwrite=False):
        self.filename = filename
        #REMINDER, INCLUDE METATAG DATA (SECTION, WORDCLASS, ETC.)
        #self.positions = {}
        # If filename given, input the file
        if filename:
            if not os.path.isfile(filename):
                raise OSError(2, 'No such file', filename)
            # get terms from noun groups
            if filename.endswith('.tchunk'):
                parser = NPParser.NPParser()
                # expand abbreviations, stemming phrase endings, etc.
                #filters = ['abbreviation', 'isWord', 'case', 'stops', 'stem']
                filters = Settings.getDocumentFilters()
                self.counts = parser.getTerms(filename, filters,overwrite=overwrite)
                # get individual word counts -- for tokenized measures
                self.token_counts = FreqDist()
                for kw in list(self.counts.keys()):
                    words = kw.split()
                    for w in words:
                        self.token_counts[w] += 1
                # now to section data as raw text blocks
                #self.sections = Section.getSections(filename)
            elif filename.endswith('.substring'):
                self.token_counts = FreqDist()
                self.counts = FreqDist()
                with open(filename,encoding="utf-8-sig") as instream:
                    for term in instream:
                        term = term.strip(os.linesep)
                        self.counts[term] += 1
                        words = term.split()
                        for w in words:
                            self.token_counts[w] += 1
                    ## update counts for each term
                    ## update token_counts for each word in each term
                    ## -- Perhaps there is some over-representation
                    ##    for words in terms that are sub-terms?
        else:
            self.counts = FreqDist()
            self.token_counts = FreqDist()
            #self.sections = []
