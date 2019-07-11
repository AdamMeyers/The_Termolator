package FuseJet.Lex;

import FuseJet.Models.FuseDocument;
import Jet.Tipster.*;
import java.util.*;
import AceJet.Ace;

/**
 * Created with IntelliJ IDEA.
 * User: yhe
 * Date: 6/10/12
 * Time: 7:36 PM
 * To change this template use File | Settings | File Templates.
 */


/**
 * container for static method for sentence splitting.
 */
public class FuseSentenceSplitter {

    /**
     * abbreviations which never end a sentence.
     */

    static HashSet abbreviations = new HashSet();
    static HashSet monocaseAbbreviations = new HashSet();

    static {// titles
        abbreviations.add("Adm.");
        abbreviations.add("Brig.");
        abbreviations.add("Capt.");
        abbreviations.add("Cmdr.");
        abbreviations.add("Col.");
        abbreviations.add("Dr.");
        abbreviations.add("Gen.");
        abbreviations.add("Gov.");
        abbreviations.add("Lt.");
        abbreviations.add("Maj.");
        abbreviations.add("Messrs.");
        abbreviations.add("Mr.");
        abbreviations.add("Mrs.");
        abbreviations.add("Ms.");
        abbreviations.add("Prof.");
        abbreviations.add("Rep.");
        abbreviations.add("Reps.");
        abbreviations.add("Rev.");
        abbreviations.add("Sen.");
        abbreviations.add("Sens.");
        abbreviations.add("Sgt.");
        abbreviations.add("Sr.");
        abbreviations.add("St.");
        abbreviations.add("U.S.");
        abbreviations.add("U.K.");
        // abbreviated first names
        abbreviations.add("Alex.");
        abbreviations.add("Benj.");
        abbreviations.add("Chas.");

        // other abbreviations
        abbreviations.add("a.k.a.");
        abbreviations.add("c.f.");
        abbreviations.add("i.e.");
        abbreviations.add("vs.");
        abbreviations.add("v.");
        abbreviations.add("e.g.");

        Iterator it = abbreviations.iterator();
        while (it.hasNext())
            monocaseAbbreviations.add(((String) it.next()).toLowerCase());
    }

    /**
     * annotation types whose start and end points are always sentence boundaries.
     */

    static final String[] dividingAnnotations =
            {"POST", "POSTER", "POSTDATE", "SUBJECT", "SPEAKER", "TURN", "P",
                    "dateline", "textBreak", "text", "footnote"};

    /**
     * splits the text in <I>textSpan</I> into sentences, adding <B>sentence</B>
     * annotations to the document.   We split after a period if the following
     * token is capitalized, and the preceding token is not a known
     * not-sentence-ending abbreviation (such as a title) or a single capital
     * letter.
     *
     * Change from original SentenceSplitter - Yifan
     *
     * For Fuse files that are derived from XMLs, all XML element boundaries serve
     * as token delimiters (in addition to WHITESPACE).
     */
    public static void split(FuseDocument doc, Span textSpan) {
        boolean[] separatingIdx = doc.findSeparatingIdx(); // TODO: using separateIdx
        int start = textSpan.start();
        int end = textSpan.end();
        HashSet boundaries = annotationBoundaries(doc, start, end);
        String text = doc.text();
        //  advance 'start' to first non-blank
        while ((start < end) && Character.isWhitespace(text.charAt(start))) start++;
        int posn = start;
//        int tokenCount = 0;
        int sentenceStart = start;
        int sentenceEnd;
        int nextTokenStart;
        String currentToken = null;
        boolean boundaryAfterCurrentToken = false;
        String nextToken;
        boolean startOfSentence = true;
        //  if all blank (or empty span), exit:  no sentence annotations
        if (posn >= end) return;
        while (posn < end) {
            nextTokenStart = posn;
            // advance to next blank
            while ((posn < end) && !Character.isWhitespace(text.charAt(posn)) &&
                    ((nextTokenStart == posn) || !separatingIdx[posn]))
                posn++;
            nextToken = text.substring(nextTokenStart, posn);
//            tokenCount++;
            // advance to next non-blank
            boolean boundaryAfterNextToken = boundaries.contains(new Integer(posn));
            while ((posn < end) && Character.isWhitespace(text.charAt(posn))) {
                posn++;
                boundaryAfterNextToken |= boundaries.contains(new Integer(posn));
            }
            if (boundaryAfterCurrentToken ||
                    isSentenceEnd(currentToken, nextToken, startOfSentence)) {
                    // _ is often used in gene/protein names, so we ignore the dateline case here - Yifan
                    // ||
                    // isDatelineEnd(currentToken, tokenCount ) {
                sentenceEnd = nextTokenStart;
//                boolean isDuplicate = false;
//                if (doc.annotationsAt(sentenceStart, "sentence") != null) {
//                    Vector<Annotation> conflictingAnns = doc.annotationsAt(sentenceStart, "sentence");
//                    for (Annotation ann : conflictingAnns) {
//                        if (ann.end() == sentenceEnd) {
//                            isDuplicate = true;
//                            break;
//                        }
//                    }
//                }

//                if (!isDuplicate) {
                doc.annotate("sentence", new Span(sentenceStart, sentenceEnd), null);
//                }
                // System.out.println ("Sentence from " + sentenceStart + " to " + sentenceEnd);
                sentenceStart = sentenceEnd;
                startOfSentence = true;
            }
            else {
                startOfSentence = false;
            }
            currentToken = nextToken;
            boundaryAfterCurrentToken = boundaryAfterNextToken;
        }
        sentenceEnd = end;
        // if there is text in the textSegment following the last period,
        // record it as an additional sentence
        if (sentenceStart != sentenceEnd) {
//            boolean isDuplicate = false;
//            if (doc.annotationsAt(sentenceStart, "sentence") != null) {
//                Vector<Annotation> conflictingAnns = doc.annotationsAt(sentenceStart, "sentence");
//                for (Annotation ann : conflictingAnns) {
//                    if (ann.end() == sentenceEnd) {
//                        isDuplicate = true;
//                        break;
//                    }
//                }
//            }
            //if (doc.annotationsAt(sentenceStart, "sentence") == null)
//            if (!isDuplicate) {
            doc.annotate("sentence", new Span(sentenceStart, sentenceEnd), null);;
//            }
            // System.out.println ("Sentence from " + sentenceStart + " to " + sentenceEnd);
        }
    }

    /**
     * returns the set of all boundaries (start and end points) of all annotations
     * of a type on list <I>dividingAnnotations</I> between 'start' and 'end'.
     */

    private static HashSet annotationBoundaries(Document doc, int start, int end) {
        HashSet boundaries = new HashSet();
        for (int i = 0; i < dividingAnnotations.length; i++) {
            Vector annotations = doc.annotationsOfType(dividingAnnotations[i]);
            if (annotations == null) continue;
            for (int j = 0; j < annotations.size(); j++) {
                Annotation ann = (Annotation) annotations.get(j);
                Span span = ann.span();
                int annStart = span.start();
                if (annStart >= start && annStart <= end)
                    boundaries.add(new Integer(annStart));
                int annEnd = span.end();
                if (annEnd >= start && annEnd <= end)
                    boundaries.add(new Integer(annEnd));
            }
        }
        return boundaries;
    }


    /**
     * returns true if <I>currentToken</I> is the final token of a sentence.
     * <P> This is a simplified version of the OAK sentence splitter.
     */

    private static boolean isSentenceEnd(String currentToken, String nextToken,
                                         boolean startOfSentence) {
        if (currentToken == null) return false;
        int cTL = currentToken.length();
        // token is a mid-sentence abbreviation (mainly, titles) --> middle of sent
        if (isAbbreviation(currentToken)) return false;
        if (cTL > 1 &&
                in(currentToken.charAt(0), "`'\"([{<") &&
                isAbbreviation(currentToken.substring(1))) return false;
        if (cTL > 2 &&
                ((currentToken.charAt(0) == '\'' && currentToken.charAt(1) == '\'') ||
                        (currentToken.charAt(0) == '`' && currentToken.charAt(1) == '`')) &&
                isAbbreviation(currentToken.substring(2))) return false;
        char currentToken0 = currentToken.charAt(cTL - 1);
        char currentToken1 = (cTL > 1) ? currentToken.charAt(cTL - 2) : ' ';
        char currentToken2 = (cTL > 2) ? currentToken.charAt(cTL - 3) : ' ';
        int nTL = nextToken.length();
        char nextToken0 = nextToken.charAt(0);
        char nextToken1 = (nTL > 1) ? nextToken.charAt(1) : ' ';
        char nextToken2 = (nTL > 2) ? nextToken.charAt(2) : ' ';
        // nextToken does not begin with an upper case,
        //    [`'"([{<] + upper case, `` + upper case, or < -> middle of sent.
        if (!(Character.isUpperCase(nextToken0) ||
                Ace.monocase ||        // << added Oct. 3
                (Character.isUpperCase(nextToken1) &&
                        in(nextToken0, "`'\"([{<")) ||
                (Character.isUpperCase(nextToken2) &&
                        ((nextToken0 == '`' && nextToken1 == '`') ||
                                (nextToken0 == '\'' && nextToken1 == '\''))) ||
                // for ACE, where '_' represents '--'
                nextToken.equals("_") ||
                nextToken0 == '<')) return false;
        // ends with ?, !, [!?.]["'}>)], or [?!.]'' -> end of sentence
        if (currentToken0 == '?' ||
                currentToken0 == '!' ||
                (in(currentToken1, "?!.") && in(currentToken0, "\"'}>)")) ||
                (in(currentToken2, "?!.") && currentToken1 == '\'' && currentToken0 == '\''))
            return true;
        // last char not "." -> middle of sentence
        if (currentToken0 != '.') return false;
        // -- added to handle Q. / A. in news wire ---------
        // Q. or A. at start of sentence --> end of sentence
        // (so 'Q.' or 'A.' is treated as a 1-word sentence)
        if (startOfSentence &&
                (currentToken.equalsIgnoreCase("Q.") ||
                        currentToken.equalsIgnoreCase("A."))) return true;
        // single upper-case alpha + "." -> middle of sentence
        if (cTL == 2 &&
                (Ace.monocase ?
                        Character.isLetter(currentToken1) :
                        Character.isUpperCase(currentToken1))) return false;
        // double initial (X.Y.) -> middle of sentence << added for ACE
        if (cTL == 4 &&
                currentToken2 == '.' &&
                (Ace.monocase ?
                        (Character.isLetter(currentToken1) &&
                                Character.isLetter(currentToken.charAt(0))) :
                        (Character.isUpperCase(currentToken1) &&
                                Character.isUpperCase(currentToken.charAt(0))))) return false;
        // U.S. or U.N. -> middle of sentence
        if (Ace.monocase)
            if (currentToken.equalsIgnoreCase("U.S.") ||
                    currentToken.equalsIgnoreCase("U.N."))
                return false;
            else if (currentToken.equals("U.S.") || currentToken.equals("U.N."))
                return false;
        // (for XML-marked text) next char is < -> end of sentence
        // if (nextToken0 == '<') return true;
        // if next token is enclosed in parens, '(token)' --> middle of sent.
        // [added to handle ticker symbols after names, 3/16/05]
        if (nextToken0 == '(' &&
                (nextToken.endsWith(")") || nextToken.endsWith(").") ||
                        nextToken.endsWith("),")))
            return false;
        return true;
    }

    private static boolean in(char c, String s) {
        return s.indexOf(c) >= 0;
    }

    private static boolean forcesCap(Annotation currentToken, Document doc) {
        if (currentToken == null) return false;
        String word = doc.text(currentToken).trim();
        return (word.equals("\"") || word.equals("'"));
    }

    private static boolean isAbbreviation(String token) {
        if (Ace.monocase)
            return monocaseAbbreviations.contains(token.toLowerCase());
        else
            return abbreviations.contains(token);
    }

    // a '_' within the first 5 characters is treated as the end of a dateline

    private static boolean isDatelineEnd(String currentToken, int tokenCount) {
        return currentToken != null && currentToken.equals("_") && tokenCount <= 5;
    }
}