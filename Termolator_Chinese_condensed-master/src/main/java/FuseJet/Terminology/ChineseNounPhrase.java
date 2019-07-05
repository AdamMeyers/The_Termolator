package FuseJet.Terminology;

import java.util.ArrayList;
import java.util.List;

/**
 * User: yhe
 * Date: 10/10/12
 * Time: 12:25 PM
 */
public class ChineseNounPhrase extends NounPhrase {

    @Override
    public List<String> extractPossibleTerms(){
        List<String> terms = new ArrayList<String>();
        int pos = 0;
        while(pos < tokens.size()){
            Word token = tokens.get(pos);
            if(token.pos.equals("JJ") || token.pos.startsWith("NN"))
                break;
            else
                pos++;
        }
        if(pos == tokens.size()){
            return terms;
        }

        String term = "";
        for(int i = pos;i<tokens.size();i++){
            term = term+" "+tokens.get(i).word;
            if(tokens.get(i).pos.equals("JJ") == false)
                addTermToList(term, terms);
        }
        term = "";
        for(int i= tokens.size()-1;i>=pos;i--){
            term = tokens.get(i).word+" "+term;
            addTermToList(term, terms);
        }
        return terms;
    }

}
