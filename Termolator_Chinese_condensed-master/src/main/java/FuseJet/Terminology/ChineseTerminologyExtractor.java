package FuseJet.Terminology;

import FuseJet.Terminology.Models.ChineseTerm;

import java.io.FileReader;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Properties;

/**
 * User: yhe
 * Date: 7/15/13
 * Time: 3:52 PM
 */
public class ChineseTerminologyExtractor {
    private static final boolean DEBUG = false;

    public static void main(String[] args) {
        String stopWordListName;
        String endWordListName;
        String forbiddenCharListName;
        int stopThreshold;
        int forbiddenThreshold;
        int minAV;
        int minCount;
        int minDocumentCount;
        double terminologyThreshold = 0.5;

        try {
            Properties props = new Properties();
            props.load(new FileReader(args[0]));
            stopWordListName = props.getProperty("stopWordListName");
            endWordListName = props.getProperty("endWordListName");
            forbiddenCharListName = props.getProperty("forbiddenCharListName");
            stopThreshold = Integer.valueOf(props.getProperty("stopThreshold"));
            forbiddenThreshold = Integer.valueOf(props.getProperty("forbiddenThreshold"));
            minAV = Integer.valueOf(props.getProperty("minAV"));
            minCount = Integer.valueOf(props.getProperty("minCount"));
            minDocumentCount = Integer.valueOf(props.getProperty("minDocumentCount"));
            terminologyThreshold = Double.valueOf(props.getProperty("terminologyThreshold"));
            ChineseTypedTermFilter filter = new ChineseTypedTermFilter(stopWordListName,
                    endWordListName,
                    forbiddenCharListName,
                    stopThreshold,
                    forbiddenThreshold,
                    minAV,
                    minCount,
                    minDocumentCount);

            AccessorVarietyChineseTermExtractor extractor = new AccessorVarietyChineseTermExtractor();
            System.err.println("Extracting NPs from RDG...");
            List<ChineseTerm> allTermList = extractor.extractNPFromFileList(args[1]);
            System.err.println("Extracting NPs from background set...");
            Map<String, ChineseTerm> negTermMap = extractor.extractNPMapFromFileList(args[2]);
            allTermList = filter.filterTerm(allTermList);
            System.err.println("Update negative set statistics...");
            for (ChineseTerm cterm : allTermList) {
                if (negTermMap.containsKey(cterm.getTerm())) {
                    cterm.updateNegative(negTermMap.get(cterm.getTerm()));
                }
            }
            //terms = filter.filterTerm(terms);
            System.err.println("Sorting...");
            Collections.sort(allTermList, new AccessorVarietyChineseTermExtractor.DRDCComparator());
            for (int i = 0; i < allTermList.size(); i++) {
                if (i > allTermList.size()*terminologyThreshold)
                    break;
                ChineseTerm t = allTermList.get(i);
                if (DEBUG)
                    System.out.println(t);
                else
                    System.out.println(t.getTerm().replaceAll("\\s+", "") + " ||| " + t.getDRDC());
            }
        }
        catch (Exception e) {
            System.err.println("FuseJet.Terminology.ChineseTerminologyExtractor props RDG BackgroundSet");
            e.printStackTrace();
        }

    }

}
