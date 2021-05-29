This wikipedia extraction program was written by Sandra Sandra
Burlaud. It is a program enables you to get text documents from
Wikipedia given a topic.  It can be useful for extracting documents
from Wikipedia for a controlled experiment.  Note that the set up for
creating a summary (in the $TERMOLATOR/summary directory) could be
used for a similar purpose. However, this utility allows for more
controlled experiments.

A sample command that extracts a set of 500 text documents from
Wikipedia about the topic of electiricty.  They are put in a directory
named Electricity:

         get_wiki_corpus_recurs.sh English electricity electricity TRUE 3  500

A sample command to extract covid articles
	 get_wiki_corpus_recurs.sh English COVID-19 covid-19 TRUE 4  500
	 
The arguments of the command, in order are:

Argument1: LANGUAGE -- currently, this can be English, French or Chinese

Argument 2: TOPIC -- this must be a topic found in Wikipedia, with a
sufficient number of files placed in that category (some categories
will yield no results). ** Note this program currently works only if
the exact name of the wikipedia category is provided ** For example
COVID-19 in the above search works, but not covid-19 (lowercase).

Argument 3: DIRECTORY_NAME -- this is typically the same as argument 2

Argument 4: TRUE if you want to recursively retrieve  articles
inside all subcategories found under the category, FALSE otherwise.

Argument 5:  Depth of recursion (I suggest 3 or 5).  Some experimentation may be necessary if you do not get desired results.

Argument 6:  Maximum  number of articles to retrieve




