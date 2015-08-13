I. Files

A. README-FILTER-TERMS.txt:   this file

B. Python Files needed: 
   abbreviate4.py
   add_citations3.py
   find_patent_topic_terms3.py
   get_abbreviation_dict_patent.py
   get_morphological_and_abbreviation_variations.py
   nyu_utilities.py
   run_make_term_dict.py
C. Dictionary files needed:
   NOMLIST.dict 
   POS.dict
   location-lisp2-ugly.dict
   nom_map.dict 
   noun-morph-2000.dict
   out_adjectives.dict 
   out_ing.dict 
   person_name_list.dict 
   time_names.dict
   verb-morph-2000.dict

II. Abbreviation dictionaries: 2 abbreviations dictionaries are
needed: one mapping abbreviations to full terms and the other one
doing the reverse.  It is possible to create abbreviation dictionaries
tuned to a particular domains or, alternatively, default abbreviation
dictionaries are provided which can be used instead.

Default Dictionaries:

bio-cs-abbrev-full.dict -- maps abbreviations to full forms based on files in computer science and biology
bio-cs-full-abbrev.dict -- maps from full forms to abbreviations in these domains

To create tuned abbreviation dictionaries, follow these steps:

1. Create a file called txt_fact.list
   -- each line should be of the form XYZ.txt;XYZ.fact
      where XYZ.txt is a txt file and XYZ.fact is the corresponding fact file
2. run the program as follows:
   
   get_abbreviation_dict_patent.py txt_fact.list Patent_full_abbrev.dict Patent_abbrev_full.dict

   Patent_full_abbrev.dict is the name of the dictionary you are creating for mapping full forms to abbreviations
   Patent_abbrev_full.dict is the name of the dictionary you are creating to map abbreviations to full forms

III. Filter the output of the terminology extractor.

Notice that the following shell command has 7 arguments:

run_make_term_dict.py TERM_LIST OUTPUT.dict OUTPUT.rejects ABBREV_FULL.dict FULL_ABBREV.dict CUTOFF TRUE_OR_FALSE

TERM_LIST -- is the file output from the terminology program. There
are 2 possible formats. The version 2 format puts each form of a term
on its own line, whereas the version 3 format groups alternative forms
together. For example, the strings "stem cell" and "stem cells" would
be on the same line in version 3, but on separate lines in version 2.

OUTPUT.dict -- these are the entries that we are recommending keeping
OUTPUT.rejects -- these are the entries that we are recommending discarding
ABBREV_FULL.dict -- this is the input dictionary file that maps abbreviations to full forms
FULL_ABBREV.dict -- this is the input dictionary file that maps full forms to abbreviations
CUTOFF -- This is a user selected cutoff. It is a decimal number
          between 0 and 1 indicating, the portion of the list that you
          are keeping as valid terms. Only this portion of TERM_LIST
          is considered for inclusion in either of the output
          files. For example, if a cutoff of .5 is chosen, than the
          combined number of terms in both output files together will
          add up to about 50% of the number of input terms.
TRUE_OR_FALSE -- Mark his as "TRUE" if TERM_LIST is in the version 2 format

IV. Explaining the output. Each line of the OUTPUT.dict and
OUTPUT.rejects file consists of the following fields, separated by
tabs.

In OUTPUT.dict, the fields are: TERM, SIGNIFICANT_TERM, RuleName, Rating
TERM is the term in question
SIGNIFICANT_TERM marks this term as one of the ones we are keeping
RuleName is the rule used to make this determination
Rating is a Good, Medium, or Bad rating

In Output.rejects, the fields are: TERM, RuleName, PS, Rating

The TERM, RuleName and Rating fields are defined as above. 

The PS field is either an approximation of the phrase structure of
that term or the word False (this is useful for understanding how the
system works).

Inclusion in OUTPUT.dict is based on both the rankings and which rule
fires.  So for some rules, Good, Medium and Bad are all kept.  For
others, only Good and Medium, etc. Some of this is hard-coded so that a
particular rule is always Good or Bad, etc. Nevertheless, the entries
in OUTPUT.dict tend to be mostly "Good" and the entries in
OUTPUT.rejects tend to be mostly "Bad".  Furthermore, entries that are
ranked near the top are given special treatment and are more likely to
be kept even if a rule fires that typically would cause a term to be
rejected.

V. Setting the cutoff. We are not currently sure which cutoff to
use. We have experimented with .1, which seems to be really really
safe for finding reliable terms. The results of setting the cutoff to
.5 don't seem terrible. Towards the end, they are imperfect, but there
are still some valid ones. Our suspicion is that the filtering may
allow us to use a larger portion of the list than we could use
otherwise.
