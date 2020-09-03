import click
import glob
import re

from os import makedirs
from os.path import basename, join

from my_lemmatizer import MyLemmatizer
from nlp_utils import nltk_setup
from query_mesh import merge_descendants
from typing import Dict, List, Set

# fields in the .txt file created by xml2txt.py
PMID_INDEX = 0
PUBYEAR_INDEX = 1
DESCRIPTORS_INDEX = 2
KEYWORDS_INDEX = 3
ABSTRACT_INDEX = -1


def check_descriptors(ctx, param, value: List[str]) -> List[str]:
    """
    Check format of each MeSH descriptor passed as command line argument. Raise
    exception if any has incorrect format.
    :param ctx: required for click callback feature
    :param param: required for click callback feature
    :param value: tuple of MeSH descriptors as written on command line
    :return: value if all descriptors are correctly formatted
    """
    for des in value:
        if not re.fullmatch(r'D(\d{6}|\d{9})', des):
            raise click.BadParameter(
                'Descriptor %s incorrect, should be D followed by 6 or 9 digits'
                % des, param_hint='MeSH DESCRIPTORS')
    return value


def extract_descriptors(descriptor_str: str) -> Dict[str, bool]:
    """
    Convert a string of MeSH descriptors to a dictionary (skip over the labels).
    String has the form (but all on one line):
        D000900 Anti-Bacterial Agents N | D001424 Bacterial Infections N |
        D004352 Drug Resistance, Microbial N | D006801 Humans N |
        D019966 Substance-Related Disorders N
    :param descriptor_str: MeSH descriptors for PubMed abstract
    :return: dictionary mapping MeSH identifier to boolean is this descriptor a
             major topic for this abstract
    """
    retval = {}
    descriptors = descriptor_str.split(' | ')
    for des in descriptors:
        des_parts = des.split()
        retval[des_parts[0]] = des_parts[-1].upper() == 'Y'
    return retval


def extract_keywords(lemmatizer: MyLemmatizer,
                     keyword_str: str) -> Dict[str, bool]:
    """
    Convert a string of keywords to a dictionary.
    String has the form (but all on one line):
        Aging-related tau astrogliopathy (ARTAG) N | Astrocytes N |
        Atypical Alzheimer disease N | Clinical heterogeneity N | Tau N
    :param lemmatizer:  MyLemmatizer object
    :param keyword_str: keywords for PubMed article
    :return: dictionary mapping each keyword (or keyword phrase), in lowercase,
             to boolean is this keyword a major topic for this abstract
    """
    retval = {}
    kwd_segments = keyword_str.split(' | ')
    for kwd_segment in kwd_segments:
        kwds = kwd_segment[:-2].lower()
        major = kwd_segment[-1].upper() == 'Y'
        retval[lemmatizer.lemmatize_seq(kwds)] = major
    return retval


def find_relevant_abstracts(in_file, out_path, major_topic: bool,
                            search_dict: Dict[str, Set[str]]):
    """
    Filter PubMed articles from input according to MeSH descriptors/keywords
    and major topic flag; write PMID, publication date, and abstract of
    relevant articles to output file.
    :param in_file: input file of PubMed id, year, descriptors, abstract
    :param out_path: path to output directory
    :param major_topic: boolean, if true only consider major topic descriptors
    :param search_dict: mapping of MeSH descriptor to set of synonyms for MeSH
                        descriptors user gave as search terms
    :return: None
    """
    lem = MyLemmatizer()
    # Each value in search_dict is a set of labels for the MeSH descriptor;
    # want to flatten to one big set, convert to lowercase and lemmatize
    search_keywords = {lem.lemmatize_seq(elt.lower()) for subset in
                       search_dict.values() for elt in subset}
    with click.open_file(in_file) as unfiltered_file:
        outfile_path = join(out_path,
                            basename(in_file).replace('.txt', '_relevant.tsv'))
        with click.open_file(outfile_path, 'w') as filtered_file:
            for line in unfiltered_file:
                segments = line.split('##')
                descriptor_str = segments[DESCRIPTORS_INDEX]
                keyword_str = segments[KEYWORDS_INDEX]
                abstract = segments[ABSTRACT_INDEX].strip()
                # check whether this line contains an abstract
                if abstract != '':
                    relevant = False
                    # does article have MeSH descriptors?
                    if descriptor_str != '':
                        article_descriptors = extract_descriptors(descriptor_str)
                        relevant = is_relevant(article_descriptors,
                                               set(search_dict.keys()), major_topic)
                    # if no relevant descriptors, does article have keywords?
                    if not relevant and keyword_str != '':
                        article_keywords = extract_keywords(lem, keyword_str)
                        # Ignore value of major_topic because almost all keywords
                        # are marked N for not major_topic
                        relevant = is_relevant(article_keywords, search_keywords,
                                               False)
                    # record relevant abstract in output file
                    if relevant:
                        filtered_file.write('{}\t{}\t{}\n'.format(
                            segments[PMID_INDEX], segments[PUBYEAR_INDEX], abstract))


def is_relevant(article_dict: Dict[str, bool], search_set: Set[str],
                major_bool: bool) -> bool:
    """
    Determine whether article is relevant w.r.t. the desired MeSH
    descriptors/keywords. Since descriptors and keywords are both
    represented as strings, this function handles either type of search set.
    Article considered relevant if there is any overlap between its
    descriptors/keywords and the set of desired descriptors/keywords.
    If major topic flag is True, consider only those descriptors/keywords
    marked as major topic for this article.
    :param article_dict: maps each MeSH descriptor/keyword to boolean flag
                         indicating major topic
    :param search_set: set of descriptors/keywords that user specified as relevant
    :param major_bool: if true, consider only article's major topics
    :return: True if this article is relevant, False otherwise
    """
    article_set = set(article_dict.keys())
    if major_bool:
        # Keep only the descriptors/keywords that are marked as major topics
        # Note: some entries in the input files have no descriptors marked as
        # major topics for the article; this probably means that one of the
        # qualifiers on the descriptor is marked as a major topic. We do not
        # extract qualifiers from the .xml file. Also, most keywords are
        # marked N so it is not very useful to filter keywords by their major
        # topic flag, the result will likely be an empty set.
        article_set = set(filter(lambda d: article_dict[d], article_set))
    return not search_set.isdisjoint(article_set)


@click.command()
@click.option('-i', type=click.Path(exists=True), required=True, help='input directory')
@click.option('-n', type=click.Path(), required=True, help='directory for nltk data')
@click.option('-o', type=click.Path(), required=True, help='output directory')
@click.option('-m', is_flag=True, flag_value=True, help='filter on major topics only')
@click.argument('descriptors', callback=check_descriptors, metavar='MeSH_DESCRIPTORS', nargs=-1)
# python filter-abstracts.py -i ../data/pubmed_txt -n ../data/nltk_data \
#        -o ../data/pubmed_relevant -m D005796 D009369 D037102
def main(i, n, o, descriptors: List[str], m: bool):
    """
    Filters each .txt file from input directory by MeSH descriptors/keywords.
    Writes PMID and publication year of relevant articles to corresponding
    output file.
    """
    files_to_parse = glob.glob(join(i, '*.txt'))
    nltk_setup(n)
    makedirs(o, exist_ok=True)
    mesh_dict = merge_descendants(descriptors)
    for f in files_to_parse:
        find_relevant_abstracts(f, o, m, mesh_dict)
        click.echo(basename(f))


if __name__ == '__main__':
    main()
