package FuseJet.Terminology;

import FuseJet.Terminology.Models.ChineseTerm;
import junit.framework.TestCase;

import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * User: yhe
 * Date: 7/14/13
 * Time: 4:21 PM
 */
public class AccessorVarietyChineseTermExtractorTest extends TestCase {

    public void testExtractNPFromDocument() throws Exception {
        AccessorVarietyChineseTermExtractor extractor = new AccessorVarietyChineseTermExtractor();
        List<ChineseTerm> terms = extractor.extractNPFromDocument("src/test/data/CN1238058A.chunk.full", 0);
        for (ChineseTerm term: terms) {
            System.out.println(term);
        }
    }
}
