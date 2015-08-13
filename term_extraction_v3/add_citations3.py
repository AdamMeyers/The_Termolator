import os
import re
import distutils.core
from nyu_utilities import *


## nxml specific patterns
xref = re.compile(r'<([/]?)xref *(ref-type=)?("([^"]*)")? *(rid=)?("([^"]*)")?[^>]*>',re.I)
ref_search= re.compile(r'ref-type="([^"]*)"',re.I)
nxml_end = re.compile(r'<ref-list[^>]*>',re.I)
nxml_restart = re.compile(r'</ref-list[^>]*>',re.I)
nxml_divider2 = re.compile(r'<([/]?)(title|P|article-title|contrib|label|aff|term)( [^>]*)?>',re.I)
nxml_divider3 = re.compile(r'<([/]?)(title|P|article-title|contrib|label|aff|term|sec|abstract|ack) ?([^>])*>',re.I)
nxml_divider4 = re.compile(r'<([/]?)(P|article-title|contrib|label|aff|term|sec|abstract|ack) ?([^>])*>',re.I)
global_start = False
require_psuedo_spaces = ['aff','contrib','name'] ## compatibility only, not used here

standard_number = 0

self_information = False
biblio_dict = {}

self_cite = re.compile(r'(^| )((here|us|[Ww]e)|([Oo]ur)|([tT]h(is|ese) +(findings?|stud(y|ies)|research|effects?|results?|work|approach(es)?|papers?|manuscripts?|documents|report)))([^a-z]|$)') ## "this" as an NP is OK, but "this" is too ambiguous without syntactic clues
## group(2) is the output string

self_cite_patent = re.compile(r'(^| )((this( +(patent|application|document))+)|((our) +.{0,10}(patent|invention|apparatus|application|device|system|algorithm|process))|(t((his)|(he)) +present +(patent|application|document|invention|device))|((the|this) +(patent|document|invention))|(this +application)|(the +methods? +of +the +invention)|(herein)|(in +(section +[0-9]+([.][0-9]+)*)))([^a-z]|$)',re.I) ## this does not allow "the application" or "the device" or "this device"

## group(2) is the output string
## if group(6) exists, it is an instance of 'our'
## and then might be further clarified by self_cite_patent_temporal

## this patent|app|doc -- refers to current document
## our ... patent (depending on pattern below, either identifies previous/related applications
## by same authors or current document)
## we -- refers to the authors (if there is a nearby citation of the form "in XYZ, we"
## it could be part of the nearby pattern.  Else it is the current article)
## -- we can refer to a generic we -- OK if
##      a) we is shortly followed bythis by past tense or past participle verb approx ("[dtn] ") en/ed/found/
##      ...) -- most reliable
##      b) we followed by a verb like propose/understand/... -- look at COMLEX sent complement verbs
##      c) math verbs calculate, etc,

self_cite_patent_temporal = re.compile(r'(^| )((current)|(new)|(present)|(future)|(co-pending)|(prior)|(earlier)|(previous))([^a-z]|$)',re.I) ## case?
## when applied to output of self_cite_patent, can determine if the reference is the current or a previous patent
## co-pending means pending at the same time (it can be something in the same patent family, e.g.,
## continuation-in-part,etc.)

## lang_family_key_terms = re.compile(r'(^| )(((([Rr]elated)|([Pp]arent)) +((([Cc]ase)|([aA]pplication))s?))|([Cc]ross[- ]+[Rr]eference)|([cC]continuation([ -]+in[ -]+part))|(Divisional)|([cC]laims the benefit of)|(application .{0,6}related to)|([pP]riority)|([nN]ational stage)|(Copyright))([^a-z]|$)')

lang_family_key_terms = re.compile(r'(^| )((((related)|(parent)) +(((case)|(application))s?))|(cross[- ]+reference)|(ccontinuation([ -]+in[ -]+part))|(divisional)|(claims the benefit of)|(application .{0,6}related to)|(priority)|(national stage)|(copyright))([^a-z]|$)',re.I) # 


## parent - one instance short distance in front of patent number -- attach to closest following patent number only
## related (to ..) patent
## continuation ...
## if it affect patent 1, it affects any patents found by subsequent_patent_search.search(...)

## lang_family_key_terms_short = re.compile(r'(^| )(([c][C]urrently)|([nN]ow))([^a-z]|$)')
lang_family_key_terms_short = re.compile(r'(^| )((currently)|(now))([^a-z]|$)',re.I)

patent_number = r'((A-Z)*([0-9,/-]{4,})(A-Z)*)|([0-9][0-9]+( [0-9][0-9]+)+((([.-][0-9]+)| [A-Z][0-9]+)?)+)|([0-9][0-9]/[0-9]{3},[0-9]{3})|(PCT/[A-Z]{2}[0-9]{2,4}/[0-9]{5,})'

german_patent = r'DE(-OS)? [0-9][0-9]+( [0-9][0-9]+)+(([.][0-9]+)| [A-Z][0-9]+)?'

other_prefixes = r'(AU|AR|AT|BE|BR|CA|CH|CN|CS|CZ|DD|DK|EP|ES|FI|FR|GB|HU|IE|IL|IN|IT|JP|KR|LU|MX|NL|NO|NZ|PH|PT|RD|RO|RU|SE|SG|SK|SU|TP|TW|US|WO|ZA|U[.]S[.])'
other_patent = r'( |^)('+other_prefixes+r'[ -]*([A-Z]?[A-Z]-)*[0-9][0-9/\- ]{4,}( *[A-Z][0-9]*)?)([^A-Z0-9]|$)'
## used to end with (,| |$)
## I think this includes the German patents

no_prefix_patent = r'(([Pp]at(([.])|(ent)))|([(]?[kK]okai[)]?)|(U[.]?S[.]?)) *(([pP]rovisional *)?)(([aA]ppl(([.]|ication)?))|([lL]aid[ -]open)|[Pp]ublication)? *([sS]er([.]|(rial)))? *(([nN]os?[.])|([nN]umber(s|ed)?)) *(U[.]?S[.]?)? *('+patent_number+')'

pct_patent = r'(PCT/[A-Z]{2}[0-9]{,4}/[0-9]{5,})'

other_foreign_application = '(Application +([0-9]{8,}[.][0-9]+))'

patent_number_on_a_line_by_itself = '(^ *'+patent_number+' *$)'

## Don't use '|([Dd]ocket)' as part of first field

german_patent_search = re.compile(german_patent)
## output = group 0

no_prefix_patent_search = re.compile(no_prefix_patent)
## output = group 17 -- but, trim_final comma

other_patent_search = re.compile(other_patent)
## output = group 0

varied_patent_search = re.compile(no_prefix_patent+r'|('+german_patent+r')|('+other_patent+')|'+pct_patent+'|'+other_foreign_application+\
                                  '|'+patent_number_on_a_line_by_itself)
## if group 0, then there is some answer
## if there is a group 42, then it falls under other_patent 
## if there is a group 26 (which should be trimmed), then it is a no_prefix_patent 
## if there is a group 35, then it is a german_patent 
## if there is a group 47, it is a PCT match
## if there is a group 49, it is an other_foreign_application
## if there is a group 53, it is a patent_number_on_a_line_by_itself
    
subsequent_patent_search = re.compile(r'((;|,|( *and))? *)(('+patent_number+')|('+german_patent+')|('+other_patent+')|'+pct_patent+')')
## subsequent_patent_search = re.compile(r'(,|( *and)) *(('+patent_number+')|('+german_patent+')|('+other_patent+'))')

isbn = r'ISBN[:]? *([0-9][ -][0-9]{3}[ -][0-9]{2}[ -][0-9]{3}[ -][0-9X])'

isbn_search = re.compile(isbn)

## searches for standards/standard documents

abbreviated_standard_orgs = 'AASHTO|ABNT|ACCSQ|AENOR|AFNOR|AIDMO|AMN|ANSI|ARSO|ASTM|BSI|BSJ|CEN|CENELEC|COPANT|CROSQ|DGN|DIN|EAC|ETSI|ICONTEC|IEC|IEEE|IETF|IRAM|IRMM|ISO|ITU|JISC|KATS|NEN|NFPA|PASC|SABS|SAC|SAE|SCC|SFS|SIS|SN|SNV|SNZ|UL|UNI|W3C|WSC'

full_standard_orgs = 'American Association of State & Highway Officials|American National Standards Institute|American National Standards Institute|American Society for Testing and Materials|Brazilian National Standards Organization|British Standards Institution|Bureau of Standards of Jamaica|Colombian Institute of Technical Standards and Certification|Deutsches Institut für Normung|Dirección General de Normas|East Africa Standards Committee|Ente Nazionale Italiano di Unificazione|Finnish Standards Association|French association for Standardization|Institute of Electrical and Electronics Engineers|Instituto Argentino de Normalización y Certificación|International Organization for Standardization|Japanese Industrial Standards Committee|Korean Agency for Technology and Standards|National Fire Protection Association|Nederlandse Norm|Society of Automotive Engineers|South African Bureau of Standards|Spanish Association for Standarization and Certification|Standardization Administration of China|Standards Council of Canada|Standards New Zealand|Standards Norway|Swedish Standards Institute|Swiss Association for Standardization|Internet Engineering Task Force|Underwriter Laboratories|World Wide Web Consortium|ASEAN Consultative Committee for Standards and Quality|African Organization for Standardization|Arabic industrial development and mining organization|CARICOM Regional Organisation for Standards and Quality|European Committee for Electrotechnical Standardization|European Committee for Standardization|European Telecommunications Standards Institute|Gulf Standardisation Organisation for GCC Arab Countries|Institute for Reference Materials and Measurements|International Electrotechnical Commission|International Telecommunication Union|MERCOSUR Standardization Association|Pacific Area Standards Congress|Pan American Standards Commission|World Standards Cooperation'

all_standard_orgs = abbreviated_standard_orgs +'|'+full_standard_orgs

standard_number_string = '[A-Z]?[/\.]?[0-9]( ?[0-9\.:-])+[A-Za-z]?'

numbered_abbrev_standard_pattern = r'('+abbreviated_standard_orgs+')+([/]('+abbreviated_standard_orgs+'))? *((([Ss]tandard)|([Pp]rotocol))s? )?('+standard_number_string+')'

numbered_full_standard_pattern = r'('+full_standard_orgs+') +'+'([(]('+abbreviated_standard_orgs+')[)] +)?('+standard_number_string+')'

closed_class_words = r'the|a|of|for|at|on|in|by|into|onto|to|per|plus|through|till|towards?|under|until|via|with|within|without|no|any|each'
## leaving out "as", "and" and "or" due to possible overgeneration
closed_class_check = re.compile('^('+closed_class_words+')$',re.I)

arbitrary_standard_pattern = r'([A-Z][A-Za-z0-9\.]* +)((([A-Z][A-Za-z0-9\.]*)|('+closed_class_words+')|([^a-zA-Z ]+)) +)*(([Ss]tandard)|([Pp]rotocol))($|[^a-zA-Z0-9])'

standard_right_filter =re.compile(r'^ *((('+closed_class_words+') +)*([A-Z][A-Za-z0-9\.]* ))')

standard_match = re.compile('(^|([^A-Za-z]))(('+numbered_abbrev_standard_pattern+')|('+numbered_full_standard_pattern+')|('+arbitrary_standard_pattern+'))')

standard_continuation_pattern = re.compile(r'([,]|( *and)) *('+standard_number_string+')')



## Probably need to assume some minimum length for patent numbers-- this is currently not incorporated into the above patterns

## self_cites for patents and articles are different. The above patterns will over_generate for self_cites of patents as follows:
## "We" is sometimes generic instead of a self-cite
## "application" is ambigous between patent application and a practical application of something

## self_site_patent includes co-pending/prior/earlier = other patents by same originators
##                           current, new, present or nothing = this patent applicaiton

def augment_BAE_fact_file_with_NYU_ID(factfile,outfile):
    number = 0
    with open(factfile,'r') as instream, open(outfile,'w') as outstream:
        for line in instream:
            outstream.write(line.strip(os.linesep))
            if re.search('^CITATION',line):
                number = number+1
                outstream.write(' NYU_ID=\"E'+str(number)+'\"')
            outstream.write(os.linesep)
    return(number)

def write_section_fact(fact,outstream,text_block=False):
    outstream.write('SECTION')
    for key in ['TYPE','TITLE','START','END']:
        if key in fact:
            if key in ['START','END']:
                outstream.write(' '+key+'='+str(fact[key]))
            else:
                outstream.write(' '+key+'="'+str(fact[key])+'"')
    ## Also Write Corresponding STRUCTURE (not sure how these are used)
    ## Do not differentiate types at this time
    if ('TYPE' in fact) and (fact['TYPE'] in ['TEXT','UNLABELED','TITLE']):
        if fact['TYPE'] == 'UNLABELED':
            structure_type = 'TEXT'
        elif fact['TYPE'] == 'TEXT':
            structure_type = 'TEXT_CHUNK'
        else:
            structure_type = 'TITLE'
        # if True:
        #     structure_type = 'TEXT'
        #     ## the rest is unused because I do not understand the 
        #     ## difference between TEXT and TEXT_CHUNK (after looking
        #     ## at the previous output of h5n1
        # elif text_block and (fact['START']>=text_block[0]) and \
        #               (fact['END']<=text_block[1]):
        #     structure_type = 'TEXT'
        # elif (not text_block) or (fact['START']>text_block[1]):            
        #     text_block = [fact['START'],fact['END']]
        #     ## Marks the beginning of a text segment
        #     structure_type = 'TEXT_CHUNK'
        # else:
        #     ## something is weird for this to happen
        #     structure_type = 'TEXT_CHUNK'
    else:
        ## this is not part of a text segment
        structure_type = 'DO_NOT_PARSE'
    outstream.write(os.linesep+'STRUCTURE TYPE="'+structure_type+'" START='+str(fact['START'])+' END='+str(fact['END'])+os.linesep)
    return(text_block)

def delete_appositive_self_cite(output,start):
    if (len(output)> 0) and (output[-1]['CITE_CLASS']=='patent_self_cite'):
        previous_position =  (output[-1]['END'])
        character_distance = start - previous_position
        if (character_distance < 25):  ## including (negative, i.e., overlap)
            ## self cite is ignored
            ## print('deleting',output[-1])
            output.pop()

def get_next_standard_id():
    global standard_number
    standard_number = standard_number+1
    return('NYU_STANDARD_DOCUMENT_'+str(standard_number))

def get_more_standards_from_line(line,start,file_start):
    match = standard_continuation_pattern.search(line,start)
    output = []
    if match and (match.start() != start):
        match = False
    while match:
        if (len(match.group(3))>1) and not(re.search('[a-zA-Z0-9]',match.group(3)[-1])):
            ## (match.group(3)[-1] in '.-:) '):
            out = {'ID':get_next_standard_id(),'START':match.start()+file_start,'END':(match.end()+file_start)-1,'CITE_CLASS':'standard_document','TEXT':match.group(3)[:-1]}
        else:
            out = {'ID':get_next_standard_id(),'START':match.start()+file_start,'END':match.end()+file_start,'CITE_CLASS':'standard_document','TEXT':match.group(3)}  ## group 3 contains the match
        output.append(out)
        start = match.end()
        match = standard_continuation_pattern.search(line,start)
        if match and (match.start() != start):
            match = False
    if len(output)>0:
        return(output,start)
    else:
        return(False,start)

def filter_out_standard_end(line):
    if standard_right_filter.search(line):
        return(True)
    else:
        return(False)

def filter_out_lowercase_standard(match):
    ## print(1,match.group(20),2,match.group(24),3,match.group(21),4,match.group(26))
    filter_out = False
    ## only applies to instances containing the strings "standard" or "protocol" with lowercase letters
    ## filters out cases where preceding word (skipping closed class) is something other than a simple capitalized word
    ## simple capitalized word = word beginning with capital where all non-initial letters are lowercase
    ## 21 is first word, 24 is last word if capital, 25 is last word if closed class, 26 is standard or protocol,
    ## 22,23 is last word regardless (same as 24 or 25)
    if match.group(26) and (match.group(26)[0] in 'ps'):  ## filter 24 (non closed class word if more than 1) if exists, else 21 (if one)
        if match.group(24):
            check_word = match.group(24)
        else:
            check_word = match.group(21)
        if match.group(25):
            filter_out=True
        elif len(check_word) == 1:
            if check_word == 'A':
                filter_out = True
        elif re.search('[^a-z ]',check_word[1:]):
            ## print('*'+check_word+'*')
            pass
        else:
            filter_out = True
    return(filter_out)

def first_closed_class_word_check(in_string,start_num):
    space = re.search(' +',in_string)
    out_string,out_start = in_string,start_num
    ## print(in_string,start_num,space.start())
    if space:
        word = in_string[:space.start()].strip(' ')
        ## print(word)
        if closed_class_check.search(word):
            out_string = in_string[space.end():]
            out_start = space.end()+out_start+1            
    ## print(1, out_string,out_start,2)
    return(out_string,out_start)

        
    
def get_standard_facts_from_line(line,file_start):
    match = standard_match.search(line)
    output = []
    while match:
        # for num in range(20):
        #     print(num,match.group(num))
        ## group 4 is for numbered_abbrev_standard_pattern
        ## group 14 is for numbered_full_standard_pattern
        ## group 20 is for arbitrary_standard_pattern
        ## 4 and 14 are possible beginnings of continuation patterns
        if match.group(4):
            group_number = 4
        elif match.group(14):
            group_number = 14
        elif match.group(20):
            group_number = 20
            if filter_out_standard_end(line[match.end():]) or filter_out_lowercase_standard(match):
                start = match.end()
                match = False
        else:
            match = False
            start = match.end()
            print('Something is odd about get_standard_facts_from_line')
        if not match:
            pass
        else:
            out_end = match.end()+file_start
            out_string = match.group(group_number)
            if (len(out_string)>1) and not(re.search('[a-zA-Z0-9]',out_string[-1])): 
            ## and (out_string[-1] in '.-:) '):
                out_end = out_end-1
                out_string = out_string[:-1]
            out_string,out_start = first_closed_class_word_check(out_string,match.start())
            out = {'ID':get_next_standard_id(),'START':out_start+file_start,'END':out_end,'CITE_CLASS':'standard_document','TEXT':out_string}
            output.append(out)
            start = match.end()
            if match.group(4) or match.group(14):
                more_output,start = get_more_standards_from_line(line,start,file_start)
                if more_output:
                    output.extend(more_output)
        match = standard_match.search(line,start)
    if len(output)>0:
        return(output)
    else:
        return(False)
            
def add_self_citations_for_article(line,overlap_string,initial_offset,debug=False):
    global self_information
    start = 0
    end = False
    output = []
    debug_output = []
    if overlap_string:
        search_line = overlap_string + line
        modified_offset = initial_offset - len(overlap_string)
    else:
        search_line = line
        modified_offset = initial_offset
    pattern = self_cite.search(search_line,start)
    while pattern:
        end = pattern.end()
        pattern_start = modified_offset+pattern.start(2)
        pattern_end = modified_offset+pattern.end(2)
        if self_information and ('ID' in self_information):
            out = {'ID':self_information['ID'],'START':pattern_start,'END':pattern_end, 'TITLE':self_information['TITLE'],'CITE_CLASS':'article_self_cite','TEXT':pattern.group(2)}
        else:
            out = {'START':pattern_start,'END':pattern_end,'CITE_CLASS':'article_self_cite','TEXT':pattern.group(2)}
        output.append(out)
        start = end
        pattern = self_cite.search(search_line,start)
    if len(output)>0:
        if end:
            if overlap_string:
                end=max(end,len(overlap_string))
            new_overlap = line[end:]
        else:
            print('bug in add_self_citations_for_article')
            new_overlap = False
        return(output,new_overlap,debug_output)
    else:
        return(False,line,debug_output)

def patent_family_test(search_string):
    ## print(search_string)
    ## input('')
    last_word = re.search('([a-zA-Z]+)[^a-zA-Z]*$',search_string)
    if last_word and lang_family_key_terms_short.search(last_word.group(1)):
        return(True)
    else:
        pattern = lang_family_key_terms.search(search_string)
        if pattern:
            return(pattern)
        else:
            return(False)

def clean_blanks_in_out(out):
    ## print('start',out,'end')
    ## input('')
    if out and ('TEXT' in out) and ('ID' in out):
        if out['TEXT']==out['ID']:
            id_equals_text = True
        else:
            id_equals_text = False
        out_string = out['TEXT']
        start_spaces = re.search('^[ ]+',out_string)
        end_spaces = re.search('[ ]+$',out_string)
        if end_spaces:
            minus = len(end_spaces.group(0))
            out_string = out_string[:0-minus]
            out['END']=out['END']-minus
        if start_spaces:
            plus = len(start_spaces.group(0))
            out_string = out_string[plus:]
            out['START']=out['START']+plus
        out['TEXT'] = out_string
        if id_equals_text:
            out['ID']=out_string
    return(out)


def filter_out_subsequent_patent(string):
    ## possibly introduce stronger filters later
    return(len(string.strip(", "))<5)
    
def valid_subsequent_patent(line,start):
    pattern = subsequent_patent_search.match(line,start)
    if pattern and not filter_out_subsequent_patent(pattern.group(4)):
        return(pattern)
    else:
        return(False)

def get_subsequent_patents(search_line,start,patent_family,modified_offset):
    ## print(0,start)
    output = []
    pattern = valid_subsequent_patent(search_line,start)
    ## using match rather than search because they must occur one after the other
    while pattern:
        ## group 3 is the id string
        start = pattern.start(4)
        end = pattern.end(4)
        pattern_start = modified_offset+start
        if pattern.group(4)[-1]==',':
            end = end-1
            pattern_end = modified_offset+end-1
            pattern_id = re.sub(' +',' ',pattern.group(4)[:-1])
        else:
            pattern_end = modified_offset+end
            pattern_id = re.sub(' +',' ',pattern.group(4))
        if patent_family:
            out = {'ID':pattern_id,'START':pattern_start,'END':pattern_end,'CITE_CLASS':'patent_family_member','TEXT':pattern_id}
        else:
            out = {'ID':pattern_id,'START':pattern_start,'END':pattern_end,'CITE_CLASS':'patent','TEXT':pattern_id}
        out = clean_blanks_in_out(out)
        start = end
        ## print(start)
        pattern = valid_subsequent_patent(search_line,start)
        ## print('end')
        output.append(out)
    if len(output)>0:
        ## print(1,search_line)
        ## print(2,start)
        ## print(3,output)
        return(output,start)
    else:
        return(False,False)

def put_fact_in_sorted_position(output,out):
    ## we will assume that this is rarely used, else we should use a quick_sort (or similar) strategy
    ## currently using insertion sort
    if len(output) == 0:
        output.append(out)
    else:
        done = False
        for num in range(len(output)):
            if out['START']<output[num]['START']:
                output = output.insert(num,out)
                done = True
                break
        if not done:
            output.append(out)

def patent_pattern_filter(pattern):
    if not pattern or not(pattern.group(53)):
        return(False)
    else:
        string = pattern.group(53).strip(' ')
    if string.isalnum() or (len(string)<8): 
        ## print(pattern.group(47))
        return(True)
    else:
        return(False)

def run_varied_patent_search(line,start):
    pattern = varied_patent_search.search(line,start)
    done = False
    ## print(start)
    while (pattern and not(done)):
        ## print(pattern.group(0))
        if pattern:
            if patent_pattern_filter(pattern):
                start = pattern.end()
                pattern = varied_patent_search.search(line,start)
            else:
                done = True
    ## print(pattern.group(0))
    return(pattern)
        

def add_citations_from_patent_line(line,overlap_string,initial_offset,debug=False):
    ## for now we will always return an overlap_string of False
    ## we would use this if patent numbers were split over 2 lines
    ## but first, we need to see if it actually happens

    ## self-cite ffor patents-- 2 types
    ## This or Our +(current)|(new)|(present)  - regular
    ## Our (other) -- work by same originators (modifiers may say if it is
    ## past or future or at the same time as the current one
    ## some co-pending (could be same language family)
    ## print(line)
    global self_information
    start = 0
    end = False
    if overlap_string:
        search_line = overlap_string + line
        modified_offset = initial_offset - len(overlap_string)
    else:
        search_line = line
        modified_offset = initial_offset
    pattern = run_varied_patent_search(search_line,start)
    pattern2 = self_cite_patent.search(search_line,start)
    output = []
    word_blocks = []
    debug_output = []
    delay_pattern1 = False
    delay_pattern2 = False
    last_patent_end = 0
    iterations = 0
    while pattern or pattern2:
        if pattern and pattern2:
            start1 = pattern.start()
            start2 = pattern2.start()
            if start1 < start2:
                delay_pattern2 = True
            elif start2 < start1:
                delay_pattern1 = True
            else:
                pattern2 = self_cite_patent.search(search_line,pattern.end()+1)
                delay_pattern2 = True
            ## print(pattern.groupUS20100163099A1-mae.xml(0),delay_pattern1)
            ## print(pattern2.group(0),delay_pattern2)
        if pattern and not delay_pattern1:   
            end = pattern.end()
            ## print(pattern.group(0),end='|')
            if pattern.group(23):
               ## no prefix patent (probably US)
                group_number = 23
            elif pattern.group(42):
               ## other patent
                group_number = 42
            elif pattern.group(35):
                ## german patent
                group_number = 35
            elif pattern.group(47):
                group_number = 47
            elif pattern.group(49):
                group_number = 49
            elif pattern.group(50):
                group_number = 50
            elif pattern.group(53):
                group_number = 53
            else:
                group_number = False
            if pattern and group_number:
                ## print(group_number,pattern.group(group_number),sep='|',end='|')
                pattern_start = modified_offset+pattern.start(group_number)
                if pattern.group(group_number)[-1] == ',':
                    pattern_end = modified_offset+pattern.end()-1
                    pattern_id = re.sub(' +',' ',pattern.group(group_number)[:-1])
                else:
                    pattern_end = modified_offset+pattern.end(group_number)
                    pattern_id = re.sub(' +',' ',pattern.group(group_number))
                ## print(pattern_start,last_patent_end)
                family_start = max(0,(pattern.start()-100),last_patent_end)
                ## last_patent_end makes sure that family indicator only affects
                ## one patent -- different when we include subsequent_patent_search
                ## patent_family = False
                ## print('hello')
                patent_family = patent_family_test(search_line[family_start:pattern.start()])
                word_blocks.append({'START':pattern.start()+modified_offset,'END':pattern.end()+modified_offset})
                if patent_family:
                    if not patent_family == True:
                        word_blocks.append({'START':patent_family.start()+family_start+modified_offset,\
                                                'END':patent_family.end()+family_start+modified_offset})
                    out = {'ID':pattern_id,'START':pattern_start,'END':pattern_end,'CITE_CLASS':'patent_family_member','TEXT':pattern_id}
                else:
                    out = {'ID':pattern_id,'START':pattern_start,'END':pattern_end,'CITE_CLASS':'patent','TEXT':pattern_id}
                ## print('out',out)
                delete_appositive_self_cite(output,pattern.start()+modified_offset)
                out = clean_blanks_in_out(out)
                output.append(out)
                subsequent_start = pattern_end-modified_offset
                subsequent_out,new_end = get_subsequent_patents(search_line,subsequent_start,patent_family,modified_offset)
                if subsequent_out:
                    output.extend(subsequent_out)
                    end = new_end
            start = end
            pattern = run_varied_patent_search(search_line,start)
            last_patent_end = end
        elif pattern2 and not delay_pattern2:
            end = pattern2.end()
            pattern_start = modified_offset+pattern2.start(2)
            pattern_end = modified_offset+pattern2.end(2)
            pattern_text = pattern2.group(2)
            same_originator = False
            if pattern2.group(6):
                ## an our patent
                temporal_pattern = self_cite_patent_temporal.search(pattern2.group(2))
                in_section = False
            elif pattern2.group(20) and pattern2.group(21):
                pattern_start = modified_offset+pattern2.start(21)
                pattern_text = pattern2.group(21)
                temporal_pattern = False
            else:
                in_section = False
                temporal_pattern = False
            if temporal_pattern and temporal_pattern.group(2).upper() in ['CO-PENDING','PRIOR','EARLIER','PREVIOUS']:
                out = {'START':pattern_start,'END':pattern_end,'CITE_CLASS':'patent_same_originator','TEXT':pattern_text}
                ## assume that current, new, present, future indicate current patent
            elif self_information and 'ID' in self_information:
                out = {'ID':self_information['ID'],'START':pattern_start,'END':pattern_end,'CITE_CLASS':'patent_self_cite','YEAR':self_information['YEAR'],'TEXT':pattern_text}
            else:
                out = {'START':pattern_start,'END':pattern_end,'CITE_CLASS':'patent_self_cite','TEXT':pattern_text}
            out = clean_blanks_in_out(out)
            word_blocks.append({'START':pattern2.start()+modified_offset,'END':pattern2.end()+modified_offset})
            output.append(out)
            start = end
            pattern2 = self_cite_patent.search(search_line,start)
        delay_pattern1 = False
        delay_pattern2 = False
    ## print(output)
    start = 0
    ISBN_pattern = isbn_search.search(search_line,start)
    while ISBN_pattern:
        ## print('hello')
        end = ISBN_pattern.end()
        start = ISBN_pattern.start()
        pattern_start = start+modified_offset
        pattern_end = end+modified_offset
        ## print('ISBN_pattern.group(0)')
        ## os.print('ISBN_pattern.group(1)')
        pattern_id = re.sub(' +',' ',ISBN_pattern.group(1))
        out = {'ID':pattern_id,'START':pattern_start,'END':pattern_end,'CITE_CLASS':'isbn','TEXT':pattern_id}
        put_fact_in_sorted_position(output,out)
        start=end
        ISBN_pattern = isbn_search.search(search_line,start)
    if len(output)>0:
        if end:
            if overlap_string:
                end=max(end,len(overlap_string))
            else:
                end = max(end,0)
            new_overlap = line[end:]
        else:
            print('bug in add_citations_from_patent_line')
            new_overlap = False
        ## print('out',output)
        return(output,new_overlap,debug_output,word_blocks)
    else:
        return(False,line,debug_output,word_blocks)

def get_self_citation_info_from_fact_file(factfile):
    with open(factfile,'r') as instream:
        for line in instream:
            line_attributes = get_integrated_line_attribute_value_structure(line,['PAPER','PATENT'])
            if line_attributes:
                return(line_attributes)
    
def add_citation_facts_to_file (textfile,factfile,outfile,is_patent=False,debug_file=False,initialize=True,output_style="BAE",NYU_ID=False):
    global standard_number
    standard_number = 0
    overlap_string = False
    facts = []
    new_facts = []
    word_blocks_line = []
    all_word_blocks = []
    number = 0
    start = 0
    debug_output = []
    global self_information
    self_information = get_self_citation_info_from_fact_file(factfile)
    if debug_file and initialize and os.path.isfile(debug_file):
        os.remove(debug_file)
    ## print('1')
    lines = 0
    with open(textfile,'r') as instream:
        for line in instream:
            line = line.strip(os.linesep)+' '
            if is_patent:
                new_facts,overlap_string,debug_out,word_blocks_line = add_citations_from_patent_line(line,overlap_string,start,debug=debug_file)
                if word_blocks_line:
                    all_word_blocks.extend(word_blocks_line)
                standard_facts = get_standard_facts_from_line(line,start)
                if standard_facts:
                    if new_facts:
                        new_facts.extend(standard_facts)
                    else:
                        new_facts = standard_facts
            else:
                new_facts,overlap_string,debug_out = add_self_citations_for_article(line,overlap_string,start,debug=debug_file)
            if new_facts:
                facts.extend(new_facts)
            if debug_out:
                debug_output.extend(debug_out)
            start = start+len(line)
            lines = 1+ lines
##            if ((lines%200)or(lines>3400))==0:
##                print(lines,end=' ')
##                if new_facts:
##                    print(new_facts)
##    print('new:', facts)
##    print(2)
    if output_style == "BAE":
        if NYU_ID:
            number = augment_BAE_fact_file_with_NYU_ID(factfile,outfile)
            ## initializes number at 0 and outputs the highest number
            ## for later use with self-citations
        else:
            distutils.file_util.copy_file(factfile,outfile)
        open_option = 'a'
    else:
        open_option = 'w'
    ## print(3)
    if facts:
        with open(outfile,open_option) as outstream:
            number = number+1
            if output_style=='MAE':
                outstream.write('''<?xml version="1.0" encoding="UTF-8" ?>
<JargonTask>
<TEXT><![CDATA[''')
                with open(textfile,'r',) as textstream:
                    for line in textstream:
                        outstream.write(line)
                ## copy entire text_file surrounded by MAE header and tag introducing text
                outstream.write(']]></TEXT>'+os.linesep)
                outstream.write('<TAGS>'+os.linesep)
            for fact in facts:
                write_citation_fact(fact,outstream,number,output_style=output_style,NYU_ID=NYU_ID)
                number = number+1
            if (output_style=='BAE') and all_word_blocks and (len(all_word_blocks)>0):
                for fact in all_word_blocks:
                    write_word_block_fact(fact,outstream,number,NYU_ID=NYU_ID)
                    number = number+1
            if output_style=='MAE':
                ## add in MAE end of file sequence
                outstream.write('</TAGS>'+os.linesep)
                outstream.write('</JargonTask>'+os.linesep)
    if debug_file and debug_output:
        with open(debug_file,'a') as outstream:
            for line in debug_output:
                outstream.write(line+os.linesep)
    ## print(4)

def add_citation_facts_to_directory(directory,is_patent=True,debug_out=False,NYU_ID=False):
    initial = True
    for file in os.listdir(directory):
        if (len(file)> 3) and file[-3:]=='txt':
            print('file:',file)
            add_citation_facts_to_file(directory+os.sep+file,directory+os.sep+file[:-3]+'fact',directory+os.sep+file[:-3]+'fact2',\
                                       is_patent=is_patent,debug_file=debug_out,initialize=initial,NYU_ID=NYU_ID)
            initial=False

def add_citation_facts_for_mae_to_directory(directory,is_patent=True,debug_out=False,NYU_ID=False):
    initial = True
    for file in os.listdir(directory):
        if (len(file)> 3) and file[-3:]=='txt':
            ## print('file:',file,end=' ')
            print(file)
            add_citation_facts_to_file(directory+os.sep+file,directory+os.sep+file[:-3]+'fact',directory+os.sep+file[:-4]+'-mae.xml',\
                                       is_patent=is_patent,debug_file=debug_out,initialize=initial,output_style="MAE",NYU_ID=NYU_ID)
            ## print('done')
            initial=False

def batch_add_citation_facts(input_file_list, output_file_list,NYU_ID=False,is_patent=True):
    input_files = open(input_file_list).readlines()
    output_files = open(output_file_list).readlines()
    if len(input_files) != len(output_files):
        print("Lists of input and output files should be of same length.")
        sys.exit(-1)
    for i in range(len(input_files)):
        try:
            txt_file, fact_file, is_patent = input_files[i].strip().split(';')
            output_file = output_files[i].strip()
            if is_patent.upper().strip() == 'TRUE':
                is_patent = True
            else:
                is_patent = False
        except:
            print("Error opening input/output files:")
            print("Input: %s\nOutput: %s" % (input_files[i].strip(), output_files[i].strip()))
        add_citation_facts_to_file(txt_file,
                fact_file,
                output_file,
                is_patent=is_patent,
                debug_file=False,
                initialize=False,
                NYU_ID=NYU_ID
            )

def citation_line(line):
    if re.search('^CITATION ',line):
        return(True)

def section_line(line):
    if re.search('^SECTION ',line):
        return(True)

def break_up_big_line2(big_line):
    ## from get_annotatable_nxml.py
    output = []
    start = 0
    unfinished = ''
    global global_start
    markers = []
    done = nxml_end.search(big_line)
    restart = nxml_restart.search(big_line)
    if done:
        done = done.start()
    p_count = 0
    use_pseudo_spaces = False
    command = ''
    ## within certain fields, it is necessary to add psuedospaces: aff, contrib (so far)
    while (start < len(big_line)):
        pattern = nxml_divider2.search(big_line,start)
        if use_pseudo_spaces:
            command = '<USE_PSEUDO_SPACES/>'
        else:
            command = ''
        if (not done) or (start < done) or (restart and (start >= restart.start())):
            ## divides lines by xml markers (as defined by the task)
            if pattern and done and (pattern.start() >= done) and restart and (pattern.start() < restart.start()):
                start = restart.start()
            elif pattern and done and (pattern.start() >= done) and (not restart):
                start = len(big_line)
            elif pattern:
                if pattern.group(1) == '/':
                    output.append(command+unfinished+big_line[start:pattern.start()]+os.linesep)
                    ## output.append(pattern.group(0).upper()+os.linesep)
                    if p_count > 1:
                        output.append('</P>'+os.linesep+'<P>')
                    else:
                        output.append('</P>'+os.linesep)
                    p_count = p_count-1
                    unfinished = ''
                    if len(markers) > 0:
                        markers.pop()
                    if pattern.group(2) in require_psuedo_spaces:
                        use_pseudo_spaces = False
                else:
                    if global_start and len(markers) > 0:
                        ## skip first stuff before first divider
                        output.append(command+unfinished+big_line[start:pattern.start()]+os.linesep)
                    else:
                        global_start = True
                        unfinished = ''
                    ## unfinished = pattern.group(0).upper()
                    if p_count >= 1:
                        unfinished = '</P>'+os.linesep+'<P>'
                    else:
                        unfinished = '<P>'
                    p_count = p_count+1
                    markers.append(pattern.group(2))
                    if pattern.group(2) in require_psuedo_spaces:
                        use_pseudo_spaces = True
                start = pattern.end()
            else:
                if len(markers)>0:
                    unfinished = unfinished+big_line[start:]
                    if global_start:
                        output.append(command+unfinished)
                ##elif global_start and (re.search('[A-Za-z0-9]+',remove_xml(big_line[start:]))):
                    ## this elif is a possible fix if there are short lines
                    ## output.append(big_line[start:])
                start = len(big_line)
        elif done and restart and start < restart.start():
            start = restart
        else:
##            if re.search('[A-Za-z0-9]+',remove_xml(big_line)):
##                output.append(big_line[start:])
            start = len(big_line)            
            ## print('unfinished',unfinished)
    return(output)

def break_up_big_line4(big_line):
    ## modified version of 2
    output = []
    start = 0
    unfinished = ''
    global global_start
    markers = []
    done = nxml_end.search(big_line)
    restart = nxml_restart.search(big_line)
    if done:
        done = done.start()
    p_count = 0
    use_pseudo_spaces = False
    command = ''
    section_marker = False
    ## within certain fields, it is necessary to add psuedospaces: aff, contrib (so far)
    while (start < len(big_line)):
        pattern = nxml_divider4.search(big_line,start)
        ## pattern = nxml_divider3.search(big_line,start)
        ## pattern = nxml_divider2.search(big_line,start)
        if use_pseudo_spaces:
            ## command = '<USE_PSEUDO_SPACES/>'
            command = ' '
        else:
            command = ''
        if (not done) or (start < done) or (restart and (start >= restart.start())):
            ## divides lines by xml markers (as defined by the task)
            if pattern and done and (pattern.start() >= done) and restart and (pattern.start() < restart.start()):
                start = restart.start()
            elif pattern and done and (pattern.start() >= done) and (not restart):
                start = len(big_line)
            elif pattern:
                if pattern.group(2).lower() in ['sec','abstract','ack','title']:
                    ## print(pattern.group(0))
                    next = pattern.end()
                    section_marker = True
                else:
                    section_marker = False
                    next = pattern.start()
                if pattern.group(1) == '/':
                    output.append(command+unfinished+big_line[start:next]+os.linesep)
                    ## output.append(pattern.group(0).upper()+os.linesep)
                    if section_marker:
                        p_count = p_count+1 ## counteract counters
                    elif p_count > 1:
                        output.append('</P>'+os.linesep+'<P>')
                    else:
                        output.append('</P>'+os.linesep)
                    p_count = p_count-1
                    unfinished = ''
                    if len(markers) > 0:
                        markers.pop()
                    if pattern.group(2) in require_psuedo_spaces:
                        use_pseudo_spaces = False
                else:
                    if pattern.group(2).lower() in ['sec','abstract','ack','title']:
                        next = pattern.end()
                        section_marker = True
                        ## print(pattern.group(0))
                        ## print(big_line[start:next])
                    else:
                        section_marker = False
                        next = pattern.start()
                    output.append(command+unfinished+big_line[start:next]+os.linesep)
                    ## if global_start and len(markers) > 0:
                    if global_start:
                        ## skip first stuff before first divider
                        ## output.append(command+unfinished+big_line[start:next]+os.linesep)
                        pass
                    else:
                        global_start = True
                        unfinished = ''
                    ## unfinished = pattern.group(0).upper()
                    if p_count >= 1:
                        unfinished = '</P>'+os.linesep+'<P>'
                    else:
                        unfinished = '<P>'
                    p_count = p_count+1
                    markers.append(pattern.group(2))
                    if pattern.group(2) in require_psuedo_spaces:
                        use_pseudo_spaces = True
                start = pattern.end()
            else:
                if len(markers)>0:
                    unfinished = unfinished+big_line[start:]
                    if global_start:
                        output.append(command+unfinished)
                ##elif global_start and (re.search('[A-Za-z0-9]+',remove_xml(big_line[start:]))):
                    ## this elif is a possible fix if there are short lines
                    ## output.append(big_line[start:])
                start = len(big_line)
        elif done and restart and start < restart.start():
            start = restart.end()
        else:
##            if re.search('[A-Za-z0-9]+',remove_xml(big_line)):
##                output.append(big_line[start:])
            output.append(big_line[start:])
            start = len(big_line)            
            ## print('unfinished',unfinished)
    return(output)

def chop_up_mercilessly(line,section):
    ## extracts proper text normally
    ## puts weird text on its own line
    ## print(line)
    ## print(section)
    ## input('')
    next_xml = re.compile(r'<([/])?([^<]*)>')
    start = 0
    output = []
    while (start < len(line)):
        pattern = next_xml.search(line,start)
        if pattern:
            if pattern.group(2).lower() in ['sec','abstract','ack','title','p']:
                end = pattern.end()
                ## if possible, keep groups ot text together as single units
                if pattern.group(1) == '/':
                    if len(output)>1:
                        next_one = output.pop()
                        next_one = next_one[0]
                        next_one = next_one + os.linesep+line[start:end]+os.linesep
                        output.append([next_one,'TEXT'])
                        ## print(next_one)
                    else:
                        output.append([os.linesep+line[start:end]+os.linesep,'TEXT'])
                        ## print(next_one)
                elif (len(output)>1) and (output[-1][1]=='TEXT'):
                    next_one = output.pop()
                    next_one = next_one[0]
                    next_one = next_one + os.linesep+line[start:end]+os.linesep
                    output.append([next_one,'TEXT'])
                    ## print(next_one)
                else:
                    ## print(os.linesep+line[start:end]+os.linesep)
                    output.append([os.linesep+line[start:end]+os.linesep,'TEXT'])
            elif pattern.group(1) == '/':
                end = pattern.start()
                if len(line[start:end])>0:
                    segment_type = section
                    output.append([os.linesep+'<p>'+line[start:end]+'</p>'+os.linesep,segment_type])
            start = pattern.end()
        else:
            segment_type = section
            output.append([os.linesep+'<p>'+line[start:]+'</p>'+os.linesep],segment_type)
    return(output)

def chop_up_specially(line):
    special_types = re.compile(r'<([/])?(ref-list|table)([^>]*)>',re.I)
    start = 0
    output = []
    label = False
    ## print(line)
    while(start<len(line)):
        pattern = special_types.search(line,start)
        ## print(start)
        if pattern:
            if pattern.group(1) == '/':
                if not label:
                    label = pattern.group(2)
                if label == 'ref-list':
                    label = 'REFERENCES'
                end = pattern.start()
                output.append([line[start:end],label.upper()])
                label = False
            else:
                output.append([line[start:pattern.start()]+os.linesep,'TEXT'])
                label = pattern.group(2)
            start = pattern.end()                    
        else:
            output.append([line[start:]+os.linesep,'TEXT'])
            start = len(line)
    return(output)

def break_up_big_line4a(big_line):
    output = []
    for line in break_up_big_line4(big_line):
        output.append([line,'TEXT'])
    return(output)

def break_up_by_sections(line):
    ## output = []
    output = ''
    start = 0
    while (start < len(line)):
        pattern = nxml_divider3.search(line,start)
        if pattern:
            end = pattern.end()
            ## output.append(line[start:end]+os.linesep)
            output=output+line[start:end]+os.linesep
            start = end
        else:
            output=output+line[start:]
            start = len(line)
    return(output)

def break_up_references(line):
    ## output = []
    reference_divider = re.compile('<([/]?)(ref|name|collab|article-title|source) ?([^>])*>',re.I)
    ## id name (surname given-names) year article-title source volume fpage lpage issue collab
    output = ''
    start = 0
    while (start < len(line)):
        pattern = reference_divider.search(line,start)
        if pattern:
            end = pattern.end()
            ## output.append(line[start:end]+os.linesep)
            output=output+line[start:end]+os.linesep
            start = end
        else:
            output=output+line[start:]
            ## output.append(line[start:]+os.linesep)
            start = len(line)
    return(output)

    
def break_up_big_line5(big_line):
    ## modified version of 2
    output = []
    front = []
    body = []
    start = 0
    pat_type = False
    big_divider = re.compile(r'<([/])?(front|body|back)([^>]*)>',re.I)
    ## treat back as part of body
    special_sections = re.compile('r<([/])?(table|ref-list)([^>]*)>',re.I)
    while (start < len(big_line)):
        pattern = big_divider.search(big_line,start)
        ## print(start)
        if pattern:
            if (pattern.group(1) == '/'):
                if pat_type == 'front':
                    front.append(big_line[start:pattern.start()])
                else:
                    body.append(big_line[start:pattern.start()])
                pat_type = False
            elif pat_type:
                if pat_type == 'front':
                    front.append(big_line[start:pattern.start()])
                else:
                    body.append(big_line[start:pattern.start()])
                pat_type = pattern.group(2)                
            else:
                pat_type = pattern.group(2)                
            start = pattern.end()
        elif pat_type:
            if pat_type == 'front':
                front.append(big_line[start:])
            else:
                body.append(big_line[start:])
            pat_type = False
            start = len(big_line)
        else:
            start = len(big_line)
    for line in front:
        for piece,stype in chop_up_mercilessly(line,'front'):
            output.append([piece,stype])
    output.append(['<RESET>','reset'])
    ## print('front',front)
    ## print('body',body)
    for largeline in body:
        for line,stype in chop_up_specially(largeline):
            ## print('small')
            if stype == 'TEXT':
                ## for sect in break_up_by_sections(line):
                ##    output.append([sect,stype])
                output.append([break_up_by_sections(line),stype])
            elif stype == 'REFERENCES':
                ## for piece in break_up_references(line):
                    ## get reference facts
                    ## replace chop_up_mercilessly to include messages for
                    ## get_paragraph_facts
                    ## output.append([piece,stype])
                output.append([line,stype])
            else:
                for piece,stype2 in chop_up_mercilessly(line,stype):
                    output.append([piece,stype2])
    return(output)


def process_xml_line3(line):
    ## from get_annotatable_nxml
    line = convert_markoff_utf8_numbers_to_characters(line)
    line = remove_xml_except(line,['xref','XREF'])
    return(line)

def process_xml_line4(line):
    ## from get_annotatable_nxml
    line2 = convert_markoff_utf8_numbers_to_characters(line)
    line2 = remove_xml_except(line2,['P','SEC','ABSTRACT','ACK','TITLE'])
    return(line2)

def store_BAE_citation_information (line):
    global BAE_citation_dictionary
    fact = get_integrated_line_attribute_value_structure(line,['CITATION'])
    start = line_attributes['START'][0]
    if start.isalnum():
        start = int(start)
        unlist_attributes(line_attributes)
        if not (start in BAE_citation_dictionary):
            BAE_citation_dictionary[start]=line_attributes

def get_ref_type(ref_string):
    pattern = ref_search.search(ref_string)
    if pattern:
        return(pattern.group(1))
    else:
        return(False)

def get_nxml_citation_facts(line,file_offset):
    global BAE_citation_dictionary
    global unique_citation_number
    output = []
    start = 0
    clean_start = 0
    text_start = 0
    text_end = 0
    ref_start = file_offset
    pattern = xref.search(line)
    TYPE = False
    ## ** 57 **
    while pattern:
        clean_start=clean_start+(pattern.start()-start)
        if pattern.group(1) == '/':
            if TYPE == 'bibr':
                ref_end=clean_start+file_offset
                TEXT = line[start:pattern.start()].strip(' \n')
                if not (re.search('[a-zA-Z0-9]',ENTITY_ID)):
                    ENTITY_ID = False
                if ref_start in BAE_citation_dictionary:
                    prev_entry = BAE_citation_dictionary[ref_start]
                elif TEXT.upper() in BAE_citation_dictionary:
                    prev_entry = BAE_citation_dictionary[TEXT.upper()]
                elif ENTITY_ID and (ENTITY_ID in BAE_citation_dictionary):
                    prev_entry = BAE_citation_dictionary[ENTITY_ID]
                else:
                    prev_entry = False       
                if ENTITY_ID and (not ENTITY_ID in BAE_citation_dictionary):
                    BAE_citation_dictionary[ENTITY_ID] = prev_entry
                fact = {'START':ref_start,'END':ref_end,'CITE_CLASS':'article','TEXT':TEXT}
                if ENTITY_ID:
                    fact['ENTITY_ID'] = ENTITY_ID
                if prev_entry:
                    if 'TITLE' in prev_entry:
                        fact['TITLE'] = prev_entry['TITLE']
                    if 'ID' in prev_entry:
                        fact['ID'] = prev_entry['ID']
                    if 'YEAR' in prev_entry:
                        fact['YEAR'] = prev_entry['YEAR']
                output.append(fact)
        else:
            ENTITY_ID = pattern.group(7)
            TYPE = get_ref_type(pattern.group(0))
            start = pattern.end()
            ref_start=clean_start+file_offset
        start = pattern.end()
        pattern = xref.search(line,start)            
    return(output)

def get_nxml_citation_facts2(line,file_offset):
    global BAE_citation_dictionary
    global unique_citation_number
    output = []
    start = 0
    clean_start = 0
    text_start = 0
    text_end = 0
    ref_start = file_offset
    pattern = xref.search(line)
    TYPE = False
    while pattern:
        if pattern.start()==start:
            difference_string = ''
        else:
            difference_string = remove_xml(line[start:pattern.start()])
        clean_start=clean_start+len(difference_string)
        if pattern.group(1) == '/':
            if TYPE == 'bibr':
                ref_end=clean_start+file_offset
                TEXT = line[start:pattern.start()].strip(' \n')
                if not (re.search('[a-zA-Z0-9]',ENTITY_ID)):
                    ENTITY_ID = False
                if ref_start in BAE_citation_dictionary:
                    prev_entry = BAE_citation_dictionary[ref_start]
                elif TEXT.upper() in BAE_citation_dictionary:
                    prev_entry = BAE_citation_dictionary[TEXT.upper()]
                elif ENTITY_ID and (ENTITY_ID in BAE_citation_dictionary):
                    prev_entry = BAE_citation_dictionary[ENTITY_ID]
                else:
                    prev_entry = False       
                if ENTITY_ID and (not ENTITY_ID in BAE_citation_dictionary):
                    BAE_citation_dictionary[ENTITY_ID] = prev_entry
                fact = {'START':ref_start,'END':ref_end,'CITE_CLASS':'article','TEXT':TEXT}
                if ENTITY_ID:
                    fact['ENTITY_ID'] = ENTITY_ID
                if prev_entry:
                    if 'TITLE' in prev_entry:
                        fact['TITLE'] = prev_entry['TITLE']
                    if 'ID' in prev_entry:
                        fact['ID'] = prev_entry['ID']
                    if 'YEAR' in prev_entry:
                        fact['YEAR'] = prev_entry['YEAR']
                output.append(fact)
        else:
            ENTITY_ID = pattern.group(7)
            TYPE = get_ref_type(pattern.group(0))
            ref_start=clean_start+file_offset
        start = pattern.end()
        pattern = xref.search(line,start)            
    return(output)


def get_paragraph_facts (line,unfinished_section_info,file_offset,text_style):
    section_divider = re.compile('<(/)?((abstract)|(ack)|(sec))([^>]*)>',re.I)
    title = re.compile('<title>([^<]+)</title>',re.I)
    # if re.search('title',line):
    #     print(line)
    # if file_offset ==684:
    #     print(unfinished_section_info)
    paragraph = re.compile('<(/)?p>',re.I)
    if unfinished_section_info:
        paragraph_start = unfinished_section_info[0]
        section_start = unfinished_section_info[1]
        section_info = unfinished_section_info[2]
    else:
        paragraph_start = file_offset
        section_start = []
        section_info = []
    next_section_pattern = section_divider.search(line)
    next_paragraph_pattern = paragraph.search(line)
    sec_type_pattern = re.compile('sec-type="([^"]+)"',re.I)
    title_pattern = re.compile('<title>([^<]+)</title>')
    next_title_pattern = title_pattern.search(line)
    start = 0
    clean_start = 0
    text_start = 0
    text_end = 0
    ref_start = file_offset
    pattern = False
    TITLE = False
    TYPE = False
    for pat in [next_section_pattern,next_paragraph_pattern,next_title_pattern]:
        if pat:
            if (not pattern) or (pat.start()<pattern.start()):
                pattern = pat
    if pattern:
        start = pattern.end()
        clean_start = len(remove_xml(line[:start]))
        ## print('clean',clean_start,1)
    output = []
    title_offset = 0
    while pattern:
        if (pattern == next_title_pattern) and (len(section_info) > 0):
            title_phrase = remove_xml(next_title_pattern.group(1))
            title_offset = len(title_phrase)
            section_info[-1]['TITLE']=title_phrase.strip(os.linesep)
            title_start = clean_start+file_offset
            title_end = title_start+title_offset
            fact = {'TYPE':'TITLE','START':title_start,'END':title_end}
            output.append(fact)
        elif pattern.group(1) == '/':
            title_offset = 0
            ## field 1 optionally contains the slash
            ref_end=clean_start+file_offset
            if pattern == next_section_pattern:
                ## print('1')
                next_one = 'section'
                section_tag = pattern.group(2).lower()
                if len(section_start) > 0:
                    ref_start = section_start.pop()
                    Sinfo = section_info.pop()
                    if 'TITLE' in Sinfo:
                        TITLE = Sinfo['TITLE']
                    elif section_tag == 'ack':
                        TITLE = 'Acknowledgments'
                    elif section_tag == 'abstract':
                        TITLE = 'Abstract'
                        TYPE = 'ABSTRACT'
                    else:
                        TITLE = False
                    if 'TYPE' in Sinfo:
                        TYPE = Sinfo['TYPE']
                    elif section_tag == 'ack':
                        TYPE = 'ACKNOWLEDGMENTS'
                    elif section_tag == 'abstract':
                        TYPE = 'ABSTRACT'
                    else:
                        TYPE = 'UNLABELED'
                    ## print(ref_start,ref_end,TYPE,TITLE)
                    fact={'TYPE':TYPE,'START':ref_start,'END':ref_end}
                    ## print(fact)
                    ## print('file',file_offset,'clean',clean_start,'start',start)
                    if TITLE:
                        fact['TITLE']=TITLE 
                    output.append(fact)
                    ## print(fact)
                ## for now, we will ignore nested sections
                ## we assume they are all of the variety in which
                ## sec and some other tag (abstract or ack) are redundant
            else:
                next_one = 'paragraph'
                ref_start = paragraph_start
                if text_style and (text_style !='TEXT'):
                    TYPE = text_style
                else:
                    TYPE = 'UNLABELED'
                TITLE = False
                ## paragraph_start = False
                fact={'TYPE':TYPE,'START':ref_start,'END':ref_end}
                if TITLE:
                    fact['TITLE']=TITLE
            ## print('offset',file_offset,'next',next_one,'fact',fact)
                output.append(fact)
        else:
            title_offset = 0
            ref_start=clean_start+file_offset ## paragraph_start or section_start
            if pattern == next_section_pattern:
                ## print(2)
                ## print(pattern.group(0))
                section_tag = pattern.group(2).lower()
                section_start.append(ref_start)
                ## look for TYPE
                type_pattern = sec_type_pattern.search(pattern.group(6))
                ## field 6 holds all the attributes
                if type_pattern:
                    TYPE = type_pattern.group(1)
                elif (text_style and text_style != 'TEXT'):
                    TYPE = text_style
                else:
                    TYPE = False
                ## print(pattern.group(0),TYPE)
##                title_patt = title_pattern.search(line,pattern.end())
##                ## look for TITLE
##                if title_patt and (not re.search('[a-zA-Z0-9]',line[start:title_patt.start()])):
##                    TITLE = title_patt.group(1)
                Sinfo = {}
##                if TITLE:
##                    section_info['TITLE'] = TITLE
                if TYPE:
                    Sinfo['TYPE'] = TYPE
                elif text_style:
                    Sinfo['TYPE'] = text_style
                section_info.append(Sinfo)
            else:
                paragraph_start = ref_start
        start = pattern.end()
        if pattern == next_section_pattern:
            next_section_pattern = section_divider.search(line,start)
        elif pattern == next_title_pattern:
            next_title_pattern = title_pattern.search(line,start)
        else:
            next_paragraph_pattern = paragraph.search(line,start)
        pattern = False
        for pat in [next_section_pattern,next_paragraph_pattern,next_title_pattern]:
            if pat:
                if (not pattern) or (pat.start()<pattern.start()):
                    pattern = pat
        if pattern:
            if pattern.start() == start:
                difference_string = ''
            else:
                difference_string = remove_xml(line[start:pattern.start()])
            clean_start= clean_start+title_offset+len(difference_string)
            pstart = pattern.start()
##            if pstart > 500:
##                print('clean 2',clean_start,'title',title_offset,'pstart',pattern.start(),'start',start)
##                print(line)
    return(output,[paragraph_start,section_start,section_info])

def get_bib_authors(reference_string):
    collab_pattern = re.compile('<collab[^>]*>([^<]*)</collab>',re.I)
    ## there can be more than one name
    name_pattern = re.compile('<name[^>]*>([^<]*)</name>',re.I)
    ## next 2 are inside of name
    given_names_pattern = re.compile('<given-names[^>]*>([^<]*)</given-names>',re.I)
    surname_pattern = re.compile('<surname[^>]*>([^<]*)</surname>',re.I)
    string_position = 0
    output = []
    collab = collab_pattern.search(reference_string)
    if collab:
        output.append([collab.group(1)])
    author_name = name_pattern.search(reference_string,string_position)
    while author_name:
        current_name = author_name.group(1)
        surname = surname_pattern.search(current_name)
        given_name = given_names_pattern.search(current_name)
        if given_name and surname:
            output.append([surname.group(1),given_name.group(1)])
        elif given_name:
            output.append([given_name.group(1)])
            print('Warning: Ill-formed name in bibliography',reference_string)
        elif surname:
            output.append([surname.group(1)])
        else:
            output.append([current_name])
        string_position = name.end()
        name = name_pattern.search(reference_string,string_position)
    return(output)
        
def update_biblio_dict(line):
    ### id name (surname given-names) year article-title source volume fpage lpage issue collab
    global biblio_dict
    ref_pattern = re.compile('<ref id="(.*?)"[^>]*>(.*?)</ref>',re.I)
    source_pattern = re.compile('<source[^>]*>([^<]*)</source>',re.I)
    article_title_pattern = re.compile('<article-title[^>]*>([^<]*)</article-title>',re.I)
    year_pattern = re.compile('<year[^>]*>([^<]*)</year>',re.I)
    volume_pattern = re.compile('<volume[^>]*>([^<]*)</volume>',re.I)
    fpage_pattern = re.compile('<fpage[^>]*>([^<]*)</fpage>',re.I)
    lpage_pattern = re.compile('<lpage[^>]*>([^<]*)</lpage>',re.I)
    issue_pattern = re.compile('<issue[^>]*>([^<]*)</issue>',re.I)
    ext_link_pattern = re.compile('<ext-link[^>]*>(.*?)</ext-link>',re.I)
    line_position = 0
    entry = {}
    next_ref = ref_pattern.search(line,line_position)
    while next_ref:
        ref_id = next_ref.group(1)
        ref = next_ref.group(2)
        ## print(ref,ref_id)
        ## print(0,next_ref.group(0))
        if ref and ref_id:
            entry['id']=ref_id
            source = source_pattern.search(ref)
            if source:
                entry['SOURCE'] = source.group(1)
            article_title = article_title_pattern.search(ref)
            if article_title:
                entry['TITLE'] = article_title.group(1)
            year = year_pattern.search(ref)
            if year:
                entry['YEAR'] = year.group(1)
            volume = volume_pattern.search(ref)
            if volume:
                entry['VOLUME'] = volume.group(1)
            fpage = fpage_pattern.search(ref)
            if fpage:
                entry['FPAGE'] = fpage.group(1)
            lpage = lpage_pattern.search(ref)
            if lpage:
                entry['LPAGE'] = lpage.group(1)
            issue = issue_pattern.search(ref)
            if issue:
                entry['ISSUE'] = issue.group(1)
            names = get_bib_authors(ref)
            if names:
                entry['AUTHORS'] = names
            ext_link = ext_link_pattern.search(ref)
            if ext_link:
                entry['EXT_LINK'] = ext_link.group(1)
            biblio_dict[entry['id']]=entry
            ## print(entry)
            entry = {}
        line_position = next_ref.end()
        next_ref = ref_pattern.search(line,line_position)

def write_biblio_fact(fact,outstream):
    outstream.write('BIB_ENTRY')
    for feature in ['id','AUTHORS','YEAR','TITLE','SOURCE','VOLUME','ISSUE','FPAGE','LPAGE','EXT_LINK']:
        if feature in fact:
            ## print(feature,fact[feature])
            if feature == 'AUTHORS':
                for author in fact[feature]:
                    if len(author) == 1:
                        outstream.write(' AUTHOR="'+author[0]+'"')
                    else:
                        outstream.write(' AUTHOR="'+author[0]+', '+author[1]+'"')
            else:
                outstream.write(' '+feature+'="'+fact[feature]+'"')
    outstream.write(os.linesep)

def replace_citation_facts_from_nxml_file2 (nxml_file, in_fact_file, out_fact_file, out_text_file):
    big_line = ''
    number = 0
    file_position = 0
    global BAE_citation_dictionary
    global unique_citation_number
    global biblio_dict
    biblio_dict.clear()
    unique_citation_number = 0
    BAE_citation_dictionary = {}
    citation_facts = []
    paragraph_facts = []
    current_reference_id = False
    with open(out_fact_file,'w') as outstream_facts, open(out_text_file,'w') as outstream_text:
        if in_fact_file and os.path.isfile(in_fact_file):
            with open(in_fact_file,'r') as instream:
                for line in instream:
                    if re.search('^(CITATION|STRUCTURE|SECTION|DOC_SEGMENT)',line):
                       ## store_BAE_citation_information(line)
                       ## removing information that we cannot align
                        pass                    
                    else:
                        outstream_facts.write(line)
        with open(nxml_file,'r') as instream:
            for line in instream:
                big_line=big_line+line
##        big_line = re.sub('</[pP]>','</P>\n',big_line) ## adding lines for readability
##        big_line = process_xml_line3(big_line)
##        facts = get_nxml_citation_facts2(line,file_position)
##        outstream_text.write(remove_xml(big_line))
        unfinished_section_info = False
        ## big_list = break_up_big_line5(big_line)
        big_list = break_up_big_line5(big_line)
        ## **57 -- need to add divisions (front, back, etc.)
        ## these should act as notes to clear out unfinished_section_info
        ## in between mega-sections
        ## print('big_list',len(big_list))
        for line,text_style in big_list:
##            if re.search('<sec',line):
##                print('Section?',line)
            if line == '<RESET>':
                unfinished_section_info = False
            elif text_style == 'REFERENCES':
                update_biblio_dict(line)
                line = break_up_references(line)
                line = process_xml_line3(line)
                line = remove_xml(line)
                outstream_text.write(line)
                file_position = file_position+len(line)
            else:
                line2 = process_xml_line4(line)
                ## line2 = line
                new_facts,unfinished_section_info = get_paragraph_facts(line2,unfinished_section_info,file_position,text_style)
                paragraph_facts.extend(new_facts)
                line = process_xml_line3(line)
                ## readability issues
                ## fact_length = len(facts)
                new_facts = get_nxml_citation_facts2(line,file_position)
                citation_facts.extend(new_facts)
                line = remove_xml(line)
                outstream_text.write(line)
    ##            if len(facts)>fact_length:
    ##                print(file_position,facts[fact_length:])
                file_position = file_position+len(line)
                ## print(file_position)
        text_block = False
        ## initialize text_block
        for fact in paragraph_facts:
            text_block = write_section_fact(fact,outstream_facts,text_block=text_block)
        for fact in citation_facts:
            write_citation_fact(fact,outstream_facts,number,NYU_ID=True)
            number=number+1
        for fact in biblio_dict:
            write_biblio_fact(biblio_dict[fact],outstream_facts)

def recreate_citation_facts_for_nxml_directory (old_directory,new_directory):
    Fail = False
    if not os.path.isdir(new_directory):
        if os.path.isfile(new_directory):
            print('Error -- Cannot create directory',new_directory)
            Fail = True
        else:
            os.mkdir(new_directory)
    if Fail:
        print('Did not run program')
    else:
        print('Creating New Fact Files')
        for file in os.listdir(old_directory):
            if (len(file)> 4) and file[-4:]=='.xml':
                base_file = file[:-4]
                print(base_file)
                if os.path.isfile(old_directory+os.sep+base_file+'.fact'):
                    old_fact_file = old_directory+os.sep+base_file+'.fact'
                else:
                    old_fact_file = False
                replace_citation_facts_from_nxml_file2(\
                    old_directory+os.sep+base_file+'.xml', \
                    old_fact_file,\
                    new_directory+os.sep+base_file+'.fact',\
                    new_directory+os.sep+base_file+'.txt')
        print('Adding Self Citations')
        add_citation_facts_to_directory(new_directory,is_patent=False,NYU_ID=True)

def recreate_citation_facts_for_nxml_list (input_list,output_list,is_patent=False,NYU_ID=True):
    with open(input_list) as instream1, open(output_list) as instream2:
        infiles = instream1.readlines()
        outfiles = instream2.readlines()
        if len(infiles) != len(outfiles):
            print('Uneven number of input and output files. Try again!')
            return(False)
        else:
            for num in range(len(infiles)):
                infile = infiles[num].strip()
                infile_list = infile.split(';')
                nxml_file = infile_list[0]                
                if len(infile_list)>1:
                    old_fact_file = infile_list[1]
                else:
                    old_fact_file = False
                outfile = outfiles[num].strip()
                txt_file,fact_file1,fact_file2 = outfile.split(';')
                replace_citation_facts_from_nxml_file2(nxml_file,old_fact_file,fact_file1,txt_file)
                add_citation_facts_to_file(txt_file,fact_file1,fact_file2,is_patent=is_patent,debug_file=False,initialize=False,NYU_ID=NYU_ID)

## Citations of papers in patents: 1) 2 environments: a) at the
## beginning of a paragraph (typically the subject of a sentence); b)
## Inside of parens, but unfortunately matching parens cannot be
## relied on.  2) the paren environment usually, but not always begins
## with 'reference', 'Ref.' or 'cf.'. Without one of these (or other)
## intro words, look for a journal keyword match inside of a paren; 3)
## Sometimes a new "cf|ref|etc." left paren occurs when the last one
## has not been closed -- this indicates closure; 4) multiple
## references within the paren environment can be divided by ";" or
## "and", the latter being more ambigous; 4) To get the span right, it
## is necessary to look for the following components: (a) a last name;
## (b) something in quotes (beware for absense of closing quote); (c)
## a year, possibly in parens; and (d) a publication name; (e) ISBN
## number -- If there is an ISBN, it will always occur
## last. Otherwise, either the year or the publication comes last.

## The specs for these would need to be negotiated with Andy We would
## need to detect people names and possibly identify the correct spans
## for journal names.  This may require adding a journal gazetteer or
## adding a publication NE to our NE tagger.

## Components of this work:

# '(((Journal)|(J[.])|(Proceedings)|(Proc[.])|(Proceedings)) of)'
# '(Annual +)?(((International)|(Int\'?l[.]?)) +)?(Conf([.]|(erence))) + on'
# '[A-Z]+ +Journal'
# 'et. al'

## [reference.*] -- references divided by semicolons and sometimes the word "and"
## (cf. .*) -- unclear how to break up
## (Ref. .*)
## if parens contain a publication key phrase and meet some other
## minimal criteria (a year?), then they are broken down as above

## Some spans depend on finding Person name, e.g., PERSON
## Name.*quotation mark -- Example: M. Haase et al, Journal of Alloys
## and Compounds, 303-304 (2000) 191-197, “Synthesis and properties of
## colloidal lanthanide-doped nanocrystals” compare the propert...
