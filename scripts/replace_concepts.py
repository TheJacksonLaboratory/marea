import click
import glob
import re

from os import makedirs
from os.path import basename, join
from typing import Dict

from filter_abstracts import PMID_INDEX, PUBYEAR_INDEX


def make_relevant_dict(rel_dir) -> Dict[str, str]:
    relevant = {}
    files_to_process = glob.glob(join(rel_dir, '*.tsv'))
    for f in files_to_process:
        click.echo(basename(f))
        with click.open_file(f) as infile:
            for line in infile:
                fields = line.split('\t')
                relevant[fields[PMID_INDEX]] = fields[PUBYEAR_INDEX]
    return relevant


def select_articles(pubtator_file, out_dir, relevant: Dict[str, str]) -> None:
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
    makedirs(o, exist_ok=True)
    rel_dict = make_relevant_dict(r)
    select_articles(p, o, rel_dict)


if __name__ == '__main__':
    main()
