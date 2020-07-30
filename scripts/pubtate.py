import click
import re

from os import makedirs
from os.path import join
from typing import List, Tuple


def add_prefix(category: str, cid: str) -> str:
    if category == 'Gene':
        return 'NCBIGene:' + cid
    elif category == 'Species':
        return 'NCBITaxon:' + cid
    else:
        return cid


def replace_all(input_dir, output_dir) -> None:
    pmid = title = abstract = ''
    total_len = 0
    t_pattern = re.compile(r'(\d+)\|t\|(.+)')   # matches title
    a_pattern = re.compile(r'(\d+)\|a\|(.*)')   # matches abstract, which might be empty
    c_pattern = re.compile(
        r'\d+\t(\d+)\t(\d+)\t[\S \n\r\f\v]+\t(\w+)\t(.*)$')
    #         r'\d+\t(\d+)\t(\d+)\t[\S \n\r\f\v]+\t(
    #         DNAMutation|CellLine|Chemical|Disease|Gene|ProteinMutation|Species)\t(.*)$')
    e_pattern = re.compile('^$')
    with click.open_file(join(input_dir,
                              'bioconcepts2pubtatorcentral.offset')) as infile:
        with click.open_file(join(output_dir,
                                  'bioconcepts2pubtatorcentral.replaced'), 'w') as outfile:
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
                    else:
                        m = a_pattern.match(line)
                        if m:
                            abstract = m.group(2)
                            total_len = len(title) + len(abstract)
                            concepts = []
                        else:
                            m = c_pattern.match(line)
                            if m:
                                start = int(m.group(1))
                                end = int(m.group(2))
                                category = m.group(3)
                                concept_id = m.group(4)
                                if concept_line_ok(start, total_len, category, concept_id):
                                    concepts.append((start, end, add_prefix(category, concept_id)))
                            else:
                                print('Line does not match any pattern:\n{}'.format(line))
    return None


def concept_line_ok(start: int, max_len: int, category: str, cid: str) -> bool:
    return start < max_len and \
           category in {'CellLine', 'Chemical', 'Disease', 'Gene', 'Species'} and \
           cid != ''


def replace_one(title: str, abstract: str,
                concepts: List[Tuple[int, int, str]]) -> str:
    all_text = ''.join([title, abstract])
    new_text = []
    current = 0
    for (start, end, cid) in concepts:
        new_text.append(all_text[current:start])
        new_text.append(cid)
        current = end
    new_text.append(all_text[current:])
    return ''.join(new_text)


@click.command()
@click.option('-i', type=click.Path(exists=True), required=True,
              help='directory of pubtator offset file')
@click.option('-o', type=click.Path(), help='output directory, defaults to input directory')
# python pubtate.py -i ../data/pubtator
# python pubtate.py -i ../data -o ../data/pubtator
def main(i, o):
    if o is None:
        output_dir = i
    else:
        makedirs(o, exist_ok=True)
        output_dir = o
    replace_all(i, output_dir)


if __name__ == '__main__':
    main()
