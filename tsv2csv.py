import sys
import csv

tabin = csv.reader(sys.stdin, dialect=csv.excel_tab)
commaout = csv.writer(sys.stdout, dialect=csv.excel)
for row in tabin:
    commaout.writerow(row)

""" BASH
for file in *.tsv
do
    python tsv2csv.py < $file > ${file%.*}.csv
done

TO REMOVE ALL FILES BY EXTENSION
find . -name '*.txt' -delete

TO CHANGE PART OF A NAME FILE
for file in *.csv ; do mv $file ${file//C1_/CA} ; done

"""
