import requests


def filter_name_by_websearch(lemma):
        try:
                response = requests.get(
                        'https://api.case.law/v1/cases/?page_size=10000&name=' + lemma,
                        headers={'Authorization': '75985a5f356905ed74fa631f1a44962852bad577'}
                )
                cases = response.json()
                for case in cases['results']:
                        case_name = case['name_abbreviation'].lower()
                        if lemma in case_name:
                                return True
                return False
        except:
                print(lemma,'caused a bug in filter_name_by_websearch')
                return False
