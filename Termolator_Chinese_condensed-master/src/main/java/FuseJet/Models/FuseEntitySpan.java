package FuseJet.Models;

import Jet.Tipster.Annotation;
import Jet.Tipster.Document;
import Jet.Tipster.Span;

import java.util.ArrayList;
import java.util.List;
import java.util.Vector;

/**
 * User: yhe
 * Date: 6/18/12
 * Time: 3:50 PM
 */
public class FuseEntitySpan extends Span {
    public FuseEntitySpan(int start, int end) {
        super(start, end);
    }

    public FuseEntitySpan(Span span) {
        super(span.start(), span.end());
        setDocument(span.document());
    }

    public void trim() {
        Vector<Annotation> tokens = document().annotationsOfType("token", this);
        int start = this.start();
        if (tokens == null) return;
        int i = 0;
        for (; i < tokens.size(); i++) {
            Annotation token = tokens.get(i);
            Vector<Annotation> cats = document().annotationsOfType("constit", token.span());
            if (cats == null) return;
            for (Annotation cat : cats) {
                if (cat.get("cat").equals("dt")) {
                    start = token.end();
                } else {
                    break;
                }
            }

        }
        setStart(start);
        //tokens = document().annotationsOfType("token", this);
        for (; i < tokens.size(); i++) {
            Annotation token = tokens.get(i);
            Vector<Annotation> cats = document().annotationsOfType("constit", token.span());
            if (cats == null) return;
            for (Annotation cat : cats) {
                if (cat.get("cat").equals("in")) {
                    setEnd(token.start());
                    break;
                }
            }
        }
    }

    public boolean isValidJargon() {
//        System.err.println("In isValidJargon():" + this);
//        System.err.println("Length of whole text:" + document().text().length());
        if (document().text(this).length() == 0) {
            return false;
        }
        Vector<Annotation> tokens = document().annotationsOfType("token", this);
        if (tokens != null) {
            for (Annotation token : tokens) {
                String lemma = ((String) token.get("tokenString")).toLowerCase();
                if (lemma.endsWith("ly")) {
                    return false;
                }
                if (lemma.equals("same") || lemma.equals("similar") || lemma.equals("data")) {
                    return false;
                }
            }
            return true;
        } else {
            return false;
        }
    }

    public boolean isValidSpecificJargon() {
        return isValidJargon();
    }

    public FuseEntitySpan[] fromSpan(Span span) {
        List<FuseEntitySpan> spanList = new ArrayList<FuseEntitySpan>();
        if (span.document() == null) {
            spanList.add(new FuseEntitySpan(span));
            return spanList.toArray(new FuseEntitySpan[1]);
        }
        Document doc = span.document();
        Vector<Annotation> annotations = doc.annotationsOfType("np-group", span);
        if (annotations.size() == 0) {
            spanList.add(new FuseEntitySpan(span));
            return spanList.toArray(new FuseEntitySpan[1]);
        }
        Annotation npGroup = annotations.get(0);
        Span npSpan = (Span) npGroup.get("conj");
        while (npSpan != null) {
            spanList.add(new FuseEntitySpan(npSpan));
            npSpan = (Span) doc.annotationsOfType("constit", npSpan).get(0).get("conj");
        }
        return spanList.toArray(new FuseEntitySpan[spanList.size()]);
    }
}
