package FuseJet.Terminology;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.List;

public class Term implements Comparable<Term>{
	final String word;
	int length = 1;
	double cvalue = -1; ;
	double DCvalue = -1;
	private int posFreq = -1;
    private int posDocFreq = -1; // added by Yifan
	int negFreq = 0;
	int rFreqValue = 0;
	List<Integer> rFreq = new ArrayList<Integer>();
	double tokenDR = 0.0;
	
	void calTokenDR(TerminologyExtractor tmap){
		tokenDR = 0.0;
		String[] tokens = word.split(" ");
		for(String token: tokens){
			if(isDigit(token) == false)
			   tokenDR += (double)tmap.token_rel.get(token)/tmap.token_total.get(token);
		}
		tokenDR = tokenDR/tokens.length;
	}
	
	boolean isDigit(String word){
		for(int i=0;i<word.length();i++){
			char c = word.charAt(i);
			if(Character.isDigit(c) == false)
				return false;
		}
		return true;
	}

	Term(String w){
		word = w;
		for(int i=0;i<w.length();i++){
			if(w.charAt(i) == ' ')
				length++;
		}
	}

	private void addPos(int freq){
		if(freq == 0)
			return;
		rFreq.add(freq);		
	}

	private void addNeg(int n){
		negFreq += n;
	}

	void addFreq(int n, boolean positive){
		if(positive)
			addPos(n);
		else
			addNeg(n);
	}

	public int getPosFreq(){
		if(posFreq == -1){
			posFreq = 0;
			for(Integer freq:rFreq)
				posFreq += freq;
		}
		return posFreq;
	}

    public int getPosDocFreq(){
        if(posDocFreq == -1){
            posDocFreq = 0;
            for(Integer freq:rFreq)
                posDocFreq += (freq>0) ? 1 : 0;
        }
        return posDocFreq;
    }

    public int getWholeFreq(){
		return getPosFreq()+negFreq;
	}

	//calculate Document Relevance (DR)
	public double calDR(){
		double posFreq = getPosFreq();
		return posFreq*Math.log(length+2.0)/(negFreq+posFreq);
	}

	//calculate Document Consensus (DC)	
	public double calDC(){
		if(DCvalue < 0 ){
			int posFreq = getPosFreq();
			double DC = 0;
			for(Integer freq:rFreq){
				double ptd = (double)freq/posFreq;
				DC += ptd*Math.log(1/ptd);
			}
			DCvalue =  DC;///rFreq.size();
		}
		return DCvalue;
	}

	//different metrics can be used for terminology extraction
	double calTermhoodWeight(){
		//DR and DC method, fromPaola Velardi 2001
		//return termMap.alpha*calDR()+termMap.beta*calDC();
		//try our new method, without normalization
		return calDR()*calDC();
	}


	public double calIDF(){
		return calDR()/Math.log(rFreq.size()+3.0);
	}

	public double calTFIDF(){
		int max = 0;
		for(int freq:rFreq){
			if(max < freq)
				max = freq;
		}
		return calDR()*max/calIDF();
		//return calDR()*posFreq/calIDF(); 
	}


	@Override
	public int compareTo(Term t) {
		double score = calTermhoodWeight()-t.calTermhoodWeight();
		if(score > 0)
			return -1;
		else if(score < 0)
			return 1;
		else
			return 0;
	}

	@Override
	public String toString() {
		return String.format("%-30s\t %-6d\t %-6d\t %-6d\t %-6.2f\t %-6.2f\t  %-6.2f\t %-6.1f", 
				word,getPosFreq(),negFreq,rFreq.size(),tokenDR,calDR(), calDC(),cvalue);
	}

	public static Term readTerm(String line){
		System.err.println(line);
		String[] tokens = line.split("\t");
		Term t = new Term(tokens[0]);
		t.posFreq = Integer.parseInt(tokens[1].trim());
		t.negFreq = Integer.parseInt(tokens[2].trim());
		t.rFreqValue = Integer.parseInt(tokens[3].trim());
		t.tokenDR = Double.parseDouble(tokens[4].trim());
		t.DCvalue = Double.parseDouble(tokens[6].trim());
		t.cvalue = Double.parseDouble(tokens[7].trim());
		return t;
	}

	public static List<Term> readTermsFromFile(String termFile) throws IOException{
		List<Term> terms = new ArrayList<Term>();
		BufferedReader reader = new BufferedReader(new FileReader(termFile));
		String line;
		while((line = reader.readLine()) != null){
			Term t = readTerm(line);
			terms.add(t);
		}
		reader.close();
		return terms;
	}

	public static void writeTermsToFile(Collection<Term> terms, String termFile)throws IOException{
		System.err.println("Begin to write ranking list.");
		BufferedWriter writer= new BufferedWriter(new OutputStreamWriter(new FileOutputStream(termFile),"utf-8"));
		for(Term t:terms){
			writer.write(t.toString()+"\n");
		}
		writer.close();
	}

}


class IDFComparator implements Comparator<Term>{
	@Override
	public int compare(Term o1, Term o2) {
		return -Double.compare(o1.calIDF(), o2.calIDF());

	}
}

class TFIDFComparator implements Comparator<Term>{
	@Override
	public int compare(Term o1, Term o2) {
		return -Double.compare(o1.calTFIDF(), o2.calTFIDF());
	}
}

class DRComparator implements Comparator<Term>{
	@Override
	public int compare(Term o1, Term o2) {
		return -Double.compare(o1.calDR(), o2.calDR());

	}
}

class DRDCComparator implements Comparator<Term>{
	@Override
	public int compare(Term o1, Term o2) {
		return -Double.compare(o1.calTermhoodWeight(), o2.calTermhoodWeight());

	}
}


//normalized by terminology length
class TokenDRDCComparator implements Comparator<Term>{
	@Override
	public int compare(Term o1, Term o2) {
		return -Double.compare(score(o1),score(o2));
	}

	public double score(Term o){
		return (double)o.calTermhoodWeight()*o.tokenDR;
	}
}

class TokenIDFComparator implements Comparator<Term>{
	@Override
	public int compare(Term arg0, Term arg1) {
		
		return -Double.compare(score(arg0),score(arg1));
	}
	
	public double score(Term o){
		return (double)o.calIDF()*o.tokenDR;
	}
}



