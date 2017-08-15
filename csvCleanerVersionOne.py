import  sys, os, csv, pylab, math, re



folders = ['C1']#,'FF','ED','CB','GR','JC','EM', 'JP', 'NB']
for folder in folders:
    listing = os.listdir('./data/' + folder +'/foCsv')
    for fichier in listing:
        if '.DS_Store' in fichier:
            pass
        else:
            target_file = './data/' + folder +'/foCsv/' + fichier
            print(target_file, "_____________________________________________________________")
            newFile = './data/' + folder +'/foCsvCorrected/' + fichier
            with open(newFile, 'w') as fOut:
                with open(target_file, mode='rU') as f:
                    #reader = csv.reader( (line.replace('"','') for line in f) )
                    reader = csv.reader( (line.replace('\0','') for line in f) )
                    for num, row in enumerate(reader):
                        if not row:
                            print("--------------------------------------------------------------------->>> empty")
                            continue

                        if len(row) == 1:
                            print("------------------------------------------------->>> unique entry", row)
                            row = row[0].strip()
                            x = 'error'
                            pattern = re.compile(r',')
                            if pattern.findall(row[0]):
                                x = "there is a coma"
                                row = row[0].strip().split(",")
                                print("------------------------------------------------->>> changed", row)

                            else:
                                continue

                        elif len(row) == 2:
                            flag = 'yes'
                            for x in row:
                                #print(x)
                                matchObj = re.search("\.", x)
                                if not matchObj:
                                    print("------------------------------------------------->>> BAD BAD BAD", row)
                                    flag = 'no'
                                else:
                                    row = row
                                    x = 'good'



                        #print(num,row, "--------------------------", x)
                        if flag == 'yes':
                            newLine = (str(row[0]) + ", " + str(row[1]) + "\n")
                            fOut.write(newLine)
            fOut.close()
