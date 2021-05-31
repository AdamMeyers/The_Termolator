This is the README for auto.py which allows the Glossary summarization
system to be run by anyone with any topics.

This program provides a front end to choose foreground and background
topics in wikipedia, running termolator and creating terms and a
summary (glossary) based on the wikipedia entries.  An attempt is made
to use Wikipedia's hierarchy of classes to choose a background topic
that is more general than the foreground. Options are offered if your
choices do not match what is available in Wikipedia.

It is run in a more modular manner than the do-it-yourself summary
program provided and allows for glossaries to be more easily and
quickly created. It also mitigates the issue of having to confirm if
two topics are related in Wikipedia's tree structure and if they exist
in Wikipedia's topic list at all.

For running the program:

It is setup so the program is inside of the summary subdirectory under
the TERMOLATOR main directory.  The Python package bs4 (BeautifulSoup)
to be installed.  To run the program, type the following from the command line:

python3 auto_summary.py

(or equivalent).  See the README.txt file under
test-summaries/README.txt for more detailed instructions, with
examples.

Note: If you choose a topic with very few wikipedia files, it is
likely that the system will produce very little output (or no output)
in the resulting summary.  This is because a term is assumed to be
valid if it appears in at least 3 documents.  If there are very few
documents to begin with, there may be no term that reaches this
threshold.
