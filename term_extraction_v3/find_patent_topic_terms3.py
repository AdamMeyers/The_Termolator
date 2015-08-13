import sys, os, re
from nyu_utilities import *
from abbreviate4 import *
from add_citations3 import *
from get_morphological_and_abbreviation_variations import *

nom_file = DICT_DIRECTORY+'NOMLIST.dict'
person_name_file =  DICT_DIRECTORY+'person_name_list.dict'
skippable_adj_file = DICT_DIRECTORY+'out_adjectives.dict'
out_ing_file = DICT_DIRECTORY+'out_ing.dict'
nom_map_file = DICT_DIRECTORY+'nom_map.dict'
time_name_file = DICT_DIRECTORY+'time_names.dict'
nom_dict = {}
nom_map_dict = {}
stat_term_dict = {}
et_al_citation = re.compile(' et[.]? al[.]? *$')
lemma_dict = {}

closed_class_stop_words = ['a','the','an','and','or','but','about','above','after','along','amid','among',\
                           'as','at','by','for','from','in','into','like','minus','near','of','off','on',\
                           'onto','out','over','past','per','plus','since','till','to','under','until','up',\
                           'via','vs','with','that','can','cannot','could','may','might','must',\
                           'need','ought','shall','should','will','would','have','had','has','having','be',\
                           'is','am','are','was','were','being','been','get','gets','got','gotten',\
                           'getting','seem','seeming','seems','seemed',\
                           'enough', 'both', 'all', 'your' 'those', 'this', 'these', \
                           'their', 'the', 'that', 'some', 'our', 'no', 'neither', 'my',\
                           'its', 'his' 'her', 'every', 'either', 'each', 'any', 'another',\
                           'an', 'a', 'just', 'mere', 'such', 'merely' 'right', 'no', 'not',\
                           'only', 'sheer', 'even', 'especially', 'namely', 'as', 'more',\
                           'most', 'less' 'least', 'so', 'enough', 'too', 'pretty', 'quite',\
                           'rather', 'somewhat', 'sufficiently' 'same', 'different', 'such',\
                           'when', 'why', 'where', 'how', 'what', 'who', 'whom', 'which',\
                           'whether', 'why', 'whose', 'if', 'anybody', 'anyone', 'anyplace', \
                           'anything', 'anytime' 'anywhere', 'everybody', 'everyday',\
                           'everyone', 'everyplace', 'everything' 'everywhere', 'whatever',\
                           'whenever', 'whereever', 'whichever', 'whoever', 'whomever' 'he',\
                           'him', 'his', 'her', 'she', 'it', 'they', 'them', 'its', 'their','theirs',\
                           'you','your','yours','me','my','mine','I','we','us','much'                           
                           ]
                           ## ABBREVIATION_STOP_WORDS plus some

patent_stop_words = ['patent','provisional','kokai','open','publication','number','nos','serial',\
                     'related','claim','claims','embodiment','related','present','priority','design',\
                     'said','respective','fig','figs','copyright','following','preceding','according',\
                         'barring','pending','pertaining','International', 'et', 'al']
## 'application', 'dependent', 'european','japanese','chinese',
## "application" and "dependent" have technical non-patent uses -- removing both of them
##  I think this will be better than leaving them in


def read_in_nom_dict (infile=nom_file):
    global nom_dict
    for line in open(infile).readlines():
        nom_class,word = line.strip().split('\t')
        if word in nom_dict:
            nom_dict[word].append(nom_class)
        else:
            nom_dict[word] = [nom_class]

read_in_nom_dict()

def read_in_nom_map_dict (infile=nom_map_file):
    global nom_map_dict
    for line in open(infile).readlines():
        word,nominalization = line.strip().split('\t')
        nom_map_dict[word]=nominalization

read_in_nom_map_dict()

def update_pos_dict (name_infiles=[person_name_file],other_infiles=[skippable_adj_file,out_ing_file,time_name_file]):
    global pos_dict
    for infile in name_infiles:
         for line in open(infile).readlines():
            line = line.strip() 
            word,word_class = line.split('\t')
            word = word.lower()
            if word in pos_dict:
                pos_dict[word].append(word_class)
            else:
                pos_dict[word] = [word_class]
    for infile in other_infiles:
         for line in open(infile).readlines():
            line = line.strip()
            out_list = line.split('\t')
            word = out_list[0]
            word_class = out_list[1]
            if len(out_list)>2:
                flag = out_list[2]
            else:
                flag = False
            word = word.lower()
            if flag == 'ABSOLUTE':
                pos_dict[word] = [word_class]
            elif word in pos_dict:
                pos_dict[word].append(word_class)
            else:
                pos_dict[word] = [word_class]
    for word in patent_stop_words:
        pos_dict[word]=['OTHER']
        ## treat stop words as inadmissable parts of terms

update_pos_dict()

read_in_verb_morph_file()

stat_term_dict = {}
stat_adj_dict = {}

def topic_section_score(title):
   ## Field 3, Invention 2, Background 2, Endeavor 2, Technical 2, Summary 1
    field = re.compile('(^|[^a-z])fields?($|[^a-z])',re.I)
    technology = re.compile('(^|[^a-z])(technology|technical|endeavor|invention)($|[^a-z])',re.I)
    background = re.compile('(^|[^a-z])background($|[^a-z])',re.I)
    summary = re.compile('(^|[^a-z])summary($|[^a-z])',re.I)
    description = re.compile('(^|[^a-z])description($|[^a-z])',re.I)
    points = 0
    if field.search(title):
        points = points+4
    if background.search(title):
        points = points+3
    if summary.search(title):
        points = points+2
    if technology.search(title):
        points = points+1
    if description.search(title):
        points = points+1
    return(points)

def get_topic_terms_from_one_patent(fact_file,txt_file,outfile,pretty=True):
    relates_to_topic_pattern = re.compile('(^|[^a-z])(invention|disclosure|subject|topic|embodiment|application|present).{0,50}?[^a-z]((relat(e|ed|es|ing).{0,15}[^a-z]to)|concerns|concerned with) +([^ ].*?( e\.g\..*?)?)\.')
    is_topic_pattern = re.compile('(^|[^a-z])(invention|disclosure|subject|topic|embodiment|application) +(is|provides|regards|pertains +to) +(.*?( e\.g\..*?)?)\.')
    ## alternative is simply an abbreviated item in the first sentence of the paragraph
    ## of the section in question
    subtopic_pattern = re.compile('(^|[^a-z])((in particular)|(particularly)|(specifically))(,)? +((the|this) +(present +)?invention +)?(((relat(e|ed|es|ing))|(applicable)) +)?(to +)?([^ ].*?( e\.g\..*?)?)(\.|$)',re.I)
    ## ( e\.g\..*?)?
    subsection_pattern = re.compile('(^| +)1\. +((Technical +)?Field(.{0,15}of the Invention)?)(.*?)2\.',re.I) 
    ## field 5 is the section 
    possible_sections = []
    topic_section = False
    topic_text = False
    subtopic_text = False
    match_start = False
    match_end = False
    match = False
    match2 = False
    confidence_score = False
    confidence_score1 = False
    confidence_score2 = False
    with open(fact_file,'r') as fact_stream:
        for line in fact_stream:
            line_attributes = get_integrated_line_attribute_value_structure(line,['SECTION','PAPER'])
            if line_attributes:
                avtype = line_attributes['av_type']
                if avtype == 'PAPER':
                    patent_title = line_attributes['TITLE'][0]
                elif avtype == 'SECTION':
                    ## divide into subsections here
                    ## if there exist lines that just have
                    ##  1. blah blah blah -- short title like things
                    ##  2. blah blah blah
                    ## then these are numbered subsections with the thing after the number
                    ## as the title
                    section_title = line_attributes['TITLE'][0]
                    section_score = topic_section_score(section_title)
                    if section_score > 0:
                        start,end = line_attributes['START'][0],line_attributes['END'][0]
                        possible_sections.append([section_score,section_title,start,end])
    if len(possible_sections)>0:
        possible_sections.sort()
        offset = False
        ## print(possible_sections)
        with open(txt_file,'r') as instream:
            intext=instream.read()
            while ((len(possible_sections)>0) and not match):
                match = False
                section_text1 = False
                section_text2 = False
                ## print(possible_sections[-1])
                topic_section=possible_sections.pop()
                confidence_score1,sect1_start,sect1_end = topic_section[0],int(topic_section[2]),int(topic_section[3])
                confidence_score1 = min(confidence_score1,4)
                ## print(topic_section)
                section_text1 = intext[sect1_start:sect1_end].replace(os.linesep,' ')
                ## print(section_text1)
                subsection_match = subsection_pattern.search(section_text1)
                if subsection_match:
                    sect1_end = sect1_start+subsection_match.end(5)
                    sect1_start = sect1_start+subsection_match.start(5)
                    section_text1 = subsection_match.group(5)
                match = relates_to_topic_pattern.search(section_text1)
                if match:
                    confidence_score = confidence_score1+2
                    topic_text = match.group(6)
                    section_text = section_text1
                    match_start = match.start(6)
                    match_end = match.end(6)
                    offset = sect1_start
                else:
                    if len(possible_sections)>0:
                        topic_section2 = possible_sections.pop()
                        ## print(topic_section2)
                        confidence_score2,sect2_start,sect2_end = topic_section2[0],int(topic_section2[2]),int(topic_section2[3])
                        confidence_score2 = min(confidence_score2,4)
                        section_text2 = intext[sect2_start:sect2_end].replace(os.linesep,' ')
                        ## print(section_text2)
                        subsection_match = subsection_pattern.search(section_text2)
                        if subsection_match:
                            sect2_end = sect2_start+subsection_match.end(5)
                            sect2_start = sect2_start+subsection_match.start(5)
                            section_text2 = subsection_match.group(5)
                        match = relates_to_topic_pattern.search(section_text2)
                        ## print('relates 2')
                        if match:
                            confidence_score = confidence_score2+2
                            topic_text = match.group(6)
                            ## print(topic_text)
                            ## print(match.group(0))
                            section_text = section_text2
                            match_start = match.start(6)
                            match_end = match.end(6)
                            offset = sect2_start
                    if not match:
                        match = is_topic_pattern.search(section_text1)
                        if match:
                            confidence_score=confidence_score1
                            topic_text = match.group(4)
                            section_text = section_text1
                            match_start = match.start(4)
                            match_end = match.end(4)
                            offset = sect1_start
                        elif section_text2:
                            match = is_topic_pattern.search(section_text2)
                            if match:
                                ## print('match 2')
                                confidence_score=confidence_score2
                                topic_text = match.group(4)
                                section_text = section_text2
                                match_start = match.start(4)
                                match_end = match.end(4)
                                offset = sect2_start
        if topic_text:
            match2 = subtopic_pattern.search(section_text,match_start)
            if match2 and (match2.start() < match.end()):
                if match2.start()<match_end:
                    match_end = match2.start()
                    topic_text = section_text[match_start:match_end]
            else:
                match2 = subtopic_pattern.search(section_text,match.end())
            if match2:
                subtopic_text = match2.group(16)
                subtopic_start = match2.start(16)
                subtopic_end = match2.end()
            if confidence_score >=4:
                confidence = 'High'
            elif confidence_score >=2:
                confidence = 'Medium'
            else:
                confidence = 'Low'
            with open(outfile,'w') as outstream:
                outstream.write('Topic START='+str(match_start+offset)+' END='+str(match_end+offset)+' CONFIDENCE="'+confidence+'"')
                ## outstream.write('Topic START='+str(match_start+offset)+' END='+str(match_end+offset))
                if pretty:
                    outstream.write(' STRING="'+topic_text+'"')
                outstream.write(os.linesep)
                if subtopic_text:
                    outstream.write('Subtopic START='+str(subtopic_start+offset)+' END='+str(subtopic_end+offset)+' CONFIDENCE="'+confidence+'"')
                    ## outstream.write('Subtopic START='+str(subtopic_start+offset)+' END='+str(subtopic_end+offset))
                    if pretty:
                        outstream.write(' STRING="'+subtopic_text+'"')
                    outstream.write(os.linesep)

def get_topics_for_file_list(infile_list,outfile_list,pretty=True):
    with open(infile_list) as infile_list_stream, open(outfile_list) as outfile_list_stream:
        inlist = infile_list_stream.readlines()
        outlist = outfile_list_stream.readlines()
        if len(inlist) != len(outlist):
            print("Lists of input and output files should be of same length.")
            sys.exit(-1)
        for i in range(len(inlist)):
            try:
                txt_file,fact_file = inlist[i].strip().split(';')
                out_file = outlist[i].strip()
                print(txt_file)
            except:
                print("Error opening input/output files:")
                print("Input: %s\nOutput: %s" % (inlist[i].strip(),outlist[i].strip()))
            get_topic_terms_from_one_patent(fact_file,txt_file,out_file,pretty=pretty)

def closed_class_confict(word):
    if word in closed_class_stop_words:
        return(True)
    elif (word in noun_base_form_dict):
        for base in(noun_base_form_dict[word]):
            if base in closed_class_stop_words:
                return(True)

def technical_adj (word):
    technical_pattern = re.compile('(ic|[c-x]al|ous|[ao]ry|[coup]id|lar|ine|ian|rse|iac|ive)$')
    ## matches adjectives with certain endings
    return(technical_pattern.search(word))

def id_number_profile (word):
    digits = len(re.sub('[^0-9]','',word))
    alpha = len(re.sub('[0-9]','',word))
    if (digits > 0) and (alpha>0):
        return(True)

def verbal_profile(word):
    if (len(word)>5) and re.search('[aeiou][b-df-hj-np-ts-z]ed$',word):
        return(True)        

def resolve_differences_with_pos_tagger(word,offset,dict_pos,tagger_pos):
    if (tagger_pos == 'ADJECTIVE') and ('ORDINAL' in dict_pos):
        return(['ORDINAL'])
    elif (tagger_pos == 'ADJECTIVE') and ('SKIPABLE_ADJ' in dict_pos):
        return(['SKIPABLE_ADJ'])
    elif (tagger_pos in ['ADJECTIVE','NOUN']) and \
         (word.endswith('ing') or word.endswith('ed')):
        return([tagger_pos])
    elif tagger_pos in dict_pos:
        return([tagger_pos])
    elif (tagger_pos == 'OTHER'):
        if ('AUX' in dict_pos) or ('WORD' in dict_pos) or \
          ('CCONJ' in dict_pos) or ('PRONOUN' in dict_pos) or \
          ('TITLE' in dict_pos) or ('SCONJ' in dict_pos) or \
          ('ADVERB' in dict_pos):
            return(['WORD'])
        else:
            ## print('Ignoring',tagger_pos,'in light of',dict_pos)
            ## print('Word =',word,'Offset=',offset)
            ## input('')
            return(dict_pos)
    elif (tagger_pos == 'NOUN') and ('NOUN_OOV' in dict_pos):
        return (['NOUN_OOV'])
    else:
        return(dict_pos)

def citation_number(word):
    ## derived from add_citations3.py
    ## There may still be clashes with standard
    patent_number = r'((A-Z)*([0-9,/-]{4,})(A-Z)*)|([0-9][0-9]+( [0-9][0-9]+)+((([.-][0-9]+)| [A-Z][0-9]+)?)+)|([0-9][0-9]/[0-9]{3},[0-9]{3})|(PCT/[A-Z]{2}[0-9]{2,4}/[0-9]{5,})'
    german_patent = r'DE(-OS)? [0-9][0-9]+( [0-9][0-9]+)+(([.][0-9]+)| [A-Z][0-9]+)?'
    pct_patent = r'(PCT/[A-Z]{2}[0-9]{,4}/[0-9]{5,})'
    isbn = r'ISBN[:]? *([0-9][ -][0-9]{3}[ -][0-9]{2}[ -][0-9]{3}[ -][0-9X])'
    ## these focus on citation IDs that are number+letter combos
    citation_number_match = re.compile('((((U[.]?S[.]?)? *)?('+patent_number+'))|('+german_patent+')|('+pct_patent+')|('+isbn+'))')
    if citation_number_match.search(word):
        return(True)
    else:
        return(False)


def guess_pos(word,is_capital,offset=False):
    ## print(word,offset)
    pos = []
    plural = False
    if offset and (offset in pos_offset_table):
        tagger_pos = pos_offset_table[offset]            
        ## Most conservative move is to use for disambiguation,
        ## and for identifying ing nouns (whether NNP or NN)
        ## We care about: 
        ## Easy translations: NN NNP NNPS NNS; JJ JJR JJS; RB RBR RBS RP WRB;
        ## 'FW' 'SYM' '-LRB-''-RRB-'; VBD VBG VBN VBP VBZ VB; DT PDT WDT PRP$ WP$
        ## CC CD EX FW LS MD POS PRP UH WP 
        if tagger_pos in ['NNP','NNPS','FW','SYM','-LRB-','-RRB-']:
            ## these are inaccurate for this corpus or irrelevant for this task
            ## NNP and NNPS are not very accurate, FW identifies some conventionalized abbreviations (et. al. and i.e.)
            ##     and latin terms (per se).  SYM cases are eliminated in other ways
            ## Punctuation cases are already ignored
            tagger_pos = False
        elif tagger_pos == 'NN':
            tagger_pos = 'NOUN'
        elif tagger_pos == 'NNS':
            tagger_pos = 'PLURAL'
        elif tagger_pos in ['TO','IN']:
            tagger_pos = 'PREP'
        elif tagger_pos in ['RB','RBR','RBS','RP','WRB']:
            tagger_pos = 'ADVERB'
        elif tagger_pos in ['JJ','JJR','JJS']:
            tagger_pos = 'ADJECTIVE'
        elif tagger_pos in ['VBD', 'VBG', 'VBN', 'VBP', 'VBZ','VB']:
            tagger_pos = 'VERB'
        elif tagger_pos in ['DT','PDT','WDT','PRP$','WP$','CD']:
            tagger_pos = 'DET'
        else:
            tagger_pos = 'OTHER'
    else:
        tagger_pos = False
    if (len(word)> 2) and word[-2:] in ['\'s','s\'']:
        possessive = True
        word = word[:-2]
    else:
        possessive = False
    if (len(word)==1) and not word.isalnum():
        return('OTHER')
    if word in pos_dict:
        pos = pos_dict[word][:]
        if not possessive:
            ## print(1,pos,tagger_pos)
            pos = resolve_differences_with_pos_tagger(word,offset,pos,tagger_pos)
            ## print(2,pos,tagger_pos)
        if ('PERSON_NAME' in pos) and (not is_capital):
            pos.remove('PERSON_NAME')
            if len(pos) == 0:
                pos.append('NOUN_OOV')
        ## initially set pos based on dictionary
        if (word in nom_dict) and ('NOM' in nom_dict[word]):
            is_nom = True
        else:
            is_nom = False
        if (len(pos)>1):
            if 'PREP' in pos:
                return('PREP')
            elif ('DET' in pos) or ('QUANT' in pos) or ('CARDINAL' in pos):
                return('DET')
            elif ('ADVERB' in pos) and not is_nom:
                return('ADVERB')
            elif ('AUX' in pos) or ('WORD' in pos) or \
               ('CCONJ' in pos) or ('PRONOUN' in pos) or \
               ('TITLE' in pos) or ('SCONJ' in pos):
                return('OTHER')
            elif (('SKIPABLE_ADJ' in pos) or ('ORDINAL' in pos)) and (not word.lower() in stat_adj_dict):
                return('SKIPABLE_ADJ')
            elif (('NOUN' in pos) or ('NOUN_OOV' in pos)) and not closed_class_confict(word):
                if possessive:
                    return('AMBIG_POSSESS')
                elif (len(word)>1) and (word[-1] == 's') and (word in noun_base_form_dict) and (not (word in noun_base_form_dict[word])):
                    return('AMBIG_PLURAL')
                else:
                    return('AMBIG_NOUN')
            elif 'VERB' in pos:
                return('AMBIG_VERB')
            # elif 'SKIPABLE_ADJ' in pos:
            #     return('SKIPABLE_ADJ')
            elif 'ADJECTIVE' in pos:
                ## print(word)
                if technical_adj(word):
                    return('TECH_ADJECTIVE')
                else:
                    return('ADJECTIVE')
            else:        
                return('OTHER')
        elif len(pos)==1:
            if (('NOUN' in pos) or ('NOUN_OOV' in pos)):
                if possessive:
                    return('POSSESS')
                elif (len(word)>1) and (word[-1] == 's') and (word in noun_base_form_dict) and (not (word in noun_base_form_dict[word])):
                    return('PLURAL')
                ## plurals are nouns ending in 's' and that are not base forms
                elif 'NOUN_OOV' in pos:
                    return('NOUN_OOV')
                else:
                    return('NOUN')
            elif ('PERSON_NAME' in pos):
                if possessive:
                    return('POSSESS')
                else:
                    return('PERSON_NAME')
            elif 'VERB' in pos:
                return('VERB')
            elif 'DET' in pos:
                return('DET')
            elif 'PREP' in pos:
                return('PREP')
            elif (('SKIPABLE_ADJ' in pos) or ('ORDINAL' in pos)) and not (word.lower() in stat_adj_dict):
                return('SKIPABLE_ADJ')
            elif 'ADJECTIVE' in pos:
                if technical_adj(word):
                    return('TECH_ADJECTIVE')
                else:
                    return('ADJECTIVE')
            elif 'PERSON_NAME' in pos:
                return('PERSON_NAME')
            else:
                return('OTHER')
    elif (not possessive) and ('-' in word) and re.search('[a-zA-Z]',word):
        little_words = word.split('-')
        ## print(1,little_words)
        if len(little_words)>2:
            for word in little_words:
                little_pos = guess_pos(word,word.istitle())
                if little_pos == 'NOUN_OOV':
                    return('NOUN_OOV')
            return('NOUN')
        if len(little_words)==1 and (little_words[0].isalnum()):
            return(guess_pos(little_words[0]),is_capital)
        if little_words[1] in pos_dict: ## the last word
            ## print(1,little_words)
            last_pos = pos_dict[little_words[1]][:]
            first_pos = guess_pos(little_words[0],little_words[0].istitle())
            first_word = little_words[0].lower()
            if first_pos == 'NOUN_OOV':
                return('NOUN_OOV')
            if 'ADVPART' in last_pos:
                return('SKIPABLE_ADJ')
            if 'NOUN' in last_pos:
                ## print('hi')
                if (len(word)>2) and (word[-1] == 's') and (not word[-2] in "aiousc"):
                    return('PLURAL')
                else:
                    return('NOUN')
            elif 'PERSON_NAME' in last_pos:
                return('NOUN')
            elif 'SKIPABLE_ADJ' in pos:
                if word.lower() in stat_adj_dict:
                    if technical_adj(word):
                        return('TECH_ADJECTIVE')
                    else:
                        return('ADJECTIVE')
                else:
                    return('SKIPABLE_ADJ')
            elif 'ADJECTIVE' in last_pos:
                if technical_adj(word):
                    return('TECH_ADJECTIVE')
                elif (first_pos == 'NOUN') and ((not first_word in pos_dict) or (nom_class(first_word,first_pos)>1)):
                    return('TECH_ADJECTIVE')
                else:
                    return('ADJECTIVE')
            elif 'VERB' in last_pos:
                if word.endswith('ed') or word.endswith('ing'):
                    if  (first_pos == 'NOUN') and ((not first_word in pos_dict) or (nom_class(first_word,first_pos)>1)):
                        return('TECH_ADJECTIVE')
                    else:
                        return('ADJECTIVE')
##                elif 'CARDINAL' in last_pos:
##                    return('ADJECTIVE')
                elif 'NOUN' in last_pos:
                    return('NOUN')
##                else:
##                    return('VERB')
                else:
                    return('ADJECTIVE')
            else:
                return('OTHER')
        elif (len(word)>2) and (word[-1] == 's') and (not word[-2] in "aiousc"):
            return('PLURAL')
        else:
            return('NOUN')
    elif (len(word)>4) and (word[-2:] == 'ly'):
        ## length requirement will get rid of most enumerations in parens
        return('ADVERB')
    elif possessive and re.search('^[0-9]+$',word[:-2]):
        ## possessive number
        return('OTHER')
    elif possessive:
        return('POSSESS_OOV')
    elif (id_number_profile(word)):
        if citation_number(word):
            return('OTHER')
        else:
            return('NOUN_OOV')
    elif re.search('^[0-9\-.\/]+$',word):
        ## here an id_number is any combination of numbers and letters
        ## this may need to be modified to differentiate patent numbers from chemical/virus/etc. names
        ## the second term describes a number consisting of a combination of digits, periods and fractional slashes
        return('OTHER')
    elif verbal_profile(word):
        ## return('VERB')
        ## long word ending in 'ed'
        return('TECHNICAL_ADJECTIVE')
    elif (len(word)>2) and (word[-1] == 's') and (not word[-2] in "aiousc"):
        return('PLURAL')
        ## assume out-of-vocabulary (OOV) words ending in 's' can be nouns, given the right circumstances
    elif roman(word):
        return('ROMAN_NUMBER')
    else:
        return('NOUN_OOV')
        ## otherwise assume most OOV words are nouns

def stringify_word_list(word_list):
    output = word_list[0]
    if len(word_list)>1:
        for word in word_list[1:]:
            output=output+' '+word
    return(output)

def nom_class(word,pos):
    if word in ['invention','inventions']:
        return(0)
    ## invention is usually a self-citation and we want to downgrade its score
    elif word in nom_dict:
        rank = 0
        for feature in nom_dict[word]:
            if feature in ['NOM', 'NOMLIKE', 'ABLE-NOM']:
                ## 'NOMADJ', 'NOMADJLIKE'
                ## secondary: ability, attribute, type, group
                ## question NOMADJ and NOMADJLIKE
                if rank < 2:
                    rank = 2
            elif feature in ['ABILITY','ATTRIBUTE','TYPE','GROUP']:
                if rank < 1:
                    rank = 1
        return(rank) ## return highest possible rank
    elif (pos in ['VERB','AMBIG_VERB']) and (len(word)>5) and (word[-3:]=='ing'):
        return(1)
    else:
        return(0)

def ugly_word(word):
    ## words that are probably typos
    if (len(word)>3) and (word[0] in "0123456789") and word[-1].isalpha():
        return(True)
    elif (len(word)>1) and (word[0] in "`~!@#$%^&*-_+=<>,.?/\\"):
        return(True)
    elif not re.search('[a-z]',word):
        return(True)

def section_heading_word(word):
    ## print(word)
    if (len(word)>1) and (word[-1]=='s'):
        if (word in ['descriptions','claims','embodiments', 'examples','fields','inventions','priorities','applications']):
            return(True)
    elif word in ['description', 'summary', 'claim', 'embodiment', 'example', 'explanation', 'field', 'invention', 'introduction', 'priority', 'application(s)', 'statement', 'reference']:
        return(True)

def topic_term_ok(word_list,pos_list,term_string):
##    print(word_list)
##    print(pos_list)
##    print([term_string])
    if len(term_string) == 1:
        return(False)
    elif term_string.lower() in stat_term_dict:
        ## print('stat')
        return(True)
    OOV_count = 0
    signif_term = 0
    nominalization_count = 0
    nom_length = 0
    non_final_common_noun = 0
    has_section_heading_word = False
    ##final_position = len(word_list)-1
    alpha = False
    has_lower = False
    has_upper = False
    if pos_list[-1]=='PERSON_NAME':
        return(False)
    if (len(word_list)==1) and (len(word_list[0])==1):
        return(False)
    for num in range(len(word_list)):
        if word_list[num].isupper():
            has_upper = True
        elif re.search('[a-z]',word_list[num]):
            ## true for capcase or all lower
            has_lower = True
        common = False
        oov = False
        lower = word_list[num].lower()
        ugly = False
        if word_list[num].isupper():
            allcaps = True
        else:
            allcaps = False
        if lower in stat_term_dict:
            signif_term = signif_term + 1
        if (not alpha) and re.search('[a-zA-Z]',lower):
            alpha = True
        if lower in pos_dict:
            if ('NOUN' in pos_dict[lower])and (len(lower)<8):
                common = True
            if 'NOUN_OOV' == pos_list[num]:
                oov = True
                OOV_count = 1 + OOV_count
            if lower in noun_base_form_dict:
                base = noun_base_form_dict[lower][0]
            else:
                base = lower
        elif ugly_word(lower):
            ugly = True
        elif 'NOUN' in pos_list:  ## some OOV words are not classified as noun
            base = lower
            oov = True
            OOV_count = 1 + OOV_count
            ## it does not matter for our purposes if an OOV is plural or singular here
        else:
            base = lower
        if ugly or oov:
            nom_rank = 0
        elif allcaps and section_heading_word(lower):
            nom_rank = 0
            has_section_heading_word = True
        elif pos_list[num] in ['PLURAL','AMBIG_PLURAL']:
            nom_rank = nom_class(base,pos_list[num]) ## 2 (for real nom), 1 (for other nom class), 0 for no nom class
        else:
            nom_rank = nom_class(lower,pos_list[num])
        ## print('rank',nom_rank,lower,'common',common,'oov',oov)
        if (nom_rank>0) or  (pos_list[num]=='TECH_ADJECTIVE'):
            nominalization_count = 1 + nominalization_count
        elif (not oov) and common and (num==0) or (lower in ['invention','inventions']):
            non_final_common_noun = non_final_common_noun+1
        if nom_rank >= 2:
            ## only record length if real nominalization (not other nom class)
            if lower.endswith('ing'):
                length = len(lower)-3
            else:
                length = len(lower)
            if length > nom_length:
                nom_length = length
        ## print('OOV',OOV_count,'NOM',nominalization_count,'comon_result',non_final_common_noun)
        ## print('nom_rank',nom_rank,'common',common,num)
    ## print(signif_term,alpha,OOV_count,nom_length,nominalization_count)
    if signif_term>0:
        return(True)
    if not alpha:
        return(False)
    if has_upper and (not has_lower) and has_section_heading_word:
        return(False)
    if (OOV_count >= 1) or ((nominalization_count >=3) and (len(word_list)>=4)):
        return(True)
    if non_final_common_noun>0:
        return(False)
    elif (nom_length>11):
        return(True)
    elif (len(word_list)>1) and (nominalization_count >= 1):
        return(True)
    else:
        return(False)

def is_nom_piece(word):
    lower = word.lower()
    if lower in ['invention','inventions']:
        return(False)
    if (lower in noun_base_form_dict) and (lower[-1]=='s'):
        base = noun_base_form_dict[lower][0]
    else:
        base = lower
    nom_rank = nom_class(base,'NOUN')
    if nom_rank >= 2:
        return(True)
    else:
        return(False)
        
def get_topic_terms(text):
    ## print(text)
    ## single_quote_pattern=re.compile('[\`\'‘](?!(s |d | |t |ll |m |ve |re ))([^\`\']*)[\'’](?!(s |d |t |ll |m |ve |re ))')
    single_quote_pattern=re.compile('[\`\'‘](?!(s[^a-z]|d[^a-z]| |t[^a-z]|ll[^a-z]|m[^a-z]|ve[^a-z]|re[^a-z]))([^\`\']*?)[\'’](?!(s[^a-z]|d[^a-z]|t[^a-z]|ll[^a-z]|m[^a-z]|ve[^a-z]|re[^a-z]))')
    ## '...', where ' is not followed by a contraction or possessive marker (the first one cannot be followed by a space either,
    ## since this would make it a second quote or a plural possessive marker -- note this procludes an apostrophe inside a single quote
    double_quote_pattern=re.compile('["“]([^"“”]*?)["”]')
    splitters=re.compile('\.|,|;|:|/| and | or | as well as | along with | in addition to ',re.I)
    start = 0
    paren_pat = parentheses_pattern2.search(text,start)
    pieces = []
    topic_terms = []
    extend_antecedent = False
    last_start = False
    pre_np = False
    ## Part 1: based on get_next_abbreviation_relations
    ## it servers two purposes: (a) it breaks up the text by the round and square parentheses (reliable units); (b) it identifies
    ## abbreviations and their antecedents as terms
    while (paren_pat):
        result = False
        Fail = False
        first_word_break=re.search('[ ,;:]',paren_pat.group(1))
        if first_word_break:
                abbreviation=paren_pat.group(1)[:first_word_break.start()]
        else:
            abbreviation=paren_pat.group(1)
        search_end = paren_pat.start()
        search_end,Fail = find_search_end(text,search_end)
        if ill_formed_abbreviation_pattern(paren_pat) or re.search('^[a-zA-Z]$',abbreviation):
            Fail = True
        else:
            previous_words = remove_empties(word_split_pattern.split(text[start:search_end].rstrip(' ')))
        if not Fail:
            result = abbreviation_match(abbreviation,previous_words,text,search_end,0,False,False)
        if result and (result[3] == 'JARGON'):
            topic_terms.extend([result[2],abbreviation])
            pieces.append(text[start:paren_pat.start()])
        else:
            pieces.extend([text[start:paren_pat.start()],paren_pat.group(1)])
        start = paren_pat.end()
        paren_pat = parentheses_pattern2.search(text,start)
    if start and (len(text) > start):
        pieces.append(text[start:])
    if len(pieces)==0:
        pieces=[text]
    ## print(pieces)
    pieces2 = []
    ## Part 2: quotation mark off reliable units, separate these out
    ## print(1)
    for piece in pieces:
        start = 0
        ## print(piece)
        sing = single_quote_pattern.search(piece,start)
        doub = double_quote_pattern.search(piece,start)
        while (start < len(piece)) and (sing or doub):
            if doub and ((not sing) or ((sing.start() < doub.start()) and (sing.end()>doub.end()))):
                ## if doub nested inside of singular, assume singular quotes are in error
                pieces2.extend([piece[start:doub.start()],doub.group(1)])
                start = doub.end()
                doub = double_quote_pattern.search(piece,start)
                if sing:
                    sing = single_quote_pattern.search(piece,start)
            elif (not doub) or (sing.end() < doub.start()):
                ## if there is no doub or if sing completely precedes doub
                pieces2.extend([piece[start:sing.start()],sing.group(2)])
                start = sing.end() 
                sing = single_quote_pattern.search(piece,start)             
            elif (sing.start()>doub.start()) and (sing.end() < doub.end()):
                ## nesting sing inside doub
                pieces2.extend([piece[start:doub.start()],piece[doub.start(1):sing.start()],sing.group(2),piece[sing.end():doub.end(1)]])
                start = doub.end()
                doub = double_quote_pattern.search(piece,start)
            elif doub.end() < sing.start():                
                ## doub first -- do doub only  (treat similarly to first case, except don't reinitialize singular)
                pieces2.extend([piece[start:doub.start()],doub.group(1)])
                start = doub.end()
                doub = double_quote_pattern.search(piece,start)
                ## otherwise it is some sort of error
            elif doub and sing:
                if doub.start()<sing.start():
                    start = doub.start()+1
                    doub = double_quote_pattern.search(piece,start)
                else:
                    start = sing.start()+1
                    sing = single_quote_pattern.search(piece,start) 
            elif doub:
                start = doub.start()+1
                doub = double_quote_pattern.search(piece,start)
            elif sing:
                start = sing.start()+1
                sing = single_quote_pattern.search(piece,start) 
            else:
                print('Error in program regarding single and double quotes')
                print('piece:',piece)
                print('text:',text)
                ## this is probably not a real instance of quotation
        if start < len(piece):
            pieces2.append(piece[start:])
    ## Part III: split into chunks by commas and abbreviations
    ## each resulting piece an then be analyzed syntactically based on word class
    ## print(2)
    for piece in pieces2:
        ## parse each piece separately
        ## current_out_list = False
        ## print(piece)
        for piece2 in splitters.split(piece):
            piece2 = piece2.strip(''' ,.?><'";:][{}-_=)(*&^%$#@!~''')
            ## print(piece2)
            current_out_list = False
            current_pos_list = False
            pre_np = False
            first_piece = True
            last_pos = False
            all_pieces = piece2.split()
            for piece_num in range(len(all_pieces)):
                piece3 = all_pieces[piece_num]
                if piece3.istitle():
                    is_capital = True
                else:
                    is_capital = False
                lower = piece3.lower()
                ## print(lower)
                if piece3 == '':
                    pass
                else:
                    pos = guess_pos(lower,is_capital)
                    ## print(pos,lower,pre_np)
                    if (pos in ['SKIPABLE_ADJ']) and not(current_out_list):
                        pass
                    elif pos in ['DET','PREP']:
                        pre_np = True
                        if current_out_list:
                            term_string = stringify_word_list(current_out_list)
                        if current_out_list and topic_term_ok(current_out_list,current_pos_list,term_string):
                            topic_terms.append(term_string)
                        current_out_list = False
                        current_pos_list = False
                    elif pos in ['AMBIG_POSSESS','POSSESS']:
                        piece3 = piece3[:-2]
                        if current_out_list:
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                        else:
                            current_out_list = [piece3]
                            current_pos_list = [pos]
                        if current_out_list:
                            term_string = stringify_word_list(current_out_list)
                        else:
                            term_string = False
                        if topic_term_ok(current_out_list,current_pos_list,term_string):
                            topic_terms.append(stringify_word_list(term_string))
                        current_out_list = False
                        current_pos_list = False
                        pre_np = False
                        first_piece=False
                    elif (pos == 'PLURAL') or (current_out_list and (len(current_out_list)>=1) and \
                                               ((pos in ['AMBIG_PLURAL']) or \
                                                    ((current_pos_list[-1] == 'ADJECTIVE') and \
                                                         (pos == 'VERB') and (len(piece3)>3) and \
                                                     (piece3[-3:]=='ing')))):
                        ## a) plural nouns must end noun groups
                        ## b) ing verbs can sometimes also end noun groups
                        ## c) AMBIG_PLURALS, AMBIG_SINGULARs and ing verbs cannot stand by themselves and 
                        ## they can not be initial in noun groups
                        ## d) there is an exception -- if the next word is a nominalization,
                        ##    then the NP could continue
                        if current_out_list:
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                        else:
                            current_out_list = [piece3]
                            current_pos_list = [pos]
                        if  (piece_num<(len(all_pieces)-1)) and is_nom_piece(all_pieces[piece_num+1]):
                            ## look ahead to see if next word is a nominalization
                            pass
                        else:
                            if current_out_list:
                                term_string = stringify_word_list(current_out_list)
                            else:
                                term_string = False
                            if topic_term_ok(current_out_list,current_pos_list,term_string):
                                topic_terms.append(term_string)
                            current_out_list = False
                            current_pos_list = False
                        pre_np = False
                        first_piece=False
                    elif pos in ['NOUN','POSSESS_OOV','AMBIG_NOUN','PERSON_NAME']:
                        ## out of vocab possessive
                    ## evaluate piece by POS
                    ## looking for sequences of pieces that either: a) are unambigous nouns; or b) are OOV words
                        if current_out_list:
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                        else:
                            current_out_list = [piece3]
                            current_pos_list = [pos]
                        pre_np = False
                        first_piece=False
                    elif (current_out_list == False) and (pre_np or first_piece) and \
                         ((pos == 'TECH_ADJECTIVE') or \
                              ((pos =='ADJECTIVE') and (piece3 in stat_adj_dict)) or \
                              ((pos in ['VERB','AMBIG_VERB']) and (lower.endswith('ed') or lower.endswith('ing')))):
                        current_out_list = [piece3]
                        current_pos_list = [pos]
                        pre_np = False
                        first_piece=False                                    
                    elif (pre_np or first_piece or (last_pos in ['VERB','AMBIG_VERB']))  and (current_out_list == False) and \
                            (((pos in ['VERB','AMBIG_VERB']) and (lower.endswith('ed') or lower.endswith('ing'))) or \
                                 (pos in ['TECH_ADJECTIVE']) or \
                                 ((pos =='ADJECTIVE') and (piece3 in stat_adj_dict))):
                        ## considering allowing -ing verbs also, but this causes problems
                        current_out_list = [piece3]
                        current_pos_list = [pos]
                        pre_np = False
                        first_piece=False
                    else:
                        if current_out_list:
                            term_string = stringify_word_list(current_out_list)
                        else:
                            term_string = False
                        if current_out_list and topic_term_ok(current_out_list,current_pos_list,term_string):
                            topic_terms.append(term_string)
                        current_out_list = False
                        current_pos_list = False
                        pre_np = False
                        first_piece=False
                    last_pos = pos
            if current_out_list:
                term_string=stringify_word_list(current_out_list)
                if topic_term_ok(current_out_list,current_pos_list,term_string):
                    topic_terms.append(term_string)
    return(topic_terms)

def get_next_word(instring,start):
    word_pattern = re.compile('\w+')
    punctuation_pattern = re.compile('\S')
    found = word_pattern.search(instring,start)
    non_white_space = punctuation_pattern.search(instring,start)
    if non_white_space and found and (non_white_space.start()<found.start()):
        found = non_white_space
    if found:
        start = found.start()
        ## initialize start to first word character
    end = False
    while found:
        border = found.end()
##        print(instring)
##        print(found.group(0))
##        print(border)
##        print(instring[border])
        if (border >= len(instring)):
            end = found.end()
            found = False
        elif instring[border]=="'":
            next_word = word_pattern.search(instring,found.end())
            if next_word and (border+1==next_word.start()) and next_word.group(0) in ['s','t']:
                end = next_word.end()
            else:
                end = found.end()
            found = False
        elif (instring[border]=='*'):
            end = border+1
            found = False
        elif (instring[border]=="/"):
            next_word = word_pattern.search(instring,found.end())
            first_word = found.group(0)
            ## print(next_word.group(0))
            if next_word:
                second_word = next_word.group(0)
            if next_word and (border+1==next_word.start()) and (len(first_word)>0) and (len(second_word)>0) and first_word.isalpha() and second_word.isalpha():
                end = next_word.end()
                found = next_word
            else:
                end = found.end()
                found = False
            ## This will not correctly identify paths (file paths, html paths, some bio names, etc.)
        elif instring[border]=="-":
            next_word = word_pattern.search(instring,found.end())
            if next_word and(border+1==next_word.start()) and (((found.group(0).isalpha() and \
                                ((len(found.group(0))==1) or found.group(0).isalpha()))) or \
               ((len(next_word.group(0))>3)and ((next_word.group(0)[-2:]=="ed") or (next_word.group(0)[-3:]=='ing')))):
                end = next_word.end()
                found = next_word
            else:
                end=found.end()
                found = False
        else:
            end = found.end()
            found = False
        ## print(instring[start:end],start,end)
        ## print(found.group(0))
        ## input('?')
    if end:
        return(instring[start:end],start,end)
    else:
        return(False,False,False)
        
def get_topic_terms2(text,offset):
    ## print(offset,text)
    ## single_quote_pattern=re.compile('[\`\'‘](?!(s |d | |t |ll |m |ve |re ))([^\`\']*)[\'’](?!(s |d |t |ll |m |ve |re ))')
    single_quote_pattern=re.compile('[\`\'‘](?!(s[^a-z]|d[^a-z]| |t[^a-z]|ll[^a-z]|m[^a-z]|ve[^a-z]|re[^a-z]))([^\`\']*?)[\'’](?!(s[^a-z]|d[^a-z]|t[^a-z]|ll[^a-z]|m[^a-z]|ve[^a-z]|re[^a-z]))')
    ## '...', where ' is not followed by a contraction or possessive marker (the first one cannot be followed by a space either,
    ## since this would make it a second quote or a plural possessive marker -- note this procludes an apostrophe inside a single quote
    double_quote_pattern=re.compile('["“]([^"“”]*?)["”]')
    splitters=re.compile('\.|,|;|:| and | or | as well as | along with | in addition to |'+os.linesep,re.I)
    first_character_pattern=re.compile('[^ ,\.?><\'";:\]\[{}\-_=)(*&\^%$\#@!~]')
    start = 0
    paren_pat = parentheses_pattern2.search(text,start)
    pieces = []
    topic_terms = []
    extend_antecedent = False
    last_start = False
    pre_np = False
    ## Part 1: based on get_next_abbreviation_relations
    ## it servers two purposes: (a) it breaks up the text by the round and square parentheses (reliable units); (b) it identifies
    ## abbreviations and their antecedents as terms
    while (paren_pat):
        result = False
        Fail = False
        first_word_break=re.search('[ ,;:]',paren_pat.group(1))
        if first_word_break:
                abbreviation=paren_pat.group(1)[:first_word_break.start()]
        else:
            abbreviation=paren_pat.group(1)
        search_end = paren_pat.start()
        search_end,Fail = find_search_end(text,search_end)
        if ill_formed_abbreviation_pattern(paren_pat) or re.search('^[a-zA-Z]$',abbreviation):
            Fail = True
        else:
            previous_words = remove_empties(word_split_pattern.split(text[start:search_end].rstrip(' ')))
        if not Fail:
            result = abbreviation_match(abbreviation,previous_words,text,search_end,offset,False,False)
        if result and (result[3] == 'JARGON'):
            # print('pps',paren_pat.start(),'se',search_end,'s',start)
            # print('r',result)
            # print('off',offset,'paren_start',paren_pat.start()+2+start)
            # print('abbrev',abbreviation)
            # input()
            ARG1_start = result[0]
            ARG1_end = result[1]
            if result[4]:
                ARG2_start = paren_pat.start()+2+offset
                ARG2_end = ARG2_start+len(abbreviation)-1
                topic_terms.extend([[ARG1_start,ARG1_end,result[2]],[ARG2_start,ARG2_end,abbreviation[1:]]])
            else:
                ARG2_start = paren_pat.start()+1+offset
                ARG2_end = ARG2_start+len(abbreviation)
                topic_terms.extend([[ARG1_start,ARG1_end,result[2]],[ARG2_start,ARG2_end,abbreviation]])
            pieces.append([start,text[start:paren_pat.start()]])
        else:
            pieces.extend([[start,text[start:paren_pat.start()]],[paren_pat.start(1),paren_pat.group(1)]])
        start = paren_pat.end()
        paren_pat = parentheses_pattern2.search(text,start)
    if start and (len(text) > start):
        pieces.append([start,text[start:]])
    if len(pieces)==0:
        pieces=[[0,text]]
    ## print(pieces)
    pieces2 = []
    ## Part 2: quotation mark off reliable units, separate these out
    ## print(1)
    for meta_start,piece in pieces:
##        print(meta_start)
##        print(piece)
##        input()
        start = 0
        ## print(piece)
        sing = single_quote_pattern.search(piece,start)
        doub = double_quote_pattern.search(piece,start)
        while (start < len(piece)) and (sing or doub):
            if doub and ((not sing) or ((sing.start() < doub.start()) and (sing.end()>doub.end()))):
                ## if doub nested inside of singular, assume singular quotes are in error
                pieces2.extend([[meta_start+start,piece[start:doub.start()]],\
                                [meta_start+doub.start(1),doub.group(1)]])
                start = doub.end()
                doub = double_quote_pattern.search(piece,start)
                if sing:
                    sing = single_quote_pattern.search(piece,start)
            elif (not doub) or (sing.end() < doub.start()):
                ## if there is no doub or if sing completely precedes doub
                pieces2.extend([[meta_start+start,piece[start:sing.start()]],\
                                [meta_start+sing.start(2),sing.group(2)]])
                start = sing.end() 
                sing = single_quote_pattern.search(piece,start)             
            elif (sing.start()>doub.start()) and (sing.end() < doub.end()):
                ## nesting sing inside doub
                pieces2.extend([[meta_start+start,piece[start:doub.start()]],\
                                [meta_start+doub.start(1),piece[doub.start(1):sing.start()]],\
                                    [meta_start+sing.start(2),sing.group(2)],\
                                    [meta_start+sing.end(),piece[sing.end():doub.end(1)]]])
                start = doub.end()
                doub = double_quote_pattern.search(piece,start)
            elif doub.end() < sing.start():                
                ## doub first -- do doub only  (treat similarly to first case, except don't reinitialize singular)
                pieces2.extend([[meta_start+start,piece[start:doub.start()]],\
                                [meta_start+doub.start(1),doub.group(1)]])
                start = doub.end()
                doub = double_quote_pattern.search(piece,start)
                ## otherwise it is some sort of error
            elif doub and sing:
                if doub.start()<sing.start():
                    start = doub.start()+1
                    doub = double_quote_pattern.search(piece,start)
                else:
                    start = sing.start()+1
                    sing = single_quote_pattern.search(piece,start) 
            elif doub:
                start = doub.start()+1
                doub = double_quote_pattern.search(piece,start)
            elif sing:
                start = sing.start()+1
                sing = single_quote_pattern.search(piece,start) 
            else:
                print('Error in program regarding single and double quotes')
                print('piece:',piece)
                print('text:',text)
                ## this is probably not a real instance of quotation
        if start < len(piece):
##            print('piece',piece)
##            print('start',start)
##            print('?')
##            input()
            pieces2.append([meta_start+start,piece[start:]])
    ## Part III: split into chunks by commas and abbreviations
    ## each resulting piece an then be analyzed syntactically based on word class
    ## print(2)
    ## print(pieces2[0])
    for meta_start,piece in pieces2:
        ## parse each piece separately
        ## current_out_list = False
        ## print(piece)
        ## need a new version of splitters that provides offsets
        ## print(meta_start)
        ## print(piece)
        start = 0
        split_position = splitters.search(piece,start)
        ## print('split',split_position.start(),split_position.end())
        if not split_position:
            last = True
        else:
            last = False
        ## input()
        ## print(meta_start,piece)
        ## print('off',offset)
        while split_position or last:
        ## for piece2 in splitters.split(piece):
            start_match = first_character_pattern.search(piece,start)
            ## print(start)
            if start_match:
                start = start_match.start()
                ## print('start 2',start)
            ## print(start)
            if last:
                piece2 = piece[start:]
                ## print(2,last)
            else:
                piece2 = piece[start:split_position.start()]
                ## print('split',split_position.start())
                ## print(1,piece2)
##            if split_position:
##                print(meta_start,start,split_position.start(),piece2)
##            else:
##                print('last',last,start,piece2)
            ## ** 57 ***
            ## print('start',start)
            ## print(1,piece2)
            ## piece2 = piece2.rstrip(''' ,.?><'";:][{}-_=)(*&^%$#@!~''')
            ## print(2,piece2)
            ## input()
            current_out_list = False
            current_pos_list = False
            pre_np = False
            first_piece = True
            last_pos = False
            ## print(piece2)
            piece3, next_word_start,next_word_end = get_next_word(piece2,0)
            ## print(1,piece3)
            if piece3:
                piece2_start = next_word_start
                term_start = piece2_start+start ## start is the start for one level up
            ## for piece3 in piece2.split():
            ## print(piece2)
            while piece3:
                if piece3.istitle():
                    is_capital = True
                else:
                    is_capital = False
                lower = piece3.lower()
                ## print(lower)
                word_offset = next_word_start + start + meta_start + offset
                if piece3 == '':
                    pass
                else:
                    pos = guess_pos(lower,is_capital,offset=word_offset)
##                    print(pos,piece3,end=' ')
##                    if current_out_list:
##                        print(current_out_list)
##                    else:
##                        print('')
                    ## print(pos,lower,pre_np)
                    if (pos in ['SKIPABLE_ADJ']) and not(current_out_list):
                        pass
                    elif pos in ['DET','PREP']:
                        pre_np = True
                        if current_out_list:
                            term_string = stringify_word_list(current_out_list)
                        else:
                            term_string = False
                        if current_out_list and topic_term_ok(current_out_list,current_pos_list,term_string):
                            start_offset = term_start + meta_start+offset
                            end_offset = piece2_start+start+meta_start+offset
                            topic_terms.append([start_offset,end_offset,term_string])
                        current_out_list = False
                        current_pos_list = False
                    elif pos in ['AMBIG_POSSESS','POSSESS']:
                        piece3 = piece3[:-2]
                        if current_out_list:
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                        else:
                            current_out_list = [piece3]
                            current_pos_list = [pos]
                            term_start = piece2_start + start
                        if current_out_list:
                            term_string = stringify_word_list(current_out_list)
                        else:
                            term_string = False
                        if topic_term_ok(current_out_list,current_pos_list,term_string):
                            start_offset = term_start + meta_start+offset
                            ## end_offset = piece2_start+start+meta_start+offset
                            end_offset = next_word_end+start+meta_start+offset
                            topic_terms.append([start_offset,end_offset,term_string])
                        current_out_list = False
                        current_pos_list = False
                        pre_np = False
                        first_piece=False
                    elif (pos == 'ROMAN_NUMBER') and current_out_list and (len(current_out_list)>=1) and \
                         (current_pos_list[-1] in ['NOUN_OOV','NOUN','AMBIG_NOUN','PLURAL','AMBIG_PLURAL']):
                        if current_out_list:
                            term_string = stringify_word_list(current_out_list)
                        else:
                            term_string = False
                        if topic_term_ok(current_out_list,current_pos_list,term_string):
                            ## Roman Numerals can tack on to other terms
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                            start_offset = term_start + meta_start+offset
                            end_offset = next_word_end+start+meta_start+offset
                            topic_terms.append([start_offset,end_offset,term_string])
                        current_out_list = False
                        current_pos_list = False
                        pre_np = False
                        first_piece=False
                    elif (pos in ['PLURAL','AMBIG_PLURAL']) or (current_out_list and (len(current_out_list)>=1) and \
                                               ((current_pos_list[-1] == 'ADJECTIVE') and \
                                                         (pos == 'VERB') and (len(piece3)>3) and \
                                                     (piece3[-3:]=='ing'))):
                        ## a) plural nouns must end noun groups
                        ## b) ing verbs can sometimes also end noun groups
                        ## c) AMBIG_PLURALS, AMBIG_SINGULARs and ing verbs cannot stand by themselves and 
                        ## they can not be initial in noun groups
                        ## d) there is an exception -- if the next word is a nominalization,
                        ##    then the NP could continue
                        look_ahead,look_ahead_start,look_ahead_end = get_next_word(piece2,next_word_end)
                        if look_ahead:
                            look_ahead2,look_ahead2_start,dummy2 = get_next_word(piece2,look_ahead_end)
                            ## print(piece3,look_ahead,look_ahead2)
                            look_ahead2_offset = look_ahead2_start + start + meta_start + offset
                            if look_ahead2 and (guess_pos(look_ahead2,False,offset=look_ahead2_offset) in ['PLURAL','AMBIG_PLURAL','NOUN','AMBIG_NOUN','NOUN_OOV']):
                                look_ahead = False
                            look_ahead2 = False          
                        if current_out_list:
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                        else:
                            current_out_list = [piece3]
                            current_pos_list = [pos]
                            term_start = next_word_start + start
                        if look_ahead and is_nom_piece(look_ahead):
                            ## print(57,look_ahead)
                            pass
                        else:
                            if current_out_list:
                                term_string = stringify_word_list(current_out_list)
                            else:
                                term_string = False
                            if topic_term_ok(current_out_list,current_pos_list,term_string):
                                start_offset = term_start + meta_start+offset
                                ## end_offset = piece2_start+start+meta_start+offset
                                end_offset = next_word_end+start+meta_start+offset
                                topic_terms.append([start_offset,end_offset,term_string])
                                current_out_list = False
                                current_pos_list = False
                            else:
                                current_out_list = False
                                current_pos_list = False
                        pre_np = False
                        first_piece=False
                    elif pos in ['NOUN','POSSESS_OOV','AMBIG_NOUN','PERSON_NAME','NOUN_OOV']:
                        ## out of vocab possessive
                    ## evaluate piece by POS
                    ## looking for sequences of pieces that either: a) are unambigous nouns; or b) are OOV words
                        if current_out_list:
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                        else:
                            current_out_list = [piece3]
                            current_pos_list = [pos]
                            term_start = next_word_start + start
                        pre_np = False
                        first_piece=False
                    elif current_out_list and (last_pos == 'NOUN_OOV') and \
                            ((pos == 'TECH_ADJECTIVE') or ((pos == 'ADJECTIVE') and (piece3 in stat_adj_dict))):
                        current_out_list.append(piece3)
                        current_pos_list.append(pos)
                    elif (current_out_list == False) and (pre_np or first_piece) and \
                         ((pos == 'TECH_ADJECTIVE') or \
                              ((pos in ['VERB','AMBIG_VERB']) and (lower.endswith('ed') or lower.endswith('ing'))) or \
                              ((pos == 'ADJECTIVE') and (piece3 in stat_adj_dict))):
                        current_out_list = [piece3]
                        current_pos_list = [pos]
                        term_start = next_word_start + start
                        pre_np = False
                        first_piece=False                                    
                    elif (pre_np or first_piece or (last_pos in ['VERB','AMBIG_VERB']))  and (current_out_list == False) and \
                            (((pos in ['VERB','AMBIG_VERB']) and lower.endswith('ed')) or \
                                 ((pos == 'ADJECTIVE') and (piece3 in stat_adj_dict)) or \
                                 ((pos in ['TECH_ADJECTIVE']))):
                        ## considering allowing -ing verbs also, but this causes problems
                        current_out_list = [piece3]
                        current_pos_list = [pos]
                        term_start = next_word_start + start
                        pre_np = False
                        first_piece=False
                    elif current_out_list and (pos in ['TECH_ADJECTIVE','ADJECTIVE']) and (last_pos in ['TECH_ADJECTIVE','ADJECTIVE']):
                        current_out_list.append(piece3)
                        current_pos_list.append(pos)
                        pre_np = False
                        first_piece = False
                    else:
##                        print(1, pos,last_pos)
##                        print(current_out_list)
##                        print(piece3)
                        if current_out_list:
                            term_string = stringify_word_list(current_out_list)
                        else:
                            term_string = False
                        if current_out_list and topic_term_ok(current_out_list,current_pos_list,term_string):
                            start_offset = term_start + meta_start+offset
                            end_offset = piece2_start+start+meta_start+offset
                            topic_terms.append([start_offset,end_offset,term_string])
                        current_out_list = False
                        current_pos_list = False
                        pre_np = False
                        first_piece=False
                    last_pos = pos
                piece2_start = next_word_end
                piece3, next_word_start,next_word_end = get_next_word(piece2,piece2_start)
                ## print(2,piece3)
            if current_out_list:
                term_string=stringify_word_list(current_out_list)            
                if topic_term_ok(current_out_list,current_pos_list,term_string):
                    start_offset = term_start + meta_start+offset
                    end_offset = piece2_start+start+meta_start+offset
                    topic_terms.append([start_offset,end_offset,term_string])
            if split_position:
                start = split_position.end()
                split_position = splitters.search(piece,start)
            if not (last or split_position):
                last = True
            else:
                last = False
    return(topic_terms)

def get_topic_terms_from_one_patent2(fact_file,txt_file,outfile,pretty=True):
    ## this adds on the parsing out of key terms
    relates_to_topic_pattern = re.compile('(^|[^a-z])(invention|disclosure|subject|topic|embodiment|application|present).{0,50}?[^a-z]((relat(e|ed|es|ing).{0,15}[^a-z]to)|concerns|concerned with) +([^ ].*?( e\.g\..*?)?)\.')
    is_topic_pattern = re.compile('(^|[^a-z])(invention|disclosure|subject|topic|embodiment|application) +(is|provides|regards|pertains +to) +(.*?( e\.g\..*?)?)\.')
    ## relates_to_topic_pattern = re.compile('(^|[^a-z])(invention|disclosure|subject|topic|embodiment|application|present).{0,50}?[^a-z]((relat(e|ed|es|ing).{0,15}[^a-z]to)|concerns|concerned with)(.*?( e\.g\..*?)?)\.')
    ## is_topic_pattern = re.compile('(^|[^a-z])(invention|disclosure|subject|topic|embodiment|application) (is|provides|regards|pertains +to) (.*?( e\.g\..*?)?)\.')
    ## alternative is simply an abbreviated item in the first sentence of the paragraph
    ## of the section in question
    subtopic_pattern = re.compile('(^|[^a-z])((in particular)|(particularly)|(specifically))(,)? +((the|this) +(present +)?invention +)?(((relat(e|ed|es|ing))|(applicable)) +)?(to +)?(.*?( e\.g\..*?)?)(\.|$)',re.I)
    ## ( e\.g\..*?)?
    subsection_pattern = re.compile('(^| +)1\. +((Technical +)?Field(.{0,15}of the Invention)?)(.*?)2\.',re.I) 
    ## field 5 is the section 
    possible_sections = []
    topic_section = False
    topic_text = False
    subtopic_text = False
    match_start = False
    match_end = False
    match = False
    match2 = False
    confidence_score = False
    confidence_score1 = False
    confidence_score2 = False
    with open(fact_file,'r') as fact_stream:
        for line in fact_stream:
            line_attributes = get_integrated_line_attribute_value_structure(line,['SECTION','PAPER'])
            if line_attributes:
                avtype = line_attributes['av_type']
                if avtype == 'PAPER':
                    patent_title = line_attributes['TITLE'][0]
                elif avtype == 'SECTION':
                    ## divide into subsections here
                    ## if there exist lines that just have
                    ##  1. blah blah blah -- short title like things
                    ##  2. blah blah blah
                    ## then these are numbered subsections with the thing after the number
                    ## as the title
                    section_title = line_attributes['TITLE'][0]
                    section_score = topic_section_score(section_title)
                    if section_score > 0:
                        start,end = line_attributes['START'][0],line_attributes['END'][0]
                        possible_sections.append([section_score,section_title,start,end])
    if len(possible_sections)>0:
        possible_sections.sort()
        offset = False
        ## print(possible_sections)
        with open(txt_file,'r') as instream:
            intext=instream.read()
            while ((len(possible_sections)>0) and not match):
                match = False
                section_text1 = False
                section_text2 = False
                ## print(possible_sections[-1])
                topic_section=possible_sections.pop()
                confidence_score1,sect1_start,sect1_end = topic_section[0],int(topic_section[2]),int(topic_section[3])
                confidence_score1 = min(confidence_score1,4)
                ## print(topic_section)
                line_break_match = os.linesep+'(([ \t]*)[^A-Z \t])'
                section_text1 = intext[sect1_start:sect1_end]
                section_text1 = re.sub(line_break_match, '\g<1>',section_text1)
                ## print(section_text1)
                subsection_match = subsection_pattern.search(section_text1)
                if subsection_match:
                    sect1_end = sect1_start+subsection_match.end(5)
                    sect1_start = sect1_start+subsection_match.start(5)
                    section_text1 = subsection_match.group(5)
                match = relates_to_topic_pattern.search(section_text1)
                if match:
                    confidence_score = confidence_score1+2
                    topic_text = match.group(6)
                    section_text = section_text1
                    match_start = match.start(6)
                    match_end = match.end(6)
                    offset = sect1_start
                else:
                    if len(possible_sections)>0:
                        topic_section2 = possible_sections.pop()
                        ## print(topic_section2)
                        confidence_score2,sect2_start,sect2_end = topic_section2[0],int(topic_section2[2]),int(topic_section2[3])
                        confidence_score2 = min(confidence_score2,4)
                        section_text2 = intext[sect2_start:sect2_end].replace(os.linesep,' ')
                        ## print(section_text2)
                        subsection_match = subsection_pattern.search(section_text2)
                        if subsection_match:
                            sect2_end = sect2_start+subsection_match.end(5)
                            sect2_start = sect2_start+subsection_match.start(5)
                            section_text2 = subsection_match.group(5)
                        match = relates_to_topic_pattern.search(section_text2)
                        ## print('relates 2')
                        if match:
                            confidence_score = confidence_score2+2
                            topic_text = match.group(6)
                            ## print(topic_text)
                            ## print(match.group(0))
                            section_text = section_text2
                            match_start = match.start(6)
                            match_end = match.end(6)
                            offset = sect2_start
                    if not match:
                        match = is_topic_pattern.search(section_text1)
                        if match:
                            confidence_score=confidence_score1
                            topic_text = match.group(4)
                            section_text = section_text1
                            match_start = match.start(4)
                            match_end = match.end(4)
                            offset = sect1_start
                        elif section_text2:
                            match = is_topic_pattern.search(section_text2)
                            if match:
                                ## print('match 2')
                                confidence_score=confidence_score2
                                topic_text = match.group(4)
                                section_text = section_text2
                                match_start = match.start(4)
                                match_end = match.end(4)
                                offset = sect2_start
        if topic_text:
            match2 = subtopic_pattern.search(section_text,match_start)
            if match2 and (match2.start() < match.end()):
                if match2.start()<match_end:
                    match_end = match2.start()
                    topic_text = section_text[match_start:match_end]
            else:
                match2 = subtopic_pattern.search(section_text,match.end())
            if match2:
                subtopic_text = match2.group(16)
                subtopic_start = match2.start(16)
                subtopic_end = match2.end()
            if confidence_score >=4:
                confidence = 'High'
            elif confidence_score >=2:
                confidence = 'Medium'
            else:
                confidence = 'Low'
            topic_terms = get_topic_terms(topic_text)  ## could use patent title
            if subtopic_text:
                subtopic_terms = get_topic_terms(subtopic_text)
            else:
                subtopic_terms = False
            with open(outfile,'w') as outstream:
                outstream.write('Topic START='+str(match_start+offset)+' END='+str(match_end+offset)+' CONFIDENCE="'+confidence+'"')
                ## outstream.write('Topic START='+str(match_start+offset)+' END='+str(match_end+offset))
                if topic_terms:
                    for term in topic_terms:
                        outstream.write(' TERM="'+term+'"')
                if pretty:
                    outstream.write(' STRING="'+topic_text+'"')
                outstream.write(os.linesep)
                if subtopic_text:
                    outstream.write('Subtopic START='+str(subtopic_start+offset)+' END='+str(subtopic_end+offset)+' CONFIDENCE="'+confidence+'"')
                    ## outstream.write('Subtopic START='+str(subtopic_start+offset)+' END='+str(subtopic_end+offset))
                    if subtopic_terms:
                        for term in subtopic_terms:
                            outstream.write(' TERM="'+term+'"')
                    if pretty:
                        outstream.write(' STRING="'+subtopic_text+'"')
                    outstream.write(os.linesep)

def get_topic_terms_for_file_list(infile_list,outfile_list,pretty=True):
    with open(infile_list) as infile_list_stream, open(outfile_list) as outfile_list_stream:
        inlist = infile_list_stream.readlines()
        outlist = outfile_list_stream.readlines()
        if len(inlist) != len(outlist):
            print("Lists of input and output files should be of same length.")
            sys.exit(-1)
        for i in range(len(inlist)):
            try:
                txt_file,fact_file = inlist[i].strip().split(';')
                out_file = outlist[i].strip()
                print(txt_file)
            except:
                print("Error opening input/output files:")
                print("Input: %s\nOutput: %s" % (inlist[i].strip(),outlist[i].strip()))
            get_topic_terms_from_one_patent2(fact_file,txt_file,out_file,pretty=pretty)

term_id_number = 0

def write_term_summary_fact_set(outstream,term,instances,lemma_count):
    global term_id_number
    frequency = len(instances)
    lemma = lemma_dict[term]
    lemma_freq = lemma_count[lemma]
    for start,end in instances:
        term_id_number = 1 + term_id_number
        outstream.write('TERM ID="NYU_TERM_'+str(term_id_number)+'" STRING="'+term+'"'+' FREQUENCY='+str(frequency))
        outstream.write(' START='+str(start)+' END='+str(end))
        outstream.write(' LEMMA="'+lemma+'" LEMMA_FREQUENCY='+str(lemma_freq))
        outstream.write(os.linesep)

def write_term_becomes_article_citation(outstream,term,instances):
    global term_id_number
    for start,end in instances:
        term_id_number = 1 + term_id_number
        outstream.write('CITATION ID="NYU_ID_'+str(term_id_number)+'" STRING="'+term+'" CITE_CLASS="article"')
        outstream.write(' START='+str(start)+' END='+str(end)+os.linesep)
    
def write_term_summary_fact(outstream,term,frequency):
    global term_id_number
    term_id_number = 1 + term_id_number
    outstream.write('TERM ID="NYU_TERM_'+str(term_id_number)+'" STRING="'+term+'"'+' FREQUENCY='+str(frequency))
    outstream.write(os.linesep)

def patent_terms_from_file_using_manual_rules(nesent_file,outfile):
    ## strategy: 1) use sentence split lines, but remove xml (ignore NE, for now)
    ## 2) use same function as for topic terms case
    ## this is version 1 which does not get the offsets of the actual terms
    term_hash = {}
    with open(nesent_file,'r') as instream:
        for line in instream:
            if line[0].isdecimal():
                start, line = split_offset_from_line(line.strip())
                clean_line = remove_xml(line)
                end = len(line)+int(start)
                terms = get_topic_terms(clean_line)
                for term in terms:
                    if term in term_hash:
                        term_hash[term].append([start,end])
                    else:
                        term_hash[term]=[[start,end]]
    term_list = list(term_hash.keys())
    term_list.sort()
    with open(outfile,'w') as outstream:
        for term in term_list:
            write_term_summary_fact(outstream,term,len(term_hash[term]))

def get_all_terms_for_file_list(infile_list,outfile_list):
    with open(infile_list) as infile_list_stream, open(outfile_list) as outfile_list_stream:
        inlist = infile_list_stream.readlines()
        outlist = outfile_list_stream.readlines()
        if len(inlist) != len(outlist):
            print("Lists of input and output files should be of same length.")
            sys.exit(-1)
        for i in range(len(inlist)):
            try:
                nesent_file = inlist[i].strip()
                out_file = outlist[i].strip()
                print(nesent_file)
            except:
                print("Error opening input/output files:")
                print("Input: %s\nOutput: %s" % (inlist[i].strip(),outlist[i].strip()))
            patent_terms_from_file_using_manual_rules(nesent_file,out_file)

def patent_terms_from_file_using_manual_rules2(fact_file,txt_file,outfile):
    ## strategy: 1) use sentence split lines, but remove xml (ignore NE, for now)
    ## 2) use same function as for topic terms case
    ## this is version 1 which does not get the offsets of the actual terms
    paragraphs = []
    term_hash = {}
    with open(fact_file,'r') as fact_stream:
        for line in fact_stream:
            line_attributes = get_integrated_line_attribute_value_structure(line,['PAPER','STRUCTURE'])
            if line_attributes:
                ## print(line_attributes)
                avtype = line_attributes['av_type']
                if avtype == 'PAPER':
                    patent_title = line_attributes['TITLE'][0]
                elif (avtype == 'STRUCTURE') and ('TEXT' in line_attributes['TYPE']):
                    start,end = line_attributes['START'][0],line_attributes['END'][0]
                    start = int(start)
                    end = int(end)
                    paragraphs.append([start,end])
    paragraphs.sort()
    ## print('hi',paragraphs)
    ## print(1)
    with open(txt_file) as instream:
        intext=instream.read()
        for paragraph in paragraphs:
            start = paragraph[0]
            end = paragraph[1]
            line_break_match = os.linesep+'(([ \t]*)[^A-Z \t])'
            text = intext[start:end]
            text = re.sub(line_break_match, '\g<1>',text)
            terms = get_topic_terms(text)
            for term in terms:
                if term in term_hash:
                    term_hash[term].append([start,end])
                else:
                    term_hash[term]=[[start,end]]
    ## print(2)
    term_list = list(term_hash.keys())
    term_list.sort()
    with open(outfile,'w') as outstream:
        for term in term_list:
            write_term_summary_fact(outstream,term,len(term_hash[term]))

def get_all_terms_for_file_list2(infile_list,outfile_list):
    with open(infile_list) as infile_list_stream, open(outfile_list) as outfile_list_stream:
        inlist = infile_list_stream.readlines()
        outlist = outfile_list_stream.readlines()
        if len(inlist) != len(outlist):
            print("Lists of input and output files should be of same length.")
            sys.exit(-1)
        for i in range(len(inlist)):
            try:
                txt_file, fact_file = inlist[i].strip().split(';')
                out_file = outlist[i].strip()
                print(txt_file)
            except:
                print("Error opening input/output files:")
                print("Input: %s\nOutput: %s" % (inlist[i].strip(),outlist[i].strip()))
            patent_terms_from_file_using_manual_rules2(fact_file,txt_file,out_file)

def get_term_lemma(term):
    ## add plural --> singular
    global lemma_dict
    last_word_pat = re.compile('[a-z]+$',re.I)
    if term in lemma_dict:
        return(lemma_dict[term])
    elif (term in abbreviation_to_full_form) and (len(abbreviation_to_full_form[term])>0):
        output = abbreviation_to_full_form[term][0]
    else:
        last_word_match = last_word_pat.search(term)
        if last_word_match:
            last_word = last_word_match.group(0).lower()
            last_word_start = last_word_match.start()
            if (last_word in noun_base_form_dict) and (not last_word.endswith('ing')):
                if (last_word in noun_base_form_dict[last_word]):
                    output = term.upper()
                else:
                    output = (term[:last_word_start]+noun_base_form_dict[last_word][0]).upper()
            elif last_word.endswith('ies'):
                output = (term[:-3]+'y').upper()
            elif last_word.endswith('es') and (len(last_word)>3) and (last_word[-3] in 'oshzx'):
                output = term[:-2].upper()
            elif last_word.endswith('s'):
                output = term[:-1].upper()
            else:
                output = term.upper()
        else:
             output = term.upper()
    lemma_dict[term] = output                
    return(output)

def get_compound_lemma(compound_term,first_term,second_term):
    if compound_term in lemma_dict:
        return(lemma_dict[compound_term])
    else:
        first_lemma = get_term_lemma(first_term)
        second_lemma = get_term_lemma(second_term)
        output = (second_lemma+' '+first_lemma).upper()
        lemma_dict[compound_term] = output
        return(output)

def patent_terms_from_file_using_manual_rules3(fact_file,txt_file,outfile,pos_file=False):
    ## strategy: 1) use sentence split lines, but remove xml (ignore NE, for now)
    ## 2) use same function as for topic terms case
    ## this is version 1 which does not get the offsets of the actual term
    line_break_match = os.linesep+'(([ \t]*)[^A-Z \t])'
    paragraphs = []
    term_hash = {}
    pos_offset_table.clear()
    lemma_dict.clear()
    lemma_count = {}
    if pos_file and os.path.isfile(pos_file):
        load_pos_offset_table(pos_file)
    ## citations = []
    global term_id_number
    term_id_number = 0
    with open(fact_file,'r') as fact_stream:
        for line in fact_stream:
            line_attributes = get_integrated_line_attribute_value_structure(line,['PAPER','STRUCTURE'])
            if line_attributes:
                ## print(line_attributes)
                avtype = line_attributes['av_type']
                if avtype == 'PAPER':
                    if 'TITLE' in line_attributes:
                        patent_title = line_attributes['TITLE'][0]
                    else:
                        patent_tile = short_file(txt_file)
                elif (avtype == 'STRUCTURE') and ('TEXT' in line_attributes['TYPE']):
                    start,end = line_attributes['START'][0],line_attributes['END'][0]
                    start = int(start)
                    end = int(end)
                    paragraphs.append([start,end])
    paragraphs.sort()
    ## print('hi',paragraphs)
    ## print(1)
    with open(txt_file) as instream:
        intext=instream.read()
        for paragraph in paragraphs:
            start = paragraph[0]
            end = paragraph[1]            
            text = intext[start:end]
            text = re.sub(line_break_match, ' \g<1>',text)
            overlap_string = False ## at the paragraph level, we can ignore the overlap_strings
            ## citation_facts,overlap_string,debug_out = add_citations_from_patent_line(text,overlap_string,start)
            # if citation_facts:
            #     citations.extend(citation_facts)
            # standard_facts = get_standard_facts_from_line(text,start)
            # if standard_facts:
            #     citations.extend(standard_facts)
            term_triples = get_topic_terms2(text,start)
            compound_triples = []
            last_triple = False
            ## the terms are in t_start order
            for t_start,t_end,term in term_triples:
                if term in term_hash:
                    term_hash[term].append([t_start,t_end])
                    lemma = get_term_lemma(term)
                    if lemma in lemma_count:
                        lemma_count[lemma]=lemma_count[lemma]+1
                    else:
                        lemma_count[lemma]=1
                else:
                    term_hash[term]=[[t_start,t_end]]
                    lemma = get_term_lemma(term)
                    if lemma in lemma_count:
                        lemma_count[lemma]=lemma_count[lemma]+1
                    else:
                        lemma_count[lemma]=1
                if last_triple and (t_start>last_triple[1]):
                    inbetween = re.search('^ +[Oo][Ff] +$',intext[last_triple[1]:t_start])
                    if inbetween:
                        compound_term = intext[last_triple[0]:t_end]
                        compound_triple = [last_triple[0],t_end,compound_term]
                        term_triples.append(compound_triple)
                        if compound_term in term_hash:
                            term_hash[compound_term].append([last_triple[0],t_end])
                            lemma = get_compound_lemma(compound_term,last_triple[2],term)
                            if lemma in lemma_count:
                                lemma_count[lemma]=lemma_count[lemma]+1
                            else:
                                lemma_count[lemma]=1
                        else:
                            term_hash[compound_term]=[[last_triple[0],t_end]]
                            lemma = get_compound_lemma(compound_term,last_triple[2],term)
                            if lemma in lemma_count:
                                lemma_count[lemma]=lemma_count[lemma]+1
                            else:
                                lemma_count[lemma]=1
                last_triple=[t_start,t_end,term]
    ## print(2)
    term_list = list(term_hash.keys())
    term_list.sort()
    with open(outfile,'w') as outstream:
        # citation_num = 0
        # for fact in citations:
        #     citation_num = 1 + citation_num
        #     write_citation_fact(fact,outstream,citation_num,output_style="BAE",NYU_ID=True)
        for term in term_list:
            if et_al_citation.search(term):
                write_term_becomes_article_citation(outstream,term,term_hash[term])
            else:
                write_term_summary_fact_set(outstream,term,term_hash[term],lemma_count)

def read_in_stat_term_dict (indict):
    stat_term_dict.clear()
    stat_adj_dict.clear()
    with open(DICT_DIRECTORY+indict) as instream:
        for line in instream.readlines():
            line_entry = line.strip().split('\t')
            stat_term_dict[line_entry[0]] = True
            if ' ' in line_entry:
                position = line_entry.index(' ')
                first_word = line_entry[:position].lower()
                pos = guess_pos(first_word)
                if pos in ['ADJECTIVE','SKIPABLE_ADJ','TECH_ADJECTIVE']:
                    if not first_word in stat_adj_dict:
                        stat_adj_dict[first_word] = 1
                    else:
                        stat_adj_dict[first_word] = stat_adj_dict[first_word]+1
    adj_threshold = 5 ## not sure what this number should be
    for key in stat_adj_dict:
        if stat_adj_dict[key]<adj_threshold:
            stat_adj_dict.pop(key)


def get_all_terms_for_file_list3(infile_list,outfile_list,term_dict=False,abbrev_full_dict_file=False,full_abbrev_dict_file=False):
    if term_dict:
        read_in_stat_term_dict(term_dict)
    if full_abbrev_dict_file and abbrev_full_dict_file:
        read_in_full_to_abbreviation_dict(full_abbrev_dict_file,abbrev_full_dict_file)
    with open(infile_list) as infile_list_stream, open(outfile_list) as outfile_list_stream:
        inlist = infile_list_stream.readlines()
        outlist = outfile_list_stream.readlines()
        if len(inlist) != len(outlist):
            print("Lists of input and output files should be of same length.")
            sys.exit(-1)
        for i in range(len(inlist)):
            try:
                file_tuple = inlist[i].strip().split(';')
                txt_file = file_tuple[0]
                fact_file = file_tuple[1]
                if len(file_tuple)>2:
                    pos_file = file_tuple[2]
                else:
                    pos_file = False
                out_file = outlist[i].strip()
                print(txt_file)
            except:
                print("Error opening input/output files:")
                print("Input: %s\nOutput: %s" % (inlist[i].strip(),outlist[i].strip()))
            patent_terms_from_file_using_manual_rules3(fact_file,txt_file,out_file,pos_file=pos_file)

cluster_hash = {}

def derive_base_form_from_plural(word):
    if word in noun_base_form_dict:
        return(noun_base_form_dict[word])
    elif (len(word)>3) and (word[-3:] == 'ies'):
        return([word[:-3]+'y',word[:-2]])
    elif len(word)>2 and (word[-2:] == 'es'):
        return([word[:-1],word[:-2]])
    elif len(word)>1 and (word[-1]=='s') and not(word[-2] in "suciy"):
        return([word[:-1]])
    else:
        return(False)

def topic_term_rating(word,pos):
    ## based on topic_term_ok
    ## print(word)
    word = word.lower()
    if (word in pos_dict) and not (pos == 'NOUN_OOV'):
        in_dictionary = True
    else:
        in_dictionary = False
    if (pos in ['NOUN','AMBIG_NOUN']) or ((pos == 'NOUN_OOV') and not(word in pos_dict)):
        ## adding 'NOUN_OOV' to this list without modification has the effect
        ## of permitting people names as terms
        if word.isnumeric():
            return('Bad')
        elif not in_dictionary:
            return('Good')
        else:
            nom_rank = nom_class(word,pos)
            if nom_rank >=2:
                return('Medium')
            else:
                return('Bad')
    elif pos in ['PLURAL','AMBIG_PLURAL']:
        if word in noun_base_form_dict:
            base = noun_base_form_dict[word][0]
            nom_rank = nom_class(base,pos)
            if nom_rank >=2:
                return('Medium')
            else:
                return('Bad')
        else:
            return('Good')
    elif pos in ['TECH_ADJECTIVE','ADVERB']:
        if in_dictionary:
            return('Bad')
        else:
            return('Medium')
    else:
        return('Bad')

def make_term_prefix(word_list):
    if len(word_list)==0:
        return('')
    else:
        return(' '.join(word_list)+' ')

def make_term_suffix(word_list):
    if len(word_list)==0:
        return('')
    else:
        return(' '+' '.join(word_list))

def get_morph_variants(word_seq,pos_seq,POS,mitre=False):
    ## based on get_term_variations in
    ## get_morphological_and_abbreviation_variations
    last_word = word_seq[-1]
    prefix = make_term_prefix(word_seq[:-1])
    bases = False
    dict_forms = False
    plurals = False
    output = []
    big_bases = []
    vp_ing = []
    main_base = False
    if POS == 'NP':
        if last_word in noun_base_form_dict:
            bases = noun_base_form_dict[last_word]
            if last_word in bases:
                plurals = derive_plurals(last_word)
            else:
                plurals = [last_word]
                if bases and (len(last_word)>2) and (last_word[-2]=='s'):
                    dict_forms = plural_dict[bases[0]]
                    if dict_forms:
                    ## just add -ing forms
                        for form in dict_forms:
                            if (len(form)>3) and (form[-3:]=='ing'):
                                plurals.append(form)
        ## input list is all lower case (so there is no reason to check upper/lower case)
        elif len(last_word)>3 and (last_word[-3:] == 'ies'):
            bases = [last_word[:-3]+'y',last_word[:-2]]
            plurals = [last_word]
        elif len(last_word)>2 and (last_word[-2:] == 'es'):
            bases = [last_word[:-1],last_word[:-2]]
            plurals = [last_word]
        elif len(last_word)>1 and (last_word[-1]=='s') and \
             not(last_word[-2] in "suciy"):
            bases = [last_word[:-1]]
            plurals = [last_word]
        else:
            ## print('hello')
            bases = [last_word]
            plurals = derive_plurals(last_word)
        main_base = bases[0].lower()
        if plurals:
            for plural in plurals:
                output.append(prefix+plural)
        if bases:
            for base in bases:
                big_base = prefix+base
                output.append(big_base)
                big_bases.append(big_base.upper())
        return(big_bases,output,main_base)
    elif POS == 'VP':
        if last_word in verb_variants_dict:
            big_bases.append((prefix+last_word).upper())
            main_base = last_word.lower()
            for variant in verb_variants_dict[last_word]:
                big_variant = prefix+variant
                if (len(variant)>3) and (variant[-3:] == 'ing') and (not mitre):
                    vp_ing.append(big_variant)
                output.append(big_variant)
        elif last_word in verb_base_form_dict:
            if not last_word in verb_base_form_dict[last_word]:
                big_variant = prefix+last_word
                if (len(last_word)>3) and (last_word[-3:] == 'ing') and (not mitre):
                    vp_ing.append(big_variant)
                output.append(big_variant)
            other_variants = []
            for base in verb_base_form_dict[last_word]:
                if base in verb_variants_dict:
                    for item in verb_variants_dict[base]:
                        if (item != last_word) and (not item in other_variants):
                            other_variants.append(item)
                big_base = prefix+last_word
                big_bases.append(big_base.upper())
                output.append(big_base)
            main_base = verb_base_form_dict[last_word][0].lower()
            for variant in other_variants:
                big_variant = prefix+variant
                if (len(variant)>3) and (variant[-3:] == 'ing') and (not mitre):
                    vp_ing.append(big_variant)
                output.append(big_variant)
        elif word_seq[0] in verb_variants_dict:
            suffix = make_term_suffix(word_seq[1:])
            big_bases.append((' '.join(word_seq)).upper())
            for variant in verb_variants_dict[word_seq[0]]:
                big_variant = variant+suffix
                if (len(variant)>3) and (variant[-3:] == 'ing') and (not mitre):
                    vp_ing.append(big_variant)
                output.append(big_variant)                
            main_base = word_seq[0].lower()
        elif word_seq[0] in verb_base_form_dict:
            suffix = make_term_suffix(word_seq[1:])
            if not word_seq[0] in verb_base_form_dict[word_seq[0]]:
                big_variant = word_seq[0]+suffix
                if (len(word_seq[0])>3) and (word_seq[0][-3:] == 'ing') and (not mitre):
                    vp_ing.append(big_variant)
                output.append(big_variant)
            other_variants = []
            for base in verb_base_form_dict[word_seq[0]]:
                if base in verb_variants_dict:
                    for item in verb_variants_dict[base]:
                        if (item != word_seq[0]) and (not item in other_variants):
                            other_variants.append(item)
                big_base = word_seq[0]+suffix
                big_bases.append(big_base.upper())
                output.append(big_base)
            main_base = verb_base_form_dict[word_seq[0]][0].lower()
            for variant in other_variants:
                big_variant = variant+suffix
                if (len(variant)>3) and (variant[-3:] == 'ing') and (not mitre):
                    vp_ing.append(big_variant)
                output.append(big_variant)
        else:
            ## assume (for now) that if a word is not in the verb dictionary, it is not a verb
            big_base = ' '.join(word_seq)
            output.append(big_base)
            big_bases.append(big_base.upper())
            main_base = word_seq[0].lower()
        return(big_bases,output,vp_ing,main_base)

def get_noun_nom_map(word):
    if word in pos_dict:
        if word in nom_map_dict:
            return(nom_map_dict[word])
    elif (len(word) > 3) and (word[-1] == 'r') and (word[-2] in 'eo'):
        if (word[:-2] in nom_map_dict):
            return(nom_map_dict[word[:-2]])
        elif (word[-3] == word[-4]) and (word[:-3] in nom_map_dict):
            return(nom_map_dict[word[:-3]])
        elif (word[-2]+'e') in nom_map_dict:
            return(nom_map_dict[word[-2]+'e'])
        else:
            return(False)
    else:
        return(False)

def is_ok_nom(word):
    if word in nom_dict:
        entry = nom_dict[word]
        if ('NOM' in entry) or ('ABLE-NOM' in entry):
            return(True)

def get_penult_word(instring):
    out = re.search('(\w+)[^\w]+\w+$',instring)
    if out:
        return(out.group(1))
    else:
        return(False)

def normal_word(word):
    ## print(word)
    if (word in pos_dict):
        pos = pos_dict[word][:]
        if 'PERSON_NAME' in pos:
            if len(pos)>1:
                return(True)
            else:
                return(False)
        else:
            return(True)
    else:
        return(False)

def get_np1_lemma(np1_base):
    np_out = ''
    words = re.split('[^\w]+',np1_base)
    first = True
    nominalization = False
    for word in words:
        ## print(word)
        if first and (word.lower() in ABBREVIATION_STOP_WORDS):
            pass
        else:
            upper = word.upper()
            word_map = get_noun_nom_map(word)
            if (not normal_word(word)) or word.isupper():
                fulls = get_expanded_forms_from_abbreviations(upper)
            else:
                fulls = False
            ## print(1,word_map)
            ## print(2,fulls)
            if not first:
                np_out = np_out+' '
            else:
                first = False
            if word_map:
                nominalization = True
                np_out = np_out+word_map.upper()
            elif fulls:
                np_out = np_out+fulls[0]
            else:
                np_out = np_out+upper
    return(np_out,nominalization)

def get_np_lemma (np1_base,prep=False,np2=False):
    ## print(np1_base)
    np1_out,map1 = get_np1_lemma(np1_base)
    if not np2:
        return(np1_out,map1)
    else:
        np2_lemma,map2 = get_np1_lemma(np2)
        if prep:
            return(np2_lemma + ' ' + np1_out,map1 or map2)
        else:
            return(np1_out + ' ' + np2_lemma,map1 or map2)                                              


def get_np_vp_lemma (np_base,vp_base,vp_ing,np_rating,verb_base):
    ## print(1,np_base,2,vp_base,3,vp_ing,np_rating)
    ## print('np_vp',type(np_base))
    np_lemma,nom = get_np_lemma(np_base)
    ## use rule above -- don't currently
    ## deal with 2NPs + VP case (which is possible)
    ## print(np_lemma)
    out = np_lemma[:]
    ## print(out)
    found_nom = False
    vp_pos_seq_mod = []
    last_pos = False
    vp_rating = 'Not Sure'
        ## this only keeps the last verb
    ## print(vp_base)
    ## print(vp_pos_seq_mod)
##    if len(vp_base)>len(vp_pos_seq_mod):
##        print(vp_base)
##        print(vp_pos_seq_mod)
    if verb_base in nom_map_dict:
        vp_rating = 'Good'
        out = out+' '+nom_map_dict[verb_base].upper()
    elif vp_ing:
        out = out+' '+vp_ing.upper()
    else:
        out = out+' '+verb_base.upper()
    if (np_rating == 'OK') or (vp_rating == 'Good'):
        rating = 'Good'
    else:
        rating = 'Medium'
    ## print(out,rating)
    ## input('')
    return(out,rating)

def simple_tech_adj_chunk(chunk):
    if (len(chunk) == 2) and (type(chunk[1]) == list) and (chunk[1][0] == 'TECHNICAL_ADJECTIVE'):
        return(True)
    else:
        return(False)

def simple_singular_np(chunk):
    if (len(chunk) == 2) and (type(chunk[1]) == list) and (chunk[1][0] in ['NOUN','AMBIG_NOUN']):
        return(True)
    else:
        return(False)

def word_split(line):
    start = 0
    output = []
    while start < len(line):
        next_word,start,end=(get_next_word(line,start))
        if next_word:
            output.append(next_word)
            start = end
        else:
            return(output)
    return(output)
    
def term_classify(line,mitre=False):
    ## based on get_topic_terms, but based on smaller n-grams, typically with no punctuation
    ## return (lemma, classification, rating, other_terms)
    ## initially, do not handle verb + particle nominalizations
    ## print(line)
    weird_char = re.compile('[^ 0-9A-Za-z\-\'\.]')
    word_pattern = re.compile('[^\w]+')
    weird_spacing = re.compile('([^a-zA-Z0-9] )|( [^a-zA-Z0-9])|(-$)')
    pre_np = False
    main_base = False
    verb_base = False
    chunks = False
    ## ratings: good, medium, bad
    if weird_char.search(line) or weird_spacing.search(line):
        return(line,'bad_character','Bad',False,chunks)
    ## words = word_pattern.split(line)
    if mitre:
        words = word_pattern.split(line)
    else:
        words = word_split(line)
    if len(words) == 1:
        pos = guess_pos(words[0].lower(),False)
        base2 = False
        abbrevs = False
        output = False
        if pos in ['NOUN','AMBIG_NOUN','NOUN_OOV']:
            if '-' in words[0]:
                base2 = re.sub('\-',' ',words[0])
            if (not normal_word(words[0])) or words[0].isupper():
                fulls = get_expanded_forms_from_abbreviations(words[0].upper())
            else:
                fulls = False
            plurals = derive_plurals(words[0])
            if fulls:
                output = fulls
                if base2:
                    output.append(base2)
                if plurals:
                    output.extend(plurals)
                for full in fulls:
                    return(full,'ABBREVIATION','Good',output,chunks)
            elif base2:
                rating = topic_term_rating(words[0],pos)
                return(base2.upper(),'HYPHENATION',rating,output,chunks)
            else:
                rating = topic_term_rating(words[0],pos)
                return(words[0].upper(),'SIMPLE',rating,output,chunks)
        elif pos in ['PLURAL','AMBIG_PLURAL']:
            bases = derive_base_form_from_plural(words[0])
            base2s = []
            if bases:
                abbrevs = []
                for base in bases:
                    if '-' in base:
                        base2s.append(re.sub('\-',' ',base))
                    if (not normal_word(base)) or words[0].isupper():
                        out = get_expanded_forms_from_abbreviations(base.upper())
                    else:
                        out = False
                    if out:
                        abbrevs.extend(out)
                if base2s:
                    for base in base2s:
                        if (not normal_word(base)) or words[0].isupper():
                            out = get_expanded_forms_from_abbreviations(base.upper())
                        else:
                            out = False
                        if out:
                            abbrevs.extend(out)
            if abbrevs and (len(abbrevs)>0):
                output = abbrevs
                output.append(words[0])
                if base2s:
                    output.extend(base2s)
                for abbrev in abbrevs:
                    return(abbrev,'ABBREVIATION','Good',output,chunks)
            elif base2s:
                rating = topic_term_rating(words[0],pos)
                return(base2s[0].upper(),'HYPHENATION',rating,output,chunks)
            elif bases:
                rating = topic_term_rating(words[0],pos)
                return(bases[0].upper(),'SIMPLE',rating,output,chunks)
            else:
                rating = topic_term_rating(words[0],pos)
                return(line.upper(),'SIMPLE',rating,output,chunks)
        else:
            ## 1) additional alternative for verb: look up nominalization
            ##    Also, varying verb forms in that case, but unclear whether
            ##    any one word verb case is really OK
            ## 2) additional alternative for argument nominalization:
            ##    look up verb nominalization, but unclear whether this is
            ##    really justified for the one word case
            ## 3) adverb --> adjective + some sort of generic noun
            ## 4) adjective --> add generic noun
            rating = topic_term_rating(words[0],pos)
            classification = 'In_or_Out_of_Dictionary'
            return(line.upper(),classification,rating,False,chunks)
    else:
        conjunction_position = False ## there is never more than one in the current Mitre list
        position = 0
        current_chunk = False
        chunks = []
        unnecessary_pieces = 0
        prep_count = 0
        ## allow at most 1 verb chunk
        length = len(words)
        if line.upper() in full_to_abbreviation_dict:
            return(line.upper(),'ABBREVIATION','Good',[line],chunks)
        elif (len(line)>2) and (line[-1] in ['s','S']) and (line[:-1].upper() in full_to_abbreviation_dict):
            return(line[:-1].upper(),'ABBREVIATION','Good',[line],chunks)
        elif (len(line)>3) and (line[-1] in ['es','ES']) and (line[:-2].upper() in full_to_abbreviation_dict):
            return(line[:-2].upper(),'ABBREVIATION','Good',[line],chunks)
        for word in words:
            ## print(word)
            position = position+1
            if word in ['and','or']:
                pos = 'CCONJ'
            else:
                pos = guess_pos(word,False) ## the Mitre output is monocase (all lowercase)
            ## print(pos,word)
            ## print(current_chunk)
            if pos == 'PREP':
                prep_count = 1+prep_count
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = False
                chunks.append([pos,word])
            elif pos == 'CCONJ':
                conjunction_position = True
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = False
            elif pos in ['DET','AMBIG_POSSESS','POSSESS','POSSESS_OOV']:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = ['NP',[pos,word]]
                if pos == 'DET':
                   unnecessary_pieces = 1 + unnecessary_pieces 
            elif pos in ['SKIPABLE_ADJ','ADJECTIVE','TECH_ADJECTIVE']:
                if (pos != 'TECH_ADJECTIVE') and (not word in stat_adj_dict):
                    unnecessary_pieces = 1 + unnecessary_pieces                    
                if current_chunk:
                    if current_chunk[0]=='NP':
                        current_chunk.append([pos,word])
                    else:
                        chunks.append(current_chunk)
                        current_chunk = ['NP',[pos,word]]
                else:
                    current_chunk = ['NP',[pos,word]]
            elif pos in ['PLURAL','AMBIG_PLURAL']:
                if current_chunk:
                    if current_chunk[0] == 'NP':
                        current_chunk.append([pos,word])
                        chunks.append(current_chunk)
                        current_chunk = False
                    elif simple_tech_adj_chunk(current_chunk):
                        current_chunk[0] = 'NP'
                        current_chunk.append([pos,word])
                        chunks.append(current_chunk)
                        ## print(1,current_chunk)
                        current_chunk = False
                    else:
                        chunks.append(current_chunk)
                        current_chunk = False
                        chunks.append(['NP',[pos,word]])
                else:
                    chunks.append(['NP',[pos,word]])
            elif pos in ['NOUN','AMBIG_NOUN','NOUN_OOV']:
                if current_chunk:
                    if current_chunk[0]=='NP':
                        current_chunk.append([pos,word])
                    elif simple_tech_adj_chunk(current_chunk):
                        ## print(2,current_chunk)
                        current_chunk[0] = 'NP'
                        current_chunk.append([pos,word])
                        ## print(2,current_chunk)
                    else:
                        chunks.append(current_chunk)
                        current_chunk = ['NP',[pos,word]]
                else:
                    current_chunk = ['NP',[pos,word]]
            elif pos in ['VERB','AMBIG_VERB']:
                if current_chunk:
                    if current_chunk[0] == 'ADVP':
                        current_chunk[0] = 'VP'
                        current_chunk.append([pos,word])
                    elif current_chunk[0] == 'VP':
                        current_chunk.append([pos,word])
                    else:
                        chunks.append(current_chunk)
                        current_chunk = ['VP',[pos,word]]
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = ['VP',[pos,word]]
            elif pos in ['ADVERB']:
                if current_chunk:
                    if current_chunk[0] in ['VP','ADVP']:
                        current_chunk.append([pos,word])
                    else:
                        chunks.append(current_chunk)
                        current_chunk = ['ADVP',[pos,word]]
            elif current_chunk:
                chunks.append(current_chunk)
                chunks.append(['XP',[pos,word]])
                current_chunk = False
            else:
                current_chunk = ['XP',[pos,word]]
            position = 1 + position
        ## print(chunks)
        if current_chunk:
            last_pos_word_pair = current_chunk[-1]
            if (current_chunk[0] == 'NP') and (not last_pos_word_pair[0] in ['NOUN','AMBIG_NOUN','PLURAL','AMBIG_PLURAL','NOUN_OOV']):
                current_chunk[0] = 'XP'
##            elif (current_chunk[0] == 'NP') and (not last_pos_word_pair[-1] in ['NOUN','AMBIG_NOUN','PLURAL','AMBIG_PLURAL','NOUN_OOV']):
##                current_chunk[0] = 'XP'
            chunks.append(current_chunk)
        ## print(2,chunks)
        if conjunction_position:
            ## a real term should not contain a conjunction
            ## print('contains conjunction:',line)
            ## verify this case
            return(line.upper(),'contains_conjunction','Bad',[line],chunks)
        elif len(chunks)>3:
            ## verify this case, there may be some cases that are OK
            return(line.upper(),'too_many_chunks','Bad',[line],chunks)
        else:
            ok_np = 0
            np_1 = False
            np_1_bases = False
            np_1_pos_seq = False
            np_1_variants = False
            np_2 = False
            np_2_bases = False
            np_2_variants = False
            vp_1 = False
            vp_2 = False
            vp_bases = False
            vp_variants = False
            vp_ing = False
            vp_pos_seq = False
            new_construction = False
            position = 0
            prep_position = False
            for chunk in chunks:
                if chunk[0] == 'PREP':
                    prep_position = position
                elif chunk[0] == 'NP':
                    word_seq = []
                    pos_seq = []
                    for leaf in chunk[1:]:
                        ## print(leaf)
                        pos_seq.append(leaf[0])
                        word_seq.append(leaf[1])
                    if word_seq:
                        term_string=stringify_word_list(word_seq)
                    else:
                        term_string = False
                    if topic_term_ok(word_seq,pos_seq,term_string):
                        ok_np = 1+ ok_np
                        if np_1:
                            np_2 = [word_seq, 'Good']
                            np_2_bases,np_2_variants,main_base = get_morph_variants(word_seq,pos_seq,'NP')
                        else:
                            np_1 = [word_seq, 'Good']
                            np_1_pos_seq = word_seq
                            np_1_bases,np_1_variants,main_base = get_morph_variants(word_seq,pos_seq,'NP')
                    else:
                        if np_1:
                            np_2 = [word_seq, 'Bad']
                            np_2_bases,np_2_variants,main_base = get_morph_variants(word_seq,pos_seq,'NP')
                        else:
                            np_1 = [word_seq, 'Bad']
                            np_1_bases,np_1_variants,main_base = get_morph_variants(word_seq,pos_seq,'NP')
                elif chunk[0] == 'VP':
                    if vp_1 or vp_2:
                        return(line.upper(),'too_many_verbs','Bad',[line],chunks)
                    else:
                        word_seq = []
                        pos_seq = []
                        for leaf in chunk[1:]:
                            pos_seq.append(leaf[0])
                            word_seq.append(leaf[1])
                        if np_1:
                            vp_2 = [word_seq,'OK']
                            vp_bases,vp_variants,vp_ing,verb_base = get_morph_variants(word_seq,pos_seq,'VP',mitre=True)
                            vp_pos_seq = pos_seq
                        else:
                            vp_1 = [word_seq,'OK']
                            vp_bases,vp_variants,vp_ing,verb_base = get_morph_variants(word_seq,pos_seq,'VP',mitre=True)
                            vp_pos_seq = pos_seq
                else:
                    new_construction = True
                position = 1 + position
            if new_construction:
                ## print(chunks)
                return(line.upper(),'sequence_with_XP_chunk','Bad',[line],chunks)
            elif np_1 and (len(chunks) == 1):
                if unnecessary_pieces >=2:
                    rating = 'Bad'
                elif np_1[1] in ['OK','Good']:
                    if unnecessary_pieces >0:
                        rating = 'Medium'
                    else:
                        rating = 'Good'
                elif np_1[1] == 'Medium':
                    rating = 'Medium'
                else:
                    rating = 'Bad'
                ## print(np_1[0])
                ## print('term_classify',type(np_1[0]))
                ## print(np_1)
                lemma,nom = get_np_lemma(' '.join(np_1[0]))
                ## print('np_1_lemma',lemma)
                ## print(np_1,rating)
                return(lemma,'Normal_NP',rating,np_1_variants,chunks)
            elif np_1 and np_2 and (prep_position == 1):
                if unnecessary_pieces >=2:
                    rating = 'Bad'
                if (np_1[1] == 'OK') and (np_2[1] == 'OK'):
                    if unnecessary_pieces >0:
                        rating = 'Medium'
                    else:
                        rating = 'Good'
                elif (np_1[1] == 'OK') or (np_2[1] == 'OK'):
                    rating = 'Medium'
                else:
                    rating = 'Bad'
                full_bases = []
                full_variants = []
                for np1 in np_1_bases:
                    for np2 in np_2_bases:
                        full_base = np1 + ' '+ chunks[1][1]+' '+np2
                        full_bases.append(full_base)
                for np1 in np_1_variants:
                    for np2 in np_2_variants:
                        full_variant = np1 + ' '+ chunks[1][1]+' '+np2
                        full_variants.append(full_variant)
                ## for NP NP constructions, just choose first one (for now)
                ## Eventually, unify "recognition of speech" and "speech recognition"
                ## print('term_classify2',type(np_1[0]))
                lemma,nom = get_np_lemma(np_1_bases[0],prep=chunks[1][1],np2=np_2_bases[0])
                return(lemma,'2_Part_NP',rating,full_variants,chunks)
            elif np_1 and (vp_1 or vp_2) and (len(chunks) == 2):
                ## did not implement nominalization fixes
##                if (len(np_1)<1) or (len(vp_bases)<1) or (len(vp_ing)<1) or (len(np_1)<2):
##                    print(1,np_1,2,vp_bases,3,vp_ing,4,np_1)
##                print(1,np_1_bases)
##                print(2,vp_bases)
##                print(3,vp_ing)
##                print(4,np_1)
##                print(verb_base)
                if vp_ing and (len(vp_ing)>0):
                    ing = vp_ing[0]
                else:
                    ing = False
                lemma,rating = get_np_vp_lemma(np_1_bases[0],vp_bases[0],ing,np_1[1],verb_base)
                if unnecessary_pieces >=2:
                    rating = 'Bad'
                elif (rating == 'Good') and (unnecessary_pieces >0):
                    rating = 'Medium'
                ## vp first, e.g., "recognizing/recognizes/recognized speech"
                full_variants = []
                ## print(chunks)
                for np1 in np_1_variants:
                    for vp in vp_variants:
                        full_variants.append(vp+' '+np1)
                    if vp_ing:
                        for vp in vp_ing:
                            full_variants.append(np1+' '+vp)
                if vp_2 and not (line in full_variants):
                    full_variants.append(line)
                if vp_2 and vp_ing:
                    return(lemma,'NP+VP_ing',rating,full_variants,chunks)
                elif vp_ing:
                    return(lemma,'VP_ing+NP',rating,full_variants,chunks)
                else:
                    return(lemma,'verb+NP',rating,full_variants,chunks)
            # elif np_1 and vp_2:
            #     lemma = get_np_vp_lemma(np_1_variants,vp_variants)
            #     ## vp second, e.g., "speech recognizing"
            elif np_1 and np_2 and (len(chunks) == 2) and simple_singular_np(chunks[1]):
                if unnecessary_pieces >=2:
                    rating = 'Bad'
                elif (np_1[1] == 'OK') and (np_2[1] == 'OK'):
                    if unnecessary_pieces >0:
                        rating = 'Medium'
                    else:
                        rating = 'Good'
                elif (np_1[1] == 'OK') or (np_2[1] == 'OK'):
                    rating = 'Medium'
                else:
                    rating = 'Bad'
                full_bases = []
                full_variants = []
                for np1 in np_1_bases:
                    for np2 in np_2_bases:
                        full_base = np1 +' '+np2
                        full_bases.append(full_base)
                for np1 in np_1_variants:
                    for np2 in np_2_variants:
                        full_variant = np1 + ' '+np2
                        full_variants.append(full_variant)
                lemma,nom = get_np_lemma(np_1_bases[0],np2=np_2_bases[0])
                return(lemma,'2_Part_NP_no_prep',rating,full_variants,chunks)
            else:
                ## print(chunks)
                ## print(np_1)
                ## print(np_2)
                return(line.upper(),'unexpected_POS_sequence','Bad',[line],chunks)
            ## rating based on OOV and nominalizations
            ## have not really attempted to identify "uninteresting" nouns and verbs
            ## e.g., support verbs, transparent nouns, boring nouns ('device', etc.)

def print_term_rating_fact(term,lemma,classification,rating,outstream):
    outstream.write('TERM_LIST_ENTRY')
    for pair in [['TERM',term],['LEMMA',lemma],['CLASSIFICATION',classification],['RATING',rating]]:
        if not type(pair[1]) == str:
            print(term)
            print(pair)
        outstream.write(' '+pair[0]+'="'+pair[1]+'"')
    outstream.write(os.linesep)

def print_term_set(outstream,key,variations):
    outstream.write('TERM_DICTIONARY_ENTRY')
    outstream.write(' LEMMA="'+key+'"')
    for word in variations:
        outstream.write(' TERM="'+word+'"')
    outstream.write(os.linesep)

def mitre_print (line,lemma,classification,rating):
    if classification == 'Normal_NP':
        recommendation = 'KEEP'
    elif classification == 'ABBREVIATION':
        classification = 'ABBREVIATION_OR_TERM_THAT_IS_ABBREVIATED'
        recommendation = 'KEEP'
    elif classification == 'SIMPLE':
        if rating == 'Good':
            recommendation = 'KEEP'
            classification = 'Out_of_Vocabulary_Word'
        elif rating == 'Medium':
            recommendation = 'REMOVE'
            classification = 'Common_Noun_Nominalization'
        else:
            recommendation = 'REMOVE'
            classification = 'Normal_Common_Noun_or_Number'
    elif classification == 'In_or_Out_of_Dictionary':
        recommendation = 'REMOVE'
        classification = 'Single_Word_Non_Noun'
    elif classification in ['contains_conjunction','too_many_verbs','unexpected_POS_sequence', 'bad_character','2_Part_NP','2_Part_NP_no_prep']:
        recommendation = 'REMOVE'
    elif classification in ['too_many_chunks','sequence_with_XP_chunk']:
        classification = 'unexpected_POS_sequence'
        recommendation = 'REMOVE'
    elif classification == 'verb+NP':
        recommendation = 'REMOVE'
        classification = 'Verbal or Sentential Structure'
    elif classification in ['NP+VP_ing','VP_ing+NP']:
        recommendation = 'REMOVE'
    else:
        print('unexpected -- need to debug:',classification)
        print(line)
        print(rating)
        recommendation = 'REMOVE'
    return('\t'.join([line,recommendation,classification])+os.linesep)
    
def cluster_and_filter_terms (infile,outfile,cluster_file,file_format='fact',\
                              abbrev_full_dict_file=False,full_abbrev_dict_file=False,\
                              mitre=False):
    global cluster_hash
    cluster_hash.clear()
    if full_abbrev_dict_file and abbrev_full_dict_file:
        read_in_full_to_abbreviation_dict(full_abbrev_dict_file,abbrev_full_dict_file)
    with open(infile) as instream,open(outfile,'w') as outstream:
        for line in instream:
            line = line.strip()
            line = re.sub('['+chr(147)+chr(148)+']','',line) ## fix for output of converting xls to csv
            if line != '':
                lemma,classification,rating,other_terms,chunks = term_classify(line,mitre=mitre)
##                if not rating:
##                    print(line)
##                    print(lemma)
##                    print(classification)
##                print('l',lemma,'c',classification,'r',rating,'t',other_terms)
##                input()
                if lemma in cluster_hash:
                    ## print('lem',lemma,'line',line,1)
                    cluster_hash[lemma].append(line)
                else:
                    ## print('lem',lemma,'line',line,2)
                    cluster_hash[lemma] = [line]
                if other_terms:
                    for term in other_terms:
                        if not term in cluster_hash[lemma]:
                            cluster_hash[lemma].append(term)
                if file_format == 'fact':
                    print_term_rating_fact(line,lemma,classification,rating, outstream)
                elif file_format == 'tuples':
                    outstream.write('\t'.join([line,lemma,classification,rating])+os.linesep)
                elif file_format == 'for_Mitre':
                    outstream.write(mitre_print(line,lemma,classification,rating))
                else:
                    print('Unknown file format',file_format)
                    return(False)
    keys = list(cluster_hash.keys())
    keys.sort()
    term_id_number = 0
    if cluster_file:
        with open(cluster_file,'w') as outstream:
            for key in keys:
                if file_format == 'fact':
                    print_term_set(outstream,key,cluster_hash[key])
                elif file_format == 'tuples':
                    outstream.write('\t'.join(cluster_hash[key])+os.linesep)
            
def ok_statistical_term(term,lenient=False):
    ## if single word, it should be a possible noun
    ##
    rating = False
    if len(term)==1:
        return(False,'1-character-term',False,rating)
    lemma,classification,rating,other_terms,chunks = term_classify(term)
    if (classification == 'Normal_NP') and (rating == 'Bad'):
        return(False,classification,chunks,rating)
    elif classification in ['Normal_NP','ABBREVIATION','NP+VP_ing','VP_ing+NP','2_Part_NP_no_prep']:
        return(True,classification,chunks,rating)
    elif classification in ['SIMPLE','HYPHENATION']:
        POS = guess_pos(term.lower(),term.istitle())
        if lenient and classification == 'SIMPLE':
            if rating != 'Good':
                rating = rating+'_but_top_term'
            return(True,classification,chunks,rating)
        elif rating !='Good':
            return(False,classification,chunks,rating)
        elif POS in ['NOUN','AMBIG_NOUN','PLURAL','AMBIG_PLURAL','NOUN_OOV']:
            return(True,classification,chunks,rating)
        elif classification == 'HYPHENATION':
            return(False,classification,chunks,rating)
        else:
            return(False,POS,chunks,rating)
    elif (classification == 'In_or_Out_of_Dictionary'): 
        POS = guess_pos(term.lower(),term.istitle())
    return(False,classification,chunks,rating)
            

# def record_statistical_terms_from_line(line):
#     line_list = line.split(' | ')
#     for term in line_list[:-1]:
#         ## last term is statistical score
#         if ok_statistical_term(term):
#             stat_term_dict[term] = True

# def read_in_statistical_term_list(infile,cutoff):
#     ## cutoffs
#     with open(infile) as instream:
#         lines = instream.readlines()
#         length_of_terms = round(cutoff*lines)
#         for line in lines[:length_of_terms]:
#             record_statistical_terms_from_line(line)

def large_prefix_overlap(term1,term2):
    small_length = min(len(term1),len(term2))
    sub_string_length = small_length//2
    answer = term1[:sub_string_length]==term2[:sub_string_length]
    return(answer)

def collapse_line_lists(lines):
    output = []
    last_line_list = False
    for line in lines:
        line_list = line.split('\t')
        # print(line_list)
        if last_line_list and (last_line_list[-1]==line_list[-1]) and large_prefix_overlap(last_line_list[0],line_list[0]):
            last_line_list.pop()
            last_line_list.extend(line_list)
        else:
            if last_line_list:
                output.append(last_line_list)
            last_line_list = line_list
    if last_line_list:
        output.append(last_line_list)
    ## print(output[:5])
    ## input()
    # print(output)
    return(output)

def make_stat_term_dictionary(infile,outfile,extrafile,cutoff2=.1,\
                              cutoff1=.00002,abbrev_full_dict_file=False,\
                              full_abbrev_dict_file=False,\
                              terms_on_separate_lines=False):
    if full_abbrev_dict_file and abbrev_full_dict_file:
        read_in_full_to_abbreviation_dict(full_abbrev_dict_file,abbrev_full_dict_file)
    with open(infile) as instream, open(outfile,'w') as outstream, open(extrafile,'w') as extrastream:
        lines = instream.readlines()
        # print(lines)
        if terms_on_separate_lines:
            line_lists = collapse_line_lists(lines)
        else:
            line_lists = []
            for line in lines:
                line_lists.append(line.split(' | '))
        lenient_simple_threshold = round(cutoff1*len(line_lists))
        length_of_terms = round(cutoff2*len(line_lists))
        num = 0
        # print(length_of_terms)
        for line_list in line_lists[:length_of_terms]:
            ## line_list = line.split(' | ')
            num = num+1
            for term in line_list[:-1]:              
                # print(term)
                keep,classification,chunks,rating = ok_statistical_term(term,lenient=(num < lenient_simple_threshold))
                rating = str(rating)
                if keep:
                    outstream.write(term+'\t'+'SIGNIFICANT_TERM'+'\t'+classification+'\t'+rating+os.linesep)
                else:
                    extrastream.write(term+'\t'+classification+'\t'+str(chunks)+'\t'+rating+os.linesep)
