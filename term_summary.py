import requests
import re
import math
import time
from term_utilities import *
import csv
import shelve
import wikipedia

basic_wikipedia_search_url = "https://en.wikipedia.org/wiki/"

## wikipedia_xml_file = "enwiki-20190101-pages-articles-multistream.xml"

wiki_shelve_open = False
wiki_shelve = False
redirect_shelve = False
## There does not seem to be any way to test
## whether a "shelve" is open
## -- So I am using this flag

count = 0

initialize_utilities()

def ends_with_non_terminal_punctuation(text):
    if re.search('[,:();] *$',text):
        return(True)
    else:
        return(False)

def may_refer_to_entry (title,entry):
    global count
    try:
        if len(entry)>50:
            return(False)
        title = re.escape(title).lower()
        ## entry = re.escape(entry)
        title_pattern = title + '(.*)(may|can) refer to:? *$'
        entry = entry.lower()
        if re.search(title_pattern,entry,re.I):
            count += 1
            return(True)
        else:
            return(False)
    except:
        print('Problem with title:',title)
        print('Problem with entry:',entry)
        ## input('pause')

def replace_spaces_with_underscores(search_term):
    output = search_term.replace(' ','_')
    return(output)

def look_up_wikipedia_page_from_internet(search_term):
    search_term = replace_spaces_with_underscores(search_term)
    url = basic_wikipedia_search_url+search_term
    response = requests.get(url).text
    return(response)

def get_first_paragraph_from_wikipedia_entry(entry,min_length=500):
    paragraph_start = re.compile('<p[^>]*>')
    paragraph_end = re.compile('</p>')
    done = False
    start = 0
    while not done:
        next_paragraph_start = paragraph_start.search(entry,start)
        if next_paragraph_start:
            start = next_paragraph_start.end()
            next_paragraph_end = paragraph_end.search(entry,start)
            if next_paragraph_end:
                end = next_paragraph_end.start()
                text = remove_xml(entry[start:end])
                if (len(text) < min_length) or (ends_with_non_terminal_punctuation(text)):
                    new_next_p_end = paragraph_end.search(entry,end+10)
                    if new_next_p_end:
                        next_paragraph_end = new_next_p_end
                        end = next_paragraph_end.start()                 
                        text = remove_xml(entry[start:end]) 
                if re.search('[a-z]{3}',text):
                   return(text)
                else:
                   start = next_paragraph_end.end()
            else:
                done = True
        else:
            done=True   
    return(False)

def print_paragraphs_from_wikipedia_entry(entry):
    paragraph_start = re.compile('<p[^>]*>')
    paragraph_end = re.compile('</p>')
    done = False
    start = 0
    while not done:
        next_paragraph_start = paragraph_start.search(entry,start)
        if next_paragraph_start:
            start = next_paragraph_start.end()
            next_paragraph_end = paragraph_end.search(entry,start)
            if next_paragraph_end:
                end = next_paragraph_end.start()
                text = remove_xml(entry[start:end])
                if re.search('[a-z]{3}',text):
                   print(text)
                start = next_paragraph_end.end()
            else:
                done = True
        else:
            done = True
    return(False)

def non_match(entry):
    if re.search('<b>Wikipedia does not have an article with this exact name.</b>',entry,re.I):
        return(True)
    else:
        return(False)

def print_out_all_paragraphs_from_wikipedia_online(search_term):
    ## using online wikipedia instead of shelved wikipedia
    full_page = look_up_wikipedia_page_from_internet(search_term)
    if non_match(full_page):
        return(False)
    print_paragraphs_from_wikipedia_entry(full_page)

def is_chinese(string):
    return bool(re.match(r'^[\u4e00-\u9fff]+$', string))
    
def get_first_paragraph_from_wikipedia_online(search_term):
    global basic_wikipedia_search_url
    basic_wikipedia_search_url = "https://zh.wikipedia.org/wiki/" if is_chinese(search_term) else "https://en.wikipedia.org/wiki/"
    ## using online wikipedia instead of shelved wikipedia
    full_page = look_up_wikipedia_page_from_internet(search_term)
    if non_match(full_page):
        print("false")
        return(False)
    return(get_first_paragraph_from_wikipedia_entry(full_page))

def get_wikipedia_approximate_summaries_online(term):

    summaries = {}
    # firstly try to get summary of term
    summary = get_first_paragraph_from_wikipedia_online(term)
    if summary:
        summaries[term] = summary
        return summaries
    
    # Try subterms if term does not exist in wiki
    words = list(term) if is_chinese(term) else term.split()
    for i in range(len(words), 0, -1):
        for j in range(len(words) - i + 1):
            sub_term = ''.join(words[j:j+i]) if is_chinese(term) else ' '.join(words[j:j+i])
            summary = get_first_paragraph_from_wikipedia_online(sub_term)
   
            # Not allowed if sub_term is contained in other
            if summary and not any(sub_term in longer_term for longer_term in summaries):
                summaries[sub_term] = summary
                    
    return summaries

def get_wikipedia_approximate_summaries_online_by_API(term):
    summaries = {}
    is_subterm=False

    wikipedia.set_lang("zh" if is_chinese(term) else "en")
    try:
        summary = wikipedia.summary(term, sentences=5,auto_suggest=False)  
        if summary:
            summaries[term] = summary
            return summaries,is_subterm
    except wikipedia.exceptions.DisambiguationError:
        pass  
    except wikipedia.exceptions.PageError:
        pass  

    words = list(term) if is_chinese(term) else term.split()
    for i in range(len(words), 0, -1):
        for j in range(len(words) - i + 1):
            sub_term = ''.join(words[j:j+i]) if is_chinese(term) else ' '.join(words[j:j+i])
            try:
                summary = wikipedia.summary(sub_term, auto_suggest=False)  
                if summary and not any(sub_term in longer_term for longer_term in summaries):
                    summaries[sub_term] = summary
            except wikipedia.exceptions.DisambiguationError:
                continue  
            except wikipedia.exceptions.PageError:
                continue
    is_subterm = True
    return summaries,is_subterm

    
def get_next_id_paragraph_title(instream,infile=False,minimum_length=500):
    doc_id_pattern = re.compile('<doc id="([0-9]+)".*title="([^"]*)".*>')
    doc_end_pattern = re.compile('</doc>')
    stop = False
    title = False
    doc_id = False
    paragraph = False
    while not stop:
        next_line = instream.readline()
        if next_line == '':
            stop = True
        elif doc_end_pattern.search(next_line):
            if title and doc_id and paragraph:                
                return(paragraph,doc_id,title)
            else:
                paragraph,doc_id,title = False, False, False
        elif doc_id and title and (not paragraph):
            next_line = next_line.strip(os.linesep)
            if (next_line.lower() == title) or not re.search('[a-zA-Z]',next_line):
                pass
            else:
                paragraph = next_line ## paragraphs seem to be on single lines
        elif doc_id and title and (not doc_id_pattern.search(next_line)) and paragraph and ((len(paragraph) < minimum_length)  \
                                                                                                or (ends_with_non_terminal_punctuation(paragraph))):
            next_line = next_line.strip(os.linesep)
            paragraph = paragraph + ' ' + next_line
        else:
            match = doc_id_pattern.search(next_line)
            if match:
                doc_id = match.group(1)
                title = match.group(2)
                title = title.lower() ## regularize titles to lowercase
    return(False,False,False) ## if there are no more left

def get_first_paragraph_id_and_title_triples_from_file(infile,first_paragraph_hash):
    ## this function should work regardless of whether first_paragraph_hash
    ## is a dictionary or a shelve
    with open(infile) as instream:
        stop = False
        ambigs = 0
        while (not stop):
            first_paragraph,id,title = get_next_id_paragraph_title(instream,infile=infile)
            if not title:
                stop = True
            elif may_refer_to_entry(title,first_paragraph):
                pass
            elif title in first_paragraph_hash:
                first_paragraph_hash[title].append([id, first_paragraph])
                ambigs += 1
            else:
                first_paragraph_hash[title] = [[id, first_paragraph]]
        return(ambigs)

def get_implied_redirect(source,goal):
    goal_redirect_pattern = '^(.*)\([^\)]*\)$'
    goal_match = re.search(goal_redirect_pattern,goal,re.I)
    if goal_match:
        prefix = goal_match.group(1).lower()
        if source.lower().startswith(prefix):
            return(prefix.strip())
    else:
        return(False)

def load_wiki_shelves(wiki_shelve,redirect_shelve,paragraph_directory,redirect_file):
    ## files in paragraph_directory
    ## pages go from <doc ..> </doc>
    ## id = <doc id="12" ...>
    ## articles.csv
    ## id,title,redirect
    ## articles.csv:2051,Anarchist,Anarchism

    ## 1) wiki_shelve should get info from wiki_extractor
    ##    title --> id number, first paragraph

    ## 2) redirect_shelve should get info from following process:
    ## go through lines in articles.csv
    ##    for each redirect, associate with corresponding first
    ##    paragraph (or create redirect, which allows lookup
    ##    from Anarchist to Anarchism to paragraph

    subdirectories = os.listdir(paragraph_directory)
    ambiguous_titles = 0
    for subdirectory in subdirectories:
        filelist = os.listdir(paragraph_directory+os.sep+subdirectory)
        for infile in filelist:
            infile = paragraph_directory+os.sep+subdirectory+os.sep+infile
            ambiguous_titles += get_first_paragraph_id_and_title_triples_from_file(infile,wiki_shelve)
    print('There are',ambiguous_titles,'ambiguous titles')
    print(count,'entries were skipped due to "may refer to"')
    with open(redirect_file) as instream:
        first_line = instream.readline()
	## ignore first line (labels)
        ambig_redirects = 0
        for row in csv.reader(instream):
            id,source,goal = row
            source = source.lower() ## regularize to lower case
            goal = goal.lower()
            if not (goal in wiki_shelve):
                ## if there is no entry, there is no point redirecting
                pass
            elif (source in redirect_shelve): 
                redirect_shelve[source].append(goal)
                ambig_redirects += 1
            else:
                redirect_shelve[source]=[goal]
            if goal and (goal in wiki_shelve):
                source2 = get_implied_redirect(source,goal)
            else:
                source2 = False
            if source2:
                if source2 in redirect_shelve:
                    redirect_shelve[source2].append(goal)
                    ambig_redirects += 1
                else:
                    redirect_shelve[source2]=[goal]
    print('There are',ambig_redirects,'ambigous redirects')
    return(wiki_shelve,redirect_shelve)

def get_wikipedia_score(paragraph,distribution_marker):
    if (not distribution_marker) or (not paragraph):
        return(0)
    if len(paragraph)< 40:
        factor = .5
    else:
        factor = 1
    word_list,idf_counts,average_vector = distribution_marker 
    word_freq_dict = get_word_dist_from_paragraph(paragraph)
    paragraph_vector = make_vector(word_list,word_freq_dict,idf_counts)
    score = cosine_similarity(average_vector,paragraph_vector)
    return(score*factor)



def bad_abbreviation_filter(paragraph,required_words):
    paragraph = paragraph.lower().split()
    ## input('pause')
    for word in required_words:
        if word in paragraph:
            return(False)
    else:
        return(True)

## big_flag = True ## testing new feature

def get_first_paragraph_from_wikipedia_xml_shelve(term,variants=[],paragraph_directory="wiki-extractor-output",redirect_file="wiki-basic-output/articles.csv",shelve_file = "wiki.slv", shelve_redirect_file = "swiki.slv",quiet=False,initialize=False,distribution_marker=False,trace=False): 
    ## 1) Once compiled in a file, it is very fast access 
    ## 2) However, will not work across different versions of Python
    ##    Creating shelve files under one version and loading them in another
    ## will lead to a "bad magic number" error.
    ## 3) Only one process can access a shelves file at a time.
    ##    It is an error for a second process to attempt a connection
    ##    (I guess it is possible to copy shelve files though).
    global DICT_DIRECTORY
    ## global big_flag
    if paragraph_directory:
        paragraph_directory = DICT_DIRECTORY + paragraph_directory
    if redirect_file:
        redirect_file = DICT_DIRECTORY + redirect_file
    if shelve_file:
        shelve_file = DICT_DIRECTORY + shelve_file
    if shelve_redirect_file:
        shelve_redirect_file = DICT_DIRECTORY + shelve_redirect_file
    ## set wikipedia info files so they are in DICT_DIRECTORY

    global wiki_shelve_open
    global wiki_shelve
    global redirect_shelve
    term = term.lower()  
    if wiki_shelve_open:
        pass
    elif os.path.isfile(shelve_file):
        start_time = time.time()
        wiki_shelve = shelve.open(shelve_file,writeback=True)
        redirect_shelve = shelve.open(shelve_redirect_file,writeback=True)
        end_time = time.time()
        print('Loading time:',round(end_time-start_time),'seconds')
        wiki_shelve_open = True
    else:
        wiki_shelve = shelve.open(shelve_file)
        redirect_shelve = shelve.open(shelve_redirect_file)
        start_time = time.time()
        load_wiki_shelves(wiki_shelve,redirect_shelve,paragraph_directory,redirect_file)
        end_time = time.time()
        print('Creating shelves and Loading time:',round(end_time-start_time),'seconds')
        wiki_shelve_open = True
    best_entry = False
    top_score = 0
    term_list = [term]
    one_word_terms = []
    words_in_multi_word_terms = []
    for t in variants:
        space_count = t.count(' ')
        if space_count == 0:
            one_word_terms.append(t)
        else:
            big_word = ''
            for w in t.split():
                # if not big_flag:
                #     pass -- next elif instead of if
                if big_word == '':
                    big_word = w
                else:
                    big_word = big_word+'_'+w
                if (not w in words_in_multi_word_terms) \
                  and (not w in closed_class_stop_words):
                    words_in_multi_word_terms.append(w)
            ##if big_flag and (big_word != ''):
            if (big_word != ''):
                term_list.append(big_word)
        if t != term:
            term_list.append(t)
    for term2 in term_list:
        length_score = math.log(len(term2))
        ## favor longer key words for wikipedia
        if term2 in wiki_shelve:
            full_entry = wiki_shelve[term2]
            for entry in full_entry:
                if (term2 in one_word_terms) and words_in_multi_word_terms and \
                  (bad_abbreviation_filter(entry[1], words_in_multi_word_terms)):
                    current_score = -1
                else:
                    current_score = get_wikipedia_score(entry[1],distribution_marker)\
                      *length_score
                ## second item in entry is paragraph
                if current_score == -1:
                    pass
                elif (current_score > top_score) or (not best_entry):
                    best_entry = entry
                    top_score = current_score
        if (term2 in redirect_shelve):
            for search_term in redirect_shelve[term2]:
                if search_term in wiki_shelve:
                    full_entry = wiki_shelve[search_term]
                    for entry in full_entry:
                        if (term2 in one_word_terms) and words_in_multi_word_terms and \
                            (bad_abbreviation_filter(entry[1], words_in_multi_word_terms)):
                            current_score = -1
                        else:
                            current_score = get_wikipedia_score(entry[1],distribution_marker)\
                              *length_score
                        ## second item in entry is paragraph
                        if current_score == -1:
                            pass
                        elif (current_score > top_score) or (not best_entry):
                            best_entry = entry
                            top_score = current_score
    if best_entry:
       term_id,first_paragraph = best_entry
    else:
       term_id,first_paragraph = False,False
    if (not quiet) and (not term_id):
       print('The term "'+term+'" was not found')
    if first_paragraph and trace:
       print('Term',term,'score',top_score)
    ## unclear if we need term_id for anything (perhaps ambiguity resolution later)
    return(first_paragraph)
    
