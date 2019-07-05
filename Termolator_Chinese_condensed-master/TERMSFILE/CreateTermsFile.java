
/*
* Author: Yuling Gu
* Date: July 26, 2018
* Description: 
* This program takes in two files, the first one containing a list of file names, and
* the second with the target terms as extracted using part of the Chinese termolator. 
* The purpose of this program is to produce an intermediate file like that of the .terms
* file in the English termolator which has not undergone the distributional metric stage.
* Usage : java CreateTermsFile fileList targetTermslist
* Example : java CreateTermsFile sample.pos.filelist targetTermsAll.txt
*/

import java.io.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.regex.*;

public class CreateTermsFile {

    // Use Rabin Karp algorithm to search to target terms in the documents
    public static ArrayList<Integer> RabinKarp(String pattern, String text, int x, int p){
        int l = pattern.length();
        int n = text.length();
        int xL = 1;
        int patternHash = 0;
        int runningHash = 0;
        for(int i = 0; i < l; i++){
            patternHash = (patternHash * x + pattern.charAt(i)) % p;
            runningHash = (runningHash * x + text.charAt(i)) % p;
        }
        for(int i = 0; i < l-1; i++)
            xL = (xL * x) % p;
        ArrayList<Integer> positions = new ArrayList<Integer>();
        for(int i = 0; i <= n-l; i++){
            if(patternHash == runningHash){
                int j = 0;
                for(j = 0; j < l; j++)
                    if(text.charAt(i+j) != pattern.charAt(j))
                        break;
                if(j == l)
                    positions.add(i);
            }
            if(i < n-l){
                runningHash = ((runningHash - text.charAt(i) * xL) * x + text.charAt(i+l)) % p;
                if(runningHash < 0)
                    runningHash += p;
            }
            else
                runningHash = -1;
        }
        return positions;
    }

    public static void main(String[] args) throws Exception {
        String fileList = args[0];
        String termsList = args[1];
        String line;
        // Store the target terms extracted
        ArrayList<String> targetTerms = new ArrayList<String>();
        BufferedReader targetList = new BufferedReader(new FileReader(termsList));
        while ((line = targetList.readLine()) != null) {
            line = line.replace("\n", "");
            targetTerms.add(line);
        }

        // Go through each document in the file list
        BufferedReader br = new BufferedReader(new FileReader(fileList));
        while ((line = br.readLine()) != null) {
            // for each document file
            String documentName = line;
            // read the whole file as one string
            String documentContent = new String(Files.readAllBytes(Paths.get(line)), StandardCharsets.UTF_8);
            // output file
            PrintWriter output = new PrintWriter(documentName + ".terms");
            int termID = 1;
            // try to match all the terms
            for (int i = 0; i < targetTerms.size(); i++) {
                String termFound;
                int stringLength, start, end;
                // match in the document
                termFound = targetTerms.get(i);
                stringLength = termFound.length();
                ArrayList<Integer> a = RabinKarp(termFound, documentContent, 123, 1000000009);
                int docFreq = a.size();
                for(int j : a) {
                    start = j + 1;
                    end = j + stringLength;
                    output.println("TERM ID=\"NYU_TERM_" + termID + "\" STRING=\"" + termFound + "\" FREQUENCY=" + docFreq +
                        " START=" + start + " END=" + end + " LEMMA=\"" + termFound + "\" LEMMA_FREQUENCY=" + docFreq);
                    termID++;
                }                    
            }
            output.close();
        }
  }
}



