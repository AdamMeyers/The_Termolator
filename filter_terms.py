from find_terms import *
from webscore import *


def large_prefix_overlap(term1,term2):
    small_length = min(len(term1),len(term2))
    sub_string_length = small_length//2
    answer = term1[:sub_string_length]==term2[:sub_string_length]
    return(answer)

def s_filter_check(word1,word2):
    if word1.endswith('s'):
        word1_s=True
        if word1.endswith('es'):
            word1_es=True
        else:
            word1_es=False
    else:
        word1_s=False
    if word2.endswith('s'):
        word2_s=True
        if word2.endswith('es'):
            word2_es=True
        else:
            word2_es=False
    else:
        word2_s=False
    if word1_s:
        if word2_s:
            if word1_es or word2_es:
                return(True)
        else:
            return(True)
    elif word2_s:
        return(True)

def collapse_lines(lines,alternate_lists):
    output = []
    last_line_list = False
    current_collection = []
    for line in lines:
        line_list = line.split('\t')
        if last_line_list and (last_line_list[-1]==line_list[-1]) \
          and large_prefix_overlap(last_line_list[0],line_list[0]) \
          and (s_filter_check(last_line_list[0],line_list[0])):
            if len(line_list[0])<len(last_line_list[0]):
                if not last_line_list[0] in current_collection:
                    current_collection.append(last_line_list[0])
                last_line_list = line_list
            elif not last_line_list[0] in current_collection:
                current_collection.append(last_line_list[0])
        else:
            if last_line_list:
                if not last_line_list[0] in current_collection:
                    current_collection.append(last_line_list[0])
                alternate_lists[last_line_list[0]]=current_collection
                output.append(last_line_list)
            last_line_list = line_list
            current_collection=[]
    if last_line_list:
        if not last_line_list[0] in current_collection:
            current_collection.append(last_line_list[0])
        alternate_lists[last_line_list[0]]=current_collection
        output.append(last_line_list)
    return(output)

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
    elif word in jargon_words:
        return('Medium')
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
    elif pos in ['TECH_ADJECTIVE','NATIONALITY_ADJ','ADVERB']:
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

def normal_word(word):
    if (word in pos_dict) and (not word in jargon_words):
        pos = pos_dict[word][:]
        if 'PERLOC_NAME' in pos:
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
        if first and (word.lower() in ABBREVIATION_STOP_WORDS):
            pass
        else:
            upper = word.upper()
            word_map = get_noun_nom_map(word)
            if (not normal_word(word)) or word.isupper():
                fulls = get_expanded_forms_from_abbreviations(upper)
            else:
                fulls = False
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
    np_lemma,nom = get_np_lemma(np_base)
    ## use rule above -- don't currently
    ## deal with 2NPs + VP case (which is possible)
    out = np_lemma[:]
    found_nom = False
    vp_pos_seq_mod = []
    last_pos = False
    vp_rating = 'Not Sure'
        ## this only keeps the last verb
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

def stringify_word_list(word_list):
    output = word_list[0]
    if len(word_list)>1:
        for word in word_list[1:]:
            output=output+' '+word
    return(output)

def term_classify(line,mitre=False):
    ## based on get_topic_terms, but based on smaller n-grams, typically with no punctuation
    ## return (lemma, classification, rating, other_terms)
    weird_char = re.compile('[^ 0-9A-Za-z\-\'\.]')
    word_pattern = re.compile('[^\w]+')
    weird_spacing = re.compile('([^a-zA-Z0-9] )|( [^a-zA-Z0-9])|(-$)')
    pre_np = False
    main_base = False
    verb_base = False
    chunks = False
    ## ratings: good, medium, bad
    if weird_char.search(line) or weird_spacing.search(line):
        return(line,'bad_character','Bad',False,chunks,.1)
    if mitre:
        words = word_pattern.split(line)
    else:
        words = word_split(line)
    if len(words) == 1:
        pos = guess_pos(words[0].lower(),False,case_neutral=True)
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
                    return(full,'ABBREVIATION','Good',output,chunks,1)
            elif base2:
                rating = topic_term_rating(words[0],pos)
                if rating == 'Good':
                    wf_score = 1
                elif rating == 'Medium':
                    wf_score = .7
                elif rating == 'Bad':
                    wf_score = .3
                return(base2.upper(),'HYPHENATION',rating,output,chunks,wf_score)
            else:
                rating = topic_term_rating(words[0],pos)
                if rating == 'Good':
                    wf_score = 1
                elif rating == 'Medium':
                    wf_score = .7
                elif rating == 'Bad':
                    wf_score = .3
                return(words[0].upper(),'SIMPLE',rating,output,chunks,wf_score)
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
                    return(abbrev,'ABBREVIATION','Good',output,chunks,1)
            elif base2s:
                rating = topic_term_rating(words[0],pos)
                if rating == 'Good':
                    wf_score = 1
                elif rating == 'Medium':
                    wf_score = .7
                elif rating == 'Bad':
                    wf_score = .3
                return(base2s[0].upper(),'HYPHENATION',rating,output,chunks,wf_score)
            elif bases:
                rating = topic_term_rating(words[0],pos)
                if rating == 'Good':
                    wf_score = 1
                elif rating == 'Medium':
                    wf_score = .7
                elif rating == 'Bad':
                    wf_score = .3
                return(bases[0].upper(),'SIMPLE',rating,output,chunks,wf_score)
            else:
                rating = topic_term_rating(words[0],pos)
                if rating == 'Good':
                    wf_score = 1
                elif rating == 'Medium':
                    wf_score = .7
                elif rating == 'Bad':
                    wf_score = .3
                return(line.upper(),'SIMPLE',rating,output,chunks,wf_score)
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
            if rating == 'Good':
                wf_score = 1
            elif rating == 'Medium':
                wf_score = .4
            elif rating == 'Bad':
                wf_score = .2
            return(line.upper(),classification,rating,False,chunks,wf_score)
    else:
        conjunction_position = False ## there is never more than one in the current Mitre list
        position = 0
        current_chunk = False
        chunks = []
        unnecessary_pieces = 0
        prep_count = 0
        ## allow at most 1 verb chunk
        length = len(words)
        if line.upper() in full_to_abbr_dict:
            return(line.upper(),'ABBREVIATION','Good',[line],chunks,1)
        elif (len(line)>2) and (line[-1] in ['s','S']) and (line[:-1].upper() in full_to_abbr_dict):
            return(line[:-1].upper(),'ABBREVIATION','Good',[line],chunks,1)
        elif (len(line)>3) and (line[-1] in ['es','ES']) and (line[:-2].upper() in full_to_abbr_dict):
            return(line[:-2].upper(),'ABBREVIATION','Good',[line],chunks,1)
        for word in words:
            ## print(word)
            position = position+1
            if word in ['and','or']:
                pos = 'CCONJ'
            else:
                pos = guess_pos(word,False,case_neutral=False) ## the Mitre output is monocase (all lowercase)
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
            elif pos in ['SKIPABLE_ADJ','ADJECTIVE','TECH_ADJECTIVE','NATIONALITY_ADJ']:
                if (not (pos in ['TECH_ADJECTIVE','NATIONALITY_ADJ'])) and (not term_dict_check(word,stat_adj_dict)):
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
            return(line.upper(),'contains_conjunction','Bad',[line],chunks,.1)
        elif len(chunks)>3:
            ## verify this case, there may be some cases that are OK
            return(line.upper(),'too_many_chunks','Bad',[line],chunks,.3)
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
                    OK_term,has_OOV  =  topic_term_ok(word_seq,pos_seq,term_string)
                    if OK_term:
                        ok_np = 1+ ok_np
                        if has_OOV:
                            rating = 'Good'
                        else:
                            rating = 'Medium'
                        if np_1:
                            np_2 = [word_seq, rating]
                            np_2_bases,np_2_variants,main_base = get_morph_variants(word_seq,pos_seq,'NP')
                        else:
                            np_1 = [word_seq, rating]
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
                        return(line.upper(),'too_many_verbs','Bad',[line],chunks,.1)
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
                return(line.upper(),'sequence_with_XP_chunk','Bad',[line],chunks,.3)
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
                if rating == 'Good':
                    wf_score = 1
                elif rating == 'Medium':
                    wf_score = .5
                elif rating == 'Bad':
                    wf_score = .2
                return(lemma,'Normal_NP',rating,np_1_variants,chunks,wf_score)
            elif np_1 and np_2 and (prep_position == 1):
                if unnecessary_pieces >=2:
                    rating = 'Bad'
                elif (np_1[1] == 'OK') and (np_2[1] == 'OK'):
                    if unnecessary_pieces >0:
                        rating = 'Medium'
                    else:
                        rating = 'Good'
                elif (np_1[1] in ['OK','Medium']) or (np_2[1] in ['OK','Medium']):
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
                ## print('term_classify',type(np_1[0]))
                lemma,nom = get_np_lemma(np_1_bases[0],prep=chunks[1][1],np2=np_2_bases[0])
                if rating == 'Good':
                    wf_score = 1
                elif rating == 'Medium':
                    wf_score = .5
                elif rating == 'Bad':
                    wf_score = .2
                return(lemma,'2_Part_NP',rating,full_variants,chunks,wf_score)
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
                if rating == 'Good':
                    wf_score = .5
                elif rating == 'Medium':
                    wf_score = .3
                elif rating == 'Bad':
                    wf_score = .2
                if vp_2 and vp_ing:
                    return(lemma,'NP+VP_ing',rating,full_variants,chunks,wf_score-.1)
                elif vp_ing:
                    return(lemma,'VP_ing+NP',rating,full_variants,chunks,wf_score)
                else:
                    return(lemma,'verb+NP',rating,full_variants,chunks,wf_score)
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
                elif (np_1[1] in ['OK','Medium']) or (np_2[1] == ['OK','Medium']):
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
                if rating == 'Good':
                    wf_score = .8
                elif rating == 'Medium':
                    wf_score = .5
                elif rating == 'Bad':
                    wf_score = .2
                return(lemma,'2_Part_NP_no_prep',rating,full_variants,chunks,wf_score)
            else:
                return(line.upper(),'unexpected_POS_sequence','Bad',[line],chunks,.1)
            ## rating based on OOV and nominalizations
            ## have not really attempted to identify "uninteresting" nouns and verbs
            ## e.g., support verbs, transparent nouns, boring nouns ('device', etc.)

def ok_statistical_term(term,lenient=False,penalize_initial_the=False):
    ## if single word, it should be a possible noun
    ##
    initial_the_pattern = re.compile('^the ',re.I)
    rating = False
    well_formedness = 0
    if len(term)==1:
        return(False,'1-character-term',False,rating,well_formedness)
    lemma,classification,rating,other_terms,chunks,well_formedness = term_classify(term)
    if penalize_initial_the and initial_the_pattern.search(term):
        well_formedness = 0
        ## for NYU internal purposes only, downgrade all terms beginning with "the"
    if (classification == 'Normal_NP') and (rating == 'Bad'):
        if well_formedness>=.1:
            well_formedness = well_formedness - .1
        return(False,classification,chunks,rating,well_formedness)
    elif classification in ['Normal_NP','ABBREVIATION','NP+VP_ing','VP_ing+NP','2_Part_NP_no_prep']:
        if rating == 'Medium':
            well_formedness = well_formedness+.1
        elif rating == 'Bad':
            well_formedness = well_formedness+.25            
        return(True,classification,chunks,rating,well_formedness)
    elif classification in ['SIMPLE','HYPHENATION']:
        POS = guess_pos(term.lower(),term.istitle(),case_neutral=True)
        if lenient and classification == 'SIMPLE':
            if rating != 'Good':
                rating = rating+'_but_top_term'
                well_formedness = (well_formedness+1)/2
            return(True,classification,chunks,rating,well_formedness)
        elif rating !='Good':
            ## well_formedness = well_formedness *1.5
            return(False,classification,chunks,rating,well_formedness)
        elif POS in ['NOUN','AMBIG_NOUN','PLURAL','AMBIG_PLURAL','NOUN_OOV']:
            if rating == 'Medium':
                well_formedness = well_formedness+.1
            elif rating == 'Bad':
                well_formedness = well_formedness+.25
            return(True,classification,chunks,rating,well_formedness)
        elif classification == 'HYPHENATION':
            well_formedness = well_formedness * .5
            return(False,classification,chunks,rating,well_formedness)
        else:
            well_formedness = well_formedness * .5
            return(False,POS,chunks,rating,well_formedness)
    elif (classification == 'In_or_Out_of_Dictionary'): 
        POS = guess_pos(term.lower(),term.istitle(),case_neutral=True)
    well_formedness = well_formedness * .5
    return(False,classification,chunks,rating,well_formedness)

def filter_terms (infile, \
                  outfile,\
                  abbr_full_file,\
                  full_abbr_file, \
                  abbr_files = False, \
                  use_web_score = True, \
                  ranking_pref_cutoff = .001, \
                  percent_cutoff=.3, \
                  numeric_cutoff=30000,\
                  reject_file = False, \
                  penalize_initial_the = True, \
                  web_score_dict_file=False,
                  web_score_max = 1000
                  ):
    ## it is possible that some people may want to allow NPs as well as noun groups as terms
    webscore_count = 0
    if abbr_full_file and full_abbr_file:
        if os.path.isfile(abbr_full_file) and os.path.isfile(full_abbr_file):
            read_in_abbrev_dicts_from_files(abbr_full_file,full_abbr_file)
        elif abbr_files:
            make_abbr_dicts_from_abbr(abbr_files,full_abbr_file,abbr_full_file)
            ## this creates abbr dicts and loads them
    if use_web_score and web_score_dict_file:
        load_web_score_dict_file(web_score_dict_file)
        use_web_score_dict = True
    else:
        use_web_score_dict = False
    stat_scores = []
    alternate_lists = {}
    if reject_file:
        reject_stream = open(reject_file,'w')
    else:
        reject_stream = False
    ## make_stat_term_dictionary4
    instream = open(infile,errors='replace')
    lines = instream.readlines()
    instream.close()
    line_lists = collapse_lines(lines,alternate_lists)
    for line in line_lists:
        if (len(stat_scores)> 0) and (line[-1] == stat_scores[-1]):
            pass
        else:
            stat_scores.append(line[-1])
    stat_rank_scores = {}
    num = 0
    num_of_scores = len(stat_scores)
    for score in stat_scores:
        percentile = (num_of_scores-num)/num_of_scores
        percentile_score = round((percentile**2),4)
        if score in stat_rank_scores:
            pass
        else:
            num = num+1
            stat_rank_scores[score]=percentile_score
    lenient_simple_threshold = round(ranking_pref_cutoff*len(line_lists))
    length_of_terms = min(round(percent_cutoff*len(line_lists)),numeric_cutoff)
    num = 0
    output = []
    final_output = []
    for line_list in line_lists:
        num = num+1
        for term in line_list[:-1]:              
            keep,classification,chunks,rating,well_formedness_score = ok_statistical_term(term,lenient=(num < lenient_simple_threshold),penalize_initial_the=penalize_initial_the)
            rank_score = stat_rank_scores[line_list[-1]]
            confidence = rank_score * well_formedness_score
            output.append([confidence,term,keep,classification,rating,well_formedness_score,rank_score])
            ## output.sort(key=lambda sublist: sublist[::-1]) ## sort based on last score first, thus giving web search more effect
            output.sort()
    output.reverse()
    confidence_position = min(round(len(output)*percent_cutoff),numeric_cutoff)
    if len(output)>0:
        confidence_cutoff = output[confidence_position][0]
    else:
        confidence_cutoff = 0
    no_more_good_ones = False
    for out in output:
        confidence,term,keep,classification,rating,well_formedness_score,rank_score = out
        num = False
        if confidence<confidence_cutoff:
            no_more_good_ones = True
            message = 'BEYOND_CUTOFF'
            if not keep:
                message = 'BEYOND CUTOFF and FILTERED OUT'
        elif not keep:
            message = 'FILTERED OUT'
        else:
            message = 'SIGNIFICANT_TERM'
        if no_more_good_ones or (not keep):
            if reject_stream:
                stream = reject_stream
            else:
                stream = False
        else:
            ## print('webscore status:',term,webscore_count,web_score_max)
            ## after 1000 instances assign minimum webscore of .1
            ## fixing mismatch (2/12/20) -- max of 1000 websearches
            ## minimum webscore of .1
            if use_web_score and (webscore_count<web_score_max):
                webscore,increment = webscore_one_term(term,use_web_score_dict=use_web_score_dict) ### fix this
                webscore_count += increment
                webscore = max(webscore,.1) ## actual observed should not go below minimum webscore
                combined_score = webscore*confidence
                out.extend([webscore,combined_score])
                final_output.append([combined_score,out])
            elif use_web_score:
                webscore = .1
                combined_score = webscore*confidence
                out.extend([webscore,combined_score])
                final_output.append([combined_score,out])
            else:
                webscore = False
                # out.extend([False,out[-1]]) 
                ## out.extend([False,0]) ## fixing mismatch (2/12/20)
                final_output.append([confidence,out])
            stream = False
        if stream:
            rating = str(rating)
            well_formedness_score = str(well_formedness_score)
            rank_score = str(rank_score)
            confidence = str(confidence)
            stream.write(term+'\t'+message+'\t'+classification+'\t'+rating+'\t'+well_formedness_score+'\t'+rank_score+'\t'+confidence+os.linesep)
    final_output.sort()
    final_output.reverse()
    stream = open(outfile,'w')
    for out in final_output:
        if use_web_score:
            confidence,term,keep,classification,rating,well_formedness_score,rank_score,webscore,combined_score = out[1]
        else:
            confidence,term,keep,classification,rating,well_formedness_score,rank_score  = out[1]
            web_score = False
            combined_score = False
        confidence = str(confidence)
        rating = str(rating)
        well_formedness_score = str(well_formedness_score)
        rank_score = str(rank_score)
        if use_web_score:
            webscore = str(webscore)
            combined_score = str(combined_score)
            stream.write(term+'\t'+classification+'\t'+rating+'\t'+well_formedness_score+'\t'+rank_score+'\t'+confidence+'\t'+webscore+'\t'+combined_score+os.linesep)
        else:
            stream.write(term+'\t'+classification+'\t'+rating+'\t'+well_formedness_score+'\t'+rank_score+'\t'+confidence+os.linesep)
    if use_web_score and web_score_dict_file:
        write_webscore_dictionary(web_score_dict_file)
     
    
