import os, re

root = '/home/zg440/Documents'

def find_examples(words, text):
    #sents = text.split('.')
    sents = text.split('\n')
    examples = {}
    for i in range(len(words)):
        print i
        examples[words[i]] = []
        #pattern = re.compile('[^\n]{,50}'+words[i]+'[^\n]{,50}')
        #matches = re.finditer(pattern, text)
        #w = words[i]
        #for s in sents:
        #    if w in s:
        #        if w in examples:
        #            examples[w].append(s)
        #        else:
        #            examples[w] = [s]
        #
        #    examples[words[i]].extend(re.findall(pattern, text))
        #    if len(examples[words[i]]) > 3:
        #        break
        #
        #for i in range(3):
        #    try:
        #        temp = matches.next()
        #        examples[words[i]].append(temp.group())
        #    except:
        #        # no matches left
        #        break
        for s in sents:
            try:
                loc = s.lower().index(words[i])
                if loc > 0:
                    if s[loc-1] != ' ':
                        continue
                if loc < len(s)-1:
                    if s[loc+len(words[i])] != ' ':
                        continue
                init = max(0, loc-50)
                fin = loc + 50
                examples[words[i]].append(s[init:fin])
                if len(examples[words[i]]) > 2:
                    break
            except:
                # no match
                continue
    return examples

def save_examples(words, examples, filename):
    f = open(filename, 'w')
    #words = examples.keys()
    #words.sort()
    for i in range(len(words)):
        f.write(words[i] + ' | ' + 'false | Unknown |  | false')
        for s in examples[words[i]]:
            f.write(' | '+s)
        f.write('\n')
    f.close()

def get_text(folder):
    text = []
    filenames = [folder+f for f in os.listdir(folder) if f[-4:] == '.txt']
    for name in filenames:
        f = open(name)
        text.append(f.read())
        f.close()
    text = '\n'.join(text)
    return text

def run(ranking, infolder='../test/patents/US_out/full/', outfile='out/annotation2TokenDRDC.out', N=1000):
    #infolder = root+'/test/patents/US_out/full/'
    #outfile = root+'/ver2/out/annotation2TokenDRDC.out'
    print 'Getting words...'
    if type(ranking[0]) == type(()):
        words = map(lambda x: x[0], ranking[:N])
    else:
        words = ranking[:N]
    print 'done'
    print 'Getting text...'
    text = get_text(infolder)
    print 'done'
    print 'Getting examples...'
    examples = find_examples(words, text)
    print 'done'
    print 'Saving data...'
    save_examples(words, examples, outfile)
    print 'done'
