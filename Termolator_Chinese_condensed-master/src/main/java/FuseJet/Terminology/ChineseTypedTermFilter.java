package FuseJet.Terminology;

import FuseJet.Terminology.Models.ChineseTerm;
import FuseJet.Utils.FuseUtils;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * User: yhe
 * Date: 7/15/13
 * Time: 3:38 PM
 */
public class ChineseTypedTermFilter {
    private Set<String> endWordList = new HashSet<String>();
    private Set<String> stopWordList = new HashSet<String>();
    private Set<String> forbiddenWordList = new HashSet<String>();
    private Set<String> forbiddenCharList = new HashSet<String>();
    private int minAV = 3;
    private int minCount = 5;
    private int minDocCount = 3;

    public ChineseTypedTermFilter(String stopWordListName,
                           String endWordListName,
                           String forbiddenCharListName,
                           int stopThreshold,
                           int forbiddenThreshold,
                           int minAV,
                           int minCount,
                           int minDocumentCount) {
        // add forbidden chars!!! 所 祥 图 例 述
//        if (resourceInformation.length != 5) {
//            System.err.println("Chinese tagger initialization error: unable to obtain correct path.");
//            System.exit(-1);
//        }
//        String stopWordListName = resourceInformation[0];
//        String endWordListName = resourceInformation[1];
//        String forbiddenCharListName = resourceInformation[4];
//        int stopThreshold = 0;
//        int forbiddenThreshold = 0;
//        try {
//            stopThreshold = Integer.valueOf(resourceInformation[2]);
//            forbiddenThreshold = Integer.valueOf(resourceInformation[3]);
//        }
//        catch (Exception e) {
//            System.err.println("The third parameter for ChineseTermFilter should be a number");
//            e.printStackTrace();
//            System.exit(-1);
//        }
        try {
            stopWordList = FuseUtils.readWordListWithThreshold(stopWordListName, stopThreshold);
            forbiddenWordList = FuseUtils.readWordListWithThreshold(stopWordListName, forbiddenThreshold);
            endWordList = readLinesToSet(endWordListName);
            forbiddenCharList = readLinesToSet(forbiddenCharListName);
        }
        catch (IOException e) {
            System.err.println("ChineseTermFilter error loading files...");
            e.printStackTrace();
            System.exit(-1);
        }

    }

    public static boolean containsCJKCharacter(String s) {
        char[] chars = s.toCharArray();
        for (char c : chars) {
            if (Character.UnicodeBlock.of(c) == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS) return true;
        }
        return false;
    }

    public static boolean endsWithCJKCharacter(String s) {
        return Character.UnicodeBlock.of(s.charAt(s.length()-1)) ==
                Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS;
    }

    private Set<String> readLinesToSet(String wordListName) throws IOException {
        BufferedReader r = new BufferedReader(new FileReader(wordListName));
        Set<String> result = new HashSet<String>();
        String line;
        while ((line = r.readLine()) != null) {
            result.add(line.trim());

        }
        r.close();
        return result;
    }

    public List<ChineseTerm> filterTerm(List<ChineseTerm> termList) {
        List<ChineseTerm> result = new ArrayList<ChineseTerm>();
        for (ChineseTerm term : termList) {
            if (!containsCJKCharacter(term.getTerm()))
                continue;
            if (!endsWithCJKCharacter(term.getTerm()))
                continue;
            String[] tokens = term.getTerm().split(" ");
            if ((tokens.length > 0 ) && (endWordList.contains(tokens[tokens.length-1]))) {
                continue;
            }
            if (tokens.length > 0 && tokens[0].length() == 1 && !containsCJKCharacter(tokens[0]))
                continue;
            boolean forbidden = false;
            for (String token : tokens) {
                if (forbiddenWordList.contains(token)) {
                    forbidden = true;
                    break;
                }
            }
            if (forbidden) {
                continue;
            }

            String termWithOutSpace = term.getTerm().replaceAll("\\s+", "");
            char[] chars = termWithOutSpace.toCharArray();
            for (char c : chars) {
                if (Character.isDigit(c)) {
                    forbidden = true;
                    break;
                }
                if (c >= 'a' && c <= 'z') {
                    forbidden = true;
                    break;
                }
                if (forbiddenCharList.contains(String.valueOf(c))) {
                    forbidden = true;
                    break;
                }
            }
            if (forbidden) {
                continue;
            }
            if (stopWordList.contains(termWithOutSpace)) {
                continue;
            }
            if (term.getCount() < minCount ||
                term.getDocumentCount() < minDocCount ||
                term.accessorVariety() < minAV) {
                continue;
            }
            result.add(term);
        }
        return result;
    }


}
