import os
import re
import random
from nyu_utilities import *

DICT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + os.sep
## DICT_DIRECTORY = '''/home/meyers/FUSE/Python-Scripts/'''
pos_file = DICT_DIRECTORY+'POS.dict'
pos_dict = {}
garbage_count = 0
full_to_abbreviation_dict = {}
abbreviation_to_full_form = {}

ABBREVIATION_STOP_WORDS = ['a','the','an','and','or','but','about','above','after','along','amid','among',\
                           'as','at','by','for','from','in','into','like','minus','near','of','off','on',\
                           'onto','out','over','past','per','plus','since','till','to','under','until','up',\
                           'via','vs','with','that']
## from abbreviate3.py

read_in_noun_morph_file()

def read_in_pos_file (infile=pos_file):
    global pos_dict
    pos_dict.clear()
    for line in open(infile).readlines():
        line = line.strip()
        items = line.split('\t')
        pos_dict[items[0]]=items[1:]

read_in_pos_file()

def read_in_full_to_abbreviation_dict(f_to_a_file,a_to_f_file,dict_directory=DICT_DIRECTORY):
    global full_to_abbreviation_dict
    global abbreviation_to_full_form
    full_to_abbreviation_dict.clear()
    abbreviation_to_full_form.clear()
    with open(dict_directory+f_to_a_file) as instream:
        for line in instream:
            line = line.strip()
            items = line.split('\t')
            full_to_abbreviation_dict[items[0]] = items[1:]
    with open(dict_directory+a_to_f_file) as instream:
        for line in instream:
            line = line.strip()
            items = line.split('\t')
            abbreviation_to_full_form[items[0]] = items[1:]

def make_simple_abbreviations(words):
    ## note that these do not include the type of abbreviation with periods
    ## in it, but most of these seem to be organizations, not real terms (e.g., U.S.A., but not H.M.M.)
    ## print(words)
    output1 = ''
    ## each word
    output2 = False
    ## every word except words in outlist
    output3 = False
    output4 = False
    ## allow for all caps word
    all_caps = False
    for word in words:
        if len(word)>0:
            if (word.lower() in ABBREVIATION_STOP_WORDS):
                ## print(word)
                if not output2:
                ## we will assume an all or nothing approach: either remove all stop words, or keep all of them
                    output2 = output1
                    if output3:
                        output4 = output3
            else:
                if output2:
                    output2 = output2+word[0]
                if output4:
                    output4 = output4+word[0]
            if word.isupper():
                if all_caps:
                    output3 = False
                    output4 = False
                else:
                    all_caps = True
                    output3 = output1+word
                    if output2:
                        output4 = output2+word
            elif output3:
                output3 = output3+word[0]
            output1 = output1+word[0]
    output = []
    for item in [output1,output2,output3,output4]:
        if item and (len(item)>2) and \
        (not(item.lower() in pos_dict)) and (not (item.upper() in pos_dict)):
        ## not(item.lower() in ABBREVIATION_STOP_WORDS):
            output.append(item)
            output.append(item+'s')
        ## allow for plural
    return(output)

def derive_plurals(word):
    ## the dictionary plurals, actually includes -ing forms of verbs as well
    ## and regularizes them to verbs (which may or may not also be nouns)
    if word in plural_dict:
        return(plural_dict[word])
    elif len(word) <= 1:
        return(False)
    elif (word[-1] in 'sxz') or (word[-2:] in ['sh', 'ch']):
        return([word+'es'])
    elif (word[-1] == 'y') and not(word[-2] in 'aeiou'):
        return([word[:-1]+'ies'])
    else:
        return([word+'s'])

def look_up_abbreviation_variation(term):
    variations = [term.upper(),term.lower()]
    if (len(variations[0])>2) and (variations[0][-1] == 'S'):
        variations.append(variations[0][:-1]+'s')
    output = []
    ## print(variations)
    for variation in variations:
        if variation in full_to_abbreviation_dict:
            for item in full_to_abbreviation_dict[variation]:
                if not item in output:
                    ## print(1,item)
                    output.append(item)
        if variation in abbreviation_to_full_form:
            for item in abbreviation_to_full_form[variation]:
                if not item in output:
                    ## print(2,'*',variation,'*',item)
                    output.append(item)
    return(output)

def get_expanded_forms_from_abbreviations(term):
    variations = [term.upper(),term.lower()]
    if (len(variations[0])>2) and (variations[0][-1] == 'S'):
        variations.append(variations[0][:-1]+'s')
    output = []
    ## print(variations)
    for variation in variations:
        if variation in abbreviation_to_full_form:
            for item in abbreviation_to_full_form[variation]:
                if not item in output:
                    ## print(2,'*',variation,'*',item)
                    output.append(item)
    return(output)

        
def get_term_variations(term,morph_only=False):
    ## assumes that input list is all lower case
    term = term.rstrip("-_")
    words = re.split('[- _]',term)
    last_word = words[-1]
    bases = False
    plurals = []
    output = []
    if last_word in noun_base_form_dict:
        ## print('1')
        bases = noun_base_form_dict[last_word]
        if last_word in bases:
            plurals = derive_plurals(last_word)
        else:
            plurals = [last_word]
            if bases and (len(last_word)>2) and (last_word[-2]=='s'):
                dict_forms = plural_dict[word]
                if dict_forms:
                    ## just add -ing forms
                    for form in dict_forms:
                        if (len(form)>3) and (form[-3:]=='ing'):
                            plurals.append(form)
    else:
        ## print(1)
        last_word2 = last_word.lower()
        if last_word2 in noun_base_form_dict:
            bases = noun_base_form_dict[last_word2]
            if last_word2 in bases:
                plurals = derive_plurals(bases[0])
        elif len(last_word)>3 and (last_word[-3:] == 'ies'):
            bases = [last_word[:-3]+'y',last_word[:-2]]
            plurals = [term]
        elif len(last_word)>2 and (last_word[-2:] == 'es'):
            bases = [last_word[:-1],last_word[:-2]]
            plurals = [term]
        elif len(last_word)>1 and (last_word[-1]=='s') and \
             not(last_word[-2] in "suciy"):
            bases = [last_word[:-1]]
            plurals = [last_word]
        else:
            ## print('hello')
            bases = [last_word]
            plurals = derive_plurals(last_word)
    if len(words)>1:
        end = term.lower().rfind(words[-1].lower())
        if term[end:].islower():
            casetype = 'lower'
        elif term[end:].upper():
            casetype = 'upper'
        else:
            casetype = 'title'
        ## print(term,' --> ',bases)
        if bases:
            for base in bases:
                if casetype == 'lower':
                    replacement = base.lower()
                elif casetype == 'upper':
                    replacement = base.upper()
                else:
                    replacement = base.title()
                output.append(term[:end]+replacement)
        if plurals:
            for plural in plurals:
                if casetype == 'lower':
                    replacement = plural.lower()
                elif casetype == 'upper':
                    replacement = plural.upper()
                else:
                    replacement = plural.title()
                output.append(term[:end]+replacement)
        return(output,False)
    elif len(words)==1:
        ## print('b',bases,'p',plurals)
        if bases and not morph_only:
            expanded_forms = []
            for base in bases:
                more_stuff = get_expanded_forms_from_abbreviations(base)
                for item in more_stuff:
                    if not item in expanded_forms:
                        expanded_forms.append(item)
            if len(expanded_forms)==0:
                expanded_forms = False
        else:
            expanded_forms = False
        if bases and plurals:
            out = bases[:]
            out.extend(plurals)
            return(out,expanded_forms)
        elif bases:
            out = bases[:]
            more_stuff = get_expanded_forms_from_abbreviations(base)
            for item in more_stuff:
                if not item in out:
                    out.append(item,expanded_forms)
            return(out)
        elif plurals:
            return(plurals,False)
        else:
            return([term],False)
    else:
        return([term],False)


def bad_term(term):
    alpha_test = re.compile('[a-z].*[a-z]',re.I)
    punctuation_test = re.compile('[~`#!@$%^&*()-_<>?/,|]+={}\;"?/><]')
    words = re.split('[- _]',term)
    if (not alpha_test.search(term)) \
    or ((words[-1] in pos_dict) and (not 'NOUN' in pos_dict[words[-1]])) \
     or punctuation_test.search(words[-1]) \
     or ((len(words[-1])>2) and (words[-1][-2:] == "'s")) \
     or ((not (words[-1] in pos_dict)) and (len(words[-1])>5) and (words[-1][-2:] == 'ed')):
        return(True)
    
def get_term_variations_file (infile, outfile, format='fact',filter_out_garbage=True,garbage_file=False,morph_only=False,abbrev_full_dict_file=False,full_abbrev_dict_file=False):
    ## infile is a list of terms, 1 per line
    terms = open(infile).readlines()
    output = {}
    term_list = []
    garbage_list = []
    if not morph_only and full_abbrev_dict_file and abbrev_full_dict_file:
        read_in_full_to_abbreviation_dict(full_abbrev_dict_file,abbrev_full_dict_file)
    if garbage_file:
        garbage_stream = open(garbage_file,'w')
    for term in terms:
        term = term.strip()
        ## term_list.append(term)
        expanded_list = []
        if filter_out_garbage and bad_term(term):
            if garbage_file:
                if format == 'list':
                    garbage_stream.write(term+os.linesep)
                elif format == 'fact':
                    garbage_stream.write('LEMMATIZE TERM=\"'+term+'\" GARBAGE=\"True"'+os.linesep)
        else:
            expanded_list,expansions_of_abbreviation = get_term_variations(term,morph_only=morph_only)
            ## print(term,expanded_list)
            if term == '':
                ## print('empty line'+os.linesep)
                pass
            elif expansions_of_abbreviation:
                if not expanded_list:
                    expanded_list = [term]
                elif not term in expanded_list:
                    expanded_list.append(term)
                for item in expanded_list:
                    if item in output:
                        for expansion in expansions_of_abbreviation:
                            if not expansion in output[item]:
                                output[item].append(expansion)
                    else:
                        output[item] = expansions_of_abbreviation
                        term_list.append(item)
            elif not (term in output):
            ## print(term,expanded_list)
                for item in expanded_list:
                    if item in output:
                        ## print(output[item])
                        output[item].append(term)
                    else:
                        output[item] = [term]
                        term_list.append(item)
    with open(outfile,'w') as outstream:
        ## print(term_list)
        for item in term_list:
            terms = output[item]
            ## print('item:',item,'term:',term)
            for term in terms:
                if format == 'list':
                    outstream.write(item+'\t'+term)
                elif format == 'fact':
                    outstream.write('LEMMATIZE TERM=\"'+item+'\" BASEFORM=\"'+term.lower()+'"'+os.linesep)

def get_next_term(output,terms,filter_out_garbage):
    ## print(filter_out_garbage)
    ##input()
    term = False
    global garbage_count
    while (len(output)<(len(terms)-garbage_count)) and not(term):
        term = random.choice(terms)
        term = term.strip()
        if term in output:
            term = False
        elif bad_term(term) and filter_out_garbage:
            ## print('bad_term',term)
            term = False
            garbage_count=garbage_count+1
    return(term)

def get_term_variations_file_for_n_random_terms (infile, outfile, format='fact',term_number=200,filter_out_garbage=True):
    ## infile is a list of terms, 1 per line
    global garbage_count
    garbage_count = 0
    terms = open(infile).readlines()
    output = {}
    term_list = []
    number_found = 0
    find_terms = True
    while(number_found < term_number) and find_terms:
        term = get_next_term(output,terms,filter_out_garbage)
        if not term:
            find_terms = False
        if find_terms:
            ## term = term.strip()
            ## term_list.append(term)
            expanded_list = get_term_variations(term)
            ## print(term,expanded_list)
            if not (term in output):
                ## print(term,expanded_list)
                for item in expanded_list:
                    if bad_term(item):
                        pass
                    elif item in output:
                        output[item].append(term)
                        # output.pop(item)
                        # term_list.remove(item)
                    else:
                        output[item] = [term]
                        term_list.append(item)
        number_found = number_found+1
    with open(outfile,'w') as outstream:
        ## print(term_list)
        for item in term_list:
            terms = output[item]
            ## print('item:',item,'term:',term)
            for term in terms:
                if format == 'list':
                    outstream.write(item+'\t'+term)
                elif format == 'fact':
                    outstream.write('LEMMATIZE TERM=\"'+item+'\" BASEFORM=\"'+term.lower()+'"'+os.linesep)
