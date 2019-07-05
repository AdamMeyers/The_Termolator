import java.io.*;
import java.util.*;

/*Author: Leizhen Shi
Update Date: 08/16/2018
Information: Generating .pos tag and .tchunk files by reading outputs from Brandeis Chinese System
The format read by the program will be consistent to .out.txt file generated from Brandeis System

Rule:
Find a "NN" or "NP"
Look for if there is a "JJ", "JJS" or "JJR" before the noun phrase
If there is, the the adjective is "B"
Then keep looking for the noun phrases after the noun we found
 */

public class NounChunkerGenerator {
    public static void main (String[] args){
        try {
            //Modify the input directory to read data. This is for test purpose. Will update in later version
            BufferedReader br = new BufferedReader(new FileReader("./test.out.txt"));

            File posfile = new File("test.pos.txt");
            File tchunkfile = new File("test.tchunk.txt");
            posfile.createNewFile();
            tchunkfile.createNewFile();
            FileWriter posfileWriter = new FileWriter(posfile);
            FileWriter tchunkfileWriter = new FileWriter(tchunkfile);

            String CurrentLine;

            long counter = 1;

            long positionCounter = 0;

            ArrayList<Chunk> chunklist = new ArrayList<Chunk>();

            while ((CurrentLine = br.readLine()) != null){
                String[] lineInString = CurrentLine.split(" ");
                for (int i = 0; i < lineInString.length; i++){
                    //Generating POS Tag files
                    String[] wordProperty = lineInString[i].split("_");
                    long endCounter = counter + wordProperty[0].length() - 1;
                    posfileWriter.write(wordProperty[0] + "  |||  " + "S: " + counter + " " + "E: " + endCounter + "  " + "|||  " + wordProperty[1] + "\n");

                    //Store information to a list
                    Chunk chunk = new Chunk(wordProperty[0], wordProperty[1], positionCounter);
                    chunklist.add(chunk);
                    positionCounter ++;
                }
            }

            long BICounter = 0;

            for (int i = 0; i < positionCounter; i++){
                //For B and I Tags
                if (chunklist.get(i).getTag().equals("NN") || chunklist.get(i).getTag().equals("NP")){
                    //The case that the found NN is at the start of the text
                    if (i == 0){
                        chunklist.get(i).modifyBIOTag("B");
                        BICounter ++;
                    }

                    else{
                        if (BICounter == 0){
                            if (chunklist.get(i-1).getTag().equals("JJ") || chunklist.get(i-1).getTag().equals("JJR") || chunklist.get(i-1).getTag().equals("JJS")){
                                chunklist.get(i-1).modifyBIOTag("B");
                                chunklist.get(i).modifyBIOTag("I");
                                BICounter += 2;
                            }
                            else{
                                chunklist.get(i).modifyBIOTag("B");
                                BICounter ++;
                            }
                        }
                        else {
                            chunklist.get(i).modifyBIOTag("I");
                        }
                    }
                }
                else {
                    BICounter = 0;
                }
            }

            for (int j = 0; j < positionCounter; j++){
                tchunkfileWriter.write(chunklist.get(j).getWord() + "  " +chunklist.get(j).getWord() + "  " + chunklist.get(j).getTag() + "  " + chunklist.get(j).getBIOTag() + "\n");
            }

            posfileWriter.close();
        } catch (IOException  e){
            e.printStackTrace();
        }
    }
}

class Chunk{
    private String word;
    private String tag;
    private long position;
    private String BIOTag = "O";

    public Chunk(String word, String tag, long position){
        this.word = word;
        this.tag = tag;
        this.position = position;
    }

    public String getWord(){
        return word;
    }

    public String getTag(){
        return tag;
    }

    public long getPosition(){
        return position;
    }

    public String getBIOTag(){
        return BIOTag;
    }

    public void modifyWord (String word){
        this.word = word;
    }

    public void modifytag (String tag){
        this.tag = tag;
    }

    public void modifyPosition(long position){
        this.position = position;
    }

    public void modifyBIOTag(String BIOTag){
        this.BIOTag = BIOTag;
    }
}