This directory contains some test summaries.  I generated these in the
summary directory (1 directory up from here), using the command:

	python3 auto_summary.py

and then answering the questions.  For each run of the system, I chose
a foreground and background topic and then chose to use 500 files and
return a .txt file as output.  The only thing different about these
runs are the choices of foreground and background.

1) For foreground, I chose "osteopenia" and for the background, I
chose "diseases and disorders".  The script did not find enough
articles about "osteopenia" so it expanded the result to include terms
for all "aging associated diseases".  The resulting file is:
"Aging-associated_diseases.summary"  ** running **

2) For foreground, I chose "chocolate" and for background I chose "sugar confectionery".  The resulting output is "Chocolate.summary"

3) I generated two different results for COVID-19 as foreground, but
choosing 2 different possible backgrounds.
	 a) "COVID-19-vs-airborne.summary" is the result of using
	 "airborne diseases" as background.
	 b)  "COVID-19-vs-all.summary" is the result of using "all" of the proposed
	     	backgrounds

4) I chose "printmaking" as the foreground and 2 of the possible
    backgrounds combined.  I chose choices 1,2 which meant a
    combination of "Artistic techniques" and "Visual arts media". The
    resulting file is "Printmaking.summary"

5) For the foreground I chose "seti" and the system clarified some
     choices and I chose "Search for extraterrestrial intelligence".
     For the background, I chose a combination of all the chosen
     backgrounds.  The resulting file is
     "Search_for_extraterrestrial_intelligence.summary"

6) For the foreground I chose "Antioxidant" and for background I
     chose "Biomolecules by physiological function". The result are in
     Antioxidants.summary

7) For the foreground I chose "Category Theory" and for the background
I chose "all. The results are in Category_theory.summary

8) For the oreground, I chose "Ergodic theory" and for the background,
I chose "Dynamical systems." The results are in Ergodic_theory.summary
