package FuseJet.Models;

import FuseJet.Lex.FuseSentenceSplitter;
import FuseJet.Lex.FuseTokenizer;
import FuseJet.Utils.FuseUtils;
import Jet.Lisp.FeatureSet;
import Jet.Tipster.Annotation;
import Jet.Tipster.Document;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.*;
import java.io.File;

/**
 * User: yhe
 * Date: 5/25/12
 * Time: 1:54 PM
 */
public class FuseDocument extends Document {
    private String name=null;
    // private String metaDataInString = "";

    public Set<FuseRelation> getRelations() {
        return relations;
    }

    public void setRelations(Set<FuseRelation> relations) {
        this.relations = relations;
    }

    private Set<FuseRelation> relations = new HashSet<FuseRelation>();

    private boolean[] separatingIdx;

    private Vector<Annotation> temporaryAnnotations = new Vector<Annotation>(250);

    public Set<FuseAnnotation> getFuseEntities() {
        return fuseEntities;
    }

    private Set<FuseAnnotation> fuseEntities = new HashSet<FuseAnnotation>();

    // In constructor, we initialize textAnnTypes with "abstract"
    // and "body"
    private Set<String> textAnnTypes = new HashSet<String>();

    public static final FuseAnnotation THIS_ARTICLE =
            new FuseAnnotation("fuse-entity", new FuseEntitySpan(-1, -1), new FeatureSet(),
                    FuseAnnotation.AnnotationCategory.ENAMEX,
                    FuseAnnotation.AnnotationType.NA);

    public static final int MAX_SENTENCE_LENGTH = 120;

    public FuseDocument() {
        super();
        relations = new HashSet<FuseRelation>();
        textAnnTypes.add("text");
    }

    public FuseDocument(String name) {
        super();
        relations = new HashSet<FuseRelation>();
        textAnnTypes.add("text");
        this.name=name;
    }

//    public void setMaxSentenceLength(int maxSentenceLength) {
//        this.MAX_SENTENCE_LENGTH = maxSentenceLength;
//    }

//    @Deprecated
//    public Span abstractSpan() {
//        Vector<Annotation> annotations = this.annotationsOfType("ABSTRACT");
//        if (annotations == null || annotations.size() == 0) {
//            return new Span(0, 0);
//        }
//        return annotations.get(0).span();
//    }
//
//    @Deprecated
//    public Span bodySpan() {
//        Vector<Annotation> annotations = this.annotationsOfType("BODY");
//        if (annotations == null || annotations.size() == 0) {
//            return new Span(0, 0);
//        }
//        return annotations.get(0).span();
//    }

    public boolean[] findSeparatingIdx() {
        return separatingIdx;
        //return findSeparatingIdx(this.fullSpan());
    }

//    public boolean[] findSeparatingIdx(Span span) {
//        boolean[] isSeparatingIdx = new boolean[span.end() - span.start() + 1];
//        for (int i = span.start(); i < span.end(); i++) {
//            isSeparatingIdx[i - span.start()] = this.separatingIdx[i];
//        }
//        isSeparatingIdx[span.end() - span.start()] = true;
//        return isSeparatingIdx;
//    }

    @Deprecated
    public void saveToMaeFile(String fileName) throws IOException {
        PrintWriter w = new PrintWriter(new File(fileName));
        String text = text();
        w.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n" +
                "<JargonTask>\n" +
                "<TEXT><![CDATA[" +
                text +
                "\n]]></TEXT>\n<TAGS>\n</TAGS>\n</JargonTask>"
        );
        w.close();
    }

    public void splitAndTokenize() {
        // Remove all sentence and token annotations
        Vector<Annotation> oldTokens = annotationsOfType("token");
        if (oldTokens != null) {
            for (Annotation oldToken : oldTokens) {
                removeAnnotation(oldToken);
            }
        }
        Vector<Annotation> oldSentences = annotationsOfType("sentence");
        if (oldSentences != null) {
            for (Annotation oldSentence : oldSentences) {
                removeAnnotation(oldSentence);
            }
        }
        //System.err.println("Before splitting" + new Date());
        for (String textAnnType : textAnnTypes) {
            Vector<Annotation> texts = annotationsOfType(textAnnType);
            if (texts != null) {
                for (Annotation text : texts) {
                    FuseSentenceSplitter.split(this, text.span());
                }
            }
        }
        //FuseSentenceSplitter.split(this, this.bodySpan());
        //System.err.println("After splitting" + new Date());
        Vector<Annotation> sentences = this.annotationsOfType("sentence");
        String text = this.text();
        if (sentences != null) {
            Annotation.sortByStartPosition(sentences);
            int prevStart = -1;
            for (Annotation sent : sentences) {
                if (sent.start() == prevStart) {
                    this.removeAnnotation(sent);
                } else {
                    //System.err.println(sent.span());
                    FuseTokenizer.tokenize(this, sent.span(), text);
                }
                prevStart = sent.start();
            }
        } else {
            System.err.println("SplitAndTokenize WARNING: No sentence found to tokenize in document.");
        }
        //System.err.println(new Date());
    }


//    public void annotateExactNames(List<String> exactNames) {
//        for (int i = 0; i < exactNames.size(); i++) {
//            String exactName = exactNames.get(i);
//            Vector<Annotation> anns = annotationsOfType(exactName);
//            for (Annotation ann : anns) {
//                removeAnnotation(ann);
//                Annotation isExactNameAnn = AnnotationFactory.createSingleAttributeAnnotation("isExactName",
//                        this,
//                        ann.start(),
//                        ann.end(),
//                        "type",
//                        exactName);
//                addAnnotation(isExactNameAnn);
//            }
//        }
//    }

    public void saveOneLinePerSent(String fileName) throws IOException {
        PrintWriter w = new PrintWriter(new File(fileName));
//        FuseSentenceSplitter.split(this, this.abstractSpan());
//        FuseSentenceSplitter.split(this, this.bodySpan());
        Vector<Annotation> sentences = this.annotationsOfType("sentence");
        if (sentences == null) return;
        for (Annotation sent : sentences) {
            if (annotationsOfType("token", sent.span()).size() > MAX_SENTENCE_LENGTH) {
                continue;
            }
            StringBuilder sb = new StringBuilder();
//            FuseTokenizer.tokenize(this, sent.span());
            Vector<Annotation> tokens = this.annotationsOfType("token", sent.span());
            for (Annotation token : tokens) {
                sb.append(token.get("tokenString")).append(" ");

            }
            w.println(sb.toString().trim());
        }
        w.close();
    }

    public void loadGeniaAnnotations(String fileName) throws IOException {
        String[] geniaSentences = FuseUtils.readFileAsString(fileName).split("\n\n");
        Vector<Annotation> sentences = this.annotationsOfType("sentence");
        int geniaSentenceId = 0;
        for (int i = 0; i < sentences.size(); i++) {
            if (annotationsOfType("token", sentences.get(i).span()).size() > MAX_SENTENCE_LENGTH) {
                continue;
            }
            addGeniaAnnotationOnSentence(geniaSentences[geniaSentenceId].split("\n"), sentences.get(i));
            geniaSentenceId++;
        }

    }

    private void addGeniaAnnotationOnSentence(String[] geniaSentence, Annotation sentenceAnn) {
        int chunkStart = -1;
        String chunkName = "";
        int neStart = -1;
        String neName = "";
        Vector<Annotation> tokens = this.annotationsOfType("token", sentenceAnn.span());
        int i = 0;
        for (i = 0; i < tokens.size(); i++) {
            Annotation token = tokens.get(i);
            String[] features = geniaSentence[i].split("\t");
            /* Genia features 1: lemma, 2: pos, 3: chunk 4: NE */
            token.put("lemma", features[1].toLowerCase());
            //token.put("pos", features[2].toLowerCase());
            Annotation ann = AnnotationFactory.createSingleAttributeAnnotation(
                    "constit",
                    this,
                    token.start(),
                    token.end(),
                    "cat",
                    features[2].toLowerCase()
            );
            addAnnotation(ann);
            switch (FuseUtils.getBIOSwitch(features[3])) {
                case 'B':
                    if (chunkStart >= 0) {
                        ann = AnnotationFactory.createSingleAttributeAnnotation(
                                "constit",
                                this,
                                tokens.get(chunkStart).start(),
                                tokens.get(i - 1).end(),
                                "cat",
                                chunkName
                        );
                        addAnnotation(ann);
                    }
                    chunkStart = i;
                    chunkName = features[3].split("-")[1].toLowerCase();
                    break;
                case 'O':
                    if (chunkStart >= 0) {
                        ann = AnnotationFactory.createSingleAttributeAnnotation(
                                "constit",
                                this,
                                tokens.get(chunkStart).start(),
                                tokens.get(i - 1).end(),
                                "cat",
                                chunkName
                        );
                        addAnnotation(ann);
                    }
                    chunkStart = -1;
                    break;
            }
            /* adding NE annotations */
            switch (FuseUtils.getBIOSwitch(features[4])) {
                case 'B':
                    if (neStart >= 0) {
                        ann = AnnotationFactory.createSingleAttributeAnnotation(
                                "geniaEntity",
                                this,
                                tokens.get(neStart).start(),
                                tokens.get(i - 1).end(),
                                "cat",
                                neName
                        );
                        addAnnotation(ann);
                    }
                    neStart = i;
                    neName = features[4].split("-")[1].toLowerCase();
                    break;
                case 'O':
                    if (neStart >= 0) {
                        ann = AnnotationFactory.createSingleAttributeAnnotation(
                                "geniaEntity",
                                this,
                                tokens.get(neStart).start(),
                                tokens.get(i - 1).end(),
                                "cat",
                                neName
                        );
                        addAnnotation(ann);
                    }
                    neStart = -1;
                    break;
            }
        }
        if (chunkStart >= 0) {
            Annotation ann = AnnotationFactory.createSingleAttributeAnnotation(
                    "constit",
                    this,
                    tokens.get(chunkStart).start(),
                    tokens.get(i - 1).end(),
                    "cat",
                    chunkName
            );
            addAnnotation(ann);
        }
        if (neStart >= 0) {
            Annotation ann = AnnotationFactory.createSingleAttributeAnnotation(
                    "geniaEntity",
                    this,
                    tokens.get(neStart).start(),
                    tokens.get(i - 1).end(),
                    "cat",
                    neName
            );
            addAnnotation(ann);
        }
    }

    public void removeTemporaryAnnotations() {
        for (Annotation ann : temporaryAnnotations) {
            removeAnnotation(ann);
        }
    }

    public void addRelation(FuseRelation relation) {
        if (!relations.contains(relation)) {
            relations.add(relation);
        }
    }

    @Override
    public Annotation addAnnotation(Annotation ann) {
        Annotation result = super.addAnnotation(ann);
        if (ann.type().equals("fuse-entity")) {
            if (fuseEntities.contains(ann)) {
                removeAnnotation(ann);
                // obtain same object in fuseEntities Set
                for (FuseAnnotation entity : fuseEntities) {
                    if (entity.equals(ann)) {
                        result = entity;
                    }
                }
            } else {
                fuseEntities.add((FuseAnnotation) ann);
            }
        } else {
            if (ann.type().startsWith("ELEMENT_")) {
                temporaryAnnotations.add(ann);
            }
            if (separatingIdx != null) {
                separatingIdx[ann.start()] = true;
                separatingIdx[ann.end()] = true;
            }
        }
        return result;
    }

    @Override
    public void setText(String stg) {
        super.setText(stg);
        separatingIdx = new boolean[stg.length() + 1];
    }
    public String getName(){
        return name;
    }

    public void setName(String outputFile) {
        this.name = outputFile;
    }
}
