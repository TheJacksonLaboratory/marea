import click
import ftplib

from os import makedirs
from os.path import join

# file containing list of URLs for PubMed files to download
FTP_FILENAMES = 'medline_ftp_links.txt'


@click.command()
@click.option('-d', type=click.Path(), required=True,
              help='directory for list of PubMed files')
# python retrieve_pubmed_names.py -d ../data
def main(d):
    f = ftplib.FTP()
    pubmedftp = 'ftp.ncbi.nlm.nih.gov'
    f.connect(pubmedftp)
    f.login()
    f.cwd('pubmed/baseline')
    ls = []
    f.retrlines('MLSD', ls.append)

    xmlfiles = []
    for entry in ls:
        fname = entry.rstrip('\n').split(';')[-1].strip()
        if not fname.endswith('xml.gz'):
            continue
        click.echo('%s' % click.format_filename(fname))
        xmlfiles.append(fname)

    makedirs(d, exist_ok=True)
    ftp_filenames = join(d, FTP_FILENAMES)
    with click.open_file(ftp_filenames, 'w') as f:
        for xfile in xmlfiles:
            path = join('ftp.ncbi.nlm.nih.gov/pubmed/baseline', xfile)
            f.write("%s\n" % path)


if __name__ == '__main__':
    main()