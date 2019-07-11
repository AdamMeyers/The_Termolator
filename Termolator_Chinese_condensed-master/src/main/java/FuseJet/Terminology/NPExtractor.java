package FuseJet.Terminology;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


public class NPExtractor {
	protected NPParser parser;

    public NPExtractor(){
        parser = new GeniaNPParser();
    }

	public NPExtractor(boolean useJet){
		if(useJet){
			//parser = new JetNPParser();
			System.err.println("Error: Current system does not support jet output.");
			System.exit(1);
		}
		else
			parser = new GeniaNPParser();
	}

    public Map<String, Integer> extractNPFromDocument(String filename) throws IOException{
		List<NounPhrase> nps = parser.NPParse(filename);
		Map<String, Integer> nouns = new HashMap<String, Integer>();
		for(NounPhrase np: nps){
			List<String> terms = np.extractPossibleTerms();
			for(String term:terms)
				addTermToMap(term, nouns, 1);
		}
		return nouns;
	}

    public Map<String, Integer> extractNPFromDocumentRelaxed(String filename) throws IOException{
        List<NounPhrase> nps = parser.NPParse(filename);
        Map<String, Integer> nouns = new HashMap<String, Integer>();
        for(NounPhrase np: nps){
            List<String> terms = np.extractPossibleTermsRelaxed();
            for(String term:terms)
                addTermToMap(term, nouns, 1);
        }
        return nouns;
    }

	protected void addTermToMap(String word, Map<String, Integer> map, int freq){
		if(!isWord(word))
			return;
		if(map.containsKey(word))
			freq += map.get(word);
		map.put(word, freq);
	}

	protected boolean isWord(String word){
		if(word.length() < 2)
			return false;
		if(word.contains("&lt") || word.contains("%") || word.contains("/") || word.contains("\\")
				|| word.contains("& lt") || word.contains(")") || word.contains("(")
				|| word.contains(".")||word.contains("+")
				|| word.startsWith("and ") || word.endsWith(" and")||word.contains(" and "))
			return false;
		for(int i=0;i<word.length();i++){
			if(Character.isLetter(word.charAt(i)) && word.charAt(i) != ' ' )
				return true;
		}
		return false;
	} 

	public static void main(String[] args) throws IOException{
		String file = "/Users/shashaliao/Research/FUSE/" +
				"test.pos";
		NPExtractor extractor = new NPExtractor(false); 
		Map<String,Integer> nps = extractor.extractNPFromDocument(file);
		for(String w: nps.keySet()){
			System.err.println(w);
		}
	}


}
