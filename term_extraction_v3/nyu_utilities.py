import random
import os
import shutil
import re

### path variables

DICT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + os.sep
## DICT_DIRECTORY = '/home/meyers/FUSE/Python-Scripts/'

ORG_DICTIONARY = DICT_DIRECTORY+'org_dict.txt'

LOC_DICTIONARY = DICT_DIRECTORY+'location-lisp2-ugly.dict'

NAT_DICTIONARY = DICT_DIRECTORY+'nationalities.dict'

DISC_DICTIONARY = DICT_DIRECTORY+'discourse.dict'

TERM_REL_DICTIONARY = DICT_DIRECTORY+'term_relation.dict'

pos_offset_table = {}

xml_pattern = re.compile(r'<([/!?]?)([a-z?\-]+)[^>]*>',re.I)
xml_string = '<([/!?]?)([a-z?\-]+)[^>]*>'
attribute_value_from_fact = re.compile(r'([A-Z_]+)[=]((["][^"]+["])|([0-9]+))',re.I)
find_numbered_utf8 = re.compile(r'&#x([0-9a-f]*);',re.I)
noun_base_form_dict = {}
plural_dict = {}
verb_base_form_dict = {}
verb_variants_dict = {}

ARG1_NAME_TABLE ={'EXEMPLIFY':'SUBCLASS','DISCOVER':'INVENTOR','MANUFACTURE':'MAKER','SUPPLY':'SUPPLIER',\
                      'ORIGINATE':'INVENTOR','ALIAS':'FULLNAME','ABBREVIATE':'FULLNAME','BETTER_THAN':'BETTER',\
                      'BASED_ON':'DERIVED','CONTRAST':'THEME','CORROBORATION':'THEME','CO-CITATION':'THEME',\
                      'POSITIVE':'JUDGE','NEGATIVE':'JUDGE','SIGNIFICANT':'JUDGE','PRACTICAL':'JUDGE','STANDARD':'JUDGE'}
ARG2_NAME_TABLE ={'EXEMPLIFY':'SUPERCLASS','DISCOVER':'INVENTION','MANUFACTURE':'PRODUCT','SUPPLY':'PRODUCT',\
                      'ORIGINATE':'INVENTION','ALIAS':'FULLNAME','ABBREVIATE':'SHORTNAME','BETTER_THAN':'WORSE',\
                      'BASED_ON':'ORIGINAL','CONTRAST':'THEME','CORROBORATION':'THEME','CO-CITATION':'THEME',\
                      'POSITIVE':'THEME','NEGATIVE':'THEME','SIGNIFICANT':'THEME','PRACTICAL':'THEME','STANDARD':'THEME'}

RELATION_SUB_TYPE_TO_TYPE={'CONTRAST':'RELATED_WORK','BASED_ON':'RELATED_WORK','CORROBORATE':'RELATED_WORK',\
                           'BETTER_THAN':'RELATED_WORK','CO-CITATION':'RELATED_WORK','SUPPLY':'ORIGINATE',\
                           'MANUFACTURE':'ORIGINATE','DISCOVER':'ORIGINATE','ALIAS':'ABBREVIATE','POSITIVE':'OPINION',\
                           'NEGATIVE':'OPINION','SIGNIFICANT':'OPINION','PRACTICAL':'OPINION','STANDARD':'OPINION'}
                      
def look_up_main_relation(SUBTYPE):
    if SUBTYPE in RELATION_SUB_TYPE_TO_TYPE:
        return(RELATION_SUB_TYPE_TO_TYPE[SUBTYPE])
    else:
        return(SUBTYPE)

def short_file(filename):
    start = filename.rfind(os.sep)
    if start == -1:
        start = 0
    elif start == len(filename) - 1:
        return('???')
    else:
        start = start + 1
    end = filename[start:].rfind('.')
    if end == -1:
        return(filename[start:])
    else:
        end = start + end
        return(filename[start:end])

def short_file_with_extension(filename):
    start = filename.rfind(os.sep)
    if start == -1:
        start = 0
    elif start == len(filename) - 1:
        return('???')
    else:
        start = start + 1
    return(filename[start:])
    
def split_offset_from_line(line):
    out_list = line.partition(' ')
    return([out_list[0],out_list[2]])

def get_line_list(stream,length):
    output = []
    if stream:
        for num in range(length):
            offset_line_pair = split_offset_from_line(line)
            offset = offset_line_pair[0]
            line = offset_line_pair[1]
            output.append(line)
    return(output)

def choose_N_random_numbers (highest,length):
    so_far = 0
    output = []
    while len(output) < length:
        randnum = random.randint(0,highest-1)
        if not (randnum in output):
            output.append(randnum)
    return(output)

def choose_new_file(all_files,ignore_list):
    out_file = 'FAKE'
    while (out_file == 'FAKE') or (len(ignore_list) >= len(all_files)):
        number = random.randint(0,len(all_files)-1)
        out_file = all_files[number]
        if not (out_file in ignore_list):
            ignore_list.append(out_file)
            return(out_file)
    return(False)

def fix_spaces_in_file_name(file):
    import re
    outfile = re.sub(' ','\ ',file)
    return(outfile)
    
def choose_n_random_files(indirectory,infile,N,outdirectory,record_file,ignore_files='/home/meyers/annotation/used_files.txt'):
    ## infile is a list of files and indirectory is the relative
    ## path where all these files begin
    ignore_list = []
    lines = []
    output = []
    with open(ignore_files,'r') as instream:
        for line in instream:
            ignore = line.strip(os.linesep)
            ignore_list.append(ignore)
    with open(infile,'r') as instream:
        for line in instream:
            lines.append(line.strip(os.linesep))
        ## lines = instream.readlines()
        ## print('step 1',len(lines))
        if len(lines) <= N:
            for new_file in lines:
                if not new_file in ignore_list:
                    output.append(new_file)
        else:
            for n in range(N):
                new_file=choose_new_file(lines,ignore_list)
                ## finds new file that is not in ignore list,
                ## returns new_file, while adding new_file to ignore list
                ## for use in the next round
                if new_file:
                    output.append(new_file)
    if not os.path.isdir(outdirectory):
        os.mkdir(outdirectory)
    os.chdir(indirectory)
    with open(record_file,'w') as outstream:
        for file in output:
            ## file = fix_spaces_in_file_name(file)
            outstream.write(file+os.linesep)
            outfile = outdirectory+short_file_with_extension(file)
            infile = indirectory+file
            ## print(infile)
            ## print(outfile)
            shutil.copy(infile,outfile)
    
def path_merge (directory,file):
    if directory[-1] == os.sep:
        return(directory+file)
    else:
        return(directory+os.sep+file)


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

def roman_greater(string1,string2):
    return (roman(string1) and roman(string2) \
                   and (evaluate_roman(string1) > evaluate_roman(string2)))

def listify(item):
    if type(item) == list:
        return(item)
    else:
        return([item])

def remove_extra_spaces(input_string):
    match_string = '([    ]|'+os.linesep+')' ## various kinds of blanks are inside of the [] -- may need more
    output_string = re.sub(match_string+'+',' ',input_string)
    output_string = re.sub('^'+match_string+'*','',output_string)
    return(output_string)
        
def remove_sgml_line(line):
    pattern = xml_pattern.search(line)
    output = ''
    start = 0
    if not pattern:
        output = line
    while(pattern):
       output = output+line[start:pattern.start()]
       start = pattern.end()
       pattern = xml_pattern.search(line,start)
       if not pattern:
           output = output+line[start:]
    return(output)

def remove_xml(string):
    pattern = xml_pattern.search(string)
    output = ''
    start = 0
    use_pseudo_spaces = False
    if not pattern:
        output = string
    while(pattern):
        # if output != '' and output[-1] != ' ':
        #     output = output + ' '
        output = output+string[start:pattern.start()]
        if use_pseudo_spaces and pattern.group(1) == "/":
            output == output+'<space/>'
        start = pattern.end()
        pattern = xml_pattern.search(string,start)
        if pattern and (pattern.group(0) == '<USE_PSEUDO_SPACES/>'):
            use_pseudo_spaces = True
        if not pattern:
            # if output != '' and output[-1] != ' ':
            #     output = output + ' '
            output = output+string[start:]
    return(output)

def remove_xml_except(string,exceptions):
    pattern = xml_pattern.search(string)
    output = ''
    start = 0
    use_pseudo_spaces = False
    exceptions.extend(['SPACE','COMMA'])
    if not pattern:
        output = string
    while(pattern):
        # if output != '' and output[-1] != ' ':
        #     output = output + ' '
        if pattern.group(2).upper() in exceptions:
            output = output+string[start:pattern.end()]
        else:
            output = output+string[start:pattern.start()]
            if use_pseudo_spaces and pattern.group(1)=='/':
                output = output+'<space/>'
        if pattern.group(0) == '<USE_PSEUDO_SPACES/>':
            use_pseudo_spaces = True
        start = pattern.end()
        pattern = xml_pattern.search(string,start)
        if not pattern:
            # if output != '' and output[-1] != ' ':
            #     output = output + ' '
            output = output+string[start:]
    return(output)


def unlist_attributes(attribute_value_structure):
    if attribute_value_structure:
        for attribute in attribute_value_structure:
            if type(attribute_value_structure[attribute])==list:
                attribute_value_structure[attribute] = attribute_value_structure[attribute][0]

def get_integrated_line_attribute_value_structure(line,types):  
## From find_funders.py
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
            ## print(pattern.group(0))
            output[pattern.group(1)]=[pattern.group(2).strip('"')]  ## values are lists to permit multi-values
            start = pattern.end()
            pattern = attribute_value_from_fact.search(line,start)      
    return(output)

def get_integrated_line_attribute_value_structure_no_list(line,types):  
## From find_funders.py
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
            ## print(pattern.group(0))
            output[pattern.group(1)]=pattern.group(2).strip('"')  ## no list version
            start = pattern.end()
            pattern = attribute_value_from_fact.search(line,start)      
    return(output)

def breakup_line_into_chunks(inline,difference):
	size = 1000
	start = 0
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
    difference = 0 ## difference = 1
    table_pattern = re.compile('[^a-zA-Z0-9]TABLE[^a-zA-Z0-9]')
    end_table_pattern = re.compile('[A-Za-z][a-z]')
    table_start = table_pattern.search(line)
    output = []
    start = 0
    if not table_start:
        return([line])
    # else:
    #     print('start_length',len(line))
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
    ## print('A',len(output))
    for out in output:
        if len(out)<3000:
            output2.append(out)
        else:
            output2.extend(breakup_line_into_chunks(out,difference))
    # for out in output2:
    #     print(len(out),',',sep='',end='')
    # print('')
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

def get_lines_from_file(infile):
    with open(infile,'r') as instream:
        output = []
        for line in (instream.readlines()):
            for line2 in long_line_split(line):
                output.append(line2)
        return(output)

## code for loading lisp style dictionaries

organization_dictionary = {}
location_dictionary = {}
nationality_dictionary = {}
discourse_dictionary = {}
term_rel_dictionary = {}

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
    ## print(string)
    initial_list = string.partition(' ')
    key = initial_list[0]
    value = initial_list[2].strip(' ')
    if list_starter(value):
        if list_ender(value):
            value = process_lexicon_list(value)
        else:
            raise Exception('Current Program cannot handle recursive structures')
    elif string_starter(value) and string_ender(value):
        value = value.strip('"')
    return (key, value)

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

def return_stray_colons(string):
    return(string.replace('-colon-',':'))
        
def add_dictionary_entry(line,dictionary,shallow):
    ## print(line)
    clean_line = line.strip(os.linesep+'(\t')
    if clean_line[-1] == ")":
        clean_line = clean_line[:-1]
    clean_line = fix_stray_colons(clean_line)
    ## print(clean_line)
    line_list = clean_line.split(':')
    for index in range(len(line_list)):
        line_list[index] = return_stray_colons(line_list[index])
    entry_type = line_list[0].strip(' ')
    entry_dict = {}
    current_key = False
    current_value = False
    started_string = False
    ## print ('line list: ', line_list[1:])
    for key_value in line_list[1:]:
        key_value = key_value.strip(' ')
        key_value = get_key_value(key_value)
        key = key_value[0]
        value = key_value[1]
        entry_dict[key] = value
    if dictionary == 'org':
        organization_dictionary[entry_dict['ORTH'].upper()] = entry_dict  
    elif dictionary == 'loc':
        location_dictionary[entry_dict['ORTH'].upper()] = entry_dict
    elif dictionary =='nat':
        nationality_dictionary[entry_dict['ORTH'].upper()] = entry_dict
    elif dictionary in ['discourse', 'term_relation']:
        if dictionary == 'discourse':
            actual_dict = discourse_dictionary
        else:
            actual_dict = term_rel_dictionary
        if shallow and ('SHALLOW_LOW_CONF' in entry_dict):
            pass
        elif 'FORMS' in entry_dict:
            forms = entry_dict['FORMS']
            entry_dict.pop('FORMS')
            word = entry_dict.pop('ORTH')
            word = word.lower()
            for num in range(len(forms)):
                forms[num] = forms[num].lower()
##            if not word in forms:
##                forms.append(word)
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

def read_in_org_dictionary(dict_file,dictionary='org',shallow=True):
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
            add_dictionary_entry(line,dictionary,shallow)

def utf8_from_html_code(code):
    num = int("0x"+code,0)
    return(chr(num))

def convert_markoff_utf8_numbers_to_characters(line,proteus=False,sgml=[]):
    ## may want to deal with "<", even if not converted.
    ## to do this, we need to know the sgml exceptions
    utf8_conversion = find_numbered_utf8.search(line)
    start = 0
    if not utf8_conversion:
        output = line
    else:
        output = ''
    while utf8_conversion:
        converted_character = utf8_from_html_code(utf8_conversion.group(1))
        if proteus and (converted_character == '<'):
            converted_character = '&lt;'
        output = output+line[start:utf8_conversion.start()]+converted_character
        start = utf8_conversion.end()
        utf8_conversion = find_numbered_utf8.search(line,start)
        if not utf8_conversion:
            output = output + line[start:]
    return(output)

## make some fudges so that it matches when necessary, e.g., theta matches 'T' (the first letter in 'Theta')
## it probably won't overgenerate, but it might

greek_match_table = {'Α':'A','Β':'B','Γ':'G','Δ':'D','Ε':'E','Ζ':'Z', 'Η':'H', 'Θ':'T',\
                         'Ι':'I', 'Κ':'K', 'Λ':'L','Μ':'M', 'Ν':'N','Ξ':'X', 'Ο':'O', \
                         'Π':'P', 'Ρ':'R', 'Σ':'S','Τ':'T', 'Υ':'U','Φ':'P','Χ':'C','Ψ':'P','ϖ':'P'}

def write_citation_fact(fact,outstream,number,output_style="BAE",NYU_ID=False):
    ## Default style = BAE
    ## other fact_type = MAE
    if output_style=="BAE":
        if not 'ID' in fact:
            if 'ENTITY_ID' in fact:
                outstream.write('CITATION ID="'+fact['ENTITY_ID']+'"')
            else:
                outstream.write('CITATION ID="NYU_RELATION_'+str(number)+'"')
        else:
            outstream.write('CITATION')
        if NYU_ID:
            outstream.write(' NYU_ID=\"E'+str(number)+'\"')
        # if ('YEAR' in fact) and ('TITLE' in fact):
        #     outstream.write(' UniqueID="'+str(fact['YEAR'])+' '+fact['TITLE']+'"')
        for key in ['ID','TITLE','YEAR','START','END','CITE_CLASS','SOURCE','VOLUME','FPAGE','LPAGE','ISSUE','AUTHORS','EXT_LINK','INCOMPLETE','MULTIPLE_CITATIONS_ERROR']:
            if key in fact:
                value = fact[key]
                if (type(value) == list) and (len(value) == 1):
                    value = value[0]
                if type(value) == int:
                    value = str(value)
                elif type(value) == str:
                    value = '"'+value+'"'
                elif type(value) == bool:
                    value = '"'+str(value)+'"'
                else:
                    value = '"'+str(value)+'"'
                    print('Bad value for fact',number,'--',value)
                outstream.write(' '+key+'='+value)
    elif output_style=='MAE':
        outstream.write('<ENAMEX id=\"E'+str(number)+'\" ')
        if 'ID' in fact:
            fact['ENTITY_ID']=fact['ID']
        fact['type']='CITATION'
        for key_pair in [['START','start'],['END','end'],['TEXT','TEXT'],['type','type'],['ENTITY_ID','ENTITY_ID'],['CITE_CLASS','CITE_CLASS']]:
            if key_pair[0] in fact:
                outstream.write(key_pair[1]+'="'+str(fact[key_pair[0]])+'" ')
        outstream.write("/>")
    outstream.write(os.linesep)

def write_word_block_fact(fact,outstream,number,NYU_ID=False):
    outstream.write('WORD_BLOCK ID="NYU_BLOCK_'+str(number)+'"')
    for key in ['START','END']:
        value = fact[key]
        if (type(value) == list) and (len(value) == 1):
            value = value[0]
        if type(value) == int:
            value = str(value)
        outstream.write(' '+key+'='+value)
    outstream.write(os.linesep)

def get_n_random_lines (infile,outfile,N):
    random.seed()
    lines = get_lines_from_file(infile)
    nums = []
    while len(nums) < N:
        new_num = random.randint(0,len(lines)-1)
        if not new_num in nums:
            nums.append(new_num)
    nums.sort()
    with open(outfile,'w') as outstream:
        for num in nums:
            ## print(num)
            outstream.write(lines[num])

def remove_xml_file(infile,outfile):
    with open(infile) as instream, open(outfile,'w') as outstream:
        for line in instream:
            outstream.write(remove_xml(line))

noun_morph_file = DICT_DIRECTORY+'noun-morph-2000.dict'

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

verb_morph_file = DICT_DIRECTORY+'verb-morph-2000.dict'

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

def default_verb_forms(base):
    if base[-1] == 'e':
        return ([base,base+'s',base+'d',base[-1]+'ing'])
    elif (len(base)>3) and (base[-1] == 'y') and (not (base[-2] in aeiou)):
        return([base,base[:-1]+'s',base[:-1]+'ied',base+'ing'])
    elif base[-1] in ['szxhy']:
        return([base,base+'es',base+'ed',base+'ing'])        
    elif base[-1] == 'c':
        return([base,base+'s',base+'ked',base+'king'])
    elif (len(base)>3) and (not (base[-1] in 'aiou')) and (base[-2] in 'aeiou'):
        return ([base,base+'s',base+base[-1]+'ed',base+base[-1]+'ing'])
    else:
        return ([base,base+'s',base+'ed',base[-1]+'ing'])

def load_pos_offset_table(pos_file):
    global  pos_offset_table
    pos_offset_table.clear()
    with open(pos_file) as instream:
        for line in instream.readlines():
            line_info = line.strip().split(' ||| ')
            start_end = line_info[1]
            start_end_strings = start_end.split(' ')
            start = int(start_end_strings[0][2:])
            pos = line_info[2]
            pos_offset_table[start] = pos
