import click
import glob
import re

from os import makedirs
from os.path import basename, join
from typing import Dict

from filter_abstracts import PMID_INDEX, PUBYEAR_INDEX


def make_relevant_dict(rel_dir) -> Dict[str, str]:
    """
    Create dictionary with key PMID, value publication year for all articles
    considered relevant.
    :param rel_dir: directory containing files of relevant PubMed articles.
    :return:        dictionary
    """
    relevant = {}
    files_to_process = glob.glob(join(rel_dir, '*.tsv'))
    for f in files_to_process:
        click.echo(basename(f))
        with click.open_file(f) as infile:
            for line in infile:
                fields = line.strip().split('\t')
                relevant[fields[PMID_INDEX]] = fields[PUBYEAR_INDEX]
    return relevant


def select_articles(pubtator_file, out_dir, relevant: Dict[str, str]) -> None:
    """
    Write output file containing PMID, publication year, and title+abstract
    with Pubtator Central concept replacements for all relevant articles.
    :param pubtator_file: path to file containing PubMed articles after concept
                          replacement
    :param out_dir:       directory for output file
    :param relevant:      dictionary mapping PMID to publication year for
                          relevant articles
    :return:              none (side effect is writing output file)
    """
    pattern = re.compile(r'^(\d+)\t(.+)$')
    with click.open_file(join(out_dir, 'pubmed_cr.tsv'), 'w') as outfile:
        with click.open_file(pubtator_file) as pfile:
            for line in pfile:
                m = pattern.match(line)
                if m:
                    pmid = m.group(1)
                    abstract = m.group(2)
                    if pmid in relevant:
                        outfile.write('{}\t{}\t{}\n'.format(
                            pmid, relevant[pmid], abstract))
                else:
                    raise ValueError('Unexpected format in pubtator file:\n{}'.format(line))


@click.command()
@click.option('-p', type=click.Path(exists=True), required=True,
              help='path to pubtator file with concepts replaced')
@click.option('-r', type=click.Path(exists=True), required=True,
              help='directory of relevant abstracts')
@click.option('-o', type=click.Path(), required=True, help='output directory')
# python replace_concepts.py -p ../data/bioconcepts2pubtatorcentral.replaced \
#        -r ../data/pubmed_rel -o ../data/pubmed_cr
def main(p, r, o):
    """
    Extract relevant articles from pre-computed file of PubMed titles and
    abstracts with Pubtator Central concept replacements.
    :param p: path to file containing PubMed titles and abstracts with concept ids
    :param r: directory containing files of PMID, publication year for relevant articles
    :param o: directory for output file of relevant articles with concept replacements
    :return: None
    """
    makedirs(o, exist_ok=True)
    rel_dict = make_relevant_dict(r)
    select_articles(p, o, rel_dict)


if __name__ == '__main__':
    main()
