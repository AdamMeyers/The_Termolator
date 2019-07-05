package FuseJet.Models;

import Jet.Tipster.Annotation;

/**
 * @author yhe & gcl
 */
public class FuseRelation {
    public enum RelationType {
        ABBREVIATE, EXEMPLIFY, OPINION, ORIGINATE, RELATED_WORK, DEFINED, UNKNOWN
    }

    private String id = "";
    /*
    ARG1 and ARG2 can be: jargon terms or any currently supported type of enamex
    (citations, organizations, urls or people). ARG1 (without modifiers, see below)
    must be more specific than ARG2.
     */
    private FuseAnnotation arg1;
    private FuseAnnotation arg2;
    private String arg3;
    private String arg4;
    private RelationType type;
    private FuseAnnotation annotatedSignal;
    private String textSignal = "";
    private String gramSignal = "";
    private String auto = "";

    public FuseRelation(String id, FuseAnnotation arg1, FuseAnnotation arg2, String arg3, String arg4, RelationType type, String textSignal, String gramSignal) {
        this.id = id;
        this.arg1 = arg1;
        this.arg2 = arg2;
        this.arg3 = arg3;
        this.arg4 = arg4;
        this.type = type;
        this.textSignal = textSignal;
        this.gramSignal = gramSignal;
    }

    public FuseRelation(String id, FuseAnnotation arg1, FuseAnnotation arg2, String arg3, String arg4, RelationType type, FuseAnnotation annotatedSignal, String gramSignal) {
        this.id = id;
        this.arg1 = arg1;
        this.arg2 = arg2;
        this.arg3 = arg3;
        this.arg4 = arg4;
        this.type = type;
        this.annotatedSignal = annotatedSignal;
        this.gramSignal = gramSignal;
    }

    public FuseRelation(String id, FuseAnnotation arg1, FuseAnnotation arg2, RelationType type) {
        this.id = id;
        this.arg1 = arg1;
        this.arg2 = arg2;
        this.arg3 = "";
        this.arg4 = "";
        this.type = type;
        this.textSignal = "";
        this.gramSignal = "";
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public FuseAnnotation getArg1() {
        return arg1;
    }

    public void setArg1(FuseAnnotation arg1) {
        this.arg1 = arg1;
    }

    public FuseAnnotation getArg2() {
        return arg2;
    }

    public void setArg2(FuseAnnotation arg2) {
        this.arg2 = arg2;
    }

    public String getArg3() {
        return arg3;
    }

    public void setArg3(String arg3) {
        this.arg3 = arg3;
    }

    public String getArg4() {
        return arg4;
    }

    public void setArg4(String arg4) {
        this.arg4 = arg4;
    }

    public RelationType getType() {
        return type;
    }

    public void setType(RelationType type) {
        this.type = type;
    }

    public FuseAnnotation getAnnotatedSignal() {
        return annotatedSignal;
    }

    public void setAnnotatedSignal(FuseAnnotation annotatedSignal) {
        this.annotatedSignal = annotatedSignal;
    }

    public String getTextSignal() {
        /*
        First try to find existing string-based textSignal. If it does not exist,
        and the span of annotatedSignal match a chunk of text in the Document, use
        the text in in that span as textSignal.
         */
        return textSignal;
    }

    public void setTextSignal(String textSignal) {
        this.textSignal = textSignal;
    }

    public String getGramSignal() {
        return gramSignal;
    }

    public void setGramSignal(String gramSignal) {
        this.gramSignal = gramSignal;
    }

    public void setAuto(String auto){
        this.auto = auto;
    }

    public String getAuto(){
        return auto;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        FuseRelation that = (FuseRelation) o;

        if (!arg1.equals(that.arg1)) return false;
        if (!arg2.equals(that.arg2)) return false;
        if (!arg3.equals(that.arg3)) return false;
        if (!arg4.equals(that.arg4)) return false;
        if (!id.equals(that.id)) return false;
        if (type != that.type) return false;

        return true;
    }

    @Override
    public int hashCode() {
        int result = id.hashCode();
        result = 31 * result + arg1.hashCode();
        result = 31 * result + arg2.hashCode();
        result = 31 * result + arg3.hashCode();
        result = 31 * result + arg4.hashCode();
        result = 31 * result + type.hashCode();
        return result;
    }
}