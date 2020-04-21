import os
import re
import shutil
import socket

from urllib.request import Request, urlopen
from urllib.error import URLError

DOWNLOADS_DIR = '/projects/robinson-lab/PMP/'
# DOWNLOADS_DIR = '../data/'
PUBMED_DIR = DOWNLOADS_DIR + 'pubmed/'
# ftp_filenames = DOWNLOADS_DIR + 'medline_ftp_links.txt'
ftp_filenames = 'medline_ftp_links.txt'

def main():
    """
    Download gzipped xml files of PubMed abstracts from NCBI ftp site to PUBMED_DIR.
    URLs listed in ftp_filenames file.
    """
    os.makedirs(PUBMED_DIR, exist_ok=True)

    # timeout in seconds --- if you don't set a timeout, socket can hang
    timeout = 10
    socket.setdefaulttimeout(timeout)

    with open(ftp_filenames, 'r') as f:
        for line in f:
            ftp_url = line.rstrip()
            # extract the filename from the URL
            ptrn = re.compile(r'(?:[\w.]+/)+([^/]+)$')
            match = ptrn.search(ftp_url)
            if match:   # avoids error on last (empty) line of input file
                gzip_filename = match.group(1)
                print(gzip_filename)

                # Download the file from ftp_url and save it locally under gzip_filename:
                req = Request('http://' + ftp_url)
                try:
                    response = urlopen(req)
                except URLError as e:
                    if hasattr(e, 'reason'):
                        print('We failed to reach a server.')
                        print('Reason: ', e.reason)
                    elif hasattr(e, 'code'):
                        print('The server could not fulfill the request.')
                        print('Error code: ', e.code)
                else: # so far so good
                    try:
                        with open(PUBMED_DIR + gzip_filename, 'wb') as gzf:
                            shutil.copyfileobj(response, gzf)
                    except OSError as e:
                        print('Could not write file: ' + e)


if __name__ == "__main__":
    main()
