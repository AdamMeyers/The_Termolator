package FuseJet.Models;

import Jet.Lisp.FeatureSet;
import Jet.Tipster.Annotation;
import Jet.Tipster.Document;
import Jet.Tipster.Span;

/**
 * Created with IntelliJ IDEA.
 * User: yhe
 * Date: 5/25/12
 * Time: 11:43 PM
 * To change this template use File | Settings | File Templates.
 */
public class AnnotationFactory {

    public static Annotation createAnnotation(String text, Document document, int start, int end) {
        FeatureSet featureSet = new FeatureSet();
        Span span = new Span(start, end);
        span.setDocument(document);
        return new Annotation(text, span, featureSet);
    }

    public static Annotation createSingleAttributeAnnotation(String text, Document document, int start, int end, String attrName, Object attrValue) {
        FeatureSet featureSet = new FeatureSet(attrName, attrValue);
        Span span = new Span(start, end);
        span.setDocument(document);
        return new Annotation(text, span, featureSet);
    }

    public static Annotation createDoubleAttributeAnnotation(String text, Document document, int start, int end, String attrName1, Object attrValue1, String attrName2, Object attrValue2) {
        FeatureSet featureSet = new FeatureSet(attrName1, attrValue1, attrName2, attrValue2);
        Span span = new Span(start, end);
        span.setDocument(document);
        return new Annotation(text, span, featureSet);
    }

    public static Annotation createTripleAttributeAnnotation(String text, Document document, int start, int end, String attrName1, Object attrValue1, String attrName2, Object attrValue2,  String attrName3, Object attrValue3) {
        FeatureSet featureSet = new FeatureSet(attrName1, attrValue1, attrName2, attrValue2, attrName3, attrValue3);
        Span span = new Span(start, end);
        span.setDocument(document);
        return new Annotation(text, span, featureSet);
    }
}
