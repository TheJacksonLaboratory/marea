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
    f.login(passwd='hannah.blau@jax.org')
    baseline = []
    updates = []
    f.cwd('pubmed/baseline')
    f.retrlines('NLST', lambda fn: baseline.
                append(join('ftp.ncbi.nlm.nih.gov/pubmed/baseline', fn)))
    f.cwd('../updatefiles')
    f.retrlines('NLST', lambda fn: updates.
                append(join('ftp.ncbi.nlm.nih.gov/pubmed/updatefiles', fn)))

    xmlfiles = [fn for fn in baseline if fn.endswith('xml.gz')]
    updates = [fn for fn in updates if fn.endswith('xml.gz')]

    for entry in xmlfiles:
        click.echo('%s' % click.format_filename(entry))
        # xmlfiles.append(fname)
    for entry in updates:
        click.echo('%s' % click.format_filename(entry))

    # makedirs(d, exist_ok=True)
    # ftp_filenames = join(d, FTP_FILENAMES)
    # with click.open_file(ftp_filenames, 'w') as f:
    #     for xfile in xmlfiles:
    #         path = join('ftp.ncbi.nlm.nih.gov/pubmed/baseline', xfile)
    #         f.write("%s\n" % path)


if __name__ == '__main__':
    main()
