package FuseJet.Terminology;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * User: yhe
 * Date: 10/11/12
 * Time: 1:32 PM
 */
public class ChineseNPExtractor extends NPExtractor {

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
//        String term = "";
//        for(int i = pos;i<tokens.size();i++){
//            term = term+" "+tokens.get(i).word;
//            if(!tokens.get(i).pos.equals("JJ"))
//                addTermToList(term, terms);
//        }
        String term = "";
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
        List<NounPhrase> nps = parser.NPParse(filename);
        Map<String, Integer> nouns = new HashMap<String, Integer>();
        for (NounPhrase np : nps) {
            List<String> terms = extractPossibleTermsFromNP(np);
            for (String term : terms)
                addTermToMap(term, nouns, 1);
        }
        return nouns;
    }

}
