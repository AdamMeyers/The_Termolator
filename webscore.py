## This file contains code to obtain and process websearches

## We will try Yahoo searches first because these seem to be our best
## option at the moment due to: lower and more flexible cost structure
## than Google and Bing.  Also, processing (and obtaining permissions)
## seems like it might be easier than Google, but that is not entirely
## clear yet.  Specifically, Google would end up be about .5 cents per
## search; Bing would be .2 cents per search and Yahoo costs about .08
## cents per search.

## Instructions for Yahoo searches on
## https://developer.yahoo.com/python/python-rest.html

## First experiments are with unauthenticated requests
## later we may need to sign up with yboss 
## and use an address like: "https://yboss.yahooapis.com/ysearch/web"
## see http://stackoverflow.com/questions/6796722/yahoo-boss-v2-authorization-troubles

from term_utilities import *
import urllib.request
import re
import math
import time

basic_yahoo_search_url_prefix = '''https://search.yahoo.com/search?p='''
basic_bing_search_url_prefix = '''https://search.yahoo.com/search?q='''
## basic_google_search_url_prefix = '''https://www.google.com/search?q='''

def replace_spaces_with_plus (term):
    return(term.replace(' ','+'))
    
def do_provider_search(term,provider):
    if provider == 'yahoo':
        url_prefix = basic_yahoo_search_url_prefix
    elif provider == 'bing':
        url_prefix = basic_bing_search_url_prefix
    # Google blocks program-generated searches 
    else:
        print('no such provider implemented:',provider)
    url = url_prefix + '"'+replace_spaces_with_plus(term)+'"'
    url_stream = urllib.request.urlopen(url)
    data = str(url_stream.read())
    return(data)

def do_provider_search_with_pause(term,provider,timing=1,reps=0):
    ## without this function, the system will halt every time
    ## the internet connection is interupted
    if reps>5:
        print('internet search failure')
        output = False
    else:
        try:
            output = do_provider_search(term,provider)
        except:
            print('Temporary internet search failure. Trying again')
            time.sleep(timing)
            output = do_provider_search_with_pause(term,provider,timing=timing,reps=reps+1)
    return(output)



def find_output_sets_by_comp_title(section, require_id=True,link_id_required=True):
    ## url,id,abstract,title
    ## substitute number for id
    ## 1) find <div class="compTitle" ...>... <a ... href=URL> TITLE </a> ...</div>
    ## 2) <div class="compText aAbs" > abstract </div>
    div_title_pattern = re.compile('<div [^>]*class="compTitle"[^>]*>(.*?)</div>')
    a_link_pattern = re.compile('<a ([^>]*)>(.*?)</a>')
    ## id_a_link_pattern = re.compile('<a id=([^>]*)>(.*?)</a>')
    href_search = re.compile('href="([^"]*)"')
    ## id_search = re.compile('id="([^"]*)"')
    ## link_id = re.compile('link-')
    ## id -- criteria for it being a document result
    ## alink surrounds title
    ## abstract_pattern = re.compile('<div [^>]*class="abstr"([^>]*)>(.*?)</div>')
    abstract_search = re.compile('<div [^>]*class="((compText aAbs)|(abstr))"([^>]*)>(.*?)</div>')
    ## abstract = main text of search result
    position = 0
    output = []
    output_set = []
    ## a_link = a_link_pattern.search(section,position)
    title_match = div_title_pattern.search(section)
    id_num = 0
    while title_match:
        output_set = []
        title_value = False
        href_value = False
        abstract_value = False
        a_link = a_link_pattern.search(title_match.group(1))
        if a_link:
            title_value = a_link.group(2)
        href_pattern = href_search.search(a_link.group(1))
        if href_pattern:
            href_value = href_pattern.group(1)
        id_num = id_num+1
        abstract_pattern = abstract_search.search(section,title_match.end())
        if abstract_pattern:
            abstract_value = abstract_pattern.group(5)
        output_set = [href_value,title_value,id_num,abstract_value]
        output.append(output_set)
        title_match = div_title_pattern.search(section,title_match.end())
    return(output)
    
def get_top_ten(term,provider='Yahoo'):
    global test_out
    provider = provider.lower()
    get_total_results = re.compile('<span[^>]*> *([0-9,]+) results *</span>')
    questionable_result_check = re.compile('((Showing)|(Including)) results for .{,40}<a href="https://search.yahoo.com/search')
    full_page = do_provider_search_with_pause(term,provider)
    total_results_match = False
    questionable_results = False
    if full_page:
        start = 0
        section = full_page ## stopped figuring out section
        total_results_match = get_total_results.search(section)
        questionable_results = questionable_result_check.search(section)
            ## find <a id="link-1"...> to <a id="link-10" ...>
            ## this includes a url
            ## and together with </a> surrounds the title
            ## there is an optional span tag that includes another url
            ## then there is usually a following <div class="X" field
            ## X="abstr" and indicates an abstract follows
            ##   -- other stuff follows <a url links with other labels, e.g., 
            ## titles that include Video Results or Image Results
        output = find_output_sets_by_comp_title(section)
                ## makes list: url, title, link label, abstract
                ## for Yahoo searches
                ## keyword searches would catch patents easily and somewhat
                ## articles as well
                ## should do Bing test as well
        if questionable_results:
            total_results = False
        elif total_results_match:
            total_results = str(total_results_match.group(1).replace(',',''))
        else:
            total_results = False
        return(output,total_results)
    else:
       return([],False)


def print_top_10(term,provider='yahoo'):
    ## useful primarily for debugging
    search_output,total_results = get_top_ten(term,provider=provider)
    for output_set in search_output:
        print('*** Next Set ***')
        for item in output_set:
            print(remove_xml(item))
        if total_results:
            print('total_results:',total_results)

def do_search_and_classify_top_10(term,provider='yahoo',minimum=5,debug=False,strict=False):
    ### keywords for patent:  patent, invention,
    ### keywords for academic: article, sciencedirect, proceedings, journal,
    ### PDF + edu, "related articles", dissertation, thesis, abstract
    ###
    patent_match = re.compile('patent',re.I)
    academic_string = 'article|sciencedirect|proceedings|journal|dissertation|thesis|abstract'
    academic_document_match = re.compile(academic_string,re.I)
    ## reference_match = re.compile('encyclopedia|dictionary',re.I)
    ## we found that hits for wikipedia and other references did not
    ## improve our scoring
    dot_pdf = re.compile('\.pdf($|[^a-z0-9])',re.I)
    dot_edu = re.compile('\.edu($|[^a-z0-9])',re.I)
    search_output,total_results = get_top_ten(term,provider=provider)
    if total_results:
        total_results = int(total_results)
        if total_results == 0:
            total_results = 'no total results'
    else:
        total_results = 'no total results'
    output_size = 0
    patent_count = 0
    academic_count = 0
    ## reference_count = 0
    for output_set in search_output:
        ## url, title, id, abstract
        pdf = False
        edu = False
        if (len(output_set) == 4) or (output_size == 10):
            url,title,id_code,abstract = output_set
            if not url:
                url = ''
            if not title:
                title = ''
            if not id_code:
                id_code = ''
            if not abstract:
                abstract = ''
        else:
            url=''
            title=''
            id_code=''
            abstract=''
            if debug:                
                print(output_set)
                print('problem: format of websearch may have changed.')
        if not url:
            url = ''
        if not title:
            title = ''
        if not id_code:
            id_code = ''
        if not abstract:
            abstract = ''
        if (not (url or title or abstract)) and debug:
            print('strange search output for',term)
        if patent_match.search(url) or patent_match.search(title) \
           or patent_match.search(abstract):
            patent_count = 1+patent_count
        elif academic_document_match.search(url) or academic_document_match.search(title) \
           or academic_document_match.search(abstract):
            academic_count = 1+academic_count
        # elif reference_match.search(url) or reference_match.search(title) or reference_match.search(abstract):
        #     reference_count = 1+reference_count
        else:
            for doc in [url,title,abstract]:
                if dot_pdf.search(doc):
                    pdf = True
                if dot_edu.search(doc):
                    edu = True
            if edu and pdf:
                academic_count = 1+academic_count
        if output_size<10:
            output_size = 1+output_size
    if (not strict) and (total_results == 'no total results') or (total_results == 0):
        if output_size < 10:
            total_results = output_size
        else:
            total_results = 100*minimum
    rating = (academic_count+patent_count)/10
    ## reference_score = reference_count/10
    if (total_results == 'no total results') or (total_results < minimum):
        enough = False
        total_results = 100*minimum
    else:
        enough = True
    if debug:
        print(term)
        ## return(rating,reference_score,total_results)
    return(rating,total_results)
        
def webscore_one_term(term,debug=False):
    search_rating, total_results = do_search_and_classify_top_10(term,debug=False)
    ## search_rating = (academic_count+patent_count)/10
    ## total_results = number of hits
    ## sample call: score_one_term('speech recognition system')
    output = []
    score = 'unscored'
    try:
        component1 = search_rating
        component2 = min(math.log(total_results,10),10)/10
        component2_weight = 2
        score = component1 * (component2 ** component2_weight)
    except:
        print('unscored:',term)
        print('component1:',component1)
        print('total_results:',total_results)
    ## these scores can be adjusted by changing the weights or
    ## adding a reference score (component1 can be set to search_rating + reference_score
    ## see the comments in do_search_and_classify_top_10
    if score == 'unscored':
        print('unscored:',term)
        return(0)
    return(score)

