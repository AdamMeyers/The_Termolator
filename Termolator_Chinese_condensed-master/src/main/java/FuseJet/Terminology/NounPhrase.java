package FuseJet.Terminology;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class NounPhrase {
	protected List<Word> tokens;

    private String leftToken;

    private String rightToken;

    public String getLeftToken() {
        return leftToken;
    }

    public String getRightToken() {
        return rightToken;
    }

    public NounPhrase() {

    }

	public NounPhrase(List<Word> ts){
		tokens = ts;
	}

    public void setTokens(List<Word> ts) {
        tokens = ts;
    }

    public List<Word> getTokens() {
        return tokens;
    }

	public static List<NounPhrase> extractNpsFromGenia(List<Word> words){
		List<NounPhrase> nps = new ArrayList<NounPhrase>();
		List<Word> np = new ArrayList<Word>();
        String previousWord = "^^^";
        String leftToken = "^^^";
		for(int i=0;i<words.size();i++){
			Word word = words.get(i);
			if(word.chunk.equals("B-NP")){
				if(np.size() > 0){
                    NounPhrase nounPhrase = new NounPhrase(np);
                    nounPhrase.rightToken = word.word;
                    nounPhrase.leftToken = leftToken;
					nps.add(nounPhrase);
				}
				np = new ArrayList<Word>();
                leftToken = previousWord;
				np.add(word);
			}
			else if(word.chunk.equals("I-NP")){
				np.add(word);
			}
			else{
				if(np.size() > 0){
                    NounPhrase nounPhrase = new NounPhrase(np);
                    nounPhrase.rightToken = word.word;
                    nounPhrase.leftToken = leftToken;
					nps.add(nounPhrase);
				}
				np = new ArrayList<Word>();
			}
            previousWord = words.get(i).word;
		}
        if(np.size() > 0){
            NounPhrase nounPhrase = new NounPhrase(np);
            nounPhrase.rightToken = "";
            nounPhrase.leftToken = leftToken;
            nps.add(nounPhrase);
        }
		return nps;

	}


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

    public List<String> extractPossibleTermsRelaxed(){
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
        for(int i= tokens.size()-1;i>=pos;i--){
            term = tokens.get(i).word+" "+term;
            addTermToList(term, terms);
        }
        return terms;
    }

	protected void addTermToList(String term, List<String> terms){
		term  = term.trim().toLowerCase();
		if(terms.contains(term)==false)
			terms.add(term);
	}

	protected String getSequence(){
		StringBuffer buf = new StringBuffer();
		for(int i=0;i<tokens.size();i++){
			buf.append(tokens.get(i).word+" ");
		}
		return buf.toString().trim();
	}

	public static void main(String[] args) throws IOException {
		String file = "/Users/shashaliao/Research/FUSE/" +
				"test.pos";
		GeniaNPParser extractor = new GeniaNPParser(); 
		List<NounPhrase> nps = extractor.NPParse(file);
		for(NounPhrase np: nps){
			System.err.println("=====\n"+np.getSequence());
			List<String> terms = np.extractPossibleTerms();
			for(String term:terms){
				System.err.println(term);
			}
		}
	}
}
