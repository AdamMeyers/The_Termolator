'''
This is exactly the same file as term_utilities.py in the English system.
'''

import random
import os
import shutil
import re

DICT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + os.sep
## DICT_DIRECTORY = '../'
## DICT_DIRECTORY = './'
ORG_DICTIONARY = DICT_DIRECTORY+'org_dict.txt'
LOC_DICTIONARY = DICT_DIRECTORY+'location-lisp2-ugly.dict'
NAT_DICTIONARY = DICT_DIRECTORY+'nationalities.dict'
DISC_DICTIONARY = DICT_DIRECTORY+'discourse.dict'
TERM_REL_DICTIONARY = DICT_DIRECTORY+'term_relation.dict'
nom_file = DICT_DIRECTORY+'NOMLIST.dict'
pos_file = DICT_DIRECTORY+'POS.dict'
nom_map_file = DICT_DIRECTORY+'nom_map.dict'
person_name_file =  DICT_DIRECTORY+'person_name_list.dict'
nat_name_file =  DICT_DIRECTORY+'nationalities_name_list.dict'
skippable_adj_file = DICT_DIRECTORY+'out_adjectives.dict'
out_ing_file = DICT_DIRECTORY+'out_ing.dict'
time_name_file = DICT_DIRECTORY+'time_names.dict'
verb_morph_file = DICT_DIRECTORY+'verb-morph-2000.dict'
noun_morph_file = DICT_DIRECTORY+'noun-morph-2000.dict'

jargon_files = [DICT_DIRECTORY+'chemicals.dict',DICT_DIRECTORY+'more_jargon_words.dict']
dictionary_table = {'legal': DICT_DIRECTORY+'legal_dictionary.dict'}
special_domains = []

stat_adj_dict = {}
stat_term_dict = {}
noun_base_form_dict = {}
plural_dict = {}
verb_base_form_dict = {}
verb_variants_dict = {}
nom_dict = {} 
pos_dict = {}
jargon_words = set()
pos_offset_table = {}
organization_dictionary = {}
location_dictionary = {}
nationality_dictionary = {}
nom_map_dict = {}
unigram_dictionary = set()
## add all observed words (in the foreground set) to unigram_dictionary


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
                           'you','your','yours','me','my','mine','I','we','us','much','and/or'
                           ]
                           ## ABBREVIATION_STOP_WORDS plus some

patent_stop_words = ['patent','provisional','kokai','open','publication','number','nos','serial',\
                     'related','claim','claims','embodiment','related','present','priority','design',\
                     'said','respective','fig','figs','copyright','following','preceding','according',\
                         'barring','pending','pertaining','international','wo','pct']

signal_set=['academically', 'accordance', 'according', 'accordingly', 'actuality', 'actually', 'addition', 'additionally', 'administratively', 'admittedly', 'aesthetically', 'agreement', 'alarmingly', 'alas', 'all', 'allegedly', 'also', 'alternative', 'alternatively', 'although', 'altogether', 'amazingly', 'analogously', 'anyhow', 'anyway', 'anyways', 'apparently', 'appropriately', 'architecturally', 'arguably', 'arithmetically', 'artistically', 'as', 'assumingly', 'assuredly', 'astonishingly', 'astronomically', 'asymptotically', 'atypically', 'axiomatically', 'base', 'based', 'bases', 'basing', 'besides', 'biologically', 'but', 'case', 'certainly', 'coincidentally', 'colloquially', 'combination', 'combine', 'combined', 'combines', 'combining', 'commercially', 'compared', 'comparison', 'compliance', 'computationally', 'conceivably', 'conceptually', 'concord', 'concordance', 'confirm', 'confirmation', 'confirmed', 'confirming', 'confirms', 'conformity', 'consequence', 'consequentially', 'consequently', 'consistent', 'constitutionally', 'constrasts', 'contrarily', 'contrariwise', 'contrary', 'contrast', 'contrasted', 'contrasting', 'contrastingly', 'controversially', 'conversely', 'correlate', 'correlated', 'correlates', 'correlation', 'correspondingly', 'corroborate', 'corroborated', 'corroborates', 'corroborating', 'corroboration', 'couple', 'coupled', 'couples', 'coupling', 'course', 'curiously', 'definitely', 'described', 'descriptively', 'despite', 'done', 'doubtless', 'doubtlessly', 'due', 'ecologically', 'economically', 'effect', 'effectively', 'else', 'empirically', 'endorse', 'endorsed', 'endorsement', 'endorses', 'environmentally', 'ethically', 'event', 'eventually', 'evidently', 'example', 'excitingly', 'extend', 'extended', 'extending', 'extends', 'extension', 'fact', 'factually', 'far', 'fifthly', 'finally', 'first', 'firstly', 'following', 'formally', 'fortunately', 'fourth', 'fourthly', 'frankly', 'further', 'furthermore', 'genealogically', 'general', 'generally', 'genetically', 'geographically', 'geologically', 'geometrically', 'grammatically', 'gratuitously', 'hand', 'hence', 'historically', 'honestly', 'honesty', 'hopefully', 'however', 'ideally', 'implement', 'implementation', 'implemented', 'implementing', 'implements', 'incidentally', 'increasingly', 'indeed', 'indubitably', 'inevitably', 'informally', 'instance', 'instead', 'institutionally', 'interestingly', 'intriguingly', 'invoke', 'invoked', 'invokes', 'invoking', 'ironically', 'journalistically', 'lamentably', 'last', 'lastly', 'legally', 'lest', 'light', 'likelihood', 'likewise', 'line', 'linguistically', 'literally', 'logically', 'luckily', 'lyrically', 'manner', 'materialistically', 'mathematically', 'meantime', 'meanwhile', 'mechanically', 'mechanistically', 'medically', 'melodramatically', 'merge', 'merged', 'merges', 'merging', 'metaphorically', 'metaphysically', 'methodologically', 'metrically', 'militarily', 'ministerially', 'miraculously', 'mix', 'mixed', 'mixes', 'mixing', 'mixture', 'modestly', 'morally', 'moreover', 'morphologically', 'mundanely', 'musically', 'mutandis', 'mutatis', 'naturally', 'nay', 'necessarily', 'needfully', 'nevertheless', 'next', 'nonetheless', 'normally', 'not', 'notwithstanding', 'now', 'numerically', 'nutritionally', 'objectionably', 'obscenely', 'observably', 'obviously', 'oddly', 'odds-on', 'of', 'offhand', 'officially', 'ominously', 'optimally', 'optimistically', 'ordinarily', 'originally', 'ostensibly', 'otherwise', 'overall', 'paradoxically', 'parenthetically', 'particular', 'peculiarly', 'perceptively', 'perchance', 'personally', 'perversely', 'pessimistically', 'pettily', 'pharmacologically', 'philanthropically', 'philosophically', 'phonetically', 'photographically', 'physically', 'plausibly', 'poetically', 'politically', 'possibly', 'potentially', 'practically', 'pragmatically', 'predictably', 'preferably', 'presumably', 'presumptively', 'probabilistically', 'probability', 'probably', 'problematically', 'professedly', 'propitiously', 'rashly', 'rate', 'rather', 'rationally', 'realistically', 'really', 'reference', 'regardless', 'regretfully', 'regrettably', 'reportedly', 'reputedly', 'result', 'retrospectively', 'rhetorically', 'ridiculously', 'roughly', 'sceptically', 'scientifically', 'second', 'secondly', 'separately', 'seriously', 'shockingly', 'similar', 'similarly', 'simultaneously', 'somehow', 'speaking', 'specifically', 'statistically', 'still', 'strangely', 'strikingly', 'subsequently', 'superficially', 'superstitiously', 'support', 'supported', 'supporting', 'supports', 'supposedly', 'surely', 'surprisingly', 'symbolically', 'tactically', 'take', 'taken', 'takes', 'taking', 'technically', 'thankfully', 'thanks', 'then', 'thence', 'theologically', 'theoretically', 'thereafter', 'therefore', 'third', 'thirdly', 'though', 'thus', 'time', 'took', 'touchingly', 'traditionally', 'tragically', 'trivially', 'truly', 'truth', 'truthfully', 'ultimately', 'unaccountably', 'unarguably', 'undeniably', 'understandably', 'undisputedly', 'undoubtedly', 'unexpectedly', 'unfortunately', 'unsurprisingly', 'use', 'used', 'uses', 'using', 'usually', 'utilization', 'utilize', 'utilized', 'utilizes', 'utilizing', 'verily', 'view', 'way', 'whence', 'whereas', 'whereby', 'wherefore', 'wherein', 'whereof', 'whereon', 'whereto', 'whereunto', 'whereupon', 'while', 'withal', 'worryingly', 'yet']

## ne_stop_words = ['et', 'co', 'al', 'eds','corp','inc','sa','cia','ltd','GmbH','Esq','PhD']

NE_stop_words = ['eds','publications?','et', 'co', 'al', 'eds','corp','inc','sa','cia','ltd','gmbh','esq','phd','natl','acad','sci','proc','chem','soc']

ARG1_NAME_TABLE ={'EXEMPLIFY':'SUBCLASS','DISCOVER':'INVENTOR','MANUFACTURE':'MAKER','SUPPLY':'SUPPLIER',\
                      'ORIGINATE':'INVENTOR','ALIAS':'FULLNAME','ABBREVIATE':'FULLNAME','BETTER_THAN':'BETTER',\
                      'BASED_ON':'DERIVED','CONTRAST':'THEME','CORROBORATION':'THEME','CO-CITATION':'THEME',\
                      'POSITIVE':'JUDGE','NEGATIVE':'JUDGE','SIGNIFICANT':'JUDGE','PRACTICAL':'JUDGE','STANDARD':'JUDGE','EMPHASIZED_TERM':'THEME','COMPONENT':'PART','FEATURE':'FEATURE'}
                      
ARG2_NAME_TABLE ={'EXEMPLIFY':'SUPERCLASS','DISCOVER':'INVENTION','MANUFACTURE':'PRODUCT','SUPPLY':'PRODUCT',\
                      'ORIGINATE':'INVENTION','ALIAS':'FULLNAME','ABBREVIATE':'SHORTNAME','BETTER_THAN':'WORSE',\
                      'BASED_ON':'ORIGINAL','CONTRAST':'THEME','CORROBORATION':'THEME','CO-CITATION':'THEME',\
                      'POSITIVE':'THEME','NEGATIVE':'THEME','SIGNIFICANT':'THEME','PRACTICAL':'THEME','STANDARD':'THEME','EMPHASIZED_TERM':'THEME','COMPONENT':'WHOLE','FEATURE':'BEARER'}

attribute_value_from_fact = re.compile(r'([A-Z0-9_]+) *[=] *((["][^"]*["])|([0-9]+))',re.I)

person_ending_pattern = re.compile(' (Esq|PhD|Jr|snr)\.?$',re.I)

org_ending_pattern = re.compile(' (corp|inc|sa|cia|ltd|gmbh|co)\.?$',re.I)

closed_class_words2 = r'and|or|as|the|a|of|for|at|on|in|by|into|onto|to|per|plus|through|till|towards?|under|until|via|with|within|without|no|any|each|that|there|et|al'
closed_class_check2 = re.compile('^('+closed_class_words2+')$',re.I)

organization_word_pattern = re.compile(r'^(AGENC(Y|IE)|ASSOCIATION|BUREAU|CENT(ER|RE|RO)|COLL[EÈ]GE|COMMISSION|CORP[\.]|CORPORATION|COUNCIL|DEPARTMENT|ENDOWMENT|FOUNDATION|FUND|GROUP|HOSPITAL|(INC|SA|CIA|LTD|CORP|GMBH|CO)\.?|IN?STITUT[EO]?|LABORATOR((Y)|IE)|OFFICE|ORGANI[SZ]ATION|PARTNER|PROGRAMME|PROGRAM|PROJECT|SCHOOL|SOCIET(Y|IE)|TRUST|(UNIVERSI[TD](AD)?(E|É|Y|IE|À|ÄT)?)|UNIVERSITÄTSKLINIKUM|UNIVERSITÄTSSPITAL)S?$',re.I)

last_word_organization = re.compile(r'^(AGENC(Y|IE)|ASSOCIATION|CENT(ER|RE|RO)|COLL[EÈ]GE|COMMISSION|CORP[\.]|CORPORATION|COUNCIL|DEPARTMENT|ENDOWMENT|FOUNDATION|FUND|GROUP|HOSPITAL|(INC|SA|CIA|LTD|CORP|GMBH|CO)\.?|IN?STITUT[EO]?|LABORATOR((Y)|IE)|OFFICE|ORGANI[SZ]ATION|PARTNER|PROGRAMME|PROGRAM|PROJECT|SCHOOL|SOCIET(Y|IE)|TRUST|(UNIVERSI[TD](AD)?(E|É|Y|IE|À|ÄT)?)|UNIVERSITÄTSKLINIKUM|UNIVERSITÄTSSPITAL|INDUSTRIE|PRESS|SOLUTIONS|TELECOMMUNICATIONS|TECHNOLOGIE|PHARMACEUTICAL|CHEMICAL|BIOSCIENCE|BIOSYSTEM|BIOTECHNOLOG(Y|IE)|INSTRUMENT|SYSTEMS|COMPANY|INST|RES|ABSTRACTS|ASSOC(ITATES)?|SCIENTIFICA|UNION)S?$',re.I)

ambig_last_word_org = re.compile(r'^(PROGRAM|SYSTEM)S?$',re.I)

last_word_gpe = re.compile(r'(HEIGHTS?|MASS|TOWNSHIP|PARK)$',re.I)

last_word_loc = re.compile(r'(STREET|AVENUE|BOULEVARD|LANE|PLACE)$',re.I)

xml_pattern = re.compile(r'<([/!?]?)([a-z?\-]+)[^>]*>',re.I)

xml_string = '<([/!?]?)([a-z?\-]+)[^>]*>'

## abbreviate patterns -- the b patterns ignore square brackets
global parentheses_pattern2
global parentheses_pattern3
parentheses_pattern2a = re.compile(r'[(\[]([ \t]*)([^)\]]*)([)\]]|$)')
parentheses_pattern3a = re.compile(r'(\s|^)[(\[]([^)\]]*)([)\]]|$)([^a-zA-Z0-9-]|$)')
parentheses_pattern2b = re.compile(r'[(]([ \t]*)([^)]*)([)]|$)')   
parentheses_pattern3b = re.compile(r'(\s|^)[(]([^)]*)([)\]]|$)([^a-zA-Z0-9-]|$)')


html_fields_to_remove = ['style','script']

text_html_fields = ['p','h1','h2','h3','h4','h5','h6','li','dt','dd','address','pre','td','caption','br']
## some of these may require additional formatting to properly process them, e.g., 
## the following (not implemented) may require additional new lines: address, pre

roman_value = {'i':1,'v':5,'x':10,'l':50,'c':100,'d':500,'m':1000}

def ok_roman_bigram (pair):
    if pair in ['ii','iv','ix','vi','xi','xv','xx','xl','xc','li','lv','lx','ci','cv','cx','cl','cc','cd','cm','mi','mv','mx','ml','mc','md','mm']:
        return(True)
    else:
        return(False)

def OK_roman_trigram(triple):
    if triple in ['ivi','ixi','xlx','xcx','cdc','cmc']:
        return(False)
    else:
        return(True)

def roman (string):
    lower = string.lower()
    if (type(lower) == str) and re.search('^[ivxlcdm]+$',lower):
        ## lower consists completely of correct characters (unigram)
        ## now check bigrams
        result = True
        for position in range(len(lower)):
            if ((position == 0) or ok_roman_bigram(lower[position-1:position+1])) and \
                    ((position < 2) or OK_roman_trigram(lower[position-2:position+1])):
                pass
            else:
                result = False
        return(result)
    else:
        return(False)


def evaluate_roman (string):
    total = 0
    value_list = []
    for character in string:
        value_list.append(roman_value[character.lower()])
    last = value_list[0]
    for number in value_list[1:]:
        if last and (last < number):
            total = total + (number - last)
            last = False
        elif last and (last >= number):
            total = total + last
            last = number
        else:
            last = number
    if last != 100000000:
        total = total + last
    return(total)


def return_stray_colons(string):
    return(string.replace('-colon-',':'))

def fix_stray_colons (string):
    position = string.find(':')
    if position == -1:
        output = string
    elif position == 0 or string[position + 1] != ' ':
        border = 1 + position
        output = string[:border]+fix_stray_colons(string[border:])
    else:
        border = 1 + position
        output = string[:position]+'-colon-'+fix_stray_colons(string[border:])
    return(output)

def is_lisp_key_word (string):
    return(string[0] == ':')

def list_starter (string):
    return(string[0] == '(')

def list_ender (string):
    return(string[-1] == ')')

def string_starter (string):
    return(string[0] == '"')

def string_ender (string):
    return(string[-1] == '"')

def process_lexicon_list(value):
    output = []
    value = value.strip('()')
    if '"' in value:
        value_list = value.split('"')
    else:
        value_list = value.split(' ')
    if "" in value_list:
        value_list.remove('')
    for item in value_list:
        item = item.strip(' ')
        if item != '':
            output.append(item)
    return(output)

def get_key_value (string):
    initial_list = string.partition(' ')
    key = initial_list[0]
    value = initial_list[2].strip(' ')
    if list_starter(value):
        if list_ender(value):
            value = process_lexicon_list(value)
        else:
            print('string',string)
            print('value',value)
            raise Exception('Current Program cannot handle recursive structures')
    elif string_starter(value) and string_ender(value):
        value = value.strip('"')
    return (key, value)


def add_dictionary_entry(line,dictionary,shallow,lower=False,patent=False):
    clean_line = line.strip(os.linesep+'(\t')
    if clean_line[-1] == ")":
        clean_line = clean_line[:-1]
    clean_line = fix_stray_colons(clean_line)
    line_list = clean_line.split(':')
    for index in range(len(line_list)):
        line_list[index] = return_stray_colons(line_list[index])
    entry_type = line_list[0].strip(' ')
    entry_dict = {}
    current_key = False
    current_value = False
    started_string = False
    for key_value in line_list[1:]:
        key_value = key_value.strip(' ')
        key_value = get_key_value(key_value)
        key = key_value[0]
        value = key_value[1]
        entry_dict[key] = value
    if dictionary == 'org':
        if lower:
            orth = entry_dict['ORTH'].lower()
        else:
            orth = entry_dict['ORTH'].upper()
        organization_dictionary[orth] = entry_dict  
    elif dictionary == 'loc':
        if lower:
            orth = entry_dict['ORTH'].lower()
        else:
            orth = entry_dict['ORTH'].upper()
        location_dictionary[orth] = entry_dict
    elif dictionary =='nat':
        if lower:
            orth = entry_dict['ORTH'].lower()
        else:
            orth = entry_dict['ORTH'].upper()
        nationality_dictionary[orth] = entry_dict
    elif dictionary in ['discourse', 'term_relation']:
        if dictionary == 'discourse':
            actual_dict = discourse_dictionary
        else:
            actual_dict = term_rel_dictionary
        if shallow and ('SHALLOW_LOW_CONF' in entry_dict):
            pass
        elif ('PATENT_ONLY' in entry_dict) and (not patent):
            pass
        elif ('ARTICLE_ONLY' in entry_dict) and patent:
            pass
        elif 'FORMS' in entry_dict:
            forms = entry_dict['FORMS']
            entry_dict.pop('FORMS')
            word = entry_dict.pop('ORTH')
            word = word.lower()
            for num in range(len(forms)):
                forms[num] = forms[num].lower()
            for form in forms:
                new_entry = entry_dict.copy()
                new_entry['ORTH']=form
                form = form.upper()
                if form in actual_dict:
                    actual_dict[form].append(new_entry)
                else:
                    actual_dict[form]=[new_entry]
        elif entry_dict['ORTH'].upper() in actual_dict:
            actual_dict[entry_dict['ORTH'].upper()].append(entry_dict)
        else:    
            actual_dict[entry_dict['ORTH'].upper()] = [entry_dict]

def read_in_org_dictionary(dict_file,dictionary='org',shallow=True,lower=False,patent=False):
    if dictionary == 'org':
        organization_dictionary.clear()
    elif dictionary == 'loc':
        location_dictionary.clear()
    elif dictionary == 'nat':
        nationality_dictionary.clear()
    elif dictionary == 'discourse':
        discourse_dictionary.clear()
    elif dictionary == 'term_relation':
        term_rel_dictionary.clear()
    with open(dict_file,'r') as instream:
        for line in instream:
            add_dictionary_entry(line,dictionary,shallow,lower=lower,patent=patent)

def read_in_nom_map_dict (infile=nom_map_file):
    global nom_map_dict
    for line in open(infile).readlines():
        word,nominalization = line.strip().split('\t')
        nom_map_dict[word]=nominalization

def read_in_noun_morph_file (infile=noun_morph_file):
    global noun_base_form_dict
    global plural_dict
    plural_dict.clear()
    noun_base_form_dict.clear()
    for line in open(infile).readlines():
        line_entry = line.strip().split('\t')
        word = line_entry[0]
        base = line_entry[1]
        if (word in noun_base_form_dict):
            if not (base in noun_base_form_dict[word]):
                noun_base_form_dict[word].append(base)
        else:
            noun_base_form_dict[word]=[base]
    for word in noun_base_form_dict:
        if not (word in noun_base_form_dict[word]):
            for base_form in noun_base_form_dict[word]:
                if base_form in plural_dict:
                    plural_dict[base_form].append(word)
                else:
                    plural_dict[base_form] = [word]
                    
def read_in_verb_morph_file(infile=verb_morph_file):
    global verb_base_form_dict
    global verb_variants_dict
    verb_base_form_dict.clear()
    verb_variants_dict.clear()
    for line in open(infile).readlines():
        line_entry = line.strip().split('\t')
        word = line_entry[0]
        base = line_entry[1]
        if (word in verb_base_form_dict):
            verb_base_form_dict[word].append(base)
        else:
            verb_base_form_dict[word]=[base]
    for word in verb_base_form_dict:
        for base_form in verb_base_form_dict[word]:
            if base_form in verb_variants_dict:
                verb_variants_dict[base_form].append(word)
            else:
                verb_variants_dict[base_form] = [word]

def read_in_pos_file (infile=pos_file):
    global pos_dict
    pos_dict.clear()
    for line in open(infile).readlines():
        line = line.strip()
        items = line.split('\t')
        pos_dict[items[0]]=items[1:]
    for dictionary in special_domains:
        jargon_files.append(dictionary_table[dictionary])
    for jargon_file in jargon_files:
        ## remove jargon from dictionary
        with open(jargon_file) as instream:
            for line in instream.readlines():
                word = line.strip()
                word = word.lower()
                if word in pos_dict:
                    ## pos_dict.pop(word)
                    jargon_words.add(word)

def update_pos_dict (name_infiles=[person_name_file,nat_name_file],other_infiles=[skippable_adj_file,out_ing_file,time_name_file]):
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
    for word in NE_stop_words:
        pos_dict[word]=['OTHER']

def read_in_nom_dict (infile=nom_file):
    global nom_dict
    for line in open(infile).readlines():
        nom_class,word = line.strip().split('\t')
        if word in nom_dict:
            nom_dict[word].append(nom_class)
        else:
            nom_dict[word] = [nom_class]

def initialize_utilities():
    global parentheses_pattern2
    global parentheses_pattern3
    read_in_pos_file()
    update_pos_dict()
    read_in_org_dictionary(ORG_DICTIONARY,dictionary='org',lower=True)
    read_in_org_dictionary(LOC_DICTIONARY,dictionary='loc',lower=True)
    read_in_nom_map_dict()
    read_in_verb_morph_file()
    read_in_noun_morph_file()
    read_in_nom_dict()
    if 'legal' in special_domains:
        parentheses_pattern2 = parentheses_pattern2b
        parentheses_pattern3 = parentheses_pattern3b
    else:
        parentheses_pattern2 = parentheses_pattern2a
        parentheses_pattern3 = parentheses_pattern3a

def parentheses_pattern_match(instring,start,pattern_number):
    if 'legal' in special_domains:
        if pattern_number == 2:
            return(parentheses_pattern2b.search(instring,start))
        else:
            return(parentheses_pattern3b.search(instring,start))
    else:
        if pattern_number == 2:
            return(parentheses_pattern2a.search(instring,start))
        else:
            return(parentheses_pattern3a.search(instring,start))

def breakup_line_into_chunks(inline,difference):
    size = 1000
    start = 0
    if difference == 0:
        ## this seems to happen sometimes
        ## perhaps this is the case where
        ## the current filters do not 
        ## detect good break points
        return([inline])
    output = []
    while start < len(inline):
        end = start + size
        if end>=len(inline):
            output.append(inline[start:])
        else:
            output.append(inline[start:end-difference])
            start = end
    return(output)

def table_upper_split(line):
    ## in order to maintain offsets this program will delete
    ## one non-alphanumeric character or upper case character
    ## per new line created
    ## since other programs assume a newline character between
    ## lines.
    difference = 0 
    table_pattern = re.compile('[^a-zA-Z0-9]TABLE[^a-zA-Z0-9]')
    end_table_pattern = re.compile('[A-Za-z][a-z]')
    table_start = table_pattern.search(line)
    output = []
    start = 0
    if not table_start:
        return([line])
    while table_start:
        output.append(line[start:table_start.start()-difference])
        end_table = end_table_pattern.search(line,table_start.end())
        if end_table:
            output.append(line[table_start.start()+difference:end_table.start()])
            start = end_table.start()
            table_start = table_pattern.search(line,start)
        else:
            output.append(line[start:])
            start = len(line)
            table_start=False
    output2 = []
    if start < len(line):
        output.append(line[start:])
    for out in output:
        if len(out)<3000:
            output2.append(out)
        else:
            output2.extend(breakup_line_into_chunks(out,difference))
    return(output2)
    
def long_line_split(input_line):
    ## really long lines can be problematic
    ## one case we found is inserted tables
    ## we will start with these.
    ## if we find more cases, this
    ## function can increase in complexity
    if len(input_line)<2000:
        return([input_line])
    else:
        return(table_upper_split(input_line))

def remove_xml(string):
    output = xml_pattern.sub('',string)
    return(output)

def clean_string_of_ampersand_characters(string):
    ampersand_char_pattern = re.compile('&[^;]+;')
    ampersand_char_pattern2 = re.compile('&[^;<]+[<]')
    match = ampersand_char_pattern.search(string)
    if not match:
        match = ampersand_char_pattern2.search(string)
    while match:
        if match.group(0).endswith('<'):
            string = string[:match.start()]+(len(match.group(0))-1)*' '+string[match.end()-1:]
        else:
            string = string[:match.start()]+len(match.group(0))*' '+string[match.end():]
        match = ampersand_char_pattern.search(string)
        if not match:
            match = ampersand_char_pattern2.search(string)
    return(string)

def remove_xml_spit_out_paragraph_start_end(string,offset):
    string = clean_string_of_ampersand_characters(string)
    next_xml = xml_pattern.search(string)
    start = 0
    out_string = ''
    bare_string_border = 0
    paragraph_starts = []
    paragraph_ends = []
    remove_starts = []
    remove_ends = []
    while next_xml:
        out_string = out_string + string[start:next_xml.start()]
        if next_xml.group(2).lower() in text_html_fields:
            if next_xml.group(1) == '/':
                paragraph_ends.append(len(out_string)+offset)
            else:
                paragraph_starts.append(len(out_string)+offset)
        elif next_xml.group(2).lower() in html_fields_to_remove:
            if next_xml.group(1) == '/':
                remove_ends.append(len(out_string)+offset)
            else:
                remove_starts.append(len(out_string)+offset)
        start = next_xml.end()
        next_xml = xml_pattern.search(string,start)
    out_string = out_string + string[start:]
    return(out_string,paragraph_starts,paragraph_ends,remove_starts,remove_ends)

def replace_less_than_with_positions(string,offset):
    out_string = ''
    num = 0
    less_thans = []
    length = len(string)
    for char in string:
        if char == '<':
            start = num+offset
            if (num<(length-1)) and (string[num+1] == ' '):
                plus = 2
            else:
                plus = 1
            less_thans.append([num+offset,num+offset+plus])
            out_string = out_string + ' '
        else:
            out_string = out_string + char
        num = num + 1
    return(out_string,less_thans)

def interior_white_space_trim(instring):
    out1 = re.sub('\s+',' ',instring)
    out2 = re.sub('\s*(.*[^\s])\s*$','\g<1>',out1)
    return(out2)

def isStub(line):
    if (len(line)<1000) and re.search('[\(\[][ \t]*$',line):
        return(True)

def get_lines_from_file(infile):
    with open(infile,'r') as instream:
        output = []
        short_line = False
        for line in (instream.readlines()):
            line = remove_xml(line)
            if short_line:
                line = short_line+line
            if isStub(line):
                short_line = re.sub(os.linesep,' ',line)
            else:
                short_line = False
                for line2 in long_line_split(line):
                    output.append(line2)
        if short_line:
            output.append(short_line)
        return(output)

def load_pos_offset_table(pos_file):
    global  pos_offset_table
    pos_offset_table.clear()
    if os.path.isfile(pos_file):
        with open(pos_file) as instream:
            for line in instream.readlines():
                line_info = line.rstrip().split(' ||| ')
                start_end = line_info[1]
                start_end_strings = start_end.split(' ')
                start = int(start_end_strings[0][2:])
                pos = line_info[2]
                pos_offset_table[start] = pos

def citation_number(word):
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


def resolve_differences_with_pos_tagger(word,offset,dict_pos,tagger_pos):
    if (tagger_pos == 'ADJECTIVE') and ('ORDINAL' in dict_pos):
        return(['ORDINAL'])
    elif (tagger_pos == 'ADJECTIVE') and ('SKIPABLE_ADJ' in dict_pos):
        return(['SKIPABLE_ADJ'])
    elif (tagger_pos == 'ADJECTIVE') and ('NATIONALITY' in dict_pos):
        return(['NATIONALITY_ADJ'])
    elif (tagger_pos in ['ADJECTIVE','NOUN']) and \
         (word.endswith('ing') or word.endswith('ed')):
        return([tagger_pos])
    elif (tagger_pos == 'VERB') and dict_pos and (not 'VERB' in dict_pos):
        return(dict_pos)
    elif tagger_pos in dict_pos:
        return([tagger_pos])
    elif (tagger_pos == 'OTHER'):
        if ('AUX' in dict_pos) or ('WORD' in dict_pos) or \
          ('CCONJ' in dict_pos) or ('PRONOUN' in dict_pos) or \
          ('TITLE' in dict_pos) or ('SCONJ' in dict_pos) or \
          ('ADVERB' in dict_pos):
            return(['WORD'])
        else:
            return(dict_pos)
    elif ('NATIONALITY' in dict_pos) and (tagger_pos == 'NOUN'):
        return('NOUN')
    elif (tagger_pos == 'NOUN') and ('NOUN_OOV' in dict_pos):
        return (['NOUN_OOV'])
    else:
        return(dict_pos)

def closed_class_conflict(word):
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


def read_in_stat_term_dict (indict,dict_dir=DICT_DIRECTORY):
    global stat_term_dict
    global stat_adj_dict
    stat_term_dict.clear()
    stat_adj_dict.clear()
    with open(dict_dir+indict) as instream:
        for line in instream.readlines():
            line_entry = line.strip().split('\t')
            stat_term_dict[line_entry[0]] = True
            if ' ' in line_entry[0]:
                position = line_entry[0].index(' ')
                first_word = line_entry[0][:position].lower()
            else:
                first_word = line_entry[0].lower()
            pos = guess_pos(first_word,False)
            if pos in ['ADJECTIVE','SKIPABLE_ADJ','TECH_ADJECTIVE']:
                if not first_word in stat_adj_dict:
                    stat_adj_dict[first_word] = 1
                else:
                    stat_adj_dict[first_word] = stat_adj_dict[first_word]+1
    adj_threshold = 5 ## not sure what this number should be
    for key in list(stat_adj_dict.keys()):
        if stat_adj_dict[key]<adj_threshold:
            stat_adj_dict.pop(key)

def nom_class(word,pos):
    if word in ['invention','inventions']:
        return(0)
    ## invention (patents) is usually a self-citation and we want to
    ## downgrade its score
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

def term_dict_check(term,test_dict):
    if term in test_dict:
        return(True)
    elif ('-' in term):
        pat = re.search('-([^-]+)$',term)
        if pat and pat.group(1) in test_dict:
            return(True)
        
def guess_pos(word,is_capital,offset=False,case_neutral=False):
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
        elif tagger_pos == 'POS':
            pass
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
            pos = resolve_differences_with_pos_tagger(word,offset,pos,tagger_pos)
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
            elif (('SKIPABLE_ADJ' in pos) or ('ORDINAL' in pos)) and (not term_dict_check(word.lower(),stat_adj_dict)):
                return('SKIPABLE_ADJ')
            elif (('NOUN' in pos) or ('NOUN_OOV' in pos)) and not closed_class_conflict(word):
                if possessive:
                    return('AMBIG_POSSESS')
                elif (len(word)>1) and (word[-1] == 's') and (word in noun_base_form_dict) and (not (word in noun_base_form_dict[word])):
                    return('AMBIG_PLURAL')
                else:
                    return('AMBIG_NOUN')
            elif 'VERB' in pos:
                return('AMBIG_VERB')
            elif 'ADJECTIVE' in pos:
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
            elif (('SKIPABLE_ADJ' in pos) or ('ORDINAL' in pos)) and not (term_dict_check(word.lower(),stat_adj_dict)):
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
        if len(little_words)>2:
            for word in little_words:
                little_pos = guess_pos(word,word.istitle())
                if little_pos == 'NOUN_OOV':
                    return('NOUN_OOV')
            return('NOUN')
        if len(little_words)==1 and (little_words[0].isalnum()):
            return(guess_pos(little_words[0]),is_capital)
        if little_words[1] in pos_dict: ## the last word
            last_pos = pos_dict[little_words[1]][:]
            first_pos = guess_pos(little_words[0],little_words[0].istitle())
            first_word = little_words[0].lower()
            if first_pos == 'NOUN_OOV':
                return('NOUN_OOV')
            if 'ADVPART' in last_pos:
                return('SKIPABLE_ADJ')
            if 'NOUN' in last_pos:
                if (len(word)>2) and (word[-1] == 's') and (not word[-2] in "aiousc"):
                    return('PLURAL')
                elif word[0].isnumeric():
                    return('ADJECTIVE')
                    ## treat like adjective, like PTB, also to rule out
                else:
                    return('NOUN')
            elif 'PERSON_NAME' in last_pos:
                return('NOUN')
            elif 'SKIPABLE_ADJ' in pos:
                if term_dict_check(word.lower(),stat_adj_dict):
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
                elif 'NOUN' in last_pos:
                    return('NOUN')
                else:
                    return('ADJECTIVE')
            else:
                return('OTHER')
        elif (len(word)>2) and (word[-1] == 's') and (not word[-2] in "aiousc"):
            return('PLURAL')
        else:
            return('NOUN')
    elif (tagger_pos == 'POS') or ((not tagger_pos) and (word in ["'s","'S"])):
        ## if there is no POS tagger, do not try to find verb cases of "'s"
        return('POS')
    elif tagger_pos in ['ADVERB','VERB']:
        return(tagger_pos)
    elif (tagger_pos in ['ADJECTIVE']):
        ### added at the same time as adding jargon terms
        return('TECH_ADJECTIVE')
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
    elif (case_neutral or is_capital) and (len(word)<6):
        if ((word.title() in pos_dict) and ('TITLE' in pos_dict[word.title()])) or \
          (((word.title()+ '.') in pos_dict) and ('TITLE' in pos_dict[word.title()+'.'])):
            return('OTHER')
        else:
            return('NOUN_OOV')
    else:
        return('NOUN_OOV')
        ## otherwise assume most OOV words are nouns

def divide_sentence_into_words_and_start_positions (sentence,start=0):
    ## only sequences of letters are needed for look up
    break_pattern = re.compile('[^0-9A-Za-z-]')
    match = break_pattern.search(sentence,start)
    output = []
    while match:
        if start !=match.start():
            output.append([start,sentence[start:match.start()]])
        start = match.end()
        match = break_pattern.search(sentence,start)
    if start < len(sentence):
        output.append([start,sentence[start:]])
    return(output)

def list_intersect(list1,list2):
    for item1 in list1:
        for item2 in list2:
            if item1 == item2:
                return(True)

def get_integrated_line_attribute_value_structure_no_list(line,types):  
    start = line.find(' ')
    if start != -1:
        av_type = line[:start]
        output = {}
    else:
        output = False
        av_type = False
    if av_type in types:
        pattern = attribute_value_from_fact.search(line,start)
        output['av_type']=av_type
        while pattern:
            output[pattern.group(1)]=pattern.group(2).strip('"')
            start = pattern.end()
            pattern = attribute_value_from_fact.search(line,start)      
    return(output)

def derive_plurals(word):
    ## the dictionary plurals, actually includes -ing forms of verbs as well
    ## and regularizes them to verbs (which may or may not also be nouns)
    if word in plural_dict:
        return(plural_dict[word])
    elif len(word) <= 1:
        return(False)
    elif (word[-1] in 'sxz') or (word[-2:] in ['sh', 'ch']):
        output = word+'es'
    elif (word[-1] == 'y') and not(word[-2] in 'aeiou'):
        output = word[:-1]+'ies'
    else:
        output = word+'s'
    return([output])
    ## for more stringent use of plurals, add optional variable unigram_check
    ## and set it to True, uncomment the following line and all other unigram references
    # if (not unigram_check) or (output.lower() in unigram_dictionary):
    #     return([output])

def increment_unigram_dict_from_lines(lines):
    for line in lines:
        words = re.split('[^a-zA-Z]',line)
        for word in words:
            if word != '':
                unigram_dictionary.add(word.lower())

def save_unigram_dict(outfile):
    global unigram_dictionary    
    with open(outfile,'w') as outstream:
        for word in unigram_dictionary:
            outstream.write(word+os.linesep)

def load_unigram_dict(infile):
    global unigram_dictionary
    unigram_dictionary.clear()
    with open(infile) as instream:
        for line in instream:
            unigram_dictionary.add(line.strip())

def get_n_random_lines (infile,outfile,N):
    random.seed()
    lines = open(infile).readlines()
    output = []
    while (len(output) < N) and (len(lines)>0):
        new_num = random.randint(0,len(lines)-1)
        output.append(lines.pop(new_num))
    with open(outfile,'w') as outstream:
        for line in output:
            outstream.write(line)

def merge_multiline_and_fix_xml (inlinelist):
    outlinelist = []
    current_line = ''
    start_xml = re.compile('^[ \t]*<')
    for line in inlinelist:
        if start_xml.search(line) and (not '>' in line):
            current_line = current_line+line
        elif (current_line != ''):
            if ('>' in line):
                outlinelist.append(current_line+line)
                current_line = ''
            else:
                current_line = current_line + line
        else:
            outlinelist.append(line)
    if (current_line != ''):
        outlinelist.append(line)            
    return(outlinelist)

def get_my_string_list(input_file):
    try:
        instream = open(input_file)
        output = instream.readlines()
    except:
        instream = open(input_file,encoding='ISO-8859-1')
        output = instream.readlines()
    return(output)
    
    
    
