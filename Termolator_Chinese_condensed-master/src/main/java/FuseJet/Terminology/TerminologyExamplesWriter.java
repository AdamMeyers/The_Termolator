package FuseJet.Terminology;

import FuseJet.Utils.FuseUtils;
import org.apache.lucene.analysis.de.GermanStemmer;

import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * User: yhe
 * Date: 10/6/12
 * Time: 4:11 PM
 */
public class TerminologyExamplesWriter {
    private boolean toUpper = false;
    private boolean concatSent = false;
    private List<String> posFileList;
    private int termSize;
    private int exampleSize;

    public void setWindowSize(int windowSize) {
        this.windowSize = windowSize;
    }

    private int windowSize = 4;

    public TerminologyExamplesWriter(List<String> posFileList, int termSize, int exampleSize, boolean toUpper, boolean concatSent) {
        this.toUpper = toUpper;
        this.concatSent = concatSent;
        this.posFileList = posFileList;
        this.termSize = termSize;
        this.exampleSize = exampleSize;
    }

    private boolean useDEStemmer = false;

    public void setUseDEStemmer(boolean useDEStemmer) {
        this.useDEStemmer = useDEStemmer;
    }

    private PublicGermanStemmer stemmer = new PublicGermanStemmer();
    private Set<String> usedStems = new HashSet<String>();

    public void write(List<Term> termList, String outputFileName) {
        System.err.println("[Info] Starting to write results: Use stemmer:"+useDEStemmer + " Context Window Size:" + windowSize);

        PrintWriter w;
        try {
            w = new PrintWriter(outputFileName);
        } catch (Exception e) {
            System.err.println("Unable to open file in TerminlogyExamplesWriter:" + outputFileName);
            e.printStackTrace();
            return;
        }

        // Load sentences
        List<List<String>> sentenceCollection = new ArrayList<List<String>>();
        for (String fileName : posFileList) {
            List<String> sentences = FuseUtils.readSentencesFromPOSFileWithStartEnd(fileName);
            if (sentences != null)
                sentenceCollection.add(sentences);
        }

        // Search Term
        int termCount = 0;
        for (Term term : termList) {
            Set<String> usedExample = new HashSet<String>();
            Set<String> usedContext = new HashSet<String>();
            if (useDEStemmer) {
                if (usedStems.contains(stemmer.doStem(term.word))) {
                    continue;
                }
            }
            String searchTerm;
            if (toUpper) {
                searchTerm = term.word.substring(0, 1).toUpperCase() + term.word.substring(1);
            } else {
                searchTerm = term.word;
            }
            searchTerm = " " + searchTerm.trim() + " ";
            int count = 0;
            boolean duplicateExample = false;
            //int windowSize = 4;
            for (List<String> sentences : sentenceCollection) {
                for (String sentence : sentences) {
                    int termPos = sentence.indexOf(searchTerm);
                    if ((termPos < windowSize) ||
                            (termPos + searchTerm.trim().length() > sentence.length() - windowSize)) {
                        continue;
                    }
                    List<String> contexts = getContext(sentence,
                            termPos,
                            termPos + searchTerm.trim().length(),
                            windowSize);
                    if (usedContext.contains(contexts.get(0)) || usedContext.contains(contexts.get(1))) {
                        usedContext.addAll(contexts);
                        //duplicateExample = true;
                        break;
                    }
                    else {
                        usedContext.addAll(contexts);
                    }
                    if (usedExample.contains(sentence)) {
                        duplicateExample = true;
                        break;
                    } else {
                        usedExample.add(sentence);
                        count += 1;
                        //if (count >= exampleSize) break;
                        break; // go to new document!!!
                    }

                }
                if ((duplicateExample) || (count >= exampleSize)) {
                    break;
                }
            }
            if ((count >= exampleSize) && (!duplicateExample)) {
                String termToPrint = searchTerm.trim();
                if (concatSent) {
                    termToPrint = termToPrint.replaceAll(" ", "");
                }
                w.print(termToPrint);
                for (String ex : usedExample) {
                    w.print(" | " + ex.replaceAll("\n", " ").replaceAll("\r", " ").trim());
                }
                w.println();
                termCount += 1;
                if (useDEStemmer) {
                    usedStems.add(stemmer.doStem(term.word));
                }
            }
            if (termCount >= termSize) {
                break;
            }

        }
        w.close();

    }

    private List<String> getContext(String context, int startId, int endId, int windowSize) {
        List<String> contexts = new ArrayList<String>(2);
        contexts.add(context.substring(startId-windowSize, startId) + " <<<");
        contexts.add(">>> " + context.substring(endId, endId + windowSize));
        return contexts;
    }

}
