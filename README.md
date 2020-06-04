# marea
Filter PubMed articles for relevance.

### Naive filter
The goal of this project is to select PubMed articles based on their MeSH descriptors, or their keywords for articles
that do not have MeSH descriptors. For MeSH descriptors, user specifies a set of high-level descriptor ids. Any article
that has at least one of these descriptors or any subcategory of these descriptors is considered relevant.

### 1. Requirements
Requirements for the virtual environment of marea:

* Python 3.8
* SPARQLWrapper 1.8.5
* click 7.1.2
* isodate 0.6.0
* pip 20.1.1
* pyparsing 2.4.7
* rdflib 5.0.0
* setuptools 47.1.1
* six 1.15.0

### 2. Download .xml files
First, create the list of PubMed files to be downloaded from NCBI. Run _retrieve_pubmed_names.py_ from
the __scripts__ subdirectory, which writes the file _medline_ftp_links.txt_ in
the directory specified as the _-d_ command line option. For example,

`python retrieve_pubmed_names.py -d ../data`

Next, download the files by running _retrieve_pubmed_files.py_ from the __scripts__ subdirectory.
The _-d_ command line option specifies the directory containing _medline_ftp_links.txt_
(the directory used in the previous step). The _-x_ option specifies the directory to which the
gzipped _.xml_ files of PubMed article abstracts and metadata should be downloaded. For example,

`python retrieve_pubmed_files.py -d ../data/ -x ../data/pubmed_xml/`

### 3. Extract .txt from .xml

### 4. Select relevant articles from .txt files
