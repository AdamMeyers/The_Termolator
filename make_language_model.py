import re
import os
import string
import math

unigrams = {}
bigrams = {}
trigrams = {}
fourgrams = {}
fivegrams = {}

ngrams = [unigrams,bigrams,trigrams,fourgrams,fivegrams]

def non_english_alphachar(char):
  ## Adapted from Stackoverflow post: https://stackoverflow.com/questions/280712/javascript-unicode-regexes/8933546#8933546
  ## There does not seem to be an implemented standard Python method for doing this
  if re.match('[\u00AA\u00B5\u00BA\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02C1\u02C6-\u02D1\u02E0-\u02E4\u02EC\u02EE\u0370-\u0374\u0376\u0377\u037A-\u037D\u037F\u0386\u0388-\u038A\u038C\u038E-\u03A1\u03A3-\u03F5\u03F7-\u0481\u048A-\u052F\u0531-\u0556\u0559\u0561-\u0587\u05D0-\u05EA\u05F0-\u05F2\u0620-\u064A\u066E\u066F\u0671-\u06D3\u06D5\u06E5\u06E6\u06EE\u06EF\u06FA-\u06FC\u06FF\u0710\u0712-\u072F\u074D-\u07A5\u07B1\u07CA-\u07EA\u07F4\u07F5\u07FA\u0800-\u0815\u081A\u0824\u0828\u0840-\u0858\u08A0-\u08B4\u0904-\u0939\u093D\u0950\u0958-\u0961\u0971-\u0980\u0985-\u098C\u098F\u0990\u0993-\u09A8\u09AA-\u09B0\u09B2\u09B6-\u09B9\u09BD\u09CE\u09DC\u09DD\u09DF-\u09E1\u09F0\u09F1\u0A05-\u0A0A\u0A0F\u0A10\u0A13-\u0A28\u0A2A-\u0A30\u0A32\u0A33\u0A35\u0A36\u0A38\u0A39\u0A59-\u0A5C\u0A5E\u0A72-\u0A74\u0A85-\u0A8D\u0A8F-\u0A91\u0A93-\u0AA8\u0AAA-\u0AB0\u0AB2\u0AB3\u0AB5-\u0AB9\u0ABD\u0AD0\u0AE0\u0AE1\u0AF9\u0B05-\u0B0C\u0B0F\u0B10\u0B13-\u0B28\u0B2A-\u0B30\u0B32\u0B33\u0B35-\u0B39\u0B3D\u0B5C\u0B5D\u0B5F-\u0B61\u0B71\u0B83\u0B85-\u0B8A\u0B8E-\u0B90\u0B92-\u0B95\u0B99\u0B9A\u0B9C\u0B9E\u0B9F\u0BA3\u0BA4\u0BA8-\u0BAA\u0BAE-\u0BB9\u0BD0\u0C05-\u0C0C\u0C0E-\u0C10\u0C12-\u0C28\u0C2A-\u0C39\u0C3D\u0C58-\u0C5A\u0C60\u0C61\u0C85-\u0C8C\u0C8E-\u0C90\u0C92-\u0CA8\u0CAA-\u0CB3\u0CB5-\u0CB9\u0CBD\u0CDE\u0CE0\u0CE1\u0CF1\u0CF2\u0D05-\u0D0C\u0D0E-\u0D10\u0D12-\u0D3A\u0D3D\u0D4E\u0D5F-\u0D61\u0D7A-\u0D7F\u0D85-\u0D96\u0D9A-\u0DB1\u0DB3-\u0DBB\u0DBD\u0DC0-\u0DC6\u0E01-\u0E30\u0E32\u0E33\u0E40-\u0E46\u0E81\u0E82\u0E84\u0E87\u0E88\u0E8A\u0E8D\u0E94-\u0E97\u0E99-\u0E9F\u0EA1-\u0EA3\u0EA5\u0EA7\u0EAA\u0EAB\u0EAD-\u0EB0\u0EB2\u0EB3\u0EBD\u0EC0-\u0EC4\u0EC6\u0EDC-\u0EDF\u0F00\u0F40-\u0F47\u0F49-\u0F6C\u0F88-\u0F8C\u1000-\u102A\u103F\u1050-\u1055\u105A-\u105D\u1061\u1065\u1066\u106E-\u1070\u1075-\u1081\u108E\u10A0-\u10C5\u10C7\u10CD\u10D0-\u10FA\u10FC-\u1248\u124A-\u124D\u1250-\u1256\u1258\u125A-\u125D\u1260-\u1288\u128A-\u128D\u1290-\u12B0\u12B2-\u12B5\u12B8-\u12BE\u12C0\u12C2-\u12C5\u12C8-\u12D6\u12D8-\u1310\u1312-\u1315\u1318-\u135A\u1380-\u138F\u13A0-\u13F5\u13F8-\u13FD\u1401-\u166C\u166F-\u167F\u1681-\u169A\u16A0-\u16EA\u16F1-\u16F8\u1700-\u170C\u170E-\u1711\u1720-\u1731\u1740-\u1751\u1760-\u176C\u176E-\u1770\u1780-\u17B3\u17D7\u17DC\u1820-\u1877\u1880-\u18A8\u18AA\u18B0-\u18F5\u1900-\u191E\u1950-\u196D\u1970-\u1974\u1980-\u19AB\u19B0-\u19C9\u1A00-\u1A16\u1A20-\u1A54\u1AA7\u1B05-\u1B33\u1B45-\u1B4B\u1B83-\u1BA0\u1BAE\u1BAF\u1BBA-\u1BE5\u1C00-\u1C23\u1C4D-\u1C4F\u1C5A-\u1C7D\u1CE9-\u1CEC\u1CEE-\u1CF1\u1CF5\u1CF6\u1D00-\u1DBF\u1E00-\u1F15\u1F18-\u1F1D\u1F20-\u1F45\u1F48-\u1F4D\u1F50-\u1F57\u1F59\u1F5B\u1F5D\u1F5F-\u1F7D\u1F80-\u1FB4\u1FB6-\u1FBC\u1FBE\u1FC2-\u1FC4\u1FC6-\u1FCC\u1FD0-\u1FD3\u1FD6-\u1FDB\u1FE0-\u1FEC\u1FF2-\u1FF4\u1FF6-\u1FFC\u2071\u207F\u2090-\u209C\u2102\u2107\u210A-\u2113\u2115\u2119-\u211D\u2124\u2126\u2128\u212A-\u212D\u212F-\u2139\u213C-\u213F\u2145-\u2149\u214E\u2183\u2184\u2C00-\u2C2E\u2C30-\u2C5E\u2C60-\u2CE4\u2CEB-\u2CEE\u2CF2\u2CF3\u2D00-\u2D25\u2D27\u2D2D\u2D30-\u2D67\u2D6F\u2D80-\u2D96\u2DA0-\u2DA6\u2DA8-\u2DAE\u2DB0-\u2DB6\u2DB8-\u2DBE\u2DC0-\u2DC6\u2DC8-\u2DCE\u2DD0-\u2DD6\u2DD8-\u2DDE\u2E2F\u3005\u3006\u3031-\u3035\u303B\u303C\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FC-\u30FF\u3105-\u312D\u3131-\u318E\u31A0-\u31BA\u31F0-\u31FF\u3400-\u4DB5\u4E00-\u9FD5\uA000-\uA48C\uA4D0-\uA4FD\uA500-\uA60C\uA610-\uA61F\uA62A\uA62B\uA640-\uA66E\uA67F-\uA69D\uA6A0-\uA6E5\uA717-\uA71F\uA722-\uA788\uA78B-\uA7AD\uA7B0-\uA7B7\uA7F7-\uA801\uA803-\uA805\uA807-\uA80A\uA80C-\uA822\uA840-\uA873\uA882-\uA8B3\uA8F2-\uA8F7\uA8FB\uA8FD\uA90A-\uA925\uA930-\uA946\uA960-\uA97C\uA984-\uA9B2\uA9CF\uA9E0-\uA9E4\uA9E6-\uA9EF\uA9FA-\uA9FE\uAA00-\uAA28\uAA40-\uAA42\uAA44-\uAA4B\uAA60-\uAA76\uAA7A\uAA7E-\uAAAF\uAAB1\uAAB5\uAAB6\uAAB9-\uAABD\uAAC0\uAAC2\uAADB-\uAADD\uAAE0-\uAAEA\uAAF2-\uAAF4\uAB01-\uAB06\uAB09-\uAB0E\uAB11-\uAB16\uAB20-\uAB26\uAB28-\uAB2E\uAB30-\uAB5A\uAB5C-\uAB65\uAB70-\uABE2\uAC00-\uD7A3\uD7B0-\uD7C6\uD7CB-\uD7FB\uF900-\uFA6D\uFA70-\uFAD9\uFB00-\uFB06\uFB13-\uFB17\uFB1D\uFB1F-\uFB28\uFB2A-\uFB36\uFB38-\uFB3C\uFB3E\uFB40\uFB41\uFB43\uFB44\uFB46-\uFBB1\uFBD3-\uFD3D\uFD50-\uFD8F\uFD92-\uFDC7\uFDF0-\uFDFB\uFE70-\uFE74\uFE76-\uFEFC\uFF21-\uFF3A\uFF41-\uFF5A\uFF66-\uFFBE\uFFC2-\uFFC7\uFFCA-\uFFCF\uFFD2-\uFFD7\uFFDA-\uFFDC]',char):
    return(True)

def increment_ngram_hash_table(hash_table,key):
  if type(key) == list:
    key = tuple(key)
  if key in hash_table:
    hash_table[key] += 1
  else:
    hash_table[key] = 1

def record_5_gram(char,previous_chars,hash_table_list):
  ## hash_table_list is list of 5 hash tables:
  ## [1-gram,2-gram,3-gram,4-gram,5-gram]
  ## previous_chars = [-4,-3,-2,-1]
  # print(char)
  # print(previous_chars)
  # input('pause')
  increment_ngram_hash_table(hash_table_list[0],char)
  for index in range(len(previous_chars)):
    back_index = -1 * (index+1)
    key = previous_chars[back_index:]
    key.append(char)
    increment_ngram_hash_table(hash_table_list[index+1],key)

char_types1 = ['WHITESPACE','DIGIT','SENT_PUNCTUATION','WORD_SYMBOL_PUNCTUATION',
        'MATH_PUNCTUATION',
        'NUMERIC_SYMBOL','VOWEL','STOP','FRICATIVE','AFFRICATE','NASAL','SEMIVOWEL',
        'OTHER_LETTER', 'UPPER_VOWEL','UPPER_STOP','UPPER_FRICATIVE','UPPER_AFFRICATE',
        'UPPER_NASAL','UPPER_SEMIVOWEL','UPPER_OTHER_LETTER','NONASCII_LETTER',
        'UPPER_NONASCII_LETTER', 'OTHER']

char_types2 = ['WHITESPACE','DIGIT','LETTER','PUNCTUATION','OTHER']

def characterize_next_segment(character,output,char_model_name):
  if char_model_name == 'VANILLA':
    output.append(character)
  elif char_model_name == 'generalized_character2':
    if character in string.whitespace:
      output.append('WHITESPACE')
    elif character in '0123456789':
      output.append('DIGIT')
    elif character in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
      output.append('LETTER')
    elif character in string.punctuation:
      output.append('PUNCTUATION')
    else:
      output.append('OTHER')    
  elif char_model_name == 'generalized_character1':
    if character in string.whitespace:
      output.append('WHITESPACE')
    elif character in '0123456789':
      output.append('DIGIT')
    elif character in '''`!()-_[{]};:\'",.?–—−''':
      ## note that this includes endash, emdash and minus
      ## which are not part of string.punctuation
      output.append('SENT_PUNCTUATION')
    elif character in '#$%&@':
      ## these are part of string.punctuation
      ## they can be standins for words
      output.append('WORD_SYMBOL_PUNCTUATION')
    elif character in '*+/<=>\\^|~':
      ## these are part of string.punctuation
      output.append('MATH_PUNCTUATION')
    elif character.isnumeric():
      ## includes non-digit numbers, e.g., '½' or '万'
      output.append('NUMERIC_SYMBOL')
    elif character.isalpha():
      ## ignores different characterization of consonant clusters
      ## e.g., "sh", "ch", not really handled correctly
      if character.isupper():
        upper = True
        character = character.lower()
      else:
        upper = False
      if character in 'aeiou':
        char_type = 'VOWEL'
      elif character in 'bcdgkpqt':
        char_type = 'STOP'
      elif character in 'fsvz':
        char_type = 'FRICATIVE'
      elif character in 'jx':
        char_type = 'AFFRICATE'
      elif character in 'mn':
        char_type = 'NASAL'
      elif character in 'hlrwy':
        char_type = 'SEMIVOWEL'
      elif non_english_alphachar(character):
        char_type = 'NONASCII_LETTER'
      else:
        print('This should be impossible')
        print('***',character,'***')
        ## input('pause')
        print('.isalpha should only be true for letters a-z and some accented letters')
        char_type = 'OTHER_LETTER'
      if upper:
        output.append('UPPER_'+char_type)
      else:
        output.append(char_type)
    elif non_english_alphachar(character):
      if character.isupper():
        output.append('UPPER_NONASCII_LETTER')
      else:
        output.append('NONASCII_LETTER')
    else:
      output.append('OTHER')
  else:
    print('No such model name has been defined:',char_model_name)
    output.append(character)

def char_model_preprocess_segment(text_segment,char_model_name):
  output = []
  for character in text_segment:
    characterize_next_segment(character,output,char_model_name)
  return(output)

def update_5_gram_char_model_on_line(character_model_hash_list,char_model_name,text_segment):
  previous_chars = [False,False,False,'START']
  length = 0
  hash_index = -2
  while length < len(character_model_hash_list)-1:
    hash_table = character_model_hash_list[hash_index-length]
    start_key = tuple(previous_chars[length:])
    if False in start_key:
      pass
    elif len(start_key) == 1:
      start_key = start_key[0]
    if isinstance(start_key,tuple) and (False in start_key):
      pass
    elif start_key in hash_table:
      hash_table[start_key]+=1
    else:
      hash_table[start_key]=1
    length += 1
  preprocessed_segment = char_model_preprocess_segment(text_segment,char_model_name)
  preprocessed_segment.append('END') ## add an end of segment marker
  for char in preprocessed_segment:
    record_5_gram(char,previous_chars,character_model_hash_list)
    previous_chars.pop(0)
    previous_chars.append(char)

def train_model(infile_list,ngrams,model_name,output_file,verbose=False):
  ## go through text and count instances of 1 to N grams
  unigrams.clear()
  bigrams.clear()
  trigrams.clear()
  fourgrams.clear()
  fivegrams.clear()
  with open(infile_list,encoding='utf-8-sig') as instream:
    for line in instream:
      filename=line.strip(os.linesep)
      with open(filename,encoding='utf-8',errors="replace") as textstream:
        for text_chunk in textstream.read().split(os.linesep+os.linesep):
          ## assume that two line separators in a row break text into units
          text_chunk = text_chunk.strip() 
          ## whitespace at the beginning and end of a segment is irrelevant
          ## the parts at the beginning mark the beginning of the string
          linesep_num = text_chunk.count(os.linesep)
          if (linesep_num > 2) and (len(text_chunk)>(200*linesep_num)):
            for small_text_chunk in text_chunk.split(os.linesep):
              update_5_gram_char_model_on_line(ngrams,model_name,small_text_chunk)
          else:
            update_5_gram_char_model_on_line(ngrams,model_name,text_chunk)
  for higher,lower in [[fivegrams,fourgrams],
                       [fourgrams,trigrams],
                       [trigrams,bigrams],
                       [bigrams,unigrams],
                       ]:
    remove = []
    for high_key in higher:
      low_key = high_key[0:len(high_key)-1]
      if len(low_key) == 1:
        low_key = low_key[0]
      if False in high_key:
        remove.append(high_key)        
      elif low_key in lower:
        ratio = higher[high_key]/lower[low_key]
        if ratio <= 0:
           print('Why is ratio for',high_key,'over',low_key,'equal to zero or less')
           print(high_key,higher[high_key])
           print(low_key,lower[low_key])
        higher[high_key]=math.log(ratio)
      elif (low_key == False) or (low_key[-1]==False):
        ## 'Start' can be the first item in lower
        ## but preceding ones don't make sense
        ## e.g., FALSE FALSE START STOP
        ## allows a bigram, trigram, etc. for STOP,
        ## but START does not allow N-grams except Unigram
        pass
      else:
        print('Error: n-grams are not correctly updating')
        print(high_key,'is in',str(len(high_key))+'-gram table')
        print('There are',higher[high_key],'instances')
        print(low_key,'is not in',str(len(low_key))+'-gram table')
        higher[high_key]=0
    for key in remove:
      higher.pop(key)
  total_unigrams = 0 
  for value in unigrams.values():
    total_unigrams += value
  for key in unigrams:
    ratio = unigrams[key]/total_unigrams
    if ratio == 0:
      print('Why is ratio for key',key,'equal to zero')
    unigrams[key]=math.log(ratio)
  for table in ngrams:
    values = list(table.values())
    minimum = min(values)
    table['Minimum']=minimum
  with open(output_file,'w',encoding='utf-8-sig') as outstream:
    for name,table in [[1,unigrams],[2,bigrams],[3,trigrams],[4,fourgrams],[5,fivegrams]]:
      outstream.write('<'+str(name)+'>\n')
      for key,value in table.items():
        outstream.write(str(key)+'\t'+str(value)+'\n')        
      outstream.write('</'+str(name)+'>\n')

def lookup_5_gram(char,previous_chars,character_model_hash_list):
  ## OK for first items because tuples with False will not be found
  key = previous_chars[:]
  if 'START' in key:
    index = key.index('START')
    key = key[index:]
  key = tuple(key)
  if len(key) == 5:
    if key in fivegrams[key]:
      return(fivegrams[key])
    else:
      return(fivegrams['Minimum'])
  elif len(key) == 4:
    if key in fourgrams:
      return(fourgrams[key])
    else:
      return(fourgrams['Minimum'])
  elif len(key) == 3:
    if key in trigrams:
      return(trigrams[key])
    else:
      return(trigrams['Minimum'])
  elif len(key) == 2:
    if key in bigrams:
      return(bigrams[key])
    else:
      return(bigrams['Minimum'])
  elif char in unigrams:
    return(unigrams[char])
  else:
    return(unigrams['Minimum'])

def profile_segment(character_model_hash_list,char_model_name,text_segment):
  ## next make the first part similar to update_5_gram_char_model_on_line
  ## but lookup probabilities instead of counting or calculating
  total_prob = 0
  count = 0
  previous_chars = [False,False,False,'START']
  preprocessed_segment = char_model_preprocess_segment(text_segment,char_model_name)
  if len(preprocessed_segment)>0:
    for char in preprocessed_segment:    
      value = lookup_5_gram(char,previous_chars,character_model_hash_list)
      ## print(char,value)
      previous_chars.pop(0)
      previous_chars.append(char)
      total_prob +=value
      count +=1
    return(total_prob/count) ## average probability of segment
  else:
    return('Null Segment')

def get_stats_from_profile(import_file):
  distribution = re.compile('^<Distribution.*')
  range_info = re.compile('^<Absolute_Range.*')
  ## stand_dev_info = re.compile('^<Stand_devs_from_mean.*')
  distrib_values = re.compile('mean="([^"]*)" standard_dev="([^"]*)"')
  range_values = re.compile('maximum="([^"]*)" minimum="([^"]*)"')
  ## sd_values = re.compile('high="([^"]*)" low="([^"]*)"')
  mean_sd = False
  range_v = False
  ## sd_v = False
  with open(import_file,encoding='utf-8-sig') as instream:
    for line in instream:
      sd = distribution.search(line)
      if sd and not mean_sd:
        mean_sd = distrib_values.search(line)
        if mean_sd:
          ## print(1,mean_sd.group(0))
          mean = float(mean_sd.group(1))
          stand_dev = float(mean_sd.group(2))
      ri  = range_info.search(line)
      if ri and not range_v:
        range_v = range_values.search(line)
        ## print(2,range_v.group(0))
        maximum = float(range_v.group(1))
        minimum = float(range_v.group(2))
      # if stand_dev_info.search(line):
      #   sd_v = sd_values.search(line)
      #   high = float(sd_v.group(1))
      #   low = fload(sd_v.group(2))
      # if mean_sd and range_v and sd_v:
      if mean_sd and range_v:
        return(mean,maximum,minimum,stand_dev)
      
def load_model_into_ngrams(model_file):
  with open(model_file,encoding='utf-8-sig') as instream:
    for line in instream:
      line = line.strip(os.linesep)
      if line == '<1>':
        current_ngram = unigrams
      elif line == '<2>':
        current_ngram = bigrams
      elif line == '<3>':
        current_ngram = trigrams        
      elif line == '<4>':
        current_ngram = fourgrams        
      elif line == '<5>':
        current_ngram = fivegrams
      elif '\t' in line:
        feature,value = line.split('\t')
        if isinstance(feature,str) and ('(' in feature):
          feature = eval(feature)
        value = float(value)
        current_ngram[feature]=value
  
def profile_file(char_model_name,model_file,infile_list,outfile,import_profile=False):
  if os.path.isfile(import_profile):
    mean,maximum,minimum,stand_dev = get_stats_from_profile(import_profile)
    calculate_stats = False
  else:
    calculate_stats = True
  for ngram in ngrams:
    ngram.clear()
  load_model_into_ngrams(model_file) 
  with open(infile_list,encoding='utf-8-sig') as instream:
    values = []
    chunks = []
    for line in instream:
      text_file = line.strip(os.linesep)
      with open(text_file,encoding='utf-8-sig',errors='replace') as textstream:
        offset = 0
        start = offset
        for text_chunk in textstream.read().split(os.linesep+os.linesep):
           ## strip text_chunk before profiling
          linesep_num = text_chunk.count(os.linesep)
          if (linesep_num > 2) and (len(text_chunk)>(200*linesep_num)):
             for small_chunk in text_chunk.split(os.linesep):
               end = start+len(small_chunk)
               chunks.append([text_file,start,end])
               value = profile_segment(ngrams,char_model_name,small_chunk.strip())
               if value == 'Null Segment':
                 chunks.pop()
               else:
                 values.append(value)
               start = end+1 ## 1 for the 1 linesep
          else:
            end = start+len(text_chunk)
            chunks.append([text_file,start,end])
            value = profile_segment(ngrams,char_model_name,text_chunk.strip())
            if value == 'Null Segment':
              ## null segments (all white space) don't count
              chunks.pop()
            else:
              values.append(value)
          start = end+2 ## 2 for the 2 lineseps
  if calculate_stats:
      mean = sum(values)/len(values)
      sum_of_squares = 0
      denominator = len(values)-1 ## with Bessel's correction
      if denominator < 1:
        no_profile = True
      else:
        no_profile = False
        for value in values:
          difference = value-mean
          square = difference**2
          sum_of_squares +=square
        variance = sum_of_squares/denominator
        stand_dev = variance**.5
  else:
    no_profile = False  
  with open(outfile,'w',encoding='utf-8-sig') as outstream:
    if no_profile:
      pass
    else:
      maximum = max(values)
      minimum = min(values)
      max_mean_diff = abs((maximum-mean)/stand_dev)
      min_mean_diff = abs((minimum-mean)/stand_dev)      
      diff = (maximum-minimum)/stand_dev
      property_line = '<Distribution mean="'+str(mean)+'" standard_dev="'+str(stand_dev)+'"/>\n'
      Range_line = '<Absolute_Range maximum="'+str(maximum)+'" minimum="'+str(minimum)+'"/>\n'
      Mean_line = '<Stand_devs_from_mean high="'+str(max_mean_diff)+'" low="'+str(min_mean_diff)+'"/>\n'
      for line in [property_line,Range_line,Mean_line]:
        outstream.write(line)
    outstream.write('\n\n')
    for index in range(len(values)):
      text_file,start,end = chunks[index]
      value = values[index]
      xml_line = '<Segment file="'+text_file+'" start="'+str(start)+'" end="'+str(end)+'" value="'+str(value)+'"/>\n'
      outstream.write(xml_line)

def filter_text_piece(text_piece,char_model_name,ngrams,cutoff,mean,stand_dev):
  ## based on profile_file
  offset = 0
  start = offset
  values = []
  chunks = []
  output = []
  for text_chunk in text_piece.split(os.linesep+os.linesep):
    linesep_num = text_chunk.count(os.linesep)
    if (linesep_num > 2) and (len(text_chunk)>(200*linesep_num)):
      for small_chunk in text_chunk.split(os.linesep):
        end = start+len(small_chunk)
        chunks.append([start,end])
        value = profile_segment(ngrams,char_model_name,small_chunk.strip())
        if value == 'Null Segment':
          chunks.pop()
        else:
          values.append(value)
        start = end+1 ## 1 for the 1 linesep
    else:
      end = start+len(text_chunk)
      chunks.append([start,end])
      value = profile_segment(ngrams,char_model_name,text_chunk.strip())
      if value  == 'Null Segment':
        chunks.pop()
      else:
        values.append(value)
    start = end + 2 ## 2 for the 2 lineseps
  for index in range(len(values)):
    ## value = probability
    difference = (values[index]-mean)/stand_dev
    if difference > cutoff:
      output.append(chunks[index])
  return(output)

def get_sample_print_out_from_profile(profile_file,output_file,sample_multiple=1):
  mean,maximum,minimum,stand_dev = get_stats_from_profile(profile_file)
  pattern = re.compile('<Segment file="([^"]*)" start="([^"]*)" end="([^"]*)" value="([^"]*)"')
  example_table = {}
  with open(profile_file,encoding='utf-8-sig') as instream:
    for line in instream:
      match = pattern.search(line)
      if match:
        infile = match.group(1)
        start = int(match.group(2))
        end = int(match.group(3))
        value = float(match.group(4))
        difference = (value-mean)/stand_dev
        if (difference > 1) or (difference <-1):
          difference = round(difference)
        else:
          difference = round(difference,1)
        if not difference in example_table:
          example_table[difference]=[[infile,start,end,value]]
        elif len(example_table[difference]) < sample_multiple:
          example_table[difference].append([infile,start,end,value])
  differences = list(example_table.keys())
  differences.sort()
  with open(output_file,'w',encoding='utf-8-sig') as outstream:
    for difference in differences:
      if difference in example_table:
        outstream.write('*** Difference at '+str(difference)+' standard deviations from the mean ***\n')
        for diff in example_table[difference]:
          infile,start,end,value = diff
          with open(infile) as instream:
            text = instream.read()[start:end]
            outstream.write('*** File: '+infile+' ***\n\n')
            outstream.write(text)
            outstream.write('\n***\n')
        outstream.write('\n**************************************\n\n')
  

def train_on_OANC():
  ## this creates gen2_lang.model and OANC.profile2, which are currently
  ## used for filtering.
  ## Other language models and profiles can be created and used.
  ## The input text should be a utf-8 text file (like all-OANC.txt)
  train_model('lang_model1_input.list',ngrams,'generalized_character2','gen2_lang.model')
  profile_file('generalized_character2','gen2_lang.model','lang_model1_input.list','OANC.profile2')

#added for FR to create files for lang model  
def train_on_FR_leipzig():
  train_model('modelFRinput-leipzig.list',ngrams,'generalized_character2','lang_model_fr_leipzig.model')
  profile_file('generalized_character2','lang_model_fr_leipzig.model','modelFRinput-leipzig.list','leipzigFR.profile')
  
def print_OANC_demo():
  ## This demo illustrates the sort of text that are different numbers of standard deviations
  ## from the mean probability. This illustrates what different cutoffs could rule out.
  get_sample_print_out_from_profile('OANC.profile2','OANC.printout2')

def filter_fact_file(textfile,in_fact_file,out_fact_file,ngrams,model_name,model_file,profile_file,cutoff=-1,initialize=False):
  global mean
  global maximum
  global minimum
  global stand_dev
  ## borrowing from inline_terms.py
  ## Cutoff is in terms of standard deviations from the training corpus mean
  ## -1 means that if the probability is lower than the probability at -1 standard deviations 
  ## from the mean, it is ruled out. -1 and higher (including the mean and SDs above the mean)
  ## are OK.
  ## Our current hypothesis is that -1 is OK for normal text and that 0 or -0.2 are OK for
  ## text (like patents) that tend to have more unusuable text.
  structure_pattern = re.compile('STRUCTURE *TYPE="TEXT" *START=([0-9]*) *END=([0-9]*)',re.I)
  txt_stream = open(textfile,encoding='utf-8-sig')
  txt = txt_stream.read()
  txt_stream.close()
  if initialize or (len(unigrams)==0):
    mean,maximum,minimum,stand_dev = get_stats_from_profile(profile_file)##OANC.profile2
    for ngram in ngrams:
      ngram.clear()
    load_model_into_ngrams(model_file)    
  with open(in_fact_file,encoding='utf-8-sig') as instream,open(out_fact_file,'w',encoding='utf-8-sig') as outstream:
    for line in instream:
      match = structure_pattern.search(line)
      if match:
        start = int(match.group(1))
        end = int(match.group(2))
        text_piece = txt[start:end]
        good_pieces = filter_text_piece(text_piece,model_name,ngrams,cutoff,mean,stand_dev)
        for p_start,p_end in good_pieces:
          out_string = 'STRUCTURE TYPE="TEXT" START='+str(p_start+start)+' END='+str(p_end+start)+'\n'
          outstream.write(out_string)
      else:
        outstream.write(line)
        
  
def filter_fact_files(file_list,model_name,model_file,profile_file,cutoff=-1):
  global ngrams
  with open(file_list,encoding='utf-8-sig') as instream:
    for line in instream:
      line = line.strip(os.linesep)
      textfile,in_fact_file,out_fact_file = line.split(';')
      ### revise fact file to make new fact file
      filter_fact_file(textfile,in_fact_file,out_fact_file,ngrams,\
                       model_name,model_file,profile_file,cutoff=cutoff)

def make_filter_printout(txt_file,fact_file,good_file,bad_file):
  structure_pattern = re.compile('STRUCTURE *TYPE="TEXT" *START=([0-9]*) *END=([0-9]*)',re.I)
  with open(txt_file,encoding='utf-8-sig') as instream:
    text = instream.read()
  with open(fact_file,encoding='utf-8-sig') as instream,open(good_file,'w',encoding='utf-8-sig') as \
    goodstream, open(bad_file,'w') as badstream:
    start = 0
    good_number = 0
    bad_number = 0
    for line in instream:
       match = structure_pattern.search(line)
       if match:
         text_start = int(match.group(1))
         text_end = int(match.group(2))
         good_piece = text[text_start:text_end]
         good_number += 1
         goodstream.write('\n***** Good Section '+str(good_number)+' *********\n')
         goodstream.write(good_piece)
         if text_start > start:
           bad_piece = text[start:text_start]
           if re.search('[^ \n\r\t]', bad_piece):
             bad_number += 1
             badstream.write('\n***** Bad Section '+str(bad_number)+' *********\n')
             badstream.write(bad_piece)
           start = text_end

def apply_model_to_simple_example(input_string,profile_file,ngrams,model_name,model_file,cutoff=-1):
  ## profile_file = OANC.profile2'
  ## ngrams = ngrams
  ## model_name = 'generalized_character2'
  ## model_file = 'gen2_lang.model'
  ## 
  global mean
  global maximum
  global minimum
  global stand_dev
  mean,maximum,minimum,stand_dev = get_stats_from_profile(profile_file)
  for ngram in ngrams:
      ngram.clear()
  load_model_into_ngrams(model_file)
  value = profile_segment(ngrams,model_name,input_string)
  print(value)
