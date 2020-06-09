import click
import glob
import re

from os import makedirs
from os.path import basename, join
from query_mesh import get_descendants

# fields in the .txt file created by xml2txt.py
PMID_INDEX = 0
PUBYEAR_INDEX = 1
DESCRIPTORS_INDEX = 2
# KEYWORDS_INDEX = 3
ABSTRACT_INDEX = -1


def check_descriptors(ctx, param, value):
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


def extract_descriptors(descriptor_str):
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


def find_relevant_abstracts(in_file, out_path, major_topic, desired_descriptors):
    """
    Filter PubMed articles from input according to MeSH descriptors and major
    topic flag; write PMID, publication date, and abstract of relevant articles
    to output file.
    :param in_file: input file of PubMed id, year, descriptors, abstract
    :param out_path: path to output directory
    :param major_topic: boolean, if true only consider major topic descriptors
    :param desired_descriptors: list of MeSH descriptor ids
    :return: None
    """
    with click.open_file(in_file) as unfiltered_file:
        outfile_path = join(out_path,
                            basename(in_file).replace('.txt', '_relevant.tsv'))
        with click.open_file(outfile_path, 'w') as filtered_file:
            for line in unfiltered_file:
                segments = line.split('##')
                abstract = segments[ABSTRACT_INDEX].strip()
                descriptor_str = segments[DESCRIPTORS_INDEX]
                # check whether this line contains an abstract and descriptors
                # TODO: handle articles that have keywords but no descriptors
                if abstract != '' and descriptor_str != '':
                    # check whether the abstract meets relevancy criteria
                    abstract_descriptors = extract_descriptors(descriptor_str)
                    if is_relevant(abstract_descriptors, desired_descriptors,
                                   major_topic):
                        # record relevant abstract in output file
                        filtered_file.write('{}\t{}\t{}\n'.format(segments[PMID_INDEX],
                                                                  segments[PUBYEAR_INDEX],
                                                                  abstract))


def is_relevant(abstract_dict, desired_list, major_bool):
    """
    Determine whether abstract is relevant w.r.t. the desired MeSH descriptors.
    Abstract considered relevant if one of its descriptors is on the list of
    desired descriptors. If major topic flag is set, consider only those
    descriptors marked as major topic for this PubMed article.
    :param abstract_dict: maps each MeSH descriptor to boolean major topic flag
    :param desired_list: list of descriptors that user specified as relevant
    :param major_bool: if true, consider only abstract's major topic descriptors
    :return: True if this abstract is relevant, False otherwise
    """
    relevant = False
    abstract_des = list(abstract_dict.keys())
    if major_bool:
        # Keep only the descriptors that are marked as major topics
        # Note: some entries in the input files have no descriptors marked as
        # major topics for the article; this probably means that one of
        # the qualifiers on the descriptor is marked as a major topic.
        # We do not extract qualifiers from the .xml file.
        abstract_des = list(filter(lambda d: abstract_dict[d], abstract_des))
    i = 0
    # stop looking as soon as we find a relevant descriptor for this abstract
    while not relevant and i < len(abstract_des):
        relevant = abstract_des[i] in desired_list
        i += 1
    return relevant


def merge_descendants(ancestors):
    """
    Find all descendants of ancestor descriptors in MeSH classification tree
    :param ancestors: list of MeSH descriptors
    :return: list including ancestors and all their descendants in MeSH
    """
    retval = []
    for descriptor in ancestors:
        retval.append(descriptor)
        retval.extend(get_descendants(descriptor).keys())
    return sorted(retval)


@click.command()
@click.option('-i', type=click.Path(exists=True), required=True, help='input directory')
@click.option('-o', type=click.Path(), required=True, help='output directory')
@click.option('-m', is_flag=True, flag_value=True, help='filter on major topics only')
@click.argument('descriptors', callback=check_descriptors, metavar='MeSH_DESCRIPTORS', nargs=-1)
# python filter-abstracts.py -i ../data/pubmed_txt -o ../data/pubmed_relevant -m D005796 D009369 D037102
def main(i, o, descriptors, m):
    """
    Filters each .txt file from input directory by MeSH descriptors, writes PMID, publication
    year, and abstract of relevant articles to corresponding output file.
    """
    files_to_parse = glob.glob(join(i, '*.txt'))
    makedirs(o, exist_ok=True)
    desired_descriptors = merge_descendants(descriptors)
    for f in files_to_parse:
        find_relevant_abstracts(f, o, m, desired_descriptors)
        click.echo(basename(f))


if __name__ == '__main__':
    main()
