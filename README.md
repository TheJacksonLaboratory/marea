# marea
Filter PubMed articles for relevance and apply Pubtator Central concept recognition to the titles and abstracts of
relevant articles.

### Naive filter
The goal of this project is to select PubMed articles based on their MeSH descriptors and keywords, then recognize
and replace concepts in the title and abstract of each relevant article. For filtering, the user specifies a set of
high-level MeSH descriptors. Any article marked with at least one of these descriptors or any subcategory of these
descriptors is considered relevant. An article is also judged relevant if it has a keyword that matches a label or
synonym of the search descriptors or their subcategories. __marea__ relies on
[Pubtator Central](https://www.ncbi.nlm.nih.gov/research/pubtator/) to find the names of chemicals, diseases,
genes, etc. and replaces each phrase recognized in the title or abstract with the identifier of the
corresponding concept.

### 1. Requirements
Requirements for the virtual environment of __marea__:
* Python 3.8
* certifi 2020.6.20
* chardet 3.0.4
* click 7.1.2
* idna 2.10
* isodate 0.6.0
* joblib 0.16.0
* nltk 3.5
* numpy 1.19.1
* pyparsing 2.4.7
* rdflib 5.0.0
* regex 2020.7.14
* requests 2.24.0
* six 1.15.0
* SPARQLWrapper 1.8.5
* tqdm 4.48.2
* urllib3 1.25.10

These requirements are automatically packaged into the __marea__ singularity container. All the Python code
of steps 2-5 below can be run in the singularity container on the high performance cluster using the slurm
scripts listed in step 6.

### 2. Download .xml files
First, create the list of PubMed files to be downloaded from NCBI. Run _scripts/retrieve_pubmed_names.py_
to obtain the file _medline_ftp_links.txt_ in the directory specified on the command line with the _-d_ option.
The output directory will be created if it does not already exist (true for all the __marea__ scripts).
For example,
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
descriptors is a subcategory of, or identical to, one of the specified search descriptors. If there is no
match on MeSH descriptors, the code compares the article's keywords to the set of preferred labels and synonyms
in MeSH for all the search descriptors and their subcategories. If at least one of the article's keywords is
included in the set, the article is considered relevant. Before making the comparison, the script applies the
WordNet lemmatizer in **nltk** to both the labels from MeSH and the keywords from the article. The lemmatizer
reduces words to their base form, for example plural nouns are lemmatized to the singular. 

In the _.xml_ file,
each MeSH descriptor and keyword is marked Y/N as a "major topic" for the article. The command line parameters for 
_filter_abstracts.py_ include an optional flag to restrict the search to major topics only. Note that using this
flag will drastically reduce the number of matching articles. Few MeSH descriptors and even fewer keywords
are marked as major topics. Many articles have no MeSH descriptors or keywords marked as major topics. The current
implementation respects the major topic flag for MeSH descriptors but ignores it for keywords.

Not all PubMed articles have MeSH descriptors or keywords; many have no abstract. Any article that has no abstract
is irrelevant for the search regardless of its MeSH descriptors or keywords. 

For each input _.txt_ file, _filter_abstracts.py_ writes an output _.tsv_ file containing only the PubMed ID and
year of publication for those articles deemed relevant. MeSH descriptors, keywords, and abstract are not preserved
in the output file. (The abstract is recovered from the Pubtator Central offset file described in step 5.)
For an input named _pubmed20n1014.txt_, the corresponding output file is named
_pubmed20n1014_relevant.tsv_.

_filter_abstracts.py_ has five command line parameters. The _-i_ option specifies the directory containing the
text files produced in step 3. The _-o_ option names the directory for the _.tsv_ files written by 
_filter_abstracts.py_. The _-n_ option specifies the directory where **nltk** data should be downloaded.
_-m_ is the optional flag that limits the search to major topic MeSH
descriptors only. At the end of the command line is the list of MeSH descriptors that designate relevant
categories. These should be high-level descriptors; the software automatically includes all their subcategories in
the search. For example,
```
python filter_abstracts.py -m -i ../data/pubmed_txt -n ../data/nltk_data \
                           -o ../data/pubmed_rel D005796 D009369 D037102
```
finds articles whose major topic descriptors fall under one or more of the categories for Genes, Neoplasms,
 and Lectins.

### 5. Concept replacement with Pubtator Central
[Pubtator Central](https://www.ncbi.nlm.nih.gov/research/pubtator/) from the NLM provides data for concept
recognition in PubMed articles for the following categories:
* CellLine
* Chemical
* Disease
* Gene
* SNP
* Species

(as well as other categories __marea__ does not track, such as DNAMutation and ProteinMutation). The first step
is to download _bioconcepts2pubtatorcentral.offset.gz_ from the Pubtator Central ftp site.
```
ftp://ftp.ncbi.nlm.nih.gov/pub/lu/PubTatorCentral
```
The offset file contains the title and abstract for every PubMed article and a list of concept replacements.
Each concept replacement line includes the concept category and concept identifier along with the start and end
offsets (in characters) of the text to be replaced by that concept identifier. Unzip 
_bioconcepts2pubtatorcentral.offset.gz_ before running _scripts/pubtate.py_.

_pubtate.py_ takes two command line options. The _-i_ option indicates the directory containing the
Pubtator Central offset file.  _pubtate.py_ applies all the offset file's
concept replacements to the title and abstract of each article and writes them to
_bioconcepts2pubtatorcentral.replaced_ in the directory specified by the _-o_ option. For example,
```
python pubtate.py -i ../data -o ../data/pubtator
```
The output directory is optional and will default to the input directory.

_scripts/replace_concepts.py_ takes as input the file produced by _pubtate.py_ and selects those articles
that were labeled relevant by _filter_abstracts.py_ (step 4). _replace_concepts.py_ postprocesses the text
into which _pubtate.py_ has inserted concept identifiers. _replace_concepts.py_ removes stop words (as
defined by **nltk**) from the title and abstract. It also deletes any hyphen that appears
at the start or at the end of a word (for example, '-induced' becomes 'induced'). These odd tokens arise
when half of a compound word gets replaced by a concept identifier. _replace_concepts.py_ writes to its
output file the PMID, publication date, and modified title and abstract for each relevant article.

_replace_concepts.py_ takes four command line options. The command line option _-p_ specifies the directory
containing the _bioconcepts2pubtatorcentral.replaced_ file written by _pubtate.py_.
Option _-r_ specifies the directory containing files of relevant articles produced by _filter_abstracts.py_.
Option _-n_ specifies the directory where **nltk** data have been downloaded.
Option _-o_ specifies the output directory where _replace_concepts.py_ writes its output file _pubmed_cr.tsv_.
Example usage:
```
python replace_concepts.py -p ../data/pubtator -r ../data/pubmed_rel \
                           -n ../data/nltk_data -o ../data/pubmed_cr
```

### 6. Run pipeline on HPC
Copy the processing pipeline scripts to the HPC file system, preserving the directory structure.
```
marea
├── scripts
│   ├── __init__.py
│   ├── filter_abstracts.py
│   ├── my_lemmatizer.py
│   ├── nlp_utils.py
│   ├── pubtate.py
│   ├── query_mesh.py
│   ├── replace_concepts.py
│   ├── retrieve_pubmed_files.py
│   ├── retrieve_pubmed_names.py
│   └── xml2txt.py
└── singularity
    ├── concept_recog.sh
    ├── download.sh
    ├── filter.sh
    ├── marea_python.def
    └── marea_python.sh
```
_marea_python.sh_ builds a singularity container _marea_python.sif_ from _marea_python.def_ with the latest
version of python and other requirements listed in step 1. _download.sh_ downloads from NCBI the gzipped
_.xml_ files for PubMed articles. _filter.sh_ extracts _.txt_ files from the _.xml_ and then identifies
relevant articles according to the specified MeSH descriptors (as explained in step 4). _concept_recog.sh_
consumes the concept recognition information from Pubtator Central to replace text with concept identifiers
in the titles and abstracts of relevant articles (step 5).

Edit these slurm scripts to change
* the email address for slurm messages
* the directories to which files are written
* the MeSH descriptors for relevance filtering

On sumner, these scripts can be run in the __singularity__ directory with
```
sbatch -q batch <scriptname>.sh
```
