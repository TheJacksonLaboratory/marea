import click
import subprocess

from ftplib import FTP, all_errors
from os import makedirs
from os.path import join
from typing import List


def list_current_directory(f: FTP) -> List[str]:
    contents = []
    f.retrlines('NLST', lambda ln: contents.append(ln))
    filenames = [fn for fn in contents if fn.endswith('xml.gz')]
    filenames.sort()
    return filenames


def get_files(f: FTP, local_dir: str, remote_dir: str) -> None:
    wd = f.pwd()
    f.cwd(remote_dir)
    filenames = list_current_directory(f)
    for fn in filenames:
        local_path = join(local_dir, fn)
        md5_path = local_path + '.md5'
        try:
            with click.open_file(local_path, 'wb') as gzf:
                f.retrbinary('RETR ' + fn, gzf.write)
            with click.open_file(md5_path, 'wb') as md5f:
                f.retrbinary('RETR ' + fn + '.md5', md5f.write)
        except all_errors as e:
            click.echo('Error retrieving file {}: {}'.
                       format(fn, e.strerror))
        try:
            output = subprocess.check_output([r"md5sum", local_path])
            mdfive = output.decode('utf-8').split()[0]
            with click.open_file(md5_path, 'r') as md5f:
                should_be = md5f.readline().split()[1]
            if mdfive == should_be:
                click.echo(fn)
            else:
                click.echo('md5 checksum does not match for file {}\n{} should be {}'.
                           format(local_path, mdfive, should_be))
        except subprocess.CalledProcessError:
            click.echo('Error calculating md5 checksum for ' + local_path)
    f.cwd(wd)


# def retrieve_pubmed_names() -> List[str]:
#     f = FTP()
#     f.connect('ftp.ncbi.nlm.nih.gov')
#     f.login(passwd='hannah.blau@jax.org')
#     baseline = list_directory(f, 'pubmed/baseline')
#     updates = list_directory(f, 'pubmed/updatefiles')
#     pubmed_names = baseline + updates
#     pubmed_names.sort()
#     return pubmed_names


@click.command()
@click.option('-x', type=click.Path(), required=True,
              help='directory for gzipped xml files')
# python retrieve_pubmed_files.py -x ../data/pubmed_xml/
def main(x):
    """
    Download gzipped xml files of PubMed abstracts along with their .md5 files
    from NCBI ftp site to directory specified as command line argument.
    """
    makedirs(x, exist_ok=True)
    f = FTP()
    f.connect('ftp.ncbi.nlm.nih.gov')
    f.login(passwd='hannah.blau@jax.org')
    get_files(f, x, 'pubmed/baseline')
    get_files(f, x, 'pubmed/updatefiles')
    f.quit()


if __name__ == "__main__":
    main()
