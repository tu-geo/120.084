#!/bin/bash

OUT_FILE=../data/cleaned/FINAL_SORT_NORAD.csv
# cat ../data/cleaned/ID_LIST_ALL.csv | sed -n "/UNKNOWN/!p" | sort -t";" -k2 > f1

sort -t";" -k4 -u ../data/cleaned/ID_LIST_ALL.csv | sort -t";" -k2 | sed -n '/#/!p' > f1
sort -t";" -k4 ../data/cleaned/PRIORITIES.csv | sed -n '/#/!p' > f2

echo ""

# COSPAR: ID_LIST_ALL.2, PRIORITY.4

echo "#Priority;Name;COSPAR;NORAD" > $OUT_FILE

join -t";" -1 2 -2 4 -o 2.1,2.2,1.2,1.3 f1 f2 | sort -t ";" -k1 -h >> $OUT_FILE
rm f1 f2

cat $OUT_FILE
