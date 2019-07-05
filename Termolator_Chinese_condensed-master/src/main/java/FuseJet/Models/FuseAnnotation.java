package FuseJet.Models;

import Jet.Lisp.FeatureSet;
import Jet.Tipster.Annotation;

/**
 *@author yhe & gcl
 */
public class FuseAnnotation extends Annotation {
    // ENAMEX or JARGON
    private AnnotationCategory category;

    public AnnotationType getEntityType() {
        return entityType;
    }

    public void setEntityType(AnnotationType entityType) {
        this.entityType = entityType;
    }

    public AnnotationCategory getCategory() {
        return category;
    }

    public void setCategory(AnnotationCategory category) {
        this.category = category;
    }

    private AnnotationType entityType;

    public FuseAnnotation(String tp, FuseEntitySpan sp, FeatureSet att, AnnotationCategory category, AnnotationType entityType) {
        super(tp, sp, att);
        this.category = category;
        this.entityType = entityType;
    }

//    public static FuseAnnotation getEnamexInstance(Document doc, int start, int end, AnnotationType type) {
//        Span sp = new Span(start, end);
//        sp.setDocument(doc);
//        return new FuseAnnotation(type.toString(), sp, new FeatureSet(), AnnotationCategory.ENAMEX, type);
//    }

    public enum AnnotationCategory {ENAMEX, JARGON, SIGNAL, NA};
    public enum AnnotationType {CITATION, ORGANIZATION, URL, PERSON, GPE,  NA};

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        FuseAnnotation that = (FuseAnnotation) o;

        if (category != that.category) return false;
        if (entityType != that.entityType) return false;
        if (!this.span().equals(that.span())) return false;
        if (!this.type().equals(that.type())) return false;

        return true;
    }

    @Override
    public int hashCode() {
        int result = category.hashCode();
        result = 31 * result + entityType.hashCode();
        result = 31 * result + this.type().hashCode();
        result = 31 * result + span().hashCode();
        return result;
    }
}
