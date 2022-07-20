import os
path = "" ##os.getenv('TERMOLATOR')

SET_OF_EXCLUDING_TERMS = set()
## LEGISLATION = "/legal_feature/legal_terms_exclusion/unique_legislation_names.txt"
## CASE = "/legal_feature/legal_terms_exclusion/unique_case_names.txt"
CASE = path + "/legal_feature/unique_case_names.txt"

def legal_filter_setup(path):
    global SET_OF_EXCLUDING_TERMS
    ## global LEGISLATION
    global CASE
    # LEGISLATION = path + LEGISLATION
    # with open(LEGISLATION) as f1:
    #     for line in f1:
    #         SET_OF_EXCLUDING_TERMS.add(line.rstrip())
    CASE = path + CASE
    with open(CASE) as f2:
        for line in f2:
            SET_OF_EXCLUDING_TERMS.add(line.rstrip())

def filter_name(lemma, set_of_excluding_terms=SET_OF_EXCLUDING_TERMS):
	terms = lemma.split(" ")
	if terms[-1] == "act":
		return True
	else:
		for excluded_term in set_of_excluding_terms:
			if lemma in excluded_term:
				return True
	return False

def filter_hyphenated_term(lemma):
	return '-' in lemma

def filter_term_with_digits(lemma):
	for c in lemma:
		if c.isdigit():
			return True
	return False
