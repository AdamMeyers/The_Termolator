package FuseJet.Terminology;

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
 * Date: 10/2/12
 * Time: 4:20 PM
 */
public class ChineseTermFilter implements TermFilter {

    Set<String> endWordList = new HashSet<String>();
    Set<String> stopWordList = new HashSet<String>();
    Set<String> forbiddenWordList = new HashSet<String>();
    Set<String> forbiddenCharList = new HashSet<String>();

    @Override
    public void initialize(String[] resourceInformation) {
        // add forbidden chars!!! 所 祥 图 例 述
        if (resourceInformation.length != 5) {
            System.err.println("Chinese tagger initialization error: unable to obtain correct path.");
            System.exit(-1);
        }
        String stopWordListName = resourceInformation[0];
        String endWordListName = resourceInformation[1];
        String forbiddenCharListName = resourceInformation[4];
        int stopThreshold = 0;
        int forbiddenThreshold = 0;
        try {
            stopThreshold = Integer.valueOf(resourceInformation[2]);
            forbiddenThreshold = Integer.valueOf(resourceInformation[3]);
        } catch (Exception e) {
            System.err.println("The third parameter for ChineseTermFilter should be a number");
            e.printStackTrace();
            System.exit(-1);
        }
        try {
            stopWordList = FuseUtils.readWordListWithThreshold(stopWordListName, stopThreshold);
            forbiddenWordList = FuseUtils.readWordListWithThreshold(stopWordListName, forbiddenThreshold);
            endWordList = readLinesToSet(endWordListName);
            forbiddenCharList = readLinesToSet(forbiddenCharListName);
        } catch (IOException e) {
            System.err.println("ChineseTermFilter error loading files...");
            e.printStackTrace();
            System.exit(-1);
        }

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

    public boolean shouldFilterWord(String term) {

        String[] tokens = term.split(" ");
        if ((tokens.length > 0) && (endWordList.contains(tokens[tokens.length - 1]))) {
            return true;
        }
        boolean forbidden = false;
        for (String token : tokens) {
            if (forbiddenWordList.contains(token)) {
                forbidden = true;
                break;
            }
        }
        if (forbidden) {
            return true;
        }
        StringBuilder b = new StringBuilder();
        for (String token : tokens) {
            b.append(token);
        }
        char[] chars = b.toString().toCharArray();
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
            return true;
        }
        if (stopWordList.contains(b.toString())) {
            return true;
        }
        return false;
    }

    public List<String> filterWords(List<String> termList) {
        List<String> result = new ArrayList<String>();
        for (String term : termList) {
            String[] tokens = term.split(" ");
            if ((tokens.length > 0) && (endWordList.contains(tokens[tokens.length - 1]))) {
                continue;
            }
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
            StringBuilder b = new StringBuilder();
            for (String token : tokens) {
                b.append(token);
            }
            char[] chars = b.toString().toCharArray();
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
            if (stopWordList.contains(b.toString())) {
                continue;
            }
            result.add(term);
        }

        return result;
    }

    @Override
    public List<Term> filterTerm(List<Term> termList) {
        List<Term> result = new ArrayList<Term>();
        for (Term term : termList) {
            String[] tokens = term.word.split(" ");
            if ((tokens.length > 0) && (endWordList.contains(tokens[tokens.length - 1]))) {
                continue;
            }
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
            StringBuilder b = new StringBuilder();
            for (String token : tokens) {
                b.append(token);
            }
            char[] chars = b.toString().toCharArray();
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
            if (stopWordList.contains(b.toString())) {
                continue;
            }
            result.add(term);
        }

        return result;
    }


}
