from term_utilities import *
import re

def different_characters(string1,string2):
    if len(string1) > len(string2):
        pivot = string2
    else:
        pivot = string1
    for char in pivot:
        if (char in string1) and (char in string2):
            string1 = string1.replace(char,'',1)
            string2 = string2.replace(char,'',1)
    return(len(string1+string2))

def minor_one_word_difference(words1,words2):
    # print(words1)
    # print(words2)
    # input('break')
    words1_only = []
    words2_only = []
    ## this should not be used for 2 word acronyms
    if (min (len(words1),len(words2)))<3:
        return(False)
    for word in words1:
        if word in words2:
            pass
        else:
            words1_only.append(word)
    for word in words2:
        if word in words1:
            pass
        else:
            words2_only.append(word)
    if (len(words1_only) == 1) and (len(words2_only) == 1):
        diff = different_characters(words1_only[0],words2_only[0])
        maximum = max(len(words1_only[0]),len(words2_only[0]))
        if (diff <= 1):
            return(True)
        if (diff > 3):
            return(False)
        if (maximum > 5):
            return(True)

def substantial_word_overlap(form1,form2):
    length1 = len(form1)
    length2 = len(form2)
    diff = abs(length1-length2)
    diff = different_characters(form1,form2)
    maximum = max(length1,length2)
    if diff <= 1:
        return(True)
    elif (diff >3) or (maximum < 10):
        return(False)
    elif (diff <=3) and (maximum/diff >=8):
        return(True)
    else:
        return(False)

def extra_internal_word(wordlist1,wordlist2):
    length1 = len(wordlist1)
    length2 = len(wordlist2)
    if (length1 >=3) and (length2 >= 3):
        if  (length1-length2) == 1:
            for word in wordlist2:
                if not word in wordlist1:
                    return(False)
            return(True)
        elif (length2-length1) == 1:
            for word in wordlist1:
                if not word in wordlist2:
                    return(False)
            return(True)
    return(False)

def partially_abbreviated_overlap(wordlist1,wordlist2):
    if (len(wordlist1) < 3) and  (len(wordlist2) < 3):
        return(False)
    wordlist1_only = []
    wordlist2_only = []
    for word in wordlist1:
        if word in wordlist2:
            pass
        else:
            wordlist1_only.append(word)
    for word in wordlist2:
        if word in wordlist1:
            pass
        else:
            wordlist2_only.append(word)
    if wordlist1_only and wordlist2_only:
        if (len(wordlist1_only) == 1) and (len(wordlist2_only) == len(wordlist1_only[0])):
            match = True
            for index in range(len(wordlist1_only[0])):
                if wordlist1_only[0][index] == wordlist2[index][0]:
                    pass
                else:
                    match = False
            return(match)
        if (len(wordlist2_only) == 1) and (len(wordlist1_only) == len(wordlist2_only[0])):
            match = True
            for index in range(len(wordlist2_only[0])):
                if wordlist2_only[0][index] == wordlist1[index][0]:
                    pass
                else:
                    match = False
            return(match)
    else:
        return(False)
                

def incompatible_full_form(wordlist1,wordlist2):
    ## if strings overlap, they are compatible
    form1 = ''.join(wordlist1)
    form2 = ''.join(wordlist2)
    if form1 in form2:
        return(False)
    elif form2 in form1:
        return(False)
    elif substantial_word_overlap(form1,form2):
        return(False)
    elif partially_abbreviated_overlap(wordlist1,wordlist2):
        return(False)
    elif minor_one_word_difference(wordlist1,wordlist2):
        return(False)
    elif extra_internal_word(wordlist1,wordlist2):
        return(False)
    else:
        return(True)

def overlap_normalization (wordstring):
    # item = item.lower()
    words = []
    words1 = re.split('[^a-z]',wordstring.lower())
    for word in words1:
        if re.search('[a-z]',word):
            words.append(word)
    reg_words = []
    number_words = ['one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety','hundred','thousand','million','billion','trillion']
    greek = ['alpha','beta','gamma','delta','epsilon','zeta','eta','theta','iota','kappa','lambda',
'mu','nu','xi','omicron','pi','rho','sigma','tau','upsilon','phi','chi','psi','omega']
    for word in words:
        if (word in closed_class_stop_words) or (word in number_words) or (word in greek):
            pass
        else:
            reg_words.append(word)
    return(reg_words)
    
def incompatible_full_forms2(word_lists):
    ## recursive definition
    if len(word_lists)==1:
        return(False)
    for other in word_lists[1:]:
        if incompatible_full_form(word_lists[0],other):
            return(True)
        else:
            return(incompatible_full_forms2(word_lists[1:]))

def incompatible_full_forms(forms):
    if len(forms)==1:
        return(False)
    else:
        reg_words = []
        for form in forms:
            reg_words.append(overlap_normalization(form))
        return(incompatible_full_forms2(reg_words))
        
def filter_abbr_to_full(abbr_to_full_dict):
    out = []
    for abbreviation in abbr_to_full_dict.keys():
        full_forms = abbr_to_full_dict[abbreviation][:]
        if (len(abbreviation) > 4) or ((len(abbreviation) == 4) and (not abbreviation[-1]  in 'sS')):
            ## 4 character long abbreviations are safe, unless they end in 's'
            ## 5 character long abbreviations are safe more generally
            pass
        elif incompatible_full_forms(full_forms):
            out.append(abbreviation)
            ## avoid changing the dictionary while looping through its keys
    for abbreviation in out:
        abbr_to_full_dict.pop(abbreviation)

def filter_both_abbr_dicts(abbr_to_full_dictq,full_to_abbr_dict):
    out = []
    for abbreviation in abbr_to_full_dict.keys():
        full_forms = abbr_to_full_dict[abbreviation][:]
        if (len(abbreviation) > 4) or ((len(abbreviation) == 4) and (not abbreviation[-1]  in 'sS')):
            ## 4 character long abbreviations are safe, unless they end in 's'
            ## 5 character long abbreviations are safe more generally
            pass
        elif incompatible_full_forms(full_forms):
            out.append(abbreviation)
            ## avoid changing the dictionary while looping through its keys
    out2 = []
    for abbreviation in out:
        full_forms = abbr_to_full_dict[abbreviation]
        abbr_to_full_dict.pop(abbreviation)
        for full in full_forms:
            if (full in full_to_abbr_dict):
                full_entry = full_to_abbr_dict[full]
                new_entry = []
                for item in full_entry:
                    if item!=abbreviation:
                        new_entry.append(item)
                if len(new_entry) > 0:
                    full_to_abbr_dict[full]=new_entry
                else:
                    out2.append(full)
    for full in out2:
        if full in full_to_abbr_dict:
            full_to_abbr_dict.pop(full)

def filter_lemma_dictionary_for_abbreviation_conflicts(lemma_dict,abbr_to_full_dict):
    out = []
    for abbreviation in abbr_to_full_dict.keys():
        full_forms = abbr_to_full_dict[abbreviation][:]
        if (len(abbreviation) > 4) or ((len(abbreviation) == 4) and (not abbreviation[-1]  in 'sS')):
            ## 4 character long abbreviations are safe, unless they end in 's'
            ## 5 character long abbreviations are safe more generally
            pass
        elif incompatible_full_forms(full_forms):
            out.append(abbreviation)
            ## avoid changing the dictionary while looping through its keys
    out2 = []
    for abbreviation in out:
        full_forms = abbr_to_full_dict[abbreviation]
        abbr_to_full_dict.pop(abbreviation)
        for full in full_forms:
            if (full in lemma_dict):
                full_entry = lemma_dict[full]
                new_entry = []
                for item in full_entry:
                    if item!=abbreviation:
                        new_entry.append(item)
                if len(new_entry) == 0:
                    new_entry.append(full)
                lemma_dict[full]=new_entry

def correct_abbreviation_dict(indict,outdict,outdict2=False):
    ## indict is an abbreviation to full form dictionary
    if outdict2:
        outstream2 = open(outdict2,'w')
        error_dict = {}
    with open(indict) as instream,open(outdict,'w') as outstream:
        for line in instream:
            items = line.strip(os.linesep).lower().split('\t')
            abbreviation = items[0]
            full_forms = items[1:]
            if (len(abbreviation) > 4) or ((len(abbreviation) == 4) and (not abbreviation[-1]  in 'sS')):
                ## abbreviations that are 4 or more characters seem to be reslient, unless the last
                ## letter is 's'.  Abbreviations of 5 or more charactes ending in s are also OK.
                outstream.write(line)
            elif incompatible_full_forms(full_forms):
                if outdict2:
                    length = len(abbreviation)
                    if abbreviation[-1] in 'sS':
                        length = length-1
                    if length in error_dict:
                        error_dict[length].append(line)
                    else:
                        error_dict[length]=[line]
            else:
                outstream.write(line)
        if outdict2:
            keys = list(error_dict.keys())
            keys.sort()
            for key in keys:
                outstream2.write('*****'+'Ambiguous Abbreviations of Length '+str(key)+'(ignoring final s) *****\n\n')
                entries = error_dict[key]
                entries.sort()
                for entry in entries:
                    outstream2.write(entry)
            outstream2.close()

def test1():
    infile ='/home/meyers/str/debugging_2020/mechanisms15.dict_abbr_to_full'
    outfile = '/home/meyers/str/debugging_2020/mechanisms15.dict_abbr_to_full2'
    errorfile = '/home/meyers/str/debugging_2020/mechanisms15.ambig'
    correct_abbreviation_dict(infile,outfile,outdict2=errorfile)

def test2():
    infile ='/home/meyers/str/debugging_2020/test.dict'
    outfile = '/home/meyers/str/debugging_2020/test2.dict'
    errorfile = '/home/meyers/str/debugging_2020/test3.dict'
    correct_abbreviation_dict(infile,outfile,outdict2=errorfile)
