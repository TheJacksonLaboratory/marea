# marea
Filter PubMed articles for relevance and apply PubTator Central concept recognition to the titles and abstracts of
relevant articles.

### What does marea stand for?
**m**area **a**damantly **r**esists **e**gregious **a**cronyms

### Overview
The goal of this project is to select PubMed articles based on their MeSH descriptors and keywords, then recognize
and replace concepts in the title and abstract of each relevant article. For filtering, the user specifies a set of
high-level MeSH descriptors. Any article marked with at least one of these descriptors or any subcategory of these
descriptors is considered relevant. An article is also judged relevant if it has a keyword that matches a label or
synonym of the search descriptors or their subcategories. __marea__ relies on
[PubTator Central](https://www.ncbi.nlm.nih.gov/research/pubtator/) to find the names of chemicals, diseases,
genes, etc. and replaces each phrase recognized in the title or abstract with the identifier of the
corresponding concept. The final step of the pipeline cleans up the text by deleting punctuation, removing stop
words, and lemmatizing the remaining words.

### 1. Requirements
Requirements for the virtual environment of __marea__:
* Python 3.8
* certifi >= 2021.10.8
* chardet >= 4.0.0
* charset-normalizer >= 2.0.6
* click >= 8.0.2
* idna >= 3.2
* isodate >= 0.6.0
* joblib >= 1.1.0
* nltk >= 3.6.4
* numpy >= 1.21.2
* pyparsing >= 2.4.7
* rdflib >= 6.0.1
* regex >= 2021.10.8
* requests >= 2.26.0
* six >= 1.16.0
* SPARQLWrapper >= 1.8.5
* tqdm >= 4.62.3
* urllib3 >= 1.26.7

These requirements are automatically packaged into the __marea__ singularity container. All the Python
code of steps 3-6 below can be run in the singularity container on the high performance cluster using
the slurm scripts listed in step 7.

### 2. Download .xml files
NCBI's FTP site makes available gzipped _.xml_ files containing titles, abstracts, and metadata
for all PubMed articles. NCBI releases an annual baseline in mid-December, followed by daily
update files throughout the year. To download the PubMed files, start an interactive session
on the high performance cluster and create the directory where you want to store your _.xml_
files. _cd_ into the target directory. The following _wget_ commands will download
the _.xml.gz_ files and their associated _.md5_ files.
```
wget --ftp-user 'anonymous' --ftp-password 'youremailaddress' -bnv -w 5 ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*
wget --ftp-user 'anonymous' --ftp-password 'youremailaddress' -bnv -w 5 ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/pubmed*.xml*
```
(The NCBI _updatefiles_ directory also contains _stats.html_ files that we do not need.) These wget
commands run in the background and write output to a log file.
You can change how many seconds to wait between downloads by adjusting the _w_ parameter,
or eliminate it entirely. The following command will verify the md5 checksums, reporting any failures:
```
md5sum -c --quiet pubmed*.xml.gz.md5
```

### 3. Extract .txt from .xml
_scripts/xml2txt.py_ extracts key fields for each article recorded in the gzipped _.xml_ file, eliminates _.xml_ 
formatting, and writes the result to a text file. The fields of interest are:

* PubMed ID
* year of publication (the earliest one if the entry has multiple dates with different years)
* MeSH descriptors (if any)
* keywords (if any)
* abstract (if any)

_xml2txt.py_ takes two command line options. 

| option | meaning                                                        |
|--------|----------------------------------------------------------------|
| _-x_   | directory containing gzipped _.xml_ files downloaded in step 2 |
| _-t_   | directory for text files produced by _xml2txt.py_              |

For example,
```
python xml2txt.py -x ../data/pubmed_xml -t ../data/pubmed_txt
```
The _-t_ directory is optional; if absent, the _.txt_ files are written to the directory that already contains
_.xml.gz_ files. There will be one _.txt_ output file for each _.xml.gz_ input file, sharing the filename.

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
in the output file. (The abstract is recovered from the PubTator Central offset file described in step 5.)
For an input named _pubmed20n1014.txt_, the corresponding output file is named
_pubmed20n1014_relevant.tsv_.

_filter_abstracts.py_ has four command line options. 

| option | meaning                                                                   |
|--------|---------------------------------------------------------------------------|
| _-i_   | directory containing text files produced in step 3                        |
| _-o_   | directory for _.tsv_ files written by _filter_abstracts.py_               |
| _-n_   | directory where **nltk** data should be downloaded                        |
| _-m_   | optional flag that limits the search to major topic MeSH descriptors only |

Following these options, at the end of the
command line is the list of MeSH descriptors that designate relevant categories. These should be high-level
descriptors; the software automatically includes all their subcategories in the search. For example,
```
python filter_abstracts.py -m -i ../data/pubmed_txt -n ../data/nltk_data \
                           -o ../data/pubmed_rel D005796 D009369 D037102
```
finds articles whose major topic descriptors fall under one or more of the categories for Genes, Neoplasms,
 and Lectins.

### 5. Concept replacement with PubTator Central
[PubTator Central](https://www.ncbi.nlm.nih.gov/research/pubtator/) from the NLM provides data for concept
recognition in PubMed articles for the following categories:
* CellLine
* Chemical
* Disease
* Gene
* SNP
* Species

(as well as other categories __marea__ does not track, such as DNAMutation and ProteinMutation). The first step
is to download _bioconcepts2pubtatorcentral.offset.gz_ from the PubTator Central ftp site.
```
ftp://ftp.ncbi.nlm.nih.gov/pub/lu/PubTatorCentral
```
The offset file contains the title and abstract for every PubMed article and a list of concept replacements.
Each concept replacement line includes the concept category and concept identifier along with the start and end
offsets (in characters) of the text to be replaced by that concept identifier. Unzip 
_bioconcepts2pubtatorcentral.offset.gz_ before running _scripts/pubtate.py_.

_scripts/pubtate.py_ applies all the offset file's concept replacements to the title and abstract 
of each article and writes them to _bioconcepts2pubtatorcentral.replaced_.
_pubtate.py_ takes two command line options. 

| option | meaning                                                                                    |
|--------|--------------------------------------------------------------------------------------------|
| _-i_   | directory containing _bioconcepts2pubtatorcentral.offset_ file                             |
| _-o_   | directory where _pubtate.py_ writes its output file _bioconcepts2pubtatorcentral.replaced_ |

For example,
```
python pubtate.py -i ../data -o ../data/pubtator
```
The output directory is optional and defaults to the input directory.

### 6. Text postprocessing
_scripts/post_process.py_ takes as input the file produced by _pubtate.py_ and selects those articles
that were labeled relevant by _filter_abstracts.py_ (step 4). _post_process.py_ cleans up the text
into which _pubtate.py_ has inserted concept identifiers.
_post_process.py_ takes four command line options.

| option | meaning                                                                                      |
|--------|----------------------------------------------------------------------------------------------|
| _-p_   | directory containing the _bioconcepts2pubtatorcentral.replaced_ file written by _pubtate.py_ |
| _-r_   | directory containing files of relevant articles produced by _filter_abstracts.py_            |
| _-n_   | directory where **nltk** data have been downloaded                                           |
| _-o_   | directory where _post_process.py_ writes its output files (_pubmed_cr.tsv_ and lexicons)     |

For example,
```
python post_process.py -p ../data/pubtator -r ../data/pubmed_rel \
                       -n ../data/nltk_data -o ../data/pubmed_cr
```
Post-processing removes all punctuation symbols, including hyphens and underscores
within words: the parts of a compound word become separate tokens. _post_process.py_ 
also removes stop words, whether lowercase or capitalized, from the title and abstract.
Uppercase acronyms of length ≥ 2, even those that coincide with stop words, are kept.
__marea__ starts with the **nltk** stop word list for English and adds some new stop words. 
Any letter of the alphabet that occurs as a single-character token is a stop word. Numerical
tokens (including those that start with a digit but contain some letters) are discarded 
unless they appear on a short list of "interesting" numbers (1-10 and a few others). 
To reduce the size of the vocabulary, the remaining tokens are lemmatized with the 
__WordNetLemmatizer__ from **nltk**. The last step converts everything to lowercase.
 
_post_process.py_ writes three output files:
* _pubmed_cr.tsv_ contains the PMID, publication date, and modified title and abstract for
  each relevant article;
* _lemmatized_alpha.txt_ contains an alphabetical listing of all lemmatized tokens,
* _lemmatized_freq.txt_ contains the same lemmatized tokens listed by their frequency
of occurrence, in decreasing order.
  
The two vocabulary files give the lemmatized token along with its frequency of occurrence
and the list of words that lemmatize to that token.

### 7. Run pipeline on HPC
Copy the processing pipeline scripts to the HPC file system, preserving the directory structure.
```
marea
├── scripts
│   ├── __init__.py
│   ├── filter_abstracts.py
│   ├── my_lemmatizer.py
│   ├── nlp_utils.py
│   ├── post_process.py
│   ├── pubtate.py
│   ├── query_mesh.py
│   ├── text_post_processor.py
│   └── xml2txt.py
└── singularity
    ├── filter.sh
    ├── marea_python.def
    ├── marea_python.sh
    ├── post_process.sh
    ├── pubtate.sh
    └── xml2txt.sh
```
_marea_python.sh_ builds a singularity container _marea_python.sif_ from _marea_python.def_ with the
latest version of python and other requirements listed in step 1. _xml2txt.sh_ extracts _.txt_ files
from the _.xml_ (step 3). _filter.sh_ identifies relevant articles according to the specified
MeSH descriptors (step 4). _pubtate.sh_ consumes the concept recognition information from
PubTator Central to replace words with concept identifiers in the titles and abstracts of 
PubMed articles (step 5). _post_process.sh_ selects the title and abstract after concept
replacement for articles that were judged relevant in step 4. It applies the NLP manipulations
described in step 6 to the selected text, and writes the final output files.

Edit these slurm scripts to change
* the email address for slurm messages
* the directories to which files are written
* the MeSH descriptors for relevance filtering

These scripts can be run in the __singularity__ directory with
```
sbatch -q batch <scriptname>.sh
```
