import os
from citation_tables import *
from wol_utilities import *
from xml.sax.saxutils import escape
from xml.sax.saxutils import unescape
import re
import roman

## this first part of this file contains the code for finding case citations
## the second part finds the code for legislation citations
## thirdly, there are functions for finding both.

## Part 1 -- Case Citations

prepositions = ['by', 'for', 'from', 'in', 'of', 'on', 'to', 'with', 'within']

year_pattern = re.compile('(^|[^0-9])((17|18|19|20)[0-9][0-9])($|[^0-9])')
initial_role_words = ['plaintiff','prosecutor', 'prosecution','defendant','appellant','appellee','claimant','petitioner','respondent', 'intervenor','complainant','libellant']
         ## there may be additional roles, but not sure if they appear as part of vs case names

in_error_pattern = re.compile('(in err(\.|or)?)([^a-z]|$)',re.I)

is_month = re.compile('^'+month+'$')

date_pattern = re.compile(full_date,re.I) ## case insensitive version
## requires month and year, with date optional

all_role_words = initial_role_words[:] 
         
role_prefixes = ['counter','cross','counterclaim','crossclaim']
pre_citation_words = ['see','also','cf','compare','later','in']
topic_matter_words = ['issue','matter','subject','topic']

compound_roles = []

id_number = 0
## include productive role combos without going into endless loop and producing, e.g., cross-cross-counter-claimant

for prefix in role_prefixes:
    for role in all_role_words:
        compound_roles.append(prefix+role)
        compound_roles.append(prefix+' '+role)
        compound_roles.append(prefix+'-'+role)

all_role_words.extend(compound_roles)

plural_roles = []

for role in all_role_words:
    plural_roles.append(role+'s')
    ## note there seem to be no irregular plurals for these roles or even roles that need an "es" added
    ## this may change if we find more roles (and the we will need to implement a more complete code for plural)

all_role_words.extend(plural_roles)

### above role settings assume original non-dictionary version
### for dictionary version, we should use the following function to generate the new sets of RANK and ROLES
### for the dictionary (replacing the old set in the dictionary)
### 

relational_dict = {}

relational_dict_file = 'relational.dict'

time_dict = {}
time_dict_file = 'time_names.dict'

one_word_person_names = {}

def is_role_word(ref_word):
    return((ref_word in relational_dict) and (('LEGAL_ROLE' in relational_dict[ref_word]) or ('PLURAL_LEGAL_ROLE' in relational_dict[ref_word])))

def capitalized_word(word):
    ## istitle and isupper don't work well enough for my purposes
    ## they exclude outliers like cammelcase
    return((len(word)>0) and word[0].isupper())

load_tab_deliniated_dict(relational_dict_file,relational_dict)
load_tab_deliniated_dict(time_dict_file,time_dict)

def add_to_POS_dict(infile,word_class):
    with open(infile) as instream:
        for line in instream:
            line = line.strip(os.linesep).lower()
            if line in POS_dict:
                if not word_class in POS_dict[line]:
                    POS_dict[line].append(word_class)
            else:
                POS_dict[line]=[word_class]

add_to_POS_dict('discourse_words.txt','DISCOURSE')
add_to_POS_dict('firstname.dict','FIRSTNAME')
add_to_POS_dict('person_name_list_short.dict','PERSONNAME')
add_to_POS_dict('location_list.dict','GPE')
add_to_POS_dict('state_abbreviations.dict','GPE')
add_to_POS_dict('org_list.dict','ORG')
add_to_POS_dict('nationalities.dict','NATIONALITY')


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

def is_roman (string):
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
        if (len(lower)>2) and (lower in POS_dict):
            return(False)
        else:
            return(result)
    else:
        return(False)

## these next 2 functions were used for generating entries in the role dictionary
def role_word_variations(base_word,prefixes):
    ## unlike basic version, this does not provide two word role names
    ## this does not account for irregular plurals or plurals requiring the adding of "es"
    ## (e.g., those ending in 'z','ch', 'sh' or 's')
    output = [base_word,base_word+'s']
    for prefix in prefixes:
        output.append(prefix+base_word)
        output.append(prefix+'-'+base_word)
        output.append(prefix+base_word+'s')
        output.append(prefix+'-'+base_word+'s')
    return(output)
        
def generate_set_of_entries(outfile):
    entries = []
    for prefix in role_prefixes:
        entries.append([prefix,'LEGAL_RANK'])
    for base_word in initial_role_words:
        for word in role_word_variations(base_word,role_prefixes):
            entries.append([word,'LEGAL_ROLE'])
    entries.sort()
    with open(outfile,'w') as outstream:
        for entry in entries:
            ### assumes all entries have exactly one class
            outstream.write(entry[0]+'\t'+entry[1]+os.linesep)

## page_number_pattern = '((([0-9—]+, )*[0-9—]+)|—-|_+)'  ## commas will may cause problems
## for disambiguating borders between citations

standard_citation_pattern = re.compile('([0-9]+)( +)('+court_reporter_rexp+')[ _]*([0-9]+)?',re.I)
at_citation_pattern = re.compile('([0-9]+)( +)('+court_reporter_rexp+'),?( +)(at *)([0-9]+)',re.I)
## fields 1 = volume, 3 = reporter, 54 = page number (under current court_reporter_rexp)
## need second pattern that starts at page number because the size of court_reporter_rexp will not be stable

standard_citation_pattern_extension = re.compile('(([0-9]+(—[0-9]+)?)|—-|_+)(, *([0-9]+( *-[0-9]+)?))?(( *(\([^)^(]+\)))*)',re.I)
## require comma for paragraph? -- paragraph overgenerates -- require date or ignore paragraph?

standard_citation_pattern_short_extension = re.compile(' *(([0-9]+(—[0-9]+)?)|—-|_+)',re.I)

at_page_number = re.compile('at *(([0-9]+(—[0-9]+)?)|—-|_+)',re.I)

def get_year_and_court_from_parentheses_region(instring):
    court_pattern = re.compile('[^a-zA-Z]([A-Za-z0-9][A-Za-z0-9\. ]*[A-Za-z-0-9\.])')
    end_paren_pattern = re.compile('\)')
    year_match = year_pattern.search(instring)
    end = False
    if year_match:
        year = year_match.group(2)
        court_match = court_pattern.search(instring[:year_match.start()])
        if court_match and not (court_match.group(1).lower() in court_abbrev_table):
            court_match = False
        if not court_match:
            court_match = court_pattern.search(instring,year_match.end())
            if court_match and not (court_match.group(1).lower() in court_abbrev_table):
                court_match = False
    else:
        court_match = court_pattern.search(instring)
        if court_match and not (court_match.group(1).lower() in court_abbrev_table):
            court_match = False
        year = False
    if court_match:
        court = court_match.group(1)
    else:
        court = False
    if court:
        if year:
            end = max(court_match.end(1),year_match.end(2))
        else:
            end = court_match.end(1)
    elif year:
        end = year_match.end(2)
    if end:
        end_pat = end_paren_pattern.search(instring,end)
        if end_pat:
            end = end_pat.end()
    return(year,court,end)

def possible_comment(comment):
    match = date_pattern.search(comment)
    if match and (comment.strip('()') == match.group(0)):
        return(False)
    return(True)
    
def revise_citation_match_extra(line,possible_start,citation_match_extra):
    ## checks to make sure that page number is not really the volume number
    if citation_match_extra.group(5):
        citation_match = standard_citation_pattern.search(line,possible_start)
        at_citation_match = at_citation_pattern.search(line,possible_start)
        if citation_match and (citation_match.start()<=citation_match_extra.start(5)):
            new_pattern = standard_citation_pattern_short_extension.search(line,possible_start)
            return(new_pattern,False,False)
        elif at_citation_match and (at_citation_match.start()<=citation_match_extra.start(5)): 
            new_pattern = standard_citation_pattern_short_extension.search(line,possible_start)
            return(new_pattern,False,False)
        elif citation_match_extra.group(9) and possible_comment(citation_match_extra.group(9)):
            comment = [citation_match_extra.start(9)+1,citation_match_extra.end(9)-1,citation_match_extra.group(9)[1:-1]]
            ## removing parens from comment
            citation_match_extra = standard_citation_pattern_extension.search(line[:citation_match_extra.start(7)],citation_match_extra.start())
            return(citation_match_extra,True,comment)
        else:
            return(citation_match_extra,True,False)
    else:
        if citation_match_extra.group(9) and possible_comment(citation_match_extra.group(9)):
            comment = [citation_match_extra.start(9)+1,citation_match_extra.end(9)-1,citation_match_extra.group(9)[1:-1]]
            ## removing parens from comment
            citation_match_extra = standard_citation_pattern_extension.search(line[:citation_match_extra.start(7)],citation_match_extra.start())
        else:
            comment = False
        return(citation_match_extra,True,comment)

def add_citation_id(record,file_id,dictionary):
    global id_number
    id_number = id_number+1
    id_string = file_id + '_' + str(id_number)
    record['id']=id_string
    dictionary[id_string]=record

def get_next_standard_citation(line,start=0):
    # print(start)
    # print(line[start:])
    pattern = standard_citation_pattern.search(line,start)
    while pattern:
        # if '$' in pattern.group(0):
        #     print(pattern.group(0))
        if pattern and (pattern.end()<len(line)) and re.search('[a-zA-Z0-9]',line[pattern.end()]):
            pattern = standard_citation_pattern.search(line,pattern.end())
        elif pattern and (pattern.start() != 0) and (line[pattern.start()-1] in '$'):
            ## possibly add additional characters to '$' that can precede numbers to make
            ## them invalid beginners of citations
            start = pattern.end(1) ## after number string
            pattern = standard_citation_pattern.search(line,start)
        else:
            return(pattern)
    
def violates_standard_citation_distance(line,citation_end,extra_start):
    if not line:
        return(True)
    elif (extra_start - citation_end)> 100:
        return(True)
    elif len(line[citation_end:extra_start].split(' '))>6:
        return(True)
    else:
        return(False)

def make_comment_object(triple,file_id,dictionary,offset,line_number):
    start,end,text = triple
    output = {'entry_type':'comment','start':start+offset,\
              'end':end+offset,'string':text,
              'line':line_number}
    add_citation_id(output,file_id,dictionary)
    return(output)

def get_citation_output(line,offset,file_id,citation_dictionary,line_number):
    global id_number
    ## to get X v Y
    ## find 2 capitalized sequences surrounding a "v."
    ## Use filters to the beginning of the sequence to not include
    ## "See" and "Cf." and a possibly a larger stop list of words
    ## the end should probably be punctuation and often should precede , + standard citation
    ## once codified as a citation -- the X v Y sequence can be found elsewhere 
    ## in the text
    output = []
    ## first getting standard citation
    citation_match = get_next_standard_citation(line)
    at_citation_match = at_citation_pattern.search(line)
    start = 0
    comments = []
    while citation_match or at_citation_match:
        comment = False
        if at_citation_match and citation_match:
            if citation_match.start()<at_citation_match.start():
                at_citation_match = False
            else:
                citation_match = False
        if at_citation_match:
            citation_start = at_citation_match.start()+offset
            if ('§' in at_citation_match.group(0)):
                out = False
                start = citation_match.end()
                citation_match_extra = False
            else:
                out = {'start':citation_start}
                out['volume'] = at_citation_match.group(1)
                out['reporter'] = at_citation_match.group(3)
                standard_reporter = at_citation_match.group(3).upper()
                if standard_reporter in court_reporter_standard_table:
                    standard_reporter = court_reporter_standard_table[standard_reporter]
                out['standard_reporter'] = standard_reporter
                citation_match_extra = at_page_number.search(line,at_citation_match.end(3))
                if citation_match_extra and ('§' in line[at_citation_match.start():citation_match_extra.end()]):
                    start = citation_match_extra.end()
                    citation_match_extra = False
                    out = False
                if citation_match_extra:
                    out['page_number'] = citation_match_extra.group(1)
        else:
            citation_start = citation_match.start()+offset
            if ('§' in citation_match.group(0)):
                start = citation_match.end()
                out = False
                citation_match_extra = False
            else:
                out = {'start':citation_start}
                out['volume'] = citation_match.group(1)
                out['reporter'] = citation_match.group(3)
                standard_reporter = citation_match.group(3).upper()
                if standard_reporter in court_reporter_standard_table:
                    standard_reporter = court_reporter_standard_table[standard_reporter]
                out['standard_reporter'] = standard_reporter
                citation_match_extra = standard_citation_pattern_extension.search(line,citation_match.end(3))
                if citation_match_extra and violates_standard_citation_distance(line,citation_match.end(),citation_match_extra.start()):
                    citation_match_extra = False
                if citation_match_extra and ('§' in line[citation_match.start():citation_match_extra.end()]):
                    start = citation_match_extra.end()
                    citation_match_extra = False
                    out = False
                else:
                    possibly_competing_citation_match = get_next_standard_citation(line,citation_match.end(3))
                    if citation_match_extra and possibly_competing_citation_match:
                        if citation_match_extra.start() >= possibly_competing_citation_match.start():
                            citation_match_extra = False
                    if citation_match_extra:
                        citation_match_extra,paragraph_check,comment = revise_citation_match_extra(line,citation_match.end(3),citation_match_extra)
        end = False
        paren_end = False
        year = False
        court = False
        if not out:
            pass
        elif citation_match_extra and not at_citation_match:
            if citation_match_extra.group(1):
                if (len(citation_match_extra.group(1))==4) and (line[citation_match_extra.start(1)-1]=='(')\
                   and year_pattern.search(citation_match_extra.group(1)):
                    out['year'] = citation_match_extra.group(1)
                else:
                    out['page_number'] = citation_match_extra.group(1)
            if paragraph_check:
                paragraph_number = citation_match_extra.group(5)
            else:
                paragraph_number = False
            if paragraph_number:
                out['paragraph_number'] = paragraph_number
                ## the "at" pattern seems not to include year and court info
            if paragraph_check:
                year,court,paren_end = get_year_and_court_from_parentheses_region(citation_match_extra.group(7))
            else:
                year,court,paren_end = False,False,False
                paragraph_number = False
            if paren_end:
                end = paren_end + citation_match_extra.start(7)
                out['end'] = end + offset
                out['string']=line[citation_match.start():end]
            else:        
                end = False        
                out['string']=line[citation_match.start():citation_match_extra.end()]
                out['end'] = citation_match_extra.end()+offset
            if year:
                out['year'] = year
            if court:
                out['court'] = court
            if end:
                start = end
            else:
                start = citation_match_extra.end()
        elif at_citation_match:
            out['end'] = at_citation_match.end()+offset
            out['string']=at_citation_match.group(0)
            start = at_citation_match.end()
        elif citation_match:
            out['end'] = citation_match.end()+offset
            out['string']=citation_match.group(0)
            start = citation_match.end()
        if out and re.search(',$',out['string']):
            ## fix for comma at end
            out['string'] = out['string'][:-1]
            out['end'] = out['end']-1
        if out and ('reporter' in out) and ('volume' in out) and ('page_number' in out):
            output.append(out)
        if comment and not date_pattern.search(comment[2]):
            ## dates will be handled by a separate process
            comments.append(make_comment_object(comment,file_id,citation_dictionary,\
                                                offset,line_number))
        citation_match = get_next_standard_citation(line,start)
        at_citation_match = at_citation_pattern.search(line,start)
        citation_match_extra = False
    for record in output:
        add_citation_id(record,file_id,citation_dictionary)
    return(output,comments)

def generic_object_print(outstream,out):
    if 'entry_type' in out:
        outstream.write('<'+out['entry_type'])
    else:
        return()
    for attribute in ['id','entry_type','start','end']:
        if attribute in out:
            outstream.write(' '+attribute+'="'+wol_escape(str(out[attribute]))+'"')
    for attribute in out:
        if not attribute in ['entry_type','id','entry_type','start','end','string']:
            outstream.write(' '+attribute+'="'+wol_escape(str(out[attribute]))+'"')
    outstream.write('>')
    if 'string' in out:
        outstream.write(wol_escape(out['string']))
    outstream.write('</'+out['entry_type']+'>\n')

def citation_print(outstream,citation):
    if citation['entry_type'] in ['standard_case','case_X_vs_Y','case_citation_other']:
        outstream.write('<citation')
    elif citation['entry_type'] in ['docket']:
        outstream.write('<docket')
    for attribute in ['id','entry_type','start','end','name','reporter','standard_reporter','volume','page_number','paragraph_number','court','year','party1','party2','party1_role','party2_role','line']:
        if attribute in citation:
            outstream.write(' '+attribute+'="'+wol_escape(str(citation[attribute]))+'"')
    outstream.write('>')
    if 'string' in citation:
        outstream.write(wol_escape(citation['string']))
    if citation['entry_type'] in ['standard_case','case_X_vs_Y','case_citation_other']:
        outstream.write('</citation>'+os.linesep)
    elif citation['entry_type'] in ['docket']:
        outstream.write('</docket>'+os.linesep)

def ok_docket(docket):
    if re.search('[0-9]',docket):
        return(True)
    else:
        return(False)

def get_docket_numbers(line,spans,offset,file_id,citation_dictionary):
    docket_pattern = re.compile('(^| )(no\. *([a-z0-9]+[-–][a-z0-9\-–]+))',re.I)
    match = docket_pattern.search(line)
    output = []
    while match:
        target_field = 3
        next_start = match.end()
        for span_start,span_end in spans:
            span_start = span_start-offset
            span_end = span_end-offset
            if match and (match.start(1) >=span_start) and (match.start(target_field)<span_end):
                match = False
        if match and ok_docket(match.group(target_field)):
          out = {'start':match.start(target_field)+offset,'end':match.end(target_field)+offset,'string':match.group(target_field),'offset_start':match.start(0)+offset}
          output.append(out)
        if match:
          match = docket_pattern.search(line,match.end(target_field))
    for record in output:
        add_citation_id(record,file_id,citation_dictionary)
    return(output)

def get_docket_number_sets(line,spans,offset,file_id,citation_dictionary):
    docket_pattern = re.compile('(^| )nos\. *([a-z0-9]+[-–][a-z0-9\-–]+)',re.I)
    docket_pattern2 = re.compile('( and|,) *([a-z0-9]+[-–][a-z0-9\-–]+)',re.I)
    match1 = docket_pattern.search(line)
    match2 = False
    output = []
    while match1 or match2:
        semi_match = False
        if match1 and match2:
            if match1.start() < match2.start():
                match = match1
            else:
                match = match2
        elif match1:
            match = match1
        else:
            match = match2
        next_start = match.end()
        for span_start,span_end in spans:
            span_start = span_start-offset
            span_end = span_end-offset
            if match and (match.start(2) >=span_start) and (match.start(2)<span_end):
                if match and (not semi_match):                
                    semi_match = match
                match = False
        if match and ok_docket(match.group(2)):
          out = {'start':match.start(2)+offset,'end':match.end(2)+offset,'string':match.group(2),'offset_start':match.start(0)+offset}
          output.append(out)
        if not match:
            match = semi_match
        match1 = docket_pattern.search(line,match.end(2))
        match2 = docket_pattern2.search(line,match.end(2))            
    for record in output:
        add_citation_id(record,file_id,citation_dictionary)
    return(output)

def ok_to_delete_left_most_vs_item (matches):
    if (len(matches)>0) and (len(matches[-1].group(1))>0):
        ref_item = matches[-1].group(1).strip(".,'\"").replace('/','')
    else:
        ref_item = False
    if len(matches)> 1:
        penult_ref_item = matches[-2].group(1).strip(".,'\"").replace('/','').lower()
    else:
        penult_ref_item = False
    if len(matches)==0:
        return(False)
    elif (ref_item.lower() in prepositions):
        return(True)
    elif (len(ref_item)>0) and ref_item[0].isupper():
        return(False)
    elif penult_ref_item in (org_ending_words+person_ending_words):
        return(False)
    else:
        return(True)

def ok_to_delete_right_most_vs_item (matches):
    month_match = re.compile(r'^('+month+r')$')
    if len(matches)==0:
        return(False)
    elif (len(matches[-1].group(0))>0) and (not matches[-1].group(0)[0].isupper()) \
      and (matches[-1].group(0).lower() in not_uppercase_part_of_org_names):
        return(True)
    elif month_match.search(matches[-1].group(0).lower()):
        return(True)
    elif (matches[-1].group(0).lower() in POS_dict) and ('PREP' in (POS_dict[matches[-1].group(0).lower()])):
        return(True)
    else:
        return(False)

def OK_comma_follows(word,first_letter):
    if (word == 'state') or (word in relational_dict) or (word in citation_filler_words) or first_letter.isupper() or (word in org_ending_words) or (word in person_ending_words):
        return(True)

def OK_comma_precedes(word):
    if (word in org_ending_words) or (word in person_ending_words) or (word in citation_filler_words) or (word in relational_dict) or (word in alias_words):
        return(True)

def possible_abbrev(word):
    ### may need longer list of abbreviations that do not end named units
    if (len(word)>0) and word[0].isupper() and ((len(word)==1) or (word.lower() in ['assoc', 'asst', 'capt', 'cdr', 'cmdr', 'col', 'dr', 'dr', 'exec', \
                                            'gen', 'gen', 'hon', 'lieut', 'lt', 'maj', 'messrs', 'mr', 'mrs', \
                                            'ms', 'pres', 'rep', 'sgt','nos','ltd','co','inc','corp','sa','cia','gmbh','llp'])):
        return(True)
    elif (word.lower() in relational_dict) and (word.lower()+'.' in relational_dict):
        return(True)

def advance_left_span(line,left_span,end):
    deletable = re.compile('(cite +as)|(writ of cert.*district,?( +division +[a-z]+)?)|(((Statement +of.*)|(Per +Curiam *))?SUPREME +COURT +OF +THE +UNITED STATES)|(ORDER IN PENDING CASE)',re.I)
    match = deletable.search(line,left_span)
    if match and (match.start()<end):
        return(match.end())
    else:
        return(left_span)

def deletable_middle(middle):
    ## for early lines in file only
    ## should be essentially same criteria as advance_left_function (except for the ^ and $)
    deletable = re.compile('^[^a-z]*((cite +as)|(writ of cert.*district,?( +division +[a-z]+)?)|(((Statement +of.*)|(Per +Curiam *))?SUPREME +COURT +OF +THE +UNITED STATES))[^a-z]*$',re.I)
    if deletable.search(middle):
        return(True)

def title_word(word):
    if (word.lower() in POS_dict) and ('TITLE' in POS_dict[word.lower()]):
        return(True)

def find_left_vs_border(line,end,left_span,one_line_objects,paren_comma,line_number):
    ## if one_line_objects, left border is more likely to be 0
    # if 'holmes' in line.lower():
    ## print(1,line,2,end,3,left_span,4,one_line_objects,5,paren_comma,6,line_number)
    global all_role_words
    pattern = re.compile('([a-z\'\-&/\[\]]+)([^a-z\-&/\[\]]*)$',re.I) ## allow words to contain intermediate hyphens and apostrophes
    roles = []
    current_end = end
    previous_word = pattern.search(line[:current_end])
    matches = []
    finished_roles = False
    if line_number < 5:
        old_left_end = left_span
    else:
        old_left_end = False
    left_span = advance_left_span(line,left_span,end)
    lowercase_parenthetical_commas_left_of_v = False
    lowercase = False
    is_number = False
    if previous_word and (previous_word.group(0).lower() in ['error', 'err']):
        current_end = previous_word.start()
        matches.append(previous_word)
        previous_word = pattern.search(line[:current_end])
        if previous_word and (previous_word.group(1).lower() == 'in'):
            current_end = previous_word.start()
            matches.append(previous_word)
            previous_word = pattern.search(line[:current_end])
            ## skip over "in error" modifier for purposes of finding extent
    first = True
    last_corporate_ending = False
    party_end = end
    last_ref_word = False
    last_word_string = False
    last_is_role = False
    fail = False
    found_name = False
    opened_paren = False
    number_of_words = 0
    while previous_word and (previous_word.start() >= left_span):
        word_string = previous_word.group(1)
        if word_string.strip(".,").replace('/','').islower():
            lowercase = True
        else:
            lowercase = False
        simple_string = word_string.strip(".,'\"").replace('/','')
        ref_word = word_string.lower().strip("\'")
        middle_ground = line[previous_word.end(1):current_end]
        if (')' in middle_ground) and (not '(' in middle_ground):
            opened_paren = True
        is_role = is_role_word(ref_word)
        is_number = ref_word.isdigit()
        if lowercase and "," in middle_ground:
            first = True
        if is_role:
            party_end = previous_word.start()
        if ((len(simple_string)>0) and simple_string[0].isupper()) \
            or is_role \
            or re.search('\[[a-z]',ref_word) \
            or opened_paren \
            or (lowercase and paren_comma and (first or lowercase_parenthetical_commas_left_of_v)) \
            or (ref_word in not_uppercase_part_of_org_names+alias_words) \
            or (ref_word in prepositions) \
            or (last_corporate_ending and re.search('^[a-z\.]+$',ref_word))\
            or ((ref_word in org_ending_words) and ((ref_word != 'limited') or (not '.' in middle_ground))) \
            or (ref_word in person_ending_words)\
            or (is_number and (not found_name))\
            or ((len(ref_word)>0) and (ref_word[0]=="'") and ("'" in middle_ground))\
            or (ref_word in citation_filler_words):
            if re.search('(; *$)|(\)\. *[^a-zA-Z]*$)',middle_ground ):
                previous_word = False
            elif re.search('\[[a-z]',ref_word):
                pass
            elif last_corporate_ending and (number_of_words < 2):
                pass
            elif title_word(ref_word):
                pass
            elif lowercase and first and paren_comma:
                lowercase_parenthetical_commas_left_of_v = True
                if opened_paren and ('(' in middle_ground):
                    opened_paren = False
            elif opened_paren and ('(' in middle_ground):
                opened_paren = False
            elif last_is_role and re.search('^[., ]*$',middle_ground):
                pass
            elif is_number and (not found_name):
                pass
            elif ((')' in middle_ground) and word_string.isupper()) or (('(' in middle_ground) and last_word_string and last_word_string.isupper()):
                pass
            elif lowercase and lowercase_parenthetical_commas_left_of_v:
                pass
            elif (ref_word in legislation_part_words) and re.search('[0-9]',middle_ground):
                pass
            elif re.search('[:]', middle_ground):
                previous_word = False
            elif ref_word in relational_dict:
                pass
            elif (ref_word in ['and','&','in','err']) and (last_is_role or (last_ref_word in  ['and','&','in','err'])):
                pass
            elif ref_word in pre_citation_words:
                previous_word = False
            elif ref_word in topic_matter_words:
                previous_word = False
            elif (not first) and (ref_word in latin_reference_words):
                previous_word = False
            elif (not one_line_objects) and (not first) and (not is_role) and re.search('[\(\)0-9]',middle_ground) and (not ref_word in ['no','nos']) and (not opened_paren) and found_name:
                previous_word = False
            elif ((len(ref_word)>0) and (ref_word[0]=="'") and ("'" in middle_ground)):
                pass
            elif (not one_line_objects) and (',' in middle_ground) and not(OK_comma_follows(ref_word,word_string[0])) \
              and (not ((len(matches)>0) and OK_comma_precedes(matches[-1].group(1).lower()))):
                previous_word = False
            elif ("." in middle_ground) and (not "," in middle_ground) and (not word_string.isupper()) and (ref_word in POS_dict) and (not ref_word in org_ending_words+person_ending_words+citation_filler_words+standard_words_with_periods_in_citations) and (not len(ref_word)==1):
                previous_word = False
            if previous_word and lowercase_parenthetical_commas_left_of_v and (not lowercase) and ("," in middle_ground):
                lowercase_parenthetical_commas_left_of_v = False
            if previous_word:
                number_of_words += 1
                current_end = previous_word.start()
                matches.append(previous_word)
                if is_role and previous_word:
                    in_error = in_error_pattern.search(line,previous_word.end())
                    if in_error and not(re.search('[^ ,]',line[previous_word.end():in_error.start()])):
                        ref_word = ref_word+' '+in_error.group(1).lower()
                if is_role and not (ref_word in roles):
                    roles.append(ref_word)
                if roles and (not is_role):
                    finished_roles = True
                if ref_word in org_ending_words:
                    last_corporate_ending = True
                else:
                    last_corporate_ending = False
                last_ref_word = ref_word
                last_word_string = word_string
                if is_role:
                    last_is_role = True
                elif last_is_role:
                    last_is_role = False
                if (not found_name) and (not is_role) and (len(word_string)>0) and word_string[0].isupper():
                    found_name = True
                previous_word = pattern.search(line[:current_end])
        else:
            previous_word = False
        if not (first and (is_role or lowercase_parenthetical_commas_left_of_v)):
            first = False
    if roles:
        roles.sort()
    while (ok_to_delete_left_most_vs_item (matches)):
        matches.pop()
        if len(matches) > 0:
            current_end=matches[-1].start()
        else:
            current_end = end
    if fail or (current_end == end):
        current_end = 'Fail'
        party = False
    else:
        party = line[current_end:party_end].strip(' ')
    return(current_end,roles,party,old_left_end)
    
    
## skip roles, citation_filler_words (currently just et and al)
## in tokenization, assume that apostrophe is part of words
## allow corporate endings (inc, etc) to follow commas 
## allow lowercase and to be part of names (but not if there is preceding punctuation)
## capital (Cf, See, Also, Re) ends a left name boundary (and is not included)
## in addition to normal names
## "The X of Name", e.g., "The State of Texas" are OK as well
## consecutive capitals can include certain lower case words 

## Abbreviations of the form "State, Ind." -- Capitalized word + comma + abbreviation or capital

## other exceptions org_ending_words are not a sufficient "left" name
## e.g., lowercase word would be needed for "investment Co. Institute v. Camp"

## if no left border, there is no citation, e.g., (section numbers that start with V)

def possibly_shorten_right_span(line,start,right_span):
    vs_anchor = re.compile('([^a-z])+(vs?[\. ])+([^a-z])*',re.I)
    ending_match = re.compile('([^ ]+)( {2,})[^ ]+',re.I)
    vs_match = vs_anchor.search(line[:right_span],start)
    if vs_match:
        ending = ending_match.search(line[:vs_match.start()])
        if ending and ((ending.end(1)-start)>10):
            return(ending.end(1))
    return(right_span)

def find_right_vs_border(line,start,right_span):
    global all_role_words
    right_span = possibly_shorten_right_span(line,start,right_span)
    output = []
    pattern = re.compile('[a-z\'\-&/\[\]]+',re.I) ## allow words to contain intermediate hyphens and apostrophes
    roles = []
    current_start=start
    next_word = pattern.search(line,current_start)
    matches = []
    party_end = start
    last_word = False
    date_match = date_pattern.search(line,start)
    vs_anchor = re.compile('([^a-z])+(vs?[\. ]|against|versus)+([^a-z])*',re.I)
    vs_anchor2 = re.compile('([A-Z])+(vs?\.?|against|versus)[A-Z]')
    vs_match = vs_anchor.search(line,start)
    vs_match2 = vs_anchor2.search(line,start)
    if vs_match and vs_match2:
        next_vs = min(vs_match.start(2),vs_match2.start(2))
    elif vs_match:
        next_vs = vs_match.start(2)
    elif vs_match2:
        next_vs = vs_match2.start(2)
    else:
        next_vs = False  
    if next_vs and re.search('[^a-zA-Z0-9][Nn][oO][^a-zA-Z0-9]',line[:next_vs]):
        next_vs = False
    ## not sure how this will deal with numbers as part of names, e.g., X No. 5
    while next_word and (next_word.end()<=right_span):
        word_string = next_word.group(0)
        ref_word = word_string.lower()
        middle_ground = line[current_start:next_word.start()]
        is_role = is_role_word(ref_word)
        if word_string[0].isupper() \
            or is_role \
            or (ref_word in not_uppercase_part_of_org_names) \
            or (ref_word in org_ending_words) \
            or (ref_word in person_ending_words) \
            or (ref_word in citation_filler_words) \
            or re.search('\[[a-z]',ref_word):
            if (re.search('^ {6}',middle_ground) and ref_word):
                next_word = False
            elif (len(matches)>0) and ((ref_word in latin_reference_words) or (ref_word in other_non_citation_legal_words) or (ref_word in months)):
                next_word = False
            elif re.search('[:]', middle_ground):
                next_word = False
            elif re.search('^ *, *[0-9]',middle_ground):
                next_word = False
            elif (ref_word in ['no.','no','nos','nos.']) or ((ref_word in ['no','nos']) and middle_ground.startswith('.')):
                next_word = False
            elif (ref_word == 'and') and next_vs and (next_vs > next_word.start()):
                next_word = False
            elif middle_ground.startswith('.') and (len(ref_word)>1) and next_vs and (next_vs > next_word.start()):
                next_word = False
            elif ((',' in middle_ground) or (';' in middle_ground)) and  next_vs and (next_vs > next_word.start()):
                next_word = False
            elif (',' in middle_ground) and not(OK_comma_precedes(ref_word)) \
              and (not((len(matches)>0) and OK_comma_follows(matches[-1].group(0).lower(),(matches[-1].group(0)[0])))):
                next_word = False
                ## multiple commas plus 'and' might be negatively effected, but this would require more look ahead and
                ## these are probably really "et al" cases                                                
            elif (not is_role) and ((last_word in citation_filler_words) and (',' in middle_ground)) or (';' in middle_ground):
                ## assume semi-colons are absolute borders
                next_word = False
            elif date_match and (next_word.start() > date_match.start()):
                next_word = False
            else:
                if not is_role:    
                    party_end = next_word.end()
                matches.append(next_word)
                if (len(matches)>0) and (next_word.end()<right_span) and (line[next_word.end()]==".") and \
                  (possible_abbrev(word_string) or ((len(line)> (next_word.end()+1)) and (line[next_word.end()+1] in ";,"))):
                    current_start = next_word.end()
                  ## not requiring capital for ., combo
                else:
                    current_start = next_word.end()
                if (current_start < right_span) and (line[current_start-1]=='-') and (re.search('^((17|18|19|20)[0-9][0-9])',line[current_start:])):
                    current_start = current_start+4
                    if not is_role:
                        party_end = party_end+4
                if is_role:
                    in_error = in_error_pattern.search(line,current_start)
                    if in_error and not(re.search('[^ ,]',line[current_start:in_error.start()])):
                        ref_word = ref_word+' '+in_error.group(1).lower()
                        current_start = in_error.end(1)
                last_word = ref_word
                next_word = pattern.search(line,current_start)
                if is_role and not (ref_word in roles):
                    roles.append(ref_word)
        else:
            next_word = False
    if roles:
        roles.sort()
    while (ok_to_delete_right_most_vs_item (matches)):
        matches.pop()
        if len(matches) > 0:
            if party_end == current_start:
                party_end = current_start=matches[-1].end()
            current_start=matches[-1].end()
            if (line[current_start-1]=='.') and (possible_abbrev(matches.group(0)) \
                                                 or ((len(line)>current_start+1) and (line[current_start] in ";,"))):
                current_start = current_start+1
                ## not requiring capital for ., combo
        else:
            current_start = start
    if current_start == start:
        current_start = 'Fail'
        party = False
    else:
        party = line[start:party_end].strip(' ')
    if party_end and current_start and isinstance(current_start,int) and (party_end > current_start):
        current_start = party_end
    return(current_start,roles,party)
    ## corporate endings (org_ending_words) can follow commas and be included in name
    ## latin_reference_words can signal that the name is over e.g., 
    ## I have only seen "supra" so far

    ## consecutive capitals can include certain lower case words 
    ## see:  not_uppercase_part_of_org_names

    ## ill-formed right context means no vs citation, e.g., if V is part of a section number in a book
    ## "See Plato, Republic, V, 461; Aristotle, Politics, VII, 1335b 25."

def really_initial_V_in_all_caps(line,match):
    if match:
        vs_anchor = re.compile('([^a-z])+(vs?[\. ]|against|versus)+([^a-z])*',re.I)
        second_vs = vs_anchor.search(line,match.end())
        if ('V' in match.group(0)) and (not re.search('[a-z]',line)) and second_vs:
            return(True)
        

def get_vs_citations(line,spans,offset,file_id,citation_dictionary,one_line_objects,line_number):
    ## if line follows one_line_objects, it is more likely to be a one line object
    vs_anchor = re.compile('([^a-z])+(vs?[\. ]|against|versus)+([^a-z])*',re.I)
    vs_anchor_lower = re.compile('([^a-zA-Z])+(vs?[\. ]|against|versus)+([^a-zA-Z])*')
    vs_anchor2 = re.compile('([A-Z])+(vs?\.?|against|versus)[A-Z]')
    ## vs_anchor2 only applies at the beginning of a file when allcaps might be used
    year_pattern = re.compile('^,? *\(((18|19|20)[0-9][0-9])\)')
    court_year_pattern = re.compile('^ *\(([CD]\. *C\.( *A\.)?) *((18|19|20)[0-9][0-9])?\)')
    match = vs_anchor.search(line)
    if really_initial_V_in_all_caps(line,match):
        match = vs_anchor.search(line,match.end())
    if not match:
        match = vs_anchor2.search(line)
        pattern2 = True
    elif match and ('V' in match.group(0)):
        match2 = vs_anchor_lower.search(line)
        if match2:
            match = match2
        pattern2 = False
    else:
        pattern2 = False
    output = []
    end_border = False
    end_border = False
    left_span = 0
    extended_left_start = False
    while match:
        ## find preceding and following spans
        right_span = len(line)
        for start,end in spans:
            start = start-offset
            end = end-offset
            if end_border and (end_border != 'Fail') and (end_border>end):
                end=end_border
            if (end> left_span) and (end < match.start()):
                left_span = end
            if (start < right_span) and (start > match.end()):
                right_span = start
        if pattern2:
            if "," in match.group(0):
                paren_comma = True
            else:
                paren_comma = False
            start_border,roles1,party1,extended_left_start = find_left_vs_border(line,match.start(2),left_span,one_line_objects,paren_comma,line_number)
            end_border,roles2,party2 = find_right_vs_border(line,match.end(2),right_span)
        else:
            if "," in match.group(0):
                paren_comma = True
            else:
                paren_comma = False
            start_border,roles1,party1,extended_left_start = find_left_vs_border(line,match.start(2),left_span,one_line_objects,paren_comma,line_number)
            end_border,roles2,party2 = find_right_vs_border(line,match.end(),right_span)
        if (start_border != 'Fail') and (end_border != 'Fail'):
            out = {'start':start_border+offset,'end':end_border+offset,'string':line[start_border:end_border],'extended_left_start':extended_left_start}
            out['vs_anchor']=match.group(2).strip(' ')
            add_citation_id(out,file_id,citation_dictionary)
            if party1:
                out['party1']=party1
            if party2:
                out['party2']=party2
            if len(roles1)>0:
                role_string = roles1[0]
                for role in roles1[1:]:
                    role_string = role_string+', '+role
                out['party1_role']=role_string
            if len(roles2)>0:
                role_string = roles2[0]
                for role in roles2[1:]:
                    role_string = role_string+', '+role
                out['party2_role']=role_string
            year_match = year_pattern.search(line[end_border:])
            if year_match:
                out['end']=out['end']+year_match.end()
                out['string']=line[start_border:(end_border+year_match.end())]
                out['year']=year_match.group(1)
            else:
                court_year_match = court_year_pattern.search(line[end_border:])
                if court_year_match:
                    out['court'] = court_year_match.group(1)
                    if court_year_match.group(3):
                        out['year'] = court_year_match.group(3)
            if ('party1' in out) and ('party2' in out):
                output.append(out)
        else:
            pass
        if end_border and (end_border != 'Fail') and (end_border>match.end()):
            match = vs_anchor.search(line,end_border)
            left_span = end_border
        else:
            match = vs_anchor.search(line,match.end())
        pattern2 = False
    return(output)
    
def non_initial_the(line,the_start,spans,offset):
    key_end = 0
    if spans and (len(spans) != 0):
        for start,end in spans:
            end = end-offset
            if (end < the_start) and (end > key_end):
                key_end = end
    if (key_end == 0):
        if re.search('\.[^\. ]*$',line[key_end:the_start]):
        ## This instance of 'The' is non-initial if
        ## it is preceded by some period '.'
        ## and there are non-periods/non-spaces between it and the closest preceding period
            return(True)
        else:
            return(False)
    elif (not '.' in line[key_end:the_start]) or re.search('\.[^\. ]*$',line[key_end:the_start]):
        ### This instance of 'The' is non-initial if there are no periods between
        ### the end of the last object and this instance of 'The', or if
        ### there is at least one non-period/non-space since the last period
        return(True)
    else:
        return(False)

def satisfies_the_case_constraints(case_string):
    case_string = case_string.lower()
    ## print(case_string)
    if re.search('(court)|(agreement)',case_string):
        return(False)
    elif re.search('^the *united *states( *of *america)? *$',case_string):
        return(False)
    else:
        return(True)

def edit_end_of_other_case_citations(line,start,end):
    last_word = re.search(' *([^ ]+) *$',line[:end])
    number_pattern = re.compile('[0-9]+(, [0-9]+)*( +and +[0-9]+)?',re.I)
    number_key_pattern = re.compile('(amendment|rule)?',re.I)
    while last_word:
        ref_word = last_word.group(0).strip(' .-,').lower()
        if ref_word in latin_reference_words + other_non_citation_legal_words + months + ['no']:
            end = last_word.start()
            if line[end]==' ':
                non_space = re.search('([^ ]) *$',line[:end])
                if non_space:
                    end = non_space.end(1)
            if start == end:
                return(end)
            else:
                last_word = re.search('[^ ]+ *$',line[:end])
        else:
            last_word = False
    if (end<len(line)) and line[end]==',':
        next_word = re.search('[^ ,\.]+',line[end:])
        if next_word and (next_word.group(0).lower() in org_ending_words+person_ending_words):
            end = end+next_word.end()
    if number_key_pattern.search(line[start:end]):
        number_match = number_pattern.search(line,end)
        if number_match and not re.search('[A-Za-z]',line[end:number_match.start()]):
            end = number_match.end()            
    if line[end-1] in '.,: ':
        end=end-1
    return(end)

def possibly_extend_other_case_end(rest_of_line):
    if re.search(';',rest_of_line):
        return(False)
    word_pattern = re.compile('[A-Za-z0-9]+')
    start = 0
    match = word_pattern.search(rest_of_line)
    while match:
        ref_word = match.group(0).lower()
        if ref_word in latin_reference_words+other_non_citation_legal_words+months:
            return(False)
        if ref_word == 'no':
            return(False)
        elif ('.' in rest_of_line[start:match.start()]) and ((ref_word in POS_dict) and (not ref_word in standard_words_with_periods_in_citations)):
            return(False)
        else:
            start = match.end()
            match = word_pattern.search(rest_of_line,start)
    return(start)
            
def no_other_significant_words(instring):
    instring = instring.lower()
    special_word = False
    other_words = ['ex','parte','the','matter','application','claim','estate','ex','parte','petitioner','claimant','s',\
                   'matters','applications','claims','estates','petitioners','claimants']
    other_words.extend(prepositions)
    for word in re.split('[^a-zA-Z0-9]',instring):
        if special_word or (word in other_words) or (len(word)<4):
            pass
        else:
            special_word = True
    if special_word:
        return(False)
    else:
        return(True)

def other_case_citation_OK(entry):
    if ('name' in entry) and entry['name']:
        ## entry name must be a string
        case_name = entry['name'].lower()
        words = []
        for word in case_name.split(' '):
            if (word not in ['ex','parte','case','in','re','the','matter','of']) and \
                (word not in person_ending_words+org_ending_words):
                words.append(word)
        if len(words)>0:
            return(True)

def get_other_case_citations(line,spans,offset,file_id,citation_dictionary,one_line_objects):
    ### new patterns
    pre_cap_noun = '(((Ex [Pp]arte)|(The)|(In [Rr]e)|((In )?(the )?[mM]atter of( the)?)|(Application of)|(Claims of)|Estate of|(EX PARTE)|(THE)|(IN RE)|((IN )?(THE )?MATTER OF)|(APPLICATION OF)|(CLAIMS OF)|ESTATE OF)((( +[\'"]?[A-Z][\&A-Za-z-—\./]*)( of)?(( +[\'"]?[\&A-Z][\&A-Za-z-—\./]*,?[\'"]?){0,3})[\'"]?)|(( [\'"]?[A-Z-—]+)(( +\'[\&A-Z-—\./]+,?[\'"]?){0,3}))))' 
    post_cap_noun = '(([0-9]{1,3} )?((([A-Z][\&A-Za-z-—]*(\'[Ss])? ){1,4})|(([\&A-Z-—]+ ){1,10}))((Cases?)|(CASES?)))'
    petitioner_pattern = '((Re|RE)((( +[\'"]?[A-Z][\&A-Za-z-—\.]*)(( +[A-Z][\&A-Za-z-—\.]*){0,3})[\'"]?)|(( [\'"]?[A-Z-—]+)(( +[\&A-Z-\.]+){0,3}[\'"]?)))(, *)(Petitioners?|PETITIONERS?|Claimants?|CLAIMANTS?))'
    possessive_pattern = '((^| +)([A-Z][A-Za-z]*\'[Ss] +[A-Za-z\&]+)(( *$)|\.))' ## must end line or be followed by a period
    other_citation_pattern = re.compile(pre_cap_noun+'|'+post_cap_noun+'|'+petitioner_pattern+'|'+possessive_pattern)
    ## group 47 matches petitioner
    ## other group numbers are also fixed -- need to modify code if
    ## regex for other_citation_pattern is modified
    short_all_caps_line = re.compile('^ *(([A-Z]+)(( [A-Z\.]+){0,3})) *$')
    court_year_pattern = re.compile('^ *\(([CD]\. *C\.( *A\.)?) *((18|19|20)[0-9][0-9])?\)')
    extra_petitioner_pattern = re.compile(',? *(Petitioners?|PETITIONERS?|Claimants?|CLAIMANTS?)')
    all_caps_match = False
    ### change this so that we only search in between spans
    ### editing afterwards loses some instances
    last_span = False
    search_spans = []
    if not spans:
        search_spans = [[0,len(line)]]
    for span in spans:
        if not last_span:
            start = 0
        else:
            start = last_span[1]-offset
        end = span[0]-offset
        search_spans.append([start,end])
        last_span = span
    if last_span:
        start = last_span[1]-offset
        search_spans.append([start,len(line)])
    output = []
    for span_start,span_end in search_spans:
        match = other_citation_pattern.search(line[:span_end],span_start)
        if not match:
            match = short_all_caps_line.search(line[:span_end],span_start)
            if match and one_line_objects and member_if_attribute(one_line_objects,'entry_type','standard_case'):
                all_caps_match = True
            else:
                match = False
                all_caps_match = False
        while match:
            court = False
            year = False
            party1 = False
            party1_role = False
            start = match.start()
            end = match.end()
            end = edit_end_of_other_case_citations(line[:span_end],start,end)
            start_boost = re.search('[^ ]',line[start:])
            if start_boost:
                start = start+start_boost.start()
            if end-start<5:
                match = False
            if not match:
                pass
            elif (not all_caps_match) and match.group(2) and ((match.group(2).lower() !='the') or satisfies_the_case_constraints(match.group(0))):
                if start == end:
                    match = False
                if match:
                    ## these group numbers are sensitive to changes
                    ## in the above regexs
                    if no_other_significant_words(match.group(0)):
                        match = False
                        petitioner_match = False
                        extended_match = False
                    else:
                        case_name = line[start:end]
                        extended_match = court_year_pattern.search(line[end:span_end])
                        petitioner_match = extra_petitioner_pattern.search(line[end:span_end])
                else:
                    extended_match = False
                    petitioner_match = False
                if match and petitioner_match:
                    if petitioner_match.end() == end:
                        pass
                    else:
                        extend_end = possibly_extend_other_case_end(line[end:end+petitioner_match.start()])
                        if extend_end:
                            end = end + extend_end
                        elif not re.search('[A-Za-z0-9]',line[end:end+petitioner_match.start()]):
                            pass
                        else:
                            petitioner_match = False
                    if petitioner_match:
                        party1_role = petitioner_match.group(1)
                        party1 = line[match.start(20):end]  ##
                        case_name = line[start:end]
                        end = end+(petitioner_match.end()-petitioner_match.start())
                if match and not petitioner_match:
                    petitioner_match = extra_petitioner_pattern.search(match.group(0))
                    if petitioner_match and not re.search('[A-Za-z0-9]',match.group(0)[petitioner_match.end():]):
                        party1_role = petitioner_match.group(0)
                        party1 = line[match.start(20):start+petitioner_match.start()].strip(' ')
                        case_name = line[start:start+petitioner_match.start()]
                if extended_match:
                    court = extended_match.group(1)
                    if extended_match.group(3):
                        year = extended_match.group(3)
                    end = end+extended_match.end()
                if match and match.group(2) and (match.group(2).lower()=='the'):
                    if (not extended_match) and (not non_initial_the(line,match.start(),spans,offset)) and (not one_line_objects):
                        match = False
                    ## + offset
                ## 'year'
                ## 'court'
                ## 'end'
                ## additional conditions on 'The' cases (group(2) = 'The')
                if match:
                    ## print(1,match.group(0))
                    out = {'start': start+offset, 'end': end+offset,'string':line[start:end],'name':case_name}
                    if court:
                        out['court'] = court
                    if year:
                        out['year'] = year
                    if party1:
                        out['party1']=party1
                    if party1_role:
                        out['party1_role']=party1_role
                    if other_case_citation_OK(out):
                        add_citation_id(out,file_id,citation_dictionary)
                        output.append(out)
            elif (not all_caps_match) and  match.group(53) and (len(match.group(53))>0):
                start = match.start()
                end = match.end()
                if start !=end:
                    case_name = line[start:match.start(52)]
                    party1_role = match.group(53)
                    party1 = match.group(43)
                    out = {'start': start+offset, 'end': end+offset,'string':line[start:end],'name':case_name,'party1':party1,'party1_role':party1_role}
                    if other_case_citation_OK(out):
                        add_citation_id(out,file_id,citation_dictionary)
                        output.append(out)
                else: 
                    match = False
            elif all_caps_match:
                start = match.start()
                end = match.end()
                if start !=end:
                   case_name = match.group(1)
                   out = {'start': start+offset, 'end': end+offset,'string':line[start:end],'name':case_name}
                   if other_case_citation_OK(out):
                       add_citation_id(out,file_id,citation_dictionary)
                       output.append(out)
                else:
                    match = False
            elif match.group(30):
                case_name = match.group(0)
                out = {'start': start+offset, 'end': end+offset,'string':line[start:end],'name':case_name}
                if other_case_citation_OK(out):
                    add_citation_id(out,file_id,citation_dictionary)
                    output.append(out)
            elif match.group(54):
                case_name = match.group(56)
                start = match.start(56)
                end = match.end(56)
                out = {'start': start+offset, 'end': end+offset,'string':case_name,'name':case_name}
                if other_case_citation_OK(out):
                    add_citation_id(out,file_id,citation_dictionary)
                    output.append(out)
            else:
                extended_match = False
                petitioner_match = False
            if end:
                match = other_citation_pattern.search(line[:span_end],end)
    return(output)
    
def fill_dictionary_from_xml(all_text,previous_info_fields,previous_info_dictionary):
    ## currently only gets functional values -- if info is repeated, last value is kept
    ## currently assumes no embeddings
    ## currently only gets simple values (between start and end xml)
    ## more elaborate to get other stuff
    xml_pattern = re.compile('<([^>]+)>')
    unary_pattern = re.compile('/$')
    end_pattern = re.compile('^/')
    key = re.compile('^[^> /]+')
    start = 0
    match = xml_pattern.search(all_text)
    while match:
        interior = match.group(1)
        if unary_pattern.search(interior):
            ## current version does not use these
            pass
        elif end_pattern.search(interior):
            end_key_match = key.search(interior[1:])
            if (key_match.group(0) in previous_info_fields) and (end_key_match.group(0) == key_match.group(0)):
                value = all_text[start_end:match.start()]
                previous_info_dictionary[key_match.group(0)]=value
        else:
            key_match = key.search(interior)
            start_end = match.end()
        start = match.end()
        match = xml_pattern.search(all_text,start)

def word_overlap(string1,string2):
    set_1 = re.split('[^a-z]',string1.lower())
    set_2 = re.split('[^a-z]',string2.lower())
    for word in set_1:
        if word in set_2:
            return(True)

def OK_vs_filter(citation,previous_info_dictionary):
    simple_vs_pattern = re.compile('^ *(.*) *(vs?\.?|against) *(.*)$')
    string = citation['string']
    if 'vs_anchor' in citation:
        vs_anchor = citation['vs_anchor']
    else:
        vs_anchor = False
    if 'party1' in citation:
        party1 = citation['party1']
    else:
        party1 = False
    if 'party2' in citation:
        party2 = citation['party2']
    else:
        party2 = False
    if vs_anchor in ['V','V.']:
        if string.isupper() and party1 and party2 and ('citation_case_name' in previous_info_dictionary):
            match = simple_vs_pattern.search(previous_info_dictionary['citation_case_name'])
            if match:
                dictionary_party1 = match.group(1)
                dictionary_party2 = match.group(3)
            else:
                dictionary_party1 = False
                dictionary_party2 = False
            if dictionary_party1 and dictionary_party2 and word_overlap(party1,dictionary_party1) and word_overlap(party2,dictionary_party2):
                return(True)
            else:
                return(False)
        else:
            ## capital V can only be used for all uppercase, otherwise it is an initial
            return(False)
    elif vs_anchor.lower() == 'against':
        if ('party1_role' in citation) and ('party2_role' in citation):
            return(True)
        else:
            return(False)
    else:
        return(True)

def edit_vs_citations(out3,previous_info_dictionary):
    output = []
    for out in out3:
        if OK_vs_filter(out,previous_info_dictionary):
            output.append(out)
    return(output)

def merge_relational_entries(word,entry):
    if len(entry)==1:
        return(entry[0])
    if len(entry)>2:
        print('Too many classes for',word+':',entry)
        return(entry[0])
    elif ('RANK' in entry) and ('PROFESSIONAL' in entry):
        return('PROFESSIONAL_OR_RANK')
    else:
        print('Unexpected class combo for',word+':',entry)
        return(entry[0])
        

def next_word_is_sentence_likely_starter(rest_of_line):
    pattern = re.compile('[a-z\'\-&/\[\]]+',re.I) ## allow words to contain intermediate hyphens and apostrophes
    rest_of_line = rest_of_line.lstrip(' ')
    if len(rest_of_line)<1:
        pass
    elif rest_of_line[0].isupper():
        match = pattern.search(rest_of_line)
        if match:
            word = match.group(0)
            if word.lower() in POS_dict:
                for POS in POS_dict[word.lower()]:
                    if POS in ['ORDINAL', 'CARDINAL', 'WORD','PRONOUN', 'QUANT', 'AUX', 'DET', 'SCOPE']:
                        return(True)

def end_of_sentence_heuristic (word,line,next_position):
    end_of_sent_pattern = re.search('^ *[.?!]',line[next_position:])
    if end_of_sent_pattern:
        rest_of_line = line[next_position+len(end_of_sent_pattern.group(0)):]
    if end_of_sent_pattern and not (possible_abbrev(word)):        
        if next_word_is_sentence_likely_starter(rest_of_line):
            return(True)
        elif re.search('^ *[a-z]',rest_of_line):
            ## if the next word is lowercase, it is not the end of the sentence
            return(False)
            ## if beginning of next sentence is uppercase word and member of a list of likely sentence beginnings
            ## it is likely to be a sentence boundary
        elif next_word_is_sentence_likely_starter(rest_of_line):
            return(True)
        elif possible_abbrev(word):
            ## if the word is a possible abbrevation, this may not be the end of the sentence
            return(False)
        else:
            return(True)
    elif end_of_sent_pattern and rest_of_line and next_word_is_sentence_likely_starter(rest_of_line):
        return(True)
    else:
        return(False)


def start_sentence_heuristic(word,line,start):
    if start == 0:
        return(True)
    previous_word_match = re.search('([A-Za-z0-9]+)[^A-Za-z0-9]*$',line[:start])
    if not previous_word_match:
        return(True)
    elif end_of_sentence_heuristic(previous_word_match.group(1),line[previous_word_match.end(1):],0):
        return(True)
    else:
        return(False)

def reprocess_role_phrase(line,start,end,offset,in_or_out):
    word_pattern = re.compile('[1-4]?[A-Z-]+',re.I)
    match = word_pattern.search(line,start)
    so_far = start
    sequence = []
    out = {}
    words = []
    while match and (so_far < end):
        word = match.group(0)
        if len(sequence)==0:
            out['start']=match.start()+offset
        if word.lower() in relational_dict:
            sequence.append(merge_relational_entries(word.lower(),relational_dict[word.lower()]))
            words.append(word)
            so_far = match.end()
        elif word.lower() in not_uppercase_part_of_org_names:
            sequence.append('FILLER')
            words.append(word)
            so_far = match.end()
        elif (match.end()+1<len(line)) and (line[match.end()+1]=='.') and ((word.lower()+'.') in relational_dict):
            sequence.append(merge_relational_entries(word.lower()+'.',relational_dict[word.lower()+'.']))
            words.append(word)
            so_far = match.end()+1
        elif word.lower() in time_dict:
            sequence.append('TIME_NAME')
            words.append(word)
            so_far = match.end()
        elif (match.end()+1<len(line)) and (line[match.end()+1]=='.') and ((word.lower()+'.') in time_dict):
            sequence.append('TIME_NAME')
            words.append(word)
            so_far = match.end()+1
        elif capitalized_word(word):
            sequence.append('CAPITALIZED_WORD')
            words.append(word)
            if ((match.end()+1<len(line)) and (line[match.end()+1]=='.')  and (possible_abbrev(word))) \
               or ((match.end()+2<len(line)) and (line[match.end()+1]=='.') and (line[match.end()+2] in ';,')):
                so_far = match.end()+1
            else:
                so_far = match.end()
            add_on = True
        else:
            sequence.append('Filler')
            words.append(word)
            so_far = match.end()
        match = word_pattern.search(line,so_far)
        if match and (match.end()>end):
            match = False
    if not 'start' in out:
        return(False,False,False)
    if line[:so_far].endswith('-'):
        so_far = so_far-1
    out['end']=so_far+offset
    if in_or_out == 'internal':
        if ('FAMILY' in sequence) or ('LEGAL_ROLE' in sequence) or ('PROFESSIONAL' in sequence) or \
          ('PROFESSIONAL_OR_RANK' in sequence) or ('ORGANIZATION' in sequence) or \
          ('PLURAL_FAMILY' in sequence) or ('PLURAL_LEGAL_ROLE' in sequence) or ('PLURAL_PROFESSIONAL' in sequence)\
          or ('PLURAL_ORGANIZATION' in sequence):
            return(out,sequence,words)
        else:
            return(False,False,False)            
    else:
        return(out,sequence,words)

def trim_right_edge_of_role_phrase(out,sequences,offset,words,line):
    if (not sequences) or (len(sequences)<1):
        return(False,False,False,False)
    new_out = out.copy()
    new_sequences = sequences[:]
    new_words = words[:]
    done = False
    while (len(new_sequences)>0) and not done:
        if new_sequences[-1] in ['FAMILY','PLURAL_FAMILY','LEGAL_ROLE','PLURAL_LEGAL_ROLE',\
                                 'PROFESSIONAL','PLURAL_PROFESSIONAL','PROFESSIONAL_OR_RANK',\
                                 'PLURAL_ORGANIZATION','ORGANIZATION']:
            done = True
        elif new_sequences[-1] in ['CAPITALIZED_WORD']:
            ### may want to refine this
            done = True
        elif sequences[-1] in ['FILLER','TIME_NAME']:
            new_sequences.pop()
            new_words.pop()
        else:
            done = True
    if new_sequences == sequences:
        return(False,False,False,False)
    elif len(new_sequences) == 0:
        return(False,False,True,False)
    else:
        string_approx = ''
        for index in range(len(new_words)):
            word = new_words[index]
            if index<(len(new_words)-1):
                string_approx = string_approx+word+'(?:[^a-zA-Z]+)'
            else:
                string_approx = string_approx+word
        string_pattern = re.compile(string_approx)
        string_match = string_pattern.search(line,(out['start']-offset))
        if string_match:
            new_out['end']=string_match.end()+offset
            return(new_out,new_sequences,False,new_words)
        else:
            return(False,False,False,False)

def unprefixed_word(word):
    prefix_pattern = re.compile('^(p?re|un|anti|co|de|post|ex|extra|fore|non|over|pro|super|tri|bi|uni|ultra)')
    prefix_match = prefix_pattern.search(word)
    if prefix_match:
        return(word[prefix_match.end():])
    else:
        return(False)

def prefixed_non_name_word(word):
    unprefixed = unprefixed_word(word)
    if unprefixed and (unprefixed in POS_dict) and (not ('PERSONNAME' in POS_dict[unprefixed]) or ('GPE' in POS_dict[unprefixed])):
        return(True)

def name_word(word):
    lower = word.lower()
    if lower in POS_dict:
        if ('PERSONNAME' in POS_dict[lower]) or ('GPE' in POS_dict[lower]):
            return(True)
        else:
            return(False)
    elif prefixed_non_name_word(lower):
        return(False)
    elif possible_abbrev(word):
        return(False)
    elif word.istitle():
        return(True)
    else:
        return(False)

def one_word_restriction(sequence,words):
    if (len(sequence)==1) and (sequence[0] in ['CAPITALIZED_WORD']) and (not name_word(words[0])):
        return(True)

def ok_role_phrase2(out,sequence,spans,string,line,offset):
    ## 1st check if it overlaps with any spans
    new_items = []
    if ((out['end']-out['start']) <2) or ([out['start'],out['end']] in spans):
        ## do not allow completely duplicate spans
        return(False,False)
    for span_start,span_end in spans:
        if (out['start']>=span_start):
            if out['end'] <=span_end:
                ## if it is totally inside of a span, it is only OK if it can be one of our select name types
                if (('FAMILY' in sequence) or ('LEGAL_ROLE' in sequence) or ('PROFESSIONAL' in sequence) or \
                  ('PROFESSIONAL_OR_RANK' in sequence) or ('PLURAL_FAMILY' in sequence) or \
                  ('PLURAL_LEGAL_ROLE' in sequence) or ('PLURAL_PROFESSIONAL' in sequence) or \
                  ('ORGANIZATION' in sequence) or ('PLURAL_ORGANIZATION' in sequence)):
                    return(False,True)
                else:
                    return(False,False)
            elif out['start']<span_end:
                ## overlap case 1 -- start of item is "part" of existing span
                new_phrase1,new_sequence1,words1=reprocess_role_phrase(line,out['start']-offset,span_end-offset,offset,'internal')
                new_phrase2,new_sequence2,words2=reprocess_role_phrase(line,span_end-offset,out['end']-offset,offset,'external')
                if new_phrase2:
                    new_phrase2a,new_sequence2a,fail,words2a=trim_right_edge_of_role_phrase(new_phrase2,new_sequence2,offset,words2,line)
                    if fail:
                        new_phrase2 = False
                    elif new_phrase2a:
                        new_phrase = new_phrase2a
                        new_sequence2=new_sequence2a
                        words2 = words2a
                output = []
                if new_phrase1 and (not one_word_restriction(new_sequence1,words1)):
                    output.append([new_phrase1,new_sequence1,words1])
                if new_phrase2 and (not one_word_restriction(new_sequence2,words2)):
                    output.append([new_phrase2,new_sequence2,words2])
                if (len(output)>0):
                    return(output,False)
                else:
                    return(False,False)
            else:
                ## no overlap
                pass
        elif (out['end']<=span_end) and (out['end']>span_start):
            ## overlap case 2 -- end of item is "part" of existing span
            new_phrase1,new_sequence1,words1=reprocess_role_phrase(line,out['start']-offset,span_start-offset,offset,'external')
            new_phrase2,new_sequence2,words2=reprocess_role_phrase(line,span_start-offset,out['end']-offset,offset,'internal')
            if new_phrase1:
                new_phrase1a,new_sequence1a,fail,words1a=trim_right_edge_of_role_phrase(new_phrase1,new_sequence1,offset,words1,line)
                if fail:
                    new_phase1 = False
                elif new_phrase1a:
                    new_phrase1 = new_phrase1a
                    new_sequence1=new_sequence1a
                    words1=words1a
            output = []
            if new_phrase1 and (not one_word_restriction(new_sequence1,words1)):
                output.append([new_phrase1,new_sequence1,words1])
            if new_phrase2 and (not one_word_restriction(new_sequence2,words2)):
                output.append([new_phrase2,new_sequence2,words2])
            if len(output)>0:
                return(output,False)
            else:
                return(False,False)
        elif (out['start']<=span_start) and (out['end']>=span_end):
            ## what if an existing span is part of a proposed name
            new_phrase1,new_sequence1,words1=reprocess_role_phrase(line,out['start']-offset,span_start-offset,offset,'external')
            new_phrase2,new_sequence2,words2=reprocess_role_phrase(line,span_end-offset,out['end']-offset,offset,'external')
            if new_phrase1:
                new_phrase1a,new_sequence1a,fail,words1a=trim_right_edge_of_role_phrase(new_phrase1,new_sequence1,offset,words1,line)
                if fail:
                    new_phase1 = False
                elif new_phrase1a:
                    new_phrase1 = new_phrase1a
                    new_sequence1=new_sequence1a
                    words1=words1a
            output = []
            if new_phrase1 and (not one_word_restriction(new_sequence1,words1)):
                output.append([new_phrase1,new_sequence1,words1])
            if new_phrase2 and (not one_word_restriction(new_sequence2,words2)):
                output.append([new_phrase2,new_sequence2,words2])
            if len(output)>0:
                return(output,False)
            else:
                return(False,False)
    return(False,True)

def possibly_split_role_phrase(out,sequence,offset,words,line):
    triples = [] ## new sequences of out,sequence,words
    infixed_role_position = False
    index = 0
    if len(sequence) == 0:
        return(False)
    elif (sequence[-1] in ['CAPITALIZED_WORD']):
        split_point = False
        index = 0
        for num in range(1,len(sequence)+1):
            index = len(sequence)-num
            item = sequence[index]
            if (item in ['FAMILY','PLURAL_FAMILY','LEGAL_ROLE','PLURAL_LEGAL_ROLE',\
                        'PROFESSIONAL','PROFESSIONAL_OR_RANK','ORGANIZATION']) and \
                        (sequence[index+1] in ['CAPITALIZED_WORD']):
                        ## plural_professional ignored for now (caused some errors)
                if ((index==0) or (not sequence[index-1] in ['CAPITALIZED_WORD'])):
                    split_point = index+1
                elif sequence[index-1] in ['CAPITALIZED_WORD']:
                    infixed_role_position = index
                    out['name_with_infixed_role'] = True
                break
        if split_point:
            seq1 = sequence[:split_point:]
            seq2 = sequence[split_point:]
            words1 = words[:split_point]
            words2 = words[split_point:]
            string_approx = ''
            for word in words1:
                string_approx = string_approx+escape_operator_characters(word)+'([^a-zA-Z]*)'
            match = re.search(string_approx,line[out['start']-offset:out['end']-offset])
            if not match:
                ## these are not likely to be correct, e.g., these cases have lots of
                ## intervening punctuation
                # print('error',out,sequence,offset,words,line,sep=os.linesep)
                # input(' ')
                return(False)
            else:
                end1 = out['start']+match.start(len(words1))
                ## end the first phrase at the beginning of the space between the last
                ## word in word1 and the first word in words2
                start2 = out['start']+match.end(len(words1))
                ## start the 2nd phrase at the end of this same space
                out1={'start':out['start'],'end':end1}
                out2={'start':start2,'end':out['end']}
                return([[out1,seq1,words1],[out2,seq2,words2]])
        elif infixed_role_position:
            # print(1,len(words))
            # print(2,infixed_role_position)
            # print(3,words)
            # print(4,sequence)
            infixed_seq = sequence[:infixed_role_position]
            infixed_words = words[:infixed_role_position]
            string_approx = ''
            for word in words[:infixed_role_position]:
                string_approx = string_approx+escape_operator_characters(word)+'([^a-zA-Z]*)'
            match = re.search(string_approx,line[out['start']-offset:out['end']-offset])
            if not match:
                return(False)
            else:
                start1 = out['start']+match.end(index)
                string_approx = string_approx+escape_operator_characters(infixed_words[0])
                match = re.search(string_approx,line[out['start']-offset:out['end']-offset])
                if not match:
                    return(False)
                else:
                    end1 = out['start']+len(match.group(0))
                    out1 = {'start':start1,'end':end1}
                    return([[out,sequence,words],[out1,infixed_seq,infixed_words]])
        else:
            return(False)
    elif (sequence[-1] in ['RANK']) and (not ('PROFESSION' in sequence)) and (not ('PROFESSIONAL_OR_RANK' in sequence)):
        new_end = re.search(' *'+words[-1],line[:out['end']],re.I).start()
        out['end']=new_end
        sequence = sequence[:-1]
        words = words[:-1]
        return([[out,sequence,words],[False,False,False]])
    else:
        return(False)

def check_items_in_list(items_to_check,big_list):
    for item in items_to_check:
        if item in big_list:
            return(True)
    else:
        return(False)

def really_ambigous_name_word(lower,word,start_sentence):
    ## applies only to one word cases
    entry = []
    if lower in POS_dict:
        entry.extend(POS_dict[lower])
    if lower in relational_dict:
        entry.extend(relational_dict[lower])
    if (lower in pre_citation_words) or (lower in topic_matter_words) or (lower in citation_closed_class):
        return(True)
    elif check_items_in_list(['DISCOURSE','NATIONALITY','TITLE','ORDINAL', 'CARDINAL', 'WORD','PRONOUN', 'QUANT', 'AUX', 'DET', 'SCOPE'],entry):
        return(True)
    elif start_sentence and word.istitle() and name_word(word):
        for classification in entry:
            if not classification in ['FIRSTNAME','GPE','PERSONNAME','ORG']:
                return(True)
    return(False)

def ok_role_phrase(out,sequence,spans,string,line,offset,words):
    
    if ('sentence_start' in out) and out['sentence_start']:
        start_sentence = True
    else:
        start_sentence = False
    if not out:
        return(False,False)
    triples=possibly_split_role_phrase(out,sequence,offset,words,line)
    if triples:
        new_triples = []
        for new_out,new_sequence,new_words in triples:
            new_out2,new_sequence2,fail,new_words2=trim_right_edge_of_role_phrase(new_out,new_sequence,offset,new_words,line)
            if fail:
                pass
            elif new_out2:
                new_triples.append([new_out2,new_sequence2,new_words2])
            else:
                new_triples.append([new_out,new_sequence,new_words])
        if len(new_triples)>0:
            triples = new_triples[:]
    elif (len(sequence) == 1) and (sequence[0] in ['CAPITALIZED_WORD']) and (not name_word(words[0])):
        ## possibly add to list of unsuitable cases
        ## print('OUT1:',1)
        return(False,False)
    elif (len(sequence) ==1) and really_ambigous_name_word(words[0].lower(),words[0],start_sentence):
        if words[0].lower() in one_word_person_names:
            ## keep only if previously used as a party in a case
            return(False,True) 
        else:
            return(False,False)
    else:
        new_out,new_sequence,fail,new_words=trim_right_edge_of_role_phrase(out,sequence,offset,words,line)
        if new_out:
            triples = possibly_split_role_phrase(new_out,new_sequence,offset,new_words,line)
    if fail:
        ## print('OUT1:',2)
        return(False,False)
    elif triples and (len(triples)>0):
        new_phrases = []
        new_word_sequences = []
        good = False
        for new_out2,new_sequence2,new_words2 in triples:
            if new_out2:
                new_phrases2,good = ok_role_phrase2(new_out2,new_sequence2,spans,line[new_out2['start']-offset:new_out2['end']-offset],line,offset)
                if good:
                    new_phrases.append([new_out2,new_sequence2,new_words2])
                elif new_phrases2:
                    new_phrases.extend(new_phrases2)
    elif new_out:
        new_phrases,good = ok_role_phrase2(new_out,new_sequence,spans,string,line,offset)
    else:
        new_phrases,good = ok_role_phrase2(out,sequence,spans,string,line,offset)
    if new_phrases and (len(new_phrases)>0):
        return(new_phrases,False)
    elif new_out:
        if good:
            return([[new_out,new_sequence,new_words]],False)
        else:
            ## print('OUT1:',5)
            return(False,False)
    else:
        ## print('OUT1:',6)
        return(new_phrases,good)
    
def OK_family_pattern(sequence,words):
    if 'FAMILY' in sequence:
        position = sequence.index('FAMILY')
    else:
        position = sequence.index('PLURAL_FAMILY')
    before = words[:position]
    after = words[position+1:]
    if len(words) == 1:
        return(True)
    elif len(before)>0 and ((before[-1].lower() in ['his','her','my','your','their','our']) \
                          or (before[-1].lower().endswith('\'s')) or (before[-1].lower().endswith('s\''))):
        return(True)
    if ('of' in after):
        position2 = after.index('of')
    elif ('OF' in after):
        position2 = after.index('OF')
    else:
        return(False)
    position = position + position2
    ### possibility for stronger or weaker requirement
    if 'PERSONNAME' in sequence[position:]:
        return(True)
    else:
        return(False)

def find_unambig_person(words):
    OK = False
    BAD = False
    for word in words:
        word = word.lower()
        if (word in POS_dict):
            entry = POS_dict[word]
            for item in entry:
                if item in ['FIRSTNAME']:
                    OK =True
                elif item in ['PERSONNAME']:
                    pass
                else:
                    BAD = True
        elif not re.search('^[a-z\.]+$',word):
            BAD = True
    if (OK and (not BAD)):
        ## print(words)
        return(True)
    else:
        return(False)
                    
    
def person_pattern(sequence,words):
    if ('Filler' in sequence) or (len(words) < 1) or (len(sequence)< 1) or ('&' in words):
        return(False)
    elif (words[-1].lower() in person_ending_words) and (len(words) > 2) and (len(words) <= 5):
        return(True)
    elif (sequence.count('INITIAL') == 1) and  (sequence[-1] != 'INITIAL') and (len(words) > 1) and (len(words)<=3):
        return(True)
    elif 'INITIAL' in sequence:
        return(False)
    elif (words[0].lower() in POS_dict) and ('TITLE' in (POS_dict[words[0].lower()])) and (len(words) > 1) and (len(words) <= 5):
        return(True)
    elif (len(sequence) > 1) and (len(sequence)<=3) and (('PERSONNAME' in sequence) or find_unambig_person(words)):
        return(True)
    else:
        return(False)


def find_phrase_type_from_sequence(sequence,words):
    ### need to include word sequences as argument
    ## print(sequence,words)
    if len(sequence) != len(words):
        print('Bad input for find_phrase_type_from_sequence')
        print(sequence)
        print(words)
    if 'LEGISLATIVE' in sequence:
        return('NAME',False)
    elif 'LEGAL_ROLE' in sequence:
        return('LEGAL_ROLE',False)
    elif 'ORGANIZATION' in sequence:
        return('ORGANIZATION', False)
    elif 'PLURAL_ORGANIZATION' in sequence:
        return('ORGANIZATION', True)
    elif 'PROFESSIONAL' in sequence:
        return('PROFESSION',False)
    elif 'PROFESSIONAL_OR_RANK' in sequence:
        return('PROFESSION',False)
    elif ('FAMILY' in sequence) and OK_family_pattern(sequence,words):
        return('FAMILY',False)
    if 'PLURAL_LEGAL_ROLE' in sequence:
        return('LEGAL_ROLE',True)
    elif 'PLURAL_PROFESSIONAL' in sequence:
        return('PROFESSION',True)
    elif ('PLURAL_FAMILY' in sequence) and OK_family_pattern(sequence,words):
        ## ** 57 
        return('FAMILY',True)
    elif person_pattern(sequence,words):
        return('PERSON',True)
    elif 'CAPITALIZED_WORD' in sequence:
        return('NAME',False)
    elif 'TIME_NAME' in sequence:
        return('DATE',True)
    else:
        return(False,False)

def ok_non_vocab_word_start_sequence(word,start_sentence):
    if (word.lower() in not_uppercase_part_of_org_names):
        return(False)
    elif (word.lower() in POS_dict):
        keep = False
        toss = False
        confident_keep = False
        confident_toss = False
        if is_month.search(word.lower()):
            ## precedes other checks
            ## print('*',word)
            return(False)
        for POS in POS_dict[word.lower()]:
            if POS in ['NOUN','ADJECTIVE']:
                keep = True
            elif POS in ['ADVERB','ORDINAL', 'CARDINAL', 'PREP', 'WORD','PRONOUN', 'QUANT', \
                         'AUX', 'CCONJ', 'DET', 'ADVPART', 'SCOPE','SCONJ']:
                confident_toss = True
            elif POS in ['ADVERB', 'ORDINAL', 'CARDINAL', 'PREP', 'WORD', 'PRONOUN', 'SCONJ', 'QUANT', \
                         'AUX', 'CCONJ', 'DET', 'ADVPART', 'SCOPE','DISCOURSE','VERB']:
                toss = True
            elif (POS in ['PERSONNAME','GPE']) and word[0].isupper():
                confident_keep = True
            # elif (not start_sentence) and (POS in ['VERB']):
            #     ### possible random capitalized verb same as name
            #     ### less likely to be a problem if not at sentence beginning
            #     keep = True (not a good idea) 7/21/17 AM
        if confident_toss:
            result = False
        elif confident_keep:
            result = True
        else:
            result = keep and not toss
        return(result)
    else:
        return(True)

def object_within_spans(object,spans):
    if (not object) or (not spans):
        return(False)
    output = False
    for start,end in spans:
        if (object['start']>=start) and (object['end']<=end):
            output = True
    return(output)

def remove_extra_spaces(instring):
    return(re.sub(' +',' ',instring))

def check_entry(entry,check_list):
    found = False
    for item in check_list:
        if item in entry:
            found = True
    return(found)

def non_name(word):
    if word in POS_dict:
        for POSclass in POS_dict[word]:
            if POSclass not in ['PERSONNAME','GPE_word','ORG_word','NATIONALITY','LEGISLATIVE_word','FIRSTNAME','ORG','GPE']:
                return(True)

def person_test(string,has_title=False):
    if re.search('et\.? +al',string):
        et_al = True
    else:
        et_al = False
    word_list = string.split(' ')
    unperson = False
    person = False
    num = 0
    if len(word_list) == 1:
        single_word = True
    else:
        single_word = False
    for word in word_list:
        word_strip = word.strip('.')
        if (word in POS_dict) and ('PERSONNAME' in POS_dict[word]) and \
          (not check_entry(POS_dict[word],['GPE_word','ORG_word','NATIONALITY','LEGISLATIVE_word'])):
           if (not single_word) and (non_name(word) and (not (has_title or et_al))):
               pass
           else:
               person = True
        elif (word_strip in citation_filler_words) or (word_strip in person_ending_words):
            pass
        elif (word in POS_dict) and ('TITLE'in POS_dict[word]):
            if num == 0:
                person = True
                ## otherwise pass
        elif (word_strip in POS_dict) and ('TITLE'in POS_dict[word_strip]):
            pass
        elif (word_strip in relational_dict) and ('PROFESSIONAL' in relational_dict[word_strip]):
            pass
        elif (len(word) == 1) or (len(word_strip) ==1): ## initials
            pass
        elif word == 'and':
            pass
        else:
            unperson = True
    if person and not unperson:
        return(True)
    else:
        return(False)

def add_to_one_person_names(string):
    if string in one_word_person_names:
        one_word_person_names[string]+=1
    else:
        one_word_person_names[string]=1

def get_last_person_word(string):
    word_match = re.compile('([a-zA-Z]+)[^a-zA-Z]*$')
    last_word = word_match.search(string)
    while last_word: 
        word = last_word.group(1)
        if (word in POS_dict):
            if ('PERSONNAME' in POS_dict[word]):
                return(word)
            else:
                last_word = word_match.search(string[:last_word.start()])
        elif not word in relational_dict:
            return(word)
        else:
            last_word = word_match.search(string[:last_word.start()])
            
def split_phrase_record(record,file_id,dictionary):
    start = 0
    and_pattern = re.compile(' +and +',re.I)
    triples = []
    string_list  = []
    while (start< len(record['string'])):
        and_match = and_pattern.search(record['string'],start)
        if and_match:
            end = and_match.start()
            next_triple =[record['string'][start:end],start,end]
            string_list.append(next_triple[0])
            triples.append(next_triple)
            start = and_match.end()
        else:
            end = len(record['string'])
            next_triple = [record['string'][start:end],start,end]
            string_list.append(next_triple[0])
            triples.append(next_triple)
            start = end
    if len(triples) == 0:
        return(False,False)
    else:
       output = []
       first = True
       for instring,start,end in triples:
            out = {}
            out['start']=start+record['start']
            out['end']=end+record['start']
            out['string']=instring
            out['phrase_type'] = 'NAME'
            if ('sentence_start' in record) and record['sentence_start'] and first:
                out['sentence_start'] = True
            first = False
            add_citation_id(out,file_id,dictionary)
            output.append(out)
    return(output,string_list)
                                   
    
    
def make_conjoined_phrase_relation(record1,record2,file_id,dictionary):
    relation = {'gram_type':'conj','conj1':record1,'conj2':record2,'start':record1['start'],'end':record2['end'],'relation_type':'conj'}
    for rec in [record1,record2]:
        if not 'id' in rec:
            add_citation_id(rec,file_id,dictionary)
    add_citation_id(relation,file_id,dictionary)
    return(relation)

def unambig_org(entry,string):
    if len(entry) == 1:
        return(True)
    elif string.isupper():
        return(True)
    
def possibly_adjust_phrase_type(record,file_id,citation_dictionary,party=False,conj=False,string_list = False):
    string = remove_extra_spaces(record['string'].lower())
    ## not using string_list yet, but could use it to ensure parallel NE types across conjunctions
    change = False
    person_words = 0
    has_profession = False
    has_unknown = False
    other = False
    has_title = False
    words = False        
    if (string in POS_dict) and record['string'][0].isupper():
        if ('ORG' in POS_dict[string]) and unambig_org(POS_dict[string],record['string']):
            change = True
            record['phrase_type']='ORGANIZATION'
        elif ('GPE' in POS_dict[string]):
            change = True
            record['phrase_type']='GPE'
    if (not change) and re.search('^the ',string):
        substring = string[4:]
        if substring in POS_dict:
            if ('ORG' in POS_dict[substring]):
                change = True
                record['phrase_type']='ORGANIZATION'
            elif ('GPE' in POS_dict[substring]):
                change = True
                record['phrase_type']='GPE'
    if not change:
        words = string.split(' ')
    if (not change) and words and (len(words)>1) and (words[-1].strip('.') in org_ending_words):
        record['phrase_type']='ORGANIZATION'
        change = True
    if ('&' in string) and (not change) and (record['phrase_type']=='NAME'):
        ## could be PERSON (authors) or ORGANIZATION
        organization = False
        person = True
        for word in words:
            if word in POS_dict:
                entry = POS_dict[word]
                if 'ORG_word' in entry:
                    organization = True
                elif 'PERSONNAME' in entry:
                    person = True
                else:
                    organization = True
                    ## dictionary items that are not first names
                    ## are indicators of non-person
        if organization or (not person):
            record['phrase_type']='ORGANIZATION'
        else:
            record['phrase_type']='PERSON'
        change = True
    if (not change) and person_test(string,has_title=has_title):
        record['phrase_type']='PERSON'
        if (not ' ' in string):
            add_to_one_person_names(string)
        else:
            last_person_word = get_last_person_word(string.lower())
            if last_person_word:
                add_to_one_person_names(last_person_word)
        change = True
    if party and (not change):
        apposition = False
        for word in words:
            if word.endswith(','):
                apposition = True
            stripped_word = word.strip('.,-')
            if (stripped_word in POS_dict) and ('PERSONNAME' in POS_dict[stripped_word]):
                person_words += 1
            elif (stripped_word in relational_dict) and ('PROFESSIONAL' in relational_dict[stripped_word]):
                has_profession = True
            elif (word in POS_dict) and ('TITLE' in POS_dict[word]):
                has_title = True
            elif (not stripped_word in relational_dict) and (not stripped_word in POS_dict):
                has_unknown = True
            else:
                other = True
        if ((person_words >= 1) and has_profession and apposition):
            record['phrase_type']='PERSON'
            change = True
        elif has_title and ((person_words >=1) or has_unknown):
            record['phrase_type']='PERSON'
            change = True
    elif not change:
        if not words:
            words = string.split(' ')
        legislative = False
        position = 0
        for word in words:
            stripped_word = word.strip('.,-')
            if (position == 0) and (word in POS_dict) and ('TITLE' in POS_dict[word]):
                has_title = True
            elif (stripped_word in relational_dict) and ('PROFESSIONAL' in relational_dict[stripped_word]):
                has_profession = True
            elif (stripped_word in POS_dict) and ('PERSONNAME' in POS_dict[stripped_word]):
                person_words += 1
            elif (not stripped_word in relational_dict) and (not stripped_word in POS_dict):
                has_unknown = True
            elif stripped_word in POS_dict:
                entry = POS_dict[stripped_word]
                if ('LEGISLATIVE_word' in entry):
                    legislative = True
                else:
                    other = True
            else:
                other = True
            position = 1+position
        if has_title and ((person_words >=1) or has_unknown) and (not legislative):
            record['phrase_type']='PERSON'
            change = True
        elif legislative:
            record['phrase_type'] = 'NAME'
            change = True
    if not change:
        position = 0
        organization = False
        legislative = False
        person = False
        gpe = False
        gpe_count = 0
        oov_word = False
        for word in words:
            entry = []
            if word in POS_dict:
                entry.extend(POS_dict[word])
            if word in relational_dict:
                entry.extend(relational_dict[word])
            if (position == len(word)-1) and (word in org_ending_words):
                record['phrase_type']='ORGANIZATION'
                change = True
            elif word in POS_dict:
                if 'ORG_word' in entry:
                    organization = True
                if 'LEGISLATIVE_word' in entry:
                    legislative = True
                if ('GPE_word' in entry) or ('GPE' in entry):
                    gpe = True
                    gpe_count +=1
                if ('PERSONNAME' in entry):
                    person = True
            elif len(entry) == 0:
                oov_word = True                
        if (not change) and gpe and has_profession:
            record['phrase_type']='PROFESSION'
            change = True
        elif (not change) and person and has_profession:
            record['phrase_type']='PERSON'
            change = True
        elif (not change) and organization and (not legislative):
            record['phrase_type']='ORGANIZATION'
            change = True
        elif gpe and (not organization) and (not legislative) and (oov_word or (gpe_count>1)):
            record['phrase_type']='GPE'
            change = True
    if (' and ' in string) and (not conj):
        ## if conj -- change even if already changed
        ## recursive calls -- only allow one layer of recursion
        record_list,record_string_list = split_phrase_record(record,file_id,citation_dictionary)
        ## print(record_list)
        phrase_type = False
        fail = False
        for phrase in record_list:
            possibly_adjust_phrase_type(phrase,file_id,citation_dictionary,party=party,conj=True,string_list=record_string_list)
            if not phrase_type:
                phrase_type = phrase['phrase_type']
            elif phrase_type == phrase['phrase_type']:
                pass
            else:
                fail = True
        if fail:
            record['phrase_type']='NAME'
            ## do not allow conjoined phrases of different name types
        if (not fail) and phrase_type and (phrase_type != record['phrase_type']):
            record['phrase_type'] = phrase_type
        else:
            return(False)

def probably_person(previous_words):
    if (len(previous_words)> 5):
        return(False)
    person_words = 0
    title = 0
    bad = False
    for word in previous_words:
        if ((len(word)>1) and (word[0].isupper()) and (word[1].islower())) or ((len(word)==1) and word.isupper()):
            is_capital = True
        else:
            is_capital = False
        word = word.lower()
        if not is_capital:
            return(False)
        elif word in POS_dict:
            entry = POS_dict[word]
            if ('PERSONNAME' in entry) or ('TITLE' in entry):
                person_words += 1
            else:
                bad = True
        elif is_initial(word):
            person_words += 1
    if (person_words > 0) and (not bad):
        return(True)
    else:
        return(False)
    
def get_role_phrases(line,spans,offset,file_id,citation_dictionary,individual_spans,line_number):
    trace = False
    if line.startswith('On May 4, 1908, Mr. Solicitor General Hoyt'):
         trace = True
         ## print(1,line,2,spans,3,offset,4,file_id,5,{},6,individual_spans,7,line_number)
    ## detect sequences that are either in capital format (consec capital sequences, with allowances for lowercase func words)
    ##        and are not in current spans
    ## detect similar sequences that contain role words, even if not capital or if inside of current spans
    ##
    conj_output = []
    word_pattern = re.compile('[1-4]?[A-Z-]+',re.I)
    year_pattern = re.compile('([^a-zA-Z0-9]|^)((18|19|20)[0-9][0-9])([^a-zA-Z0-9]|$)')
    match = word_pattern.search(line)
    deletable_early = re.compile('[^a-z]*((cite +as)|(writ of cert.*district,?( +division +[a-z]+)?)|(((Statement +of.*)|(Per? *Curiam *))?SUPREME +COURT +OF +THE +UNITED STATES))[^a-z]*',re.I)
    if line_number <= 5:
        deletable_match = deletable_early.search(line)
    else:
        deletable_match = False
    if match and deletable_match and (match.start()>=deletable_match.start(1)) and (match.end()<=deletable_match.end(1)):
        start = deletable_match.end(1)
        match = word_pattern.search(line,deletable_match.end(1))
    else:
        start = 0
    if match and deletable_match and (deletable_match.end(1)<match.start()):
        deletable_match = deletable_early.search(line,match.start())
    output = []
    out = {}
    sequence = []
    words = []
    word_ends_in_hyphen = False
    end_of_sentence = False
    start_sentence = False
    while match:
        if match and deletable_match and (match.start() >= deletable_match.start(1)) and (match.start() <= deletable_match.end(1)):
            out = {}
            match = word_pattern.search(line,deletable_match.end(1))
            start = deletable_match.end(1)
        previous_start = start
        add_on = False
        if match:
            word = match.group(0)
            word_ends_in_hyphen = word.endswith('-')
            if word_ends_in_hyphen:
                word = word[:-1]
            end_of_sentence = end_of_sentence_heuristic(word,line,match.end())
            if end_of_sentence:
                start_sentence = False
            else:
                start_sentence = start_sentence_heuristic(word,line,match.start())
                ## print(start_sentence,word)
            not_added_to_sequence = False
        if not match:
            pass
        # elif (len(sequence) == 0) and ((word.lower() in prepositions) or (word.lower() in ['and','or'])):
        #     add_on = False
        #     start = match.end()+1
        #     print('** blah **')
        #     print(1,word)
        #     print(2,words)
        elif word.lower() in ['nos','nos.','no','no.']:
            add_on = False
        elif (word.lower() in relational_dict):
            if len(sequence)==0:
                out['start']=match.start()+offset
            entry = relational_dict[word.lower()]
            entry = merge_relational_entries(word.lower(),entry)
            if entry in ['LEGAL_ROLE','PLURAL_LEGAL_ROLE']:
                entry_type = 'LEGAL_ROLE'
            elif (entry in ['ORGANIZATION','PLURAL_ORGANIZATION']):
                entry_type = 'ORGANIZATION'
            elif entry in ['FAMILY','PLURAL_FAMILY']:
                entry_type = 'FAMILY'
            elif entry in ['PROFESSIONAL','PLURAL_PROFESSIONAL','PROFESSIONAL_OR_RANK']:
                entry_type = 'PROFESSIONAL'
            else:
                entry_type = 'OTHER'
            if ('start' in out) and (len(sequence)>0) and (entry_type in ['LEGAL_ROLE','FAMILY','PROFESSION','ORGANIZATION']) and \
              (sequence[-1] in ['FILLER','CAPITALIZED_WORD']) and \
              (((entry_type == 'ORGANIZATION') and (('ORGANIZATION' in sequence) or  ('PLURAL_ORGANIZATION' in sequence))) or \
               ((entry_type == 'LEGAL_ROLE') and (('LEGAL_ROLE' in sequence) or ('PLURAL_LEGAL_ROLE' in sequence))) or \
               ((entry_type == 'FAMILY') and (('FAMILY' in sequence) or ('PLURAL_FAMILY' in sequence))) or \
               ((entry_type == 'PROFESSIONAL') and (('PROFESSIONAL' in sequence) or ('PLURAL_PROFESSIONAL' in sequence) or \
                                                    ('PROFESSIONAL_OR_RANK' in sequence)))):
                if word_ends_in_hyphen:
                    end = start-1
                else:
                    end = start
                out['end']=end+offset
                out['sentence_start'] = start_sentence
                new_phrases,good = ok_role_phrase(out,sequence,spans,line[out['start']-offset:start],line,offset,words)
                if new_phrases:
                    for phrase,seq,phrase_words in new_phrases:
                        abort_phrase = False
                        if 'name_with_infixed_role' in phrase:
                            phrase['phrase_type'] = 'NAME'
                            plural = False
                        else:
                            value,plural = find_phrase_type_from_sequence(seq,phrase_words)
                            if value:
                                phrase['phrase_type']=value
                            else:
                                abort_phrase = True
                        if plural and (not abort_phrase):
                            phrase['plural']=True
                        if not abort_phrase:
                            phrase['string'] = line[phrase['start']-offset:phrase['end']-offset]
                            output.append(phrase)
                elif good:
                    value,plural = find_phrase_type_from_sequence(sequence,words)
                    if value:
                        out['phrase_type'] = value
                        if plural:
                            out['plural']=True                    
                            out['string']=line[out['start']-offset:out['end']-offset]
                            output.append(out)
                sequence = [entry]
                words = [word]
                out = {'start':match.start()+offset}
            else:
                sequence.append(entry)
                words.append(word)
            add_on = True
            start = match.end()
        elif (word.lower() in POS_dict) and (len(sequence)>0) and ('LEGISLATIVE_word' in POS_dict[word.lower()]):
            add_on = True
            sequence.append('LEGISLATIVE')
            words.append(word)
            start = match.end()
        elif is_initial(word) and ((len(sequence)==0) or (((match.start() == 0) or (" " ==line[match.start()-1])) and (sequence[-1] in ['PERSONNAME','CAPITALIZED_WORD','INITIAL']))):
            add_on = True
            sequence.append('INITIAL')
            words.append(word)
            start = match.end()
        elif (word.lower() in not_uppercase_part_of_org_names) and (len(sequence)==0) and \
          not((word.lower() in ['for']) and (((len(words)>1) and (probably_person(words))) or \
                                             ((len(words)>0) and (words[-1].lower() in POS_dict) and ('LEGISLATIVE_word' in POS_dict[words[-1].lower()])))):
            if len(sequence)>0:
                add_on = True
                if False and is_initial(word) and (match.start()>0) and (" " ==line[match.start()-1]):
                    sequence.append('INITIAL')
                else:
                    sequence.append('FILLER')
                words.append(word)
                start = match.end()
        elif (match.end()+1<len(line)) and (line[match.end()+1]=='.') and ((word.lower()+'.') in relational_dict):
            if len(sequence)==0:
                out['start']=match.start()+offset
            entry = relational_dict[word.lower()+'.']
            sequence.append(merge_relational_entries(word.lower(),entry))
            words.append(word)
            add_on = True
            start = match.end()+1
        elif (len(sequence) == 0) and ((len(word)<2) or (is_roman(word.lower()))) and \
          (re.search('^[\.]?[ \t]{2,}',line[match.end():]) or (not re.search('[a-zA-Z]',line[match.end():]))):
            not_added_to_sequence = True
        elif len(sequence)==0 and (word.lower() in pre_citation_words):
            not_added_to_sequence = True
        elif capitalized_word(word):
            if len(sequence)==0 and (ok_non_vocab_word_start_sequence(word,start_sentence)) or title_word(word):
                out['start']=match.start()+offset
                out['sentence_start'] = start_sentence
                add_on = True
            elif len(sequence)>0:
                add_on = True
            else:
                add_on = False
            if add_on:
                sequence.append('CAPITALIZED_WORD')
                words.append(word)
                if ((match.end()+1<len(line)) and (line[match.end()+1]=='.') and possible_abbrev(word)) \
                  or ((match.end()+2<len(line)) and (line[match.end()+1]=='.') and (line[match.end()+2] in ';,')):
                    start = match.end()+1
                else:
                    start = match.end()
            ## if immediately followed by period use heuristic and/or
            ## abbrev list to differentiate end of sentence with
            ## abbreviation
        else:
            not_added_to_sequence = True
        if not match:
            pass
        elif add_on and (not (re.search('[?";:\(\)\[\]]',line[previous_start:match.start()]))) and (not end_of_sentence) and \
          ((not ',' in line[previous_start:match.start()]) or (word.lower() in org_ending_words) or (word.lower() in person_ending_words)):
            start = match.end()
        elif add_on and end_of_sentence and (len(sequence) > 1):
            start = match.end()
            if word_ends_in_hyphen:
                end = start-1
            else:
                end = start
            out['end']=end+offset
            if 'start' in out:
                new_phrases,good = ok_role_phrase(out,sequence,spans,line[out['start']-offset:start],line,offset,words)
            else:
                new_phrases = False
                good = False
            if good:
                phrase_type,plural = find_phrase_type_from_sequence(sequence,words)
                if phrase_type:
                    out['phrase_type'] = phrase_type
                    if plural:
                        out['plural']=True
                    out['string']=line[out['start']-offset:out['end']-offset]
                    output.append(out)
            elif new_phrases:
                for phrase,seq,phrase_words in new_phrases:
                    if 'name_with_infixed_role' in phrase:
                        phrase_type = 'NAME'
                        plural = False
                    else:
                        phrase_type,plural = find_phrase_type_from_sequence(seq,phrase_words)
                    if phrase_type:
                        phrase['phrase_type'] = phrase_type
                        if plural:
                            phrase['plural']=True
                        phrase['string'] = line[phrase['start']-offset:phrase['end']-offset]
                        ## words = phrase['string'].split(' ')
                        # print('3')
                        # if len(words) != len(seq):
                        #     print(len(words),len(seq))
                        #     print(words)
                        #     print(phrase_words)
                        #     print(seq)
                        #     input('pause')
                        new2,good2 = ok_role_phrase(phrase,seq,spans,phrase['string'],line,offset,phrase_words)
                    else:
                        good2 = False
                    if good2:
                        output.append(phrase)
            sequence = []
            words = []
            out = {}
        else:
            ### conditions on last stored item as potential item to record
            ### if item is relational/occupation category, keep
            ### if simple allcap, keep only if not already part of a span
            if ('start' in out):
                if not_added_to_sequence:
                    pass
                else:
                    ## print(1,sequence,words)
                    sequence = sequence[:-1]
                    words = words[:-1]
                    ## print(2,sequence,words)
                if line[start-1]=='-':
                    start = start-1
                year_match = year_pattern.search(line,previous_start)
                if year_match and (not re.search('[a-zA-Z0-9\,\.]',line[previous_start:year_match.start()])):
                    if (line[year_match.start()-1]=='(') and (line[year_match.end()]==')'):
                        previous_start = year_match.end()
                    else:
                        previous_start = year_match.end(2)
                if ('start' in out) and (out['start']< previous_start+offset):
                    out['end']=previous_start+offset
                ## words can be incorrect here ** 57 ***
                    new_phrases,good = ok_role_phrase(out,sequence,spans,line[out['start']-offset:previous_start],line,offset,words)
                else:
                    new_phrases = False
                    good = False
                if new_phrases:
                    for phrase,seq,phrase_words in new_phrases:
                        if 'name_with_infixed_role' in phrase:
                            phrase_type = 'NAME'
                            plural = False
                        else:
                            phrase_type,plural = find_phrase_type_from_sequence(seq,phrase_words)
                        if phrase_type:
                            phrase['phrase_type'] = phrase_type
                            if plural:
                                phrase['plural']=True
                            phrase['string'] = line[phrase['start']-offset:phrase['end']-offset]
                            output.append(phrase)
                            ## if no phrase type, not a valid phrase
                elif good:
                    phrase_type, plural = find_phrase_type_from_sequence(sequence,words)
                    if phrase_type:
                        out['phrase_type'] = phrase_type
                        if plural:
                            out['plural']=True
                        out['string']=line[out['start']-offset:previous_start]
                        output.append(out)
                if (not re.search('[a-zA-Z]',line[match.end():])) or end_of_sentence:
                    if word_ends_in_hyphen:
                        end = match.end()-1
                    else:
                        end = match.end()
                    out={'start':match.start()+offset,'end':end+offset}
                    out['string']=line[match.start():end]
                    if match.group(0).lower() in relational_dict:
                        words = [word]
                        sequence = [merge_relational_entries(match.group(0),relational_dict[match.group(0).lower()])]
                        phrase_type,plural = find_phrase_type_from_sequence(sequence,words)
                        ## words = [word]
                    else:
                        phrase_type = 'OTHER'
                        sequence = ['OTHER']
                        words = [word]
                    if phrase_type in ['LEGAL_ROLE','PROFESSION','FAMILY','ORGANIZATION']:
                        out['phrase_type'] = phrase_type
                        if plural:
                            out['plural'] = True
                    elif object_within_spans(out,spans):
                        out = False
                    elif (len(match.group(0)) > 1) and capitalized_word(match.group(0)):
                        out['phrase_type'] = 'NAME'
                    else:
                        out = False
                    if out:
                        # print('sequence',sequence,offset,words)
                        # print(spans)
                        # print(77,line[out['start']-offset:start])
                        # print(777,line)
                        # print(offset)
                        if len(words) == 1:
                            new_phrases,good = ok_role_phrase(out,sequence,spans,out['string'],line,offset,words)
                            if good:
                                output.append(out)
                        else:
                            output.append(out)
                    start = match.end()
                    ## match=False
                    ## print(out)
                else:
                    start = match.start()
            else:
                start = match.end()
            # print(3)
            # print(match)
            # print(end_of_sentence)
            sequence = []
            words = []
            out = {}
        if match:
            match = word_pattern.search(line,start)
    if ('start' in out):
        if line[start-1]=='-':
            start = start-1
        year_match = year_pattern.search(line,start)
        if year_match and (not re.search('[a-zA-Z0-9\,\.]',line[start:year_match.start()])):
            if (line[year_match.start()-1]=='(') and (line[year_match.end()]==')'):
                start = year_match.end()
            else:
                start = year_match.end(2)
        if word_ends_in_hyphen:
            end = start-1
        else:
            end = start
        out['end']=end+offset
        new_phrases,good = ok_role_phrase(out,sequence,spans,line[out['start']-offset:start],line,offset,words)
        if new_phrases:
            for phrase,seq,phrase_words in new_phrases:
                if 'name_with_infixed_role' in phrase:
                    phrase['phrase_type'] = 'NAME'
                    plural = False
                else:
                    value,plural = find_phrase_type_from_sequence(seq,phrase_words)
                    if value:
                        phrase['phrase_type'] = value
                if plural:
                    phrase['plural']=True
                phrase['string'] = line[phrase['start']-offset:phrase['end']-offset]
                if 'phrase_type' in phrase:
                    output.append(phrase)
        elif good:
            value,plural = find_phrase_type_from_sequence(sequence,words)
            if value:
                out['phrase_type'] = value
            if plural:
                out['plural']=True
            out['string']=line[out['start']-offset:out['end']-offset]
            if 'phrase_type' in out:
                output.append(out)
    final_output=[]
    remove = []
    for record in output:
        if (record['phrase_type']=='NAME') or re.search(' +(and|AND|And) +',record['string']):
            conj_out = possibly_adjust_phrase_type(record,file_id,citation_dictionary)
            if conj_out:
                conj_output.extend(conj_out)
        elif ((record['phrase_type'] in ['ORGANIZATION','GPE','PERSON']) \
              and record['string'][0].islower() \
              and (not ' ' in record['string']) and (record['string'].lower() in POS_dict) \
              and (len(POS_dict[record['string'].lower()])>1)):
            remove.append(record)
        if (not [record['start'],record['end']] in individual_spans) and (not record in remove):
            ## prevents duplicates
            add_citation_id(record,file_id,citation_dictionary)
            final_output.append(record)
    # if trace:
    #     print('regular_output')
    #     print(final_output)
    #     print('conj')
    #     print(conj_output)
    return(final_output,conj_output)
    
def role_print(outstream,role_phrase):
        ## if no phrase_type don't do anything
        ## print(role_phrase)
    if 'phrase_type' in role_phrase:
        outstream.write('<'+role_phrase['phrase_type'])
        for attribute in ['id','start','end','plural','party1_of','party2_of']:
            if attribute in role_phrase:
                outstream.write(' '+attribute+'="'+wol_escape(str(role_phrase[attribute]))+'"')
        outstream.write('>')
        if 'string' in role_phrase:
            outstream.write(wol_escape(role_phrase['string']))
        outstream.write('</'+role_phrase['phrase_type']+'>'+os.linesep)

def find_dates(line,offset,file_id,citation_dictionary):
    output = []
    match = date_pattern.search(line)
    while match:
        out = {'start':match.start()+offset,'end':match.end()+offset}
        out['string']=match.group(0)
        out['phrase_type']='date'
        ## we could regularize this based on the time ISO
        output.append(out)
        start = match.end()
        match = date_pattern.search(line,start)
    for record in output:
        add_citation_id(record,file_id,citation_dictionary)
    return(output)

def sort_records(records,use_ids=False):
    import random
    ## sorting first by start and then by negative 1 X end this sorts
    ## first by the beginning and then puts larger spans first if they
    ## start first, so infixed items will follow surrounding ones
    sort_list= []
    for record in records:
        ## ran_num = random.randint(1,1000000)
        ## sort_list.append([record['start'],record['end'],ran_num,record])
        ## above possible fix if there are duplicate entries for a span
        if not 'start' in record:
            print(record)
            print('Warning: No start')
        elif use_ids:
            sort_list.append([record['start'],(-1 * record['end']),record['id'],record])
        else:
            sort_list.append([record['start'],(-1 * record['end']),record])
    sort_list.sort()
    output = []
    for record in sort_list:
        if use_ids:
            output.append(record[3])
        else:
            output.append(record[2])
    return(output)

def bad_name(string):
    words = string.lower().split(' ')
    OK = False
    for word in words:
        if word in POS_dict:
            entry = POS_dict[word]
        else:
            entry = []
        if word in relational_dict:
            entry.extend(relational_dict[word])
        if is_month.search(word) or (not re.search('[a-z]',word)):
            pass
        else:
            OK = True
        # elif not entry:
        #     OK = True
        # else:
        #     for classification in entry:
        #         if OK:
        #             pass
        #         elif classification in ['PERSONNAME','LEGAL_ROLE','PROFESSIONAL','PROFESSIONAL_OR_RANK',\
        #                                 'PLURAL_LEGAL_ROLE','PLURAL_PROFESSIONAL']:
        #             OK = True
    if not OK:
        return(True)
    
def get_party_names_and_roles_from_cases(vs_cases,file_id,citation_dictionary):
    output = []
    remove_citations = []
    conj_output = []
    for case in vs_cases:
        if 'party1' in case:
            party1 = case['party1']
            party2 = case['party2']
            if 'party1_role' in case:
                party1_role = case['party1_role']
            else:
                party1_role = False
            if 'party2_role' in case:
                party2_role = case['party2_role']
            else:
                party2_role = False
            found_party1 = False
            for party,party_type in [[party1,'party1'],[party2,'party2']]:
                if party in case['string']:
                    if found_party1 and (party_type == 'party2'):
                        local_start = case['string'].index(party,local_end) 
                        ## deals with cases where parties have the same name
                    else:
                        local_start = case['string'].index(party)
                        found_party1 = True
                    local_end = local_start+len(party)
                    start = local_start+case['start']
                    end = local_end+case['start']
                    out = {'start':start,'end':end,'string':party,'phrase_type':'NAME'}
                    conj_out = possibly_adjust_phrase_type(out,file_id,citation_dictionary,party=True)
                    if conj_out:
                        conj_output.extend(conj_out)
                    if party_type == 'party1':
                        out['party1_of']=case['id']
                    else:
                        out['party2_of']=case['id']
                    if (out['phrase_type']=='NAME') and  (bad_name(party)):
                        if (not case in remove_citations):
                            remove_citations.append(case) 
                        if party == 'party1':
                            party1_role = False
                        else:
                            party2_role = False
                        ## don't add out to output
                    elif case in remove_citations:
                        ## don't add if other party nixed citation
                        if party == 'party1':
                            party1_role = False
                        else:
                            party2_role = False
                    else:
                        if (out['phrase_type']=='PERSON') and (not ' ' in out['string']):
                            add_to_one_person_names(out['string'].lower())
                        add_citation_id(out,file_id,citation_dictionary)
                        output.append(out)                    
            for party_role in [party1_role,party2_role]:
                if party_role:
                    for role in party_role.split(', '):
                        match = re.search(role,case['string'].lower())
                        if match:
                            start = case['start']+match.start()
                            end = case['start']+match.end()
                            string = case['string'][match.start():match.end()]
                            ## party_role in case regularized to lowercase
                            ## searches must be in lowercase, but actual string can be any case
                            out = {'start':start,'end':end,'string':string,'phrase_type':'LEGAL_ROLE'}
                            add_citation_id(out,file_id,citation_dictionary)
                            output.append(out)
    return(remove_citations,output,conj_output)

def get_type_from_entity(entity):
    if 'phrase_type' in entity:
        return(entity['phrase_type'])
    elif 'entry_type' in entity:
        return(entity['entry_type'])
    else:
        return('NAME')

def merge_spans(spans):
    ## input = set of spans sorted first by start and then by end
    output = []
    last_span = False
    for span in spans:
        if not last_span:
            last_span = span[:]
        elif last_span[0] == span[0]:
            last_span[1] = span[1]
        elif last_span[1]==span[1]:
            pass
        elif (last_span[0]<span[0]) and (last_span[1]>=span[1]):
            pass
        else:
            output.append(last_span)
            last_span = span[:]
    if last_span:
        output.append(last_span)
    return(output)

def non_zero_subtract(first_num,second_num):
    difference = first_num-second_num
    if difference != 0:
        return(difference)

def merge_spans2(spans,types,line,offset):
    ## input = set of spans sorted first by start and then by end
    ## modified for use with one_line_object to allow for an initial (capitalized) string
    output = []
    num = 0
    last_span = False
    last_type = False
    current_type = False
    for span in spans:
        if not last_span:
            last_span = span[:]
            last_type = types[num]
        elif last_span[0] == span[0]:
            last_span[1] = span[1]
        elif last_span[1]==span[1]:
            pass
        elif (last_span[0]<span[0]) and (last_span[1]>=span[1]):
            pass
        elif last_span and (num > 0) and (last_type in ['NAME','PERSON','ORGANIZATION']) \
           and (last_span[1]<span[0]) \
           and re.search('^ *$',line[last_span[1]-offset:non_zero_subtract(span[0],offset)]):
            pass
        else:
            if last_span:
                output.append(last_span)
            last_span = span[:]
            last_type = types[num]
        num = num + 1
    if last_span:
        output.append(last_span)
    return(output)

def remove_out_words_from_extra(extra):
    cue_pattern = re.compile('nos?|and|[0-9]',re.I)
    ## no is the number marker for docket numbers
    ## possibly other stuff doesn't matter as well
    match = cue_pattern.search(extra)
    while match:
        extra = extra[:match.start(0)]+extra[match.end():]
        match = cue_pattern.search(extra)
    return(extra)

def merge_spans_if_take_up_whole_line(spans,line,offset):
    if len(spans) <= 1:
        return(spans)
    extra = ''
    spans.sort()
    start = 0
    for span in spans:
        extra = extra + line[start:span[0]-offset]
        start = span[-1]-offset
    if start:
        extra = extra + line[start:]
    extra = remove_out_words_from_extra(extra)
    if re.search('[a-zA-Z0-9]',extra):
        return(spans)
    else:
        return([[spans[0][0],spans[-1][1]]])

def OK_after_one_line_object(right_string):
    if not re.search('[A-Za-z]',right_string):
        return(True)
    elif re.search('^ *CERTIORARI( [A-Z]*)* *$',right_string):
        ### may want to eventually go after CERTIORIARI TO strings
        return(True)
    elif re.search('^[^a-zA-Z]*(Per )?Curiam[^a-zA-Z]*$',right_string):
        return(True)

def skippable_beginning (line_start):
    slip_opinion = re.search('(Slip +Opinion)|(SLIP +OPINION)',line_start)
    if slip_opinion:
        line_start = line_start[:slip_opinion.start()]+line_start[slip_opinion.end():]
    cite_as = re.search('Cite +as:?|CITE +AS:?',line_start)
    if cite_as:
        line_start = line_start[:cite_as.start()]+line_start[cite_as.end():]
    if re.search('[A-Za-z]',line_start):
        return(False)
    else:
        return(True)

def one_line_object(entity_set,line,offset):
    spans = []
    types = []
    citation_spans = []
    citation_types = []
    for entity in entity_set:
        spans.append([entity['start'],entity['end']])
        this_type = get_type_from_entity(entity)
        types.append(this_type)
        if this_type in ['standard_case','case_X_vs_Y','case_citation_other','docket']:
            citation_spans.append([entity['start'],entity['end']])
            citation_types.append(this_type)
    spans = merge_spans2(spans,types,line,offset)
    spans = merge_spans_if_take_up_whole_line(spans,line,offset)
    if (len(spans) == 1):
        if (not (re.search('[A-Za-z]',remove_out_words_from_extra(line[:spans[0][0]-offset])))) and OK_after_one_line_object(remove_out_words_from_extra(line[spans[0][1]-offset:])):
            return(True)
        else:
            return(False)
    elif citation_spans:
        spans = merge_spans2(citation_spans,citation_types,line,offset)
        spans = merge_spans_if_take_up_whole_line(spans,line,offset)
        if (len(spans) == 1) and skippable_beginning(line[:spans[0][0]-offset]) \
          and OK_after_one_line_object(line[spans[0][1]-offset:]):
            return(True)
        else:
            return(False)            
    else:
        return(False)

def multiline_objects(line_output):
    line_numbers = []
    for obj in line_output:
        line_number = obj['line']
        if not line_number in line_numbers:
            line_numbers.append(line_number)
    if len(line_numbers)>1:
        return(True)
    else:
        return(False)

def deletable_line(line):
    slip1 = re.compile('\(Slip +Opinion.*?done +in +connection +with +this +case, +at +the +time +the +opinion +is +issued\.',re.I)
    slip2 = re.compile('The +syllabus +constitutes +no +part +of +the +opinion.*?convenience +of +the +reader\.',re.I)
    slip3 = re.compile('See +United +States +v\. +Detroit +Timber +& +Lumber +Co\., +200 +U\. *S\. +321, +337\.',re.I)
    slip3a = re.compile(' *SUPREME.*?Syllabus',re.I) ## without greedy operator, it takes out to much
    one_liner = re.compile('(^ *(((Statement +of.*)|(NOTICE:.*))?SUPREME +COURT +OF +THE +UNITED STATES)|(ORDER IN PENDING CASE))',re.I) ## might be useful for finding author of opinion
    position = 0
    match1 = slip1.search(line)
    if match1:
        position = match1.end()
    match2 = slip2.search(line,position)
    if match2:
        position = match2.end()
    match3 = slip3.search(line,position)
    if match3:
        position = match3.end()
        position2 = slip3a.search(line,position)
        if position2:
            position = position2.end()
    match4 = one_liner.search(line)
    if match4:
        position = match4.end()
    if position and (position != 0):
        return(position)

def merge_spans_if_conjoined(spans,line,offset):
    big_start = spans[0][0]
    start,end = spans[0]
    Fail = False
    for next_start,next_end in spans[1:]:
        in_between = line[end-offset:next_start-offset].lower()
        in_between = re.sub('[;,]',' ',in_between) ## ignore inbetween separator punctuation
        in_between = re.sub('and','',in_between) ## ignore the word and
        if re.search('[^ ]',in_between):
            Fail = True
    if Fail:
        return(spans)
    else:
        ## keep the last end
        return([[big_start,next_end]])
    
def weak_one_line_object(entity_set,line,offset,one_line_objects):
    if not one_line_objects:
        return(False)
    name_citation_spans = []
    n_types = []
    other_spans = []
    for entity in entity_set:
        if get_type_from_entity(entity) in ['case_X_vs_Y','case_citation_other']:
            name_citation_spans.append([entity['start'],entity['end']])
            n_types.append(get_type_from_entity(entity))
        else:
            other_spans.append([entity['start'],entity['end']])
    name_citation_spans = merge_spans2(name_citation_spans,n_types,line,offset)
    name_citation_spans = merge_spans_if_take_up_whole_line(name_citation_spans,line,offset)
    if name_citation_spans and (len(name_citation_spans)>1):
        name_citation_spans = merge_spans_if_conjoined(name_citation_spans,line,offset)
    answer = True
    if len(name_citation_spans)==1:
        big_start,big_end = name_citation_spans[0]
        for span in other_spans:
            if span[0] < big_start:
                answer=False
    else:
        answer = False
    return(answer)


def make_other_citation_from_name(possible_other_citation,line_number,file_id,citation_dictionary):
    out = {'entry_type':'case_citation_other','line':line_number}
    ## 'start', 'end','name','string', line, type
    for key in ['start','end','string']:
        out[key] = possible_other_citation[key]
    out['name']=possible_other_citation['string']
    add_citation_id(out,file_id,citation_dictionary)
    return(out)

def span_takes_up_whole_line(line,offset,span):
    extra = line[:span[0]-offset]+line[span[1]-offset:]
    extra = remove_out_words_from_extra(extra)
    if re.search('[a-zA-Z0-9]',extra):
        return(False)
    else:
        return(True)

def begin_v(line):
    line = line.strip(os.linesep)
    match = re.search('^[ \t]*(.*)v\. +[A-Z]',line)
    if match:
        if match.group(1):
            first_word_match = re.search('[a-zA-Z]+',match.group(1))
            if first_word_match:
                if first_word_match.group(0).lower() in relational_dict:
                    return(True)
                else:
                    return(False)
            else:
                return(True)
        else:
           return(True)
    else:
        return(False)

def ambiguous_person_entry(word):
    entry = []
    if word in relational_dict:
        entry.extend(relational_dict[word])
    if word in POS_dict:
        entry.extend(POS_dict[word])
    if 'PERSONNAME' in entry:
        entry.remove('PERSONNAME')
    if len(entry)>0:
        return(True)
    else:
        return(False)

def span_conflict(span1,span2):
    start1,end1 = span1
    start2,end2 = span2
    if start1 >= end2:
        return(False)
    elif end1 <=start2:
        return(False)
    else:
        return(True)

def remove_objects_for_line_N(output,line_number):
    new_output = []
    removed = []
    for obj in output:
        if obj['line'] != line_number:
            new_output.append(obj)
        else:
            removed.append(obj)
    return(new_output,removed)
    
def find_case_citations(txt_file,file_id):
    global id_number
    global one_word_person_names
    trace = False
    one_word_person_names = {}
    id_number = 0
    citation_output = []
    docket_output = []
    vs_output = []
    dates = []
    role_phrase_output = []
    citation_dictionary = {}
    previous_info_dictionary ={}
    line_output = []
    all_comments = []
    output = []
    one_line_objects = False
    possible_other_citation = False
    line_number = 0
    max_multi_line_number = 5
    with open(txt_file) as instream:
        offset = 0
        last_line = False
        last_line_one_line_object = False
        line_combo = False
        old_one_line_objects = False
        standard_case_lines = []
        conj_output = []
        for line in instream:
            line_output=[]
            line_number = line_number+1
            out = []
            out2 = []
            out3 = []
            out3_prime = []
            out4 = []
            out5 = []
            out6 = []
            if line_number <=4:
                deletable_line_position = deletable_line(line)
            elif deletable_line_position:
                deletable_line_position = False
            if (deletable_line_position and (deletable_line_position > 0)):
                line = line[deletable_line_position:]
                offset = offset + deletable_line_position
            garbage = detect_garbage_line(line)
            if garbage:
                out = []
                last_line_one_line_object = False
            elif last_line and ((re.search('[ \t]*([vV][sS]?[\.]?|versus|against)[ \t]*$',line.strip(os.linesep))) or \
              (begin_v(line) and line_number<=max_multi_line_number)):        
                line_combo = True
                if not one_line_objects:
                    one_line_objects = old_one_line_objects
                line = last_line.strip(os.linesep) + ' ' + line
                offset = last_offset
                output,removed_output = remove_objects_for_line_N(output,line_number-1)
                if one_line_objects:
                    for item in removed_output:
                        if item in one_line_objects:
                            one_line_objects.remove(item)
                possible_other_citation = False
                max_multi_line_number = max_multi_line_number + 1
                ## if current line ends in v. 
                ## also one_line_object status is maintained
            elif line_combo:
                possible_other_citation = False
                line = last_line.strip(os.linesep) + ' ' + line
                line_combo = False
                offset = last_offset
                out,comments = get_citation_output(line,offset,file_id,citation_dictionary,line_number)
                if comments:
                    all_comments.extend(comments)
                line_output.extend(out)
                max_multi_line_number = max_multi_line_number + 1
                ## if last line (ends in  v.) and continuing one_line_object thing
            else:
                if (not last_line) and re.search('[ \t]*([vV][sS]?[\.]?|versus|against)[ \t]*$',line.strip(os.linesep)):
                    line_combo = True
                    out = []
                    possible_other_citation = False
                    max_multi_line_number = max_multi_line_number + 1
                else:
                    if possible_other_citation:
                        out_prime = make_other_citation_from_name(possible_other_citation,line_number-1,file_id,citation_dictionary)
                        line_output.append(out_prime)
                        possible_other_citation = False
                        if old_one_line_objects and not one_line_objects:
                            one_line_objects = old_one_line_objects 
                            one_line_objects.append(out_prime)   
                    out,comments = get_citation_output(line,offset,file_id,citation_dictionary,line_number)
                    if comments:
                        all_comments.extend(comments)
                    line_output.extend(out)
            if out:
                standard_case_lines.append(line_number)
            spans = []
            last_offset = offset
            for item in out:
                item['line']=line_number
                item['entry_type']='standard_case'
                spans.append([item['start'],item['end']])
            if (not garbage) and (not line_combo):
                out2 = get_docket_numbers(line,spans,offset,file_id,citation_dictionary)
            if (not garbage) and out2:
                line_output.extend(out2)
                for item in out2:
                    item['line']=line_number
                    item['entry_type']='docket'
                    spans.append([item['offset_start'],item['end']])
                    ## offset_start is the start before the signal (no., nos., and., ...), rather than the span of the actual docket no.
                spans.sort()
            if (not garbage) and (not line_combo):
                out2 = get_docket_number_sets(line,spans,offset,file_id,citation_dictionary)
            if (not garbage) and out2:
                line_output.extend(out2)
                for item in out2:
                    item['line']=line_number
                    item['entry_type']='docket'
                    spans.append([item['offset_start'],item['end']])
                spans.sort()
            if (not garbage) and (not line_combo):
                out3 = get_vs_citations(line,spans,offset,file_id,citation_dictionary,one_line_objects,line_number)
                out3 = edit_vs_citations(out3,previous_info_dictionary)
                remove_citations,parties,conj_out = get_party_names_and_roles_from_cases(out3,file_id,citation_dictionary)
                for cit in remove_citations:
                    out3.remove(cit)
                if conj_out:
                    conj_output.extend(conj_out)
            else:
                parties = False
            if (not garbage) and (not line_combo):
                out4 = find_dates(line,offset,file_id,citation_dictionary)
            if (not garbage) and out4:
                line_output.extend(out4)
                for item in out4:
                    item['line']=line_number
                    spans.append([item['start'],item['end']])
                spans.sort()
            if parties:
                line_output.extend(parties)
            if (not garbage) and out3:
                line_output.extend(out3)
                for item in out3:
                    item['line']=line_number
                    item['entry_type']='case_X_vs_Y'
                    spans.append([item['start'],item['end']])
                spans.sort()
            if (not garbage) and (not line_combo):
                out3_prime = get_other_case_citations(line,spans,offset,file_id,citation_dictionary,one_line_objects)
                line_output.extend(out3_prime)
                if out3_prime:
                    for item in out3_prime:
                        item['line']=line_number
                        item['entry_type']='case_citation_other'
                        spans.append([item['start'],item['end']])
                    spans.sort()
            if parties:
                for item in parties:
                    item['line']=line_number
                    spans.append([item['start'],item['end']])
                spans.sort()
            spans2 = spans[:]
            spans2 = merge_spans(spans2)
            if (not garbage) and (not line_combo):
                out5,conj_out = get_role_phrases(line,spans2,offset,file_id,citation_dictionary,spans,line_number)
                if out5 and (len(out5)==1) and (not (out3 or out4 or out2 or out)) and (line_number < max_multi_line_number) and \
                  ((line_number == 1) or (standard_case_lines and ((standard_case_lines[-1]+1) == line_number))) and \
                  (out5[0]['phrase_type']=='NAME') and span_takes_up_whole_line(line,offset,[out5[0]['start'],out5[0]['end']]):
                    possible_other_citation = out5[0]
                if conj_out:
                    conj_output.extend(conj_out)
            if (not garbage) and out5:
                for item in out5:
                    item['line']=line_number
                    spans2.append([item['start'],item['end']])
                line_output.extend(out5)
            offset = offset + len(line)
            spans2.sort()
            line_output.extend(all_comments)
            line_output=sort_records(line_output,use_ids=True)
            output.extend(line_output)
            if line_combo:
                pass
            if (not line_output) and (not re.search('[A-Za-z]',line)) and deletable_line_position:
                pass
            elif one_line_object(line_output,line,last_offset) or weak_one_line_object(line_output,line,last_offset,one_line_objects):
                if one_line_objects:
                    one_line_objects.extend(line_output)
                else:
                    one_line_objects = line_output
            elif one_line_objects and (not line_combo):
                old_one_line_objects = one_line_objects
                last_line_one_line_object = True
                one_line_objects = False
            last_line = line
        if conj_output:
            for item in conj_output:
                if 'phrase_type' in item:
                    output.append(item)
            ## we could sort these (later)
        for out in output:
            if 'string' in out:
                refstring = out['string'].lower()
            else:
                refstring = False
            if refstring and ('phrase_type' in out) and (out['phrase_type']=='PERSON') and (not ' ' in out['string']) \
              and (not 'party1_of' in out) and (not ('party2_of' in out)) and (refstring in one_word_person_names) \
              and ambiguous_person_entry(refstring) and (one_word_person_names[refstring] == 1):
                out['phrase_type']='NAME'
    return(output)

## Part 2: Legislation Citations

court_reporter_check = re.compile('^('+court_reporter_rexp+')$')


##################
# GENERAL REGEX: #
##################

roman_num_rexp = '(?:[MCLDXVI]+)'
numeral_rexp = roman_num_rexp + '|(?:\d+)'
section_numeral_rexp = '((?:{0}-?\.?:?)+)'.format(numeral_rexp)
section_numeral_rexp_noncap = '(?:(?:{0}-?\.?:?)+)'.format(numeral_rexp)

act_abbrev_dictionary = {}

agency_abbrev_dictionary = {'CFR':'Code of Federal Regulations'}


def get_states_dict():
    """Returns a dict of abbreviation of state names to full state name

    :return:
    """
    states_dict = {}
    with open('STATES.dict') as instream:
        for line in instream:
            states_dict[re.sub(' +','',line.split('\t')[0].replace('. ', '.'))] = line.split('\t')[1].strip()
            ## added an additional replace to get rid of multiple spaces
    # states_dict['U.S.'] = 'Federal'
    return states_dict


states_rexp = ''
for o in get_states_dict():
    # states_rexp += '(?:{0})|'.format(o.replace('.', '\.'))
    states_rexp += '(?:{0})|'.format(re.sub(r'(\w)\.(\w)\.', r'\1. ?\2.', o).replace('.', '\.'))

states_rexp = states_rexp[:len(states_rexp) - 1]
body_rexp = states_rexp + '|(?:U\.S\.)'

title_rexp = 'Tit\. ?({0})'.format(section_numeral_rexp)
part_rexp = 'pt\. ?({0})'.format(section_numeral_rexp)
division_rexp = 'div\. ?({0})'.format(section_numeral_rexp)
paragraph_rexp = 'par\. ?({0})'.format(section_numeral_rexp)
article_rexp = 'Arts?\. ?({0})'.format(section_numeral_rexp)
chapter_rexp = 'ch?\. ?({0})'.format(section_numeral_rexp)
clause_rexp = 'cl\. ?({0})'.format(section_numeral_rexp)
section_rexp = r'(?:(?:§§? ?(?:(?:(?:(?:pp?\. ?)|(?:c\. ?)|(?:subc\. ?))?\d+[A-Za-z]{0,2}(?: ?\(\d{1,3}\))?(?:\. ?|, |-| to | at |,? and |:|; ?| ))+))+)'

document_location_rexp = r'(?:(?:(?:(?:(?:Tit\.)|(?:ch?\.)|(?:subc\.)|(?:pt\.)|(?:par\.)|(?:Arts?\.)|(?:cl\.)|(?:div\.)) ?(?:[MCLDXVI]+|\d+-?\.?:?)*),? ?(?:,? ?and )?)+)'

############################
# NATURAL AMENDMENT REGEX: #
############################

ordinals = {
    'First': '1',
    'Second': '2',
    'Third': '3',
    'Fourth': '4',
    'Fifth': '5',
    'Sixth': '6',
    'Seventh': '7',
    'Eighth': '8',
    'Ninth': '9',
    'Tenth': '10',
    'Eleventh': '11',
    'Twelfth': '12',
    'Thirteenth': '13',
    'Fourteenth': '14',
    'Fifteenth': '15',
    'Sixteenth': '16',
    'Seventeenth': '17',
    'Eighteenth': '18',
    'Nineteenth': '19',
    'Twentieth': '20',
    'Twenty-first': '21',
    'Twenty-second': '22',
    'Twenty-third': '23',
    'Twenty-fourth': '24',
    'Twenty-fifth': '22',
    'Twenty-sixth': '23',
    'Twenty-seventh': '24'
}

amends = (
    'amend\.',
    'Amendment',
    'amendment'
)

# create a regex for capturing ordinals
ordinal_variants = dict()
# create mappings of lowercase ordinals too
ordinal_rexp = ''
for o in ordinals:
    ordinal_rexp += '(?:{0})|(?:{1})|'.format(o, o.lower())
    ordinal_variants[o.lower()] = ordinals[o]
    ordinal_variants[o] = ordinals[o]
ordinal_rexp = ordinal_rexp[:-1]  # remove extra '|' symbol

# create a regex for the word "Amendment" + variations
amend_rexp = ''
for o in amends:
    amend_rexp += '(?:{0})|'.format(o)
amend_rexp = amend_rexp[:-1]  # remove extra '|' symbol

# add the two rexps for a natural, verbal listing of amendment references
# (eg. "the First, Second and Third Amendments")
#
# The regex is structured as follows:
# Group 1: 1st ordinal (From above example, "First"
# Group 3: Last ordinal after "and" if present (From above, Third)
# Group 2: The list of comma-separated (accepting Oxford comma as well) middle ordinals

informal_amend_rexp = '({0})' \
                      '(?:((?:, (?:{0}))*)(?:,? and ({0})))* ' \
                      '(?:{1})' \
    .format(ordinal_rexp, amend_rexp)

##################################
# CONSTITUTIONAL CITATION REGEX: #
##################################

const_cit_rexp = '({0}) ' \
                 '(?:(?:Const\.)|(?:CONST\.)) ' \
                 '((?:art\.)|(?:amend\.)|(?:ART\.)|(?:AMEND\.)|(?:Art\.)|(?:Amend\.)) ' \
                 '({1})' \
                 '(?:, § ?({1})' \
                 '(?:, cl. ?({1}))?)?' \
    .format(body_rexp, numeral_rexp)

###########################
# STATUTE CITATION REGEX: #
###########################

federal_statute_cit_rexp = '(\d+) U\. ?S\. ?C\. § ?(\d+)((?:\(.\))+)?'
# state_statute_cit_rexp = '({0}) (?:\w+\W+ )?(?:Code)? (\w+\W )+§§? (\d+\W? ?)+ ' \
# state_statute_cit_rexp = (r'({0}) '  # state
#                           r'((?: ?\w{{0,}}\W*? ){{1,7}}?)'  # doc title
#                           r'(?:'  # start alternating so we can get either doc loc, doc section or both
#                           r'({2})'  # doc location
#                           r'|'  # OR
#                           r'({1})'  # section
#                           r'){{1,2}} ?'  # capt either doc location, section or both
#                           r'(?:\((?: ?\w{{0,}}\W*? ){{0,3}}?(\d{{4}})\))?'  # date
#                           ) \
#     .format(
#     states_rexp,
#     section_rexp,
#     document_location_rexp,
# )

state_statute_cit_rexp = (r'({0}) '  # state
                          r'((?: ?\w+\W* ){{0,7}})'  # doc title
                          r'(?:'  # start alternating so we can get either doc loc, doc section or both
                          r'({2})'  # doc location
                          r'|'  # OR
                          r'({1})'  # section
                          r'){{1,2}} ?'  # capt either doc location, section or both
                          r'(?:\((?: ?\w*\W* ){{0,3}}(\d{{4}})\))?'  # date
                          ) \
    .format(
    states_rexp,
    section_rexp,
    document_location_rexp,
)

###### AM July 2017 ##############
# Acts, Treaties, Codes, and Rules
##################################

of_date_pattern = '(of *((('+month+')'+'(( ([1-9]|[0-2][0-9]|3[01]),)|,)?'+' ((17|18|19|20)[0-9][0-9]))|((17|18|19|20)[0-9][0-9])))'

## of_phrase = '(of( *[A-Z][a-z]+){1,3})|'+of_date_pattern
of_phrase = of_date_pattern+'|(of( *[A-Z][a-z]+){1,3})'
## of date_pattern = of = date_pattern (see find_case_citations5, but make case sensitive?

rule_word = '([Cc]ode|[aA]ct|[tT]reaty|[rR]ule)'

rule_word_filter = re.compile('[ -]'+rule_word+'([ —-]|$)')

act_name1 = '(([tT]he *)?(([A-Z][a-z\.]*)[ —-]*)+'+rule_word+')'

act_name2 = '(([tT]he *)?(([A-Z][a-z\.]*)[ —-]*)+of *(([A-Z][a-z\.]*) *)+'+rule_word+')'

act_name3 = '(([tT]he *)?([A-Z][a-z\.]*[ —-]*)+'+rule_word+' *('+of_phrase+'))'

act_name = '('+act_name3+'|'+act_name2+'|'+act_name1+')'

act_abbrev = '( +\([A-Z]+\.?\))?'

# section_pattern = '(§|Section [0-9a-z\(\)]+,?)?'
# section_pattern = '((§|Section) +[0-9a-z\(\)]+,?)'
section_pattern = '((§|Section) +[0-9a-z\(\)]+,? *(?:'+ordinal_rexp+' +)?)'
## section_pattern = '((§|Section) +(?:(?:(?:[0-9a-z\(\),])|'+ordinal_rexp+') +)+)'

section_expression = re.compile(section_pattern)

legislation_id = '((ch?\. *[0-9ixlvc]+, *)*'+section_pattern+'? *'+'([0-9]+(, [0-9]+)* [sS]tat\. [0-9]+(, [0-9-]+)?))'
## we assume that chapters can be numbered with romain numerals that are lowercase and less than 400,
## and thus combos of ixlvc

pub_pattern = '( *Pub L. No [0-9-]+(,?))?'

optional_year = '( *\([0-9]{4}\))?'

optional_full_date = '(('+full_date+'),?)*'

## act_pattern = act_name + ' *' + section_pattern + ' *'+ legislation_id
act_pattern = '('+ section_pattern+' *of *)?'+act_name + act_abbrev+'(,? *' + optional_full_date + pub_pattern + section_pattern +'?' +'( *' + legislation_id +')?' + optional_year+')?'
## group 3 = name
## 52 = Pub L. No X-Y
## 2 or 54 = section number
## 57 = chapter group
## 58 = leg ID including "number Stat. numbers, numbers"
## 12, 23, 39, 61 -- possible date slots
abbrev_act_pattern = ''
abbrev_act_expression = re.compile('$a') ## initialized to a pattern
                                         ## that doesn't match
                                         ## anything. Updated when
                                         ## dictionary items are
                                         ## added.

def make_current_abbrev():
    out = ''
    for key in act_abbrev_dictionary:
        out = out + '|' + key
    return(out[1:])

def make_abbrev_act_pattern ():
    global abbrev_act_pattern
    global abbrev_act_expression
    current_abbrev = make_current_abbrev()
    abbrev_act_pattern = '('+ section_pattern+' *of *)?([Tt]he )?[\(\[]?('+current_abbrev +')[\)\]]?(,? *' + optional_full_date + pub_pattern + section_pattern +'?' +'( *' + legislation_id +')?' + optional_year+')?'
    abbrev_act_expression = re.compile(abbrev_act_pattern)


act_expression = re.compile(act_pattern)

legislation_id_expression = re.compile(legislation_id)

###AM 7/2018 #############################
# Regulations with sections
##########################################

# number + initials of acgency + optional § + section number + (optional modifier + optional year)

regulation_with_section = '([0-9]+) *([A-Z\.]+) *§? *([0-9]+)'+' *(\(([A-Z][a-z]+)? *([0-9]{4})\))?'
regulation_expression = re.compile(regulation_with_section)
## 1 title number
## 2 agency (agency is required)
## 3 section number
## 5 publisher
## 6 date

###########################################
# NATURAL CONSTITUTIONAL REFERENCE REGEX: #
###########################################

informal_const_rexp = '((?:[tT]he)|(?:[oO]ur))?(?: (?:Federal)|(?:United States))? Constitution(?: of the United States)?'


###################
# UTIL FUNCTIONS: #
###################


def ordinal_to_number(ordinal_string):
    """Returns numerical value of given ordinal string

    :param ordinal_string:
    :return: the numerical value of the ordinal
    """
    if ordinal_string in ordinal_variants:
        return ordinal_variants[ordinal_string]
    else:
        return 0


def replace_roman_nums_with_ints(num_string):
    """Returns the given string with Roman numerals converted to Hindu-Arabic Numerals

    :param num_string:
    :return:
    """

    if not num_string:
        return ''

    roman_num_rexp_cap = '({0})'.format(roman_num_rexp)
    arabized_num_string = re.sub(
        roman_num_rexp_cap,
        lambda matchobj: '{}'.format(roman.fromRoman(matchobj.group(1))),
        num_string,
    )

    return arabized_num_string


def body_abbrev_to_full(abbrev):
    """Returns a full state name given an abbreviation, or "U.S." if "U.S." is given

    :param abbrev:
    :return:
    """
    bodies = get_states_dict()
    bodies['U.S.'] = 'Federal'
    bodies['U. S.'] = 'Federal'
    ## return bodies[abbrev.replace(' ', '')]
    return bodies[re.sub(' +','',abbrev)]


##################
# CAPTURE LOGIC: #
##################

def extract_section_number(instring):
    start = 0
    section_check = re.compile('§|[sS]ection *')
    section_indicator = section_check.search(instring,start)
    while section_indicator:
        start = section_indicator.end()
        section_indicator = section_check.search(instring,start)
    instring = instring[start:]
    outstring = ''
    for word in instring.split(' '):
        if (len(word)>0) and re.search('[^a-zA-Z]',word[-1]) and (word[:-1] in ordinal_variants):
            outstring = outstring + ' ' + ordinal_variants[word[:-1]]+word[-1]
        elif word in ordinal_variants:
            outstring = outstring + ' ' + ordinal_variants[word]
        else:
            outstring = outstring + ' ' + word
    return(outstring.strip(', '))
        

def capture_informal_amendment_ordinals(in_string):
    """Returns list of strings matching the informal amendments rexp in given string

    Returns a list of strings, the 0th of which is the whole string
    The 1st and last elements are the first and last listed ordinals per the informal_amend_rexp
    The middle elements are the 2nd group from the informal_amend_rexp split and spread into a list
    :param in_string: (str) the string to search in
    :return: a list of strings
    """

    result = []
    full_amend_pattern = re.compile(informal_amend_rexp)
    amend_matches = full_amend_pattern.finditer(in_string)
    for amend_match in amend_matches:
        result.append({'ordinal': amend_match.group(1), 'match': amend_match.group(0),
                       'start': amend_match.start()})
        # The middle group is a string of the comma separated amendment
        # mentions between the first and last mentions
        # It will be split such that empty strings are possible
        # Thus they are filtered out
        if amend_match.group(2):
            result.extend(
                list(map(lambda x: {'ordinal': x, 'match': amend_match.group(0), 'start': amend_match.start()},
                         filter(lambda x: x, amend_match.group(2).split(", ")))))
        if amend_match.group(3):
            result.append({'ordinal': amend_match.group(3), 'match': amend_match.group(0),
                           'start': amend_match.start()})
    return result


def capture_const_cits(in_string):
    """Returns a list of strings, each corresponding to the match groups in the constitutional amendment/article
    citation rexp

    :param in_string:
    :return:
    """
    const_pattern = re.compile(const_cit_rexp)
    matches = const_pattern.finditer(in_string)
    if matches:
        # return [
        #     match.group(0),  # matched string
        #     match.group(1),  # jurisdiction
        #     match.group(2),  # article | amendment?
        #     match.group(3),  # article/amend num
        #     match.group(4),  # section
        #     # match.group(5),  # clause
        # ]
        return matches
    else:
        return []


def capture_informal_constitutional_refs(in_string):
    """Returns list of strings matching the informal amendments rexp in given string

    Returns a list of strings, the 0th of which is the whole string
    The 1st and last elements are the first and last listed ordinals per the informal_amend_rexp
    The middle elements are the 2nd group from the informal_amend_rexp split and spread into a list
    :param in_string: (str) the string to search in
    :return: a list of strings
    """

    const_ref_pattern = re.compile(informal_const_rexp)
    matches = const_ref_pattern.finditer(in_string)
    if matches:
        return matches
        # match.group(0),  # matched string
        # ]
    else:
        return []


def capture_federal_statute_cits(in_string):
    """Returns a list of strings, each corresponding to match groups in the federal statute citation rexp

    :param in_string:
    :return:
    """
    const_pattern = re.compile(federal_statute_cit_rexp)
    matches = const_pattern.finditer(in_string)
    if matches:
        return matches
    else:
        return []

def extract_chapter_from_state_name(instring):
    chapter_match = re.search('ch?\. *[0-9]+, *',instring)
    if chapter_match:
        state_piece = instring[:chapter_match.start()]
        chapter_piece = instring[chapter_match.start():]
    else:
        state_piece = instring
        chapter_piece = ''
    return(state_piece,chapter_piece)

def state_well_formed_start(start,instring):
    ## can add additional pararameters and constraints

    ## first constraint: state match must start word or sequence of
    ## abreviated symbols
    # print(start)
    # print('*')
    # if instring:
    #     print(len(instring))
    # else:
    #     print('No instring')
    if start == 0:
        return(True)
    elif not instring[start-1] in ' ':
        return(False)
    else:
        previous_word = re.search('[^ ]* +',instring[:start])
        if not previous_word:
            return(True)
        elif re.match('[A-Z][a-zA-Z]* +$',previous_word.group(0)):
            return(False)
        else:
            return(True)

def capture_state_statute_cits(in_string):
    """Returns a list of strings, each corresponding to match groups in the state statute citation rexp

    :param in_string:
    :return:
    """
    const_pattern = re.compile(state_statute_cit_rexp)
    matches = list(const_pattern.finditer(in_string))

    res = []

    for match in matches:
        state = match.group(1)
        state_piece,chapter_piece = extract_chapter_from_state_name(match.group(2))
        document = '{} {}'.format(state, state_piece)
        section = (match.group(4) or '').strip()
        date = match.group(5)
        if match.group(3):
            doc_loc = chapter_piece + match.group(3) 
        else:
            doc_loc = chapter_piece
        article_match = re.compile(article_rexp).search(doc_loc) if doc_loc else ''
        chapter_match = re.compile(chapter_rexp).search(doc_loc) if doc_loc else ''
        title_match = re.compile(title_rexp).search(doc_loc) if doc_loc else ''
        if state_well_formed_start(match.start(1),in_string):
            res.append([
                match.group(0),  # matched string
                state,  # state
                document,
                article_match.group(1) if article_match else '',  # article
                chapter_match.group(1) if chapter_match else '',  # chapter
                title_match.group(1) if title_match else '',  # title
                extract_section_number(section),  # section
                doc_loc,
                date if date else '',
                match.start()
        ])
    return res

def get_publ_from_string(instring):
    if instring:
        number_match = re.search('[0-9-]+',instring)
        if number_match:
            return(number_match.group(0))
        else:
            return(False)
    else:
        return(False)

def adjust_act_output_for_final_chars(name,name_end,match):
    name2 = name.rstrip(' ,')
    diff = match.end()-name_end
    if (name2 != name) and (name_end == match.end()):
        whole_string = match.group(0).rstrip(' ,')
        diff = len(match.group(0))-len(whole_string)
        match_end = match.end()-diff
    elif (name_end != match.end()) and (not re.search('[0-9a-zA-Z]',match.group(0)[-1*diff:])):
        match_end = name_end
        whole_string = match.group(0)[:(-1 * diff)]
    else:
        whole_string = match.group(0)
        match_end = match.end()
    return(name2,whole_string,match.start(),match_end)

def adjust_act_output_for_pre_citation_words(name,output_string,start_offset,end_offset):
    pre_citation_regexp = ''
    for word in pre_citation_words:
        pre_citation_regexp += word + '|'
    pre_citation_regexp.strip('|') ## remove final disjunction 
    pre_citation_pattern = re.compile('^'+'('+pre_citation_regexp+')[ \.]+',re.I)
    match = pre_citation_pattern.search(name)
    if output_string.startswith(name) and match:
        change = len(match.group(0))
        name = name[change:]
        output_string = output_string[change:]
        start_offset = start_offset + change
    return(name,output_string,start_offset,end_offset)

def pages_check(pages):
    ## if comma is in string, makes sure that
    ## pages are in sort order
    page_list = pages.split(',')
    consec = True
    last_page = False
    out_string = ''
    for page in page_list:
        if not consec:
            pass
        elif ('-' in page):
            pages2 = page.split('-')
            one_page = pages2[-1].strip(' ')
            if one_page.isdigit():
                one_page = int(one_page)
                if (not last_page) or (one_page>last_page):
                    last_page = one_page
                    out_string += page+','
                else:
                    consec = False
        else:
            one_page = page.strip(' ')
            if one_page.isdigit():
                one_page = int(one_page)
                if (not last_page) or (one_page>last_page):
                    last_page = one_page
                    out_string +=page+','
                else:
                    consec = False
    out_string = out_string.strip(',')
    if consec:
        return(pages,0)
    elif pages.startswith(out_string):
        diff = len(pages)-len(out_string)
        return(out_string,diff)
    else:
        print('pages_check worked wrong')
        print('input:','*'+pages+'*')
        print('output:','*'+out_string+'*')
        return(pages,0)
    
           

def get_volume_and_pages_from_stat_text(intext,volume_end,match_end):
    ## example: 89 Stat. 801
    ##  volume 89, page 801
    ## edited version of legislation_id pattern above
    pattern_match = re.compile('(c\. *)?([0-9]+(, [0-9]+)*) [sS]tat\. ([0-9]+(, [0-9-]+)?)')
    match = pattern_match.search(intext)
    end_modifier = 0
    if match:
        volume = match.group(2)
        pages = match.group(4)
        pages1 = pages
        if (volume_end == match_end) and (',' in pages):
            pages,end_modifier = pages_check(pages)
            # print(intext)
            # print(1,volume)
            # print(2.1,'*'+pages1+'*',2.2,'*'+pages+'*')
            # print(3,end_modifier)
        ## input('pause')
        return(volume,pages,end_modifier)
    else:
        return(False,False,end_modifier)
    
def get_chapters_from_text(intext):
    if intext:
        output = ''
        chapters = re.finditer('[0-9]+',intext)
        for chapter in chapters:
            output +=chapter.group(0)+', '
        return(output.strip(', '))
    else:
        return(False)
    
def update_abbrev_dict(abbrev,name):
    name = name.upper()
    if abbrev in act_abbrev_dictionary:
        if not name in act_abbrev_dictionary[abbrev]:
            act_abbrev_dictionary[abbrev].append(name)
            make_abbrev_act_pattern() ## update search pattern
    else:
        act_abbrev_dictionary[abbrev]= [name]
        make_abbrev_act_pattern() ## update search pattern

def extract_act_abbreviation(abbrev,name):
    ## tests whether abbrev is a possible abbrev for name
    ## this is a somewhat leanient test based on the
    ## typical abbreviation extraction heuristics
    abbrev = abbrev.strip('() ')
    test_name = name.lower()
    for char in abbrev.lower():
        if (char in 'abcdefghijklmnopqrstuvwxyz') and (not char in test_name):
            return(False)
            ## true abbreviations rarely include letters that are not in full name
    abbrev_index = 0
    next_abbrev_char = abbrev[abbrev_index]
    for word in name.split(' '):
        if (len(word) == 0):
            pass ## this accounts for extra space that serves no purpose
        elif (word[0] == next_abbrev_char):
            abbrev_index += 1
            if abbrev_index==len(abbrev):
                update_abbrev_dict(abbrev,name)
                return(abbrev)
            else:
                next_abbrev_char = abbrev[abbrev_index]
                if len(word)>1:
                    for char in word[1:]:
                        if char == abbrev[abbrev_index]:
                            abbrev_index += 1
                            next_abbrev_char = abbrev[abbrev_index]
                            if abbrev_index==len(abbrev):
                                update_abbrev_dict(abbrev,name)
                                return(abbrev)
                        else:
                            break
    return(False)

        ## section paren 3,57,62
def make_act_xml(match,line,offset,file_id,cit_num,next_match,line_string):
    ## need to find out more for c. and ch.
    ## possibly other abbreviations missing 57 **
    anaphoric_check = re.compile('^[tT](he|hat|his) *'+rule_word+'$')
    if match:
        name = match.group(4)
        end_modifier = False
        if anaphoric_check.match(name): ## match looks for exact match
            anaphoric_act='True' ## must be string for print out
        else:
            anaphoric_act=False
        name,output_string,start_offset,end_offset = adjust_act_output_for_final_chars(name,match.end(4),match)
        name,output_string,start_offset,end_offset = adjust_act_output_for_pre_citation_words(name,output_string,start_offset,end_offset)
        if match.group(38):
            abbrev = extract_act_abbreviation(match.group(38),name)
        else:
            abbrev = False
        start_offset = start_offset + offset
        end_offset = end_offset + offset
        publ = get_publ_from_string(match.group(54))
        if match.group(2) and re.search('[0-9]',match.group(2)): ## *** 57 ***
            section_number = extract_section_number(match.group(2)) ## .strip(' §,')
        elif match.group(56) and re.search('[0-9]',match.group(56)):
            section_number = extract_section_number(match.group(56)) 
        elif match.group(61) and re.search('[0-9]',match.group(61)):
            section_number = extract_section_number(match.group(61))
        else:
            if next_match:
                section_match = section_expression.search(line_string[:next_match.start()],match.end())
            else:
                # print(line_string)
                # print(match.end())
                section_match = section_expression.search(line_string,match.end())
            if section_match and ((section_match.start()-match.end())<10):
                section_number =  extract_section_number(section_match.group(0))
                end_offset = section_match.end() + offset
                output_string = line_string[(start_offset-offset):(end_offset-offset)]
                ## under right circumstances add a section pattern after end of string
                ## update final offset and update output string
            else:
                section_number = False
        if match.group(60):
            chapters = get_chapters_from_text(match.group(60))
        else:
            chapters = False
        if match.group(63):
            volume,pages,end_modifier = get_volume_and_pages_from_stat_text(match.group(63),match.end(63),match.end())
            ## ** 57 ** add constraint on pages here
            ## a) divide pages by comma
            ## b) if pages after comma are less than before comma
            ##    then: i) pages after comma should be ruled out
            ##          ii) final endpoint should be adjusted
            ## 80 Stat. 931, 944-47
            ## volume stat pages
        else:
            volume = False
            pages = False
        date = False
        for position in [11,24,41,66]:
            ## not sure about 24
            if match.group(position) and re.search('[0-9]',match.group(position)):
                temp_date = match.group(position)
                if not date:
                    date = temp_date
                elif (date.lower() != temp_date.lower()) and (date.lower() in temp_date.lower()):
                    date = temp_date
        if date:
            date = date.strip(' ').upper()
        cit_id = file_id + str(cit_num)
        output = '<citation id=\"'+cit_id+'\"'
        if end_modifier:
            end_offset = end_offset-end_modifier
            output_string = output_string[:-1*end_modifier]
        for key,value in [['entry_type','act_treaty_code_rule'],
                          ['start',str(start_offset)],
                          ['end',str(end_offset)],
                          ['line',str(line)],
                          ['document',name],
                          ['abbreviation',abbrev],
                          ['anaphoric_act',anaphoric_act],
                          ['public_law_number',publ],
                          ['section',section_number],
                          ['volume',volume],
                          ['chapter',chapters],
                          ['pages',pages],
                          ['date',date]]:
            if value and re.search('[a-zA-Z0-9]',value):
                output = output+' '+key+'="'+value+'"'
        output = output+'>'+output_string+'</citation>'
        return(output,start_offset,end_offset)

def agency_check(agency):
    if not re.search('[A-Za-z].*[A-Za-z]',agency):
        ## there must be at least 2 letters in an agency name
        return(False)
    elif court_reporter_check.search(agency):
        ## if a court reporter abbreviation, we assume it cannot also
        ## be an agency abbreviation
        return(False)
    else:
        return(True)

def make_reg_xml(match,line,offset,file_id,cit_num):
    if match:
        if match.group(1) and re.search('[0-9]',match.group(1)):
            title_number = match.group(1)
        else:
            title_number = False
        if match.group(2) and re.search('[^ ]', match.group(2)):
            agency = match.group(2)
            if not agency_check(agency):
                agency = False
        else:
            agency = False
        if not agency:
            return(False)
        if match.group(3) and re.search('[0-9]',match.group(3)):
            section_number = extract_section_number(match.group(3))
        else:
            section_number = False
        if match.group(5) and re.search('[0-9]',match.group(5)):
            publisher = match.group(5)
        else:
            publisher = False
        if match.group(6) and re.search('[0-9]',match.group(6)):
            date = match.group(6)
        else:
            date = False
        start_offset = match.start() + offset
        end_offset = match.end() + offset
        cit_id = file_id + str(cit_num)
        output = '<citation id=\"'+cit_id+'\"'
        if agency and (not ' ' in agency):
            lookup1 = agency.upper()
            if lookup1 in agency_abbrev_dictionary:
                full_form = agency_abbrev_dictionary[lookup1]
            elif '.' in lookup1:
                lookup2 = re.sub('\.','',lookup1)
                if lookup2 in agency_abbrev_dictionary:
                    full_form = agency_abbrev_dictionary[lookup2]
                else:
                    full_form = False
            else:
                full_form = False
            if full_form:
                abbrev = agency
                agency = full_form
            else:
                abbrev = False
        for key,value in [['entry_type','regulation'],
                          ['start',str(start_offset)],
                          ['end',str(end_offset)],
                          ['line',str(line)],
                          ['agency',agency],
                          ['agency_abbrev',abbrev],
                          ['publisher',publisher],
                          ['title',title_number],
                          ['section',section_number],
                          ['date',date]]:
            if value:
                output = output+' '+key+'="'+value+'"'
        output = output+'>'+match.group(0)+'</citation>'
        return(output)

def get_next_lettered_word(line,start):
    lettered_word = re.compile('[A-Za-z]+')
    next_word = lettered_word.search(line,start)
    if next_word:
        return(next_word.group(0),next_word.start(),next_word.end())
    else:
        return(False,False,len(line))

def choose_best_antecedent(abbrev,possible_full_forms):
    ## for now, choose shortest full form that previously satisfied
    ## the antecedent criteria (see extract_act_abbreviation)
    possible_full_forms.sort(key = lambda x: len(x))
    return(possible_full_forms[0])

def find_abbrev_act_xml_old (line,line_num,offset,file_id,cit_num,act_start_and_ends):
    output = []
    start = 0
    last_word = False
    last_word_start = False
    if len(act_start_and_ends)>0:
        next_blocked_start,next_blocked_end = act_start_and_ends.pop(0)
    while start < len(line):
        if (start >= next_blocked_end) and (start < next_blocked_end):
            start = next_blocked_end
            if len(act_start_and_ends)>0:
                next_blocked_start,next_blocked_end = act_start_and_ends.pop(0)
        next_word,word_start,word_end = get_next_lettered_word(line,start)
        start = word_end
        if next_word in act_abbrev_dictionary:
            name_end = word_end
            results = act_abbrev_dictionary[next_word]
            publ = False
            date = False
            section_number = False
            chapters = False
            if len(results)==1:
                full_form = results[0]
            else:
                full_form = choose_best_antecedent(next_word,results)
            if last_word.lower() == 'the':
                name_start = last_word_start
            else:
                name_start = word_start
            name = line[name_start:name_end]
            start_offset = name_start + offset
            next_leg = legislation_id_expression.search(line,start)
            end_modifier = False
            if next_leg and not re.search('[a-zA-Z]',line[word_end:next_leg.start()]):
                ## make sure legislation is close "enough"
                print(next_leg.group(0)) 
                volume,pages,end_modifier = False,False,False
                ## get_volume_and_pages_from_stat_text(next_leg
            else:
                volume,pages,end_modifier = False,False,False
            output_string = line[name_start:name_end] 
            ## change to account for leglisation_id stuff
            end_offset = word_end + offset
            cit_id = file_id + str(cit_num)
            cit_num += 1
            output_entry = '<citation id=\"'+cit_id+'\"'
            if end_modifier:
                end_offset = end_offset - end_modifier
                ## output string modify also ???
            ## change after leg id fixed up
            for key,value in [['entry_type','act_treaty_code_rule'],
                              ['start',str(start_offset)],
                              ['end',str(end_offset)],
                              ['line',str(line_num)],
                              ['document',name],
                              ['full_form',full_form],
                              ['anaphoric_act','True'],
                              ['public_law_number',publ],
                              ['section',section_number],
                              ['volume',volume],
                              ['chapter',chapters],
                              ['pages',pages],
                              ['date',date]]:
                if value and re.search('[a-zA-Z0-9]',value):
                    output_entry = output_entry+' '+key+'="'+value+'"'
            output_entry = output_entry+'>'+output_string+'</citation>'
            output.append(output_entry)
        last_word = next_word
        last_word_start = word_start
    return(output)

def is_non_word_substring(line,start,end):
    if (start == 0) or  not re.search('[a-zA-Z]',line[start-1]):
        word_start = True
    else:
        word_start = False
    if (end == len(line)) or not re.search('[a-zA-Z]',line[end]):
        word_end = True
    else:
        word_end = False
    if (not word_start) or (not word_end):
        return(True)
    else:
        return(False)

def get_next_abbrev_match(line,start):
    match = False
    while (start < len(line)) and (match==False):
        match = abbrev_act_expression.search(line,start)
        if match and is_non_word_substring(line,match.start(),match.end()):
            start = match.end()
            match = False
        elif not match:
            start = len(line)
    return(match)
                                                
def find_abbrev_act_xml(line,line_num,offset,file_id,cit_num,act_start_and_ends):
    output = []
    start_end_offsets_out = []
    start = 0
    if len(act_start_and_ends)>0:
        next_blocked_start,next_blocked_end = act_start_and_ends.pop(0)
        offset_filter = True
    else:
        offset_filter = False
        next_blocked_start,next_blocked_end = False, False
    match = False
    while start < len(line):
        while offset_filter and (start >= next_blocked_start) and (start < next_blocked_end):
            start = next_blocked_end
            if len(act_start_and_ends)>0:
                offset_filter = True
                next_blocked_start,next_blocked_end = act_start_and_ends.pop(0)
            else:
                offset_filter = False
                next_blocked_start,next_blocked_end = False, False
        match = get_next_abbrev_match(line,start)
        if not match:
            start = len(line)
        else:
            while match and offset_filter and (match.start() >= next_blocked_end):
                if len(act_start_and_ends)>0:
                    next_blocked_start,next_blocked_end = act_start_and_ends.pop(0)
                else:
                    offset_filter = False
                    next_blocked_start,next_blocked_end = False, False
            ## this gets rid of irrelevant start and ends that are before the match
            if offset_filter and (match.start() >= next_blocked_start):
                start = match.end()              
                match = False  
            else:
                ## (not next_blocked_end) or (match.end() <= next_blocked_start):
            ## only precede if the match ends before the blocked area
                name = match.group(5)
                full_forms = act_abbrev_dictionary[name]
                if len(full_forms) == 1:
                    full_form = full_forms[0]
                else:
                    full_form = choose_best_antecedent(name,full_forms)
                if match.group(21) and re.search('[0-9]',match.group(21)):
                    publ = match.group(21)
                else:
                    publ = False
                if match.group(2) and re.search('[0-9]',match.group(2)):
                    section_number = extract_section_number(match.group(2))
                elif match.group(23) and re.search('[0-9]',match.group(23)):
                    section_number = extract_section_number(match.group(23))
                elif match.group(28) and re.search('[0-9]',match.group(28)):
                    section_number = extract_section_number(match.group(28))
                else:
                    section_number = False
                if match.group(27):
                    chapters = get_chapters_from_text(match.group(27))
                else:
                    chapters = False
                if match.group(30):
                    volume,pages,end_modifier = get_volume_and_pages_from_stat_text(match.group(30),match.end(30),match.end())
                else:
                    volume,pages,end_modifier = False, False, False
                if match.group(8) and re.search('[0-9]',match.group(6)):
                    date = match.group(8)
                elif match.group(33) and re.search('[0-9]',match.group(33)):
                    date = match.group(33)
                else:
                    date = False                
                if date:
                    date = date.strip(' ').upper()
                output_string = match.group(0)
                start_offset = match.start() + offset
                end_offset = match.end() + offset
                if end_modifier:
                    output_string = output_string[:-1*end_modifier]
                    end_offset = end_offset - end_modifier
                cit_id = file_id + str(cit_num)
                cit_num += 1
                output_entry = '<citation id=\"'+cit_id+'\"'
                for key,value in [['entry_type','act_treaty_code_rule'],
                    ['start',str(start_offset)],
                    ['end',str(end_offset)],
                    ['line',str(line_num)],
                    ['document',full_form],
                    ['abbreviation',name],
                    ['anaphoric_act','True'],
                    ['public_law_number',publ],
                    ['section',section_number],
                    ['volume',volume],
                    ['chapter',chapters],
                    ['pages',pages],
                    ['date',date]]:
                    if value and re.search('[a-zA-Z0-9]',value):
                        output_entry = output_entry+' '+key+'="'+value+'"'
                if end_offset:
                    start_end_offsets_out.append([start_offset,end_offset])                    
                output_entry = output_entry+'>'+output_string+'</citation>'
                output.append(output_entry)
                start = match.end()
    return(output,start_end_offsets_out)

def get_next_unnamed_act(line,start):
    match = legislation_id_expression.search(line,start)
    return(match)

def find_unnamed_acts_xml(line,line_num,offset,file_id,cit_num,act_start_and_ends):
    output = []
    start_end_offsets_out = []
    start = 0
    if len(act_start_and_ends)>0:
        next_blocked_start,next_blocked_end = act_start_and_ends.pop(0)
        offset_filter = True
    else:
        offset_filter = False
        next_blocked_start,next_blocked_end = False, False
    match = False
    while start < len(line):
        match = get_next_unnamed_act(line,start)
        while offset_filter and (start >= next_blocked_start) and (start < next_blocked_end):
            start = next_blocked_end
            if len(act_start_and_ends)>0:
                offset_filter = True
                next_blocked_start,next_blocked_end = act_start_and_ends.pop(0)
            else:
                offset_filter = False
                next_blocked_start,next_blocked_end = False, False
                match = get_next_unnamed_act(line,start) ## ** 57 **
        if not match:
            start = len(line)
        else:
            while match and offset_filter and (match.start() >= next_blocked_end):
                if len(act_start_and_ends)>0:
                    next_blocked_start,next_blocked_end = act_start_and_ends.pop(0)
                else:
                    offset_filter = False
                    next_blocked_start,next_blocked_end = False, False
            ## this gets rid of irrelevant start and ends that are before the match
            if offset_filter and (match.start() >= next_blocked_start):
                start = match.end()              
                match = False  
            else:
                if match.group(2):
                    chapters = get_chapters_from_text(match.group(2))
                else:
                    chapters = False
                if match.group(3):
                    section_number = extract_section_number(match.group(3))
                else:
                    section_number = False
                if match.end(5):
                    volume,pages,end_modifier= get_volume_and_pages_from_stat_text(match.group(5),match.end(5),match.end())
                else:
                    print('Weird that this one matched at all',match.group(0))
                    start = match.end()
                    match = False
                if match:
                    output_string = match.group(0)
                    start_offset = match.start() + offset
                    end_offset = match.end() + offset
                    if end_modifier:
                        output_string = output_string[:-1*end_modifier]
                        end_offset = end_offset - end_modifier
                    cit_id = file_id + str(cit_num)
                    cit_num += 1
                    output_entry = '<citation id=\"'+cit_id+'\"'
                    for key,value in [['entry_type','act_treaty_code_rule'],
                        ['start',str(start_offset)],
                        ['end',str(end_offset)],
                        ['document','NAME UNSPECIFIED'],
                        ['line',str(line_num)],
                        ['section',section_number],
                        ['volume',volume],
                        ['chapter',chapters],
                        ['pages',pages]]:
                        if value and re.search('[a-zA-Z0-9]',value):
                            output_entry = output_entry+' '+key+'="'+value+'"'
                    if end_offset:
                        start_end_offsets_out.append([start_offset,end_offset])                
                    output_entry = output_entry+'>'+output_string+'</citation>'
                    output.append(output_entry)
                    start = match.end()
    return(output,start_end_offsets_out)
            
def generate_other_leg_citations_from_string(line,offset,line_num,leg_count,file_id):
    acts = list(act_expression.finditer(line))
    regs = regulation_expression.finditer(line)
    output = []
    new_cits = 0
    act_start_and_ends = []
    next_match = False
    count = 1
    maximum_index = len(acts)-1
    for match in acts:
        if count < maximum_index:
            next_match = acts[count]
        else:
            next_match = False
        count += 1
        if rule_word_filter.search(match.group(0)):
            new_cits = new_cits+1
            act_xml,start_off,end_off = \
              make_act_xml(match,line_num,offset,file_id,leg_count+new_cits,next_match,line)
            if act_xml:
                output.append(act_xml)
                act_start_and_ends.append([start_off-offset,end_off-offset])
            else:
                new_cits = new_cits-1
    for match in regs:
        new_cits = new_cits+1
        reg_xml = make_reg_xml(match,line_num,offset,file_id,leg_count+new_cits)
        if reg_xml:
            output.append(reg_xml)
        else:
            new_cits = new_cits-1
    act_start_and_ends.sort()
    abbrev_act_matches,start_end_offsets = find_abbrev_act_xml(line,line_num,offset,file_id,leg_count+new_cits+1,act_start_and_ends)
    new_cits += len(abbrev_act_matches)
    output.extend(abbrev_act_matches)
    if len(start_end_offsets)>0:
        act_start_and_ends.extend(start_end_offsets)
        act_start_and_ends.sort()
    unnamed_acts,more_start_ends = find_unnamed_acts_xml(line,line_num,offset,file_id,leg_count+new_cits+1,act_start_and_ends)
    if unnamed_acts:
        output.extend(unnamed_acts)
    if more_start_ends:
        act_start_and_ends.extend(more_start_ends)
        act_start_and_ends.sort()
    ## use act_start_and_ends to filter additional act types
    return(output)
            


def generate_legislation_citations_from_string(in_string, offset, line_num, leg_count, file_id):
    """Returns an array of citation strings from a given string

    :param in_string: string that matches natural amendment format
    :param offset: byte offset in file in_string starts from
    :param line_num: line number in file
    :param leg_count: index of the current legislation citation created from this file
    :param file_id: id of the file being read
    :return: list of citation strings
    """
    matches = {
        'amend_ref': list(capture_informal_amendment_ordinals(in_string)) or [],
        'const_cit': list(capture_const_cits(in_string)) or [],
        'const_ref': list(capture_informal_constitutional_refs(in_string)) or [],
        'federal_statute': list(capture_federal_statute_cits(in_string)) or [],
        'state_statute': list(capture_state_statute_cits(in_string)) or []
    }

    cits = []

    # 1. create pseudo citation object
    # 2. turn all into that
    # 3. sort list of pseudo cits
    # 4. THEN CONVERT TO CITATIONS!

    cits.extend(list(map(lambda x: {
        'type': 'amend_ref',
        'start_index': offset + x['start'],
        'end_index': offset + x['start'] + len(x['match']),
        'line_num': line_num,
        'cit_id': -1,
        'amend_num': ordinal_to_number(x['ordinal']),
        'text': str.strip(x['match'])
    }, matches['amend_ref'])))

    cits.extend(list(map(lambda x: {
        'type': 'const_cit',
        'start_index': offset + x.start(),
        'end_index': offset + x.start() + len(x.group(0)),
        'line_num': line_num,
        'cit_id': -1,
        'jurisdiction': body_abbrev_to_full(x.group(1)),
        'art_type': x.group(2),
        'article_num': replace_roman_nums_with_ints(x.group(3)),
        'section_num': extract_section_number(replace_roman_nums_with_ints(x.group(4))),
        'clause_num': replace_roman_nums_with_ints(x.group(5)),
        'text': str.strip(x.group(0))
    }, matches['const_cit'])))

    cits.extend(list(map(lambda x: {
        'type': 'const_ref',
        'start_index': offset + x.start(),
        'end_index': offset + x.start() + len(x.group(0)),
        'line_num': line_num,
        'cit_id': -1,
        'text': str.strip(x.group(0))
    }, matches['const_ref'])))

    cits.extend(list(map(lambda x: {
        'type': 'federal_statute',
        'start_index': offset + x.start(),
        'end_index': offset + x.start() + len(x.group(0)),
        'line_num': line_num,
        'cit_id': -1,
        'body': 'federal',
        'article': replace_roman_nums_with_ints(x.group(1)),
        'chapter': '',
        'section': extract_section_number(replace_roman_nums_with_ints(x.group(2))),
        'subsection': x.group(3),
        'text': str.strip(x.group(0)),
        'document': 'United States Code'
    }, matches['federal_statute'])))

    cits.extend(list(map(lambda x: {  # this one still processes a list not a match objet
        'type': 'state_statute',
        'start_index': offset + int(x[9]),  # temp: get offset from last list element of capture func
        'end_index': offset + int(x[9]) + len(x[0]),
        'line_num': line_num,
        'cit_id': -1,
        'body': body_abbrev_to_full(x[1]),
        'article': x[3],  # article
        'chapter': replace_roman_nums_with_ints(x[4]),  # chapter
        'section': extract_section_number(replace_roman_nums_with_ints(x[6])),  # section
        'subsection': x[7],  # subsection
        'text': str.strip(x[0]),  # full match text
        'document': x[2],
        'date': x[8],
    }, matches['state_statute'])))

    cits.sort(key=lambda cit: cit['start_index'])

    return generate_citation_strings_from_pseudo_cits(file_id, leg_count, cits)

def empty_feature_filter(instring):
    return(re.sub(' [a-z]+=""','',instring))

def generate_citation_strings_from_pseudo_cits(file_id, id_index, cits):
    def cit_convert(cit):
        if cit['type'] == 'amend_ref':
            del cit['type']
            return empty_feature_filter(generate_amendment_reference(**cit))
        elif cit['type'] == 'const_cit':
            del cit['type']
            return empty_feature_filter(generate_const_citation(**cit))
        elif cit['type'] == 'const_ref':
            del cit['type']
            return empty_feature_filter(generate_const_reference(**cit))
        elif cit['type'] == 'state_statute' or cit['type'] == 'federal_statute':
            del cit['type']
            return empty_feature_filter(generate_statute_citation(**cit))

    new_cits = []

    for index, cit in enumerate(cits, start=1):
        cit['cit_id'] = file_id + str(id_index + index)
        new_cits.append(cit_convert(cit))

    return new_cits


def generate_amendment_reference(
        start_index,
        end_index,
        line_num,
        cit_id,
        amend_num,
        text):
    """Return a citation string for an informal reference to an amendment

    :param start_index: (int) Byte offset of text from beginning of file
    :param end_index: (int) end of text
    :param line_num: (int) line number from read file
    :param cit_id: (int) the id num of this citation
    :param amend_num: (int) the number of the amendment being referred to
    :param text: (str) the text holding the amendment reference
    :return: (str) the citation string in XML style
    """
    ## changed from <refernce> AM May 2019
    citation = '<citation ' \
               'id="{0}" ' \
               'entry_type="amendment" ' \
               'start="{1}" ' \
               'end="{2}" ' \
               'line="{3}" ' \
               'amendment="{4}">' \
               '{5}' \
               '</citation>' \
        .format(
        cit_id,
        start_index,
        end_index,
        line_num,
        amend_num,
        text
    )

    return citation


def generate_const_citation(start_index, end_index, line_num, cit_id, jurisdiction, art_type, article_num, section_num,
                            clause_num, text):
    """Return a citation string for a constitutional amendment or article citation

    :param start_index:
    :param end_index:
    :param line_num:
    :param cit_id:
    :param jurisdiction:
    :param art_type:
    :param article_num:
    :param section_num:
    :param clause_num:
    :param text:
    :return:
    """

    art = re.search('((?:art\.)|(?:ART\.)|(?:Art\.))', art_type)
    if section_num:
        section_num = extract_section_number(section_num)
    if art:
        art_type = 'article'
    else:
        art_type = 'amendment'
    citation = '<citation ' \
               'id="{0}" ' \
               'entry_type="constitutional_{1}" ' \
               'start="{2}" ' \
               'end="{3}" ' \
               'line="{4}" ' \
               'jurisdiction="{5}" ' \
               'article="{6}" ' \
               'section="{7}" ' \
               'clause="{8}">' \
               '{9}' \
               '</citation>' \
        .format(
        cit_id,
        art_type,
        start_index,
        end_index,
        line_num,
        jurisdiction,
        article_num,
        section_num or '',
        clause_num or '',
        text
    )

    return citation


def generate_const_reference(start_index, end_index, line_num, cit_id, text):
    """Return a citation string for a constitutional amendment or article citation

    :param start_index:
    :param end_index:
    :param line_num:
    :param cit_id:
    :param text:
    :return:
    """
    ## changed from <reference 5/2019
    citation = '<citation ' \
               'id="{0}" ' \
               'entry_type="constitution" ' \
               'start="{1}" ' \
               'end="{2}" ' \
               'line="{3}">' \
               '{4}' \
               '</citation>' \
        .format(
        cit_id,
        start_index,
        end_index,
        line_num,
        text
    )

    return citation


def generate_statute_citation(start_index, end_index, line_num, cit_id, body, article, chapter, section, subsection,
                              text, document, date=''):
    """Returns a citation string for a statute citation

    :param document:
    :param date:
    :param start_index:
    :param end_index:
    :param line_num:
    :param cit_id:
    :param body:
    :param article:
    :param chapter:
    :param section:
    :param subsection:
    :param text:
    :return:
    """
    if section:
        section = extract_section_number(section)
    citation = '<citation ' \
               'id="{0}" ' \
               'entry_type="statute" ' \
               'start="{1}" ' \
               'end="{2}" ' \
               'line="{3}" ' \
               'body="{4}" ' \
               'document="{10}" ' \
               'article="{5}" ' \
               'chapter="{6}" ' \
               'section="{7}" ' \
               'date="{11}" ' \
               'location="{8}">' \
               '{9}' \
               '</citation>' \
        .format(
        cit_id,
        start_index,
        end_index,
        line_num,
        body.strip(),
        article.strip(),
        chapter.strip(),
        section.strip(),
        subsection.strip() if subsection else '',
        text.strip(),
        document.strip(),
        date.strip(),
    )

    return citation


def find_legislations(txt, file_id,quiet = True):
    """Returns a list of citation strings created from citations and informal amendment references in the given file

    :param txt:
    :param file_id:
    :return: (str) A list of citation strings
    """
    global id_number  ## number of case ciations
    legs = []
    with open(txt, 'r', -1, 'utf-8') as instream:

        offset = 0
        line_num = 1

        for line in instream:

            # line_remainder = len(line)
            # legis_matches = find_legislations_in_line(line)  # get list of matches

            # get the matches in order
            # for matched_string in (legis_matches if legis_matches else ()):

            # get the start offest of the match
            # start_index = line.find(matched_string)

            # increment the global offset by the start offset
            # offset += start_index

            # create a citation
            cits = generate_legislation_citations_from_string(
                line,
                offset,
                line_num,
                len(legs)+id_number,
                file_id.strip('\\/') + "_")
            cits2 = generate_other_leg_citations_from_string(line,
                offset,
                line_num,
                len(legs)+len(cits)+id_number,
                file_id.strip('\\/') + "_")
            cits.extend(cits2)

            # decrement the line remainder by (the match length + start offset) to cut out "the line so far"
            # line_remainder -= last_cit_offset
            # offset += last_cit_offset
            if not quiet:
                for x in cits: print(x)
            legs.extend(cits)
            line_num = line_num + 1
            offset += len(line)
    # print(legs)
    return legs

## PART 3 -- output to file

def case_and_legislative_citations_to_file (txt_file,file_id,outfile):
    output = find_case_citations(txt_file,file_id)
    output2 = find_legislations(txt_file,file_id)
    with open(outfile,'w') as outstream:
        for out in output:
            if ('entry_type' in out) and (out['entry_type'] in ['case_X_vs_Y','docket','standard_case','case_citation_other']):
                citation_print(outstream,out)
            elif 'phrase_type' in out:
                role_print(outstream,out)
            elif 'entry_type' in out:
                generic_object_print(outstream,out)
        for out in output2:
            outstream.write(out+'\n')

