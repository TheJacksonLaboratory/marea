# marea
Filter PubMed articles for relevance.

### Naive filter
The goal of this project is to select PubMed articles based on their MeSH descriptors, or their keywords for articles
that do not have MeSH descriptors. For MeSH filtering, the user specifies a set of high-level descriptors. Any article
marked with at least one of these descriptors or any subcategory of these descriptors is considered relevant.

### 1. Requirements
Requirements for the virtual environment of marea:

* Python 3.8
* click 7.1.2
* isodate 0.6.0
* pyparsing 2.4.7
* rdflib 5.0.0
* six 1.15.0
* SPARQLWrapper 1.8.5

### 2. Download .xml files
First, create the list of PubMed files to be downloaded from NCBI. Run _scripts/retrieve_pubmed_names.py_
to obtain the file _medline_ftp_links.txt_ in the directory specified on the command line with the _-d_ option.
The output directory will be created if it does not already exist (true for all the __marea__ scripts). For example,

```
python retrieve_pubmed_names.py -d ../data
```

Next, run _scripts/retrieve_pubmed_files.py_ to download the files listed in the previous step. As before,
the _-d_ command line option specifies the directory containing _medline_ftp_links.txt_. The _-x_ option specifies
the directory to which the gzipped _.xml_ files of PubMed article abstracts and metadata should be downloaded.
For example,

```
python retrieve_pubmed_files.py -d ../data/ -x ../data/pubmed_xml/
```

### 3. Extract .txt from .xml
_scripts/xml2txt.py_ extracts key fields for each article recorded in the gzipped _.xml_ file, eliminates _.xml_ 
formatting, and writes the result to a text file. The fields of interest are:

* PubMed ID
* year of publication (the earliest one if the entry has multiple dates with different years)
* MeSH descriptors (if any)
* keywords (if any)
* abstract (if any)

_xml2txt.py_ takes two command line options. The _-x_ option specifies the directory containing the
gzipped _.xml_ files downloaded in step 2. The _-t_ option names the directory for the text files produced by 
_xml2txt.py_. There will be one _.txt_ output file for each _.xml.gz_ input file, sharing the filename.
For example,
 
```
python xml2txt.py -x ../data/pubmed_xml -t ../data/pubmed_txt
```

The _-t_ directory is optional; if absent, the _.txt_ files are written to the directory that already contains
_.xml.gz_ files.

### 4. Select relevant articles from .txt files

_scripts/filter_abstracts.py_ filters the _.txt_ file to select articles that are relevant according to
a user-supplied set of MeSH descriptors. An article is deemed relevant if at least one of the the article's
descriptors is a subcategory of, or identical to, one of the specified search descriptors. In the _.xml_ file,
each MeSH descriptor and keyword is marked Y/N as a "major topic" for the article. The command line parameters for 
_filter_abstracts.py_ include an optional flag to restrict the search to major topics only. Note that using this
flag will drastically reduce the number of matching articles because few MeSH descriptors and even fewer keywords
are marked as major topics. Many articles have no MeSH descriptors or keywords marked as major topics.

Not all PubMed articles have MeSH descriptors; many have no abstract. Any article that has no abstract is irrelevant
for the search regardless of its MeSH descriptors. Filtering on keywords is not yet implemented.

For each input _.txt_ file, _filter_abstracts.py_ writes an output _.tsv_ file containing only the PubMed ID,
year of publication, and abstract of those articles deemed relevant. MeSH descriptors and keywords are not preserved
in the output file. For an input named _pubmed20n1014.txt_, the corresponding output file is named
_pubmed20n1014_relevant.tsv_.

_filter_abstracts.py_ has four command line parameters. The _-i_ option specifies the directory containing the
text files produced in step 3. The _-o_ option names the directory for the _.tsv_ files written by 
_filter_abstracts.py_. _-m_ is the optional flag described above that limits the search to major topic MeSH
descriptors only. At the end of the command line is the list of MeSH descriptors that designate relevant
categories. These should be high-level descriptors; the software automatically includes all their subcategories in
the search. For example,

```
python filter_abstracts.py -m -i ../data/pubmed_txt -o ../data/pubmed_relevant D005796 D009369 D037102
```

finds articles whose major topic descriptors fall under one or more of the categories for Genes, Neoplasms,
 and Lectins.

### 5. Run pipeline on HPC
Copy the processing pipeline scripts to the HPC file system, preserving the directory structure.

```
marea
├── scripts
│   ├── __init__.py
│   ├── filter_abstracts.py
│   ├── query_mesh.py
│   ├── retrieve_pubmed_files.py
│   ├── retrieve_pubmed_names.py
│   └── xml2txt.py
└── singularity
    ├── download.sh
    ├── filter.sh
    └── marea_python.def
```
_download.sh_ builds a singularity container _marea_python.sif_ as described in _marea_python.def_ with the latest
version of python and the other __marea__ requirements, writing . It then downloads from NCBI all the gzipped
_.xml_ files for PubMed articles. _filter.sh_ extracts _.txt_ files from the _.xml_ and then identifies
relevant articles according to the specified MeSH descriptors (as explained in Section 4).

Edit both _download.sh_ and _filter.sh_ to change

* the email address for slurm messages
* the directories to which files are written
* the MeSH descriptors for relevance filtering (in)

Run _download.sh_ followed by _filter.sh_ with

```
sbatch -q batch <scriptname>.sh
```
