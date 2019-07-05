package FuseJet.Terminology;

import junit.framework.TestCase;

import java.util.Map;

/**
 * Created with IntelliJ IDEA.
 * User: yhe
 * Date: 7/13/13
 * Time: 11:56 PM
 * To change this template use File | Settings | File Templates.
 */
public class ChineseNPExtractorTest extends TestCase {
    public void testExtractNPFromDocument() throws Exception {
        ChineseNPExtractor extractor = new ChineseNPExtractor();
        Map<String, Integer> nps = extractor.extractNPFromDocument("src/test/data/CN1238058A.chunk.full");
        for (String k : nps.keySet()) {
            System.out.println(k + ":" + nps.get(k));
        }
    }
}
