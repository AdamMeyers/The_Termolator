import re

def load(filename):
    """Load a list of terms from a hand-tagged file."""
    pattern = re.compile(r'<JARGON.*text=\"(.*?)\".*/>')
    terms = []
    f = open(filename)
    for line in f:
        m = re.match(pattern, line)
        if m:
            terms.append(m.groups()[0])
            #print terms[-1]
    f.close()
    return set(terms)
