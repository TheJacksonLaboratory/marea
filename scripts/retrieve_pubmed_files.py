import click
import re
import shutil
import socket

from ftplib import FTP, all_errors
from os import makedirs
from os.path import join
from typing import List
from urllib.request import Request, urlopen
from urllib.error import URLError
# file containing list of URLs for PubMed files to download
from retrieve_pubmed_names import FTP_FILENAMES


def list_directory(f: FTP, directory: str) -> List[str]:
    contents = []
    wd = f.pwd()
    f.cwd(directory)
    f.retrlines('NLST', lambda fn: contents.
                append(join('ftp.ncbi.nlm.nih.gov', directory, fn)))
    f.cwd(wd)
    return [fn for fn in contents if fn.endswith('xml.gz')]


def get_files(f: FTP, local_dir: str, remote_dir: str) -> None:
    wd = f.pwd()
    f.cwd(remote_dir)
    contents = []
    f.retrlines('NLST', lambda fn: contents.append(fn))
    filenames = [fn for fn in contents if fn.endswith('xml.gz')]
    for fn in filenames[20:24]:
        local_path = join(local_dir, fn)
        try:
            with click.open_file(local_path, 'wb') as gzf:
                f.retrbinary('RETR ' + fn, gzf.write)
        except all_errors as e:
            click.echo('Error retrieving file {}: {}'.
                       format(local_path, e.strerror))
    f.cwd(wd)
# try:
#         with click.open_file(join(x, gzip_filename), 'wb') as gzf:
#             shutil.copyfileobj(response, gzf)
#     except OSError as e:
#         click.echo('Could not write file: ' + e.strerror)


def retrieve_pubmed_names() -> List[str]:
    f = FTP()
    f.connect('ftp.ncbi.nlm.nih.gov')
    f.login(passwd='hannah.blau@jax.org')
    baseline = list_directory(f, 'pubmed/baseline')
    updates = list_directory(f, 'pubmed/updatefiles')
    pubmed_names = baseline + updates
    pubmed_names.sort()
    return pubmed_names


@click.command()
@click.option('-d', type=click.Path(exists=True), required=True,
              help='directory for list of PubMed files')
@click.option('-x', type=click.Path(), required=True,
              help='directory for gzipped xml files')
# python retrieve_pubmed_files.py -d ../data -x ../data/pubmed_xml/
def main(d, x):
    """
    Download gzipped xml files of PubMed abstracts from NCBI ftp site
    to directory specified as command line argument.
    """
    # ftp_filenames = join(d, FTP_FILENAMES)
    makedirs(x, exist_ok=True)
    f = FTP()
    f.connect('ftp.ncbi.nlm.nih.gov')
    f.login(passwd='hannah.blau@jax.org')
    get_files(f, x, 'pubmed/baseline')
    get_files(f, x, 'pubmed/updatefiles')
    f.quit()
    # timeout in seconds --- if you don't set a timeout, socket can hang
    # timeout = 10
    # socket.setdefaulttimeout(timeout)

    # with click.open_file(ftp_filenames, 'r') as f:
    #     for line in f:
    #         ftp_url = line.rstrip()
    #         # extract the filename from the URL
    #         ptrn = re.compile(r'(?:[\w.]+/)+([^/]+)$')
    #         match = ptrn.search(ftp_url)
    #         if match:   # avoids error on last (empty) line of input file
    #             gzip_filename = match.group(1)
    #             click.echo(gzip_filename)

                # Download the file from ftp_url and save it locally under gzip_filename:
    # for ftp_url in retrieve_pubmed_names():
        # print(ftp_url)
                # req = Request('http://' + ftp_url)
                # try:
                #     response = urlopen(req)
                # except URLError as e:
                #     if hasattr(e, 'reason'):
                #         click.echo('We failed to reach a server.')
                #         click.echo('Reason: ', e.reason)
                #     elif hasattr(e, 'code'):
                #         click.echo('The server could not fulfill the request.')
                #         click.echo('Error code: ', e.code)
                # else:  # so far so good
                #     try:
                #         with click.open_file(join(x, gzip_filename), 'wb') as gzf:
                #             shutil.copyfileobj(response, gzf)
                #     except OSError as e:
                #         click.echo('Could not write file: ' + e.strerror)


if __name__ == "__main__":
    main()
