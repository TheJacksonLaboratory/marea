import click
import glob
import gzip
import re

from os import makedirs
from os.path import basename, join
from typing import Dict, List, Tuple

from filter_abstracts import PMID_INDEX, PUBYEAR_INDEX


def add_prefix(category: str, cid: str) -> str:
    if category == 'Gene':
        return 'NCBIGene:' + cid
    elif category == 'Species':
        return 'NCBITaxon:' + cid
    else:
        return cid


def build_pubtator(data_dir) -> Dict[str, Tuple[str, str, List[Tuple[int, int, str]]]]:
    annotations = {}
    pmid = title = abstract = ''
    total_len = 0
    t_pattern = re.compile(r'(\d+)\|t\|(.+)')   # matches title
    a_pattern = re.compile(r'(\d+)\|a\|(.*)')   # matches abstract, which might be empty
    c_pattern = re.compile(
        r'\d+\t(\d+)\t(\d+)\t[\S \n\r\f\v]+\t(DNAMutation|CellLine|Chemical|Disease|Gene|ProteinMutation|Species)\t(.*)$')
    e_pattern = re.compile('^$')
    with gzip.open(join(data_dir,
                        'bioconcepts2pubtatorcentral.offset.sample.gz')) as pc:
        for byteline in pc:
            line = byteline.decode()
            if e_pattern.match(line):
                concepts.sort()
                annotations[pmid] = (title, abstract, concepts)
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
    return annotations


def concept_line_ok(start: int, max_len: int, category: str, cid: str) -> bool:
    return start < max_len and \
           category not in {'DNAMutation', 'ProteinMutation'} and cid != ''


def replace(pmid: str,
            cr_dict: Dict[str, Tuple[str, str, List[Tuple[int, int, str]]]]) -> str:
    (title, abstract, concepts) = cr_dict[pmid]
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
@click.option('-p', type=click.Path(exists=True), required=True,
              help='directory of gzipped pubtator offset file')
@click.option('-r', type=click.Path(exists=True), required=True,
              help='directory of relevant abstracts')
@click.option('-o', type=click.Path(), required=True, help='output directory')
# python xml2txt.py -p ../data -r ../data/pubmed_rel -o ../data/pubmed_cr
def main(p, r, o):
    pubtator_dict = build_pubtator(p)
    files_to_process = glob.glob(join(r, '*.tsv'))
    makedirs(o, exist_ok=True)
    for f in files_to_process:
        click.echo(basename(f))
        with click.open_file(f) as infile:
            outfile_path = join(o,
                                basename(f).replace('_relevant.tsv', '_cr.tsv'))
            with click.open_file(outfile_path, 'w') as outfile:
                for line in infile:
                    fields = line.split()
                    pmid = fields[PMID_INDEX]
                    if pmid in pubtator_dict:
                        outfile.write('{}\t{}\t{}\n'.format(
                            pmid, fields[PUBYEAR_INDEX], replace(pmid, pubtator_dict)))

    # for k in sorted(pubtator_dict, key=lambda x: (len(x), x)):
    #     (t, a, cs) = pubtator_dict[k]
    #     print('PMID: {} title: {}'.format(k, t))
    #     print(a)
    #     for c in cs:
    #         print('\t{}'.format(c))


if __name__ == '__main__':
    main()
