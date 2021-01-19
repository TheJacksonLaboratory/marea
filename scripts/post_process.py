import click
import glob
import re

from os import makedirs
from os.path import basename, join
from typing import Dict

from filter_abstracts import PMID_INDEX, PUBYEAR_INDEX
from pubtate import REPLACED_FILENAME
from text_post_processor import TextPostProcessor

OUT_FILENAME = 'pubmed_cr.tsv'


def make_relevant_dict(rel_dir) -> Dict[str, str]:
    """
    Create dictionary with key PMID, value publication year for all articles
    considered relevant.
    :param rel_dir: directory containing files of relevant PubMed articles.
    :return:        dictionary
    """
    relevant = {}
    files_to_process = glob.glob(join(rel_dir, '*.tsv'))
    files_to_process.sort()
    for f in files_to_process:
        click.echo(basename(f))
        with click.open_file(f) as infile:
            for line in infile:
                fields = line.strip().split('\t')
                relevant[fields[PMID_INDEX]] = fields[PUBYEAR_INDEX]
    return relevant


def select_articles(pubtator_file, nltk_dir, out_dir,
                    relevant: Dict[str, str]) -> None:
    """
    Write output file containing PMID, publication year, and title+abstract
    with Pubtator Central concept replacements for all relevant articles.
    :param pubtator_file: path to file containing PubMed articles after concept
                          replacement
    :param nltk_dir:      directory containing nltk data
    :param out_dir:       directory for output file
    :param relevant:      dictionary mapping PMID to publication year for
                          relevant articles
    :return:              none (side effect is writing output file)
    """
    pattern = re.compile(r'^(\d+)\t(.+)$')
    tpp = TextPostProcessor(nltk_dir)
    with click.open_file(join(out_dir, OUT_FILENAME), 'w') as outfile:
        with click.open_file(pubtator_file) as pfile:
            for line in pfile:
                m = pattern.match(line)
                if m:
                    pmid = m.group(1)
                    title_abstract = m.group(2)
                    if pmid in relevant:
                        cleaned_up = tpp.process_phrase(title_abstract)
                        # in case the title+abstract consists solely of
                        # punctuation and stop words, check the length
                        if cleaned_up != '':
                            outfile.write('{}\t{}\t{}\n'.format(
                              pmid, relevant[pmid], cleaned_up))
                else:
                    raise ValueError('Unexpected format in pubtator file:\n{}'.
                                     format(line))


@click.command()
@click.option('-p', type=click.Path(exists=True), required=True,
              help='directory of pubtator file with concepts replaced')
@click.option('-r', type=click.Path(exists=True), required=True,
              help='directory of relevant abstracts')
@click.option('-n', type=click.Path(), required=True, help='directory for nltk data')
@click.option('-o', type=click.Path(), required=True, help='output directory')
# python post_process.py -p ../data/pubtator -r ../data/pubmed_rel \
#        -n ../data/nltk_data -o ../data/pubmed_cr
def main(p, r, n, o):
    """
    Extract relevant articles from pre-computed file of PubMed titles and
    abstracts with Pubtator Central concept replacements.
    :param p: path to file containing PubMed titles and abstracts with concept ids
    :param r: directory containing files of PMID, publication year for relevant articles
    :param n: directory containing nltk data
    :param o: directory for output file of relevant articles with concept replacements
    :return: None
    """
    makedirs(o, exist_ok=True)
    rel_dict = make_relevant_dict(r)
    select_articles(join(p, REPLACED_FILENAME), n, o, rel_dict)
    click.echo('Highest relevant PMID is {}'.format(max(rel_dict.keys(), key=int)))


if __name__ == '__main__':
    main()
