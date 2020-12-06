import click
import glob
import gzip
import re
import xml.etree.ElementTree as ET

from os import makedirs
from os.path import basename, join
from typing import List, Set


def parse_article(pmid: str, article) -> str:
    string = f'{pmid}##'

    dates = []
    # Compare PubDate to ArticleDate if any, PubMedPubDate if any,
    # record the earliest year.
    for pdate in article.iter('PubDate'):
        year = None
        child = pdate.find('Year')
        if child is not None:
            year = child.text
        else:
            child = pdate.find('MedlineDate')
            if child is not None:
                m = re.match(r'^(\d{4}).*', child.text)
                year = m.group(1) if m else None
        if year:
            dates.append(int(year))
    for pyear in article.iterfind(".//ArticleDate/Year"):
        dates.append(int(pyear.text))
    for pyear in article.iterfind(
            ".//PubMedPubDate[@PubStatus='pubmed']/Year"):
        dates.append(int(pyear.text))
    pubyear = min(dates) if dates else 'unknown'
    string += f'{pubyear}##'

    descriptor_present = False
    for heading in article.iter('DescriptorName'):
        if heading.text is not None:
            string += \
                f"{heading.get('UI')} {sanitize(heading.text)} {heading.get('MajorTopicYN')} | "
            descriptor_present = True

    if not descriptor_present:
        string += '##'
    else:
        string = f'{string[:-3]}##'  # eliminate the final | separator

    keyword_present = False
    for keyword in article.iter('Keyword'):
        keyword_sanitized = sanitize(keyword.text)
        if keyword_sanitized is not None and keyword_sanitized != '':
            string += f"{keyword_sanitized} {keyword.get('MajorTopicYN')} | "
            keyword_present = True

    if not keyword_present:
        string += '##'
    else:
        string = f'{string[:-3]}##'

    for abstract in article.iterfind('.//Abstract/AbstractText'):
        inner_text = ''
        for sub_text in abstract.itertext():
            inner_text += sub_text
        if inner_text != '':
            string += f'{sanitize(inner_text)} '

    return string.strip()


def sanitize(string):
    """
    Remove whitespace from ends of the string, and replace any line breaks
    within the string by a single space. If passed None, return None.
    :param string: string to be cleaned up
    :return: sanitized string
    """
    if string is None:
        return string
    retval = string.strip()
    # eliminate line breaks within the string
    return " ".join(retval.splitlines())


def text_from_xml(filename: str, seen_pmids: Set[str]) -> List[str]:
    tree = ET.parse(gzip.open(filename))
    root = tree.getroot()

    parsed = []

    for article in root:
        pmid = ''
        for elem in article.iter('PMID'):
            pmid = elem.text

        # check whether this pmid was already processed in another file
        if pmid not in seen_pmids:
            seen_pmids.add(pmid)
            parsed.append(parse_article(pmid, article))

    return parsed


@click.command()
@click.option('-x', type=click.Path(exists=True), required=True,
              help='directory of gzipped xml files')
@click.option('-t', type=click.Path(),
              help='directory for txt files, defaults to xml directory')
# python xml2txt.py -x ../data/pubmed_xml/
# python xml2txt.py -x ../data/pubmed_xml -t ../data/pubmed_txt
def main(x, t):
    if t is None:
        destination = x
    else:
        makedirs(t, exist_ok=True)
        destination = t
    xml_files = glob.glob(join(x, '*.xml.gz'))
    # Sort filenames so as to parse baseline files before update files.
    # Later errata for a previously published PMID lack abstract, will
    # cause the article to be eliminated from consideration even when its
    # MeSH descriptors or keywords match the search criteria.
    xml_files.sort()
    already_seen = set()
    for pmxml in xml_files:
        click.echo(basename(pmxml))
        with click.open_file(join(destination, basename(pmxml).replace(
                "xml.gz", "txt")), 'w') as pmtxt:
            for string in text_from_xml(pmxml, already_seen):
                pmtxt.write(f'{string}\n')


if __name__ == '__main__':
    main()
