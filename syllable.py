import  sys, os, csv, pylab, math

folder = "./EM/"
syllable_file = "syllabletime.txt"
full_path = folder + syllable_file
print full_path
spans = open(full_path).read().splitlines()
a = {}
index_sample = 0

with open(full_path, mode='rU') as f:
    reader = csv.reader(f, delimiter='\t')
    next(reader)
    for num, row in enumerate(reader):
        if row[0][2:] == index_sample:
            pass
        else:
            index_sample = row[0][2:]
            print "changed to -----------------------", row[0][0:2]+index_sample

        a[index_sample+"_"+row[1]] = row[2]

for entry in a:
    print entry
