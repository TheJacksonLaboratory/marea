import glob
import os
import re
import sys

from query_mesh import get_descendants

ABSTRACTS_DIR = '../data/pubmed/'
FILTERED_DIR = '../data/relevant/'


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


def find_relevant_abstracts(f, major_topic, desired_descriptors):
    with open(f) as unfiltered_file:
        outfile_path = FILTERED_DIR + get_outfilename(f)
        with open(outfile_path, 'w') as filtered_file:
            for line in unfiltered_file:
                segments = line.split('##')
                # check whether this line contains an abstract
                abstract = segments[-1].strip()
                if abstract != '':
                    # check whether the abstract meets relevancy criteria
                    abstract_descriptors = extract_descriptors(segments[1].strip())
                    if is_relevant(abstract_descriptors, desired_descriptors,
                                   major_topic):
                        # record relevant abstract in output file
                        filtered_file.write('{}\t{}\n'.format(segments[0], abstract))


def get_outfilename(path):
    """
    Generate the filename for abstracts filtered by relevant MeSH descriptors.
    e.g. 'pubmed20n0001_relevant.txt' from '../data/pubmed/pubmed20n0001.txt'
    :param path: path to the input .txt file of PubMed abstracts
    :return: output filename with .txt extension
    """
    filename = path.split('/')[-1]
    return filename.split('.')[0] + '_relevant.txt'


def is_relevant(abstract_dict, desired_list, major_bool):
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
    while not relevant and i < len(abstract_des):
        relevant = abstract_des[i] in desired_list
        i += 1
    return relevant


def merge_descendants(ancestors):
    retval = []
    for descriptor in ancestors:
        retval.append(descriptor)
        retval.extend(get_descendants(descriptor).keys())
    return sorted(retval)


def main(descriptor_list, major_topic_only=False):
    files_to_parse = glob.glob(ABSTRACTS_DIR + '*.txt')
    os.makedirs(FILTERED_DIR, exist_ok=True)
    desired_descriptors = merge_descendants(descriptor_list)
    find_relevant_abstracts(files_to_parse[0], major_topic_only,
                            desired_descriptors)

    # for in_file in files_to_parse[:25]:
    #     parse_abstract_file(in_file, major_topic_only, descriptor_dict)

    #     if extracted:
    #         short_name = get_disease_name(file)
    #         # url = 'http://www.ncbi.nlm.nih.gov/books/n/gene/{}'.format(disease)
    #         long_name = extract_long_name(root)
    #         disease_names[long_name] = short_name
    #         #            print("{}\t\t{}".format(disease, long_name))
    #
    #         with open(GR_EXTRACTED + short_name + '.txt', 'w') as export:
    #             export.write(extracted)
    #
    # with open(MATCHES_DIR + DISEASE_NAMES, 'w') as f:
    #     for dis in sorted(disease_names, key=str.lower):
    #         f.write("{}\t{}\n".format(disease_names[dis], dis))
    #         print(dis)


if __name__ == '__main__':
    mesh_ids = [des for des in sys.argv if re.fullmatch(r'D(\d{6}|\d{9})', des)]
    major_topic_only = sys.argv[-1].lower() == 'y'
    # for des in descriptors:
    #     print(des, end=' ')
    # print('MajorTopicOnly = {}'.format(major_topic_only))
    main(mesh_ids, major_topic_only)
