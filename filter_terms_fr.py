
##filter terms French ver
from term_utilities_fr import *
from term_utilities import *
from filter_terms import * 
from find_terms import *
from webscore_fr import *


def ok_statistical_term_fr(term,lenient=False,penalize_initial_the=False):
    ## if single word, it should be a possible noun
    ##
    ##return: keep,classification,chunks,rating,well_formedness_score
  
    #make a multext dictionary for common words? for OOV 
    #have multex english dict to check for english words
    #	or make separate function to remove long passages in english earlier on?
    # 	assume that this function removed long english sequences, so remaining
    # 	english terms are valid in this case, and can be evaluated separately
    # 	so maybe have a separate function for evaluating english words?
    

    symbols = '°|\'[,]µ±_+£/\:;<>?!#@%$&*~}{"'
    rating = 'Default'
    keep = True
    chunks = False
    classification = 'Default'
    well_formedness = 1
    term.strip()
    term_split = term.split()

    if len(term) < 2:
        keep = False
        classification = 'oneCharTerm'

    #remove if contains more than one '.'
    elif term.count('.') > 1:
        keep = False
        classification = "illFormed--."
    elif term[0] == '.' or term[-1] == '.':
        keep = False
        classification = 'period'

    #remove if begins or ends with hyphen: prob a fragment leftover from bad chunking
    elif term[0] == '-' or term[-1] == '-':
        keep = False
        classification = 'badHyphen' 
    elif any(c in term for c in symbols):
        keep = False
        classification = 'hasSymbol'
 
    # deal with terms containing numbers: maybe look if in chemical list?
    # if not, remove. SO GET CHEM LIST
    elif (any(c.isdigit() for c in term)):
        keep = False
        classification = 'hasNumber'
    
    elif term_dict_check(term,nationality_dict_fr):
        keep = False
        classification = 'Nationality'
       
    elif term_dict_check(term,location_dict_fr):
        print(term, " is in loc list")
        keep = False
        classification = 'Location'

    elif term_dict_check(term,fr_gazetteer):
        print(term, " is in gaz list")
        keep = False
        classification = 'Fr Loc'
    elif term_dict_check(term,organization_dict_fr):
        keep = False
        classification = 'Organization'

    elif term_dict_check(term.upper(),person_name_general):
        keep = False
        classification = 'PersonName'
    #elif term_dict_check(term.lower(),english_dict):
    #    keep = False
    #    classification = 'EnglishCommonWord'      
    #all caps
    elif term.isupper():
        keep = False
        classification = 'allCapitalLetters -- possible org'

    elif (any(c.isupper() for c in term[1:])):
        keep = False
        classification = 'capitalizationInside'

    elif len(term) < 4 and (any(c.isupper() for c in term)):
        keep = False
        classification = 'weird'

    #weird parentheses
    elif (')' in term and '(' not in term) or ('(' in term and ')' not in term):
        keep = False
        classification = 'paren' 
    elif ('(' in term and ')' in term and "-" in term):
        keep = False
        classification = 'paren and hyphen'
 
    #capitalized words
    elif term.istitle():
        keep = False
        classification = "first chars capitals"
    
    elif len(term) < 5:
        keep = False
        classification = "suspicious length"
    
    else:
        if (len(term_split) > 2):
            keep = True
            classification = 'other'
            chunks = False
            rating = 'Good'
            well_formedness = 0.7

    #for now don't assign same to all below if don't keep:
    if (keep == False):
        chunks = False
        rating = 'Bad'
        well_formedness = 0
       
    return(keep,classification,chunks,rating,well_formedness)


def filter_terms_fr (infile, \
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
                  webscore_max = 1000
                  ):

      
    '''
    ## it is possible that some people may want to allow NPs as well as noun groups as terms
    if abbr_full_file and full_abbr_file:
        if os.path.isfile(abbr_full_file) and os.path.isfile(full_abbr_file):
            read_in_abbrev_dicts_from_files(abbr_full_file,full_abbr_file)
        elif abbr_files:
            make_abbr_dicts_from_abbr(abbr_files,full_abbr_file,abbr_full_file)
            ## this creates abbr dicts and loads them
    '''
	
    #loads web dict file

    if use_web_score and web_score_dict_file:
        load_web_score_dict_file(web_score_dict_file)
        use_web_score_dict = True
    else:
        use_web_score_dict = False
        
    stat_scores = []
    alternate_lists = {}
    
    if reject_file:
        reject_stream = open(reject_file,'w',encoding='utf-8-sig')
    else:
        reject_stream = False
        
    ## make_stat_term_dictionary4
    ##ADDED ENCODING
    instream = open(infile,errors='replace',encoding='utf-8-sig')
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
    

    #show stat reconversion
    #print(stat_rank_scores) 
    
    num = 0
    output = []
    unique = []
    final_output = []
    for line_list in line_lists:
        num = num+1
        for term in line_list[:-1]:
            
            #deal w simple plurals french 
            #if term[-1] == 's':
            term_temp = term[:-1]
            term_plus = term+'s'
                
            if term_temp in unique or term in unique or term_plus in unique: #found a version already. dont send
                continue
            else:#no ver found. send original term to filter
                unique.append(term)
                keep,classification,chunks,rating,well_formedness_score = ok_statistical_term_fr(term,lenient=(num < lenient_simple_threshold),penalize_initial_the=penalize_initial_the)
           
                rank_score = stat_rank_scores[line_list[-1]]
                confidence = rank_score * well_formedness_score
            
          
           # if term not in unique:
          #      unique.append(term)
            #    print("added ", term, " to unique")
                output.append([confidence,term,keep,classification,rating,well_formedness_score,rank_score])
         #   else:
          #      continue
               
    output.sort()
    output.reverse()
    confidence_position = min(round(len(output)*percent_cutoff),numeric_cutoff)
    
    if len(output)>0:
        confidence_cutoff = output[confidence_position][0]
    else:
        confidence_cutoff = 0
        
    no_more_good_ones = False

    ##count for search
    count = 0

    
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
            
            if use_web_score and (count < webscore_max):
                
                ##wait a random amount of seconds every 3 requests
		##makes webscore part slow but avoids getting blocked after about 1000
                count+=1
                '''
                if ((count+3) % 3 == 0):
                    ls = [3, 5, 2, 4]
                    rd = random.choice(ls)
                    print("Waiting ", rd, " secs")
                    time.sleep(rd)
                '''

                print("Term ", count, ":", term)
                webscore,increment = webscore_one_term(term,use_web_score_dict=use_web_score_dict) ### fix this
                webscore += increment
                webscore = max(webscore,.1)                
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
    stream = open(outfile,'w',encoding='utf-8-sig') ##ADDED ENCODING
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
     
