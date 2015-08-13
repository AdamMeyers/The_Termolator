## # -*- py-which-shell: "/usr/local/bin/python3"; -*-
import os
import re
from nyu_utilities import *
### from funding_detector_file_loading import *

DICT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + os.sep
## DICT_DIRECTORY = '/home/meyers/FUSE/Python-Scripts/'
LOC_DICTIONARY = DICT_DIRECTORY+'location-lisp2-ugly.dict'
read_in_org_dictionary(LOC_DICTIONARY,dictionary='loc')
FACT_STYLE = 'phase1'  ## currently this only effects printout of ENAMEX facts

RELATION_LIST = ['EXEMPLIFY','ORIGINATE', 'ABBREVIATE', 'RELATED_WORK', 'OPINION', 'TO_BE_ANNOTATED']
RELATED_WORK_SUBTYPES = ['BETTER_THAN', 'BASED_ON', 'CONTRAST', 'CORROBORATION','CO-ANNOTATION']
ARG1_NAME_TABLE ={'EXEMPLIFY':'SUBCLASS','DISCOVER':'INVENTOR','MANUFACTURE':'MAKER','SUPPLY':'SUPPLIER',\
                      'ORIGINATE':'INVENTOR','ALIAS':'FULLNAME','ABBREVIATE':'FULLNAME','BETTER_THAN':'BETTER',\
                      'BASED_ON':'DERIVED','CONTRAST':'THEME','CORROBORATION':'THEME','CO-CITATION':'THEME',\
                      'POSITIVE':'JUDGE','NEGATIVE':'JUDGE','SIGNIFICANT':'JUDGE','PRACTICAL':'JUDGE','STANDARD':'JUDGE'}
ARG2_NAME_TABLE ={'EXEMPLIFY':'SUPERCLASS','DISCOVER':'INVENTION','MANUFACTURE':'PRODUCT','SUPPLY':'PRODUCT',\
                      'ORIGINATE':'INVENTION','ALIAS':'FULLNAME','ABBREVIATE':'SHORTNAME','BETTER_THAN':'WORSE',\
                      'BASED_ON':'ORIGINAL','CONTRAST':'THEME','CORROBORATION':'THEME','CO-CITATION':'THEME',\
                      'POSITIVE':'THEME','NEGATIVE':'THEME','SIGNIFICANT':'THEME','PRACTICAL':'THEME','STANDARD':'THEME'}

## file_to_watch = False
abbreviate_dictionary = {}
jargon_dictionary = {}
full_jargon_dictionary = {}
## citation_dictionary = {}
enamex_dictionary = {} ## for person and organization strings
relation_dictionary = {}
entity_start_end_dictionary = {}
entity_pair_relation_dictionary = {}
global_key_number = 0
global_relation_number = 0
longest_jargon_term = 0

entity_keys = ['start','end','text','type','POS','ENTITY_ID','comment']

relation_keys = ['type','ARG1_ID','ARG1','ARG2_ID','ARG2','ARG3','ARG1_IMPLIED','ARG2_IMPLIED','TEXT_SIGNAL','GRAM_SIGNAL','comment']

## parentheses_pattern = re.compile(r'\(([^)]*)\)')
parentheses_pattern = re.compile(r'[(\[]([^)\]]*)[)\]]')
parentheses_pattern2 = re.compile(r'[(\[]([^)\]]*)([)\]]|$)')

## organization_word_pattern = re.compile(r'^((AGENC(YIE)|ASSOCIATION|COLLEGE|COMMISSION|CORP[\.]?|CORPORATION|COUNCIL|DEPARTMENT|ENDOWMENT|FEDERATION|FOUNDATION|FUND|HOSPITAL|INC\.?|INSTITUTE|OFFICE|ORGANIZATION|ORGANISATION|PROGRAM|PROGRAMME|PROJECT|SCHOOL|SOCIET(Y|IE)|TRUST|UNIVERSIT(Y|IE))S?)$',re.I)

organization_word_pattern = re.compile(r'^(AGENC(Y|IE)|ASSOCIATION|CENT(ER|RE|RO)|COLL[EÈ]GE|COMMISSION|CORP[\.]|CORPORATION|COUNCIL|DEPARTMENT|ENDOWMENT|FOUNDATION|FUND|GROUP|HOSPITAL|(INC|SA|CIA|LTD|CORP)\.?|IN?STITUT[EO]?|LABORATOR((Y)|IE)|OFFICE|ORGANI[SZ]ATION|PARTNER|PROGRAMME|PROGRAM|PROJECT|SCHOOL|SOCIET(Y|IE)|TRUST|(UNIVERSI[TD](AD)?(E|É|Y|IE|À|ÄT)?)|UNIVERSITÄTSKLINIKUM|UNIVERSITÄTSSPITAL)S?$',re.I)

ABBREVIATION_STOP_WORDS = ['a','the','an','and','or','but','about','above','after','along','amid','among','as','at','by','for','from','in','into','like','minus','near','of','off','on','onto','out','over','past','per','plus','since','till','to','under','until','up','via','vs','with','that']

abbreviation_section_pattern = re.compile(r'^ *abbreviations?:? *$',re.I)

abbreviation_title_match = re.compile(r'^(list of )?abbreviations?',re.I)

abbreviation_section_type = False

abbreviation_table_entry_pattern = re.compile(r'([^ :;,.]+)[:,] *([^:;,.]+)[;,.]') 
## first parens contain key and second parens contain value

## word_end_boundary = re.compile(r'[ ]+|([a-zA-Z0-9]-[a-zA-Z0-9])|$')

dash = re.compile(r'[-–‒―—]')

word_split_pattern = re.compile(r'[^\w@]+')
space_and_word_from_end=re.compile('([^\w@.:;]+)[\w@]+[^\w@\.:;,]*$')
word_and_space=re.compile('([\w@]+)(([^\w@]+)|$)')

def regularize_match_string(string):
    return(re.sub('[- ]+',' ',string.strip(''' ,.?><'";:][{}-_=)(*&^%$#@!~''').upper()))

def regularize_match_string1(string):
    return(re.sub('[-]',' ',string.upper()))

def remove_empties(input_list):
    if type(input_list) == list:
        return([x for x in input_list if (x != '')])
    else:
        return(input_list)
##    out_list=[]
##    for item in input_list:
##        if item != '':
##            out_list.append(item)
##    return(out_list)

def get_more_words(line,length):
    ## print(line)
    ## print(length)
    if line and re.search('[^\W\d]',line):
        ## was [a-zA-Z]
        words = remove_empties(word_split_pattern.split(line.strip(''' ,.?><'";:][{}-_=)(*&^%$#@!~''')))
        # words = re.split('[\W]+',\
        #                  line.strip(''' ,.?><'";:][{}-_=)(*&^%$#@!~'''))
        ## print(words,line,length,sep=os.linesep)
        ## words = [x for x in words if (x != '')]
        if len(words) > length:
            return(words[0 - length:])
        else:
            return(words)
    else:
        return(False)

def unbalanced_delimiter(outstring):
    ## This will be False if there are no delimiters (brackets), or if
    ## there is a left and right delimiter, such that the left
    ## precedes the right.
    ## This will return True if there is a left not followed by a right
    ## or a right that is not preceded by a left (i.e., exactly one delimiter
    ## or a delimiter out of order).    
    left = re.search('[(\[{"]',outstring)
    if left and len(outstring)>left.start():
        right = re.search('[)\]}"]',outstring[left.start()+1:])
        if right:
            return(False)
        else:
            return(True)
    elif re.search('[)\]}]',outstring):
        return(True)
    else:
        return(False)
    
def fix_unbalanced(outstring,line,line_position):
    ## print(outstring,line,line_position,sep=os.linesep)
    ## this balances parens for formulaic items that contain parens
    ## the good ones all have hyphens either before the left paren
    ## or after the right one
    ## print(outstring,line,line_position,sep=os.linesep)
    right = re.search('[)\]}]',outstring)
    quote = re.search('"',outstring)
    if right:
        character_position = re.search('([^ ]+) *$',line[:line_position])
        if character_position and re.search('[{\[(]',character_position.group(1)): 
            new_start = character_position.start(1)
            new_string = line[new_start:line_position]+outstring
            if re.search('(-[(\[{])|([)\]}]-)',new_string):
                return(new_start,new_string)
            else:
                return(False,False)
        else:
            return(False,False)
    elif quote:
            ## evaluates to True if out is found
        ## print(quote.start(),quote.group(0))
        if len(outstring)>quote.start() and not(re.search('"',outstring[quote.start()+1:])):
            character_position = re.search('([^ ]+) *$',line[:line_position])
            if character_position and re.search('"',character_position.group(1)):
                new_start = character_position.start(1)
                new_string = line[new_start:line_position]+outstring
                return(new_start,new_string)
            else:
                return(False,False)
        else:
            return(False,False)
    else:
        return(False,False)
    
def get_word_substring_at_end(words, line, inbetween=False, no_check=False):
    ## this assumes that the words occur at the end of the line
    ## and that any characters ignored (hyphens, numbers, etc.) 
    ## are OK to ignore
    if inbetween:
        if re.search('[)\]}]',inbetween):
            ## the match is discarded if right brackets appear
            ## in between the abbreviation and antecedent
            return(False,False)
        elif(line[-1] == ' '):
            inbetween = False
        elif len(inbetween) == 1 and inbetween[0] in '([':
            inbetween = False
        elif ' ' in inbetween:
            if inbetween[0] == ' ':
                inbetween = False
            else:
                inbetween_space = inbetween.index(' ')
                inbetween = inbetween[:inbetween_space]
    line_upper = line.upper().rstrip(' ')
    line_position = len(line_upper)
    for number in range(len(words)):
        word_position = -1-number
        word = words[word_position]
        line_position = line_upper.rindex(word.upper(),0,line_position)
    ##    print(word,line_position)
    outstring = line[line_position:]
    if inbetween:
        outstring=outstring+inbetween
    outstring=outstring.rstrip(' ')
    if unbalanced_delimiter(outstring) and (not no_check):
        ## if there is a left or right bracket, but not both
        ## this is ill-formed
        ## print('unbalanced:',outstring,line,line_position,sep='**')
        new_position,outstring = fix_unbalanced(outstring,line,line_position)
        if new_position:
            line_position = new_position
    if not outstring:
        return(False,False)
    else:
        return(outstring,line_position)

def one_word_match_match (word,abbreviation):      
    if re.search('[A-Z]',abbreviation) and (len(word)>len(abbreviation)+1) and \
       abbreviation.isalpha() and \
       (word[0].upper() == abbreviation[0].upper()):
        ## require first characters to match
        ## requires abbreviation to be at least 2 characters short than word
        ## requires abbreviation to contain at least one uppercase character
        ## require that the characters in the abbreviation after the first
        ## match in order, with any number of skips, but none are missed
        abbreviation_num = 1
        word_num = 1
        while (word_num < len(word)) and (abbreviation_num < len(abbreviation)):
            if word[word_num].upper() == abbreviation[abbreviation_num].upper():
                abbreviation_num = abbreviation_num+1
            word_num=word_num+1
        if abbreviation_num == len(abbreviation):
            return(True)
        else:
            return(False)

def almost_the_same(word1,word2):
    ## print(word1,word2)
    if (word1 == word2):
        return(True)
    if (word1 in word2) or (word2 in word1):
        ratio = len(word1)/len(word2)
        if abs(ratio-1)<=.3:
            return(True)
        else:
            return(False)
    else:
        return(False)
        

def match_abbreviation_chunk (word, abbreviation, whole=False):
    ## print(word,abbreviation,whole)
    ## print(len(abbreviation),(.7 *len(word)))
    if whole and (almost_the_same(word.upper(),whole.upper())):
        ## whole provides the whole abbreviation if the test is against a portion
        ## of the original
        return(False)
    substrings = []
    for num in range(len(abbreviation)):
        if abbreviation[0-num].upper() == word[0].upper():
            substrings.append(abbreviation[(0-num):])
    for num in range(len(substrings)):
        substring = substrings[0-num]
        if one_word_match_match(word,substring):
            ## print('1',word,'2',abbreviation,'3',substring)
            return(substring)
    return(False)

def blocked_abbreviation(line,abbreviation_position,abbreviation):
    pattern = re.search('([^ ]) *$',line[:abbreviation_position])
    if pattern:
        previous_character = pattern.group(1)
        if previous_character == ';':
            ## semicolon always blocks abbreviation
            return(True)
        elif (previous_character == '.') and (len(abbreviation)==1) and \
             (len(line)>abbreviation_position+2) and (line[abbreviation_position+2]==')'):
            ## this identifies situations likely to be enumeration, e.g., (a) ... (b) ...
            ## further constraints may include requiring the letters to be lowercase, although
            ## it is unclear that this is necessary
            return(True)
        elif abbreviation.islower() and (abbreviation in ABBREVIATION_STOP_WORDS):
            return(True)
        elif abbreviation.istitle() and (abbreviation.lower() in ABBREVIATION_STOP_WORDS):
            return(True)
        
def get_position_before_word(word,line):
    ## print(1,word)
    ## print(2,line)
    pattern = re.search(r'[^\w@]+'+word+'[^\w@]*$',line)
    if pattern:
        return(pattern.start()+1)

def classify_abbreviated_string(word_string,wordlist=False):
    if not wordlist:
        wordlist = remove_empties(word_split_pattern.split(word_string))
    if '@' in word_string:
        return('EMAIL')
    elif re.search('(http)|(www)',word_string.lower()):
        return('URL')
    for word in wordlist:
        if (organization_word_pattern.search(word)):
            return('ORGANIZATION')
    if word_string.upper() in location_dictionary:
        return('GPE')
    might_be_gpe = True
    has_gpe_word = False
    for word in wordlist:
        if word.upper() in location_dictionary:
            has_gpe_word = True
        elif not (word.lower()) in ABBREVIATION_STOP_WORDS:
            might_be_gpe = False
    if might_be_gpe and has_gpe_word:
        return('GPE')
    return('JARGON')

def letter_match(char1,word):
    ## char 1 is from the abbreviation
    char2 = word[0]
    ## char 2 is from the word
    if (char1 == char2):
        return(True)
    if (char1 in greek_match_table) and (greek_match_table[char1]==char2):
        return(True)
    elif (char2 in greek_match_table) and (greek_match_table[char2]==char1):
        return(True)
    elif (char1 == 'X') and (len(word)>2) and (word[:2]=='EX'):
        return(True)
    else:
        return(False)

def abbreviation_match(abbreviation,previous_words,line,abbreviation_position,line_offset,previous_line,more_words):
    ## this does not use previous_line or more_words (the last words on the previous line) yet
    ## however, it is possible that it should. To do this would require some minor changes

    ## Missing cases: 
    ##                matrix metalloproteinase (MMP) -- would need to be able to identify prefixes (can't right now)
    ##                A recombinant form of SPARC (rSPARC) -- not general -- unclear whether type nouns from NOMLEX-PLUS
    ##                     should be in our list of stop words (brand, breed, category, class, family, form, kind, line, manner,
    ##                     model, series, sort, species, strain, type, variety, vein)
    ## 
    ##                ADAMTS-2 (A Disintegrin And Metalloproteinase with ThromboSpondin motifs)  ## not clear if this is general either
    ##                         -- Can we always ignore a final hyphen plus number?

    ## More missing cases: (1) tetracycline (tet), roscovitine (Rosc) -- one word prefix; (2) absence (–) -- presence (+) -- idiosyncratic
    ## if abbreviation in ['VZ','18']:
    ## print('*****')
    ## print(abbreviation,previous_words)
    ## print(line)
    ## print(abbreviation_position,line_offset)
    ## print(previous_line)
    ## print(more_words)
    ## if abbreviation.upper() == 'N':
##    if True:
##        print(abbreviation)
##        print(previous_words)
##        print(line)
##        print(abbreviation_position)
##        input('')
    one_off = False
    out_string = False
    matching_words = []
    organization = False
    abbreviation2 = abbreviation
    ## abbreviation3 = abbreviation
    skipped_maximum = 3
    stop_words = 0
    skipped_words = 0
    trimmed_words = 0
    last_word_was_stop_word = False
    pattern_that_matched = False
    final_s = False
    final_match = False
    multi_letter = False
##        if abbreviation[-1].isnumeric():
##        abbreviation2=abbreviation.rstrip('1234567890')
##        number = abbreviation[0-len(abbreviation2)]   
    if len(abbreviation)>1 and abbreviation[0] in '\'"“`':
        one_off = True
        abbreviation2 = abbreviation[1:]
    if re.search('[-/]',abbreviation2):
        abbreviation2 = re.sub('[-/]','',abbreviation2)
    if blocked_abbreviation(line,abbreviation_position,abbreviation) \
      or not(re.search('[^\W\d]',abbreviation2)) or \
      ((len(abbreviation2)==1) and not(re.search('[A-Z]',abbreviation2))):
        ## initially just covers semi-colon and enumeration cases
        ## also requires that abbreviations contain letters
        ## and that single character abbreviations be a capial letter
        return(False)
    ## if (len(abbreviation2) <=len(previous_words)) or True:  ### this no longer holds
        ## exact matches (ignore case -- note most common cases of non-upper: first letter lower
        ## match is each letter of abbreviation represents first letter of words
    if not re.search('[^\W\d]',abbreviation2):
        Fail = True
    else:
        Fail = False
    if not Fail:
        ## abbreviations must contain at least one letter
        all_matches = True
        number = 0
        extra_letters = 0
        word_index = 0
        while (((number < len(abbreviation2)) and (not final_s)) or \
               (final_s and (number+1 < len(abbreviation2)))) and \
               all_matches and (len(previous_words)>((stop_words+skipped_words+number)-extra_letters)):
            if (number == 0) and \
              (len(previous_words) > 1) and (len(abbreviation2) > 1) and \
              (abbreviation2[-1] in ['s','S']) and \
              (previous_words[-1][-1] in ['s','S']) and \
              (not previous_words[-1][0] in ['s','S']):
              final_s = True
            if final_s:
                index = -2-number
                word_index = 1+(index-((stop_words+skipped_words)-extra_letters))
            else:
                index = -1-number            
                word_index = index-((stop_words+skipped_words)-extra_letters)
            ## print(abbreviation2[index],previous_words[word_index])
            if letter_match(abbreviation2[index].upper(), previous_words[word_index].upper()):
                ## print('hi',1)
                if previous_words[word_index].lower() in ABBREVIATION_STOP_WORDS:
                    last_word_was_stop_word = previous_words[word_index]
                else:
                    last_word_was_stop_word = False
                number=number+1
                if (number == len(abbreviation2)) or (final_s and ((1+number)==len(abbreviation2))):
                    final_match = True
            elif last_word_was_stop_word and (last_word_was_stop_word[0].upper() == previous_words[word_index][0].upper()):
                last_word_was_stop_word = False
                stop_words = stop_words+1
                if number == 0:
                    trimmed_words = trimmed_words+1
            elif previous_words[word_index].lower() in ABBREVIATION_STOP_WORDS:
                stop_words = stop_words+1
                if number == 0:
                    trimmed_words = trimmed_words+1
                last_word_was_stop_word = previous_words[word_index]
            else:
                if index == -1: ## end of the word is special for Python
                    possible_match = match_abbreviation_chunk(previous_words[word_index].strip('''"'.,'''),abbreviation2)
                    end_of_ab = True
                else:
                    ## print(previous_words[word_index],abbreviation2[:index+1])
                    possible_match = match_abbreviation_chunk(previous_words[word_index].strip('''"'.,'''),abbreviation2[:index+1],abbreviation2)
                    ## print(possible_match)
                    end_of_ab = False
                if possible_match:
                    number=number+len(possible_match)
                    if number == len(abbreviation2):
                        final_match = True
                    extra_letters=extra_letters+(len(possible_match)-1)
                    multi_letter = True
                    ## print(possible_match,final_match,extra_letters,number)
                elif (len(abbreviation2)>2) and (len(abbreviation2)> (skipped_words+1)) and (skipped_words < skipped_maximum):
                    skipped_words = 1+skipped_words
                    if number == 0:
                        trimmed_words = trimmed_words+1
                else:
                    all_matches = False
        ## print(all_matches,final_match,possible_match)
        ## print(skipped_words)
##        print(len(previous_words),(stop_words+skipped_words+number))
##        print(stop_words,skipped_words,number)
##        print(extra_letters)
        if all_matches and (not final_match):
            ### 57 
            all_matches = False
##        print(1,all_matches)
##        print(stop_words,skipped_words,number)
##        print(len(previous_words))
##        print(extra_letters)
        if all_matches:
##            print(len(previous_words))
##            print(stop_words)
##            print(skipped_words)
##            print(number)
            if final_s:
                if (len(previous_words)+1+extra_letters) < (stop_words+skipped_words+number):
                    all_matches = False
            elif (len(previous_words)+extra_letters) < (stop_words+skipped_words+number):
                all_matches=False
        ## print(2,all_matches)
##   questionable limitation A
        if all_matches:
            pattern_that_matched = 1
            ## print(previous_words,abbreviation2,stop_words,skipped_words,extra_letters)
            if final_s:
                matching_words = previous_words[1-(len(abbreviation2)+(stop_words+skipped_words)-extra_letters):]
            else:
                matching_words = previous_words[0-(len(abbreviation2)+(stop_words+skipped_words)-extra_letters):]
            end_position = abbreviation_position
            if trimmed_words > 0:
                for num in range(trimmed_words):
                    if end_position:
                        end_position = get_position_before_word(previous_words[0-(1+num)],line[:end_position])
                    ## subtract the length of the words removed from the end of the list of words
                    ## also subtract one for the space (or other delimiter)
                if end_position:
                    matching_words = matching_words[:(0-trimmed_words)]
            out_string,start_position = get_word_substring_at_end(matching_words,line[:end_position],line[end_position:abbreviation_position])
            # print(matching_words,line[:abbreviation_position])
            ## print('extra',extra_letters)
            ## print(out_string,start_position)
            if out_string:
                begin = line_offset+start_position
                end = begin+len(out_string)
    if out_string and (len(out_string) <= (len(abbreviation2)+1)):
        out_string = False
        all_matches = False
        Fail = True
    ## print(out_string)
    if (not out_string) and (not Fail):
       ## special case: one of the previous words is itself an allcaps abbreviation, 
       ## typically the last one:  small interfering RNA (siRNA)
       ## Note: This version does not account for stop words  *****************
        allcap_word = False
        word_number = 0
        ab_index = False
        for num in range(min(len(previous_words),len(abbreviation2)-1)):
            word_num = -1-num
            word = previous_words[word_num]
            if word.isupper() and not allcap_word:
                ab_index = abbreviation2.upper().find(word)
                if ab_index != -1:
                    allcap_word = word
        ## print(allcap_word)
        if allcap_word and allcap_word !=abbreviation2 and (len(abbreviation2)>len(allcap_word)) and len(previous_words)>1:
            all_matches = True
            chosen_words = []
            ## print(ab_index,ab_index+len(allcap_word),len(abbreviation))
            ## print('ab index',ab_index)
            if (ab_index == 0): ## allcaps is at beginning of abbreviation
                for number in range(len(abbreviation2)-len(allcap_word)):
                    index = -1-number
                    if all_matches and (abs(index)<=len(previous_words)) and \
                            (not letter_match(abbreviation2[index].upper(),previous_words[index].upper())):
                        ## print(abbreviation[index].lower(),previous_words[index])
                        all_matches = False
                if all_matches:
                    chosen_words = previous_words[(len(allcap_word)-len(abbreviation2)-1):]
                    matching_words.append(allcap_word)
                    matching_words.extend(chosen_words)
            elif (ab_index+len(allcap_word))==len(abbreviation2):  ## allcaps is at end of abbreviation
                ## print(abbreviation2,'|',previous_words)
                for number in range(len(abbreviation2)-len(allcap_word)):
                    abbreviation_index=-1-(len(allcap_word))-number
                    word_index=0-2-number
                    ## print(1,all_matches)
                    ## print(2,abbreviation2)
                    ## print(3,abbreviation_index)
                    ## print(4,previous_words)
                    if all_matches and (len(abbreviation2)>abbreviation_index) and \
                       (len(previous_words)>=abs(word_index)) and (previous_words[word_index] != '') and\
                       (not letter_match(abbreviation2[abbreviation_index].upper(), previous_words[word_index].upper())):
                        all_matches = False
                if all_matches:
                    chosen_words = previous_words[word_index:]  ## last value of word_index
                    matching_words = []
                    matching_words.extend(chosen_words)
            if all_matches:
                pattern_that_matched = 3
                ## print(chosen_words,line[:abbreviation_position])
                out_string,start_position = get_word_substring_at_end(chosen_words,line[:abbreviation_position])
                if out_string:
                    begin = line_offset+start_position
                    end = begin+len(out_string)
    if (not out_string) and (not Fail):
        ## this one is jargon specific
        if len(previous_words)>0 and one_word_match_match(previous_words[-1],abbreviation2):
            matching_words=previous_words[-1:]
            pattern_that_matched = 5
            out_string,start_position = get_word_substring_at_end(matching_words,line[:abbreviation_position])
            if out_string:
                begin = line_offset+start_position
                end = begin+len(out_string)
        elif len(previous_words)>= 2 and len(previous_words[-1]) <=2 and len(abbreviation2)>2 and \
            abbreviation2.endswith(previous_words[-1]) and \
            one_word_match_match(previous_words[-2],abbreviation2[:-1]):
            pattern_that_matched = 6
            matching_words = previous_words[-2:]
            out_string,start_position = get_word_substring_at_end(matching_words,line[:abbreviation_position])
            if out_string:
                begin = line_offset+start_position
                end = begin+len(out_string)
            ## At this point in the code abbreviation2 equals either abbreviation or abbreviation less its hyphens 

        ## if abbreviation consists of N consonants and an optional number, and those N consonants are the first N
        ## consonants in the first word of the match and the optional number is the second match
        ## examples: peroxiredoxin (Prx) and thioredoxin 1 (Trx1)

    ## Did not implement the following one as it may induce weird errors
        ## if the abbreviation includes a longer prefix (that need not be capitalized), that can match as well
        ##   oxidation index(I ox) -- this is a different order
    if out_string:
        output_type = classify_abbreviated_string(out_string,wordlist=matching_words)
    if matching_words and out_string and (not Fail):
        if out_string[1] in '''`'"“"”''':
            out_string = out_string[1:]
            begin = begin+1
        if len(out_string)>1 and (out_string[-1] in '''`'"“"”'''):
            out_string = out_string[:-1]
            end = end-1
##        print('abbreviation',abbreviation)
##        print('position',abbreviation_position)
##        print('matched',pattern_that_matched)
##        print('words',matching_words)
##        print('line:',line)
        return([begin,end,out_string,output_type,one_off])


def get_context_string(line,start,end):
    new_start = max(0,start-60)
    new_end = min(len(line),end+60)
    return(remove_extra_spaces(remove_xml(line[new_start:new_end])))

def process_abbreviation_section(line,previous_line,position,waiting):
    ## lines in abbreviation sections fall into 2 categories
    ## 1. self-contained abbreviation/antecedent pairs divided by 2 types of delimiters
    ##    abbreviation1 delimiterA antecedent1 delimeterB abbreviation2 delimiterA antecedent2 ....
    ##    delimiterA is a member of [':',','] and delimiterB is a member of [';', '.']
    ##    If a line contains none of these delimiters, the global abbreviation_section is set to False
    ## 2. alternating lines of abbreviations or values. 
    ##    (i) Waiting starts off as False; 
    ##    (ii) when line is an abbreviation the function returns abbreviation-info 
    ##         and this is the value of the next instance of waiting (a blank line causes the same
    ##         waiting value to be returned)
    ##    (iii) when an abbreviation matches a current antecedent, waiting is set to False again
    ##    (iv)  if a possible antecedent is in the wrong form, it is rejected and the global abbreviation_section
    ##          is set to False -- if we going to be strict, we can require that abbreviations match according to 
    ##          our matching rules -- but it is unclear that this is necessary
    ##    
    global abbreviation_section
    global abbreviation_section_type
    ## global file_to_watch
    pattern = False
    if abbreviation_section_type != 'table':
        pattern = abbreviation_table_entry_pattern.search(line)
    if pattern:
        if not abbreviation_section_type:
            abbreviation_section_type = 'pattern'
            ## print(abbreviation_section_type)
        while pattern:
            ARG2_string = pattern.group(1)
            ARG2_begin = position+pattern.start(1)
            ARG2_end = position+pattern.end(1)
            ARG1_string = pattern.group(2)
            ARG1_begin = position+pattern.start(2)
            ARG1_end = position+pattern.end(2)
            organization = False
            output_type = 'JARGON'
            for word in remove_empties(word_split_pattern.split(ARG1_string)):
                if (not organization) and organization_word_pattern.search(word):
                    organization = True
                    output_type = 'ORGANIZATION'
            record_new_relation_and_entities('ABBREVIATE',output_type,ARG1_string,ARG1_begin,ARG1_end, \
                                                 output_type,ARG2_string,ARG2_begin,ARG2_end,GRAM_SIGNAL='TABLE')
            pattern = abbreviation_table_entry_pattern.search(line,pattern.end(2))
        waiting = 'pattern'
        ## print(abbreviation_section_type)
        return(waiting)
    elif waiting:
        if waiting == 'pattern':
            abbreviation_section = False
            return(False)
        elif line.strip(' ') == '':
            return(waiting)
        elif type(waiting) == list:
            if abbreviation_section_type != 'pattern':
                pattern = re.search('^ *([^ ]+|[^ ].*[^ ]) *$',line)
            if pattern:
                if not abbreviation_section_type:
                    abbreviation_section_type = 'table'
                ARG2_string,ARG2_begin,ARG2_end = waiting
                ARG1_string = pattern.group(1)
                ARG1_begin = position+pattern.start(1)
                ARG1_end = position+pattern.end(1)
                organization = False
                output_type = 'JARGON'
                for word in  remove_empties(word_split_pattern.split(ARG1_string)):
                    if (not organization) and organization_word_pattern.search(word):
                        organization = True
                        output_type = 'ORGANIZATION'
                ## print('hello')
##                if file_to_watch:
##                    print(line)
                record_new_relation_and_entities('ABBREVIATE',output_type,ARG1_string,ARG1_begin,ARG1_end, \
                                                     output_type,ARG2_string,ARG2_begin,ARG2_end,GRAM_SIGNAL='TABLE')
            waiting = False
        else:
            raise Exception('Debug process_abbreviation_section'+os.linesep+line)
    else:
        pattern = re.search('^ *([^ ]+|[^ ].*[^ ]) *$',line)
        if pattern:
            ARG2_string = pattern.group(1)
            ARG2_begin = position+pattern.start(1)
            ARG2_end = position+pattern.end(1)
            if not re.search('[a-z]',ARG2_string,re.I):
                pass
            elif ' ' in ARG2_string:
                abbreviation_section = False
                return(False)
            else:
##                if file_to_watch:
##                    print(line)
                return([ARG2_string,ARG2_begin,ARG2_end])
            



def possible_word_sequences (list_of_words):
    ## in principle, we could add variations with hyphens, etc.
    out_string = list_of_words[0]
    out_list = [out_string]
    for word in list_of_words[1:]:
        out_string = out_string+' '+word
        out_list.append(out_string)
    return(out_list)


def get_text_signal_from_inbetween_string(inbetween_string,relation_type):
    inbetween_string = inbetween_string.strip()
    if (relation_type == 'ABBREVIATE') and (re.search('[^\W\d]',inbetween_string)) and (number_of_words(inbetween_string) < 3):
        return(inbetween_string)
        

def propose_jargon_relation(jargon_triple1,jargon_triple2,line):
    global global_relation_number
    global relation_dictionary
    global abbreviate_dictionary
    global entity_pair_relation_dictionary
    entity_pair_key = 'J'+str(jargon_triple1[2])+'and'+'J'+str(jargon_triple2[2])
    relation = False
    relation_type = False
    GRAM_SIGNAL = False
    ARG3=False
    TEXT_SIGNAL = False
    if not (entity_pair_key in entity_pair_relation_dictionary):
        ## if triple1 represents a substring of triple2, propose an exemplify relation
        ## if (jargon_triple1[1]<jargon_triple[1] and jargon_triple1[1]>jargon_triple2[0]) \
           ## if end of jargon1 is between the start and end of triple2 [2 [1  ]] -- probably the starts are equal
           ## probably not a good case
        jargon_object1 = jargon_dictionary[jargon_triple1[2]]
        jargon_object2 = jargon_dictionary[jargon_triple2[2]]
        arg1_text = jargon_object1['text']
        arg2_text = jargon_object2['text']
        jargon_string1 = arg1_text.upper()
        jargon_string2 = arg2_text.upper()
        if (jargon_triple2[0]<jargon_triple1[1]) and (jargon_triple2[0]>jargon_triple1[0]) and jargon_triple1[1] == jargon_triple2[1]:
           ## or if start of jargon2 is between the start and end of triple1 [1 [2 ]] and the ends are equal
            ## relation_type = 'EXEMPLIFY'
            ## GRAM_SIGNAL='NOUN_MOD'
            ## relation = True
            pass
            ## this no longer applies since we changed the specs
        ## if triple1 and triple2 are in the "right" configuration, propose an abbreviate relation
        ## if there is a parenthesis boundary, GRAM_SIGNAL='PARENTHESES'
        ## elif there are one or two words (ignore punctuation) that are between abbreviator and abbreviatee
        ## TEXT_SIGNAL = those words
        ## else, text signal is unknown
        ## for now, print to the screen the text signals for ABBREVIATE
        ## ultimately, we should start to record them (we could also generate them from preexisting annotation)
        elif (jargon_triple1[1] < jargon_triple2[0]) and jargon_string1 in abbreviate_dictionary:
              inbetween_string = line[jargon_triple1[1]:jargon_triple2[0]]
              ## print(1,line[jargon_triple1[0]:jargon_triple1[1]],2,line[jargon_triple2[0]:jargon_triple2[1]])
              ## print(jargon_triple1,jargon_object1,jargon_string1)
              ## print(jargon_triple2,jargon_object2,jargon_string2)
              ARG1_dict_entry = abbreviate_dictionary[jargon_string1]
              ## print('DICT:',ARG1_dict_entry,arg1_text,arg2_text,'In between:',inbetween_string)
              if ARG1_dict_entry:
                  if ('ALIAS' in ARG1_dict_entry) and (jargon_string2 in ARG1_dict_entry['ALIAS']):
                     ARG3='ALIAS'
                     relation_type = 'ABBREVIATE'
                  elif ('ARG2' in ARG1_dict_entry) and (jargon_string2 in ARG1_dict_entry['ARG2']):
                     relation_type = 'ABBREVIATE'
                  if (re.search('[\[(]', inbetween_string)) and not re.search('[^\W\d]',inbetween_string):
                     relation = True
                     GRAM_SIGNAL='PARENTHESES'
                  # elif len(inbetween_string) < 20:
                  #    TEXT_SIGNAL = get_text_signal_from_inbetween_string(inbetween_string,'ABBREVIATE')
                  #    if not TEXT_SIGNAL:
                  #       relation_type = False
                  # This had bizarre results
                  else:
                      relation_type = False
              elif len(inbetween_string) > 5 or re.search('[^\W\d]',inbetween_string):
                  ## if two jargon terms are close together and in a small set of grammatical relations with each other
                  ## we can hypothesize that there is some relation between them, even if we don't know which one
                  pass
              elif ('(' in inbetween_string) and not re.search('[^\W\d]',inbetween_string):
                  relation_type = 'TO_BE_ANNOTATED'
                  GRAM_SIGNAL='PARENTHESES'
              elif re.search('[,:]', inbetween_string) or dash.search(inbetween_string):
                  relation_type = 'TO_BE_ANNOTATED'
                  GRAM_SIGNAL='APPOSITION'
        if relation_type:
            relation = {'type':relation_type,'ARG1_ID':jargon_object1['id'],'ARG1':arg1_text,'ARG2_ID':jargon_object2['id'],\
                            'ARG2':arg2_text,'comment':'Automatically Generated'}
            if GRAM_SIGNAL:
                  relation['GRAM_SIGNAL']=GRAM_SIGNAL
            elif TEXT_SIGNAL:
                  relation['TEXT_SIGNAL']=TEXT_SIGNAL
            if ARG3:
                  relation['ARG3']=ARG3
            relation_dictionary[global_relation_number] = relation
            entity_pair_relation_dictionary[entity_pair_key] = global_relation_number
            global_relation_number = 1 + global_relation_number

def find_sequence_in_string(sequence,line):
    output = re.finditer('([\W]|^)'+'('+sequence+')'+'([\W]|$)',line,flags=re.I)
    return(output)

def record_second_pass_relations_and_entities(previous_line,line,line_position,longest_jargon_term,jargon_term_dict):
    global global_key_number
    global global_relation_number
    global jargon_dictionary
    global relation_dictionary
    global abbreviate_dictionary
    global entity_start_end_dictionary
    words = remove_empties(word_split_pattern.split(line))
    word_list = []
    ## given, the recorded jargon, see if there is any unrecorded jargon on this line
    for position in range(len(words)):
        words[position] = words[position].upper()
    for position in range(len(words)):
        max_position = min(len(words),longest_jargon_term+position+1)
        word_list.extend(possible_word_sequences(words[position:max_position]))
    word_list = set(word_list)
    jargon_found = []
    ## print(word_list)
    for sequence in word_list:
        if sequence in jargon_term_dict:
            ## print(sequence)
            dictionary_entry = jargon_term_dict[sequence]
            if 'POS' in dictionary_entry:
                POS = dictionary_entry['POS']
            else:
                POS = False
            if 'subtype' in dictionary_entry:
                subtype = dictionary_entry['subtype']
            else:
                subtype = '??'
            for match in find_sequence_in_string(sequence,line):
                match_string = match.group(2)
##                print('hi')
##                print(match.group(0))
##                print('1:',match.group(1),'2:',match.group(2),sep='')
                start = match.start(2)+line_position
                end = start+len(match_string)
                ## print(start,end,match_string)
                start_end_key = str(start)+'to'+str(end)
                if start_end_key in entity_start_end_dictionary:
                    jargon_found.append([start-line_position,end-line_position,entity_start_end_dictionary[start_end_key]])
                else:
                    jargon_key_number = global_key_number
                    global_key_number = 1+ global_key_number
                    if POS:
                        pass
                    elif re.search('[^iu\']s$',match_string):
                        POS = 'NNS'
                    else:
                        POS = 'NN'
                    jargon_entity = {'id':'J'+str(jargon_key_number),'start':start,'end':end,'text':match_string,\
                                         'type':'JARGON','comment':'AUTOMATICALLY GENERATED','POS':POS,'subtype':subtype}
                    jargon_found.append([start-line_position,end-line_position,jargon_key_number])
                    jargon_dictionary[jargon_key_number] = jargon_entity
                    entity_start_end_dictionary[start_end_key] = jargon_key_number
    if len(jargon_found)>1:
        jargon_found.sort()
    ## given pairs of unrecorded jargon that are sufficiently close together, such that 
    ## they match some abbreviation pair, add this abbreviation relation
        for number in range(1, len(jargon_found)):
            ## these are sorted by start position
            previous_jargon = jargon_found[number-1]
            current_jargon = jargon_found[number]
            ## print(previous_jargon,current_jargon)
            relation = propose_jargon_relation(previous_jargon,current_jargon,line)
            ## previous_jargon's start is necessarily less than or equal to current_jargon's start
            ##  PE < CE, PE > CA
            if (number > 1) and ((previous_jargon[1] < current_jargon[1] \
                                  and previous_jargon[1]>current_jargon[0]) \
                                 ## previous end is in the middle of current jargon
                                 or ((current_jargon[0] < previous_jargon[1]) \
                                     and (current_jargon[0] > previous_jargon[0]))
                                 ## current start is in the middle of previous jargon
                                 ):
                ## [big [bad [wolf]]] Exemplify(big bad wolf, bad wolf) and Exemplify(bad wolf, wolf)
                ## if jargons overlap, look at a previous jargon
                two_jargons_back = jargon_found[number-2]
                ## print(two_jargons_back,current_jargon)
                if two_jargons_back[1]<current_jargon[0]: ## try previous jargon only if it doesn't overlap
                    propose_jargon_relation(two_jargons_back,current_jargon,line)




def value_unify(value1,value2):
    ## other defaults can be added
    if value1 == '??':
        return(value2)
    elif value2 == '??':
        return(value1)
    elif value1 in ['NNS']:
        return(value1)
    elif value2 in ['NNS']:
        return(value2)
    elif value1 in ['NN']:
        return(value1)
    elif value2 in ['NN']:
        return(value2)
    else:
        return(value1)

def number_of_words(word_string):
    ## how many spaces or hyphens + 1 for the end of line
    ## items = word_end_boundary.findall(words)
    items = remove_empties(word_split_pattern.split(word_string))  ## use same splitter as the elsewhere
    return(len(items))
    

def make_jargon_lookup_tables():
    global longest_jargon_term
    longest_jargon_term = 0
    abbreviate_output_dictionary = {}
    jargon_output_dictionary = {}
    for relation_num in relation_dictionary:
        relation = relation_dictionary[relation_num]
        if relation['type'] == 'ABBREVIATE':
            ARG1,ARG2 = relation['ARG1'],relation['ARG2']
            if 'ARG3' in relation and relation['ARG3'] == 'ALIAS':
                ALIAS = True
            else:
                ALIAS = False
            ARG1 = ARG1.upper()
            ARG2 = ARG2.upper()
            if ARG1 in abbreviate_output_dictionary:
                entry = abbreviate_output_dictionary[ARG1]
                if ALIAS:
                    if 'ALIAS' in entry:
                        if not (ARG2 in entry['ALIAS']):
                            entry['ALIAS'].append(ARG2)
                    else:
                        entry['ALIAS']=[ARG2]                         
                elif 'ARG2' in entry:
                    if not (ARG2 in entry['ARG2']):
                        entry['ARG2'].append(ARG2)
                else:
                    entry['ARG2'] = [ARG2]
            else:
                ARG1 = ARG1.upper()
                ARG2 = ARG2.upper()
                if ALIAS:
                    abbreviate_output_dictionary[ARG1]={'ALIAS':[ARG2]}
                else:
                    abbreviate_output_dictionary[ARG1]={'ARG2':[ARG2]}
    for jargon_index in jargon_dictionary:
        jargon_instance = jargon_dictionary[jargon_index]
        jargon_string = jargon_instance['text'].upper()
        jargon_subtype = jargon_instance['subtype']
        jargon_pos = jargon_instance['POS']
        length = number_of_words(jargon_string)
        if longest_jargon_term < length:
            longest_jargon_term = length
        if jargon_string in jargon_output_dictionary:
            entry = jargon_output_dictionary[jargon_string]
            if not (jargon_subtype == entry['subtype']):
                jargon_subtype == value_unify(jargon_subtype,entry['subtype'])
            if not (jargon_pos == entry['POS']):
                jargon_pos == value_unify(jargon_pos, entry['POS'])
        else:
            jargon_output_dictionary[jargon_string]={'POS':jargon_pos,'subtype':jargon_subtype}                 
    return(longest_jargon_term,abbreviate_output_dictionary,jargon_output_dictionary)

def fill_entity_start_end_dictionary():
    global entity_start_end_dictionary
    for number in jargon_dictionary:
        entity = jargon_dictionary[number]
        if 'start' in entity and 'end' in entity:
            entity_start_end_dictionary[str(entity['start'])+'to'+str(entity['end'])]=int(entity['id'][1:])
    for number in enamex_dictionary:
        entity = enamex_dictionary[number]
        if 'start' in entity and 'end' in entity:
            entity_start_end_dictionary[str(entity['start'])+'to'+str(entity['end'])]=int(entity['id'][1:])
            
def fill_entity_pair_relation_dictionary():
    global entity_pair_relation_dictionary
    for key in relation_dictionary:
        entry = relation_dictionary[key]
        if ('ARG1_ID' in entry) and ('ARG2_ID' in entry):
            entity_pair_relation_dictionary[entry['ARG1_ID']+'and'+entry['ARG2_ID']]=key
        



    

# def record_annotation_information_from_file(infile):
#     global jargon_dictionary
#     global enamex_dictionary
#     global citation_dictionary
#     global relation_dictionary
#     global abbreviate_dictionary
#     global entity_start_end_dictionary
#     global entity_pair_relation_dictionary
#     global jargon_term_dict
#     relations,entities=get_relation_list(infile)
    
def fill_relation_dictionary (relation_list):
    global global_relation_number
    global relation_dictionary
    global_relation_number = 0
    relation_number = 0
    for relation_list in relation_list:
        relation = relation_list[2][1]
        if 'fromID' in relation:
            relation['ARG1_ID']=relation['fromID']
            relation['ARG1']=relation['fromText']
        if 'toID' in relation:
            relation['ARG2_ID']=relation['toID']
            relation['ARG2']=relation['toText']
        relation_number = int(relation_list[2][0][1:])
        relation_dictionary[relation_number]=relation
        if relation_number > global_relation_number:
            global_relation_number = relation_number
    global_relation_number = global_relation_number + 1

def fill_entity_dictionaries (entity_dictionary):
    global jargon_dictionary
    global enamex_dictionary
    global global_key_number
    jargon_dictionary.clear()
    enamex_dictionary.clear()
    global_key_number = 0
    for id_number in entity_dictionary:
        global_number = int(id_number[1:])
        if global_number > global_key_number:
            global_key_number=global_number
        if id_number[0]=='J':
            jargon_dictionary[global_number]=entity_dictionary[id_number]
        elif id_number[0]=='E':
            enamex_dictionary[global_number]=entity_dictionary[id_number]
        else:
            error("This file is problematic for fill_entity_dictionary")
    global_key_number = global_key_number+1

def path_merge (directory,file):
    if directory[-1] == os.sep:
        return(directory+file)
    else:
        return(directory+os.sep+file)

def lookup_entity_type(entity_id):
    if len(entity_id)<2:
        return('None',False)
    elif entity_id[0] == 'J':
        return('JARGON',False)
    elif entity_id[0]=='E':
        ## currently only
        number = int(entity_id[1:])
        if 'type' in enamex_dictionary[number]:
            ## if non-citation
            return(enamex_dictionary[number]['type'],False)
        else:
            entity_id = enamex_dictionary[number][3]
            out_type = 'CITATION'
            return(out_type,entity_id)

def clean_up_output_string (string):
    return(re.sub('[ 	'+os.linesep+']+',' ',string))

def bad_jargon(jargon):
    return(re.search('(19[89][0-9])|(20[01][0-9])|[\[=]|((^| )and($| ))|[\[\]:“"”\`\'‘]',jargon))

def OK_jargon(jargon):
    OK = (type(jargon) == str) and (len(jargon)>1) and re.search('[^\W\d]',jargon) and not (bad_jargon(jargon))
    return(OK)

def OK_abbreviate(relation):
    return(OK_jargon(relation['ARG1']) and OK_jargon(relation['ARG2']) and (relation['ARG1_ID'][0]=='J'))
    
def balance_paren(instring):
    if len(instring)>0 and (instring[-1] == ')') and (not '(' in instring):
        instring = instring[:-1]
    instring = instring.replace('(','\(').replace(')','\)')
    return(instring)

def choose_context_output(ARG1,ARG2,output):
    new_list = []
    length = 0
    for item in output:
        lower = item.lower()
        if re.search(ARG1,lower) and re.search(ARG2,lower):
            new_list.append(item)
    if len(new_list) > 1:
        return(new_list)
    elif len(new_list) == 0:
        new_list = output[:1]
    lower_item = new_list[0].lower()
    if re.search(ARG1,lower_item):
        need = ARG2
    else:
        need = ARG1
    for item in output:
        lower = item.lower()
        if re.search(need,lower):
            new_list.append(item)
            return(new_list)
    new_list.append(output[-1])
    return(new_list)

def replace_re_characters(string):
    return(re.sub('[\^?$!+*]','.',string))

def get_context_for_args(relation,inpath):
    ARG1 = balance_paren(relation['ARG1'].strip('\t '+os.linesep))
    ARG2 = balance_paren(relation['ARG2'].strip('\t '+os.linesep))
    ARG1 = replace_re_characters(ARG1)
    ARG2 = replace_re_characters(ARG2)
    ARG1_output = []
    ARG2_output = []
    output = []
    ## print(1,ARG1,2,ARG2)
    ## print(inpath)
    with open (inpath,'r') as instream:
        bigger_line = ''
        for bigline in instream:
             bigger_line=bigger_line+bigline
        for line,xml_tag,start_or_stop in break_up_big_line3(bigger_line):
            line = remove_extra_spaces(remove_xml(line))
            pattern = False
            if (line != '') and ((ARG1 !='') or ARG2 !=''):
                try:
                    pattern = re.search('(^|[\W])(('+ARG1+')|('+ARG2+'))($|[\W])',line)
                except:
                    print('ARG1',ARG1)
                    print('ARG2',ARG2)
                    print('line',line)
                    print('Bad Pattern',pattern)
            if pattern:
                out = get_context_string(line,pattern.start(),pattern.end())
                if pattern.group(3) == ARG1:
                    if len(ARG1_output) < 2:
                        ARG1_output.append(out)
                else:
                    if len(ARG2_output) < 2:
                        ARG2_output.append(out)                
            if (len(ARG1_output) > 1) and (len(ARG2_output) > 1):
                output=ARG1_output[:]
                output.extend(ARG2_output)
                output = choose_context_output(ARG1.lower(),ARG2.lower(),output)
                return(output)
        if (len(ARG1_output) == 0) and (len(ARG2_output) == 0):
            return(False)
        elif len(ARG1_output) == 0:
            return(ARG1_output)
        elif len(ARG2_output) == 0:
            return(ARG2_output)
        else:
            output = ARG1_output[:]
            output.extend(ARG2_output)
            output=choose_context_output(ARG1.lower(),ARG2.lower(),output)
            return(output)

def remove_capitalization_variants(forms):
    output = []
    for form in forms:
        if form.islower():
            output.append(form)
    for form in forms:
        if not(form.lower() in output):
            output.append(form)
    return(output)

def choose_best_example_instances(instances,number,keyterm,abbreviation):
    output = []
    if (len(instances)<= number):
        for instance in instances:
            output.append(instance[0])
        return(output)
    has_abbreviation = []
    other = []
    for instance in instances:
        ## print(instance)
        if instance[1]:
            has_abbreviation.append(instance[0])
        else:
            other.append(instance[0])
    for num in range(4):
        if (len(other)>0) and (len(output)<4):
            output.append(other.pop())
        if (len(has_abbreviation) > 0) and (len(output)<4):
            output.append(has_abbreviation.pop())
        if len(output)>=4:
            break
    return(output)
    
def print_set_of_jargon_words3(outstream,keyterm,dictEntry):
    import math
    if 'ABBREVIATION' in dictEntry:
        abbreviation = dictEntry['ABBREVIATION']
    else:
        abbreviation = False
        print('problem with entry for',keyterm)
    if 'CONTEXT' in dictEntry:
        instances = dictEntry['CONTEXT']
        length = len(instances)
    else:
        length = 0
    instances = choose_best_example_instances(instances,4,keyterm,abbreviation)
    if length>0:
        ## print(abbreviation)
        outstream.write(keyterm+' | Unknown | '+abbreviation[0])
        for instance in instances:
##            if type(instance) == list:
##                print(instance)
            outstream.write(' | '+instance)
        outstream.write(os.linesep)

def increment_full_jargon_dictionary2(relation,input_file,context):
    ## add something to include instances from the corpus
    global full_jargon_dictionary
    ARG1 = relation['ARG1'].strip('\t '+os.linesep)
    ARG2 = relation['ARG2'].strip('\t '+os.linesep)
    entry_key = ARG1.lower()
    if entry_key in full_jargon_dictionary:
        entry = full_jargon_dictionary[entry_key]
        entry['freq'] = entry['freq']+2
        if context:
            if 'CONTEXT' in entry:
                if type(context) == list:
                    entry['CONTEXT'].extend(context)
                else:
                    entry['CONTEXT'].append(context)
            else:
                if type(context) == list:
                    entry['CONTEXT']=context
                else:
                    entry['CONTEXT']=[context]
        if not (input_file in entry['files']):
            entry['files'].append(input_file)
        for token in [ARG1,ARG2]:
            if not (token in entry['forms']):
                entry['forms'].append(token)
    else:
        entry = {'freq':2,'forms':[ARG1,ARG2], 'files':[input_file]}
        if context:
            if type(context) == list:
                entry['CONTEXT']=context
            else:
                entry['CONTEXT'] = [context]
        full_jargon_dictionary[entry_key] = entry

def get_next_id_number ():
    global id_number
    id_number = 1+id_number
    return(id_number)

def make_integrated_id (Class):
    number=get_next_id_number()
    return('NYU_'+Class+str(number))

def find_abbrev_sect(fact_file,patent=False):
    ## ABBREVIATION SECTIONS for patents 
    ## "ACRONYMS AND ABBREVIATIONS"
    ## [0055] SIP Session Initiation Protocol
    ## "Abbreviations"
    ## -- table that is munged by txt conversion, but OK in original form
    ## "Definitions and Abbreviations"
    ## Alternating lines, following [0045], [0046], ...
    ## only sometimes abbreviations -- would need to check
    ## seems rare, don't implement yet
    if patent:
        return(False)
    found = False
    abbrevsect_start = False
    abbrevsect_end = False
    if os.path.isfile(fact_file):
        with open(fact_file,'r') as instream:
            for line in instream:
                line_attributes = get_integrated_line_attribute_value_structure(line,['DOC_SEGMENT','SECTION','STRUCTURE'])
                if ('TITLE' in line_attributes) and abbreviation_title_match.search(line_attributes['TITLE'][0]) \
                        and ('START' in line_attributes) and ('END' in line_attributes):
                    ## print(line_attributes['START'],line_attributes['END'])
                    found = True
                    abbrevsect_start,abbrevsect_end = line_attributes['START'],line_attributes['END']
                    break
            while not((abbrevsect_start==False) or (type(abbrevsect_start) == int)):
                if type(abbrevsect_start) == list:
                    abbrevsect_start = abbrevsect_start[0]
                elif (type(abbrevsect_start)  == str) and abbrevsect_start.isnumeric():
                    abbrevsect_start = int(abbrevsect_start)
                elif type(abbrevsect_start) == int:
                    print('error: ????')
                    abbrevsect_start = False
                    abbrevsect_end = False
                else:
                    abbrevsect_start = False
                    abbrevsect_end = False
            while not((abbrevsect_end==False) or (type(abbrevsect_end) == int)):
                if type(abbrevsect_end) == list:
                    abbrevsect_end = abbrevsect_end[0]
                elif (type(abbrevsect_end)==str) and abbrevsect_end.isnumeric():
                    abbrevsect_end = int(abbrevsect_end)
                elif type(abbrevsect_end) == int:
                    print('error: ????')
                    abbrevsect_start = False
                    abbrevsect_end = False
                else:
                    abbrevsect_start = False
                    abbrevsect_end = False
            return(abbrevsect_start,abbrevsect_end)
    else:
        return(False,False)

def make_integrated_entity(entity_type,string,begin,end):
    if entity_type == 'JARGON':
        return({'CLASS':entity_type,'ID':make_integrated_id(entity_type),'START':begin,'END':end,'TEXT':string})
    elif entity_type in ['ORGANIZATION','PERSON','URL','EMAIL','GPE']:
        return({'CLASS':'ENAMEX','TYPE':entity_type,'ID':make_integrated_id('ENAMEX'),'START':begin,'END':end,'TEXT':string})
    else:
        print('No such entity type:',entity_type)

def integrated_process_abbreviation_section(line,position,waiting):
    ## print(line,position,waiting)
    global abbreviation_section_type
    output = []
    if abbreviation_section_type != 'table':
        pattern = abbreviation_table_entry_pattern.search(line)
    else:
        pattern = False
    if pattern:
        if not abbreviation_section_type:
            abbreviation_section_type = 'pattern'
        while pattern:
            ARG2_string = pattern.group(1)
            ARG2_begin = position+pattern.start(1)
            ARG2_end = position+pattern.end(1)
            ARG1_string = pattern.group(2)
            ARG1_begin = position+pattern.start(2)
            ARG1_end = position+pattern.end(2)
            relation_start = min(ARG1_begin,ARG2_begin)
            relation_end = max(ARG1_end,ARG2_end)
            organization = False
            output_type = classify_abbreviated_string(ARG1_string)
            ARG1 = make_integrated_entity(output_type,ARG1_string,ARG1_begin,ARG1_end)
            ARG2 = make_integrated_entity(output_type,ARG2_string,ARG2_begin,ARG2_end)
            if ARG1 and ARG2:
                output.extend([ARG1,ARG2,{'CLASS':'RELATION','TYPE':'ABBREVIATE','ID':make_integrated_id('RELATION'),'START':relation_start,'END':relation_end,'ARG1':ARG1['ID'],'ARG2':ARG2['ID'],'GRAM_SIGNAL':'TABLE'}])
            pattern = abbreviation_table_entry_pattern.search(line,pattern.end(2))
        waiting = 'pattern'
        return(output,waiting)
    elif waiting:
        if waiting == 'pattern':
            return(False,False)
        elif line.strip(' ') == '':
            return(False,waiting)
        elif type(waiting) == list:
            if abbreviation_section_type != 'pattern':
                pattern = re.search('^ *([^ ]+|[^ ].*[^ ]) *$',line)
            if pattern:
                if not abbreviation_section_type:
                    abbreviation_section_type = 'table'
                ARG2_string,ARG2_begin,ARG2_end = waiting
                ARG1_string = pattern.group(1)
                ARG1_begin = position+pattern.start(1)
                ARG1_end = position+pattern.end(1)
                output_type = classify_abbreviated_string(ARG1_string)
                ARG1 = make_integrated_entity(output_type,ARG1_string,ARG1_begin,ARG1_end)
                ARG2 = make_integrated_entity(output_type,ARG2_string,ARG2_begin,ARG2_end)
                relation_start = min(ARG1_begin,ARG2_begin)
                relation_end = max(ARG1_end,ARG2_end)
                if ARG1 and ARG2:
                    output.extend([ARG1,ARG2,{'CLASS':'RELATION','TYPE':'ABBREVIATE','ID':make_integrated_id('RELATION'),'START':relation_start,'END':relation_end,'ARG1':ARG1['ID'],'ARG2':ARG2['ID'],'GRAM_SIGNAL':'TABLE'}])
            waiting = False
            return(output,waiting)            
        else:
            raise Exception('Debug process_abbreviation_section'+os.linesep+line)
    else:
        pattern = re.search('^ *([^ ]+|[^ ].*[^ ]) *$',line)
        if pattern:
            ARG2_string = pattern.group(1)
            ARG2_begin = position+pattern.start(1)
            ARG2_end = position+pattern.end(1)
            if not re.search('[a-z]',ARG2_string,re.I):
                return(False,False)
            elif ' ' in ARG2_string:
                return(False,False)
            else:
                return([],[ARG2_string,ARG2_begin,ARG2_end])
        else:
            return(output,waiting)

def ok_inbetween_abbreviation_string(string):
    word_list = remove_empties(word_split_pattern.split(string))
    ## word_list = [word for word in word_list if word != '']
    if len(word_list) < 3:
        return(True)
    else:
        return(False)
    
def lookup_abbreviation(abbreviation,line,end,file_position,backwards_borders = False):
    if len(abbreviation)>1 and abbreviation[0] in '\'"“`':
        abbreviation2 = abbreviation[1:]
        one_off = True
    else:
        one_off = False
        abbreviation2 = abbreviation
    if re.search('[-/]',abbreviation2):
        abbreviation2 = re.sub('[-/]','',abbreviation2)   
    key = abbreviation2.upper()
    output = []
    search_string = regularize_match_string1(line[:end])
    maxlength = 0
    if key in abbreviate_dictionary:
        entry = abbreviate_dictionary[key]
        ## print(entry)
        ## print(search_string)
        for fulltext_pair in entry:
            add_s = False
            position = search_string.rfind(fulltext_pair[0])
            if backwards_borders and (position != -1):
                match_end = (position+len(fulltext_pair[0]))
                len_difference = match_end-len(line)
                if len_difference>0:
                    end=backwards_borders[1]+file_position-len_difference
                else:
                    end = backwards_borders[1]+file_position
                begin = backwards_borders[0]+file_position
                out_type = fulltext_pair[1]
                out_string = line[:match_end]
                output=[begin,end,out_string,out_type,one_off]
            elif (position != -1):
                match_end = (position+len(fulltext_pair[0]))
                if (match_end<len(search_string)) and (search_string[match_end] == 'S'):
                    add_s = True
                    match_end = 1+match_end
                if (match_end<len(search_string)) and (re.search('[A-Z]',search_string[match_end])):
                    position = -1
                if position != -1:             
                    out_string = line[position:match_end]
                    if ok_inbetween_abbreviation_string(search_string[position+len(fulltext_pair[0]):]) and \
                       ((not output) or (len(out_string) > maxlength)):
                        maxlength = len(out_string)
                        arg_class = fulltext_pair[1]
                        begin = position+file_position
                        end = begin+len(out_string)
                        out_type = fulltext_pair[1]
                        # ARG1 = make_integrated_entity(arg_class,out_string,position+file_position,position+len(out_string)+file_position)
                        # ARG2 = make_integrated_entity(arg_class,abbreviation,end+file_position,end+len(abbreviation)+file_position)
                        ## 5th item is supposed to be True only if the abbreviation begins with a quote mark
                        ## output = [ARG1,ARG2,{'CLASS':'RELATION','TYPE':'ABBREVIATE','ID':make_integrated_id('RELATION'),'ARG1':ARG1['ID'],'ARG2':ARG2['ID'],'GRAM_SIGNAL':'PARENTHESES'},one_off]
                        output = [begin,end,out_string,out_type, one_off]                   
    return (output)

def find_search_end(line,search_end):
    Fail = False
    pattern = re.search('[\w][\W]+$',line[:search_end])
    if pattern:
        if re.search(r'[!:;,.?)\]}]',line[pattern.start():search_end]):
            # the parentheses pattern does not work if there is
            # sentence delimiting or conjunct delimiting punctuation
            # between antecedent and left parenthesis
            Fail = True
        return((pattern.start()+1),Fail)
    else:
        return(search_end,Fail)

def ill_formed_abbreviation_pattern(abbreviation_pattern):
    ## attempts to identify parentheses that do not contain abbreviations
    ## first type is of the form (X,Y) (or (X,Y,Z,...) where X and Y are
    ## single characters
    token_list = re.split('[,;]',abbreviation_pattern.group(1))
    out = []
    if len(token_list) > 1:
        for token in token_list:
            token = token.strip(' ')
            if len(token)>0:
                out.append(token)
    if len(out)>1 and (len(out[0])==1) and (len(out[1])==1):
        return(True)
    else:
        return(False)

def adjust_start_for_antecedent(line,start,search_end):
    if start and search_end and (';' in line[start:search_end]):
        return(start+line[start:search_end].rindex(';'))
    else:
        return(start)

def extend_abbreviation_context(pattern, line):
    end = pattern.end()
    if len(line) > end:
        next_character = line[end]
        if next_character in '-': 
        ## possibly find other bad next characters
            return(True)
    return(False)

def OK_abbrev_antec(anteced):
    words = re.split('[ .-]+',anteced)
    all_one_letter = True
    left_parens = anteced.count('(')
    right_parens = anteced.count(')')  
    for word in words:
        if len(word)>1:
            all_one_letter = False
    return((not all_one_letter) and (left_parens==right_parens) \
           and (left_parens < 2) and (right_parens < 2))

def get_next_abbreviate_relations(previous_line,line,position):
    output = []
    start = 0
    pattern = parentheses_pattern2.search(line,start)
    ## allows for unclosed parenthesis
    more_words = False
    ARG2_begin = False
    ARG2_end = False
    ARG2_string = False
    ARG1_begin = False
    ARG2_end = False
    ARG2_string = False
    output_type = False
    result=False
    Fail = False
    extend_antecedent = False
    last_start = False
    while pattern:
        result = False
        Fail = False
        first_word_break=re.search('[ ,;:]',pattern.group(1))
        if first_word_break:
                abbreviation=pattern.group(1)[:first_word_break.start()]
        else:
            abbreviation=pattern.group(1)
        if abbreviation:
            abbrev_start = re.search('[^/-]',abbreviation)
            if abbrev_start and (abbrev_start.start()>0):
                abbreviation=abbreviation[abbrev_start.start():]
        ## whole pattern goes from ( to ) 
        ## 1st guess at abbreviation is the portion that is after (
        ## and is either: before the first space; or the whole thing
        ## if there is no space
##        if (pattern.start()-start)>50:
##            start = pattern.start()-50
##            if ' ' in line[start:pattern.start()]:
##                start = line.index(' ',start)+1
        search_end = pattern.start()
        search_end,Fail = find_search_end(line,search_end)
        if ill_formed_abbreviation_pattern(pattern) or re.search('^[a-zA-Z]$',abbreviation):
            ## eliminate ill_formed pattern plus all single roman letter abbreviations
            ## the latter are correct sometimes, but rarely useful at all for our purposes
            ## also eliminate cases where the parenthesized item is part of a complex formula of some sort
            ## (wrong abbreviation context)
            Fail = True
        if not Fail:
            if extend_antecedent:
                start = adjust_start_for_antecedent(line,last_start,search_end)
            else:
                start = adjust_start_for_antecedent(line,start,search_end)
            previous_words = remove_empties(word_split_pattern.split(line[start:search_end].rstrip(' ')))
            if (start == 0) and (previous_line != '') and (len(previous_words) < len(abbreviation)):
                more_words = get_more_words(previous_line,(3 + len(abbreviation) - len(previous_words)))
            if more_words and (len(more_words)>0) and (len(abbreviation)>0):
                offset_adjustment= len(previous_line)
                ## print(more_words)
                ## print(previous_words)
                more_words.extend(previous_words)
                result = lookup_abbreviation(abbreviation,previous_line+line,search_end+offset_adjustment,position-offset_adjustment)
                if not result:
                    ## print(1,start,search_end)
                    result = abbreviation_match(abbreviation,more_words,previous_line+line,search_end+offset_adjustment,position-offset_adjustment,False,False)
            if (not result) and (len(previous_words) > 0) and (len(abbreviation)>0):
                result = lookup_abbreviation(abbreviation,line,search_end,position)
                if not result:
                    ## print(2,start,search_end)
                    result = abbreviation_match(abbreviation,previous_words,line,search_end,position,False,False)
            ## print(result)
            if result and ((not OK_jargon(result[2])) or (not OK_abbrev_antec(result[2]))):
                result = False
            if result:
                if result[4]: ## if the abbreviation is one off
                    ARG2_begin=pattern.start()+position+2
                    ARG2_string=abbreviation[1:]
                    ARG2_end = ARG2_begin+len(abbreviation)-1
                else:
                    ARG2_begin = pattern.start()+position+1
                    ARG2_string = abbreviation
                    ARG2_end = ARG2_begin+len(abbreviation)
                ARG1_begin = result[0]
                ARG1_end = result[1]
                ARG1_string = result[2]
                output_type = result[3]
            elif len(abbreviation)==1:
            ## single capital letters divided by spaces, are an alternative match, e.g., (J R A)
            ## Abbreviations can also contain periods
            ## -- we will try removing up to 7 spaces/periods
                abbreviation=re.sub('[. ]','',pattern.group(1),7) ## remove upto 7 spaces/periods from abbreviation
                if (start == 0) and (previous_line != '') and (len(previous_words) < len(abbreviation)):
                    more_words = get_more_words(previous_line,(1 + len(abbreviation) - len(previous_words)))
                    if more_words and (len(more_words)>0):
                        offset_adjustment=len(previous_line)
                        more_words.extend(previous_words)
                        result = lookup_abbreviation(abbreviation,previous_line+line,search_end+offset_adjustment,position-offset_adjustment)
                        if not result:
                            ## print(3)
                            result = abbreviation_match(abbreviation,more_words,previous_line+line,search_end+offset_adjustment,position-offset_adjustment,False,False)
                    else:
                        result = lookup_abbreviation(abbreviation,line,search_end,position)
                        ## print(4)
                        if not result:
                            result = abbreviation_match(abbreviation,previous_words,line,search_end,position,previous_line,more_words)
                if result:
                    if result[4]:
                        ARG2_begin=pattern.start()+position+2
                        ARG2_string=abbreviation[1:]
                    else:
                        ARG2_begin = pattern.start()+position+1
                        ARG2_string = pattern.start(1)
                    ARG2_end = start+pattern.end()-1
                    ARG1_begin = result[0]
                    ARG1_end = result[1]
                    ARG1_string = result[2]
                    output_type = result[3]
            # if context != False:
            #     context_string = get_context_string(line,pattern.start(),pattern.end())
            # else:
            #     context_string=False
            elif ' ' in pattern.group(0):
                ## possibility of a multi-word item in parentheses (antecedent) matching the word right before
                ## the parentheses (abbreviation), i.e., the backwards case
                if pattern.end()>3:
                    previous_word = re.search('([a-zA-ZΑ-ϖ][a-zA-Z0-9-/Α-ϖ]*[a-zA-Z0-9Α-ϖ])[^a-z0-9]$',line[:pattern.start()])
                else:
                    previous_word = False
                if previous_word:
                    abbreviation=previous_word.group(1)
                    antecedent_string = pattern.group(0)[1:-1]
                    result = lookup_abbreviation(abbreviation,antecedent_string,len(pattern.group(0))-2,position,backwards_borders=[previous_word.start(),pattern.end()])
                    if not result:
                        forward_words = remove_empties(word_split_pattern.split(antecedent_string.rstrip(' ')))
                        line_offset = len(pattern.group(0))-2
                        ## line_offset effects begin and end
                        ## *** 57 ***
                        result = abbreviation_match(abbreviation,forward_words,antecedent_string,line_offset,position,previous_line,more_words)
                    if result:
                        ARG1_string = result[2]
                        ARG2_string = abbreviation
                        ARG1_begin = pattern.start()+position+1
                        ARG1_end = ARG1_begin+len(ARG1_string) ## result[1]-1
                        ARG2_begin = previous_word.start()+position ## result[0] ## correct for lookup, but not for calculated
                        ARG2_end =  ARG2_begin+len(ARG2_string)
                        output_type = result[3]
                    ## must adjust offsets for backwards situation
                    ## perhaps provide offsets explicitly (start position = start of first word + offset)
                    ## end position = end position of pattern + offset
            if result:
                ARG1 = make_integrated_entity(output_type,ARG1_string,ARG1_begin,ARG1_end)
                ARG2 = make_integrated_entity(output_type,ARG2_string,ARG2_begin,ARG2_end)
                relation_start = min(ARG1_begin,ARG2_begin)
                relation_end = max(ARG1_end,ARG2_end)
                if ARG1 and ARG2:
                    output.extend([ARG1,ARG2,{'CLASS':'RELATION','TYPE':'ABBREVIATE','ID':make_integrated_id('RELATION'),'START':relation_start,'END':relation_end,'ARG1':ARG1['ID'],'ARG2':ARG2['ID'],'GRAM_SIGNAL':'PARENTHESES'}])
                    ## not currently using context_string or context
        if not result:
            start = pattern.start()+1
        else:
            last_start = start
            start = pattern.end()
        if extend_abbreviation_context(pattern,line):
            extend_antecedent = True
        else:
            extend_antecedent = False
        pattern = parentheses_pattern2.search(line,start)
    return(output)

def write_fact_file(output,outfile):
    global ARG1_NAME_TABLE
    global ARG2_NAME_TABLE
    global FACT_STYLE
    with open(outfile,'w') as outstream:
        keys = ['ID','TYPE','SUBTYPE','START','END','ARG1','ARG2','GRAM_SIGNAL','TEXT_SIGNAL','TEXT']
        if FACT_STYLE=='phase1':
            ENAMEX_keys = ['ID','SUBTYPE','START','END','ARG1','ARG2','GRAM_SIGNAL','TEXT_SIGNAL','TEXT']
        for out in output:
            if (out['CLASS']=='ENAMEX') and (FACT_STYLE=='phase1'):
                outstream.write(out['TYPE'])
                key_list = ENAMEX_keys
            else:
                outstream.write(out['CLASS'])
                key_list = keys
            if out['CLASS'] == 'RELATION':
                if 'SUBTYPE' in out:
                    look_up = out['SUBTYPE']
                else:
                    look_up = out['TYPE']
                ARG1_NAME = ARG1_NAME_TABLE[look_up]
                ARG2_NAME = ARG2_NAME_TABLE[look_up]
            for key in key_list:
                if key in out:
                    value = out[key]
                    # if key == 'ID':
                    #     value = 'NYU_'+out['CLASS']+str(value)
                    if type(value) == int:
                        value = str(value)
                    else:
                        value = '"'+value+'"'
                    outstream.write(' '+key+'='+value)
                    if key == 'ARG1':
                        outstream.write(' ARG1_NAME="'+ARG1_NAME+'"')
                    elif key == 'ARG2':
                        outstream.write(' ARG2_NAME="'+ARG2_NAME+'"') 
            outstream.write(os.linesep)

def bad_abbrev_arg1(text):
    if not re.search('[^\W\d]',text):
        return(True)
    
def bad_abbrev_arg2(text):
    if (not re.search('[^\W\d]',text)) or \
       ((len(text) == 1) and not re.search('[^\W\da-z]',text)):
        return(True)
    
def table_abbreviation_filter(out):
    ## out consists of ARG1, ARG2, relation
    ## print('filter',out[0]['TEXT'],out[1]['TEXT'])
    if bad_abbrev_arg1(out[0]['TEXT']) or bad_abbrev_arg2(out[1]['TEXT']) \
       or (not(len(out[0]['TEXT'])) > (len(out[1]['TEXT']))):
        return(False)
    else:
        return(out)

def integrated_record_abbreviate_dictionary(fulltext,abbreviation,argclass,global_tally=False):
    ## print(fulltext,abbreviation,argclass)
    global abbreviate_dictionary
    ## key = abbreviation.upper()
    key = abbreviation ## use naturally occuring form of abbreviations (otherwise causes problems, e.g., if abbreviation is OR
    value = [regularize_match_string1(fulltext),argclass]
    if key in abbreviate_dictionary:
        if not value in abbreviate_dictionary[key]:
            abbreviate_dictionary[key].append(value)
    else:
        abbreviate_dictionary[key] = [value]
    if type(key) == int:
        key = str(key)
    if global_tally and (not '|' in key) and ((type(value[0])==int) or (not '|' in value[0])):
        compound_key = key+'|'+str(value[0])
        if compound_key in abbreviate_tally:
            abbreviate_tally[compound_key] = abbreviate_tally[compound_key]+1
        else:
            abbreviate_tally[compound_key] = 1

def triplify (inlist):
    if len(inlist)%3!=0:
        print('problem with triplify for:',inlist)
    else:
        output = []
        start = 0
        while start < len(inlist):
            output.append(inlist[start:start+3])
            start = start+3
        return(output)

def bad_patent_line(line):
    if (len(line)>5000) and not(re.search('[a-z]',line)):
        ## print(line[:500])
        return(True)
    # if (len(line)>5000):
    #     print(line[:250],'...',line[-250:])
    #     print('LENGTH',len(line))
    else:
        return(False)     
        
def run_abbreviate_on_arbiter_file(txt_file,fact_file,output_file,tables=True,reset_dictionary=True,produce_output=False,patent=False,print_file=True,global_tally=False):
    global id_number
    id_number = 0
    output = []
    if (not patent) and fact_file:
        abbrevsect_start,abbrevsect_end = find_abbrev_sect(fact_file,patent=patent)
    else:
        abbrevsect_start = False
    global abbreviate_dictionary
    if reset_dictionary:
        abbreviate_dictionary.clear()
    start = 0
    waiting = False
    out = False
    previous_line = False
    all_lines = get_lines_from_file(txt_file)
    abbreviate_output = []  ## the empty set acts like False for if statements
    if abbrevsect_start and abbrevsect_end and tables:
        for line in all_lines:
            line = line.replace(os.linesep,' ')
            end = start + len(line)
            if (start > abbrevsect_start) and (start < abbrevsect_end):
                out,waiting = integrated_process_abbreviation_section(line,start,waiting)
                ### reworking of process_abbreviation_section
                if out:
                    out = table_abbreviation_filter(out)
                if out:
                    abbreviate_output.extend(out)
                    for triple in triplify(out):
                        if triple[1]['CLASS']=='ENAMEX':
                            argtype = triple[1]['TYPE']
                        else:
                            argtype = triple[1]['CLASS']
                        integrated_record_abbreviate_dictionary(triple[0]['TEXT'],triple[1]['TEXT'],argtype,global_tally=global_tally)                 
            elif (start > abbrevsect_end):
                break
            start = end
    start = 0
    ## print(abbreviate_output)
    for line in all_lines:
        ## print(line)
        line = line.replace(os.linesep,' ')
        end = start + len(line)
        if abbrevsect_start and abbrevsect_end and (start > abbrevsect_start) and (start < abbrevsect_end):
            if tables and abbreviate_output:
                output.extend(abbreviate_output) ## add in abbreviation output once
                abbreviate_output = False
            else:
                pass
        elif patent and bad_patent_line(line):
            pass
        else:
            out = get_next_abbreviate_relations(previous_line,line,start)
            ## print(out)
            if out:
                for triple in triplify(out):
                    if triple[1]['CLASS'] == 'ENAMEX':
                        argtype = triple[1]['TYPE']
                    else:
                        argtype = triple[1]['CLASS']
                    integrated_record_abbreviate_dictionary(triple[0]['TEXT'],triple[1]['TEXT'],argtype,global_tally=global_tally)
            ### reworking of record_preprocessed_relations
        if out:
            output.extend(out)
        start = end
        previous_line = line
    if print_file:
        write_fact_file(output,output_file)
    if produce_output:
        return(output)

def abbreviate_facts_from_directory(inpath,tables=True,version=''):
    if not version:
        version = ''
    if os.path.isdir(inpath):
        for new_path in os.listdir(inpath):
            full_new_path = path_merge(inpath,new_path)
            abbreviate_facts_from_directory(full_new_path,tables=tables,version=version)
    elif os.path.isfile(inpath) and re.search(r'[.]txt$', inpath):
        fact_file = inpath[:-3]+'fact'
        out_file = inpath[:-3]+'abbreviate'+version
        run_abbreviate_on_arbiter_file(inpath,fact_file,out_file,tables=tables)

def get_forward_substring(words,line):
    if len(words)==0 or words[0] == '':
        ## print('empty',words)
        return(False,False)
##    if words[0]=='FR':
##        print(words,line)
    pattern_string = '^[^\w@]*('+words[0]
    for num in range(1,len(words)):
        if words[num] == '':
            return(False,False)
        pattern_string = pattern_string+'[^\w@]+'+words[num]
    pattern_string=pattern_string+')'
    pattern = re.search(pattern_string,line,re.I)
    if pattern:
        return(pattern.group(1),pattern.start())
    else:
        return(False,False)

def enter_context_in_jargon_entry(context,match_string,abbrev=False):
    ## add context strings for antecedents only
    global full_jargon_dictionary
    entry = full_jargon_dictionary[match_string.upper()]
    if 'CONTEXT' in entry:
        if not([context,abbrev] in entry['CONTEXT']):
            entry['CONTEXT'].append([context,abbrev])
    else:
        entry['CONTEXT']=[[context,abbrev]]
    
def add_context_to_full_jargon_start_with_word(start,max_length,previous_words,previous_line,words,line):
    global full_jargon_dictionary
    forward_start = False
    if previous_words:
        start_length = len(previous_words)+1
        start_string = get_word_substring_at_end(previous_words,previous_line,no_check=True)
    else:
        start_length = 1
        start_string = ''
    for length in range(start_length,max_length+1):
        forward_string,forward_start = get_forward_substring(words[:length],line[start:])
        if forward_string:
            forward_start = forward_start+start+len(previous_line)
            if previous_words:
                match_string = regularize_match_string1(start_string+' '+forward_string)
            else:
                match_string = regularize_match_string1(forward_string)
            ## print(match_string)
            if (match_string in full_jargon_dictionary) or \
               (match_string in abbreviate_dictionary):
                if previous_words:
                    start_context = len(previous_line)-len(start_string)
                else:
                    start_context = forward_start
                end_context = forward_start+len(forward_string)
                context = get_context_string(previous_line.strip(os.linesep)+' '+line,start_context,end_context)
                if match_string in full_jargon_dictionary:
                    enter_context_in_jargon_entry(context,match_string)
                else:
                    for pair in abbreviate_dictionary[match_string]:
                        if pair[1] == 'JARGON':
                            enter_context_in_jargon_entry(context,pair[0],abbrev=True)
            else:
                pass
    if not previous_words:
        if len(words)==0:
            return(len(line))
        next_space_pattern = re.search(words[0]+'[^\w@]+',line[start:])
        if next_space_pattern:
            next_word_position = next_space_pattern.end()+start
            return(next_word_position)
        else:
            return(len(line))
    
def add_context_to_full_jargon(start,words,line,previous_words,previous_line,max_length):
    ## only need start if I need to provide positions in documents (possibly later)
    if previous_words and (len(previous_words) > 5):
        previous_words = previous_words[-5:]
        position = 0-len(previous_words)
    else:
        position = 0
    relative_start = 0
    while(position < len(words)):
        if position < 0:
            add_context_to_full_jargon_start_with_word(start,max_length,previous_words[:position],previous_line,words,line)
        else:
##            if words[0] in ['Heavy','Chain','FR']:
##                print(position,relative_start,previous_line,words,line)
            relative_start = add_context_to_full_jargon_start_with_word(relative_start,max_length,False,previous_line,words[position:],line)
        position = 1 + position    
 
def get_previous_line_position(line,number):
    position = len(line)
    count = 0
    for num in range(number):
        pattern = space_and_word_from_end.search(line,0,position)
        if (not pattern):
            if re.search('[\w]',line[:position]):
                return(0,count+1)
            else:
                return(0,count)
        elif (pattern.start()==0):
            return(0,count+1)
        else:
            position = pattern.start()
            count=count+1
    return(pattern.end(1),count)

def get_previous_line_positions(line,number):
    position = len(line)
    count = 0
    output = []
    for num in range(number):
        pattern = space_and_word_from_end.search(line,0,position)
        if (not pattern):
            if re.search('[\w]+[^:.;,]$',line[:position]):
                output.append(0)
                output.reverse()
                return(output,count+1)
            else:
                return(output,count)
        elif (pattern.start()==0):
            output.append(0)
            return(output,count+1)
        else:
            position = pattern.start()
            count=count+1
            output.append(pattern.end(1))
    return(output,count)

def get_forward_line_position(line,start,number,start_or_end):
    ## should start_or_end make a difference?
    position = start
    for num in range(number):
        pattern = word_and_space.search(line,start)
        if (not pattern):
            return(len(line))
        elif (pattern.end()==len(line)):
            return(pattern.end(1))
        else:
            start = pattern.end(1)
    return(start)

def get_forward_line_positions(line):
    if line:
        if re.search('^[\w]',line):
            output = [0]
        else:
            output = []
        patterns = word_and_space.finditer(line)
        output.extend([x.end() for x in patterns])
        if len(output)>0:
            return(output)
        else:
            return(False)
    else:
        return(False)


def increment_total_instances (entry):
    if 'FULL_FORM_COUNT' in entry:
        entry['FULL_FORM_COUNT'] = entry['FULL_FORM_COUNT']+1
    else:
        entry['FULL_FORM_COUNT'] = 1

def increment_abbrev_instances (entry):
    if 'ABBREV_COUNT' in entry:
        entry['ABBREV_COUNT'] = entry['ABBREV_COUNT']+1
    else:
        entry['ABBREV_COUNT'] = 1  
    
def add_context_to_full_jargon_based_on_positions(line,start,end_list,context,tally):
    for position in end_list:
        ## efficiency could be increased if we avoided regularizing the same strings
        ## over and over again
        match_string = regularize_match_string(line[start:position])
        if (match_string in full_jargon_dictionary):
            if context:
                context_string = get_context_string(line,start,position)
                enter_context_in_jargon_entry(context_string,match_string)
            if tally:
                increment_total_instances(full_jargon_dictionary[match_string])
        elif (match_string in abbreviate_dictionary):
            if context:
                context_string = get_context_string(line,start,position)
            for pair in abbreviate_dictionary[match_string]:
                if pair[1] == 'JARGON':
                    if context:
                        enter_context_in_jargon_entry(context_string,pair[0],abbrev=True)
                    if tally:
                        increment_abbrev_instances(full_jargon_dictionary[pair[0]])
    
def add_context_to_full_jargon2(line,previous_line,max_length,context=True,tally=False):
    ## this version advances by positions that correspond to the next word break
    ## this might be less compute-time-intensive
    if previous_line:
        prev_positions,prev_word_count = get_previous_line_positions(previous_line,5)
        ## print(prev_positions)
    else:
        prev_word_count = 0
    line = line.strip(os.linesep)
    line_positions = get_forward_line_positions(line)
    if line_positions:
        line_word_count = len(line_positions) 
        current_word_count=min((1+max_length-prev_word_count),line_word_count)
    if line_positions and (prev_word_count > 0):
        previous_line = previous_line.strip(os.linesep)+' '
        previous_length = len(previous_line)
        line_positions_prime = [x+previous_length for x in line_positions]
        big_line = previous_line+line
        for prev_position in range(prev_word_count):
            start = prev_positions[prev_position]
            end_list = line_positions_prime[1:current_word_count]
            ## print(end_list)
            add_context_to_full_jargon_based_on_positions(big_line,start,end_list,context,tally)                
            current_word_count = current_word_count+1
    elif(line_positions):
        big_line = line
        line_positions_prime=line_positions
    ## print(line_word_count)
##    if 'exclusive-OR' in line:
##        print(big_line)
##        print(line_positions_prime)
##        print(line_word_count)
    if line_positions:
        ## print(line_positions_prime)
        line_word_count = len(line_positions_prime)
        for start_pointer in range(line_word_count):
            ## print(start_pointer)
            start_position = line_positions_prime[start_pointer]
            ## print('hello')
            end_pointer = min((start_pointer+max_length+1),line_word_count)
            end_list = line_positions_prime[start_pointer+1:end_pointer]
            if len(end_list)> 0:
                add_context_to_full_jargon_based_on_positions(big_line,start_position,end_list,context,tally)

def abbrev_check(anteced,abbrev):
    words = remove_empties(word_split_pattern.split(anteced))
    result = abbreviation_match(abbrev,words,anteced,len(anteced)+4,0,'',False)
    if result:
        return(True)
    
def edit_anteced(anteced,abbrev):
    start = 0
    pattern = parentheses_pattern2.search(anteced,start)
    if (anteced.startswith(abbrev.upper())) and abbrev_check(anteced[(len(abbrev)):],abbrev):
        return(anteced[(len(abbrev)):])
    elif not pattern:
        return(anteced)
    elif pattern.start() == start:
        return(False)
    elif pattern.end() == len(anteced):
        return(anteced)
    else:
        words = remove_empties(pattern.group(1).split(' '))
        if (len(words)==1):
            anteced = (anteced[:pattern.start()].rstrip(' ')+anteced[pattern.end():]).rstrip(' .,')
        ## if exactly 1 word, delete whole paren, along with immediately preceding spaces
        ## then trim punctuation off the end of the result
        return(anteced)

    
def update_full_jargon_dictionary(txt_file,fact_file,context=True,tally=False,patent=False):
    global full_jargon_dictionary
    global abbreviate_dictionary  ## key = abbreviation (all caps), value = list of [full_string, argtype] pairs
    max_length = 0
    jargon_this_file = []
    for key in abbreviate_dictionary:
        is_jargon = False
        antecedents = []
        for antecedent_pair in abbreviate_dictionary[key]:
            if antecedent_pair[1] == 'JARGON':
                is_jargon = True
                words = remove_empties(word_split_pattern.split(antecedent_pair[0]))
                length = len(words)
                if length > max_length:
                    max_length = length
                anteced = remove_extra_spaces(antecedent_pair[0])
                if '(' in anteced:
                    anteced = edit_anteced(anteced,key)
                if anteced:
                    anteced = anteced.strip('\'"')
                    antecedents.append(anteced)
            ## if entry is of the right type
            ## for all terms, if there are no current
            ## jargon entries, intialize jargon entries
            ## in all cases, add 1 to the number files using
            ## jargon/abbrev
        if is_jargon:
            for ant in antecedents:
                if ant in full_jargon_dictionary:
                    if ('ABBREVIATION' in full_jargon_dictionary[ant]):
                        if not (key in full_jargon_dictionary[ant]['ABBREVIATION']):
                            full_jargon_dictionary[ant]['ABBREVIATION'].append(key)
                    else:
                        full_jargon_dictionary[ant]['ABBREVIATION'] = [key]
                    if not (ant in jargon_this_file):
                        jargon_this_file.append(ant)
                        full_jargon_dictionary[ant]['FILE_COUNT']=full_jargon_dictionary[ant]['FILE_COUNT']+1
                else:
                    full_jargon_dictionary[ant]={'ABBREVIATION':[key],'FILE_COUNT':1}
                    jargon_this_file.append(ant)
    if patent or (not fact_file):
        abbrevsect_start,abbrevsect_end = False,False
    else:
        abbrevsect_start,abbrevsect_end = find_abbrev_sect(fact_file)        
    start = 0
    ## print(jargon_this_file)
    ## print(full_jargon_dictionary)
    previous_words = False
    previous_line = False
    if context or tally:
        with open(txt_file,'r') as instream:
            for line in instream:
                if (not abbrevsect_start) or (abbrevsect_start > start) or (abbrevsect_end < start):
                    ## words = remove_empties(word_split_pattern.split(line))
                    ## add_context_to_full_jargon(start,words,line,previous_words,previous_line, max_length)
                    ## find and add context to dictionary as appropriate
                    add_context_to_full_jargon2(line,previous_line,max_length,context=context,tally=tally)
                else:
                    words = False
                start = start+len(line)
                ## previous_words = words
            previous_line = line
            
def fill_full_jargon_dictionary3(inpath,version='4',context=False,tally=False):
    global full_jargon_dictionary
    ## abbreviate_dictionary.clear()
    if os.path.isdir(inpath):
        for new_path in os.listdir(inpath):
            full_new_path=path_merge(inpath,new_path)            
            fill_full_jargon_dictionary3(full_new_path,version=version,context=context,tally=tally)
    elif os.path.isfile(inpath) and re.search('\.txt$',inpath):
        input_file = short_file(inpath)
        run_abbreviate_on_arbiter_file(inpath,inpath[:-3]+'fact',inpath[:-3]+'abbreviate'+version,reset_dictionary=True)
        update_full_jargon_dictionary(inpath,inpath[:-3]+'fact',context=context,tally=tally)


def acquire_jargon_from_directory3(inpath,version='4',context=False,tally=False):
    global full_jargon_dictionary
    global abbreviate_dictionary
    full_jargon_dictionary = {}
    ## get all abbreviate relations from all files and use them to fill full_jargon_dictionary, including frequency info
    fill_full_jargon_dictionary3(inpath,version=version,context=context,tally=tally)
    outlist = []
    for key in full_jargon_dictionary:
        ## if full_jargon_dictionary[key]['freq']>2:
        if context:
            if 'CONTEXT' in full_jargon_dictionary[key]:
                outlist.append(key)
        elif tally:
            if ('FULL_FORM_COUNT' in full_jargon_dictionary[key]) or \
              ('ABBREV_COUNT' in full_jargon_dictionary[key]):
              outlist.append(key)
        else:
            outlist.append(key)
    return(outlist)

def print_out_auto_jargon_word_list3(inpath,outfile,version='4'):
    global full_jargon_dictionary
    jargonlist = acquire_jargon_from_directory3(inpath,version=version,context=True)
    jargonlist.sort()
    with open(outfile,'w') as outstream:
        for jargon in jargonlist:
        ## This version is geared for Input to Rimma
            print_set_of_jargon_words3(outstream,jargon,full_jargon_dictionary[jargon])

def tuples_value(item):
    if type(item) == list:
        if len(item) == 0:
            return('')
        elif len(item) == 1:
            return(str(item[0]))
        else:
            output = str(item[0])
            for instance in item[1:]:
                output = output+'||'+str(instance)
            return(output)
    else:
        return(str(item))

def lisp_value(item):
    if type(item) == list:
        if len(item) == 0:
            return(False)
        else:
            output = '('+lisp_value(item[0])
            for instance in item[1:]:
                output = output+' '+lisp_value(instance)
            output = output + ')'
            return(output)
    elif type(item) == str:
        if item.isnumeric():
            return(item)
        else:
            return('"'+item+'"')
    else:
        return(str(item))

def acquire_and_print_out_dictionary(inpath,outfile,version='6',tally=False,context=False,format='tuples'):
    ## possible output formats include 'tuples' and 'lisp'
    global full_jargon_dictionary
    full_jargon_dictionary.clear()
    jargonlist = acquire_jargon_from_directory3(inpath,version=version,context=context,tally=tally)
    jargonlist.sort()
    ## keys in dictionary are regularized sequences of words: all
    ## caps, hyphens replaced by spaces, multiple spaces replaced by
    ## single spaces
    entry_attributes = ['ABBREVIATION','FILE_COUNT','FULL_FORM_COUNT','ABBREV_COUNT','CONTEXT']
    with open(outfile,'w') as outstream:
        for jargon in jargonlist:
            entry = full_jargon_dictionary[jargon]
            if format == 'tuples':
                outstream.write(jargon)
                for attribute in entry_attributes:
                    outstream.write('|||')
                    if attribute in entry:
                        if (attribute == 'CONTEXT') and ('ABBREVIATION' in entry):
                            abbrev = entry['ABBREVIATION']
                            if type(abbrev)==list:
                                abbrev=abbrev[0]
                            value = choose_best_example_instances(entry[attribute],4,jargon,abbrev)
                        elif (attribute == 'CONTEXT'):
                            value = entry[attribute]
                            if len(value)>4:
                                value = [item[0] for item in value[:4]]                                
                            else:
                                value = [item[0] for item in value]
                        else:
                            value = entry[attribute]
                        outstream.write(tuples_value(value))
                outstream.write(os.linesep)
            elif format == 'lisp':
                outstream.write('(JARGON :ORTH "'+jargon+'"')
                for attribute in entry:
                    if attribute in entry_attributes:
                        if (attribute == 'CONTEXT') and ('ABBREVIATION' in entry):
                            abbrev = entry['ABBREVIATION']
                            if type(abbrev)==list:
                                abbrev=abbrev[0]
                            value = choose_best_example_instances(entry[attribute],4,jargon,abbrev)
                        elif (attribute == 'CONTEXT'):
                            value = entry[attribute]
                            if len(value)>4:
                                value = [item[0] for item in value[:4]] 
                            else:
                                value = [item[0] for item in value]
                        else:
                             value = entry[attribute]
                        value = lisp_value(value)
                        if value:
                            outstream.write(' '+':'+attribute+' '+value)
                outstream.write(')'+os.linesep)
            
def make_abbreviate_table_from_abbreviate_factfile(abbreviate_file):
    entity_table = {}
    entity_id_table = {}
    with open(abbreviate_file,'r') as instream:
        for line in instream:
            attributes = get_integrated_line_attribute_value_structure(line,['ORGANIZATION','JARGON'])
            if attributes and ('TEXT' in attributes):
                attributes['ID']=attributes['ID'][0]
                TEXT = attributes['TEXT'][0].upper()
                if TEXT in entity_table:
                    entity_table[TEXT]['NUM']=entity_table[TEXT]['NUM']+1
                else:
                    entity_table[TEXT]={'NUM':1,'SYNONYMS':[]}
                entity_id_table[attributes['ID']]=TEXT
    with open(abbreviate_file,'r') as instream:
        for line in instream:
            attributes = get_integrated_line_attribute_value_structure(line,['RELATION'])
            if attributes and attributes['TYPE']=='ABBREVIATE':
                ARG1_TEXT = entity_id_table[attributes['ARG1']]
                ARG2_TEXT = entity_id_table[attributes['ARG1']]
                if not (ARG2_TEXT in entity_table[ARG1_TEXT]['SYNONYMS']):
                    entity_table[ARG1_TEXT]['SYNONYMS'].append(ARG2_TEXT)
                if not (ARG1_TEXT in entity_table[ARG2_TEXT]['SYNONYMS']):
                    entity_table[ARG2_TEXT]['SYNONYMS'].append(ARG1_TEXT)
    return(entity_table)

def abbreviate_facts_from_filelist(input_filelist, output_filelist):
    input_files = open(input_filelist).readlines()
    output_files = open(output_filelist).readlines()
    if len(input_files) != len(output_files):
        print("Lists of input and output files should be of same length.")
        sys.exit(-1)
    for i in range(len(input_files)):
        try:
            txt_file, fact_file,is_patent = input_files[i].strip().split(';')
            output_file = output_files[i].strip()
        except:
            print("Error opening input/output files:")
            print("Input: %s\nOutput: %s" % (input_files[i].strip(), output_files[i].strip()))
        run_abbreviate_on_arbiter_file(txt_file, fact_file, output_file, tables=(not is_patent), patent = is_patent)
        ## currently just run on the entire file, not on specific sections, but could change this

def fill_full_jargon_from_file_list(filelist,version="6",context=False,tally=False,patent=False,print_files=False,global_tally=False):
    with open(filelist) as instream:
        for line in instream:
            line = line.strip()
            try:
                if ';' in line:
                    txt_file, fact_file = line.split(';')
                elif re.search('.txt$',line):
                    txt_file = line
                    fact_file = False
            except:
                print("Error opening input/output files:")
                print("Input: "+ line)
            run_abbreviate_on_arbiter_file(txt_file,fact_file,txt_file[:-3]+'abbreviate'+version,tables=not(patent),\
                                           reset_dictionary=True,patent=patent,print_file=print_files,global_tally=global_tally)
            update_full_jargon_dictionary(txt_file,fact_file,context=context,tally=tally,patent=patent)


def acquire_jargon_from_file_list(filelist,version='6',context=False,tally=False,patent=False,indvidual_files=False):
    global full_jargon_dictionary
    global abbreviate_dictionary
    global abbreviate_tally
    full_jargon_dictionary = {}
    abbreviate_tally = {}        
    ## get all abbreviate relations from all files and use them to fill full_jargon_dictionary, including frequency info
    fill_full_jargon_from_file_list(filelist,version=version,context=context,global_tally=tally,patent=patent,print_files=indvidual_files)
    outlist = []
    for key in full_jargon_dictionary:
        outlist.append(key)
    ## print(outlist)
    return(outlist)

def acquire_and_print_out_dictionary2(filelist,outfile,version='6',tally=False,context=False,format='tabs',patent=False,indvidual_files=False):
    ## possible output formats include 'tuples' and 'lisp'
    global full_jargon_dictionary
    full_jargon_dictionary.clear()
    jargonlist = acquire_jargon_from_file_list(filelist,version=version,context=context,tally=tally,patent=patent,indvidual_files=indvidual_files)
    jargonlist.sort()
    ## keys in dictionary are regularized sequences of words: all
    ## caps, hyphens replaced by spaces, multiple spaces replaced by
    ## single spaces
    entry_attributes = ['ABBREVIATION','FILE_COUNT','FULL_FORM_COUNT','ABBREV_COUNT','CONTEXT']
    with open(outfile,'w') as outstream:
        for jargon in jargonlist:            
            entry = full_jargon_dictionary[jargon]
            if format == 'tuples':
                outstream.write(jargon)
                for attribute in entry_attributes:
                    outstream.write('|||')
                    if attribute in entry:
                        if (attribute == 'CONTEXT') and ('ABBREVIATION' in entry):
                            abbrev = entry['ABBREVIATION']
                            if type(abbrev)==list:
                                abbrev=abbrev[0]
                            value = choose_best_example_instances(entry[attribute],4,jargon,abbrev)
                        elif (attribute == 'CONTEXT'):
                            value = entry[attribute]
                            if len(value)>4:
                                value = [item[0] for item in value[:4]]                                
                            else:
                                value = [item[0] for item in value]
                        else:
                            value = entry[attribute]
                        outstream.write(tuples_value(value))
                outstream.write(os.linesep)
            elif format == 'lisp':
                outstream.write('(JARGON :ORTH "'+jargon+'"')
                for attribute in entry:
                    if attribute in entry_attributes:
                        if (attribute == 'CONTEXT') and ('ABBREVIATION' in entry):
                            abbrev = entry['ABBREVIATION']
                            if type(abbrev)==list:
                                abbrev=abbrev[0]
                            value = choose_best_example_instances(entry[attribute],4,jargon,abbrev)
                        elif (attribute == 'CONTEXT'):
                            value = entry[attribute]
                            if len(value)>4:
                                value = [item[0] for item in value[:4]] 
                            else:
                                value = [item[0] for item in value]
                        else:
                             value = entry[attribute]
                        value = lisp_value(value)
                        if value:
                            outstream.write(' '+':'+attribute+' '+value)
                outstream.write(')'+os.linesep)
            elif format == 'tabs':
                outstream.write(jargon)
                if 'ABBREVIATION' in entry:
                    abbrev = entry['ABBREVIATION']
                    if type(abbrev) == list:
                        for instance in abbrev:
                            outstream.write('\t'+instance)
                    else:
                        outstream.write('\t'+instance)
                outstream.write(os.linesep)

def get_last_word(instring):
    out = re.search('\w+$',instring)
    if out:
        return(out.group(0))
    else:
        return(False)

def update_base_abbrev_dict_entry(indict,abbreviation,items):
    if abbreviation in indict:
        for item in items:
            if not item in indict[abbreviation]:
                indict[abbreviation].append(item)
    else:
        indict[abbreviation] = items

def plural_edit(inlist):
    if len(inlist) == 1:
        return(inlist)
    else:
        ends_in_s = []
        output = []
        ## adjust for "..ses" cases
        for item in inlist[:]:
            if item[-1] in ['s','S']:
                if (item+'ES' in inlist) or (item+'es' in inlist):
                    output.append(item)
                else:
                    ends_in_s.append(item)
            else:
                output.append(item)
        ## print('s',ends_in_s)
        ## print('not',output)
        if (len(ends_in_s) > 0) and (len(output)>0):
            for item1 in ends_in_s[:]:
                for item2 in output:
                    diff = len(item1) - len(item2)
                    if not item1 in ends_in_s:
                        pass
                    elif (diff == 1) and (item1[:-1] == item2):
                        ends_in_s.remove(item1)
                    elif (diff == 2) and (item1[-2] in ['e','E']) and \
                         (item1[:-2] == item2):
                        ends_in_s.remove(item1)
            output.extend(ends_in_s)
            return(output)
        else:
            return(inlist)

def plural_edit_enum(inlist):
    ## ** 57 ***
    if len(inlist) == 1:
        return(inlist)
    else:
        ends_in_s = []
        output = []
        items = []
        freqs = []
        ## adjust for "..ses" cases
        for freq,item in inlist:
            freqs.append(freq)
            items.append(item)
        ## print(items)
        for index in range(len(inlist)):
            item = items[index]
            freq = freqs[index]
            if item[-1] in ['s','S']:
                if (item+'ES' in items) or (item+'es' in items):
                    ## print(1,item)
                    output.append([freq,item])
                else:
                    ## print(2,item)
                    ends_in_s.append([freq,item])
            else:
                output.append([freq,item])
                ## print(3,item)
        ## print('s',ends_in_s)
        ## print('not',output)
        ## print(1,ends_in_s)
        ## print(2,output)
        if (len(ends_in_s) > 0) and (len(output)>0):
            for freq1,item1 in ends_in_s[:]:
                index = 0
                for freq2,item2 in output:
                    diff = len(item1) - len(item2)
                    if not [freq1,item1] in ends_in_s:
                        pass
                    elif (diff == 1) and (item1[:-1] == item2):
                        output[index][0]=output[index][0]+freq1
                        ends_in_s.remove([freq1,item1])
                    elif (diff == 2) and (item1[-2] in ['e','E']) and \
                         (item1[:-2] == item2):
                        output[index][0]=output[index][0]+freq1
                        ends_in_s.remove([freq1,item1])
                    index = index + 1
            output.extend(ends_in_s)
            return(output)
        else:
            return(inlist)
            
def make_base_abbrev_dict(infile,outfile):
    ## create a dictionary such that each abbreviation is mapped to
    ## "base forms", where a "base form" is the expanded form in the
    ## singular, e.g., hmms is expanded to "hidden markov model", not
    ## "hidden markov models"
    global dict1
    dict1 = {}
    with open(infile) as instream:
        for line in instream:
            line = line.strip()
            items = line.split('\t')
            full_form = items[0]
            last_word = get_last_word(full_form)
            if full_form[-1] == 'S':
                alternate1 = full_form[:-1]
                if alternate1[-1] == 'E':
                    alternate2 = alternate1[:-1]
                else:
                    alternate2 = False
            else:
                alternate1 = False
                alternate2 = False
            for abbreviation in items[1:]:
                abbrev_alt = False
                if (len(abbreviation)>1) and (abbreviation[-1] in ['s','S']):
                    abbrev_alt = abbreviation[:-1]
                    if abbrev_alt in dict1:
                        if alternate1 and (alternate1 in dict1[abbrev_alt]):
                            update_base_abbrev_dict_entry(dict1,abbreviation,dict1[abbrev_alt])
                            ## dict1[abbreviation] = dict1[abbrev_alt]
                        elif alternate2 and (alternate2 in dict1[abbrev_alt]):
                            update_base_abbrev_dict_entry(dict1,abbreviation,dict1[abbrev_alt])
                    ## does abbrev_alt already have an entry
                    ## and is alternate1 or 2 in it?
                    elif (abbrev_alt in items[1:]) and not alternate1:
                        update_base_abbrev_dict_entry(dict1,abbreviation,[full_form])
                    ## Given the normal case of ending in s, regularize to the full form
                    elif alternate1 and last_word and ((not last_word[0] in ['s','S']) or (abbrev_alt[-1] in  ['s','S'])):
                        if alternate2 and not (abbrev_alt[-1] in ['e','E']):
                            update_base_abbrev_dict_entry(dict1,abbreviation,[alternate2])
                        else:
                            update_base_abbrev_dict_entry(dict1,abbreviation,[alternate1])
                    ## An abbreviation ending in S is only really a plural case if the last word in the full form does not
                    ## begin with 's', that is, unless the abbrevation actually ends in 2 "s"s.  A similar consideration holds
                    ## for figuring out whether to cut off "e" or "es" when shortening the full form.
                    else:
                        update_base_abbrev_dict_entry(dict1,abbreviation,[full_form])
                else:
                    update_base_abbrev_dict_entry(dict1,abbreviation,[full_form])
    with open(outfile,'w') as outstream:
        term_list = list(dict1.keys())
        term_list.sort()
        ## input()
        for term in term_list:
            outstream.write(term)
            for term2 in plural_edit(dict1[term]):
                outstream.write('\t'+term2)
            outstream.write(os.linesep)

def anteced_edit(anteced_list):
    anteced_list = plural_edit(anteced_list)
    output = []
    anteced_with_parens = []
    for item in anteced_list:
        if not '(' in item:
            output.append(item)
    if len(output)>0:
        return(output)
    else:
        return(anteced_list)
    
    
def acquire_and_print_out_dictionary3(filelist,outfile,inverse_outfile,version='6',tally=False,context=False,format='tabs',patent=False,indvidual_files=False,order_dictionary = False):
    ## possible output formats include 'tuples' and 'lisp'
    global full_jargon_dictionary
    global full_abbrev_dict
    full_abbrev_dict = {}
    full_jargon_dictionary.clear()
    jargonlist = acquire_jargon_from_file_list(filelist,version=version,context=context,tally=tally,patent=patent,indvidual_files=indvidual_files)
    jargonlist.sort()
    ## print(jargonlist)
    ## keys in dictionary are regularized sequences of words: all
    ## caps, hyphens replaced by spaces, multiple spaces replaced by
    ## single spaces
    entry_attributes = ['ABBREVIATION','FILE_COUNT','FULL_FORM_COUNT','ABBREV_COUNT','CONTEXT']
    for jargon in jargonlist[:]:
        if type(jargon) == str:
            entry = full_jargon_dictionary[jargon]
            new_abbrev = []
            abbrev_out = False
        else:
            entry = []
            new_abbrev = []
            abbrev_out = False
        if 'ABBREVIATION' in entry:
            for abbrev in entry['ABBREVIATION']:
                if (type(abbrev) == str):
                    abbrev_key = abbrev+'|'+jargon
                    if abbrev_key in abbreviate_tally:
                        count = abbreviate_tally[abbrev_key]
                    else:
                        count = 0
                    if count > 1:
                        new_abbrev.append([count,abbrev])
        if len(new_abbrev)>0:
            new_abbrev.sort()
            new_abbrev.reverse()
            abbrev_out = []
            for item in new_abbrev:
                abbrev_out.append(item[1])
        if abbrev_out:
            entry['ABBREVIATION'] = abbrev_out
            if (len(jargon)>2) and (jargon[-1] == 'S'):
                alternate1 = jargon[:-1]
                if alternate1[-1] == 'E':
                    alternate2 = alternate1[:-1]
                else:
                    alternate2 = False
            else:
                alternate1 = False
            last_word = get_last_word(jargon)
            for abbreviation in abbrev_out:
                if (len(abbreviation)>1) and (abbreviation[-1] in ['s','S']):
                    abbrev_alt = abbreviation[:-1]
                    if abbrev_alt in full_abbrev_dict:
                        if alternate1 and (alternate1 in full_abbrev_dict[abbrev_alt]):
                            update_base_abbrev_dict_entry(full_abbrev_dict,abbreviation,full_abbrev_dict[abbrev_alt])
                            ## full_abbrev_dict[abbreviation] = full_abbrev_dict[abbrev_alt]
                        elif alternate2 and (alternate2 in full_abbrev_dict[abbrev_alt]):
                            update_base_abbrev_dict_entry(full_abbrev_dict,abbreviation,full_abbrev_dict[abbrev_alt])
                    ## does abbrev_alt already have an entry
                    ## and is alternate1 or 2 in it?
                    elif (abbrev_alt in abbrev_out) and not alternate1:
                        update_base_abbrev_dict_entry(full_abbrev_dict,abbreviation,[jargon])
                    ## Given the normal case of ending in s, regularize to the full form
                    elif alternate1 and last_word and ((not last_word[0] in ['s','S']) or (abbrev_alt[-1] in  ['s','S'])):
                        if alternate2 and not (abbrev_alt[-1] in ['e','E']):
                            update_base_abbrev_dict_entry(full_abbrev_dict,abbreviation,[alternate2])
                        else:
                            update_base_abbrev_dict_entry(full_abbrev_dict,abbreviation,[alternate1])
                    ## An abbreviation ending in S is only really a plural case if the last word in the full form does not
                    ## begin with 's', that is, unless the abbrevation actually ends in 2 "s"s.  A similar consideration holds
                    ## for figuring out whether to cut off "e" or "es" when shortening the full form.
                    else:
                        update_base_abbrev_dict_entry(full_abbrev_dict,abbreviation,[jargon])
                else:
                    update_base_abbrev_dict_entry(full_abbrev_dict,abbreviation,[jargon])
        else:
            full_jargon_dictionary.pop(jargon)
    for abbreviation in full_abbrev_dict:
        entry = full_abbrev_dict[abbreviation]
        full_form_list = []
        for full_form in entry:
            abbrev_key = abbreviation+'|'+full_form
            if abbrev_key in abbreviate_tally:
                count = abbreviate_tally[abbrev_key]
                full_form_list.append([count,full_form])
        ## combine plural and signular instances and counts here ** 57 ***
        plural_edit_enum(full_form_list)
        full_form_list.sort()
        full_form_list.reverse()
        full_form_out = []
        for full_form in full_form_list:
            full_form_out.append(full_form[1])
        full_abbrev_dict[abbreviation] = full_form_out
    with open(outfile,'w') as outstream:
        for jargon in jargonlist: 
            if jargon in full_jargon_dictionary:           
                entry = full_jargon_dictionary[jargon]
                if format == 'tuples':
                    outstream.write(jargon)
                    for attribute in entry_attributes:
                        outstream.write('|||')
                        if attribute in entry:
                            if (attribute == 'CONTEXT') and ('ABBREVIATION' in entry):
                                abbrev = entry['ABBREVIATION']
                                if type(abbrev)==list:
                                    abbrev=abbrev[0]
                                value = choose_best_example_instances(entry[attribute],4,jargon,abbrev)
                            elif (attribute == 'CONTEXT'):
                                value = entry[attribute]
                                if len(value)>4:
                                    value = [item[0] for item in value[:4]]                                
                                else:
                                    value = [item[0] for item in value]
                            else:
                                value = entry[attribute]
                            outstream.write(tuples_value(value))
                    outstream.write(os.linesep)
                elif format == 'lisp':
                    outstream.write('(JARGON :ORTH "'+jargon+'"')
                    for attribute in entry:
                        if attribute in entry_attributes:
                            if (attribute == 'CONTEXT') and ('ABBREVIATION' in entry):
                                abbrev = entry['ABBREVIATION']
                                if type(abbrev)==list:
                                    abbrev=abbrev[0]
                                value = choose_best_example_instances(entry[attribute],4,jargon,abbrev)
                            elif (attribute == 'CONTEXT'):
                                value = entry[attribute]
                                if len(value)>4:
                                    value = [item[0] for item in value[:4]] 
                                else:
                                    value = [item[0] for item in value]
                            else:
                                 value = entry[attribute]
                            value = lisp_value(value)
                            if value:
                                outstream.write(' '+':'+attribute+' '+value)
                    outstream.write(')'+os.linesep)
                elif format == 'tabs':
                    outstream.write(jargon)
                    if 'ABBREVIATION' in entry:
                        abbrev = entry['ABBREVIATION']
                        if type(abbrev) == list:
                            for instance in abbrev:
                                outstream.write('\t'+instance)
                        else:
                            outstream.write('\t'+instance)
                    outstream.write(os.linesep)
    with open(inverse_outfile,'w') as outstream:
        term_list = list(full_abbrev_dict.keys())
        term_list.sort()
        ## input()
        for term in term_list:
            out_list = anteced_edit(full_abbrev_dict[term])
            if out_list and len(out_list)>0:
                outstream.write(term)
                for term2 in out_list:
                    outstream.write('\t'+term2)
                outstream.write(os.linesep)
