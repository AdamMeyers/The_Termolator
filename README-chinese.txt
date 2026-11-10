This is the README  for the Chinese version of the Termolator, parts of which 
combines components of the following:

* The English Termolator
* An earlier (original) version of the Chinese Termolator (https://github.com/ivanhe/termolator/) created by Yifan He.
*  A Noun Chunker Generator by Leizhen Shi https://github.com/frank190/NounChunkerGenerator .
* And other work by Yuling Gu and Echo Hong. 

## Usage

Use Bash, Java, and a Python 3 environment with NLTK installed. To run the
bundled XML sample, choose a working directory for the generated files and run:

    bash /path/to/The_Termolator/sample_chinese_documents/run_sample

This uses the dictionary and the 10 foreground and 10 background patents in
sample_chinese_documents. The original sample files stay in place. The working
directory receives sample.out_term_list, sample.term_instance_map and
sample.edited_term_list, as well as the cleaned text and ranking inputs.
TERMOLATOR_JAVA_HEAP can override the tagger heap limit (for example, 4g).

For a custom corpus, run:

    bash /path/to/The_Termolator/run_Termolator_chinese.sh True output foreground background /path/to/The_Termolator False

Argument 1 controls dictionary filtering. Argument 2 is the output prefix.
Arguments 3 and 4 are input directories and argument 5 is the program
directory. Argument 6 defaults to False for XML. Use True for plain text.

The extraction script cleans or copies the input, runs Brandeis segmentation
and POS tagging, produces noun chunks, ranks candidates, and applies Accessor
Variety. It writes output.out_term_list. To map those terms and produce
output.edited_term_list, use:

    bash /path/to/The_Termolator/run_term_map.sh cleaned_foregroundList.txt output.out_term_list output . /path/to/The_Termolator zh

Use the same working directory for both commands and a separate working
directory for each corpus. Chinese mapping pairs source files with chunks by
basename, defaults to foreground_tchunk_list, and accepts a different chunk
list as the seventh argument. The input path prefix (the fourth argument) is
the base for document names in the map. Chinese mapping rebuilds the map on
each invocation.

## Output compatibility

Accessor Variety still uses literal first-field matches and three distinct
contexts on each side. The filter preserves the original punctuation rules,
boundary offsets, and handling of the BOM on the first ranked row.

Chinese mapping consumes cached source matches directly, so the sample does
not create expanded .terms files. It retains one group of matches per
original chunk row and preserves repeated instances, total frequencies,
zero-based inclusive character offsets, ranked order, variants and the
minimum of three distinct documents. Unranked entries can still be used by
the mapper's substring pass. The standalone .terms generator retains its
record layout and sequential IDs.

Run the regression tests from the program directory:

    python3 -m unittest discover -s tests -v

For direct comparisons with the original code, set TERMOLATOR_LEGACY to a
directory containing baseline copies of accessorvariety.py, term_generator.py
and get_term_maps.py. The tests also run with fixed expectations without it.

The Chinese Termolator uses the following files/components that are not used by
the English or the French version:

* accessorvariety.py
* chinese_noun_chunker_generator.py
* remove_xml_chinese.py
* Brandeis-CASIA-LanguageProcesser
* chinese1.txt
* sample_chinese_documents
* run_Termolator_chinese.sh
* README-chinese.txt
