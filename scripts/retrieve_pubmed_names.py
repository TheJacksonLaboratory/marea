import ftplib
import os

from retrieve_pubmed_files import DOWNLOADS_DIR

f = ftplib.FTP()
pubmedftp = 'ftp.ncbi.nlm.nih.gov'
f.connect(pubmedftp)
f.login()
f.cwd('pubmed/baseline')
ls = []
f.retrlines('MLSD', ls.append)

xmlfiles = []
for entry in ls:
    # print(entry)
    # print(type(entry))
    fname = entry.rstrip('\n').split(';')[-1].strip()
    if not fname.endswith('xml.gz'):
        continue
    print("'%s'" % fname)
    xmlfiles.append(fname)

ftp_filenames = DOWNLOADS_DIR + 'medline_ftp_links.txt'
with open(ftp_filenames, 'w') as f:
    for xfile in xmlfiles:
        path = os.path.join('ftp.ncbi.nlm.nih.gov/pubmed/baseline', xfile)
        f.write("%s\n" % path)