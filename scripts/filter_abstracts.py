import glob
import os
import re
import sys

from query_mesh import get_descendants


ABSTRACTS_DIR = '../downloads/pubmed/'
FILTERED_DIR = '../downloads/filtered/'


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
    for it in sorted(retval.items()):
        print('{} {}'.format(it[0], it[1]))
    return retval


def get_filename(path):
    """
    Extract the filename from a path,
    e.g. 'pubmed20n0001' from '../downloads/pubmed/pubmed20n0001.txt'
    :param path: path to a file with a single extension, such as .txt, not .xml.gz)
    :return: unadorned filename without extension
    """
    filename = path.split('/')[-1]
    return filename.split('.')[0]


def merge_descendants(ancestors):
    retval = []
    for descriptor in ancestors:
        retval.append(descriptor)
        retval.extend(get_descendants(descriptor).keys())
    return sorted(retval)


def parse_abstract_file(f, major_topic, desired_descriptors):
    with open(f) as abstract_file:
        for line in abstract_file:
            line = line.rstrip()
            segments = line.split(';')
            pmid = segments[0]
            abs_descriptors = extract_descriptors(segments[1])
            # for it in sorted(abs_descriptors.items()):
            #     print('{} {}'.format(it[0], it[1]))
            # abs_descriptors.clear()
    return None


def main(descriptor_list, major_topic_only=False):
    files_to_parse = glob.glob(ABSTRACTS_DIR + '*.txt')
    os.makedirs(FILTERED_DIR, exist_ok=True)
    desired_descriptors = merge_descendants(descriptor_list)
    print(len(desired_descriptors))
    for des in desired_descriptors:
        print(des)

    # for item in sorted(desired_descriptors.items()):
    #     print('{} {}'.format(item[0], item[1]))
    # parse_abstract_file(files_to_parse[0], major_topic_only, desired_descriptors)
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
    descriptors = [des for des in sys.argv if re.fullmatch(r'D(\d{6}|\d{9})', des)]
    major_topic_only = sys.argv[-1].lower() == 'y'
    # for des in descriptors:
    #     print(des, end=' ')
    # print('MajorTopicOnly = {}'.format(major_topic_only))
    main(descriptors, major_topic_only)
