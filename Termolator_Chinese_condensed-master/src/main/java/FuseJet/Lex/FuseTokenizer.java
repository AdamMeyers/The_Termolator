package FuseJet.Lex;

import FuseJet.Models.FuseDocument;
import Jet.Lex.Tokenizer;
import Jet.Lisp.FeatureSet;
import Jet.Tipster.Document;
import Jet.Tipster.Span;
import com.google.common.collect.ImmutableSet;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * This is a reimplementation of the tokenizer in Genia tagger. However, we
 *
 * 1) added recognition of URLs and emails
 *
 * 2) requires that tokens do not conflict with existing FuseDocument Annotations
 */
public class FuseTokenizer {
    private static String lastToken;
    private static HashMap<Integer, Integer> specialTokenEnd;
    private static HashMap<Integer, String> specialTokenType;
    static HashSet suffixes2 = new HashSet();
    static HashSet suffixes3 = new HashSet();

    static private String userNamePatStg = "[a-zA-Z0-9_\\.-]+";
    static private String domainNamePatStg = "([a-zA-Z0-9-]+\\.)+[a-zA-Z0-9]+";
    static private String emailPatStg = userNamePatStg + "( ?\\.\\.\\. ?)?@" + domainNamePatStg;
    static private String pathPatStg = "[a-zA-Z0-9_=\\?/-]+";
    static private String urlPatStg = "https?://" + domainNamePatStg + pathPatStg;
    static private Pattern emailPat = Pattern.compile(emailPatStg);
    static private Pattern urlPat = Pattern.compile(urlPatStg);
    private static final Set<Character> SEPARATE_TOKENS = ImmutableSet.of(
            ',', ';', ':', '@', '#', '$', '%', '&',
            '?', '!', '[', ']', '(', ')', '{', '}', '>', '<', '\'', '/'
            );

    static {
        suffixes2.add("'s");
        suffixes2.add("'S");
        suffixes2.add("'m");
        suffixes2.add("'M");
        suffixes2.add("'d");
        suffixes2.add("'D");

        suffixes3.add("'re");
        suffixes3.add("'ve");
        suffixes3.add("n't");
        suffixes3.add("'ll");
        suffixes3.add("'RE");
        suffixes3.add("'VE");
        suffixes3.add("N'T");
        suffixes3.add("'LL");
    }

    public static void tokenize(FuseDocument doc, Span span, boolean performPatternMatching) {
        findTokens(doc, doc.text(), span.start(), span.end(), performPatternMatching);
    }

    public static void tokenize(FuseDocument doc, Span span) {
        findTokens(doc, doc.text(), span.start(), span.end(), true);
    }

    public static void tokenize(FuseDocument doc, Span span, String text) {
        findTokens(doc, text, span.start(), span.end(), true);
    }

    /**
     * look for predefined patterns for email addresses and URLs, starting at
     * position 'start' of 'text'.  If a match, record the token in
     * specialTokenEnd and specialTokenType.
     */

    private static void findTokensByPattern(Document doc, String text, int start, int end) {
        Matcher emailMatcher = emailPat.matcher(text).region(start, end);
        specialTokenEnd = new HashMap<Integer, Integer>();
        specialTokenType = new HashMap<Integer, String>();
        while (emailMatcher.find()) {
            int tokenStart = emailMatcher.start();
            int tokenEnd = emailMatcher.end();
            specialTokenEnd.put(tokenStart, tokenEnd);
            specialTokenType.put(tokenStart, "email");
        }
        Matcher urlMatcher = urlPat.matcher(text).region(start, end);
        while (urlMatcher.find()) {
            int tokenStart = urlMatcher.start();
            int tokenEnd = urlMatcher.end();
            specialTokenEnd.put(tokenStart, tokenEnd);
            specialTokenType.put(tokenStart, "url");
        }
    }

    public static int skipWSX(String text, int posn, int end) {
        while (posn < end) {
            if (Character.isWhitespace(text.charAt(posn))) {
                posn++;
            } else if (text.charAt(posn) == '<') {
                posn++;
                while (posn < end && text.charAt(posn) != '>')
                    posn++;
                if (posn < end) posn++;
            } else break;
        }
        return posn;
    }

    private static void findTokens(FuseDocument doc, String text, int ic, int end, boolean performPatternMatching) {
        String block;
        int tokenStart;
        boolean firstBlock = true;
        boolean lastBlock;
        lastToken = "";
        if (performPatternMatching) {
            findTokensByPattern(doc, text, ic, end);
        }
        // skip white space preceding first token
        ic = skipWSX(text, ic, end);
        boolean[] separatingIdx = doc.findSeparatingIdx();
        //boolean[] separatingIdx = new boolean[999999];
        while (ic < end) {
            tokenStart = ic;
            Integer tokenEnd = specialTokenEnd.get(ic); // get special token end
            if (tokenEnd != null)
                ic = tokenEnd;
            else
                ic++;
            while ((ic < end) && !Character.isWhitespace(text.charAt(ic)) &&
                    (!separatingIdx[ic])) {
                tokenEnd = specialTokenEnd.get(ic);
                if (tokenEnd != null)
                    ic = tokenEnd;
                else
                    ic++;
            }
            block = text.substring(tokenStart, ic);
            Span blockSpan = new Span(tokenStart, ic);
            blockSpan.setDocument(doc);
            // include whitespace following token
            while ((ic < end) && Character.isWhitespace(text.charAt(ic))) ic++;
            lastBlock = ic >= end;
            //Span span = new Span(tokenStart, ic);
            //span.setDocument(doc);
            Map<Integer, String> tokenStrings = new HashMap<Integer, String>();
            boolean[] newToken = splitIntoTokens(doc, blockSpan, firstBlock, lastBlock, tokenStrings);
            buildTokens(doc, block, newToken, tokenStart, ic, firstBlock, tokenStrings);
            firstBlock = false;
        }
    }

    /**
     * divides a white-space delimited sequence of characters into tokens.
     *
     * @param doc the document
     * @param span  the span
     * @param lastBlock   the previous sequence
     * @return a boolean array whose i-th element is true if the i-th character
     *         of blockString is the beginning of a new token [if blockString has
     *         n characters, this is an n+1 element array, in which the last
     *         element is always true]
     */
    private static boolean[] splitIntoTokens(Document doc, Span span, boolean firstBlock, boolean lastBlock, Map<Integer, String> tokenStrings) {
        String blockString = doc.text(span);
        int blockStart = span.start();
        char[] block = blockString.toCharArray();
        int blockLength = block.length;
        boolean[] newToken = new boolean[blockLength + 1];
        newToken[blockLength] = true;
        // for all SEPARATE_TOKENS, make it a separate token
        for (int i = 0; i < blockLength; i++) {
            char c = block[i];
            if (SEPARATE_TOKENS.contains(c)) {
                newToken[i] = true;
                newToken[i + 1] = true;
            }
        }

        // handle quotation marks properly: for " at beginning of block, or after <{[(,
        // annotate as left double quote ``
        // otherwise, annotate as right double quote ''
        for (int i = 0; i < blockLength; i++) {
            char c = block[i];
            if (c == '"') {
                newToken[i] = true;
                if (i == 0) {
                    tokenStrings.put(i, "``");
                }
                else {
                    if ((i > 0) &&
                            ((block[i - 1] == '<') ||
                             (block[i - 1] == '{') ||
                             (block[i - 1] == '[') ||
                             (block[i - 1] == '(')))   {
                        tokenStrings.put(i, "``");

                    }
                    else {
                        tokenStrings.put(i , "''");
                    }
                }
            }
        }

        // make ``, '', --, and ... single tokens
        for (int i = 0; i < blockLength - 1; i++) {
            char c = block[i];
            if ((c == '`' || c == '\'' || c == '-') && c == block[i + 1]
                    && newToken[i]) {
                newToken[i + 1] = false;
            }
        }
        for (int i = 0; i < blockLength - 2; i++) {
            if (block[i] == '.' && block[i + 1] == '.' &&
                    block[i + 2] == '.' && newToken[i]) {
                newToken[i + 1] = false;
                newToken[i + 2] = false;
            }
        }
        // make comma a separate token unless surrounded by digits
        for (int i = 1; i < blockLength - 2; i++) {
            if (block[i] == ',' && Character.isDigit(block[i - 1]) &&
                    Character.isDigit(block[i + 1])) {
                newToken[i] = false;
                newToken[i + 1] = false;
            }
        }
        // make period a separate token if this is the last block
        // [of a sentence] and the period is final or followed by ["'}>)[]] or ''
        // Note that this may split off the period even if the token is an
        // abbreviation.
        if (lastBlock) {
            if (block[blockLength - 1] == '.') {
                newToken[blockLength - 1] = true;
            }
            else {
                int pos = blockLength - 1;
                while (pos > 0) {
                    char c = block[pos];
                    if (c == '[' || c == ']' || c == ')' || c == '}' || c == '>' ||
                            c == '"' || c == '\'') {
                        pos--; continue;
                    }
                    break;
                }
                if (block[pos] == '.' && !(pos > 0 && block[pos-1] == '.')) {
                    newToken[pos] = true;
                }
            }
        }
        // split off standard 2 and 3-character suffixes ('s, n't, 'll, etc.)
        for (int i = 0; i < blockLength - 2; i++) {
            if (newToken[i + 3] && suffixes3.contains(blockString.substring(i, i + 3))) {
                newToken[i] = true;
                newToken[i + 1] = false;
                newToken[i + 2] = false;
            }
        }
        for (int i = 0; i < blockLength - 1; i++) {
            if (newToken[i + 2] && suffixes2.contains(blockString.substring(i, i + 2))) {
                newToken[i] = true;
                newToken[i + 1] = false;
            }
        }
        // make &...; a single token (probable XML escape sequence)
//        for (int i = 0; i < blockLength - 1; i++) {
//            if (block[i] == '&') {
//                for (int j = i + 1; j < blockLength; j++) {
//                    if (block[j] == ';') {
//                        for (int k = i + 1; k <= j; k++) {
//                            newToken[k] = false;
//                        }
//                    }
//                }
//            }
//        }
        for (int i = 0; i < blockLength; i++) {
            Integer tokenEnd = specialTokenEnd.get(blockStart + i);
            if (tokenEnd != null) {
                newToken[i] = true;
                for (int j = i + 1; j < blockLength && j + blockStart < tokenEnd; j++) {
                    newToken[j] = false;
                }
            }
        }
        return newToken;
    }

    /**
     * adds token Annotations to doc consisting of the tokens within block.
     */

    private static void buildTokens(Document doc, String block, boolean[] newToken,
                                    int offset, int nextBlockStart, boolean firstBlock,
                                    Map<Integer, String> tokenStrings) {
        //System.err.println(block);
        int tokenStart = 0;
        for (int i = 1; i <= block.length(); i++) {
            if (newToken[i]) {
                int tokenEnd = i;
                FeatureSet fs = null;
                // if number, compute value (set value=-1 if not a number)
                int value = 0;
                for (int j = tokenStart; j < tokenEnd; j++) {
                    if (Character.isDigit(block.charAt(j))) {
                        value = (value * 10) + Character.digit(block.charAt(j), 10);
                    } else if (block.charAt(j) == ',' && value > 0) {
                        // skip comma if preceded by non-zero digit
                    } else {
                        value = -1;
                        break;
                    }
                }
                String type = specialTokenType.get(tokenStart + offset);
                if (type != null) {
                    fs = new FeatureSet("type", type);
                } else if (Character.isUpperCase(block.charAt(tokenStart))) {
                    if (firstBlock ||
                            // for ACE
                            lastToken.equals("_") ||
                            lastToken.equals("\"") || lastToken.equals("``") || lastToken.equals("`")) {
                        fs = new FeatureSet("case", "forcedCap");
                    } else {
                        fs = new FeatureSet("case", "cap");
                    }
                } else if (value >= 0) {
                    fs = new FeatureSet("intvalue", value);
                } else {
                    fs = new FeatureSet();
                }
                // create token
                if (tokenStrings.containsKey(tokenStart)) {
                    fs.put("tokenString", tokenStrings.get(tokenStart).trim());
                }
                else {
                    fs.put("tokenString", block.substring(tokenStart, tokenEnd).trim());
                }
                int spanEnd = (tokenEnd == block.length()) ? nextBlockStart : tokenEnd + offset;
                String tokenString = block.substring(tokenStart, tokenEnd);
                if (!fs.get("tokenString").equals("")) {
                    String modifiedTokenString = (String)fs.get("tokenString");
                    modifiedTokenString = modifiedTokenString.replaceAll("\\(","-LRB-");
                    modifiedTokenString = modifiedTokenString.replaceAll("\\)","-RRB-");
                    modifiedTokenString  =modifiedTokenString.replaceAll("\\[", "-LSB-");
                    modifiedTokenString = modifiedTokenString.replaceAll("\\]", "-RSB-");
                    modifiedTokenString = modifiedTokenString.replaceAll("\\{", "-LCB-");
                    modifiedTokenString = modifiedTokenString.replaceAll("\\}", "-RCB-");
                    fs.put("tokenString", modifiedTokenString);
                    recordToken(doc, tokenString, tokenStart + offset, spanEnd, fs);
                }
                tokenStart = tokenEnd;
                lastToken = tokenString;
            }
        }
    }

    private static void recordToken(Document doc, String text,
                                    int start, int end, FeatureSet fs) {
        // System.out.println ("Adding token " + text + fs + " over " + start + "-" + end);

        doc.annotate("token", new Span(start, end), fs);
        if (fs.get("type") != null)
            doc.annotate("ENAMEX", new Span(start, end), new FeatureSet("TYPE", fs.get("type")));

    }

}
