package FuseJet.Terminology;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

public class GeniaNPParser implements NPParser{


	/**
	 * @extract noun phrases from Genia tagger output.
	 */

	public static void main(String[] args) throws IOException {
		String file = args[0];
//		String file = "/Users/shashaliao/Research/FUSE/" +
//				"test.pos";
		GeniaNPParser extractor = new GeniaNPParser(); 
		List<NounPhrase> nps = extractor.NPParse(file);
		for(NounPhrase np: nps){
			System.err.print("NP: ");
			System.err.println(np.getSequence());
		}
	}

	@Override
	public List<NounPhrase> NPParse(String filename) throws IOException {
		BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(filename), "utf-8"));
		String line;
		List<Word> words = new ArrayList<Word>();
		while((line = reader.readLine()) != null){
			//new line
			if(line.trim().length() < 1){
				continue;
			}
			String[] parts = line.trim().split("\\t");
			if (parts.length > 3) {
				Word word = Word.readGeniaToken(line.trim());
				words.add(word);
			}
			else {
				System.err.println("Skipped line:" + line);
			}
		}
		reader.close();
		List<NounPhrase> nps = NounPhrase.extractNpsFromGenia(words);
		return nps;
	}
}

	class Word{
		String word;
		String pos;
		String chunk;

		Word(String w, String p, String c){
			word = w;
			pos = p;
			chunk = c;
		}

		static Word readGeniaToken(String line){
			String[] tokens = line.split("\t");
			return new Word(tokens[0], tokens[2],tokens[3]);
		}
	}
