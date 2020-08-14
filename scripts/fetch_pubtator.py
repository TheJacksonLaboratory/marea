import re
import requests

from typing import List, Tuple
from time import sleep

PTC_LIMIT = 1000


def add_prefix(category: str, cid: str) -> str:
    if category == 'Gene':
        return 'NCBIGene:' + cid
    elif category == 'SNP':
        return 'SNP:' + cid.lower()
    elif category == 'Species':
        return 'NCBITaxon:' + cid
    else:
        return cid


def pubtate_list(pmid_list: List[str]) -> List[Tuple[str, str]]:
    num_pmids = len(pmid_list)
    if 0 < num_pmids <= PTC_LIMIT:
        r = requests.post(
            "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/pubtator",
            json={'pmids': pmid_list})
        if r.status_code == requests.codes.ok:
            # limit on requests per second not specified on PubtatorCentral website
            sleep(5)
            return parse_articles(r.text, num_pmids)
        else:
            r.raise_for_status()
    else:
        raise ValueError('pubtate_list: Cannot fetch {} pmids, must be between 1 and {}}.'.
                         format(num_pmids, PTC_LIMIT))


def parse_articles(ptc_return: str, num_articles: int) -> List[Tuple[str, str]]:
    # the method should parse the body, replace concepts, and return a list of tuples
    # (pmid, title_abstract) where both title and abstract have concepts replaced
    pmid = title = abstract = ''
    t_pattern = re.compile(r'(\d+)\|t\|(.+)')   # matches title
    a_pattern = re.compile(r'(\d+)\|a\|(.*)')   # matches abstract, which might be empty
    c_pattern = re.compile(
        r'\d+\t(\d+)\t(\d+)\t[\S \n\r\f\v]+\t(\w+)\t(.*)$')
    e_pattern = re.compile('^$')
    retval = concepts = []
    count_parsed = 0
    for line in ptc_return.splitlines(keepends=True):
        if e_pattern.match(line):
            count_parsed += 1
            if abstract != '':
                retval.append((pmid, replace_one(title+abstract, sorted(concepts))))
        else:
            m = t_pattern.match(line)
            if m:
                pmid = m.group(1)
                title = m.group(2)
                if not title.endswith(' '):
                    title += ' '
            else:
                m = a_pattern.match(line)
                if m:
                    abstract = m.group(2)
                    concepts = []
                else:
                    m = c_pattern.match(line)
                    if m:
                        start = int(m.group(1))
                        end = int(m.group(2))
                        category = m.group(3)
                        concept_id = m.group(4)
                        if concept_line_ok(category, concept_id):
                            concepts.append((start, end, add_prefix(category, concept_id)))
                    else:
                        print('parse_articles: Line does not match any pattern:\n{}'.
                              format(line))
    if num_articles == count_parsed:
        return retval
    else:
        raise ValueError('parse_articles: looking for {} articles, parsed {} instead.'.
                         format(num_articles, count_parsed))


def concept_line_ok(category: str, cid: str) -> bool:
    return not (category == 'DomainMotif' or 'Mutation' in category
                or cid == '' or cid == '-')


def replace_one(text: str, concepts: List[Tuple[int, int, str]]) -> str:
    new_text = []
    current = 0
    for (start, end, cid) in concepts:
        new_text.append(text[current:start])
        new_text.append(cid)
        current = end
    new_text.append(text[current:])
    return ''.join(new_text)


def main():
    payload = {'pmids': ['15055594', '22298231', '6330977', '28121313', '32229322']}
    # payload = {'pmids': ['61552', '61568', '61580', '61588', '61608', '61637', '61639', '61657', '61661', '61690',
    # '61702', '61713', '61720', '61727', '61730']}
    r = requests.post("https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/pubtator",
                      json=payload)
    print(r.text)
    # with open('../data/pubmed_cr/tryapi.txt', 'w') as outfile:
    #     outfile.write(r.text)


if __name__ == '__main__':
    main()
