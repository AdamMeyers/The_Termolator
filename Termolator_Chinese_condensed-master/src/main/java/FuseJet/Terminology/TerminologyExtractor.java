package FuseJet.Terminology;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.regex.Pattern;

public class TerminologyExtractor {
	static double alpha = 0.9;  //Usually, alpha close to 0.9 is good.
	static double beta = 0.3;// When N is sufficiently large, good beta is between 0.35 and 0.25	
	private int maxTermLength = 4;  // Shasha's params: 4, 4 Yifan's params = 9, 2
	private int minOccurrence = 4;
    private int minDocOccurrence = 6;
    private static boolean writeStats = false;
    private static int contextWindowSize = 4;
    private static boolean useDEStemmer = false;

	static enum REL_TYPE{IDF, TFIDF, DR, DRDC,TokenDRDC, TokenIDF};
	REL_TYPE type = REL_TYPE.IDF;
	private Map<String, Term> map = new HashMap<String, Term>();

	//record token frequency for future study
	Map<String, Integer> token_rel = new HashMap<String,Integer>();
	Map<String, Integer> token_total = new HashMap<String,Integer>();


	private List<String> posExampleFileList = new ArrayList<String> ();
	private List<String> negExampleFileList = new ArrayList<String>();
	private String inputSuffix;
	private String outputFileName;
    private static int termSize = 10000;
    private static int exampleSize = 6;
    private static boolean toUpper = false;
    private static boolean concatSent = false;
    private static int maxPosCollectionSize = -1;
	private NPExtractor npExtractor;

    private static String resourceInfo = "";
    private static TermFilter termFilter = new DummyTermFilter();
    private static Properties props = new Properties();


	public static void main(String[] args) throws IOException{
        String filterSetFileName = "";
        String[] argv = args;
//        if (args.length ==7) {
//            String[] opts = Arrays.copyOfRange(args, 0, 2);
//            argv = Arrays.copyOfRange(args, 2, 7);
//            Getopt getopt = new Getopt("Terminology Relation", opts, "f:");
//            int c;
//            String arg;
//            while ((c = getopt.getopt()) != -1) {
//                switch(c) {
//                    case 'f':
//                        arg = getopt.getOptarg();
//                        filterSetFileName = arg;
//                        break;
//                    default:
//                        System.out.print("getopt() returned " + c + "\n");
//                }
//            }
//        }

//		if(argv.length < 5){
//			System.err.println("Parameter not correct\n Please type: " +
//                    "-f filterList\t" +
//					"posFileList\t" +
//					"negFileList\t" +
//					"inputSuffix (pos or chunk)\trankingListFile\tRelevance Type (IDF,TFIDF,DR,REL)\n" +
//					"System exiting...");
//			return;
//		}
//        if (!(argv[2].equals("pos")||argv[2].equals("chunk"))) {
//            System.err.println("inputSuffix must be pos or chunk\n Please check:\n" + argv[2]+"\n"+
//                    "posFileList \t posDir  \t" +
//                    "negFileList \t negDir \t" +
//                    "inputSuffix (pos or chunk) \t rankingListFile\t Relevance Type (IDF,TFIDF,DR,REL)\n" +
//                    "System exiting...");
//            return;
//        }
        String posFile, inputSuffix, outputFile, relevanceType;
        String[] negFiles;
        try {
            if (argv.length == 5) {
                posFile = argv[0];
                inputSuffix = argv[2];
                outputFile = argv[3];
                relevanceType = argv[4];
                negFiles = argv[1].split(";");

            }
            else {
                if (argv.length == 4) {

                    props.load(new FileReader(argv[0]));
                    updatePropVariables();
                    posFile = argv[1];
                    inputSuffix = "pos";
                    outputFile = argv[3];
                    negFiles = argv[2].split(";");
                    relevanceType = props.getProperty("FuseJet.Terminology.RelevanceType").trim();

                    if (props.containsKey("FuseJet.Terminology.Size")) {
                        try {
                            termSize = Integer.valueOf(props.getProperty("FuseJet.Terminology.Size"));
                        }
                        catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                    if (props.containsKey("FuseJet.Terminology.MaxPosCollectionSize")) {
                        try {
                            maxPosCollectionSize = Integer.valueOf(props.getProperty("FuseJet.Terminology.MaxPosCollectionSize"));
                        }
                        catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                    if (props.containsKey("FuseJet.Terminology.ToUpper")) {
                        try {
                            toUpper = Boolean.valueOf(props.getProperty("FuseJet.Terminology.ToUpper"));
                        }
                        catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                    if (props.containsKey("FuseJet.Terminology.ConcatSent")) {
                        try {
                            concatSent = Boolean.valueOf(props.getProperty("FuseJet.Terminology.ConcatSent"));
                        }
                        catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                    if (props.containsKey("FuseJet.Terminology.WriteStats")) {
                        try {
                            writeStats = Boolean.valueOf(props.getProperty("FuseJet.Terminology.WriteStats"));
                        }
                        catch (Exception e) {
                            System.err.println("Error: Unable to update writeStats");
                            e.printStackTrace();
                        }
                    }
                    if (props.containsKey("FuseJet.Terminology.ContextWindowSize")) {
                        try {
                            contextWindowSize = Integer.valueOf(props.getProperty("FuseJet.Terminology.ContextWindowSize"));
                        }
                        catch (Exception e) {
                            System.err.println("Error: Unable to update contextWindowSize");
                            e.printStackTrace();
                        }
                    }
                    if (props.containsKey("FuseJet.Terminology.UseDEStemmer")) {
                        try {
                            useDEStemmer = Boolean.valueOf(props.getProperty("FuseJet.Terminology.UseDEStemmer"));
                        }
                        catch (Exception e) {
                            System.err.println("Error: Unable to update useDEStemmer");
                            e.printStackTrace();
                        }
                    }
                    if (props.containsKey("FuseJet.Terminology.TermFilter")) {
                        String termFilterName = props.getProperty("FuseJet.Terminology.TermFilter");
                        termFilter = (TermFilter)Class.forName("FuseJet.Terminology." +
                                termFilterName).newInstance();
                        if (props.containsKey(termFilterName + ".ResourceInformation")) {
                            String[] resourceInformations = props.getProperty(termFilterName + ".ResourceInformation").split(";");
                            if ((resourceInformations.length > 1) || (resourceInformations[0].trim().length() > 0)) {
                                termFilter.initialize(resourceInformations);
                            }
                        }
                    }
                }
                else {
                    System.err.println("inputSuffix must be pos or chunk\n Please check:\n" + argv[2]+"\n"+
                            "posFileList \t posDir  \t" +
                            "negFileList \t negDir \t" +
                            "inputSuffix (pos or chunk) \t rankingListFile\t Relevance Type (IDF,TFIDF,DR,REL)\n" +
                            "System exiting...");
                    return;
                }
            }
        }
        catch (Exception e) {
            System.err.println("Error loading TerminologyExtractor:");
            e.printStackTrace();
            return;
        }

        System.err.println("[INFO] Start:"+getTimeStampString());
		TerminologyExtractor extractor;
        if (filterSetFileName.equals("")) {
            extractor = new TerminologyExtractor(posFile, negFiles, inputSuffix, outputFile, relevanceType);
        }
        else {
            Set<String> filterSet = new HashSet<String>();
            try {
                filterSet = readFilterSet(filterSetFileName);
            }
            catch (Exception e) {
                System.err.println();
            }
            extractor = new TerminologyExtractor(argv[0], new String[]{argv[1]}, argv[2],argv[3],argv[4], filterSet);
        }
        NPExtractor npExtractorCandidate = new NPExtractor(false);
        if (props.containsKey("FuseJet.Terminology.NPExtractor")) {
            try {
                String npExtractorName = props.getProperty("FuseJet.Terminology.NPExtractor");
                npExtractorCandidate = (NPExtractor)Class.forName("FuseJet.Terminology." +
                        npExtractorName).newInstance();
                extractor.setNpExtractor(npExtractorCandidate);
                System.err.println("[Info] NPExtractor: using " + npExtractorName);
            }
            catch (Exception e) {
                System.err.println("[Error] Unable to set NPExtractor");
                e.printStackTrace();
            }
        }
        if (props.containsKey("FuseJet.Terminology.MinOccurrence")) {
            String minOccurString = props.getProperty("FuseJet.Terminology.MinOccurrence");
            int minOccurrence = 4;
            try {
                if (minOccurString.contains(".")) {
                    minOccurrence = (int)Math.round(extractor.posExampleFileList.size() * Double.valueOf(minOccurString));
                }
                else {
                    minOccurrence = Integer.valueOf(minOccurString);
                }
                //extractor.pruneTerminology();
                extractor.setMinOccurrence(minOccurrence);
                System.err.println("[Info] MIN_OCCURRENCE updated to:" + minOccurrence);
            }
            catch (Exception e) {
                System.err.println("Failed to update MIN_OCCURRENCE: " + minOccurString);

            }
        }
        if (props.containsKey("FuseJet.Terminology.MinDocOccurrence")) {
            String minOccurString = props.getProperty("FuseJet.Terminology.MinDocOccurrence");
            int minDocOccurrence = 4;
            try {
                if (minOccurString.contains(".")) {
                    minDocOccurrence = (int)Math.round(extractor.posExampleFileList.size() * Double.valueOf(minOccurString));
                }
                else {
                    minDocOccurrence = Integer.valueOf(minOccurString);
                }
                //extractor.pruneDocTerminology();
                extractor.setMinDocOccurrence(minDocOccurrence);
                System.err.println("[Info] MIN_DOC_OCCURRENCE updated to:" + minDocOccurrence);
            }
            catch (Exception e) {
                System.err.println("[Error] Failed to update MIN_DOC_OCCURRENCE: " + minOccurString);

            }
        }
        extractor.extractTerms();
		List<Term> rankList = extractor.rankTerms();
        rankList = termFilter.filterTerm(rankList);
        TerminologyExamplesWriter writer = new TerminologyExamplesWriter(extractor.posExampleFileList,
                termSize,
                exampleSize,
                toUpper,
                concatSent);
        writer.setUseDEStemmer(useDEStemmer);
        writer.setWindowSize(contextWindowSize);
        if (!writeStats) {
            writer.write(rankList, extractor.outputFileName);
        }
        else {
            Term.writeTermsToFile(rankList, extractor.outputFileName);
        }
		//Term.writeTermsToFile(rankList, extractor.outputFileName);
        System.out.println("[INFO] End:"+getTimeStampString());
    }

    private static void updatePropVariables() {
        int i = 1;
        while (true) {
            if (props.containsKey("FuseJet.path" + i)) {
                String variableName = Pattern.quote("${FuseJet.path" + i + "}");
                //System.err.println(variableName);
                String variableValue = props.getProperty("FuseJet.path" + i);
                for (String key : props.stringPropertyNames()) {
                    props.put(key, props.getProperty(key).replaceAll(variableName, variableValue));
                }
                i++;
            } else {
                break;
            }
        }
    }

    private static Set<String> readFilterSet(String filterSetFileName) throws IOException {
        Set<String> result = new HashSet<String>();
        String[] lines = FuseJet.Utils.FuseUtils.readLines(filterSetFileName);

        for (String line : lines) {
            result.add(line.trim());
        }
        return result;
    }

	public TerminologyExtractor(String posList, String[] negLists,
                         String suffix, String outputFile, String rType) throws IOException{
		type = REL_TYPE.valueOf(rType);
		posExampleFileList = readList(posList, maxPosCollectionSize);
        negExampleFileList = new ArrayList<String>();
        for (String negList : negLists) {
            negExampleFileList.addAll(readList(negList));
        }
		inputSuffix = suffix;
		outputFileName = outputFile;
		if(inputSuffix.toLowerCase().equals("chunk"))
			npExtractor = new NPExtractor(true);
		else if(inputSuffix.toLowerCase().equals("pos"))
			npExtractor = new NPExtractor(false);
		else{
			return;
		}
		//extractTerms();
	}

    public void setNpExtractor(NPExtractor npExtractor) {
        this.npExtractor = npExtractor;
    }

    public void setMaxTermLength(int maxTermLength) {
        this.maxTermLength = maxTermLength;
    }

    public void setMinOccurrence(int minOccurrence) {
        this.minOccurrence = minOccurrence;
    }

    public void setMinDocOccurrence(int minDocOccurrence) {
        this.minDocOccurrence = minDocOccurrence;
    }

    public TerminologyExtractor(String posList, String[] negLists,
                                String suffix, String outputFile, String rType, Set<String> filterSet) throws IOException{
        type = REL_TYPE.valueOf(rType);
        posExampleFileList = readList(posList);
        negExampleFileList = new ArrayList<String>();
        for (String negList : negLists) {
            negExampleFileList.addAll(readList(negList));
        }
        inputSuffix = suffix;
        outputFileName = outputFile;
        if(inputSuffix.toLowerCase().equals("chunk"))
            npExtractor = new NPExtractor(true);
        else if(inputSuffix.toLowerCase().equals("pos"))
            npExtractor = new NPExtractor(false);
        else{
            return;
        }
        extractTerms(filterSet);
    }

    public void extractTerms(Set<String> filterSet) throws IOException{
        for(String fileID:negExampleFileList){
            String inputName;
            if(fileID.endsWith(".sgm")) {
                fileID = fileID.substring(0,fileID.length()-4);
                inputName = fileID+"."+inputSuffix;
            }
            else {
                inputName = fileID;
            }
            processDocument(inputName, false, filterSet);
        }
        System.err.println("[INFO] After reading negative examples:"+getTimeStampString());

        for(String fileID:posExampleFileList){
            String inputName;
            if(fileID.endsWith(".sgm")) {
                fileID = fileID.substring(0,fileID.length()-4);
                inputName = fileID+"."+inputSuffix;
            }
            else {
                inputName = fileID;
            }
            processDocument(inputName, true, filterSet);
        }
        System.err.println("[INFO] After reading positive examples:"+getTimeStampString());
        pruneTerminology();
    }

	public void extractTerms() throws IOException{
        for(String fileID:negExampleFileList){
            String inputName;
            if(fileID.endsWith(".sgm")) {
                fileID = fileID.substring(0,fileID.length()-4);
                inputName = fileID+"."+inputSuffix;
            }
            else {
                inputName = fileID;
            }
            try {
                processDocument(inputName, false);
            }
            catch (Exception e) {
                System.err.println("[INFO] Error processing file:" + inputName);
                e.printStackTrace();
            }
        }
        System.err.println("[INFO] After reading negative examples:" + getTimeStampString());
        System.err.println("[INFO] Positive examples:" + posExampleFileList.size());

        for(String fileID:posExampleFileList){
            String inputName;
            if(fileID.endsWith(".sgm")) {
                fileID = fileID.substring(0,fileID.length()-4);
                inputName = fileID+"."+inputSuffix;
            }
            else {
                inputName = fileID;
            }
            try {
                processDocument(inputName, true);
            }
			catch (Exception e) {
                System.err.println("[INFO] Error processing file:" + inputName);
                e.printStackTrace();
            }
		}
        System.err.println("[INFO] After reading positive examples:"+getTimeStampString());
		pruneTerminology();
	}

    private static String getTimeStampString() {
        Date now = new Date();
        SimpleDateFormat formatter = new SimpleDateFormat("EEE dd-MMM-yyyy HH:mm:ss");
        return formatter.format(now);
    }


	//this extracts chunks from xml file
	private void processDocument(String inputName, boolean rel)throws IOException{
		File f = new File(inputName);
		if(!f.exists()) {
            System.err.println("[ERROR] Error Reading: " + inputName);
            return;
        }
		//System.err.println("[INFO] Reading: " + inputName);
		addDocumentTerms(inputName, rel);
	}

    private void processDocument(String inputName, boolean rel, Set<String> filterSet)throws IOException{
        File f = new File(inputName);
        if(!f.exists()) {
            System.err.println("[ERROR] Error Reading: " + inputName);
            return;
        }
        //System.err.println("[INFO] Reading: " + inputName);
        addDocumentTerms(inputName, rel, filterSet);
    }


	public void addDocumentTerms(String inputName, boolean rel) throws IOException{
		Map<String, Integer> terms = npExtractor.extractNPFromDocument(inputName);
		for(String term:terms.keySet()){
			addTermFreq(term, terms.get(term), rel);
		}
	}

    public void addDocumentTerms(String inputName, boolean rel, Set<String> filterSet) throws IOException {
        Map<String, Integer> terms = npExtractor.extractNPFromDocumentRelaxed(inputName);
        for(String term:terms.keySet()){
            if (filterSet.contains(term)) {
                addTermFreq(term, terms.get(term), rel);
            }
        }
    }

	private void addTermFreq(String word, int freq, boolean positive){
		String[] tokens = word.split(" ");
		for(String token : tokens){
			if(positive)
				addWordToMap(token_rel, token, freq);
			addWordToMap(token_total, token, freq);
		}
		if(map.containsKey(word)){
			Term t = map.get(word);
			t.addFreq(freq, positive);
			map.put(word, t);
		}
		else{
			Term t= new Term(word);
			t.addFreq(freq, positive);
			map.put(word, t);
		}
	}	
	
	private void addWordToMap(Map<String, Integer> map, String word, int freq){
		if(map.containsKey(word))
			freq += map.get(word);
		map.put(word, freq);
	}

	public List<Term> rankTerms() throws IOException{
		List<Term> rankList = new ArrayList<Term>();
		for(Term t:map.values()){
			rankList.add(t);
		}
		Comparator<Term> comp = null;
		switch(type){
		case DR:
			comp = new DRComparator();
			break;
		case DRDC:
			comp = new DRDCComparator();
			break;
		case TFIDF:
			comp = new TFIDFComparator();
			break;
		case IDF:
			comp = new IDFComparator();
			break;
		case TokenDRDC:
			comp = new TokenDRDCComparator();
			break;
		case TokenIDF:
			comp = new TokenIDFComparator();
			break;
		default:
			System.err.println("Unknown ranking method "+type);
			System.exit(1);			
		}

		Collections.sort(rankList,comp);
		return rankList;
	}

	static public List<String> readList(String fileName)throws IOException{
		List<String> list = new ArrayList<String>();
		BufferedReader reader = new BufferedReader(new FileReader(fileName));
		String fileID;
		while((fileID = reader.readLine()) != null){
			list.add(fileID);			
		}
		return list;
	}

    static public List<String> readList(String fileName, int maxFiles)throws IOException{
        List<String> list = new ArrayList<String>();
        BufferedReader reader = new BufferedReader(new FileReader(fileName));
        String fileID;
        while((fileID = reader.readLine()) != null){
            list.add(fileID);
        }
        if (maxFiles == -1) {
            return list;
        }
        else {
            Random rand = new Random(1350266648297767L);
            Collections.shuffle(list, rand);
            List<String> results = new ArrayList<String>();
            if (maxFiles < list.size()) {
                results = list.subList(0, maxFiles);
            }
            else {
                results = list;
            }
            System.err.println("[Info] Collection size set to: " + results.size());
            return results;
        }
    }

    //prune the terminology whose relevance score is less than 10, and whose length is larger than 4.
	public void pruneTerminology(){
        System.err.println(String.format("[Info] Start to prune terms: maxTermLength:%d, minOccurrence:%d, minDocOccurrence:%d",
                maxTermLength, minOccurrence, minDocOccurrence));
		Iterator<String> iter = map.keySet().iterator();
        //int actualMinDocOccurrence = (int)Math.round(posExampleFileList.size() * 0.1);
        //if (actualMinDocOccurrence >= minDocOccurrence) {
        int actualMinDocOccurrence = minDocOccurrence;
        //}
        //else {
        //    System.err.println("[Info] RDG too small. minDocOccurrence reset to:" + actualMinDocOccurrence);
        //}
		while(iter.hasNext()){
			String word = iter.next();
			Term t = map.get(word);
			if(t.length > maxTermLength || t.getPosFreq()< minOccurrence ||
                    t.getPosDocFreq()< actualMinDocOccurrence){
				iter.remove();
			}
			else{
				t.calTokenDR(this);
			}
		}		
	}

    public void pruneDocTerminology(){
        Iterator<String> iter = map.keySet().iterator();
        while(iter.hasNext()){
            String word = iter.next();
            Term t = map.get(word);
            if(t.getPosDocFreq()< minDocOccurrence){
                iter.remove();
            }
            else{
                t.calTokenDR(this);
            }
        }
    }
}






