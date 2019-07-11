package FuseJet.Terminology;

import java.io.IOException;
import java.util.List;

public interface NPParser {
	
	List<NounPhrase> NPParse(String filename) throws IOException;


}
