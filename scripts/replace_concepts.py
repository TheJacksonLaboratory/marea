import click
import glob

from os import makedirs
from os.path import basename, join
from typing import Dict

from fetch_pubtator import pubtate_list, PTC_LIMIT
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


def process_articles(out_dir, relevant: Dict[str, str]) -> None:
    i = len(relevant)
    key_list = list(relevant.keys())
    current = 0
    remaining = len(key_list)
    with click.open_file(join(out_dir, 'pubmed_crt2.tsv'), 'w') as outfile:
        while remaining > 0:
            limit = min(remaining, PTC_LIMIT)
            print(key_list[current:current+limit])
            for (pmid, title_abstract) in pubtate_list(key_list[current:current+limit]):
                # output pmid, publication date, and text with concepts replaced
                outfile.write('{}\t{}\t{}\n'.
                              format(pmid, relevant[pmid], title_abstract))
            current += limit
            remaining -= limit


@click.command()
@click.option('-r', type=click.Path(exists=True), required=True,
              help='directory of relevant abstracts')
@click.option('-o', type=click.Path(), required=True, help='output directory')
# python replace_concepts.py -r ../data/pubmed_rel -o ../data/pubmed_cr
def main(r, o):
    makedirs(o, exist_ok=True)
    rel_dict = make_relevant_dict(r)
    process_articles(o, rel_dict)


if __name__ == '__main__':
    main()
