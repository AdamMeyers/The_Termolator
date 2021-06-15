This is a minor modification of Sandra Burlaud's program to extract articles from Wikipedia.  This is used as part of the Summary program.

HOW TO RUN:

bash get_wiki_corpus_main.sh [language] [category] [output dir] [recurs: T/F] [max articles]

	1: language: target language/language of desired category. Language should be written in English.
		e.g.: "French", "Spanish"

	2: category: category to be retrieved from Wikipedia in target language, not English. In quotes if several words. ATTENTION: the category name needs to be an EXACT MATCH to the Wikipedia category name (what appears after "Category:" in the URL. For example: for the category COVID-19, https://en.wikipedia.org/wiki/Category:COVID-19, you should 
input "COVID-19" exactly, not "covid-19" or "Covid-19".)
		e.g.: "Physique" for FR, "Physics" for EN

	3: output dir: output directory where the final extracted articles will be placed

	4: recurs: TRUE if want to recursively go into all found subcategories and retrieve articles there
	       	FALSE if only want to retrieve articles in the stated category (no recursion)
	
	if 4 = TRUE, specify 5 (or set 5 to FALSE)

	5: max articles: max number of articles to retrieve. Will retrieve them starting from the "root" category (or FALSE)

EXAMPLE:
	bash get_wiki_corpus_main.sh french "Traitement en maladie infectieuse" output_maladie true 2000

FILES GENERATED:
	- dir [output dir]/: all extracted articles 
	- wget_logfile: log file for wget command
