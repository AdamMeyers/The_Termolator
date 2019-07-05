package FuseJet.Terminology;

import java.util.List;

/**
 * User: yhe
 * Date: 10/2/12
 * Time: 4:20 PM
 */
public interface TermFilter {
    public void initialize(String[] resourceInformation);
    public List<Term> filterTerm(List<Term> termList);
}
