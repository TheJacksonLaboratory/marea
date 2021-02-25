#!/bin/bash

# bash command line script that treats all PubMed articles as relevant
# for futher processing in marea. That is, this script bypasses
# filter_abstracts.py and creates the files listing relevant PMIDs directly
# from the .txt files written by xml2txt.py. The two parameters are
# -- input directory of .txt files
# -- output directory for _rel.tsv files
# any existing output files of the same file names are overwritten
# Example usage:
# $./bypass_filter.sh ../data/pubmed_txt ../data/pubmed_rel
# N.B.: do not put a final slash on the directories passed as parameters
# to the script, the regex is not smart enough to handle that.

shopt -s nullglob

# the purpose of this regex is to isolate the basename of the .txt file so it
# can be reused for the output filename
regex='^(.+/)*(.+)\.[[:alnum:]]{3}$'
for f in "$1"/*
do
  if [[ $f =~ $regex ]]
  then
    awk -v FS="##" -v OFS="\t" '{print $1,$2}' $f > "$2/${BASH_REMATCH[2]}_rel.tsv"
    echo "$f"
  else
    echo "regex failure for $f"
  fi
done
