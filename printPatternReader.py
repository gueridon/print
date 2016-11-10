# -*-coding:utf-8 -*

# based on PRInt (Nicholas Bacuez, 2012)
from printModule import *
import printConfig
import  sys, os, csv, pylab, math


######################################################################
##
#   graph production
#
def printGraph(xValues,yValues, fileNamePG):
    sample_tag = os.path.splitext(fileNamePG)[0]
    print "SAMPLETAG = ", sample_tag
    #print len (yValues)
    pylab.figure(sample_tag)
    pylab.plot(xValues, yValues, linewidth = 2, color='k')
    pylab.xlim([0, len(xValues)])
    pylab.xlabel('time in %')
    if printConfig.scalingMethod == "ERB":
        pylab.ylim([0,100])
        pylab.ylabel('fo in ERB')
        pylab.title('Sample %s (ERB scaling)' % sample_tag)
        pylab.savefig('ERB_'+ sample_tag)
    elif printConfig.scalingMethod == "PCT":
        pylab.ylim([0,100])
        pylab.ylabel('fo in %')
        pylab.title('Sample %s (percentage scaling)' % sample_tag)
        pylab.savefig('PCT_'+ sample_tag)
    print "\n-> graph for sample %s was saved to directory \n" % sample_tag

######################################################################
##
#   get lists of time and fo values from the original two-column file
#
def getOriginalValues(fileID, column, targetPathGOV):
    listOfValues = []
    rawdata = os.path.join(targetPathGOV + fileID)
    with open(rawdata, mode='rU') as f:
        reader = csv.reader(f)
        for num, row in enumerate(reader):
            value = row[column]
            listOfValues.append(float(value))
    return listOfValues

######################################################################
##
#   time scaling methods:
#   percentage (PCT)
#   syllabic adjustment
#



######################################################################
##
#   fo scaling methods:
#   percentage (PCT)
#   Equivalent Rectangular Bandwith (ERB)
#
def scalePCT(foRaw):
    minFo = min(foRaw) - 10 # Baseline is set to n points under actual value
    maxFo = max(foRaw)
    rangeFo = maxFo - minFo
    foListScaled = [round((item - minFo) * (100.0/rangeFo),0) for item in foRaw]
    return foListScaled

def scaleERB(foRaw):
    foListScaled = [round((21.4 * math.log10((0.00437 * item) +1))*10,0) for item in foRaw]
    return foListScaled

######################################################################
##
#   general movement detection tool
#
def mvtDetectionScan(foList, fileNameMDS):
    listLength = len(foList)
    init = foList[0]
    prevScan = 0
    valueList = [foList[0]]
    indexList = [foList.index(foList[0])]
    for i,  x in enumerate(foList):
        #this compare each value in the list to the next
        if i < listLength-1: #all values in the list but the last.
            if x < foList[i+1]:
                scanCheck = 0
                #print "^", x
            elif x == foList[i+1]:
                scanCheck = 0
                #print "-", x
            elif x > foList[i+1]:
                scanCheck = 1
                #print "v", x
        else:# last value in the list is compared to the previous one.
            if x < foList[i-1]:
                scanCheck = 0
                #print "vi", x
            elif x == foList[i-1]:
                scanCheck = 0
                #print "-i", x
            elif x > foList[i-1]:
                scanCheck = 1
                #print "^i", x
            valueList.append(x)
            indexList.append(i)
        # this keeps track of the movement and finds raw H and L points.
        if scanCheck == prevScan:
            continue
        elif scanCheck == 0 and prevScan == 1:
            valueList.append(x)
            indexList.append(i)
            #print "-------->", x, "at", i, "is L"
        elif scanCheck == 1 and prevScan == 0:
            valueList.append(x)
            indexList.append(i)
            #print "-------->", x, "at" ,i, "is H"
        prevScan = scanCheck
    mvtRaw = dict(zip(indexList, valueList))
    #print "there are", listLength, "points in the sample."
    #print len(mvtRaw), "turning points were found in the sample."
    #print mvtRaw

    if printConfig.graphOutput == "y":
        printGraph(indexList, valueList, fileNameMDS)

    return mvtRaw

######################################################################
##
#   FOLDER PROCESSING
#
def folderModeProcessing(targetFolder, chosenScaling):
    processedCurvesDataBase = []
    listing = os.listdir(targetFolder)
    print "folder: ", targetFolder
    for fileName in listing:
        timeData = getOriginalValues(fileName, 0, targetFolder)
        foData = getOriginalValues(fileName, 1, targetFolder)
        if chosenScaling == "ERB":
            ffScaled = scaleERB(foData)
        elif chosenScaling == "PCT":
            ffScaled = scalePCT(foData)
        #print ffScaled
        processedCurve = mvtDetectionScan(ffScaled, fileName)
        #print processedCurve
        processedCurvesDataBase.append(processedCurve)
    for eachFile in processedCurvesDataBase:
        print len(eachFile)
    print len(processedCurvesDataBase) , "files were processed successfully!"
######################################################################
##
#   subject fo range analysis
#   max, min, range, averages
