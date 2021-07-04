from abbreviate import *
from filter_legal import *
from websearch import *

et_al_citation = re.compile(' et[.]? al[.]? *$')
ok_path_types = ['url'] ##  currently 'ratio' is not an ok_path_type
compound_inbetween_string = re.compile('^ +(of|for) +((the|a|an|[A-Z]\.) +)?$',re.I)
term_stop_words_with_periods = re.compile('(^|\s)(u\.s|e\.g|i\.e|u\.k|c\.f|see|ser)([\.\s]|$)',re.I)

lemma_dict = {}
cluster_hash = {}
term_latin_pp_hash = {}

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

def nationality_check(term_lower):
    if (term_lower in pos_dict) and ('NATIONALITY' in pos_dict[term_lower]):
        return(True)

def section_heading_word(word):
    if (len(word)>1) and (word[-1]=='s'):
        if (word in ['descriptions','claims','embodiments', 'examples','fields','inventions','priorities','applications']):
            return(True)
    elif word in ['description', 'summary', 'claim', 'embodiment', 'example', 'explanation', 'field', 'invention', 'introduction', 'priority', 'application(s)', 'statement', 'reference']:
        return(True)

def ugly_word(word):
    ## words that are probably typos or other stuff we don't want
    if (len(word)>3) and (word[0] in "0123456789") and word[-1].isalpha():
        return(True)
    elif (len(word)>1) and (word[0] in "`~!@#$%^&*-_+=<>,.?/\\"):
        return(True)
    elif (('=' in word) or ('>' in word)):
        return(True)
    elif re.search('\.su[bp]$',word):
        return(True)
    elif not re.search('[a-zA-Z]',word):
        return(True)
    elif re.search('[A-Za-z]+[0-9]+[A-Za-z]+',word):
        return(True)
    elif re.search('^[0-9]{1,3}[a-zA-Z]$',word):
        return(True)


def topic_term_ok(word_list,pos_list,term_string):
    signif_term = 0
    OOV_count = 0
    nominalization_count = 0
    nom_length = 0
    non_final_common_noun = 0
    has_section_heading_word = False
    alpha = False
    has_lower = False
    has_upper = False
    has_ugly = False
    if (pos_list[-1] == 'INSIDE_LATIN_PP'):
        return(False,False)
    if term_string == False:
        return(False,False)
    if len(term_string) == 1:
        return(False,False)
    elif (len(term_string) == 2) and (("." in term_string) or (term_string[1] in '0123456789')):
        ## a single initial is not a term
        return(False,False)
    elif term_dict_check(term_string.lower(), stat_term_dict):
        ## return(True,False)
        signif_term = 1
    elif term_stop_words_with_periods.search(term_string):
        return(False,False)
    if (signif_term == 0) and [pos_list[-1] == 'PLURAL'] and (pos_list[-1][-1]=='s'):
        bases = derive_base_form_from_plural(word_list[-1].lower())
        if bases:
            for base in bases:
                if nationality_check(base):
                    return(False,False)
    if signif_term > 0:
        pass
    elif pos_list[-1]=='PERLOC_NAME':
        return(False,False)
    elif (len(word_list)==1) and (len(word_list[0])==1):
        return(False,False)
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
        jargon_word_count = 0
        if word_list[num].isupper():
            allcaps = True
        else:
            allcaps = False
        if term_dict_check(lower,stat_term_dict):
            signif_term = signif_term + 1
        if (not alpha) and re.search('[a-zA-Z]',lower):
            alpha = True
        if lower in pos_dict:
            if ('NOUN' in pos_dict[lower])and (len(lower)<8):
                common = True
            if 'NOUN_OOV' == pos_list[num]:
                oov = True
                OOV_count = 1 + OOV_count
            elif lower in jargon_words:
                jargon_word_count = jargon_word_count + 1
            if lower in noun_base_form_dict:
                base = noun_base_form_dict[lower][0]
            else:
                base = lower
        elif ugly_word(lower):
            ugly = True
            has_ugly = True
        elif pos_list[num] in ['NOUN','NOUN_OOV','PLURAL']:
            base = lower
            oov = True
            OOV_count = 1 + OOV_count ## some OOV words are not classified as noun
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
        if (nom_rank>0) or  (pos_list[num]=='TECH_ADJECTIVE'):
            nominalization_count = 1 + nominalization_count
        elif (not oov) and (jargon_word_count == 0) and common and (num==0) or (lower in ['invention','inventions']):
            non_final_common_noun = non_final_common_noun+1
        if nom_rank >= 2:
            ## only record length if real nominalization (not other nom class)
            if lower.endswith('ing'):
                length = len(lower)-3
            else:
                length = len(lower)
            if length > nom_length:
                nom_length = length
    if has_ugly:
        return(False,False)
    if signif_term>0:
        return(True,OOV_count>1)
    if not alpha:
        return(False,False)
    if has_upper and (not has_lower) and has_section_heading_word:
        return(False,False)
    if (OOV_count >= 1) or ((nominalization_count >=3) and (len(word_list)>=4)) or (jargon_word_count > 0):
        return(True,True)
    if non_final_common_noun>0:
        return(False,False)
    elif (nom_length>11):
        return(True,OOV_count>1)
    elif (len(word_list)>1) and ((nominalization_count >= 1) or (jargon_word_count >=1)):
        return(True,OOV_count>1)
    else:
        return(False,False)

def topic_term_ok_boolean(word_list,pos_list,term_string):
    value1,value2 = topic_term_ok(word_list,pos_list,term_string)
    return(value1)

def get_next_word(instring,start):
    ## 1) don't split before paren or , unless
    ## one of the adjacent characters is an alphachar
    ## or space
    ##
    ## 2) Don't break continuous string of non-space chars
    ##    if they contain one non-letter char
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
    extend = False
    border = False
    while found:
        border = found.end()
        if (border<(len(instring)-2)) and (instring[border]=="-") and (instring[border+1]=="("):
            border = border + 1
            ## designed to handle the '-(' case
        if (border >= len(instring)):
            end = found.end()
            found = False
        elif instring[border]=="'":
            next_word = word_pattern.search(instring,found.end())
            if next_word and (border+1==next_word.start()) and (next_word.group(0) in ['s','t']):
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
            ## Don't split at hyphen unless both adjacent chars are alpha chars maybe done
            next_word = word_pattern.search(instring,found.end())
            if next_word and(border+1==next_word.start()) and (((found.group(0).isalpha() and \
                                ((len(found.group(0))==1) or found.group(0).isalpha()))) or \
               ((len(next_word.group(0))>3)and ((next_word.group(0)[-2:]=="ed") or (next_word.group(0)[-3:]=='ing')))):
                end = next_word.end()
                found = next_word
            elif next_word and (not(next_word.group(0).isalpha) or not(instring[start:end].isalpha())):
                end = next_word.end()
                found = next_word
            else:
                end=found.end()
                found = False
        elif ((instring[border]==',') and \
          ((not ((border > 0) and instring[border-1].isalpha)) or (not re.search('\s',instring[border+1])))) \
            or ((instring[border]==')') and \
                (border<(len(instring)-1)) and (re.search('[a-zA-Z0-9]',instring[border+1]))):
            ## don't split unless preceding character is alphachar and following char is whitespace
            next_word = word_pattern.search(instring,found.end())
            if next_word:
                end = next_word.end()
                found = next_word
        elif (instring[border]=='(') and (border>0) and (not re.search('\s',instring[border-1])):
            paren_pat =  parentheses_pattern_match(instring,border,2)
            ### parentheses_pattern2.search(instring,border)
            if paren_pat and (not re.search('\s',paren_pat.group(1))):
                ## require matching paren pattern
                ## field 1 is pre-left paren (null), field 2 is between parens, field 3 is right paren
                end = paren_pat.end()
                found = paren_pat
            else:
                end = found.end()
                found = False
        elif (start == found.start()) and (found.end() == start+1) and (instring[start]=='('):
            paren_pat = parentheses_pattern_match(instring,start,2)
            ### parentheses_pattern2.search(instring,start)
            if paren_pat and (not re.search('\s',paren_pat.group(1))) and (len(instring)> paren_pat.end()+1) \
              and (not re.search('\s',instring[paren_pat.end()+1])):
              found = paren_pat
            else:
                end = found.end()
                found = False            
        else:
            end = found.end()
            found = False
    if end:
        return(instring[start:end],start,end)
    else:
        return(False,False,False)

def bad_splitter_pattern(pattern,piece):
    if (pattern.group(0)=='.') and (pattern.start()>0):
        previous_word = re.search(' ([a-zA-Z]+)[.]$',piece[:pattern.start()+1])
        if previous_word and (len(previous_word.group(1))==1):
            return(True)
        else:
            return(False)
    else:
        return(False)
    
def next_splitter_pattern(piece,start):
    splitters=re.compile('\.|,|;|:| and | or | as well as | along with | in addition to |'+os.linesep,re.I)
    pattern = splitters.search(piece,start)
    while(pattern and bad_splitter_pattern(pattern,piece)):
        start = pattern.end()
        pattern = splitters.search(piece,start)
    return(pattern)

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

def OK_chemical(chem_string):
    if len(chem_string)<=2:
        return(False)
    elif chem_string in abbr_to_full_dict:
        return(False)
    else:
        cap_count = 0
        elements = []
        current_element = ''
        has_two_char_element = False
        for character in chem_string:
            if character.isupper():
                if current_element == '':
                    current_element = character
                elif current_element in elements:
                    ## elements can only occur once
                    return(False)
                else:
                    elements.append(current_element)
                    current_element = character
            elif character.islower():
                if len(current_element)==1:
                    current_element=current_element+character
                    if current_element in elements:
                        ## elements can only occur once
                        return(False)
                    elements.append(current_element)
                    has_two_char_element = True
                    current_element = ''
                else:
                    ## a lowercase letter must immediately follow an uppercase
                    return(False)
            elif len(current_element)>0:
                if current_element in elements:
                    ## elements can only occur once
                    return(False)
                elements.append(current_element)
                current_element = ''
        if current_element:
            if current_element in elements:
                ## elements can only occur once
                return(False)
            elements.append(current_element)
    if (len(elements)>2) or ((len(elements)==2) and \
                             (has_two_char_element or re.search('[0-9]',chem_string))):
        return(True)
    else:
        return(False)
                    
                
def get_next_possible_match(search_object,text,start):
    space = re.compile(' ')
    match = space.search(text,start)
    if match:
        end = match.start()
    else:
        end = len(text)
    possible_match = search_object.search(text[:end],start)
    while (not possible_match) and (end < len(text)):
        start = end
        if ' ' in text[start+1:]:
            end = (text[start+1:].index(' '))+start+1
        else:
            end = len(text)
        if len(text[start:end])>100:
            possible_match = False
        else:
            possible_match = search_object.search(text[:end],start)
    if possible_match:
        return(start,possible_match)
    else:
        return(len(text),False)
    
def get_next_chemical_match(text,start):
    chemical_formula_piece1 = '(-?((A[glmrstu])|(B[aehikr]?)|(C[adeflmorsu]?)|(D[by])|(E[rsu])|(F[emr]?)|(G[ade])|(H[efgos]?)|(I[nr]?)|(Kr?)|(L[airu])|(M[dgnot])|(N[abdeiop]?)|(Os?)|(P[abdmortu]?)|(R[abefhnu])|(S[bcegimnr]?)|(T[abcehilm])|(U)|(V)|(W)|(Xe)|(Yb?)|(Z[nr]))[0-9]?-?)'
    chemical_formula_piece2 = '(-?\(((A[glmrstu])|(B[aehikr]?)|(C[adeflmorsu]?)|(D[by])|(E[rsu])|(F[emr]?)|(G[ade])|(H[efgos]?)|(I[nr]?)|(Kr?)|(L[airu])|(M[dgnot])|(N[abdeiop]?)|(Os?)|(P[abdmortu]?)|(R[abefhnu])|(S[bcegimnr]?)|(T[abcehilm])|(U)|(V)|(W)|(Xe)|(Yb?)|(Z[nr]))[0-9]?(\)[0-9]?)-?)'
    chemical_piece = '('+chemical_formula_piece2+')|('+chemical_formula_piece1+')'
    chemical_formula = re.compile('(^| )(('+chemical_piece+'){2,})($| )')
    ## group 2 is chemical
    local_start = start
    local_start,possible_match = get_next_possible_match(chemical_formula,text,local_start)
    while possible_match:
        if OK_chemical(possible_match.group(2)):
            return(possible_match)
        else:
            local_start = possible_match.end(2)
            possible_match = chemical_formula.search(text,local_start)


def OK_url(path_string):
    pivot_match = re.search('(^[^/]*)([:.])([^/]*)',path_string)
    if pivot_match:
        if pivot_match.group(2) == ':':
            return(True)
        elif (len(pivot_match.group(1))>1) and (len(pivot_match.group(3))>1):
            return(True)
        
def OK_path(path_string,url=False):
    if (path_string.count('/')>1) \
       and re.search('[a-zA-Z]',path_string) \
       and re.search('^[ -~]*$',path_string) \
       and (not re.search('^((WO)|(W/O)|(PCT))',path_string)) \
       and ((not url) or OK_url(path_string)): 
        return(True)
        
def get_next_path_match(text,start):
    path_chunk_string =   '(([^ /;,=<>()\[\]]+)(//?([^ /;,=<>()\[\]]+)))'
    path_chunk_formula_string = '('+path_chunk_string+ ' ?)+'+path_chunk_string
    ## there must be at least two chunks for there to be a path
    ## all but the last chunk can end in a space
    path_chunk_formula = re.compile(path_chunk_formula_string)    
    ## add chunk to formula if separated by space
    ## this may need to be filtered because it may pick up words otherwise
    ## well-formedness constraints include: requirement of having at
    ## least one number, 1 lowercase/uppercase sequence, or minimum
    ## length without such things
    path_chunk_no_url = '(([^ /;,=<>()\[\]]+)(/([^ /;,=<>()\[\]]+)))'
    path_chunk_formula_no_url_string = '('+path_chunk_no_url+ ')+'+path_chunk_no_url
    path_chunk_formula2 = re.compile(path_chunk_formula_no_url_string)
    current_start = start
    path_match = path_chunk_formula.search(text,current_start)
    path_match2 = path_chunk_formula2.search(text,current_start)
    while path_match or path_match2:
        if path_match and path_match2:
            if (path_match.start() < path_match2.start()) or \
               ((path_match.start() == path_match2.start()) and \
                (path_match.end() <= path_match2.end())):
                if (re.search('^[^/]*:[^/]*/',path_match.group(0)) or re.search('^[^/]*[a-zA-Z]\.[a-zA-Z][^/]*/',path_match.group(0)))\
                  and OK_path(path_match.group(0),url=True):
                    return(path_match,'url')
                elif (path_match.end() == path_match2.end()):
                    if OK_path(path_match2.group(0)):
                        return(path_match2,'ratio')
                    else:
                        current_start = path_match.end()
                        path_match = path_chunk_formula.search(text,current_start)
                        path_match2 = path_chunk_formula2.search(text,current_start)
                else:
                    current_start = path_match.end()
                    path_match = path_chunk_formula.search(text,current_start)  
            elif OK_path(path_match2.group(0)):
                return(path_match2,'ratio')
            else:
                current_start = path_match2.end()
                path_match2 = path_chunk_formula2.search(text,current_start)
        elif path_match:
            if (re.search('^[^/]*:[^/]*/',path_match.group(0)) or re.search('^[^/]*[a-zA-Z]\.[a-zA-Z][^/]*/',path_match.group(0))) \
               and OK_path(path_match.group(0),url=True):
                return(path_match,'url')
            else:
                current_start = path_match.end()
                path_match = path_chunk_formula.search(text,current_start)
        elif path_match2:
            if OK_path(path_match2.group(0)):
                return(path_match2,'ratio')
            else:
                current_start = path_match2.end()
                path_match2 = path_chunk_formula2.search(text,current_start)
        else:
            ## current_start = path_match.end()
            ## path_match = path_chunk_formula.search(text,current_start)
            print('this should be impossible -- there must be a bug')
            ## input()
            return(False,False)
    return(False,False)

def get_formulaic_term_pieces(text,offset):
    start = 0
    gene_sequence = re.compile('(^|[^A-Za-z0-9\'-])((-?[0-9]\'?)?(([CATG]{4,})|([CcAaTtGg]{5,}))(-?[0-9]\'?)?)(\$|[^A-Za-z0-9\'-])')
    ## keep group 2
    path_match,path_type = get_next_path_match(text,start)
    chemical_match = get_next_chemical_match(text,0) 
    gene_match = gene_sequence.search(text)
    next_match = False
    start = 0
    output = []
    while (path_match or chemical_match or gene_match):
        minimum_new_start = False
        next_match = False
        match_type = False
        for match,local_type in [[path_match,'path'], [chemical_match,'chemical'], [gene_match,'gene']]:
            if match and ((not next_match) or (match.start() < minimum_new_start)):
                minimum_new_start = match.start()
                next_match = match
                match_type = local_type
        if next_match:
            ## triples should be in same/similar format as get_topic_terms3 triples: [start_offset,end_offset,string]
            ##         but they should include a fourth item: type
            ## later -- we can remove conflicts between the two
            if (match_type in ['gene','chemical']):
            #     ## group 2
                start_offset = next_match.start(2)+offset
                end_offset = next_match.end(2)+offset
                term_string = next_match.group(2)
                start = next_match.end(2)
                output.append([start_offset,end_offset,term_string,False,False,match_type])
                ## print(term_string)
            else:
                start_offset = next_match.start()+offset
                end_offset = next_match.end()+offset
                term_string = next_match.group(0)
                if match_type == 'path':
                    ## preparing for futher elaboration of code
                    if path_type in ok_path_types:
                        output.append([start_offset,end_offset,term_string,False,False,path_type])
                else:
                    output.append([start_offset,end_offset,term_string,False,False,match_type])
                start = next_match.end()
            if next_match == path_match:
                path_match,path_type = get_next_path_match(text,start)
            elif next_match == chemical_match:
                ## print('chem match',start)
                chemical_match = get_next_chemical_match(text,start)
            elif next_match == gene_match:
                gene_match = gene_sequence.search(text,start)
    output.sort()
    return(output)


def merge_formulaic_and_regular_term_tuples(term_tuples,formulaic_tuples):
    ## initially, remove term_tuples that intersect at all with formulaic_tuples
    ## this might be the wrong strategy -- we need to evaluate
    ## also, add a fourth element to term_tuples, 'chunk-based' indicting these are obtained with a chunking procedure
    ## (even though some of them will be obtained some other way)
    ## also currently, this is being done before compound tuples or lemmas are being created
    ## not sure exactly of the ramifications

    ## ALSO: add term type to all next_term instances
    output = []
    ## both term_tuples and formulaic_tuples are sorted (the first 2 fields are start and end offsets)
    term_pointer = 0
    formula_pointer = 0
    if len(term_tuples)>0:
        next_term = term_tuples[term_pointer]
        next_term.append('chunk-based')
    else:
        next_term = False
    if len(formulaic_tuples)> 0:
        next_formula = formulaic_tuples[formula_pointer]
    else:
        next_formula = False
    while next_term or next_formula:
        if not next_term:
            output.extend(formulaic_tuples[formula_pointer:])
            next_formula = False
        elif not next_formula:
            for term in term_tuples[term_pointer:]:
                if len(term)<6:
                    term.append('chunk-based')
                output.append(term)
            next_term = False
        elif next_term[0] < next_formula[0]:
            ## 2 conditions: 
            ## A) next term completely preceded 
            ## then formula (keep current next term and increment)
            ## B) they overlap, but next_term begins first
            ##   -- just increment next term and ignore current next term
            if next_term[1] < next_formula[0]:
                output.append(next_term)
            term_pointer = term_pointer+1
            if len(term_tuples)>term_pointer:
                next_term = term_tuples[term_pointer]
                next_term.append('chunk-based')
            else:
                next_term = False
        elif next_formula[1] < next_term[0]:
            ## if next_formula completely precedes next_term, keep formula and increment
            output.append(next_formula)
            formula_pointer = formula_pointer+1
            if len(formulaic_tuples)>formula_pointer:
                next_formula = formulaic_tuples[formula_pointer]
            else:
                next_formula = False
        else:
            ## in all other conditions there is some overlap, but getting rid of
            ## the next term would solve the overlap
            term_pointer = term_pointer+1
            if len(term_tuples)>term_pointer:
                next_term = term_tuples[term_pointer]
                next_term.append('chunk-based')
            else:
                next_term = False
    return(output)
    
def global_formula_filter(term_list,term_hash,type_hash):
    chemical_filter_pattern = re.compile('^([A-Z]*)([0-9])$')
    chemical_matches = {}
    for term in term_list:
        if (term in type_hash) and (type_hash[term][0] == 'chemical'):
            match = chemical_filter_pattern.search(term)
            if match:
                key = match.group(1)
                value = match.group(0)
                if key in chemical_matches:
                    if value in chemical_matches[key]:
                        pass
                    else:
                        chemical_matches[key].append(value)
                else:
                    chemical_matches[key] = [value]
    for key in chemical_matches:
        if len(chemical_matches[key])>1:
            for value in chemical_matches[key]:
                term_list.remove(value)
                term_hash.pop(value)

def get_topic_terms(text,offset,filter_off=False):
    txt_markup = re.compile('(\[in-line-formulae\].*?\[/in-line-formulae\])|(</[a-z]+>)|(<(/)?[a-z]+( [a-z]+=[^>]+)* ?>)',re.I)
    single_quote_pattern=re.compile('(\s|^)[\`\'‘](?!(s[^a-z]|d[^a-z]| |t[^a-z]|ll[^a-z]|m[^a-z]|ve[^a-z]|re[^a-z]))([^\`\']*?)[\'’](?!(s[^a-z]|d[^a-z]|t[^a-z]|ll[^a-z]|m[^a-z]|ve[^a-z]|re[^a-z]))')
    ## '...', where ' is not followed by a contraction or possessive marker (the first one cannot be followed by a space either,
    ## since this would make it a second quote or a plural possessive marker -- note this procludes an apostrophe inside a single quote
    double_quote_pattern=re.compile('(\s|^)["“]([^"“”]*?)["”](\s|$)')
    first_character_pattern=re.compile('[^ ,\.?><\'";:\]\[{}\-_=)(*&\^%$\#@!~]')
    start = 0
    paren_pat = parentheses_pattern_match(text,start,3)
    ### parentheses_pattern3.search(text,start)
    txt_markup_match = txt_markup.search(text,start)
    pieces = []
    topic_terms = []
    extend_antecedent = False
    last_start = False
    pre_np = False
    ## Part 1: based on get_next_abbreviation_relations
    ## it servers two purposes: (a) it breaks up the text by the round and square parentheses (reliable units); (b) it identifies
    ## abbreviations and their antecedents as terms
    while (paren_pat or txt_markup_match):
        if txt_markup_match and (txt_markup_match.start()>=start) and ((not paren_pat) or (paren_pat.start()>txt_markup_match.start())):
            pieces.append([start,text[start:txt_markup_match.start()]])
            start = txt_markup_match.end()
            txt_markup_match = txt_markup.search(text,start)
        elif paren_pat and (paren_pat.start()<start):
            ## in case parens are inside of txt_markup
            ### paren_pat = parentheses_pattern3.search(text,start)
            paren_pat = parentheses_pattern_match(text,start,3)
        elif txt_markup_match and (not paren_pat):
            txt_markup_match = txt_markup.search(text,start)
        else:
            result = False
            Fail = False
            first_word_break=re.search('[ ,;:]',paren_pat.group(2))
            if first_word_break:
                    abbreviation=paren_pat.group(2)[:first_word_break.start()]
            else:
                abbreviation=paren_pat.group(2)
            search_end = paren_pat.start()
            search_end,Fail = find_search_end(text,search_end)
            if ill_formed_abbreviation_pattern(paren_pat) or re.search('^[a-zA-Z]$',abbreviation):
                Fail = True
            else:
                previous_words = remove_empties(word_split_pattern.split(text[start:search_end].rstrip(' ')))
            if Fail or (not abbreviation) or ((not abbreviation.isupper()) and (abbreviation in pos_dict)):
                result = False
            else:
                ## lowercase nouns in pos_dict are probably not really abbreviations
                result = abbreviation_match(abbreviation,previous_words,text,search_end,offset,False,False)
                ## result is a list
            if result and (result[3] == 'JARGON'):
                ## ARG1 is the full form
                ## ARG2 is the abbreviation
                ARG1_start = result[0]
                ARG1_end = result[1]
                if result[4]:
                    ARG2_start = paren_pat.start(2)+offset
                    ARG2_end = ARG2_start+len(abbreviation)-1
                    if filter_off or (topic_term_ok_boolean([result[2]],['NOUN_OOV'],result[2]) and topic_term_ok_boolean([abbreviation[1:]],'NOUN_OOV',abbreviation[1:])):
                        topic_terms.extend([[ARG1_start,ARG1_end,result[2],False,'ABBREVIATION'],[ARG2_start,ARG2_end,abbreviation[1:],False,'ABBREVIATION']])
                else:
                    ARG2_start = paren_pat.start(2)+offset
                    ARG2_end = ARG2_start+len(abbreviation)
                    if filter_off or (topic_term_ok_boolean([result[2]],['NOUN_OOV'],result[2]) and topic_term_ok_boolean([abbreviation],'NOUN_OOV',abbreviation)):
                        topic_terms.extend([[ARG1_start,ARG1_end,result[2],False,'ABBREVIATION'],[ARG2_start,ARG2_end,abbreviation,False,'ABBREVIATION']])
                pieces.append([start,text[start:paren_pat.start()]])
                if txt_markup_match and (txt_markup_match.start()>start) and (txt_markup_match.end()<paren_pat.end()):
                    start = txt_markup_match.start()
                else:
                    start = paren_pat.end()
            elif txt_markup_match and (txt_markup_match.start()>start) and (txt_markup_match.end()<paren_pat.end()):
                start = txt_markup_match.start()
            else:
                pieces.extend([[start,text[start:paren_pat.start()]],[paren_pat.start(2),paren_pat.group(2)]])
                start = paren_pat.end()            
                ### paren_pat = parentheses_pattern3.search(text,paren_pat.end())
                paren_pat = parentheses_pattern_match(text,paren_pat.end(),3)
    if start and (len(text) > start):
        pieces.append([start,text[start:]])
    if len(pieces)==0:
        pieces=[[0,text]]
    pieces2 = []
    ## Part 2: quotation mark off reliable units, separate these out
    for meta_start,piece in pieces:
        start = 0
        sing = single_quote_pattern.search(piece,start)
        doub = double_quote_pattern.search(piece,start)
        while (start < len(piece)) and (sing or doub):
            if doub and ((not sing) or ((sing.start() < doub.start()) and (sing.end()>doub.end()))):
                ## if doub nested inside of singular, assume singular quotes are in error
                pieces2.extend([[meta_start+start,piece[start:doub.start()]],\
                                [meta_start+doub.start(2),doub.group(2)]])
                start = doub.end()
                doub = double_quote_pattern.search(piece,start)
                if sing:
                    sing = single_quote_pattern.search(piece,start)
            elif (not doub) or (sing.end() < doub.start()):
                ## if there is no doub or if sing completely precedes doub
                pieces2.extend([[meta_start+start,piece[start:sing.start()]],\
                                [meta_start+sing.start(3),sing.group(3)]])
                start = sing.end() 
                sing = single_quote_pattern.search(piece,start)             
            elif (sing.start()>doub.start()) and (sing.end() < doub.end()):
                ## nesting sing inside doub
                pieces2.extend([[meta_start+start,piece[start:doub.start()]],\
                                [meta_start+doub.start(),piece[doub.start():sing.start()]],\
                                    [meta_start+sing.start(3),sing.group(3)],\
                                    [meta_start+sing.end(),piece[sing.end():doub.end()]]])
                start = doub.end()
                doub = double_quote_pattern.search(piece,start)
            elif doub.end() < sing.start():                
                ## doub first -- do doub only  (treat similarly to first case, except don't reinitialize singular)
                pieces2.extend([[meta_start+start,piece[start:doub.start()]],\
                                [meta_start+doub.start(2),doub.group(2)]])
                start = doub.end()
                doub = double_quote_pattern.search(piece,start)
                ## otherwise it is some sort of error
            elif doub and sing:
                if doub.start()<sing.start():
                    start = doub.start()+1
                    doub = double_quote_pattern.search(piece,start)
                else:
                    start = sing.start(1)+1
                    sing = single_quote_pattern.search(piece,start) 
            elif doub:
                start = doub.start()+1
                doub = double_quote_pattern.search(piece,start)
            elif sing:
                start = sing.start(1)+1
                sing = single_quote_pattern.search(piece,start) 
            else:
                print('Error in program regarding single and double quotes')
                print('piece:',piece)
                print('text:',text)
                ## this is probably not a real instance of quotation
        if start < len(piece):
            pieces2.append([meta_start+start,piece[start:]])
    ## Part III: split into chunks by commas and abbreviations
    ## each resulting piece an then be analyzed syntactically based on word class
    for meta_start,piece in pieces2:
        ## parse each piece separately
        ## current_out_list = []
        ## need a new version of splitters that provides offsets
        start = 0
        split_position = next_splitter_pattern(piece,start) 
        if not split_position:
            last = True
        else:
            last = False
        current_latin_pp_struct = False
        latin_pp = False
        latin_pp_start = False
        while split_position or last:
            start_match = first_character_pattern.search(piece,start)
            if start_match:
                start = start_match.start()
            if last:
                piece2 = piece[start:]
            else:
                piece2 = piece[start:split_position.start()]
            current_out_list = []
            current_pos_list = []
            latin_pp = False
            pre_np = False
            first_piece = True
            last_pos = False
            piece3, next_word_start,next_word_end = get_next_word(piece2,0)
            if piece3:
                piece2_start = next_word_start
                term_start = piece2_start+start ## start is the start for one level up
            while piece3:
                if piece3.istitle():
                    is_capital = True
                else:
                    is_capital = False
                lower = piece3.lower()
                word_offset = next_word_start + start + meta_start + offset
                if piece3 == '':
                    pass
                else:
                    pos = guess_pos(lower,is_capital,offset=word_offset)
                    if current_latin_pp_struct:
                        if lower in latin_pp_dict:
                            ## if there are two latin_pps in a row
                            ## the first is not part of a term (we assume)
                            ## this restarts the latin_pp buffer
                            current_latin_pp_struct = {'words': [lower],'dict_entry':latin_pp_dict[lower],'start':next_word_start+start}
                        elif lower in current_latin_pp_struct['dict_entry']:
                            current_latin_pp_struct['words'].append(lower)
                            current_latin_pp_struct['dict_entry']= \
                              current_latin_pp_struct['dict_entry'][lower]
                            pos = 'INSIDE_LATIN_PP'
                        elif '*NONE*' in current_latin_pp_struct['dict_entry']:
                            ## a PP has been fully matched, ending with
                            ## the preceding word
                            pp_length = len(current_latin_pp_struct['words'])
                            latin_pp = ' '.join(current_latin_pp_struct['words'])
                            current_out_list = [latin_pp]
                            current_pos_list = ['TECH_ADJECTIVE']
                            ## term_start = min(term_start,current_latin_pp_struct['start'])
                            term_start = current_latin_pp_struct['start']
                            current_latin_pp_struct = False
                        ## if completed structure,
                        ## make one big tech_adjective
                    elif lower in latin_pp_dict:
                        current_latin_pp_struct = {'words': [lower],'dict_entry':latin_pp_dict[lower],'start':next_word_start+start}
                    if (pos == 'SKIPABLE_ADJ') and is_capital:
                        pos = 'ADJECTIVE'
                    if (pos in ['SKIPABLE_ADJ']) and not(current_out_list):
                        pass
                    # elif current_latin_pp_struct and not latin_pp:
                    #     pass
                    elif pos in ['DET','PREP']:
                        pre_np = True
                        if current_out_list:
                            term_string = interior_white_space_trim(piece2[term_start-start:piece2_start])
                        else:
                            term_string = False
                        if (term_string == False) or (term_string == ''):
                            pass
                        elif current_out_list and (filter_off or topic_term_ok_boolean(current_out_list,current_pos_list,term_string)):
                            start_offset = term_start + meta_start+offset
                            end_offset = piece2_start+start+meta_start+offset
                            topic_terms.append([start_offset,end_offset,term_string,latin_pp,current_pos_list])
                        current_out_list = []
                        current_pos_list = []
                        latin_pp = False
                    elif pos in ['AMBIG_POSSESS','POSSESS']:
                        if piece3.endswith("'s"):
                            piece3 = piece3[:-2]
                            end_minus = 2
                        else:
                            end_minus = 0
                        if current_out_list:
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                        else:
                            current_out_list = [piece3]
                            current_pos_list = [pos]
                            term_start = piece2_start + start
                        if current_out_list:
                            term_string = interior_white_space_trim(piece2[term_start-start:next_word_end-end_minus])
                        else:
                            term_string = False
                        if filter_off or topic_term_ok_boolean(current_out_list,current_pos_list,term_string):
                            start_offset = term_start + meta_start+offset
                            end_offset = next_word_end+start+meta_start+offset-end_minus
                            topic_terms.append([start_offset,end_offset,term_string,latin_pp,current_pos_list])
                        current_out_list = []
                        current_pos_list = []
                        latin_pp = False
                        pre_np = False
                        first_piece=False
                    elif (len(piece3)==1) and piece3.isalpha() and (len(piece2)>next_word_start+1) \
                         and (piece2[next_word_end]=='.'):
                         ## reset next_word_end and piece3
                        next_word_end = next_word_end+1
                        piece3 = piece2[next_word_start:next_word_end]
                        pos = 'NOUN'  ## initial can be part of term, but not term by itself
                        if current_out_list:
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                        else:
                            current_out_list = [piece3]
                            current_pos_list = [pos]
                            term_start = next_word_start + start
                        pre_np = False
                        first_piece = False
                    elif (pos == 'ROMAN_NUMBER') and current_out_list and (len(current_out_list)>=1) and \
                         (current_pos_list[-1] in ['NOUN_OOV','NOUN','AMBIG_NOUN','PLURAL','AMBIG_PLURAL']):
                        if current_out_list:
                            term_string = interior_white_space_trim(piece2[term_start-start:next_word_end])
                        else:
                            term_string = False
                        if filter_off or topic_term_ok_boolean(current_out_list,current_pos_list,term_string):
                            ## Roman Numerals can tack on to other terms
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                            start_offset = term_start + meta_start+offset
                            end_offset = next_word_end+start+meta_start+offset
                            topic_terms.append([start_offset,end_offset,term_string,latin_pp,current_pos_list])
                        current_out_list = []
                        current_pos_list = []
                        latin_pp = False
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
                            pass
                        else:
                            if current_out_list:
                                term_string = interior_white_space_trim(piece2[term_start-start:next_word_end])
                            else:
                                term_string = False
                            if filter_off or topic_term_ok_boolean(current_out_list,current_pos_list,term_string):
                                start_offset = term_start + meta_start+offset
                                end_offset = next_word_end+start+meta_start+offset
                                topic_terms.append([start_offset,end_offset,term_string,latin_pp,current_pos_list])
                                current_out_list = []
                                current_pos_list = []
                                latin_pp = False
                            else:
                                current_out_list = []
                                current_pos_list = []
                                latin_pp = False
                        pre_np = False
                        first_piece=False
                    elif pos in ['NOUN','POSSESS_OOV','AMBIG_NOUN','PERLOC_NAME','NOUN_OOV']:
                        ## out of vocab possessive
                    ## evaluate piece by POS
                    ## looking for sequences of pieces that either: 
                    ## a) are unambigous nouns; or b) are OOV words
                        if piece3.endswith("'s"):
                            piece3a = piece3[:-2]
                            piece3b = piece3[-2:]
                            if current_out_list:
                                current_out_list.append(piece3a)
                                current_pos_list.append(pos)
                            else:
                                current_out_list = [piece3]
                                current_pos_list = [pos]
                                term_start = next_word_start + start
                            term_string = interior_white_space_trim(piece2[term_start-start:next_word_end-2])
                            if filter_off or topic_term_ok_boolean(current_out_list,current_pos_list,term_string):
                                start_offset = term_start + meta_start+offset
                                end_offset = next_word_end+start+meta_start+offset
                                topic_terms.append([start_offset,end_offset,term_string,latin_pp,current_pos_list])
                                current_out_list = []
                                current_pos_list = []
                                latin_pp = False
                            else:
                                current_out_list = []
                                current_pos_list = []
                                latin_pp = False
                            pre_np = True
                            first_piece=False
                        elif current_out_list:
                            current_out_list.append(piece3)
                            current_pos_list.append(pos)
                            pre_np = False
                            first_piece=False
                        else:
                            current_out_list = [piece3]
                            current_pos_list = [pos]
                            term_start = next_word_start + start
                            pre_np = False
                            first_piece=False
                    elif current_out_list and (last_pos == 'NOUN_OOV') and \
                         ((not piece3 in signal_set) or is_capital) and \
                            ((pos in ['TECH_ADJECTIVE','NATIONALITY_ADJ']) or ((pos == 'ADJECTIVE') and (is_capital or (term_dict_check(piece3,stat_adj_dict))))):
                        current_out_list.append(piece3)
                        current_pos_list.append(pos)
                    elif (current_out_list == False) and \
                         ((not piece3 in signal_set) or is_capital) and \
                         ((pos in ['TECH_ADJECTIVE','NATIONALITY_ADJ']) or \
                              ((pos in ['VERB','AMBIG_VERB']) and (lower.endswith('ed') or lower.endswith('ing'))) or \
                              ((pos == 'ADJECTIVE') and (is_capital or term_dict_check(piece3,stat_adj_dict)))):
                        current_out_list = [piece3]
                        current_pos_list = [pos]
                        latin_pp = False
                        term_start = next_word_start + start
                        pre_np = False
                        first_piece=False                                    
                    elif (pre_np or first_piece or (last_pos in ['VERB','AMBIG_VERB']))  and (current_out_list == False) and \
                         ((not piece3 in signal_set) or is_capital) and \
                            (((pos in ['VERB','AMBIG_VERB']) and lower.endswith('ed')) or \
                                 ((pos == 'ADJECTIVE') and (is_capital or term_dict_check(piece3,stat_adj_dict))) or \
                                 ((pos in ['TECH_ADJECTIVE','NATIONALITY_ADJ']))):
                        ## considering allowing -ing verbs also, but this causes problems
                        current_out_list = [piece3]
                        current_pos_list = [pos]
                        latin_pp = False
                        term_start = next_word_start + start
                        pre_np = False
                        first_piece=False
                    elif current_out_list and (pos in ['TECH_ADJECTIVE','ADJECTIVE','NATIONALITY_ADJ']) and (last_pos in ['TECH_ADJECTIVE','ADJECTIVE','NATIONALITY_ADJ']) and ((not piece3 in signal_set) or is_capital or term_dict_check(piece3,stat_adj_dict)):
                        current_out_list.append(piece3)
                        current_pos_list.append(pos)
                        pre_np = False
                        first_piece = False
                    else:
                        if current_out_list:
                            term_string = interior_white_space_trim(piece2[term_start-start:piece2_start])
                        else:
                            term_string = False
                        if current_out_list and (filter_off or topic_term_ok_boolean(current_out_list,current_pos_list,term_string)):
                            start_offset = term_start + meta_start+offset
                            end_offset = piece2_start+start+meta_start+offset
                            topic_terms.append([start_offset,end_offset,term_string,latin_pp,current_pos_list])
                            current_out_list = []
                            current_pos_list = []
                            latin_pp = False
                            pre_np = False
                            first_piece=False
                            if (len(piece3)>1) and pos in ['NOUN','POSSESS_OOV','AMBIG_NOUN','PERLOC_NAME','NOUN_OOV']:
                                if piece3.endswith("'s"):
                                    piece3a = piece3[:-2]
                                    piece3b = piece3[-2:]
                                    current_out_list = [piece3]
                                    current_pos_list = [pos]
                                    term_start = next_word_start + start
                                    term_string = interior_white_space_trim(piece2[term_start-start:next_word_end-2])
                                    first_piece = True
                                    pre_np = True
                                else:
                                    current_out_list = [piece3]
                                    current_pos_list = [pos]
                                    latin_pp = False
                                    term_start = next_word_start + start
                                    pre_np = False
                                    first_piece = True
                            elif ((not piece3 in signal_set) or is_capital) and \
                                 ((pos in ['TECH_ADJECTIVE','NATIONALITY_ADJ']) or \
                                 ((pos in ['VERB','AMBIG_VERB']) and (lower.endswith('ed') or lower.endswith('ing'))) or \
                                 ((pos == 'ADJECTIVE') and (is_capital or term_dict_check(piece3,stat_adj_dict)))):
                                current_out_list = [piece3]
                                current_pos_list = [pos]
                                latin_pp = False
                                term_start = next_word_start + start
                                pre_np = False
                                first_piece=False                                    
                            else:
                                current_out_list = []
                                current_pos_list = []
                                latin_pp = False
                                pre_np = False
                                first_piece=False
                            last_pos = pos
                        elif (len(piece3)>1) and pos in ['NOUN','POSSESS_OOV','AMBIG_NOUN','PERLOC_NAME','NOUN_OOV']:
                            if piece3.endswith("'s"):
                                piece3a = piece3[:-2]
                                piece3b = piece3[-2:]
                                current_out_list = [piece3]
                                current_pos_list = [pos]
                                term_start = next_word_start + start
                                term_string = interior_white_space_trim(piece2[term_start-start:next_word_end-2])
                                if filter_off or topic_term_ok_boolean(current_out_list,current_pos_list,term_string):
                                    start_offset = term_start + meta_start+offset
                                    end_offset = next_word_end+start+meta_start+offset
                                    topic_terms.append([start_offset,end_offset,term_string,latin_pp,current_pos_list])
                                    current_out_list = []
                                    current_pos_list = []
                                else:
                                    current_out_list = []
                                    current_pos_list = []
                                latin_pp = False
                                pre_np = True
                                first_piece=False
                            else:
                                current_out_list = [piece3]
                                current_pos_list = [pos]
                                latin_pp = False
                                term_start = next_word_start + start
                                pre_np = False
                                first_piece = True
                        elif ((not piece3 in signal_set) or is_capital) and \
                             ((pos in ['TECH_ADJECTIVE','NATIONALITY_ADJ']) or \
                              ((pos in ['VERB','AMBIG_VERB']) and (lower.endswith('ed') or lower.endswith('ing'))) or \
                              ((pos == 'ADJECTIVE') and (is_capital or term_dict_check(piece3,stat_adj_dict)))):
                              current_out_list = [piece3]
                              current_pos_list = [pos]
                              latin_pp = False
                              term_start = next_word_start + start
                              pre_np = False
                              first_piece=False                                    
                        else:
                            current_out_list = []
                            current_pos_list = []
                            pre_np = False
                            first_piece=False
                            latin_pp = False
                    last_pos = pos
                piece2_start = next_word_end
                piece3, next_word_start,next_word_end = get_next_word(piece2,piece2_start)
            if current_out_list:
                term_string = interior_white_space_trim(piece2[term_start-start:piece2_start])
                if filter_off or topic_term_ok_boolean(current_out_list,current_pos_list,term_string):
                    start_offset = term_start + meta_start+offset
                    end_offset = piece2_start+start+meta_start+offset
                    topic_terms.append([start_offset,end_offset,term_string,latin_pp,current_pos_list])
            if split_position:
                start = split_position.end()
                split_position = next_splitter_pattern(piece,start)
            if not (last or split_position):
                last = True
            else:
                last = False
    return(topic_terms)

def get_term_lemma(term,term_type=False):
    ## add plural --> singular
    ## print(term,term_type)
    global lemma_dict
    last_word_pat = re.compile('[a-z]+$',re.I)
    if term in lemma_dict:
        return(lemma_dict[term])
    elif term_type and (term_type != 'chunk-based'):
        ## this takes care of all the patterned cases
        output = term.upper()
    elif (term in abbr_to_full_dict) and (len(abbr_to_full_dict[term])>0) and (term.isupper() or (not term in pos_dict) or (term in jargon_words)):
        output = abbr_to_full_dict[term][0]
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
            elif last_word.endswith('(s)'):
                output = term[:-3].upper()
            elif (len(last_word)>1) and last_word.endswith('s') and term[-1].isalpha() and (not last_word[-2] in 'u'):
                output = term[:-1].upper()
            else:
                output = term.upper()
        elif re.search('\([sS]\)$',term):
            output = term[:-3].upper()
        else:
            output = term.upper()
    lemma_dict[term] = output                
    return(output)

def get_compound_lemma(compound_term,first_term,second_term):
    global lemma_dict
    if compound_term in lemma_dict:
        return(lemma_dict[compound_term])
    else:
        first_lemma = get_term_lemma(first_term,term_type='chunk-based')
        second_lemma = get_term_lemma(second_term,term_type='chunk-based')
        output = (second_lemma+' '+first_lemma).upper()
        lemma_dict[compound_term] = output
        return(output)

def term_is_org(term):
    words = divide_sentence_into_words_and_start_positions(term)
    perloc_names = 0
    Fail = False
    for position,word in words:
        lower = word.lower()
        is_capital = re.search('^[A-Z][a-z]',word)
        if is_capital and (lower in pos_dict) and ('PERLOC_NAME' in pos_dict[lower]):
            perloc_names = perloc_names+1
        if is_capital or closed_class_check2.search(word):
            pass
        else:
            Fail = True
    if len(words) <= 1 or (perloc_names == 0):
        return(False)
    elif ((len(words) == 2) and (perloc_names == 2)):
        ## all words of an organization except for closed class words should
        ## be capitalized.
        ## However, 2 word capitalized phrases can be person names, particularly if
        ## both words are in our person dictionary, so let's not include these
        print('The following may be a person name:',term)
        return(False)
    elif Fail:
        return(False)
    else:
        return(True)        

def term_is_org_tester(term):
    if not re.search('[A-Z]',term[0]):
        return(False)
    words = divide_sentence_into_words_and_start_positions(term)
    perloc_names = 0
    Fail = False
    ambiguous_perloc_names = 0
    word_pattern = []
    if re.search('^[A-Z][a-z]',words[-1][1]):
        if last_word_organization.search(words[-1][1]):
            ends_in = 'ORG'
        elif last_word_gpe.search(words[-1][1]):
            ends_in = 'GPE'
        elif last_word_loc.search(words[-1][1]):
            ends_in = 'LOC'
        else:
            ends_in = False
    else:
        ends_in = False
    for position,word in words:
        lower = word.lower()
        is_capital = re.search('^[A-Z][a-z]',word)
        if is_capital and (lower in pos_dict) and ('PERLOC_NAME' in pos_dict[lower]):
            perloc_names = perloc_names+1
            if len(pos_dict[lower])>1:
                ambiguous_perloc_names = ambiguous_perloc_names+1
                word_pattern.append('ambig_name')
            else:
                word_pattern.append('name')
        else:
            word_pattern.append('not_name')            
        if is_capital or closed_class_check2.search(word):
            pass
        else:
            Fail = True
    if not ambig_last_word_org.search(words[-1][1]):
        length_name_criterion = True
    elif (len(words)<4) or \
      ((perloc_names>1) and (perloc_names>ambiguous_perloc_names)):
        length_name_criterion = True
    else:
        length_name_criterion = False
    if (len(words) <= 1) or (not ' ' in term):
        return(False)
    elif (ends_in == 'ORG') and length_name_criterion:
        ne_class = 'ORGANIZATION'
    elif ends_in == 'GPE' and length_name_criterion:
        ne_class = 'GPE'
    elif ends_in == 'LOC' and length_name_criterion:
        ne_class = 'LOCATION'
    elif perloc_names == 0:
        return(False)
    elif (len(words) == 2) and (perloc_names == 2) and (perloc_names>ambiguous_perloc_names) and (' ' in term) \
      and (word_pattern[-1] == 'name'):
        ## all words of an organization except for closed class words should
        ## be capitalized.
        ## However, 2 word capitalized phrases can be person names, particularly if
        ## both words are in our person dictionary, so let's not include these
        ## If first word is a name and second word is a non-name, probably this is not
        ## an organization.
        ne_class = 'ORGANIZATION_OR_GPE'
    elif Fail:
        return(False)
    else:
        ## ne_class = 'ORGANIZATION'
        return(False)
    global term_id_number
    print(ne_class)
    return(True)

def term_is_org_with_write(outstream,term,instances):
    if not re.search('[A-Z]',term[0]):
        return(False)
    words = divide_sentence_into_words_and_start_positions(term)
    perloc_names = 0
    Fail = False
    ambiguous_perloc_names = 0
    word_pattern = []
    if re.search('^[A-Z][a-z]',words[-1][1]):
        if last_word_organization.search(words[-1][1]):
            ends_in = 'ORG'
        elif last_word_gpe.search(words[-1][1]):
            ends_in = 'GPE'
        elif last_word_loc.search(words[-1][1]):
            ends_in = 'LOC'
        else:
            ends_in = False
    else:
        ends_in = False
    for position,word in words:
        lower = word.lower()
        is_capital = re.search('^[A-Z][a-z]',word)
        if is_capital and (lower in pos_dict) and ('PERLOC_NAME' in pos_dict[lower]):
            perloc_names = perloc_names+1
            if len(pos_dict[lower])>1:
                ambiguous_perloc_names = ambiguous_perloc_names+1
                word_pattern.append('ambig_name')
            else:
                word_pattern.append('name')
        else:
            word_pattern.append('not_name')            
        if is_capital or closed_class_check2.search(word):
            pass
        else:
            Fail = True
    if not ambig_last_word_org.search(words[-1][1]):
        length_name_criterion = True
    elif (len(words)<4) or \
      ((perloc_names>1) and (perloc_names>ambiguous_perloc_names)):
        length_name_criterion = True
    else:
        length_name_criterion = False
    if (len(words) <= 1) or (not ' ' in term):
        return(False)
    elif (ends_in == 'ORG') and length_name_criterion:
        ne_class = 'ORGANIZATION'
    elif (ends_in == 'GPE') and length_name_criterion:
        ne_class = 'GPE'
    elif (ends_in == 'LOC') and length_name_criterion:
        ne_class = 'LOCATION'
    elif perloc_names == 0:
        return(False)
    elif (len(words) == 2) and (perloc_names == 2) and (perloc_names>ambiguous_perloc_names) and (' ' in term) \
      and (word_pattern[-1] == 'name'):
        ## all words of an organization except for closed class words should
        ## be capitalized.
        ## However, 2 word capitalized phrases can be person names, particularly if
        ## both words are in our person dictionary, so let's not include these
        ## If first word is a name and second word is a non-name, probably this is not
        ## an organization.
        ne_class = 'ORGANIZATION_OR_GPE'
    elif Fail:
        return(False)
    else:
        ## ne_class = 'ORGANIZATION'
        return(False)
    global term_id_number
    for start,end in instances:
        term_id_number = 1 + term_id_number
        outstream.write(ne_class+' ID="NYU_ID_'+str(term_id_number)+'" STRING="'+term+'"')
        outstream.write(' START='+str(start)+' END='+str(end)+os.linesep)
    return(True)

def org_head_ending(term,head_hash):
    if (term in head_hash) and org_ending_pattern.search(head_hash[term]):
        return(True)


term_id_number = 0

def term_string_edit(instring):
    output = re.sub('>','&gt;',instring)
    return(output)

def write_term_summary_fact_set(outstream,term,instances,lemma_count,head_term=False,head_lemma=False,term_type=False,latin_pp=False,term_subtype=False):
    global term_id_number
    global lemm_dict
    frequency = len(instances)
    lemma = lemma_dict[term]
    lemma_freq = lemma_count[lemma]
    for start,end in instances:
        term_id_number = 1 + term_id_number
        if term_type == 'url':
            outstream.write('URL ID="NYU_TERM_'+str(term_id_number)+'" STRING="'+term_string_edit(term)+'"'+' FREQUENCY='+str(frequency))
        else:
            outstream.write('TERM ID="NYU_TERM_'+str(term_id_number)+'" STRING="'+term_string_edit(term)+'"'+' FREQUENCY='+str(frequency))
        outstream.write(' START='+str(start)+' END='+str(end))
        outstream.write(' LEMMA="'+term_string_edit(lemma)+'" LEMMA_FREQUENCY='+str(lemma_freq))
        if head_term:
            outstream.write(' HEAD_TERM="'+term_string_edit(head_term)+'"')
        if head_lemma:
            outstream.write(' HEAD_LEMMA="'+term_string_edit(head_lemma)+'"')
        if term_type:
            ## includes lists of POS tags
            if (term_type == 'chunk-based') and isinstance(term_subtype,list):
                outstream.write(' TERM_PATTERN_TYPE="'+'chunk-based:'+str(term_subtype)+'"')
            else:
                outstream.write(' TERM_PATTERN_TYPE="'+term_type+'"')
        if latin_pp:
            outstream.write(' Contains_Latin_PP="'+latin_pp+'"')
        outstream.write(os.linesep)

def write_term_becomes_article_citation(outstream,term,instances):
    global term_id_number
    for start,end in instances:
        term_id_number = 1 + term_id_number
        outstream.write('CITATION ID="NYU_ID_'+str(term_id_number)+'" STRING="'+term+'" CITE_CLASS="article"')
        outstream.write(' START='+str(start)+' END='+str(end)+os.linesep)

def write_term_becomes_organization(outstream,term,instances):
    global term_id_number
    for start,end in instances:
        term_id_number = 1 + term_id_number
        outstream.write('ORGANIZATION ID="NYU_ID_'+str(term_id_number)+'" STRING="'+term+'"')
        outstream.write(' START='+str(start)+' END='+str(end)+os.linesep)

def write_term_becomes_gpe(outstream,term,instances):
    global term_id_number
    for start,end in instances:
        term_id_number = 1 + term_id_number
        outstream.write('GPE ID="NYU_ID_'+str(term_id_number)+'" STRING="'+term+'"')
        outstream.write(' START='+str(start)+' END='+str(end)+os.linesep)
        
def write_term_becomes_person(outstream,term,instances):
    global term_id_number
    for start,end in instances:
        term_id_number = 1 + term_id_number
        outstream.write('PERSON ID="NYU_ID_'+str(term_id_number)+'" STRING="'+term+'"')
        outstream.write(' START='+str(start)+' END='+str(end)+os.linesep)

def filter_txt_triples_by_start_end(start_end_filters,txt_strings):
    ## ** 57 **
    ## start_end_filters = sorted list of start end pairs
    ## txt_strings = sorted triples: start,end,string
    ## next deal with modified strings
    if len(start_end_filters)==0:
        return(txt_strings)
    output = []
    next_block_start, next_block_end = start_end_filters.pop(0)
    if len(txt_strings) == 0:
        done = True
    else: 
        done = False
    start = 'not ready'
    while not done:
        if start == 'not ready':
            if len(txt_strings) == 0:
                break
            ## if there are no more triples, we are done here
            else:
                start, end, string = txt_strings.pop(0)
        if (next_block_end == 'Done'):
            output.append([start,end,string])
            start = 'not ready'
        else:
            while (next_block_end < start) and (len(start_end_filters)>0):
                next_block_start, next_block_end = start_end_filters.pop(0)
            if (len(start_end_filters)==0) and (next_block_end < start):
                next_block_end = 'Done'
        if next_block_end == 'Done':
            pass        
        elif (start == next_block_start) and (end == next_block_end):
            ## trivial case of identity, ignore start/end
            start = 'not ready'
        elif end <= next_block_start:
            ## case 1 block is passed current start and end (no effect)
            output.append([start,end,string])
            start = 'not ready'
        elif (start >= next_block_start) and (start <= next_block_end):
            ## this occurs if start is somewhere inside block
            if end > next_block_end:
                ## case 2: this is the overlapping case where start end overlaps the block, but starts
                ## after the block starts
                start = next_block_end
                new_size = end-start
                if new_size <2:
                    start = 'not ready'
                elif not ' ' in string[-1*(new_size+1):(-1*(new_size-1))]:
                    ## new string should start with a space or previous string should end with one
                    if ' ' in string[-1*new_size:]:
                        space_position = string[-1*new_size:].index(' ')
                        start = start + space_position
                        new_size = end-start
                        modified_string = string[-1*new_size:]
                        output.append([start,end,modified_string])
                        start = 'not ready'
                    else:
                        start = 'not ready'
                else:
                    modified_string = string[-1*new_size:]
                    # if len(modified_string) != end-start:
                    #     print(1,'end',end,'start',start)
                    #     print('length',len(modified_string),modified_string)
                ### modified_string = **** 57 ****
                    output.append([start,end,modified_string])
                    start = 'not ready'
            else:
                ## case 3 this should only occur if start,end are totally inside of the block
                ## in which case this start/end segment should be ignored
                start = 'not ready'
        elif (start <= next_block_start) and (end <=next_block_end):
            ## this only arises if start is before the block and
            ## end overlaps it
            end = next_block_start
            new_size = end-start
            ### modified_string = **** 57 ****
            modified_string = string[:new_size]
            output.append([start,end,modified_string])
            start = 'not ready'
        elif (start < next_block_start) and (end > next_block_end):
            ## if the block is inside of start/end
            block_size=next_block_end-next_block_start
            end1 = next_block_start
            new_size = end1-start
            modified_string = string[:new_size]
            ### modified_string = **** 57 ****
            if len(modified_string) != end1-start:
                print(3,'end1',end1,'start',start)
                print('length',len(modified_string),modified_string)
            output.append([start,end1,modified_string])
            ### modified_string = **** 57 ****
            start = next_block_end
            ## leave end alone
            ### modified_string = **** 57 ****
            string = string[new_size+block_size:]
            ## this new start,end,string is compared to the next
            ## block -- (the previous blocking string cut it into 2 parts)
        else:
            ## This should never happen
            print('Unexpected condition for filter_txt_triples_by_start_end')
            print(start,end,string)
            print(next_block_start,next_block,end)
            output.append([start,end,string])
            start = 'not ready'
    return(output)

def resolve_term_type(term_type,term_subtype):
    ## do not change type 'chemical'
    ## due to interaction with global_formula_filter
    if isinstance(term_subtype,list):
        return(term_type,term_subtype)
    else:
        return(term_type,False)

def find_inline_terms(lines,fact_file,pos_file,terms_file,marked_paragraphs=False,\
                      filter_off=False,start_end_filters=False):
    global abbr_to_full_dict
    global full_to_abbr_dict
    global term_id_number
    global term_hash
    global term_latin_pp_hash
    global lemma_dict
    term_id_number = 0
    line_break_match = os.linesep+'(([ \t]*)[^A-Z \t])'
    start_ends = []
    txt_strings = []
    term_hash = {}
    pos_offset_table.clear()
    lemma_dict.clear()
    lemma_count = {}
    head_hash = {}
    term_type_hash = {}
    term_latin_pp_hash = {}
    structure_pattern = re.compile('STRUCTURE *TYPE="TEXT" *START=([0-9]*) *END=([0-9]*)',re.I)
    if os.path.isfile(pos_file):
        load_pos_offset_table(pos_file)
    else:
        print('Warning POS file does not exist:',pos_file)
    with open(fact_file) as instream:
        for line in instream:
            match = structure_pattern.search(line)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                start_ends.append([start,end])
    start_ends.sort()
    if (len(start_ends) > 1) and (not marked_paragraphs):
        marked_paragraphs = True
    else:
        marked_paragraphs = False
    big_txt = ''        
    if marked_paragraphs:
        for line in lines:
            big_txt = big_txt + re.sub(os.linesep,' ',line)
        for start,end in start_ends:
            txt_strings.append([start,end,big_txt[start:end]])
    elif len(start_ends)>0:
        ## changed from else, to prevent a bug (when start_ends is empty)
        start,end = start_ends[0]
        end = 0
        current_block = ''
        so_far = start
        for line in lines:
            end = so_far + len(line)
            next_line = re.sub(os.linesep,' ',line)
            current_block = current_block + next_line
            big_txt = big_txt + next_line
            if (not re.search('[a-zA-z]',line)) or re.search('[.?:!][ \t'+os.linesep+']*$',line):
                txt_strings.append([start,end,current_block])
                current_block = ''
                start = end
            so_far = end
        if current_block != '':
            txt_strings.append([start,end,current_block])
    if start_end_filters:
        txt_strings = filter_txt_triples_by_start_end(start_end_filters,txt_strings)
    for start,end,text in txt_strings:
        text = re.sub(line_break_match, ' \g<1>',text)
        if (text.count('\t')+text.count(' '))<(len(text)/3):
            ##  ignore tables
            term_quints = get_topic_terms(text,start,filter_off=filter_off)
            formulaic_tuples = get_formulaic_term_pieces(text,start)
            term_tuples = merge_formulaic_and_regular_term_tuples(term_quints,formulaic_tuples)
        else:
            term_tuples = []
        compound_tuples = []
        last_tuple = False
        test_len = [0,0]
        # for term in term_tuples:
        #     if len(term)==6:
        #         test_len[0]+=1
        #     else:
        #         print(term)
        #         input('pause')
        #         test_len[1]+=1
        # print(test_len)
        for t_start,t_end,term,latin_pp,term_subtype,term_type in term_tuples:
            ## for now we will limit compounding not to function and
            ## lemmas not to merge entries unless term_type ==
            ## 'chunk-based'
            if term == False:
                pass
            elif term in term_hash:
                term_hash[term].append([t_start,t_end])
                lemma = get_term_lemma(term,term_type=term_type)
                if lemma in lemma_count:
                    lemma_count[lemma]=lemma_count[lemma]+1
                else:
                    lemma_count[lemma]=1
            else:
                term_hash[term]=[[t_start,t_end]]
                term_type_hash[term] = resolve_term_type(term_type,term_subtype)
                if latin_pp:
                    term_latin_pp_hash[term] = latin_pp
                lemma = get_term_lemma(term,term_type=term_type)
                if lemma in lemma_count:
                    lemma_count[lemma]=lemma_count[lemma]+1
                else:
                    lemma_count[lemma]=1
            if last_tuple and (t_start>last_tuple[1]) and (last_tuple[3] in [False,'chunk-based']) and (term_type in [False, 'chunk-based']):
                inbetween = compound_inbetween_string.search(big_txt[last_tuple[1]:t_start])
                if inbetween:
                    compound_term = interior_white_space_trim(big_txt[last_tuple[0]:t_end])
                    compound_tuple = [last_tuple[0],t_end,compound_term,False,'COMPOUND','chunk-based']
                    if compound_term == False:
                        pass
                    elif compound_term in term_hash:
                        term_hash[compound_term].append([last_tuple[0],t_end])
                        lemma = get_compound_lemma(compound_term,last_tuple[2],term)
                        if lemma in lemma_count:
                            lemma_count[lemma]=lemma_count[lemma]+1
                        else:
                            lemma_count[lemma]=1
                    else:
                        term_hash[compound_term]=[[last_tuple[0],t_end]]
                        head_hash[compound_term]=last_tuple[2]
                        term_type_hash[compound_term]=['COMPOUND',False]
                        lemma = get_compound_lemma(compound_term,last_tuple[2],term)
                        if lemma in lemma_count:
                            lemma_count[lemma]=lemma_count[lemma]+1
                        else:
                            lemma_count[lemma]=1
                    last_tuple=compound_tuple[:]
                elif not re.search('[^\s]',big_txt[last_tuple[1]:t_start]):
                    compound_term = interior_white_space_trim(big_txt[last_tuple[0]:t_end])
                    compound_tuple = [last_tuple[0],t_end,compound_term,False,'COMPOUND','chunk-based']
                    if compound_term == False:
                        pass
                    elif compound_term in term_hash:
                        term_hash[compound_term].append([last_tuple[0],t_end])
                        lemma = get_compound_lemma(compound_term,last_tuple[2],term)
                        if lemma in lemma_count:
                            lemma_count[lemma]=lemma_count[lemma]+1
                        else:
                            lemma_count[lemma]=1
                    else:
                        term_hash[compound_term]=[[last_tuple[0],t_end]]
                        ## if there is only blank space and no
                        ## preposition between terms, the
                        ## compounding is normal noun noun
                        ## compounding, rather than the inversion
                        ## used for noun prep noun sequences
                        lemma = get_compound_lemma(compound_term,last_tuple[2],term)
                        head_hash[compound_term]=term
                        if lemma in lemma_count:
                            lemma_count[lemma]=lemma_count[lemma]+1
                        else:
                            lemma_count[lemma]=1
                        term_type_hash[compound_term]=['COMPOUND',False]
                else:
                    last_tuple=[t_start,t_end,term,term_type]
            else:
                last_tuple=[t_start,t_end,term,term_type]
    term_list = list(term_hash.keys())
    term_list.sort()
    global_formula_filter(term_list,term_hash,term_type_hash)
    with open(terms_file,'w') as outstream:
        for term in term_list:
            if term in term_latin_pp_hash:
                latin_pp = term_latin_pp_hash[term]
            else:
                latin_pp = False
            if term == '':
                print('*',term_type_hash[term])
            if (term in term_type_hash) and \
              (not term_type_hash[term][0] in [False,'chunk-based','COMPOUND']) and \
              (not isinstance(term_type_hash[term],list)):
                ## type dependent line *** 57 ***
                write_term_summary_fact_set(outstream,term,term_hash[term],lemma_count,head_term=term.upper(),head_lemma=term.upper(),term_type=term_type_hash[term][0],latin_pp=latin_pp,term_subtype=term_type_hash[term][1])  
            elif et_al_citation.search(term):
                write_term_becomes_article_citation(outstream,term,term_hash[term])
            elif org_ending_pattern.search(term) or org_head_ending(term,head_hash):
                write_term_becomes_organization(outstream,term,term_hash[term])
            elif person_ending_pattern.search(term):
                write_term_becomes_person(outstream,term,term_hash[term])
            elif term_is_org_with_write(outstream,term,term_hash[term]):
                pass
            else:
                if term in head_hash:
                    head_term = head_hash[term]
                    if head_term in lemma_dict:
                        head_lemma = lemma_dict[head_term]
                    elif head_term in term_type_hash:
                        head_type,head_subtype = term_type_hash(head_term)
                        head_lemma = get_term_lemma(head_term,term_type=head_type)
                    else:
                        head_lemma = get_term_lemma(head_term)
                else:
                    head_term = False
                    head_lemma = False
                write_term_summary_fact_set(outstream,term,term_hash[term],lemma_count,head_term=head_term,head_lemma=head_lemma,term_type=term_type_hash[term][0],term_subtype=term_type_hash[term][1])

def get_pos_structure (line):
    start_end = re.compile('S:([0-9]+) E:([0-9]+)')
    line = line.strip(' '+os.linesep+'\t')
    if line[0:3]=='|||':
        fields = ['|||']
        fields2 = line[3:].split(' ||| ')
        fields.extend(fields2[1:])
    else:
        fields = line.split(' ||| ')
    word = fields[0].strip(' ')
    if len(fields)<3:
        start_end_out = False
    else:
        pos = fields[2].strip(' ')
        start_end_out = start_end.search(fields[1])
    if start_end_out:
        start,end = start_end_out.group(1).strip(' '),start_end_out.group(2).strip(' ')
        start = int(start)
        end=int(end)
    else:
        return(False,False,False,False)
    return(word,pos,start,end)

def guess_limited_ptb_pos(word):
    ## assumes these are words that are part of an Noun Group (an NP
    ## up to and including the head noun, but no right modifiers) --
    ## also assumes that these same words are missing from the original
    ## non lemma entry. Also, some wrong POS may result in correct analysis.
    
    ## Thus certain POS tags are assumed to be rare and we can take advantage
    ## of several biases based on this situation.
    ## COMLEX POS: ADJECTIVE ADVERB ADVPART AUX CARDINAL CCONJ DET NOUN ORDINAL
    ## PREP PRONOUN QUANT SCONJ SCOPE TITLE VERB WORD
    ## Added POS: PERLOC_NAME NATIONALITY
    ## others
    if (word in noun_base_form_dict) and word.endswith('s'):
        return('NNS')        
    elif not word in pos_dict:
        if word.endswith('s'):
            return('NNS')
        else:
            return('NN')
    else:
        entry = pos_dict[word]
    if 'PREP' in entry:
        return('IN')
    elif 'CCONJ' in entry:
        return('CC')
    elif 'CARDINAL' in entry:
        return('CD')
    elif 'ADJECTIVE' in entry:
        return('JJ')
    elif ('DET' in entry) or ('QUANT' in entry) or ('SCOPE' in entry):
        return('DT')
    elif ('TITLE' in entry) or ('NOUN' in entry):
        if word.endswith('s') and (not word.endswith('sis')):
            return('NNS')
        else:
            return('NN')
    elif ('VERB' in entry) and (word.endswith('ing') or word.endswith('ed') or word.endswith('en')):
        if word.endswith('ing'):
            return('VBG')
        else:
            return('VBN')
    elif ('NATIONALITY' in entry) or ('ORDINAL' in entry):
        return('JJ')
    else:
        for CPOS, PPOS in [['PERLOC_NAME','NNP'], ['ADVPART','RP'],['ADVERB','RB']]:
            ## CPOS = COMLEX POS
            ## PPOS = Penn Treebank POS
            if CPOS in entry:
                return(PPOS)
        return('NN')

def get_singular_from_plural(word):
    if '-' in word:
        sublist = word.split('-')
        base = ''
        for subword in sublist:
            ## split removed all hyphens so recursion will be limited to
            ## one level
            if (subword in noun_base_form_dict) or ((not subword in pos_dict) and (subword.endswith('s'))):
                subword = get_singular_from_plural(subword)
            if base == '':
                base = subword
            else:
                base = base + '-'+subword
    elif (len(word) == 1) or ((len(word) ==2) and not(word.endswith('s'))):
        return(word)
    elif (word in noun_base_form_dict):
        base = noun_base_form_dict[word][0]
        ## issue for bases --> basis or base
        ##           leaves --> leave and leaf
        ## and other cases of plurals with multiple base forms
    elif (len(word)>3) and word.endswith('ses') and (word[:-3]+'sis' in pos_dict) and ('NOUN' in pos_dict[word[:-3]+'sis']):
        base = word[:-3]+'sis'
    elif (len(word)>3) and word.endswith('ies') and (word[:-3]+'y' in pos_dict) and ('NOUN' in pos_dict[word[:-3]+'y']):
        base = word[:-3]+'y'
    elif word.endswith('s') and (word[:-1] in pos_dict) and ('NOUN' in pos_dict[word[:-1]]):
        base = word[:-1]
    elif (len(word)>2) and word.endswith('es') and (word[:-2] in pos_dict) and ('NOUN' in pos_dict[word[:-2]]):
        base = word[:-2]
    elif (len(word)>3) and word.endswith('ies'):
        base = word[:-3]+'y'
    elif word.endswith('s'):
        base = word[:-1]
    elif word.endswith('a'):
        ## based on word istribution
        if (len(word)>3) and re.search('[aeiou]ra$',word):
            base = word[:-3]+'us'
            ## covers  corpora --> corpus, genera --> genus, opera --> opus
        elif re.search('[in]a$',word):
            base = word[:-2]+'on'
            ## covers ganglion, phenomenon
            ## misses criterion, ganglion (hard to differentiate from
            ## default case below)
        elif word.endswith('oa'):
            base = word+'n'
            ## covers protazoan and similar words
        else:
            base = word[:-1]+'um'
            ## default case 
            ## plural to singular a--> um after d,i,l,r,t,b,n,v,u 
            ## r always after nonvowel -- no conflict with first case
    elif word.endswith('i'):
        base = word[:1]+'us'
        ## I don't see pattern with exceptions to i --> us
        ## catharsi	catharsis 
        ## ciceroni	cicerone
        ## dilettanti	dilettante
        ## genii	genie
        ## graffiti	graffito
        ## soli	solo
    elif (len(word)>2) and re.search('[aeiou]e$',word):
        base = word[:-1]
        ## no exceptions in word list
    elif word.endswith('e'):
        base = word[:-1]+'a'
        ## very few cases
    elif word.endswith('children'):
        base = word[:-3]
        ## most of exceptions to 'en' rule below
    elif (len(word)>2) and word.endswith('en'):
        base = word[:-2]+'an'
        ## other exceptions isolated: oxen, fellaheen and brethren
    elif (len(word)>2) and word.endswith('ux'):
        base = word[:-1]
        ## no exceptions in word list
    elif (len(word)>2) and word.endswith('im'):
        base = word[:-2]
    else:
        base = word
    return(base)

def process_lemma_term_tuples(current_tuples,string,lemma):
    ## just making sure it works
    ## find and convert all NNS to NN
    output_list = []
    if string.lower() == lemma.lower():
        for word,pos,chunk_tag in current_tuples:
            if pos == 'FW':
                pos = guess_limited_ptb_pos(word.lower())
            if pos == 'NNS':
                word = get_singular_from_plural(word)
                pos = 'NN'
            output_list.append([word,pos,chunk_tag])
    else:
        term_tokens = string.lower().split(' ')
        mini_pos_dict = {}
        for word,pos,chunk_tag in current_tuples:
            if pos == 'FW':
                pos = guess_limited_ptb_pos(word.lower())
            mini_pos_dict[word]=pos
        lemma_tokens = lemma.lower().split(' ')
        for num in range(len(lemma_tokens)):
            if num == 0:
                chunk = 'B-NP'
            else:
                chunk = 'I-NP'
            word = lemma_tokens[num]
            if word in mini_pos_dict:
                pos = mini_pos_dict[word]
            elif (len(word)>1) and word.endswith('s') and (word[:-1] in mini_pos_dict):
                if mini_pos_dict[word[:-1]] == 'NN':
                    pos = 'NN'
                    word = word[:-1]
                elif mini_pos_dict[word[:-1]] == 'NNP':
                    pos = 'NNPS'
                else:
                    pos = guess_limited_ptb_pos(word)
                    if pos == 'NNS':
                        word = get_singular_from_plural(word)
                        pos = 'NN'
            elif (len(word)>3) and word.endswith('ses') and ((word[:-3]+'sis') in mini_pos_dict) and \
              (mini_pos_dict[(word[:-3]+'sis')] == 'NNS'):
              pos = 'NN'
              word = word[:-3]
            elif (len(word)>2) and word.endswith('es') and (word[:-2] in mini_pos_dict):
                if mini_pos_dict[word[:-2]] == 'NN':
                    pos = 'NN'
                    word = word[:-2]
                elif mini_pos_dict[word[:-2]] == 'NNP':
                    pos = 'NNPS'
                else:
                    pos = guess_limited_ptb_pos(word)
                    if pos == 'NNS':
                        word = get_singular_from_plural(word)
                        pos = 'NN'
            elif (len(word)>3) and word.endswith('ies') and (word[:-3]+'y' in mini_pos_dict):
                if mini_pos_dict[word[:-3]+'y'] == 'NN':
                    pos = 'NN'
                    word = word[:-3]
                elif mini_pos_dict[word[:-3]] == 'NNP':
                    pos = 'NNPS'
                else:
                    pos = guess_limited_ptb_pos(word)
                    if pos == 'NNS':
                        word = get_singular_from_plural(word)
                        pos = 'NN'
            else:
                pos = guess_limited_ptb_pos(word)
                if pos == 'NNS':
                    word = get_singular_from_plural(word)
                    pos = 'NN'
            output_list.append([word,pos,chunk])
    ## first item in output_list is full list, remaining items are substrings (ending in an original plural)
    return(output_list)

richard_count = 0
supreme_count = 0

def bug_test(string):
    global richard_count
    global supreme_count
    if (string == 'richard') and (richard_count < 10):
        richard_count += 1
        return(True)
    elif (string == 'opinion') and (supreme_count < 10):
        supreme_count += 1
        return(True)
    else:
        return(False)

def add_tuples_to_lemma_dict(string,lemma,new_tuples,old_tuples,lemma_dict,term_file=False):
    # if (len(string)>0) and (string[0]==' ') or (string[-1]==' '):
    #     print('*** border spaces in string:',string)
    # if (len(lemma)>0) and (lemma[0]==' ') or (lemma[-1]==' '):
    #     print('*** border spaces in lemma:',lemma) 
    if re.search(' (of|for) .*(of|for) ',string,re.I):
        use_substrings = False
        use_original_tuples = False
    elif re.search(' (of|for) ',string,re.I):
        use_substrings = True
        use_original_tuples = False
    else:
        use_substrings = True
        use_original_tuples = True
        ## only use substrings if the lemma is not transformed more than once 
        ## one transformation is fine for cases like:
        ## "recognition of spoken language" --> "spoken language recognition"
        ## (substrings: "spoken language" and "language recognition" are OK
        ## For long strings, some substrings may be odd and shouldn't be used, e.g.\
        ## Example: The transformation applies twice on:
        ## "economic beliefs for the judgment of legislative bodies"
        ##   resulting in the lemma:
        ## "legislative body judgment economic belief"
        ##
        ## The undisirable substring "body judgment" may result
        ## without this constraint
    for num in range(len(old_tuples)):
        if old_tuples[num][1]=='FW':
            old_tuples[num][1]=guess_limited_ptb_pos(old_tuples[num][0])
    for num in range(len(new_tuples)):
        if new_tuples[num][1]=='FW':
            new_tuples[num][1]=guess_limited_ptb_pos(new_tuples[num][0])    
    string = string.strip(' ')
    lemma = lemma.strip(' ')
    lemma2 = new_tuples[0][0].strip(' ')
    for word,pos,chunk in new_tuples[1:]:
        if ' ' in word:
            ## print('*** border spaces in word:',word)
            word = word.strip(' ')
        if word != '':
            lemma2 += (' '+word)
    lemma2 = lemma2.lower()
    if lemma in lemma_dict:
        if not string in lemma_dict[lemma]:
            lemma_dict[lemma].append(string)
    elif len(lemma)>1:
        lemma_dict[lemma]=[string]
    if lemma2 != lemma:
        if lemma2 in lemma_dict:
            if not string in lemma_dict[lemma2]:
                lemma_dict[lemma2].append(string)
        elif len(lemma2)>1:
            lemma_dict[lemma2]=[string]
    lemma_sequence = []
    ## also match up subsequences of NNS and premods
    if use_original_tuples:
        for num in range(len(old_tuples)):
            old_triple = old_tuples[num]
            if (old_triple[1] in ['NNS','NNPS']):
                ## The subsequence will be the whole sequence if
                ## num is equal to len of the current lemma_subsequence.
                ## In that case, the dictionary item already must exist
                for position in range(0,1+len(lemma_sequence)):
                    ## use -1 to go from last position to first,
                    ## ensuring that subsquences end in NNS
                    if position==0:
                        string3 = old_triple[0].lower().strip(' ')
                        lemma3 = get_singular_from_plural(string3).lower()
                    else:
                        previous_word = lemma_sequence[-1*position].strip(' ').lower()
                        lemma3 = previous_word + ' ' + lemma3
                        string3 = previous_word + ' ' + string3
                    if lemma3 in lemma_dict:
                        if not string3 in lemma_dict[lemma3]:
                            lemma_dict[lemma3].append(string3)
                    elif len(lemma3)>1:
                        lemma_dict[lemma3] = [string3]
                lemma_sequence = []
                ## re-initialize sequences
            elif old_triple[1] in ['NN','JJ','JJR','JJS','NNP','VBG','VBN']:
                lemma_sequence.append(old_triple[0].lower())
            else:
                lemma_sequence = []
                ## re-initialize sequence
                ## we only care about those ending in NNS
    elif use_substrings:
        for num in range(len(new_tuples)):
            if not new_tuples[num]:
                pass
            elif len(new_tuples[num]) != 3:
                print('new_tuples should have length 3')
                print(new_tuples)
            else:
                word,pos,bio_tag = new_tuples[num]
                if (pos == 'NN') and (word.lower() in plural_dict):
                    lemma3 = plural_dict[word.lower()][0]
                    string3 = word.lower()
                    if num>0:
                        for position in range(num-1):
                            previous_word = new_tuples[position][0].strip(' ').lower() ###
                            lemma3 = previous_word + ' '+lemma3
                            string3 = previous_word+ ' '+string3
                    if lemma3 in lemma_dict:
                        if not string3 in lemma_dict[lemma3]:
                            lemma_dict[lemma3].append(string3)
                    elif len(lemma3)>1:
                        lemma_dict[lemma3]=[string3]

    
def make_term_chunk_file(pos_file,term_file,abbreviate_file,chunk_file,abbr_to_full,no_head_terms_only=False,use_lemmas=True,lemma_dict= False):
    term_hash = {}
    started_term = False
    start_term = False
    end_term = False
    with open(term_file) as instream:
        for line in instream:
            fvs = get_integrated_line_attribute_value_structure_no_list(line,['TERM'])
            if not fvs:
                pass
            elif no_head_terms_only and ('HEAD_TERM' in fvs) and re.search(' (of|for) ', fvs['STRING'].lower()):
                pass
            else:
                START = int(fvs['START'])
                END = int(fvs['END'])
                if START in term_hash:
                    old = term_hash[START]
                    old_end = int(old['END'])
                    if END > old_end:
                        term_hash[START] = fvs
                else:
                    term_hash[START] = fvs
    if abbreviate_file:
        with open(abbreviate_file) as instream:
            for line in instream:
                fvs = get_integrated_line_attribute_value_structure_no_list(line,['JARGON'])
                if ('START' in fvs):
                    START = int(fvs['START'])
                    if not START in term_hash:
                        term_hash[START] = fvs
                        fvs['STRING']=fvs['TEXT']
                        if fvs['STRING'] in abbr_to_full:
                            fvs['LEMMA']=abbr_to_full[fvs['STRING']][0]
                        else:
                            fvs['LEMMA']=fvs['STRING']
                        ## don't overwrite term info
    lemma = False
    with open(pos_file) as instream,open(chunk_file,'w') as outstream:
        term_tuples = []
        current_tuples = []
        for line in instream:
            word,pos,start,end = get_pos_structure(line)
            word = word.strip(' ')
            if not word:
                pass
            elif started_term:
                if start < end_term:
                    current_tuples.append([word,pos,'I-NP'])
                else:
                    if use_lemmas:
                        string = term_hash[start_term]['STRING'].lower()
                        lemma = term_hash[start_term]['LEMMA'].lower()
                        new_tuples = process_lemma_term_tuples(current_tuples,string,lemma)
                        add_tuples_to_lemma_dict(string,lemma,new_tuples,current_tuples,lemma_dict,term_file=term_file)
                        term_tuples.extend(new_tuples)
                    else:
                        term_tuples.extend(current_tuples)
                    if start in term_hash:
                        started_term = True
                        start_term = start
                        end_term = int(term_hash[start]['END'])
                        current_tuples = [[word,pos,'B-NP']]
                    else:
                        term_tuples.append([word,pos,'0'])
                        current_tuples = []
                        started_term = False
                        start_term = False
            elif start in term_hash:
                started_term = True
                start_term=start
                end_term = int(term_hash[start]['END'])
                current_tuples = [[word,pos,'B-NP']]
            else:
                term_tuples.append([word,pos,'0'])
        if started_term:
            if use_lemmas:
                string = term_hash[start_term]['STRING'].lower()
                lemma = term_hash[start_term]['LEMMA'].lower() ## bug fix AM 9/9/17
                new_tuples = process_lemma_term_tuples(current_tuples,string,lemma)
                add_tuples_to_lemma_dict(string,lemma,new_tuples,current_tuples,lemma_dict,term_file=term_file)
                ## first item in new_tuples is the full list
                ## additional items are substrings
                term_tuples.extend(new_tuples)
            else:
                term_tuples.extend(current_tuples)
        for word,pos,CHUNK_TAG  in term_tuples:
            outstream.write(word+'\t'+word+'\t'+pos+'\t'+CHUNK_TAG+'\n')
        

def make_term_chunk_file_list(infiles,outfiles,abbr_to_full,special_ds,lemma_dict_file,no_head_terms_only=False,use_lemmas=True):
    global special_domains
    global lemma_dict
    abbr_to_full_dict = {}
    ## lemma_dict = {}
    if os.path.isfile(lemma_dict_file):
        with open(lemma_dict_file) as instream:
            for line in instream:
                line = line.strip(os.linesep)
                items = line.split('\t')
                lemma_dict[items[0]]=items[1:]
    if len(pos_dict)==0:
        if special_ds:
            special_domains.extend(special_ds.split('+'))
        initialize_utilities()
    with open(abbr_to_full) as instream:
        for line in instream:
            line = line.strip(os.linesep)
            line_list = line.split('\t')
            abbr_to_full_dict[line_list[0]]=line_list[1:]
    with open(infiles) as instream, open(outfiles) as outfile_stream:
        inlist = instream.readlines()
        outlist = outfile_stream.readlines()
        if len(inlist) != len(outlist):
            print("Lists of input and output files should be of same length.")
            sys.exit(-1)
    for num in range(len(inlist)):
        try:
            out_list = inlist[num].strip().split(';')
            if len(out_list) == 3:
                pos_file,term_file,abbreviate_file = out_list
            else:
                pos_file,term_file = out_list
                abbreviate_file = False
            chunk_file = outlist[num].strip()
        except:
            print("Error opening input/output files:")
            print("Input: %s\nOutput: %s" % inlist[i].strip(),outlist[i].strip())
        make_term_chunk_file(pos_file,term_file,abbreviate_file,chunk_file,abbr_to_full=abbr_to_full_dict,no_head_terms_only=no_head_terms_only,use_lemmas=use_lemmas,lemma_dict=lemma_dict)
    if lemma_dict_file and (len(lemma_dict)>0):
        keys = list(lemma_dict.keys())
        keys.sort()
        with open(lemma_dict_file,'w') as outstream:
            for key in keys:
                outstream.write(key)
                for value in lemma_dict[key]:
                    outstream.write('\t'+value)
                outstream.write('\n')


    ## 1/31/2019 -- an approach for getting a precise list of
    ## inline terms to use with the distributional system.
    ## Unlike our previous system, this does not have its
    ## roots in our original Noun Chunk Genia-based system.
    ## We assume the following
    ## *  All instances of JARGON from the .abbr file are candidates,
    ##    but are only added to our list of terms if the same
    ## * Instances of terms of type COMPOUND, chemical, path, gene
    ## * Instances of terms of type chunk-based
    ##   -- record lemma instead of base form
    ## * Selected substrings of multi-word terms of type chunk-based
    ##   but do so on a second pass.
    ##   -- select all substrings such that:
    ##      (a) they end in a noun of some sort ** check
    ##      (b) if 2 nouns are "split", the substring ** not implemented yet **
    ##          must occur elsewhere either as:
    ##          (i) an exact match or
    ##          (ii) a substring match such that
    ##               the adjacent left or right term
    ##               does not match the left or right term
    ##               that is cut. "Match" means "identical if case and
    ##               punctuation is removed.
    ##      (c) contain some technical word (OOV, tech_adj or nom) ** check
    ##      (d) do not split up any latin_pps (these are represented
    ##          as a single TECH-ADJ with spaces in between)
    ##          -- there will be a mismatch in word length and
    ##             length of phrase
    ##          TECH_ADJECTIVE will always precede a noun ** check
    ##      (e) eliminate single words that are note either OOV or nominalizations
    ##          check so-called "PLURAL" to see if they are OOV as well ** check

def make_term_and_substring_list(term_file,abbr_file,outfile,no_head_terms_only=False,\
                                 abbr_to_full=False,special_domain=False,initialized=False,
                                 lemma_dict_file=False
                                 ):
    global special_domains
    global abbr_to_full_dict
    global lemma_dict
    if not initialized:
        ## print('initializing make_term_and_substring_list')
        abbr_to_full_dict = {}
        lemma_dict = {}
        if special_domain:
            special_domains.extend(special_domain.split('+'))
        initialize_utilities()
        if abbr_to_full:
            with open(abbr_to_full) as instream:
                for line in instream:
                    line = line.strip(os.linesep)
                    line_list = line.split('\t')
                    abbr_to_full_dict[line_list[0]]=line_list[1:]
        if lemma_dict_file and os.path.isfile(lemma_dict_file):
            with open(lemma_dict_file) as instream:
                for line in instream:
                    for line in instream:
                        line = line.strip(os.linesep)
                        items = line.split('\t')
                        lemma_dict[items[0]]=items[1:]
    word_term_hash = {} ## not sure we need this
    ## links each word in a term to the set of 
    ## terms that they are a part of
    ## not sure if I need start_term_hash or not
    start_term_hash = {}
    ## links every start position to the set of terms
    ## that start at that position
    term_out = []
    chunks_to_check = []
    with open(term_file) as instream:
        for line in instream:
            fvs = get_integrated_line_attribute_value_structure_no_list(line,['TERM'])
            if 'TERM_PATTERN_TYPE' in fvs:
                type_value = fvs['TERM_PATTERN_TYPE']
            if (not fvs) or \
              ((no_head_terms_only) and ('HEAD_TERM' in fvs) and re.search(' (of|for) ', fvs['STRING'].lower())):
                pass
            else:
                LEMMA = fvs['LEMMA']
                STRING = fvs['STRING']
                term_out.append(LEMMA)
                # if not STRING.upper() in lemma_dict:
                #     lemma_dict[STRING.upper()] = [LEMMA]
                # elif not LEMMA  in lemma_dict[STRING.upper()]:
                #     lemma_dict[STRING.upper()].append(LEMMA)
                # ## proposed fix on 4/29/2019 for consistency -- which direction?
                if not LEMMA.upper() in lemma_dict:
                     lemma_dict[LEMMA.upper()]=[STRING.upper()]
                elif not STRING.upper() in lemma_dict[LEMMA.upper()]:
                    lemma_dict[LEMMA.upper()].append(STRING.upper())
                START = int(fvs['START'])
                END = int(fvs['END'])
                if not START in start_term_hash:
                    start_term_hash[START]=[LEMMA]
                else:
                    if not START in start_term_hash:
                        start_term_hash[START]=[LEMMA]
                    elif not LEMMA in start_term_hash[START]:
                        start_term_hash[START].append(LEMMA)
                if type_value.startswith('chunk-based:'):
                    ## print('abc','*'+type_value+'*','efg')
                    POS_SEQ = eval(type_value[len("chunk-based:"):])
                    chunks_to_check.append([fvs['STRING'],LEMMA,POS_SEQ,START,END])
    substrings = [] 
    for string,LEMMA,POS_SEQ,START,END in chunks_to_check:
        if len(POS_SEQ)> 1:
            words = string.split(' ')
            ## search from right to left
            ## we also need start and end so
            ## we can avoid duplicates of abbreviations
            ## from the abbreviation file
            
            ## triples: [new_string,preceder,follower]
            ## goal -- find other term such that:
            ## new_string is a substring
            ## neither preceder, nor follower is present
            ## example: a) exact match; b) different match
            stop = False
            new_pos_seq = POS_SEQ[:]
            # substrings should include previous word and following word
            # in order to do this check later
            previous_word = False
            next_word = False
            while (not stop) and (len(new_pos_seq) == len(words)):
                ## (a) makes sure subsequence ends in a noun of some sort
                new_pos_seq.pop()
                next_word = words.pop()
                if len(new_pos_seq) == 0:
                    stop = True
                elif new_pos_seq[-1] in \
                     ['PLURAL','AMBIG_PLURAL','NOUN',\
                      'AMBIG_NOUN','NOUN_OOV']:
                    new_string = ' '.join(words)
                    if (new_pos_seq[-1] == 'NOUN_OOV') or is_nom_piece(words[-1]) \
                      or ((len(new_pos_seq)>1) and (new_pos_seq[-2] == 'TECH_ADJECTIVE')):
                      
                        substrings.append([new_string,previous_word,next_word,START,END])
                else:
                    stop = True
            ## For 5 word long sequence
            ## above looks at first 4 words, then first 3, ... first 1
            words = string.split(' ')
            previous_word = False
            next_word = False
            if len(POS_SEQ) == len(words):
                ## don't do this for the latin pp case
                new_pos_seq = POS_SEQ[:]
                for num in range(1,len(words)):
                    previous_word = words[num-1]
                    new_pos_seq = new_pos_seq[num:]
                    new_words = words[num:]
                    if len(new_pos_seq) == 0:
                        break
                    if (new_pos_seq[-1] == 'NOUN_OOV') or is_nom_piece(words[-1]) \
                      or ((len(new_pos_seq)>1) and (new_pos_seq[-2] == 'TECH_ADJECTIVE')):
                      substrings.append([' '.join(new_words),previous_word,next_word,START,END])
            ## For 5 word long sequence
            ## above should look at last 4 words, then last 3, ... last 1
            words = string.split(' ')
            if (len(POS_SEQ) == len(words)) and (len(words)>2):
                new_pos_seq = POS_SEQ[:]
                for num in range(1,len(words)-1):
                    previous_word = words[num-1]
                    next_word = words[num+1]
                    if new_pos_seq[num] == 'NOUN_OOV':
                        substrings.append([words[num],previous_word,next_word,START,END])
            ## This is meant to handle single words not handled by previous 2 loops
    if abbr_file:
        with open(abbr_file) as instream:
            for line in instream:
                fvs = get_integrated_line_attribute_value_structure_no_list(line,['JARGON'])
                if fvs:
                    START = int(fvs['START'])
                    TEXT = fvs['TEXT'].upper()
                    if not START in start_term_hash:
                        start_term_hash[START]=[TEXT]
                        term_out.append(TEXT)
                    elif not TEXT in start_term_hash[START]:
                        start_term_hash[START].append(TEXT)
                        term_out.append(TEXT)
    term_set = set(term_out)
    for substring,left,right,START,END in substrings:
        ## We are qualifying instances here
        ## 1) we must make sure that instance, as is, does
        ##    not exactly match an abbreviation (these are already accounted for)
        ## 2) If left is not False,
        ## we must make sure that the term, at least one time,
        ## is not immediately preceded by left
        ## 3) Similarly if right is not false, we make sure that
        ## at least once, it is not followed by right.
        Fail = False
        if START in start_term_hash:
            partial_match = False
            ## regexp_match = False
            substring_index = False
            for match in start_term_hash[START]:
                ## possibly use .find instead of regexp to avoid special character issues
                ## ** 57 **
                substring_index = match.find(substring)
                ## regexp_match = re.search(substring,match)
                # if (not partial_match) and regexp_match:
                #     partial_match = match
                #     break
                if (not partial_match) and (substring_index != -1):
                    partial_match = match
                    break
            if (substring_index != -1):
                new_start = START+substring_index
                if new_start in start_term_hash:
                    for possible_match in start_term_hash[new_start]:
                        Fail = True
                        break
            # if regexp_match:
            #     new_start = START+regexp_match.start()
            #     if new_start in start_term_hash:
            #         for possible_match in start_term_hash[new_start]:
            #             Fail = True
            #             break
        if Fail:
            ## if the substring is already mentioned as an abbreviation
            pass
        elif (substring.upper() in term_set):
                ## if the same string already passed
                ## we do not need to check again
            term_out.append(substring.upper())
        elif substring in lemma_dict:
            term_out.append(lemma_dict[substring][0])
            ## pick first lemma
        else:
            substring = substring.upper()
            if left:
                left = left.upper()
            if right:
                right = right.upper()
            for term_to_match in term_set:
                ## part_match = re.search(substring,term_to_match)
                part_start = term_to_match.find(substring)
                ## possibilities: 
                ## a) no evidence (pass); 
                ## b) correct (add to terms and break)
                if part_start == -1:
                    pass
                else:
                    if left:
                        left_match = re.search(change_parens_to_dots(left+' +'+substring),term_to_match)
                    else:
                        left_match = False
                    if right:
                        right_match = re.search(change_parens_to_dots(substring+' '+right),term_to_match)
                    else:
                        right_match = False
                    if (not (left or right)):
                       term_set.add(substring)
                       term_out.append(substring)
                       ## we found the term
                       break
                    elif (left and left_match) or (right and right_match):
                       ## if left or right are the same
                       ## in the sample, then the substring
                       ## may require this left or right
                       ## so this one should not be recorded
                       ## unless there are other instances
                       ## where left or right are not there
                        pass
                    else:
                        term_set.add(substring)
                        term_out.append(substring)
                        break
    with open(outfile,'w') as outstream:
        ## term_out.sort()
        for term in term_out:
            if not(type(term))==str:
                print(term,type(term))
                input('pause')
            outstream.write(term+'\n')
    ## print('lemma_dict length',len(lemma_dict))
    
            
                

def make_top_terms_with_lemma_output_file(scored_output_file,lemma_dictionary_file,cutoff,output_file, abbr_to_full_file = False, full_to_abbr_file = False):
    lemma_dictionary = {}
    ## total_lines = 0
    with open(lemma_dictionary_file) as instream:
        for line in instream:
            ## total_lines += 1
            line = line.strip(os.linesep).lower()
            line_list = line.split('\t')
            lemma =line_list[0]
            items=line_list[1:]
            lemma_dictionary[lemma] = items
    abbr_to_full = {}
    if abbr_to_full_file:
        with open(abbr_to_full_file) as instream:
            for line in instream:
                line = line.strip(os.linesep).lower()
                line_list = line.split('\t')
                abbr_to_full[line_list[0]]= line_list[1:]
    full_to_abbr = {}
    if full_to_abbr_file:
        with open(full_to_abbr_file) as instream:
            for line in instream:
                line = line.strip(os.linesep).lower()
                line_list = line.split('\t')
                full_to_abbr[line_list[0]]= line_list[1:]
    with open(scored_output_file) as instream,open(output_file,'w') as outstream:
            ## cutoff = min(cutoff,total_lines)
        line = 'start'
        total = 0
        while (total < cutoff) and line:
            total = total + 1
            line = instream.readline()
            if line:
                lemma,tab,rest = line.partition('\t')
                lemma = lemma.lower()
                # FILTER legislation name
                # if filter_name(lemma):
                #     print("FILTER OUT:", lemma)
                #     total -= 1
                #     continue

                # FILTER hyphenated word & word with digits
                # if filter_hyphenated_term(lemma) or filter_term_with_digits(lemma):
                #     print("FILTER OUT:", lemma)
                #     total -= 1
                #     continue

                # FILTER word with digits and LOWER weight for hyphenated terms to from 0.5 to 0.1
                # if filter_term_with_digits(lemma):
                #     print("FILTER OUT:", lemma)
                #     total -= 1
                #     continue

                # FILTER legislation names, word with digits, hyphenated word
                if filter_name(lemma) or filter_hyphenated_term(lemma) or filter_term_with_digits(lemma) or filter_name_by_websearch(lemma):
                    print("FILTER OUT:", lemma)
                    total -= 1
                    continue

                outstream.write(lemma)
                additional_forms = []
                if lemma in lemma_dictionary:
                    for form in lemma_dictionary[lemma]:
                        if form != lemma:
                            additional_forms.append(form)
                more_forms = []
                for form in additional_forms:
                    if form in abbr_to_full:
                        for form2 in abbr_to_full[form]:
                            if (not form2 == lemma) and (not form2 in additional_forms) and (not form2 in more_forms):
                                more_forms.append(form2)
                    elif form in full_to_abbr:
                        for form2 in full_to_abbr[form]:
                            if (not form2 == lemma) and (not form2 in additional_forms) and (not form2 in more_forms):
                                more_forms.append(form2)
                additional_forms.extend(more_forms)
                for form in additional_forms:
                    outstream.write('\t'+form)
                outstream.write('\n')
    
def record_lemma_dict(lemma_dict_file):
    global lemma_dict
    global abbr_to_full_dict
    filter_lemma_dictionary_for_abbreviation_conflicts(lemma_dict,abbr_to_full_dict)
    ## print(1,(len(lemma_dict)),2,(len(abbr_to_full_dict)),3,len(full_to_abbr_dict))
    ## input('pause')    
    ## print('final_lemma_dict_length',len(lemma_dict))
    if len(lemma_dict) == 0:
        return(False)
    keys = list(lemma_dict.keys())
    keys.sort()
    with open(lemma_dict_file,'w') as outstream:
        for key in keys:
            outstream.write(key)
            for value in lemma_dict[key]:
                outstream.write('\t'+value)
            outstream.write('\n')