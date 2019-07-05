package FuseJet.Terminology;
import java.io.IOException;
import java.util.List;

public class JetNPParser implements NPParser{


	public static void main(String[] args) throws IOException{

	}

	@Override
	public List<NounPhrase> NPParse(String filename) throws IOException {	
		/*List<NounPhrase> nouns = new ArrayList<NounPhrase>();
		String tmp = readFile(filename, "utf-8");
		if(tmp.length() == 0)return null;
		ByteArrayInputStream stream = new ByteArrayInputStream(tmp.getBytes());
		InputStream is = stream;
		try{
			DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
			DocumentBuilder builder = factory.newDocumentBuilder();	
			Document document = builder.parse(is);
			Element rootElement = document.getDocumentElement();
			NodeList npnodes = rootElement.getElementsByTagName("np");
			if(npnodes.getLength() == 0)
				return null;
			for(int i=0;i<npnodes.getLength();i++){
				Node npnode = npnodes.item(i);
				String np = npnode.getTextContent();
				nouns.add(np);
			}
		}
		catch (ParserConfigurationException e){
			e.printStackTrace();
		} catch (SAXException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return nouns;*/
		return null;
	}


	/*private String readFile(String filename, String unicode) {
		String templetContent = "";
		try {
			FileInputStream fileinputstream = new FileInputStream(filename);
			int length = fileinputstream.available();
			byte[] bytes = new byte[length];
			fileinputstream.read(bytes);
			fileinputstream.close();
			templetContent = new String(bytes, unicode);
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return templetContent;
	}*/

}
