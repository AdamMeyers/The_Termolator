package FuseJet.Terminology;

import org.apache.lucene.analysis.de.GermanStemmer;

/**
 * User: yhe
 * Date: 11/2/12
 * Time: 4:43 PM
 */
public class PublicGermanStemmer extends GermanStemmer {
    public String doStem(String s) {
        return stem(s);
    }
}
