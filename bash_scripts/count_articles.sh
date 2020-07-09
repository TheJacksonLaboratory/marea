#!/bin/bash

# bash command line script to count up various categories of articles in
# each .txt file output by xml2txt.py. Requires one command line argument:
# path to directory containing .txt files. Output printed to console.
# Example usage:
# $./count_articles.sh /projects/robinson-lab/marea/data/pubmed_txt/*.txt

shopt -s nullglob
cum_have_desc_abs=0
cum_have_keyw_abs=0
cum_no_abs=0
cum_no_desc_no_keyw_abs=0
cum_total=0

for f in "$@"
do
  echo "$f"
  total=`wc -l < $f`
  cum_total=$((cum_total+total))
  printf "total articles: %d\n" $total

  have_desc_abs=`grep '##[0-9]\{4\}##D.\+##.*##.\+$' $f | wc -l`
  cum_have_desc_abs=$((cum_have_desc_abs+have_desc_abs))
  printf "have descriptors and abstract: %d, " $have_desc_abs
  awk "BEGIN {printf \"%.0f%s\n\", $have_desc_abs/$total*100, \"%\"}"

  have_keyw_abs=`grep '##[0-9]\{4\}####.\+##.\+$' $f | wc -l`
  cum_have_keyw_abs=$((cum_have_keyw_abs+have_keyw_abs))
  printf "no descriptors, have keywords and abstract: %d, " $have_keyw_abs
  awk "BEGIN {printf \"%.0f%s\n\", $have_keyw_abs/$total*100, \"%\"}"

  no_desc_no_keyw_abs=`grep '##[0-9]\{4\}######.\+$' $f | wc -l`
  cum_no_desc_no_keyw_abs=$((cum_no_desc_no_keyw_abs+no_desc_no_keyw_abs))
  printf "no descriptors, no keywords, have abstract: %d, " $no_desc_no_keyw_abs
  awk "BEGIN {printf \"%.0f%s\n\", $no_desc_no_keyw_abs/$total*100, \"%\"}"

  no_abs=`grep '##[0-9]\{4\}##.*##.*##$' $f | wc -l`
  cum_no_abs=$((cum_no_abs+no_abs))
  printf "no abstract: %d, " $no_abs
  awk "BEGIN {printf \"%.0f%s\n\", $no_abs/$total*100, \"%\"}"
done

printf "\n***** CUMULATIVE TOTALS *****\n"
printf "total articles: %d\n" $cum_total
printf "have descriptors and abstract: %d, " $cum_have_desc_abs
awk "BEGIN {printf \"%.0f%s\n\", $cum_have_desc_abs/$cum_total*100, \"%\"}"
printf "no descriptors, have keywords and abstract: %d, " $cum_have_keyw_abs
awk "BEGIN {printf \"%.0f%s\n\", $cum_have_keyw_abs/$cum_total*100, \"%\"}"
printf "no descriptors, no keywords, have abstract: %d, " $cum_no_desc_no_keyw_abs
awk "BEGIN {printf \"%.0f%s\n\", $cum_no_desc_no_keyw_abs/$cum_total*100, \"%\"}"
printf "no abstract: %d, " $cum_no_abs
awk "BEGIN {printf \"%.0f%s\n\", $cum_no_abs/$cum_total*100, \"%\"}"
