import click
import re

from os import makedirs
from os.path import join
from typing import List, Set, Tuple

OFFSET_FILENAME = 'bioconcepts2pubtatorcentral.offset'
REPLACED_FILENAME = 'bioconcepts2pubtatorcentral.replaced'


def concept_line_ok(start: int, max_len: int, category: str, cid: str) -> bool:
    """
    :param start:    start offset for this concept in article
    :param max_len:  length in characters of title + abstract
    :param category: concept category (Chemical, Disease, Gene, Species, etc.)
    :param cid:      concept id (MeSH id, NCBI gene or taxon id, etc.)
    :return:         True if this line should result in concept replacement;
                     False otherwise
    """
    # Some articles in pubtator offset file have concept replacement info for the
    # full text; we are only interested in the title and abstract.
    # Skip over any replacement of Species 9606 (human).
    # Skip over any DNAMutation or ProteinMutation concept replacement.
    # Skip over any replacement that has no useful concept id.
    return start < max_len and \
           not (category == 'Species' and cid == '9606') and \
           not ('Mutation' in category or cid == '' or cid == '-' or cid == 'None')


def desired_concept(desired_concepts: Set[Tuple[str, str]],
                    category: str, cid: str) -> bool:
    """
    Check whether specified concept (MeSH id, NCBI gene or taxon id, etc.)
    is contained in desired_concepts.
    :param desired_concepts: set of (concept category, concept id) tuples
    :param category:         concept category (Chemical, Disease, Gene, Species, etc.)
    :param cid:              concept id (MeSH id, NCBI gene or taxon id, etc.)
    :return:                 True if (category, cid) tuple is a member of
                                  desired_concepts (or desired_concepts is None)
                             False otherwise
    """
    # Some concept ids in the PubTator offset file are actually a list of
    # multiple ids separated by semicolons, as in
    # 36414742	14048	14053	AE1/3	Gene	6521;6508
    # 36414742	17039	17047	CDKN2A/B	Gene	1029;1030
    # if any one of the multiple ids is in the set of desired concepts,
    # the entire list will be replaced
    cids = cid.split(';')
    return desired_concepts is None or \
        any((category, concept) in desired_concepts for concept in cids)


def fix_concept_id(category: str, cid: str) -> str:
    """
    Add prefix (if necessary) to concept id. Eliminate colons,
    e.g. in MESH:D015759. Pad id with one extra space before and after.
    :param category: concept category (Chemical, Disease, Gene, Species, etc.)
    :param cid:      concept id (MeSH id, NCBI gene or taxon id, etc.)
    :return:         fixed-up concept id
    """
    if category == 'Gene':
        return f' NCBIGene{cid} '
    elif category == 'SNP':
        return f' SNP{cid.lower()} '
    elif category == 'Species':
        return f' NCBITaxon{cid} '
    else:
        return f" {cid.replace(':', '')} "


def fix_concept_ids(category: str, cid: str) -> str:
    """
    Separate 'id2;id2' into multiple ids with the same prefix. Fix up each
    concept id and return the concatenation of all ids.
    :param category:  concept category (Chemical, Disease, Gene, Species, etc.)
    :param cid:       concept id or multiple concept ids separated by semicolon
    :return:          fixed-up concept id (or string of multiple ids)
    """
    cids = cid.split(';')
    return ''.join(map(lambda x: fix_concept_id(category, x), cids))


def read_concept_set(path) -> Set[Tuple[str, str]]:
    """
    Create set of (concept category, concept id) tuples by reading contents
    from specified file.
    :param path:  path to file containing one category, id pair per line
    :return:      set of (category, id) tuples read from file

    File format: no header, 2 fields per line, separated by a tab character
                 category<tab>id
    Concept categories and concept ids must match the contents of the
    bioconcepts2pubtatorcentral.offset file from PubTator Central
    """
    concept_set = set()
    with click.open_file(path) as concept_file:
        for line in concept_file:
            concept = line.split('\t')
            if len(concept) == 2:
                category = concept[0].strip()
                cid = concept[1].strip()
                concept_set.add((category, cid))
    return concept_set


def replace_all(input_dir, output_dir, desired_concepts: Set[Tuple[str, str]]) -> None:
    """
    Process all concept annotations in the pubtator offset file.
    :param input_dir:         directory of the pubtator offset file
    :param output_dir:        directory for output file
    :param desired_concepts:  set of (category, id) tuples for concepts to be replaced
    :return:                  None, side effect is to write output file
    """
    pmid = title = abstract = ''
    total_len = 0
    t_pattern = re.compile(r'(\d+)\|t\|(.+)')  # matches title
    a_pattern = re.compile(r'(\d+)\|a\|(.*)')  # matches abstract, which might be empty
    c_pattern = re.compile(
        r'\d+\t(\d+)\t(\d+)\t[\S \n\r\f\v]+\t(\w+)\t(.*)$')
    e_pattern = re.compile('^$')
    with click.open_file(join(input_dir, OFFSET_FILENAME)) as infile:
        with click.open_file(join(output_dir, REPLACED_FILENAME), 'w') as outfile:
            for line in infile:
                if e_pattern.match(line):
                    outfile.write('{}\t{}\n'.
                                  format(pmid, replace_one(title, abstract,
                                                           sorted(concepts))))
                else:
                    m = t_pattern.match(line)
                    if m:
                        pmid = m.group(1)
                        title = m.group(2)
                        # Separate title from abstract with a space.
                        if not title.endswith(' '):
                            title += ' '
                    else:
                        m = a_pattern.match(line)
                        if m:
                            abstract = m.group(2)
                            total_len = len(title) + len(abstract)
                            # Using set for the concept replacements instead of list because
                            # the PubtatorCentral offset file contains duplicate replacements
                            concepts = set()
                        else:
                            m = c_pattern.match(line)
                            if m:
                                start = int(m.group(1))
                                end = int(m.group(2))
                                category = m.group(3)
                                concept_id = m.group(4)
                                if desired_concept(desired_concepts, category, concept_id) \
                                   and concept_line_ok(start, total_len, category, concept_id):
                                    concepts.add((start, end,
                                                  fix_concept_ids(category, concept_id)))
                            else:
                                print('Line does not match any pattern:\n{}'.format(line))
    return None


def replace_one(title: str, abstract: str,
                concepts: List[Tuple[int, int, str]]) -> str:
    """
    Replace concepts in one PubMed article's title and abstract.
    :param title:     title string
    :param abstract:  abstract string
    :param concepts:  list of (start, end, concept_id) tuples
    :return:          string of title+abstract after replacements
    """
    all_text = ''.join([title, abstract])
    new_text = []
    current = 0
    for (start, end, cid) in sorted(concepts):
        new_text.append(all_text[current:start])
        new_text.append(cid)
        current = end
    new_text.append(all_text[current:])
    return ''.join(new_text)


@click.command()
@click.option('-i', type=click.Path(exists=True), required=True,
              help='directory of pubtator offset file')
@click.option('-o', type=click.Path(), help='output directory, defaults to input directory')
@click.option('-c', type=click.Path(exists=True),
              help='file of concepts to replace')
# python pubtate.py -i ../data/pubtator
# python pubtate.py -i ../data -o ../data/pubtator
def main(i, o, c):
    """
    For each entry in OFFSET_FILENAME, perform all concept replacements in
    title and abstract. Write result to REPLACED_FILENAME.
    :param i:  directory containing offset file
    :param o:  directory for output file
    :param c:  file of concept category, concept id pairs to replace
    :return:   none
    """
    if o is None:
        output_dir = i
    else:
        makedirs(o, exist_ok=True)
        output_dir = o
    if c is None:
        concept_set = None
    else:
        concept_set = read_concept_set(c)
    replace_all(i, output_dir, concept_set)


if __name__ == '__main__':
    main()
