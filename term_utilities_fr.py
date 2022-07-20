##term utilities FR components

import random
import os
import shutil
import re
import time


DICT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + os.sep

ORG_DICTIONARY = DICT_DIRECTORY+'orgs_abbrev_dict_fr.txt'
LOC_DICTIONARY = DICT_DIRECTORY+'cities_eng.dict'
french_gazetteer = DICT_DIRECTORY+'french_gazetteer.txt'
NAT_DICTIONARY = DICT_DIRECTORY+'nationality_dict_fr.txt'
nom_file = DICT_DIRECTORY+'french_nomlist.dict'
person_name_file =  DICT_DIRECTORY+'french_names.dict'
verb_morph_file = DICT_DIRECTORY+'verb_dict_fr.txt'
general_dict_file = DICT_DIRECTORY+'dictionary_full_fr.txt'
person_name_general_file = DICT_DIRECTORY+'person_name_list_simple.dict'
english_dict_file = DICT_DIRECTORY+'english_dict_list.txt'


## FR lists
nom_map_dict_fr = []
fr_gazetteer = []
nationality_dict_fr = []
location_dict_fr = []
organization_dict_fr = []
verb_dict_fr = []
person_name_dict_fr = []
general_dict_fr = []
person_name_general = []
english_dict = []

def read_in_simple_dictionary_fr (dict_file,dictionary):
    if dictionary == 'org':		
        organization_dict_fr.clear()	
    elif dictionary == 'loc':
    	location_dict_fr.clear()
    elif dictionary == 'gaz':
        fr_gazetteer.clear()
    elif dictionary == 'nat':
        nationality_dict_fr.clear()
    elif dictionary == 'nom':
        nom_map_dict_fr.clear()
    elif dictionary == 'pers':
        person_name_dict_fr.clear()
    elif dictionary == 'verb':
        verb_dict_fr.clear()
    elif dictionary == 'general':
        general_dict_fr.clear()
    elif dictionary == 'pers-general':
        person_name_general.clear()
    elif dictionary == 'eng_general':
        english_dict.clear()

    with open(dict_file,'r',encoding='utf-8-sig') as instream:
        #print('opening ', dict_file)
        for line in instream:
            line = line.strip()
            #print(line)
	    
            if dictionary == 'org':
                organization_dict_fr.append(line)
            elif dictionary == 'loc':
                location_dict_fr.append(line)
            elif dictionary == 'gaz':
                fr_gazetteer.append(line)
            elif dictionary == 'nat':
                nationality_dict_fr.append(line)
            elif dictionary == 'nom':
                nom_map_dict_fr.append(line)
            elif dictionary == 'pers':
                person_name_dict_fr.append(line)
            elif dictionary == 'verb':	    
                verb_dict_fr.append(line)
            elif dictionary == 'general':
                general_dict_fr.append(line)
            elif dictionary == 'pers-general':
                person_name_general.append(line)
            elif dictionary == 'eng_general':
                english_dict.append(line)
    #    print(fr_gazetteer)
        

#for FR: not using POS info after stage 1 for now
def initialize_utilities_fr():
    #print("in initialize util fr")
    global parentheses_pattern2
    global parentheses_pattern3

    read_in_simple_dictionary_fr(ORG_DICTIONARY,dictionary='org')
    read_in_simple_dictionary_fr(LOC_DICTIONARY,dictionary='loc')
    read_in_simple_dictionary_fr(french_gazetteer,dictionary='gaz')
    read_in_simple_dictionary_fr(NAT_DICTIONARY,dictionary='nat')
    read_in_simple_dictionary_fr(nom_file,dictionary='nom')
    read_in_simple_dictionary_fr(person_name_file,dictionary='pers')
    read_in_simple_dictionary_fr(verb_morph_file,dictionary='verb')	
    read_in_simple_dictionary_fr(general_dict_file,dictionary='general')
    read_in_simple_dictionary_fr(person_name_general_file,dictionary='pers-general') 
    read_in_simple_dictionary_fr(english_dict_file,dictionary='eng_general')


initialize_utilities_fr()
