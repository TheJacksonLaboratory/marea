import click
import glob
import gzip
import xml.etree.ElementTree as ET

from os import makedirs
from os.path import basename, join
# from scripts.retrieve_pubmed_names import DOWNLOADS_DIR
# from scripts.utils import final_slash


def sanitize(string):
    """
    Remove whitespace from ends of the string, and replace any line breaks
    within the string by a single space.
    :param string: string to be cleaned up
    :return: sanitized string
    """
    retval = string.strip()
    # eliminate line breaks within the string
    return " ".join(retval.splitlines())


def text_from_xml(filename):
    tree = ET.parse(gzip.open(filename))
    root = tree.getroot()

    parsed = []

    for article in root:
        for elem in article.iter('PMID'):
            id = elem.text

        string = f'{id}##'

        year = 'unknown'
        # TODO: compare PubDate to PubMedPubDate if any, ArticleDate if any,
        # take the earliest date see head1015
        for pdate in article.iter('PubDate'):
            child = pdate.find('Year')
            if child is not None:
                year = child.text
            else:
                child = pdate.find('MedlineDate')
                if child is not None:
                    year = child.text.split()[0]
        string += f'{year}##'

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
            if keyword.text is not None:
                string += f"{sanitize(keyword.text)} {keyword.get('MajorTopicYN')} | "
            keyword_present = True

        if not keyword_present:
            string += '##'
        else:
            string = f'{string[:-3]}##'

        for abstract in article.iterfind('.//Abstract/AbstractText'):
            inner_text = ''
            for element in abstract.iter():
                if element.text is not None:
                    inner_text += element.text
                if element.tail is not None:
                    inner_text += element.tail
            if inner_text != '':
                string += f'{sanitize(inner_text)} '

        parsed.append(string.strip())

    return parsed


@click.command()
@click.option('-x', type=click.Path(exists=True), required=True,
              help='directory of gzipped xml files')
@click.option('-t', type=click.Path(), help='directory for txt files, defaults to xml directory')
# python xml2txt.py -x ../data/pubmed/
# python xml2txt.py -x ../data/pubmed -t ../data/txtextracted
def main(x, t):
    xml_files = glob.glob(join(x, '*.xml.gz'))
    for pmxml in xml_files:
        click.echo(basename(pmxml))
        if t is None:
            destination = x
        else:
            makedirs(t, exist_ok=True)
            destination = t
        with click.open_file(join(destination, basename(pmxml).replace(
                "xml.gz", "txt")), 'w') as pmtxt:
            for string in text_from_xml(pmxml):
                pmtxt.write(f'{string}\n')


if __name__ == '__main__':
    main()
