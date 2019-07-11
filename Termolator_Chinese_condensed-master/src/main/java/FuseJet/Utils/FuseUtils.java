package FuseJet.Utils;

import FuseJet.Models.AnnotationFactory;
import FuseJet.Models.FuseAnnotation;
import FuseJet.Models.FuseDocument;
import Jet.Lisp.FeatureSet;
import Jet.Tipster.Annotation;
import Jet.Tipster.Document;
import Jet.Tipster.Span;
import sun.font.TrueTypeFont;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

/**
 * User: yhe
 * Date: 6/5/12
 * Time: 5:19 PM
 */
public class FuseUtils {

    public static Set<String> readLinesToSet(String filename) throws IOException {
        Set<String> result = new HashSet<String>();
        BufferedReader br = new BufferedReader(new FileReader(filename));
        String strLine;
        while ((strLine = br.readLine()) != null) {
            result.add(strLine);
        }
        br.close();
        return result;
    }

    public static String[] readSentenceChunksFromConll(String fileName) throws IOException {
        return readFileAsString(fileName).split("\n\n");
    }

    public static List<List<Map<String, Object>>> readConll(String filename,
			Map<String, Integer> fields) throws IOException {
		List<String> sentences = Arrays.asList(readFileAsString(filename).split("\\n\\n"));
		List<List<Map<String, Object>>> result = new ArrayList<List<Map<String,Object>>>();
		for (String s : sentences) {
			int start = 0;
			String[] words = s.split("\n");
			List<Map<String, Object>> sentInfo = new ArrayList<Map<String,Object>>();
            int id = 0;
			for (String token : words) {
                //System.out.println(token);
				String[] parts = token.split("\\t");
				Map<String, Object> wordInfo = new HashMap<String, Object>();
				wordInfo.put("id", id);
				wordInfo.put("surface", parts[0]);
				wordInfo.put("start", start);
				wordInfo.put("end", start + parts[0].length());
				/* previous end + space = new start */
				start = (Integer)wordInfo.get("end") + 1;
				for (String fieldKey : fields.keySet()) {
					wordInfo.put(fieldKey, parts[fields.get(fieldKey)]);
				}
				sentInfo.add(wordInfo);
                id++;
			}
			result.add(sentInfo);
		}
		return result;
	}

    public static String[] readLines(String filename) throws IOException {
		List<String> result = new ArrayList<String>();
		BufferedReader br = new BufferedReader(new FileReader(filename));
		String strLine;
		while ((strLine = br.readLine()) != null) {
			result.add(strLine);
		}
		br.close();
		return result.toArray(new String[result.size()]);
	}

    public static String readFileAsString(String filePath) throws IOException {
		StringBuilder fileData = new StringBuilder(1000);
		BufferedReader reader = new BufferedReader(new FileReader(filePath));
		char[] buf = new char[1024];
		int numRead = 0;
		while ((numRead = reader.read(buf)) != -1) {
			fileData.append(buf, 0, numRead);
		}
		reader.close();
		return fileData.toString();
	}

    public static char getBIOSwitch(String s) {
        if (s.length()  > 0) return s.charAt(0);
        return 'O';
    }

    public static Annotation findAnnotationWithTypeAndSpan(Document document, String type, FeatureSet fs, Span span) {
        Vector<Annotation> candidates = document.annotationsAt(span.start(), type);
        for (Annotation ann : candidates) {
            boolean isMatch = true;
            while (fs.keys().hasMoreElements()) {
                String key = (String)fs.keys().nextElement();
                Object val = fs.get(key);
                if ((ann.get(key) == null) || (!ann.get(key).equals(val))) {
                    isMatch = false;
                    break;
                }
            }
            if (isMatch) return ann;
        }
        return null;
    }

    public static Set<String> readWordListWithThreshold(String stopFileName, int threshold) throws IOException {
        BufferedReader r = new BufferedReader(new FileReader(stopFileName));
        Set<String> result = new HashSet<String>();
        String line;
        while ((line = r.readLine()) != null) {
            String[] parts = line.split("\t");
            String word = parts[0];
            int num = Integer.valueOf(parts[1]);
            if (num >= threshold) {
                result.add(word.trim());
            }
            else {
                break;
            }
        }
        r.close();
        return result;
    }

    public static Set<String> readLCWordListWithThreshold(String stopFileName, int threshold) throws IOException {
        BufferedReader r = new BufferedReader(new FileReader(stopFileName));
        Set<String> result = new HashSet<String>();
        String line;
        while ((line = r.readLine()) != null) {
            String[] parts = line.split("\t");
            String word = parts[0];
            int num = Integer.valueOf(parts[1]);
            if (num >= threshold) {
                result.add(word.trim().toLowerCase());
            }
            else {
                break;
            }
        }
        r.close();
        return result;
    }

    public static List<String> readSentencesFromPOSFile(String fileName) {
        List<String> result = new ArrayList<String>();
        String[] sentences;
        try {
            sentences = readSentenceChunksFromConll(fileName);
        }
        catch (Exception e) {
            System.err.println("Error reading file:" + fileName);
            return null;
        }
        for (String s : sentences) {
            StringBuilder b = new StringBuilder();
            b.append(" ");
            String[] words = s.split("\n");
            for (String word : words) {
                String[] parts = word.split("\\t");
                if (parts.length > 0) {
                    b.append(parts[0]).append(" ");
                }
            }
            result.add(b.toString());
        }
        return result;
    }

    public static List<String> readSentencesFromPOSFileWithStartEnd(String fileName) {
        List<String> result = new ArrayList<String>();
        String[] sentences;
        try {
            sentences = readSentenceChunksFromConll(fileName);
        }
        catch (Exception e) {
            System.err.println("Error reading file:" + fileName);
            return null;
        }
        for (String s : sentences) {
            StringBuilder b = new StringBuilder();
            b.append(" ");
            String[] words = s.split("\n");
            for (String word : words) {
                String[] parts = word.split("\\t");
                if (parts.length > 0) {
                    b.append(parts[0]).append(" ");
                }
            }
            result.add("$$$$$$$$$$" + b.toString() + "$$$$$$$$$$");
        }
        return result;
    }

}
