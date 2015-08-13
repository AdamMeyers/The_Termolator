import re, os

class Section:
    """Class containing section data from an input file"""
    def __init__(self, title, text):
        self.title = title
        self.text = text
def getSections(filename):
    """Input a filename, return a list of Section objects from the file"""
    if not os.path.exists(filename) or \
       not filename[-4:] == '.txt' or \
       not os.path.exists(filename[:-4]+'.fact'):
        raise OSError(2, 'Incorrect file format or no such (fact) file', filename)
    f = open(filename)
    fulltext = f.read()
    f.close()
    pattern = re.compile(r'.*DOC_SEGMENT ID.*TITLE=\"(.+?)\".*START=(\d+).*END=(\d+)')
    sections = []
    f = open(filename[:-4]+'.fact')
    for line in f:
        m = re.match(pattern, line)
        if m:
            (title, start, end) = m.groups()
            start = int(start)
            end = int(end)
            sec = Section(title, fulltext[start:end+1])
            sections.append(sec)
    return sections
