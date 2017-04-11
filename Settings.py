import json, os

dir_name = os.path.dirname(os.path.realpath(__file__)) + os.sep
default_file = dir_name + 'settings.txt'

def load(filename):
    """Load settings from a file."""
    if not os.path.isfile(filename):
        raise OSError(2, 'No such file', filename)
    f = open(filename)
    lines = f.read().split('\n')
    f.close()
    i = 0
    while i < len(lines):
        if lines[i] == '[Document Filters]':
            global document_filters
            document_filters = json.loads(lines[i+1])
            i += 2
        elif lines[i] == '[Corpus Filters]':
            global corpus_filters
            corpus_filters = json.loads(lines[i+1])
            i += 2
        elif lines[i] == '[Metric Weights]':
            global metric_weights
            metric_weights = json.loads(lines[i+1])
            i += 2
        else:
            i += 1

def getDocumentFilters(filename=default_file):
    """Return the Document class filtering settings as a list."""
    if not 'document_filters' in locals():
        load(filename)
    return document_filters

def getCorpusFilters(filename=default_file):
    """Return the Corpus class filtering settings as a list."""
    if not 'corpus_filters' in locals():
        load(filename)
    return corpus_filters

def getMetricWeights(filename=default_file):
    """Return the Metric class weights (for weighted measurement) as a list."""
    if not 'metric_weights' in locals():
        load(filename)
    return metric_weights
