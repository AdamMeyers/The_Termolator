##webscore Fr ver

from webscore import *
from term_utilities import *
import urllib.request
import requests
import re
import math
import time

basic_yahoo_search_url_prefix_fr = '''https://fr.search.yahoo.com/search?p='''
basic_bing_search_url_prefix_fr = '''https://fr.search.yahoo.com/search?q='''
   
def do_provider_search_fr(term,provider):
    if provider == 'webcorp':
        use_quotes = False
    else:
        use_quotes = True
    if provider == 'yahoo':
        url_prefix = basic_yahoo_search_url_prefix_fr
        url_suffix = False
    elif provider == 'bing':
        url_prefix = basic_bing_search_url_prefix_fr
        url_suffix = False
    elif provider == 'webcorp':
        url_prefix = webcorp_prefix
        url_suffix = webcorp_suffix
    # Google blocks program-generated searches 
    else:
        print('no such provider implemented:',provider)
    if use_quotes:
        url = url_prefix + '"'+replace_spaces_with_plus(term)+'"'
    else:
        url = url_prefix + replace_spaces_with_plus(term)
    if url_suffix:
        url = url+url_suffix
    ## url_stream = urllib.request.urlopen(url)

    response = requests.get(url).text
    ## data = str(url_stream.read())
    # data = url_stream.inof().get_content_charset()
    # data = url_stream.read().decode('utf-8')
    # print(2)
    
    print("Length of response: ", len(response))
    return(response)

def do_provider_search_with_pause_fr(term,provider,timing=1,reps=0):
    ## without this function, the system will halt every time
    ## the internet connection is interupted
    if reps>5:
        print('internet search failure')
        output = False
    else:
        try:
            output = do_provider_search_fr(term,provider)
        except Exception as ex:
            print(ex)
            print('Temporary internet search failure. Trying again')
            time.sleep(timing)
            output = do_provider_search_with_pause_fr(term,provider,timing=timing,reps=reps+1)
    return(output)


def get_top_ten(term,provider='Yahoo'):
    global test_out
    provider = provider.lower()
    if provider in ['yahoo','bing']:
        get_total_results = re.compile('<span[^>]*> *([0-9,]+) results *</span>')
        questionable_result_check = re.compile('((Showing)|(Including)) results for .{,40}<a href="https://search.yahoo.com/search')
    elif provider in ['webcorp']:
        get_total_results = re.compile('Search API returned ([0-9]+) hits. WebCorp successfully')
        questionable_result_check = re.compile('No results found',re.I)
    else:
        print('Error: This system is not designed for the',provider,"search engine. Please use Yahoo, Bing or Web as a Corpus (webcorp)")
    full_page = do_provider_search_with_pause_fr(term,provider)
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
        if provider in ['yahoo','bing']:
            output = find_output_sets_by_comp_title(section)
                ## makes list: url, title, link label, abstract
                ## for Yahoo searches
                ## keyword searches would catch patents easily and somewhat
                ## articles as well
                ## should do Bing test as well
        elif provider in ['webcorp']:
            output = find_webcorp_output_sets(section)
        else:
            ## not tuned to other search engines
            output = False
        if questionable_results:
            total_results = False
        elif total_results_match:
            total_results = str(total_results_match.group(1).replace(',',''))
        else:
            total_results = False
        return(output,total_results)
    else:
       return([],False)

