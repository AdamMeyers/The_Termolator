import os
import re

attribute_value_from_fact = re.compile(r'([A-Z0-9_]+) *[=] *((["]+[^"]*["])|([0-9]+))',re.I)

## from term_utilities in Termolator

def read_in_term_line(line):
    out_dict = {}
    for att_value_pattern in attribute_value_from_fact.finditer(line):
        kv = att_value_pattern.group(0)
        equal_position = kv.index('=')
        key = kv[:equal_position]
        value = kv[equal_position+1:]
        ## key,value = att_value_pattern.group(0).split('=')
        if re.search('^".*"$',value):
            value = value.strip('"')
        elif re.search('^[0-9]+$',value):
            value = int(value)
        out_dict[key] = value
    return(out_dict)

def short_file(file_string,input_path_prefix=False):
    if input_path_prefix:
        if not input_path_prefix.endswith(os.sep):
            input_path_prefix += os.sep
        first_slash_pattern = re.compile(input_path_prefix)
        last_slash_pattern = False
    else:
        last_slash_pattern = re.compile(os.sep+'[^'+os.sep+']*$')
        first_slash_pattern = False
    last_dot_pattern = re.compile('\.[^\.]*$')
    if last_slash_pattern:
       last_slash_match = last_slash_pattern.search(file_string)
       first_slash_match = False
    elif first_slash_pattern:
        first_slash_match = first_slash_pattern.search(file_string)
        last_slash_match = False
    last_dot_match = last_dot_pattern.search(file_string)
    if first_slash_match and last_dot_match:
        return(file_string[first_slash_match.end():last_dot_match.start()])
    elif first_slash_match:
        return(file_string[first_slash_match.end():])
    elif last_slash_match and last_dot_match and (last_slash_match.start()<last_dot_match.start()):
        return(file_string[last_slash_match.start()+1:last_dot_match.start()])
    elif last_slash_match:
        return(file_string[last_slash_match.start()+1:])
    elif (not last_slash_match) and last_dot_match:
        ## last_slash_match is only used if it precedes last_dot_match
        return(file_string[:last_dot_match.start()])
    else:
        return(file_string)

def combine_path_and_file(path,file):
    if path.endswith(os.sep):
        return(path+file)
    else:
        return(path+os.sep+file)

def get_subsequence_strings(string_list,lemma_list,length):
    output = []
    for index in range(len(string_list)):
        if (index+length)> len(string_list):
            pass
        elif lemma_list == False:
            output.append([" ".join(string_list[index:index+length]),False])
        else:
            output.append([" ".join(string_list[index:index+length])," ".join(lemma_list[index:index+length])])
    return(output)

def preposition_member(string_list):
    if ('of' in string_list) or ('for' in string_list):
        return(True)
    else:
        return(False)

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

def OK_substring(substring):
    if not substring in closed_class_stop_words:
        return(True)
    else:
        return(False)
    
def get_term_substrings(string,lemma):
    global lemma_dict
    output = []
    string_list = string.split()
    if (string in lemma_dict) or (preposition_member(string_list)):
        ## these are cases where substrings of lemmas will not align
        ## with substrings of string
        lemma_list = False
    elif (lemma == string):
        lemma_list = False
    elif lemma == False:
        lemma_list = False
    else:
        lemma_list = lemma.split()
        if (len(lemma_list) == len(string_list)):
            lemma_list = False
    output = []
    for length in range(1,len(string_list)): 
        ## longest list is length-1; shortest list is 1 word
        for substring in get_subsequence_strings(string_list,lemma_list,length):
            if OK_substring(substring):
                output.append(substring)
    return(output)

def update_term_dict(short_file_name,term_dict,string,lemma,start,end,head_term,merge_super_string=False,all_keys=False,substring_of=False):
    global lemma_dict
    if lemma and (lemma in term_dict):
        entry = term_dict[lemma]
        if 'instances' in entry:
            entry['instances'].append([short_file_name,start,end,False])
        else:
            entry['instances'] = [[short_file_name,start,end,False]]
        if (not 'variants' in entry):
            entry['variants'] = [lemma]
        if (not lemma == string) and (not string in entry['variants']):
            entry['variants'].append(string)
    elif lemma:
        entry = {}
        entry['instances'] = [[short_file_name,start,end,False]]
        entry['variants'] = [lemma]
        if not string in entry['variants']:
            entry['variants'].append(string)
        term_dict[lemma] = entry
    else:
        entry = False
    if entry and substring_of:
        if not 'substring_of' in entry:
            entry['substring_of']=[substring_of]
        elif not substring_of in entry['substring_of']:
            entry['substring_of'].append(substring_of)


def count_files(instances):
    files = []
    for tfile,start,end,is_substring in instances:
        if not tfile in files:
            files.append(tfile)
    return(len(files))

def get_term_maps(term_list,file_list,outfile,input_path_prefix,remove_mismatches=True,minimum=3,json=True):
    ## don't use abbr dict for now, but could in the future
    ## term_list consists of input terms
    ## file_list consists of .terms files
    global lemma_dict
    term_dict = {}
    lemma_dict = {}
    keys = []
    with open(term_list) as instream:
        position = 0
        for line in instream:
            line = line.strip(os.linesep).lower()
            forms = line.split('\t')
            base = forms[0]
            reset_entry = False
            for form in forms:
                if (not reset_entry) and (form in lemma_dict):
                    reset_entry = True
                    base = lemma_dict[form]
            for form in forms:
                lemma_dict[form] = base
            if not base in keys:
                keys.append(base) ## maintain same order for print out
                ## does not repeat bases
    # for form in ['lrp','lung resistance related protein','lung cancer associated resistance protein']:
    #     print(lemma_dict[form],form)
    # input('pause')
    with open(file_list) as liststream:
        ## first pass do whole terms
        ## second pass just to substrings
        infile_list = []
        for infile in liststream:
            infile = infile.strip(os.linesep)
            infile = combine_path_and_file(input_path_prefix,infile)
            infile_list.append(infile)
            with open(infile) as instream:
                short_file_name = short_file(infile,input_path_prefix=input_path_prefix)
                ## print(short_file_name)
                for line in instream:
                    line = line.strip(os.linesep).lower()
                    entry = read_in_term_line(line)
                    string = entry['string']
                    if string in lemma_dict:
                        lemma = lemma_dict[string]
                    elif 'lemma' in entry:
                        lemma = entry['lemma']
                        if (lemma in lemma_dict) and (not lemma == lemma_dict[lemma]):
                            lemma = lemma_dict[lemma]
                    else:
                        lemma = False
                    if 'head_term' in entry:
                        head_term = entry['head_term']
                    else:
                        head_term = False
                    start = entry['start']
                    end = entry['end']
                    if string in lemma_dict:
                        lemma = lemma_dict[string]
                    elif lemma in lemma_dict:
                        lemma = lemma_dict[lemma]
                    else:
                        ## AM debug 8/3/2020
                        lemma = string
                    update_term_dict(short_file_name,term_dict,string,lemma,start,end,head_term,merge_super_string=remove_mismatches)
        for infile in infile_list:
            with open(infile) as instream:
                short_file_name = short_file(infile,input_path_prefix=input_path_prefix)
                for line in instream:
                    line = line.strip(os.linesep).lower()
                    entry = read_in_term_line(line)
                    string = entry['string']
                    if 'lemma' in entry:
                        lemma = entry['lemma']
                    elif string in lemma_dict:
                        lemma = lemma_dict[string]
                    else:
                        lemma = False
                    start = entry['start']
                    end = entry['end']
                    if lemma in lemma_dict:
                        lemma = lemma_dict[lemma]
                    elif string in lemma_dict:
                        lemma = lemma_dict[string]
                    for substring,lemma_substring in get_term_substrings(string,lemma):
                        if substring and lemma_substring and (substring in lemma_dict) and (lemma_substring in lemma_dict[substring]):
                            trade_key = update_term_dict(short_file_name,term_dict,substring,lemma_substring,start,end,head_term,substring_of=lemma)
                        else:
                             trade_key = update_term_dict(short_file_name,term_dict,substring,lemma_substring,start,end,head_term,substring_of=lemma)
                        if trade_key and (substring in keys):
                            position = keys.index(substring)
                            keys[position]= trade_key
                        elif trade_key and (lemma_substring in keys):
                            position = keys.index(lemma_substring)
                            keys[position] = trade_key
    with open(outfile,'w') as outstream:
        rank = 0
        ## do not repeat (repeats can arise due to substring terms)
        done = set()
        for key in keys[:]:
            rank = rank+1
            if key in term_dict:
                entry = term_dict[key]
            elif (key in lemma_dict)  and (key != lemma_dict[key]):
                ## never happens ??
                new_key = lemma_dict[key]
                if new_key in keys:
                    pass
                else:
                    print('key not found:',key)
            else:
                done.add(key)
                entry = []
                start_string = ''
                ## skip to rest of loop
            if not key in done:
                start_string = '<term string="'+key+'" rank='+str(rank)
            else:
                start_string = ''
                skip = True
            if (not 'variants' in entry) and (not 'substring_of' in entry):
                if remove_mismatches:
                    pass
                else:
                    entry['hypothetical'] = True
                    start_string +=' hypothetical_term="'+key+'"'
                skip = True
            else:
                skip = False
            if 'instances' in entry:
                number_of_files = count_files(entry['instances'])
            else:
                number_of_files = 0
                skip = True
                ## print('Warning:',key,'has no instances. Outfile:',outfile)
            if not skip:                
                start_string += ' number_of_files_containing_term='+str(number_of_files)
                length = len(entry['instances'])
                start_string += ' total_frequency='+str(length)
            if 'variants' in entry:
                start_string += ' variants="'
                for variant in entry['variants']:
                    start_string +=variant+'|'
                    if not variant in done:
                        done.add(variant)
                start_string = start_string[:-1]+'"'
            if 'substring_of' in entry:
                start_string += ' substring_of="'
                for variant in entry['substring_of']:
                    start_string +=variant+'|'
                start_string = start_string[:-1]+'"'
            if minimum and (number_of_files<minimum):
                start_string = ''
                skip = True
            elif skip and remove_mismatches:
                start_string = ''
            else:
                start_string +='>'
                done.add(key)
            ## remove final pipe and close start_string
                outstream.write(start_string+'\n')
            if not skip:
                for tfile,start,end,is_substring in entry['instances']:
                    if is_substring:
                        instance_string = '<instance file="'+tfile+'" start='+str(start)+' end='+str(end)+' is_substring="True"/>\n'
                    else:
                        instance_string = '<instance file="'+tfile+'" start='+str(start)+' end='+str(end)+'/>\n'
                    outstream.write(instance_string)
            if skip and remove_mismatches:
                pass
            else:
                outstream.write('</term>\n')
    
