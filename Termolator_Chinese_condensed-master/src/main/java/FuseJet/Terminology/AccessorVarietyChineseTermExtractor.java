package FuseJet.Terminology;

import FuseJet.Terminology.Models.ChineseTerm;
import Jet.CRF.Util.CRFUtils;

import java.io.IOException;
import java.util.*;

/**
 * This class implements Feng et al. 2004, "Accessor Variety Criteria
 * for Chinese Word Extraction". Computational Linguistics 30(1).
 */
public class AccessorVarietyChineseTermExtractor extends ChineseNPExtractor {
    private List<String> extractPossibleTermsFromNP(NounPhrase np) {
        List<String> terms = new ArrayList<String>();
        int pos = 0;
        List<Word> tokens = np.getTokens();

        // skip DT etc. at the beginning of NPs
        while (pos < tokens.size()) {
            Word token = tokens.get(pos);
            if (token.pos.equals("JJ") || token.pos.startsWith("NN"))
                break;
            else
                pos++;
        }
        if (pos == tokens.size()) {
            return terms;
        }

        // build from back
        String term = "";
        for (int i = pos; i < tokens.size(); i++) {
            term = term + " " + tokens.get(i).word;
            if (!tokens.get(i).pos.equals("JJ"))
                addTermToList(term, terms);
        }
        term = "";
        for (int i = tokens.size() - 1; i >= pos; i--) {
            term = tokens.get(i).word + " " + term;
            addTermToList(term, terms);
        }
        return terms;
    }

    private void addTermToList(String term, List<String> terms) {
        term = term.trim().toLowerCase();
        if (!terms.contains(term))
            terms.add(term);
    }

    @Override
    public Map<String, Integer> extractNPFromDocument(String filename) throws IOException {
        return null;
    }

    public List<ChineseTerm> extractNPFromDocument(String filename, int method) throws IOException {
        List<NounPhrase> nps = parser.NPParse(filename);
        Map<String, ChineseTerm> chineseTerms = new HashMap<String, ChineseTerm>();
        for (NounPhrase np : nps) {
            int pos = 0;
            List<Word> tokens = np.getTokens();

            // skip DT etc. at the beginning of NPs
            while (pos < tokens.size()) {
                Word token = tokens.get(pos);
                if (token.pos.startsWith("NN"))
                    break;
                else
                    pos++;
            }
            if (pos == tokens.size()) {
                continue;
            }

            // build from back
            String term = "";
            for (int i = pos; i < tokens.size() - 1; i++) {
                if (term.length() == 0) {
                    term = tokens.get(i).word;
                }
                else {
                    term = term + " " + tokens.get(i).word;
                }
                if (!tokens.get(i).pos.equals("JJ")) {
                    // addTermToList(term, terms);
                    if (!chineseTerms.containsKey(term)) {
                        chineseTerms.put(term, new ChineseTerm(term));
                    }
                    ChineseTerm chineseTerm = chineseTerms.get(term);
                    chineseTerm.addToLeftContexts(np.getLeftToken());
                    chineseTerm.addToRightContexts(i < tokens.size() - 1 ? tokens.get(i + 1).word : np.getRightToken());
                    chineseTerm.occur();
                }
            }
            term = "";
            for (int i = tokens.size() - 1; i >= pos; i--) {
                if (!tokens.get(tokens.size() - 1).pos.startsWith("NN")) break;
                if (term.length() == 0) {
                    term = tokens.get(i).word;
                }
                else {
                    term = tokens.get(i).word + " " + term;
                }
                if (!tokens.get(i).pos.equals("JJ")) {
                    if (!chineseTerms.containsKey(term)) {
                        chineseTerms.put(term, new ChineseTerm(term));
                    }
                    ChineseTerm chineseTerm = chineseTerms.get(term);
                    chineseTerm.addToLeftContexts(i > 1 ? tokens.get(i - 1).word : np.getLeftToken());
                    chineseTerm.addToRightContexts(np.getRightToken());
                    chineseTerm.occur();
                }
            }
        }
        return new ArrayList<ChineseTerm>(chineseTerms.values());
    }


    public List<ChineseTerm> extractNPFromFileList(String fileList) throws IOException {
        Map<String, ChineseTerm> allTerms = extractNPMapFromFileList(fileList);

//        Map<String, ChineseTerm> allTerms = new HashMap<String, ChineseTerm>();
//        String[] fileNames = CRFUtils.readLines(fileList);
//        AccessorVarietyChineseTermExtractor extractor = new AccessorVarietyChineseTermExtractor();
//        for (String fileName : fileNames) {
//            //System.err.println("Processing:" + fileName);
//            List<ChineseTerm> terms = extractNPFromDocument(fileName, 0);
//            for (ChineseTerm term : terms) {
//                if (!allTerms.containsKey(term.getTerm())) {
//                    allTerms.put(term.getTerm(), new ChineseTerm(term.getTerm()));
//                }
//                ChineseTerm t = allTerms.get(term.getTerm());
//                t.add(term);
//            }
//        }
        return new ArrayList<ChineseTerm>(allTerms.values());
    }

    public Map<String, ChineseTerm> extractNPMapFromFileList(String fileList) throws IOException {
        Map<String, ChineseTerm> allTerms = new TreeMap<String, ChineseTerm>();
        String[] fileNames = CRFUtils.readLines(fileList);
        AccessorVarietyChineseTermExtractor extractor = new AccessorVarietyChineseTermExtractor();
        for (String fileName : fileNames) {
            //System.err.println("Processing:" + fileName);
            List<ChineseTerm> terms = extractNPFromDocument(fileName, 0);
            for (ChineseTerm term : terms) {
                if (!allTerms.containsKey(term.getTerm())) {
                    allTerms.put(term.getTerm(), new ChineseTerm(term.getTerm()));
                }
                ChineseTerm t = allTerms.get(term.getTerm());
                t.add(term);
            }
        }
        return allTerms;
    }

    public static void main(String[] args) {
        try {
            Map<String, ChineseTerm> allTerms = new HashMap<String, ChineseTerm>();
            String[] fileNames = CRFUtils.readLines(args[0]);
            AccessorVarietyChineseTermExtractor extractor = new AccessorVarietyChineseTermExtractor();
//            for (String fileName : fileNames) {
//                System.err.println("Processing:" + fileName);
//                List<ChineseTerm> terms = extractor.extractNPFromDocument(fileName, 0);
//                for (ChineseTerm term : terms) {
//                    if (!allTerms.containsKey(term.getTerm())) {
//                        allTerms.put(term.getTerm(), new ChineseTerm(term.getTerm()));
//                    }
//                    ChineseTerm t = allTerms.get(term.getTerm());
//                    t.add(term);
//                }
//            }
//            List<ChineseTerm> allTermList = new ArrayList<ChineseTerm>(allTerms.values());
            List<ChineseTerm> allTermList = extractor.extractNPFromFileList(args[1]);



            System.err.println("Sorting...");
            Collections.sort(allTermList, new DRDCComparator());
            Collections.reverse(allTermList);
            for (ChineseTerm t : allTermList) {
                if (t.accessorVariety() < 3) break;
                System.out.println(t);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static class AVComparator implements Comparator<ChineseTerm> {

        public int compare(ChineseTerm chineseTerm, ChineseTerm chineseTerm1) {
            return chineseTerm.accessorVariety() - chineseTerm1.accessorVariety();
        }

        @Override
        public boolean equals(Object o) {
            return false;
        }
    }

    public static class DRDCComparator implements Comparator<ChineseTerm> {

        public int compare(ChineseTerm chineseTerm0, ChineseTerm chineseTerm1) {
            if (chineseTerm1.getDRDC() - chineseTerm0.getDRDC() < 0) return -1;
            if (chineseTerm1.getDRDC() - chineseTerm0.getDRDC() > 0) return 1;
            return 0;
        }
    }

}
