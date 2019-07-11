package Jet.CRF.Util;

import AceJet.Ace;
import AceJet.AceDocument;
import Jet.Lex.Lexicon;
import Jet.Lex.Tokenizer;
import Jet.Lisp.FeatureSet;
import Jet.Tipster.Annotation;
import Jet.Tipster.Document;
import Jet.Tipster.ExternalDocument;
import Jet.Tipster.Span;
import Jet.Zoner.SentenceSplitter;

import java.io.*;
import java.util.*;

/**
 * User: yhe
 * Date: 1/30/13
 * Time: 3:01 PM
 */
public class CRFUtils {
    private final static String DEFAULT_EXTERNAL_FILE_FORMAT = "sgml";
    private static Set<String> validTypes = new HashSet<String>(Arrays.asList("organization", "gpe", "person"));

    public static List<String> readLinesToList(String filename) throws IOException {
        List<String> result = new ArrayList<String>();
        BufferedReader br = new BufferedReader(new FileReader(filename));
        String strLine;
        while ((strLine = br.readLine()) != null) {
            result.add(strLine);
        }
        br.close();
        return result;
    }

    public static void writeBIOFile(Document doc, String fileName) throws IOException {
        PrintWriter pw = new PrintWriter(new FileWriter(fileName));
        List<Annotation> sentences = doc.annotationsOfType("paragraph");
        Annotation.sortByStartPosition(sentences);
        for (Annotation line : sentences) {
            Span span = line.span();
            List<Annotation> tokens = doc.annotationsOfType("token", span);
            Annotation.sortByStartPosition(tokens);
            for (Annotation token : tokens) {
                String label = (String) token.get("BIO_TAG");
                if (label == null) {
                    label = "O";
                }
                pw.println(CRFUtils.trimWhitespace(doc.normalizedText(token.span())) + "\t"
                        + label.replaceFirst("L-", "I-"));
            }
            pw.println();
        }
        pw.close();
    }

    public static boolean isCrossed(Annotation a1, Annotation a2) {
        return ((a1.start() <= a2.start() && a1.end() > a2.start()) ||
                (a1.start() < a2.end() && a1.end() >= a2.end()));
    }

    public static void filterENAMEXType(Document doc) {
        Vector<Annotation> enamexes = doc.annotationsOfType("ENAMEX");
        if (enamexes != null) {
            for (Annotation enamex : enamexes) {
                if (enamex.get("TYPE") == null) doc.removeAnnotation(enamex);
                if (!validTypes.contains(enamex.get("TYPE").toString().trim().toLowerCase())) {
                    doc.removeAnnotation(enamex);
                }
            }
        }
    }

    public static void upperCaseAnnotations(Document doc, String[] types) {
        if (types == null) return;
        for (String type : types) {
            List<Annotation> anns = doc.annotationsOfType(type);
            if (anns == null) continue;
            for (Annotation ann : anns) {
                doc.removeAnnotation(ann);
                Annotation newAnn = new Annotation(type.toUpperCase(), ann.span(), ann.attributes());
                doc.addAnnotation(newAnn);
            }
        }
    }

    public static Document openJetAnnotationDocument(String fileName) {
        try {
            String[] parts = fileName.split(";");
            //String[] parts;
            String textFile = parts[0];
            String annFile = parts[1];
            String text = readFileAsString(textFile);
            Document doc = new Document();
            doc.setText(text);
            String line;
            BufferedReader br = new BufferedReader(new FileReader(annFile));
            while ((line = br.readLine()) != null) {
                parts = line.split("\\|\\|\\|");
                String type = parts[0];
                int start = Integer.valueOf(parts[1].substring("START:".length(), parts[1].length()));
                int end = Integer.valueOf(parts[2].substring("END:".length(), parts[2].length()));
                FeatureSet fs = new FeatureSet();
                for (int i = 3; i < parts.length; i++) {
                    String[] featureValue = parts[i].trim().split(":");
                    fs.put(featureValue[0], featureValue[1]);
                }
                Annotation ann = new Annotation(type, new Span(start, end), fs);
                doc.addAnnotation(ann);
            }

            splitTokenizeLexicon(doc);
            doc.stretchAll();
            if (Ace.allLowerCase(doc)) {
                doc.addAnnotation(new Annotation("ALLLOWER", new Span(0, 0), new FeatureSet()));
            }
            doc.addAnnotation(new Annotation("CACHE", new Span(0, 0), new FeatureSet("CACHE", new HashMap<String, String>())));
            return doc;
        } catch (Exception e) {
            System.err.println("Error reading text and Jet annotation files: " + fileName);
            e.printStackTrace();
        }
        return null;
    }

    private static void splitTokenizeLexicon(Document doc) {
        Vector<Annotation> textSegments = doc.annotationsOfType("TEXT");
        if (textSegments == null) {
            doc.addAnnotation(new Annotation("TEXT", doc.fullSpan(), new FeatureSet()));
        }
        textSegments = doc.annotationsOfType("TEXT");
        for (Annotation ann : textSegments) {
            Span textSpan = ann.span();
            // check document case
            Ace.monocase = Ace.allLowerCase(doc);
            // System.out.println (">>> Monocase is " + Ace.monocase);
            // split into sentences
            SentenceSplitter.split(doc, textSpan);
        }
        Vector<Annotation> sentences = doc.annotationsOfType("sentence");
        if (sentences == null) return;
        for (Annotation sentence : sentences) {
            Span sentenceSpan = sentence.span();
            Tokenizer.tokenize(doc, sentenceSpan);
            Lexicon.annotateWithDefinitions(doc,
                    sentenceSpan.start(),
                    sentenceSpan.end());
            // annotator.trainOnSpan(doc, sentenceSpan);
        }
    }

    /**
     * use the annotations on Span 'span' of Document 'doc' to train the HMM.
     */
    public static Document openExternalDocument(String fileName) {
        ExternalDocument doc = new ExternalDocument(DEFAULT_EXTERNAL_FILE_FORMAT, fileName);
        doc.setAllTags(true);
        boolean isOpen = doc.open();
        if (!isOpen) {
            return null;
        }
        doc.stretchAll();
        splitTokenizeLexicon(doc);
        return doc;
    }

    public static Document annotateDocumentWithLexicon(Document doc) {
        Vector<Annotation> sentences = doc.annotationsOfType("sentence");
        if (sentences == null) return doc;
        for (Annotation sentence : sentences) {
            Span sentenceSpan = sentence.span();
            Lexicon.annotateWithDefinitions(doc,
                    sentenceSpan.start(),
                    sentenceSpan.end());
            // annotator.trainOnSpan(doc, sentenceSpan);
        }
        return doc;
    }

    public static void writeSGMLDocument(Document doc, String fileName, String[] types) throws IOException {
        PrintWriter w = new PrintWriter(new FileWriter(fileName));
        w.write(doc.writeSGML(types, 0, doc.length()).toString());
        w.close();
    }

    public static void dropENAMEX(Document doc) {
        Vector<Annotation> annotations = doc.annotationsOfType("ENAMEX");
        if (annotations == null) return;
        for (Annotation ann : annotations) {
            doc.removeAnnotation(ann);
        }
    }

    public static void dropByType(Document doc, String type) {
        Vector<Annotation> annotations = doc.annotationsOfType(type);
        if (annotations == null) return;
        for (Annotation ann : annotations) {
            doc.removeAnnotation(ann);
        }
    }

    public static void writeBAECitationFacts(Document doc, String fileName) {
        System.err.print (" Writing: " + fileName + " ");
        List<Annotation> citations = doc.annotationsOfType("CITATION");
        try {
            PrintWriter pw = new PrintWriter(new FileWriter(fileName));
            if (citations != null) {
                for (Annotation citation : citations) {
                    pw.println(String.format("CITATION START=%d END=%d",
                            citation.start(),
                            citation.end()));
                }
            }
            pw.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void writeJetAnnotationDocument(Document doc, String fileName) {
        PrintWriter wTxt;
        PrintWriter wAnn;
        try {
            wTxt = new PrintWriter(new FileWriter(fileName));
            wAnn = new PrintWriter(new FileWriter(fileName + ".jet_annotations"));
            wTxt.write(doc.text());
            Vector<Annotation> enamexs = doc.annotationsOfType("ENAMEX");
            if (enamexs != null) {
                for (Annotation enamex : enamexs) {
                    String enamexStr = enamex.get("TYPE") == null ?
                            (String) enamex.get("type") : (String) enamex.get("TYPE");
                    wAnn.println(String.format("ENAMEX|||START:%d|||END:%d|||TYPE:%s",
                            enamex.start(),
                            enamex.end(),
                            enamexStr));
                }
            }
            Vector<Annotation> citations = doc.annotationsOfType("CITATION");
            if (citations != null) {
                for (Annotation citation : citations) {
                    wAnn.println(String.format("CITATION|||START:%d|||END:%d|||TYPE:CITATION",
                            citation.start(),
                            citation.end()));
                }
            }

            Vector<Annotation> citationChunks = doc.annotationsOfType("CITATION_CHUNK");
            if (citationChunks != null) {
                for (Annotation citation : citationChunks) {
                    wAnn.println(String.format("CITATION_CHUNK|||START:%d|||END:%d|||TYPE:%s",
                            citation.start(),
                            citation.end(),
                            citation.get("TYPE")));
                }
            }
            wTxt.close();
            wAnn.close();
        } catch (IOException e) {
            System.err.println("Error writing files: " + fileName);
            e.printStackTrace();
        }
    }


    public static void writeEnamexBIO(Document doc, String outputFileName) {
        PrintWriter w = null;
        String text = doc.text();
        try {
            w = new PrintWriter(new File(outputFileName));
        } catch (FileNotFoundException e) {
            System.err.println("Error opening output file: " + outputFileName);
            return;
        }
        Vector<Annotation> sentences = doc.annotationsOfType("sentence");
        if (sentences == null) {
            w.close();
            return;
        }
        for (Annotation sentence : sentences) {
            Vector<Annotation> tokens = doc.annotationsOfType("token", sentence.span());
            if (tokens != null) {
                int tagStart = -1;
                int tagEnd = -1;
                String chunk = "O";
                String type = "";
                for (Annotation token : tokens) {
                    if (token.start() > tagEnd) {
                        Vector<Annotation> enamexAnns = doc.annotationsAt(token.start(), "ENAMEX");
                        if (enamexAnns != null) {
                            type = (String) enamexAnns.get(0).get("type");
                            if (type == null)
                                type = (String) enamexAnns.get(0).get("TYPE");
                            if (type != null) {
                                tagStart = enamexAnns.get(0).start();
                                tagEnd = enamexAnns.get(0).end();
                                type = type.trim().toUpperCase();
                            }
                        }
                    }
                    if (tagStart == token.start()) {
                        chunk = "B-" + type;
                    } else {
                        if ((tagStart < token.start()) && (tagEnd >= token.end())) {
                            chunk = "I-" + type;
                        } else {
                            chunk = "O";
                        }
                    }
                    String word = text.substring(token.start(), token.end()).trim();
                    w.println(String.format("%s\t%s\t%s",
                            word,
                            word,
                            chunk));
                }
            }
            w.println();
        }
        w.close();
    }

    public static String[] splitAtWS(String s) {
        if (s == null) return null;
        StringTokenizer st = new StringTokenizer(s);
        int length = st.countTokens();
        String[] splitS = new String[length];
        for (int i = 0; i < length; i++)
            splitS[i] = st.nextToken();
        return splitS;
    }

    public static Set<String> readLinesToSet(String filename) throws IOException {
        Set<String> result = new HashSet<String>();
        BufferedReader br = new BufferedReader(new FileReader(filename));
        String strLine;
        while ((strLine = br.readLine()) != null) {
            result.add(strLine);
        }
        br.close();
        return result;
    }

    public static String[] readLines(String filename) throws IOException {
        List<String> result = new ArrayList<String>();
        BufferedReader br = new BufferedReader(new FileReader(filename));
        String strLine;
        while ((strLine = br.readLine()) != null) {
            result.add(strLine);
        }
        br.close();
        return result.toArray(new String[result.size()]);
    }

    public static String readFileAsString(String filePath) throws IOException {
        StringBuilder fileData = new StringBuilder(1000);
        BufferedReader reader = new BufferedReader(new FileReader(filePath));
        char[] buf = new char[1024];
        int numRead = 0;
        while ((numRead = reader.read(buf)) != -1) {
            fileData.append(buf, 0, numRead);
        }
        reader.close();
        return fileData.toString();
    }

    public static String trimWhitespace(String str) {
        String trimmed = str.trim();
        int start = 0, end = str.length();
        while (start < end && Character.isWhitespace(trimmed.charAt(start))) {
            start++;
        }
        while (start < end && Character.isWhitespace(trimmed.charAt(end - 1))) {
            end--;
        }
        return trimmed.substring(start, end);
    }


}