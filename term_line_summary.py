from term_summary import *
from make_language_model import *
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
import os

Grank_order = True ## probably a better way to do this

language_model_file = DICT_DIRECTORY + 'gen2_lang.model'
profile_file = DICT_DIRECTORY + 'OANC.profile2'
language_model_name = 'generalized_character2'

def load_language_model(model_file,profile_file):
    global mean
    global maximum
    global minimum
    global stand_dev
    global ngrams
    mean,maximum,minimum,stand_dev = get_stats_from_profile(profile_file)##OANC.profile2
    for ngram in ngrams:
      ngram.clear()
    load_model_into_ngrams(model_file)

def merge_path(directory,filename):
    if directory.endswith(os.sep):
        return(directory+filename)
    else:
        return(directory+os.sep+filename)

def last_sentence_boundary(text):
    sentence_boundary = re.compile('\. *[A-Z]')
    matches = list(sentence_boundary.finditer(text))
    if len(matches) > 0:
        return(matches[-1].start()+1)
    else:
        return('nope')

def next_sentence_boundary(text):
    sentence_boundary = re.compile('\. *[A-Z]')
    match = sentence_boundary.search(text)
    if match:
        return(match.start()+1)
    else:
        return('nope')
        
def get_previous_line_break(text,end,max_distance=False):
    position = text[:end].rfind(os.linesep)
    sentence_boundary = re.compile('\. *[A-Z]')
    if position == -1:
        position = 0
    if max_distance and ((end-position)>max_distance):
        match = sentence_boundary.search(text[(end-max_distance):end])
        if match:
            position2 = match.start()+2
            position = position2+(end-max_distance)
        else:
            position2 = last_sentence_boundary(text[:end])
            if position2 != 'nope':
                position = position2
    return(position)

def get_following_line_break(text,start,max_distance=False):
    position_plus = text[start:].find(os.linesep)
    if position_plus == -1:
        position_plus = len(text)-start
    if max_distance and (position_plus > max_distance):
        position2 = next_sentence_boundary(text[(max_distance//2)+start:])
        if position2 != 'nope':
            position_plus = position2+(max_distance//2)
    return(start+position_plus)

def get_term_paragraph_from_term_map(instance_triple,text_file_directory,txt_file_list=False,txt_file_type='.txt3'):
    output = []
    infile,start,end = instance_triple
    start = int(start)
    end = int(end)
    if text_file_directory:
        infile = merge_path(text_file_directory,infile)
    if not infile.endswith(txt_file_type):
        infile = infile+txt_file_type
    with open(infile) as instream:
        all_text = instream.read()
        window_start = get_previous_line_break(all_text,start,max_distance=200)
        window_end = get_following_line_break(all_text,end,max_distance=200)
        next_text = all_text[window_start:window_end]+'\n'
        return([infile,next_text])

def get_most_probable_paragraphs_en(paragraphs,model_name=language_model_name,cutoff=-1,\
                                 top_percent=.5,minimum_len=10,max_number=100):
    pairs = []
    for infile,paragraph in paragraphs:
        segment_score = profile_segment(ngrams,model_name,paragraph)
        if ((segment_score == 'Null Segment') \
            or (segment_score < (mean - ((stand_dev * cutoff)/mean)))):
            pass
        else:
            pairs.append([segment_score,paragraph,infile])
    pairs.sort()
    pairs.reverse() ## puts highest score first
    output = []
    if len(pairs)>(2*minimum_len):
        pairs = pairs[:round(top_percent*len(pairs))]
    elif len(pairs)>minimum_len:
        pairs = pairs[:minimum_len]
    for pair in pairs:
        output.append((pair[1],pair[2]))
    if len(output)>max_number:
        output = output[:max_number]
    return(output)

def get_most_probable_paragraphs_chinese(input_list):
    output_list = []
    for sublist in input_list:
        if len(sublist) == 2:
            output_list.append([sublist[1], sublist[0]])
        else:
            output_list.append([])
    return output_list
    
def look_up_vector(cluster,vector_dict):
    if isinstance(cluster,int):
        if cluster in vector_dict:
            return(vector_dict[cluster])
        else:
            return(False)
    elif len(cluster) == 1:
        if cluster[0] in vector_dict:
            return(vector_dict[cluster[0]])
        else:
            return(False)
    else:
        if cluster in vector_dict:
            return(vector_dict[cluster])
        else:
            return(False)
            
def get_cosine_score(cluster1,cluster2,vector_dict,score_dict):
    if isinstance(cluster1,int):
        new_set1 = set()
        new_set1.add(cluster1)
    else:
        new_set1 = set(cluster1)   
    if isinstance(cluster2,int):
        new_set2 = set()
        new_set2.add(cluster2)
    else:
        new_set2 = set(cluster2)
    new_set = new_set1.union(new_set2)
    new_tuple = tuple(new_set)
    new_tuple = tuple(sorted(new_tuple))
    if new_tuple in score_dict:
        return(score_dict[new_set])
    else:
        vector1 = look_up_vector(cluster1,vector_dict)
        vector2 = look_up_vector(cluster2,vector_dict)
        if vector1 and vector2:
            return(cosine_similarity(vector1,vector2))
        else:
            print('error: no vectors for',cluster1,'and/or',cluster2)
            return(0)
            
            ### use tuples instead of single numbers for vectors
            ### for tuples, average of all individual vectors
            
            
def average_vectors(new_cluster,vectors):
    new_vector = []
    if not 0 in vectors:
        ## print(vectors) ## return empty vector
        return([])
    for num in range(len(vectors[0])):
        total = 0
        for cluster_num in new_cluster:
            total += vectors[cluster_num][num]
        average = total/len(new_cluster)
        new_vector.append(average)
    return(new_vector)

def make_cos_similar_clusters(vectors,cluster_num):
    ## only score each vector with higher numbered vectors
    ## store score in a dictionary
    clusters = []
    scores = {} ## scores is a dictionary of scores
    for key in list(vectors.keys()):
        clusters.append((key)) 
        ## keys are (ordered) tuples
        ## clusters is a list of tuples
    if len(clusters)<=cluster_num:
        stop = True
    else:
        stop = False
    num = 0
    while not stop:
        num = num+1
        score_list = [] ## score_list is a list of scores combining current pairs
        for num1 in range(len(clusters)):
            for num2 in range(num1+1,(len(clusters))):
                one_score = get_cosine_score(clusters[num1],clusters[num2],vectors,scores)
                score_list.append([one_score,num1,num2])
        high_score,item1,item2 = max(score_list, \
                                     key=lambda score_item: score_item[0])
        ## item1 has to precede item2
        cluster2 = clusters.pop(item2) ## popping a later position should not effect an earlier one
        cluster1 = clusters.pop(item1)
        ## error here attempt to pop from an empty list???
        ## *** 57 ***
        if isinstance(cluster1,int):
            cluster1 = (cluster1,)
        if isinstance(cluster2,int):
            cluster2 = (cluster2,)
        new_cluster = list(set(cluster1+cluster2))
        new_cluster.sort()
        ## eliminate duplicates and sort
        new_cluster = tuple(new_cluster) ## then turn into a tuple
        clusters.append(new_cluster)
        vectors[new_cluster]=average_vectors(new_cluster,vectors)
        if len(clusters) <= cluster_num:
            stop = True
        elif len(clusters) < 2:
            stop = True
    return(clusters)

def mmr_score(candidate, keyword_embedding, selected_sentence_embeddings, lambda_param=0.5):
    keyword_similarity = sklearn_cosine_similarity([candidate], [keyword_embedding])[0][0]
    if len(selected_sentence_embeddings) == 0:
        return keyword_similarity
    else:
        selected_similarities = sklearn_cosine_similarity([candidate], selected_sentence_embeddings)[0]
        max_selected_similarity = np.max(selected_similarities)
        return lambda_param * keyword_similarity - (1 - lambda_param) * max_selected_similarity


def mmr_algorithm(sentence_embeddings, keyword_embedding):
    initial_index = np.argmax(sklearn_cosine_similarity([keyword_embedding], sentence_embeddings))
    selected_indices = [initial_index]
    selected_sentence_embeddings = [sentence_embeddings[initial_index]]

    for _ in range(2):
        max_mmr = -float('inf')
        selected_index = -1
        for i, candidate in enumerate(sentence_embeddings):
            if i not in selected_indices:
                mmr = mmr_score(candidate, keyword_embedding, selected_sentence_embeddings)
                if mmr > max_mmr:
                    max_mmr = mmr
                    selected_index = i

        selected_indices.append(selected_index)
        selected_sentence_embeddings.append(sentence_embeddings[selected_index])

    return selected_indices


def choose_paragraphs_by_pre_train(term,list_data, model_name='infgrad/stella-base-zh-v2'):
    list_data = [sublist for sublist in list_data if len(sublist[0]) >= 10]
    list_data = [[sublist[0].replace('\n', ''), sublist[1]] for sublist in list_data]
    
    # Extract sentences
    sentences = [sublist[0] for sublist in list_data]

    # load pre-train
    model = SentenceTransformer(model_name)

    # encode
    keyword_embedding = model.encode([term], normalize_embeddings=True).flatten()
    sentence_embeddings = model.encode(sentences, normalize_embeddings=True)

    # do MMR algorithm
    selected_indices = mmr_algorithm(sentence_embeddings, keyword_embedding)

    return [list_data[i] for i in selected_indices]
    
    
def choose_paragraphs_by_local_tfidf(paragraph_list,vector_size=10,cluster_num=3,cluster_sample_strategy='big_centroid_max',lang_acronym='en'):
    ## 1) make vectors of N highest IDF words
    ##    that occur in at least 3 of the paragraphs
    ## 2) Dimensions filled by TFIDF scores
    ## 3) Cluster by similarity until there are at most
    ##    4 clusters
    ## 4) Choose vector with highest sum from each
    ##    cluster
    if lang_acronym=='zh': paragraph_list = paragraph_list[:100]
    output = []
    number_of_paragraphs = len(paragraph_list)
    distribution_marker = [] ## word_list,idf_counts,centroid
    idf_counts = {} 
    ## from tokens to numbers, later divided by number of paragraphs
    tf_counts = {} ## from line IDs to words to counts
    vectors = {} ## from line IDs to vectors
    ## for clusters, from ordered tuples to vectors
    for num in range(number_of_paragraphs):
        vectors[num] = [] ## initialize vector
        word_freq_dict = get_word_dist_from_paragraph(paragraph_list[num][0])
        ## infile = paragraph_list[num][1]
        tf_counts[num]=word_freq_dict
        for word in word_freq_dict:
            if word in idf_counts:
                idf_counts[word]+=1
            else:
                idf_counts[word]=1
    for key in idf_counts:
        num = number_of_paragraphs/idf_counts[key]
        idf_counts[key] = math.log(num)
        ## replace per paragraph counts with IDF
    word_list = list(idf_counts.keys())
    word_list.sort(key=lambda word: idf_counts[word])
    word_list = word_list[:vector_size] # only keep the top N words (N= vector_size)
    for num in range(number_of_paragraphs):
        vectors[num]=make_vector(word_list,tf_counts[num],idf_counts)
    clusters = make_cos_similar_clusters(vectors,cluster_num)
    output = []
    ## if (cluster_sample_strategy in ['big_centroid_max','big_centroid_min']) and (number_of_paragraphs>0):
    if (number_of_paragraphs>0):
        big_vector_list = tuple(range(number_of_paragraphs))
        average_vector = average_vectors(big_vector_list,vectors)
    else:
        average_vector = []
    distribution_marker = [word_list,idf_counts,average_vector]
    for cluster in clusters:
        if not(isinstance(cluster,int)) and\
           cluster_sample_strategy in ['centroid_min','centroid_max']:
            average_vector = average_vectors(cluster,vectors)
        ## clusters are lists of numbers
        if isinstance(cluster,int):
            top_paragraph = cluster
        elif cluster_sample_strategy=='maximum_sum':
            top_paragraph = max (cluster, \
                             key=lambda paragraph_num: \
                             sum(vectors[paragraph_num]))
        elif cluster_sample_strategy=='minimum_sum':
            top_paragraph = min (cluster, \
                             key=lambda paragraph_num: \
                             sum(vectors[paragraph_num]))
        elif cluster_sample_strategy in ['centroid_max','big_centroid_max']:
            ## find the paragraph furthest from the average
            top_paragraph = min (cluster, \
                                 key=lambda paragraph_num:
                                 cosine_similarity(vectors[paragraph_num],average_vector))
        elif cluster_sample_strategy in ['centroid_min','big_centroid_min']:
            ## find the paragraph closest to the average
            top_paragraph = max (cluster, \
                                 key=lambda paragraph_num:
                                 cosine_similarity(vectors[paragraph_num],average_vector))
        output.append(paragraph_list[top_paragraph])
    return(output,distribution_marker)

def one_word_filter(word,lang_acronym='en'):
    ## if (word.lower() in pos_dict) and (nom_class(word.lower(),'noun') == 0):
    if (word.lower() in pos_dict):
        return(True)
    elif ordinal_pattern(word):
        return(True)
    elif lang_acronym=='en' and len(word) < 4:
        return(True)
    elif lang_acronym=='zh' and len(word) < 2:
        return(True)
    elif not re.search('^[a-zA-Z]+$',word[:3]) and lang_acronym=='en':
        return(True)
    else:
        return(False)

def get_approximate_summaries_shelve(term,variants,distribution_marker=False,trace=False):
    clean_term = term.strip('\'";:-_+=`?')
    if clean_term != term:
        possible_paragraph = get_first_paragraph_from_wikipedia_xml_shelve(clean_term,quiet=True,distribution_marker=distribution_marker,trace=trace)
        if possible_paragraph:
            return([[clean_term,possible_paragraph]])
    summaries = []
    substrings = []
    subseqs = []
    word_list = term.split(' ')  
    if len(word_list) == 1:
        pass
    else:
        for num1 in range(len(word_list)):
            for num2 in range(num1+1,len(word_list)+1):
                subseq = word_list[num1:num2]
                if subseq != word_list:
                    subseqs.append(subseq)
    subseqs.sort(key=lambda sequence: (-1 * len(sequence)))
    ## put longest sequences first
    for subseq in subseqs:
        word_nums = len(subseq)
        if (word_nums == 1) and one_word_filter(subseq[0]):
            continue
        ## skip 1 word terms that do not pass a test
        ## regarding whether or not these are "good" terms.
        substring = ' '.join(subseq).lower()
        found = False
        for substr2,sum in summaries:
            if substring in substr2:
                found = True
        if found:
            continue        
        summary = get_first_paragraph_from_wikipedia_xml_shelve(substring,variants=variants,quiet=True,distribution_marker=distribution_marker,trace=trace)
        if summary:
            summaries.append([substring,summary])
    return(summaries)

def choose_items_randomly(sequence,number):
    output = []
    while (len(output)<number) and (len(sequence)>0):
        index = random.randint(0,len(sequence)-1)
        output.append(sequence.pop(index))
    return(output)

fixed_term_set_list = []
    
def get_next_term_map_entry(instream):
    stop = False
    term = False
    entry = False
    instances = []
    term_string_pattern = re.compile('<term string="([^"]*)"')
    variants_pattern = re.compile('variants="([^"]*)"')
    file_start_end_pattern = re.compile('file="([^"]*)" *start=([0-9]+) *end=([0-9]+)')
    rank_pattern = re.compile('rank=([0-9]+)')
    while not stop:
        next_line = instream.readline()
        next_line = next_line.strip(os.linesep)
        if next_line == '':
            stop = True
        if re.search('</term>',next_line):
            stop = True
        elif re.search('<term',next_line):
            term_match = term_string_pattern.search(next_line)
            variants_match = variants_pattern.search(next_line)
            rank_match = rank_pattern.search(next_line)
            if (not term_match) or (not variants_match):
                print('error in get_next_term_map_entry on line',next_line)
            else:
                term = term_match.group(1)
                variants = variants_match.group(1).split('|')
            if rank_match:
                rank = int(rank_match.group(1))
        elif re.search('<instance',next_line):
            instance_match = file_start_end_pattern.search(next_line)
            if not instance_match:
                print('No instances?:')
                print(next_line)
                ## input('pause')
            instance = [instance_match.group(1),instance_match.group(2),instance_match.group(3)]
            instances.append(instance)
    if term:
        entry = {'rank':rank,'variants':variants,'instances':instances}
    return(term,entry)

def get_term_dict_from_map_file(term_map_file):
    term_dict = {}
    with open(term_map_file) as instream:
        keep_going = True
        while keep_going:
            term,entry = get_next_term_map_entry(instream)
            if term:
                term_dict[term]=entry
            else:
                keep_going = False
    return(term_dict)

def filter_only_chinese(lst):
    chinese_pattern = re.compile(r'^[\u4e00-\u9fa5]+$')
    
    filtered_lst = [item for item in lst if chinese_pattern.match(item)]
    
    return filtered_lst
    
def write_terms(outstream,terms,text_file_directory,txt_file_list,txt_file_type,cluster_sample_strategy,trace=False,lang_acronym='en'):
    config = read_config()
    if lang_acronym == 'zh':
        terms=filter_only_chinese(terms)
    print("Terms here: ",terms)
    for term in terms:
        print("Writing term: ",term)
        variants =term_dict[term]['variants']
        if not term in variants:
            variants = [term]+variants
        if trace:
            print('Term',term)
        outstream.write('*************************************\n')
        outstream.write('Term Summary for "'+term+'"\n')    
        outstream.write('*************************************\n')
        outstream.flush()
        entry = term_dict[term]
        selection1 = []
        distribution_marker = False
        stages = []
        term_paragraphs = []
        for instance_triple in entry['instances']:
            term_paragraph = get_term_paragraph_from_term_map(instance_triple,text_file_directory,txt_file_list=txt_file_list,txt_file_type=txt_file_type)
            term_paragraphs.append(term_paragraph)                
        ## pairs of the form [file,paragraph]
        if len(term_paragraphs)>0:
            stages.append(1)
        if txt_file_type==".txt":
            term_paragraphs = get_most_probable_paragraphs_chinese(term_paragraphs)
        else:
            term_paragraphs = get_most_probable_paragraphs_en(term_paragraphs)
        if len(term_paragraphs)>0:
            stages.append(2)
        print("tfidf...")
        selection1,distribution_marker = choose_paragraphs_by_local_tfidf(term_paragraphs,cluster_sample_strategy=cluster_sample_strategy,lang_acronym=lang_acronym)
        #selection1=choose_paragraphs_by_pre_train(term,term_paragraphs)
        
        if len(selection1) == 0:
            print('No selected paragraphs for',term)
            print('stages:',stages)
            ## input('pause')
        else:
            pass
            
        if config['use_shelve'] == 'True':
            if (not ' ' in term) and one_word_filter(term,lang_acronym):
                ## filter one word terms that are not "normal" enough
                wiki_summary = False
            else:
                print("getting paragraph from slv...")
                wiki_summary = get_first_paragraph_from_wikipedia_xml_shelve(term, variants=variants, quiet=True,
                                                                             distribution_marker=distribution_marker,
                                                                             trace=trace)
            if (not wiki_summary):
                print("getting approximate paragraph from slv...")
                approximate_summaries = get_approximate_summaries_shelve(term, variants,
                                                                         distribution_marker=distribution_marker)
            else:
                approximate_summaries = False
        
            if wiki_summary:
                outstream.write('Wikipedia First Paragraph for "' + term + '"\n\n')
                outstream.write(wiki_summary)
                outstream.write('\n\n')
                outstream.flush()
            elif approximate_summaries:
                #outstream.write('Wikipedia First Paragraph for substrings of "' + term + '"\n\n')
                for subterm, summary in approximate_summaries:
                    outstream.write('Wikipedia First Paragraph for substring "' + subterm + '"\n\n')
                    outstream.write(summary)
                    outstream.write('\n\n')
                    outstream.flush()
            else:
                outstream.write('No Wikipedia Entry Found')
                outstream.write('\n\n')
                outstream.flush()
        else:
            print("getting paragraph online...")
            wiki_summary,is_subterm = get_wikipedia_approximate_summaries_online_by_API(term)
            if wiki_summary:
                print(len(wiki_summary))
                for subterm, summary in wiki_summary.items():
                    outstream.write('Wikipedia First Paragraph for substring "' + subterm + '"\n\n') if is_subterm else outstream.write('Wikipedia First Paragraph for "' + subterm + '"\n\n') 
                    outstream.write(summary)
                    outstream.write('\n\n')
                    outstream.flush()
            else:
                outstream.write('No Wikipedia Entry Found')
                outstream.write('\n\n')
                outstream.flush()
                
        if len(selection1)> 0:
            outstream.write('Sample Passages mentioning the term:"'\
                            +term+'"\n\n')
            for paragraph,infile in selection1:
                outstream.write('From file: '+infile+': ')
                outstream.write(paragraph+'\n')
            outstream.write('*********************************************\n\n')
            outstream.flush()
        else:
            outstream.write('No Sample Passages Found\n')
            outstream.flush()

def log_10_termset(terms):
    import math
    length = len(terms)
    log_length = round(math.log(length,10))
    sets = []
    start = 0
    for exponent in range(1,log_length+1):
        end = (10**exponent)
        if length<=end:
            sets.append(terms[start:])
        else:
            sets.append(terms[start:end])
            start = end
    return(sets)
    ##

    
def generate_summaries_from_term_file_map(term_map_file,summary_outfile,text_file_directory,txt_file_list=False,model_file=language_model_file,profile_file=profile_file,test_on_n_terms=False,cluster_sample_strategy='big_centroid_max',choose_terms_randomly=False,fixed_term_set=False,txt_file_type='.txt3',trace=False,breakdown_by_log_10 = False,lang_acronym='en'):
    global term_dict
    global fixed_term_set_list
    global Grank_order
    if Grank_order:
        rank_order = True
    else:
        rank_order = False
    if not txt_file_type.startswith('.'):
        txt_file_type = "." + txt_file_type
    print('Loading term dict')
    term_dict = get_term_dict_from_map_file(term_map_file)
    print('completed loading')
    terms = list(term_dict.keys())
    load_language_model(model_file,profile_file)
    outstream = open(summary_outfile,'w')
    terms.sort(key = lambda key: term_dict[key]['rank'])
    if breakdown_by_log_10:
        first_item = 1
        log_level = 1
        termsets = log_10_termset(terms)
        for termset in termsets:
            outstream.write('*********************************************\n\n')
            outstream.write('Terms '+str(first_item)+' to '+ str(10**log_level)+'\n')
            outstream.write('*********************************************\n\n')
            first_item = 1 + (10**log_level)
            log_level +=1
            termset.sort()
            write_terms(outstream,termset,text_file_directory,txt_file_list,txt_file_type,cluster_sample_strategy,trace=trace,lang_acronym=lang_acronym)
    else:
        if not rank_order:
            terms.sort() 
        if test_on_n_terms:
            if choose_terms_randomly:
               terms = choose_items_randomly(terms,test_on_n_terms)
               fixed_term_set_list = terms[:]
            elif fixed_term_set and (len(fixed_term_set_list)>0):
                terms = fixed_term_set_list
            else:
               terms = terms[:test_on_n_terms]
        write_terms(outstream,terms,text_file_directory,txt_file_list,txt_file_type,cluster_sample_strategy,trace=trace,lang_acronym=lang_acronym)
    outstream.close()        

    


