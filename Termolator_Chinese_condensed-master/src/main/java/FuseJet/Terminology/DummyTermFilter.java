package FuseJet.Terminology;

import java.util.List;

/**
 * User: yhe
 * Date: 10/3/12
 * Time: 3:11 PM
 */
public class DummyTermFilter implements TermFilter {
    @Override
    public void initialize(String[] resourceInformation) {

    }

    @Override
    public List<Term> filterTerm(List<Term> termList) {
        return termList;
    }
}
