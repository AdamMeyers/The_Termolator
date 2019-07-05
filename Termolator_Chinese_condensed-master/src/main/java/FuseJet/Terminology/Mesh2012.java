package FuseJet.Terminology;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.HashSet;
import java.util.Set;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

public class Mesh2012 {

	static String unicode = "utf-8";	
	Set<String> vocabulary = new HashSet<String>();

	/**
	 * @throws SAXException 
	 * @throws ParserConfigurationException 
	 * @throws IOException 
	 */
	public static void main(String[] args) throws ParserConfigurationException, SAXException, IOException{
		/*String meshfile = "/Users/shashaliao/Research/FUSE/data/Mesh2012.xml";
		String dicFile = "/Users/shashaliao/Research/FUSE/mesh_vocabulary.txt";*/
		String meshfile = args[0];
		String dicFile = args[1];
		buildVoc(meshfile,dicFile);
	}

	public static void buildVoc(String meshfile, String dicFile)throws ParserConfigurationException, SAXException, IOException{

		Mesh2012.buildVocabularyFromMesh(meshfile,dicFile);
	}

	Mesh2012(String vocFile) throws IOException{
		readVocabulary(vocFile);
	}

	public boolean containsTerm(String term){
		term = term.replace("-", " ");
		if(vocabulary.contains(term))
			return true;
		return false;
	}

	static public void buildVocabularyFromMesh(String filename, String dicFile) throws IOException, ParserConfigurationException, SAXException{
		String text = readFile(filename);
		if(text.length() == 0)return ;
		ByteArrayInputStream stream = new ByteArrayInputStream(text.getBytes());
		InputStream is = stream;
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
		DocumentBuilder builder = factory.newDocumentBuilder();	
		Document document = builder.parse(is);
		Element rootElement = document.getDocumentElement();	
		Set<String> voc = getTerms(rootElement);
		writeVocabulary(voc, dicFile);
	}

	/*static public Set<String> getTerms(Element rootElement){
		Set<String> voc = new HashSet<String>();
		NodeList list = rootElement.getElementsByTagName("Term");
		for(int i=0;i<list.getLength();i++){
			Element tNode = (Element)list.item(i);
			Node strNode = tNode.getElementsByTagName("String").item(0);
			String term = strNode.getTextContent();
			voc.add(term);
		}
		return voc;
	}*/
	
	static public Set<String> getTerms(Element rootElement){
		Set<String> voc = new HashSet<String>();
		NodeList list = rootElement.getElementsByTagName("String");
		for(int i=0;i<list.getLength();i++){
			Element tNode = (Element)list.item(i);
			String term = tNode.getTextContent();
			voc.add(term.toLowerCase().trim());
		}
		return voc;
	}

	static private String readFile(String filename) {
		String templetContent = "";
		try {
			FileInputStream fileinputstream = new FileInputStream(filename);
			int length = fileinputstream.available();
			byte[] bytes = new byte[length];
			fileinputstream.read(bytes);
			fileinputstream.close();
			templetContent = new String(bytes);
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return templetContent;
	}

	static public void writeVocabulary(Set<String> voc, String dicFile) throws IOException{
		BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(dicFile),unicode));
		for(String term:voc){
			writer.write(term.toLowerCase()+"\n");
		}
		writer.close();
	}

	public void readVocabulary(String dicFile) throws IOException{
		BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(dicFile),unicode));
		String line ;
		while((line = reader.readLine()) != null){
			vocabulary.add(line.toLowerCase().replace("-", " "));
			int pos = line.indexOf(",");
			if(pos >0){
				String term = line.substring(pos+1)+" "+line.substring(0,pos);
				vocabulary.add(term.toLowerCase().replace("-", " "));
			}
		}
		reader.close();
	}

}
