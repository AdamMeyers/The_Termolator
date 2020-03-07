import java.io.*;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.*;


//USER INPUT: file containing list of all foreground files (having been chunked by TreeTagger)

public class getNounChunks {
	
	public static void main(String[] args)  throws FileNotFoundException, UnsupportedEncodingException, IOException {
		boolean start = false;
		boolean endNP = false;
		boolean APstart = false;
		
		//open file
		String inname = args[0];
		
		File in = new File(inname);	
		String[] dirnamesplit = inname.split("\\.");
		Scanner read = new Scanner(in, "UTF-8");
	
		
		//new dir file to write all new terms files to
		String outname = dirnamesplit[0] + ".chunklist";
		OutputStreamWriter listwrite = new OutputStreamWriter(new FileOutputStream(outname), Charset.forName("UTF-8").newEncoder());
		
		//for every line in input file aka for every doc
		while (read.hasNextLine()) {
			
			//extract docname from list 
			//remove path components and ext
			
			
			String fulldocname = read.nextLine();
			//System.out.println("This line: " + fulldocname);
			//System.out.println(fulldocname.charAt(0));
			
			if (fulldocname.equals("")) {
		 		continue;

			}
			
			//identify if first character of file is a weird char due to encoding 
			if ((fulldocname.length() != 0) && !Character.isLetterOrDigit(fulldocname.charAt(0))) {
				//System.out.println("y");
				fulldocname = fulldocname.substring(1);
			}
			
		    String[] namesplit = fulldocname.split("/|\\.");
			//System.out.println("Split name: " + Arrays.deepToString(namesplit));	
			String docname = namesplit[namesplit.length - 2];
			//System.out.println("Bare doc name: " + docname);
			String pathname = "";
			
			for (int i = 0; i < namesplit.length - 2; i++) {
				pathname += (namesplit[i] + "/");
			}
			
			//System.out.println("Path name: " + pathname);
			String ext = namesplit[namesplit.length - 1];
			//System.out.println("Extension: " + ext);
			
			File thisdoc = new File(fulldocname);	
			Scanner doc = new Scanner(thisdoc, "UTF-8");		
			OutputStreamWriter writer = new OutputStreamWriter(new FileOutputStream(pathname + docname + ".chunks"), Charset.forName("UTF-8").newEncoder());
			
			start = false;
			endNP = false;
			APstart = false;	
			
			String chunk = "";
			String[] thisLine;
			
			while(doc.hasNextLine()) {
				
				thisLine = doc.nextLine().split("\t");
				
				
				//write to file if have endNP and APstart
				if (thisLine[0].equals("</AP>")) {
					
					APstart = false;
					
					//remove trailing punctuation
					if (chunk.length() > 1 && !Character.isLetter(chunk.charAt(chunk.length()-1))) {
						chunk = chunk.substring(0, chunk.length()-1);
					}
					//remove bugs from nounchunker
					else if (chunk.length() > 5 && chunk.substring(chunk.length()-5).equals("et/ou")){
						chunk = chunk.substring(0, chunk.length()-5);
					}
					
					//System.out.println(chunk);
					
					if (!chunk.isEmpty()) {
						writer.write(chunk + "\r\n");
					}
									
					chunk = "";				
					endNP = false;
				}
				
						
				if (thisLine[0].equals("</NP>")) {
					start = false;
					endNP = true;
					continue;
				}
				
				
				if (start || APstart) {
					if (thisLine[0].length() == 1) {
						
						if (Character.isLetter(thisLine[0].charAt(0))) {
							chunk = chunk.concat(" " + thisLine[0]);
						}
					}
					else {
						chunk = chunk.concat(thisLine[0] + " ");
					}
					
				}
				
				if (thisLine[0].equals("<NP>")) {
					start = true;
					endNP = false;
				}
				
				if (thisLine[0].equals("<AP>")) {
					if (endNP) {
						APstart = true;
					}
				}
				
				if (endNP) {
					if (!APstart) { //no AP: write
						//remove trailing punctuation
						if (chunk.length() > 1 && !Character.isLetter(chunk.charAt(chunk.length()-1))) {
							chunk = chunk.substring(0, chunk.length()-1);
						}
						//remove bugs from nounchunker
						else if (chunk.length() > 5 && chunk.substring(chunk.length()-5).equals("et/ou")){
							chunk = chunk.substring(0, chunk.length()-5);
						}
						
						//System.out.println(chunk);
						
						if (!chunk.isEmpty()) {
							writer.write(chunk + "\r\n");
						}
						
						
						chunk = "";
						
						endNP = false;
					}
					
				}
				
				
				
				
			}
			
			writer.flush();
			writer.close();
			doc.close();
			
			//write new chunk file name to dir file
			listwrite.write(pathname + docname +".chunks");
			listwrite.write("\n");
			
		}	
		
		listwrite.flush();
		listwrite.close();
		read.close();
		
	}
}
