package FuseJet.Terminology.Models;

import java.util.*;

/**
 * User: yhe
 * Date: 7/14/13
 * Time: 2:50 PM
 */
public class ChineseTerm implements Comparable<ChineseTerm> {
    private String term;
    private int count;
    private int negativeCount;
    private Set<String> leftContexts = new HashSet<String>();
    private Set<String> rightContexts = new HashSet<String>();
    private int documentCount;
    private List<Integer> dist = new ArrayList<Integer>();
    private double dc = -1.0;
    private double dr = -1.0;
    private double drdc = -1.0;

    public ChineseTerm(String term) {
        count = 0;
        negativeCount = 1;
//        documentCount = 1;
        dist.add(0);
        this.term = term;
    }

    public String getTerm() {
        return term;
    }

    public void setTerm(String term) {
        this.term = term;
    }

    public int getCount() {
        return count;
    }

    public void setCount(int count) {
        this.count = count;
    }

    private void addToContexts(String term, Set<String> contexts) {
        contexts.add(term);
    }

    public void addToRightContexts(String term) {
        addToContexts(term, rightContexts);
    }

    public void addToLeftContexts(String term) {
        addToContexts(term, leftContexts);
    }

    public int getRightCount() {
        return rightContexts.size();
    }

    public int getLeftCount() {
        return leftContexts.size();
    }

    public Set<String> getLeftContexts() {
        return leftContexts;
    }

    public Set<String> getRightContexts() {
        return rightContexts;
    }

    public int accessorVariety() {
        return rightContexts.size() < leftContexts.size() ? rightContexts.size() : leftContexts.size();
    }

    public void occur() {
        documentCount = 1;
        dist.set(0, dist.get(0)+1);
        count++;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        ChineseTerm that = (ChineseTerm) o;

        if (count != that.count) return false;
        if (leftContexts != null ? !leftContexts.equals(that.leftContexts) : that.leftContexts != null) return false;
        if (rightContexts != null ? !rightContexts.equals(that.rightContexts) : that.rightContexts != null)
            return false;
        if (term != null ? !term.equals(that.term) : that.term != null) return false;

        return true;
    }

    @Override
    public int hashCode() {
        int result = term != null ? term.hashCode() : 0;
        result = 31 * result + count;
        result = 31 * result + (leftContexts != null ? leftContexts.hashCode() : 0);
        result = 31 * result + (rightContexts != null ? rightContexts.hashCode() : 0);
        return result;
    }

    @Override
    public int compareTo(ChineseTerm chineseTerm) {
        return 0;  //To change body of implemented methods use File | Settings | File Templates.
    }

    public String toString() {
        return term + "\t\tLC:" + leftContexts.size() + "\t\tRC:" + rightContexts.size() + "\t\tOCCUR:" + count + "\t\tDocCount:" + documentCount
                + "\t\tDRDC:" + getDRDC();
    }

    public void add(ChineseTerm t) {
        leftContexts.addAll(t.leftContexts);
        rightContexts.addAll(t.rightContexts);
        count += t.count;
        dist.add(t.count);
        documentCount++;
    }

    public void updateNegative(ChineseTerm t) {
        if (term.equals(t.term)) {
            negativeCount = t.count;
        }
    }

    public int getDocumentCount() {
        return documentCount;
    }

    public double getDC() {
        if(dc < 0){
            updateDC();
        }
        return dc;
    }

    public void updateDC() {
        int posFreq = count;
        dc = 0.0;
        for(Integer freq:dist){
            double ptd = (double)freq/posFreq;
            if (ptd > 0.0) {
                dc += ptd*Math.log(1/ptd);
            }
        }
    }

    public void updateDR() {
        double posFreq = count;
        int length = term.split(" ").length;
        int negFreq = negativeCount;
        dr = posFreq*Math.log(length+2.0)/(negFreq+posFreq);
    }

    public double getDR() {
        if (dr < 0.0) {
            updateDR();
        }
        return dr;
    }

    public void updateDRDC() {
        drdc = getDR()*getDC();
    }

    public double getDRDC() {
        if (drdc < 0.0)  {
            drdc = getDR()*getDC();
        }
        return drdc;
    }

}
