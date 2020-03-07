#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#driver function for stage 1 filter

import sys, copy
#from stage1_fr import *
from term_utilities_fr import *
from term_utilities import *

def main(args):
	listfile = args[1]
	#print("list file:", listfile)
	new = listfile + ".substring_list"
	newlist = open(new, "w+", encoding="utf-8-sig")
	#print('opened:', newlist)

	#for every doc name in list, run stage1 filter
	with open(listfile, "r", encoding="utf-8-sig") as doclist:
		for line in doclist:
			line = line.rstrip()
			#print("chunkfile:", line)
			stage1_filter(line)
			newlist.write(line+".substring\n")		

def stage1_filter(arg):
	
	infile = arg.rstrip()
	#print("infile:", infile)
	endings = ["e.g.", "e.g", "etc", "etc.", "cf", "cf.", "e.i.", "e.i", "et al."]
	articles_sw = ["résultat", "résultats", "discussion", "conclusion", "introduction", "résumé", 	"summary", "abstract", "figure", "figures", "tableau", "références", "étude", "études", "pubmed", "scholar", "epub"]
	extensions =  [".com", ".fr", ".org", ".gov", ".gouv", ".co", ".net", ".eu", ".js", ".ex", ".exe", ".ly", "'s"]
	determiners = ["les", "ce", "celle", "ces", "cette", "cettes", "le", "la", "l'", 
				"un", "une", "des", "d'", "etc", "qui", "que", "quelle",
				"au", "aux", "du", "mon", "ma", "mes", "ton", "ta", "tes",
				"son", "sa", "ses", "notre", "nos", "votre", "vos", "leur",
				"aucun", "chaque", "nul", "plusieurs", "quelques", "certains"]
	#write to new file
	#same filename but add .stage1 at the end
	outname = infile + ".substring"
	stage1_out = open(outname, "w+", encoding="utf-8-sig")

	#rejected file
	#reject = infile + ".stage1_rejected"
	#rejected = open(reject, "w+", encoding="utf-8-sig")

	with open(infile, "r", encoding="utf-8-sig") as chunklist:
		for term in chunklist:

			keep = True

			term_og = term
			term = term.rstrip()
			termarray = list(term.strip())
			#print("term array:", termarray)

			#replace all apostrophes with standard " ' " in place
			change = False
			for i in range(len(termarray)):
				if termarray[i] == '’' or termarray[i] == '´' or termarray[i] == '‘':
					#print("found apostrophe:", termarray[i])
					termarray[i] = '\''
					change = True
 			
			if change:
				term = ''.join(termarray)
				#print("new term (apostrophe fixed):", term)
			
			if term.isdigit(): #remove term if it is all numbers
				#rejected.write(term+"\n")
				term = ""
				keep = False
				continue


			#look at each word in potential term
			
			words = term.split(" ")
			#print("words array:", words)
			
			for i in range(len(words)):
				#handle dets that are not split from the words
				#if (len(words[i]) > 2):
				if (i == 0):
					if (words[i][:2].lower() == "d'" or words[i][:2].lower() == "l'"): #add qu'??	
						words[i] = words[i][2:] #remove them
				
				#remove determiners
				if (words[i].lower() in determiners) and (i == 0 or i == (len(words) -1)):
					words[i] = ""
				
				#if find leftover tags from nounchunker, delete
				if ('<' in words[i]) or ('>' in words[i]):
					words[i] = ""
				
				if ('œ' in words[i]):
					words[i] = words[i].replace('œ', 'oe')
					
			#print("words split by space:", words)
			#print("after dets, oe and tags:", words)
			term = " ".join(words)
			words = term.rstrip().split(" ")
			#print("new term:", term)

			#separate words from apostrophe
			if "'" in term:
				split_term = term.split("'")
				split_term[0] = split_term[0] + "'"
				term = ' '.join(split_term)
				#print("term w separated apostrophe:",term)

			term = " ".join(words)
			term = term.rstrip()
			words = term.split(" ")
			#print("new term:", term)
			#eliminate if
			
			#one char long
			if (len(words) == 1 and len(words[0]) == 1):
				#rejected.write(term+"\n")
				term = ""
				keep = False
				continue
			
			#if ends in common list abrev
			if words[-1].strip().lower() in endings:
				#rejected.write(term+"\n")
				term = ""
				keep = False
				continue				
			
			#if contains words from stoplist of common article section subheadings
			for word in words:
				if word.strip().lower() in articles_sw:
					#rejected.write(term+"\n")
					term = ""
					keep = False
					continue
			
			#if matches from list of extensions
			for ext in extensions:
				if ext in term:
					#rejected.write(term+"\n")
					term = ""
					keep = False

			#if matches a name
			for word in words:
				if term_dict_check(word.strip(),person_name_dict_fr):
					#rejected.write(term+"\n")
					term = ""
					keep = False
					continue
											
			#also remove structure: initial, dot, and word not in dict
			if len(words) == 2:
				if words[0].endswith("."):

					if term_dict_check(words[1].strip().lower(),general_dict_fr):
						#rejected.write(term+"\n")
						term = ""
						keep = False
						continue
			
			#if not eliminated, keep if satisfies at least one criterion
			#keep = False
			if term == "":
				continue

			term = " ".join(words)
			term = term.strip()
			words = term.split(" ")
			#print("new term:", term)

			#multi-word terms: contains at least two common nominalizations
			nomCount = 0
			
			if len(words) > 1:
				for word in words:
					if term_dict_check(word.strip().lower(),nom_map_dict_fr):
						nomCount += 1
				if nomCount < 2:
					#rejected.write(term+" (for less than 2 nominalizations) \n")
					term = ""
					keep = False
					continue
			
			else: #for single-word terms, keep in-vocab nominalizations of at least 13 chars
				if term_dict_check(words[0].strip(),nom_map_dict_fr):
					if len(words[0]) < 13:
						#rejected.write(term+" (for single word nom under 13 chars)\n")
						term = ""
						keep = False
						continue
				

			#keep if contains at least one OOV word, not found in general dict
			OOV = 0
			for word in words:
				if not term_dict_check(word.strip().lower(),general_dict_fr):
					#print(word, " is not in general dict")
					OOV += 1
			if OOV == 0:
				#rejected.write(term+" (for no OOV terms)\n")
				term = ""
				keep = False
				continue
			else:
				keep = True		 						
			
			 

			#look at potential term as a whole	
			term = " ".join(words)
			term = term.strip()
			#print("final term:", term)
			
			if (not term == "") and keep:
				stage1_out.write(term+"\n")



if __name__ == '__main__': sys.exit(main(sys.argv))
