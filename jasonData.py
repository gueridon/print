import json
from sys import argv
from pprint import pprint
import glob, sys, time, re, wave
import os, os.path
import csv
import contextlib

#global parameters
script, FolderName = argv


LisToTranscriptions = "./questionData/questionList.csv"
AudioFolder = "./questionData/"+FolderName+"/audio/"
DataFolder = "./questionData/"+FolderName+"/foCsv/"
SyllableStartFile = "./questionData/"+FolderName+"/starttimes.csv"
SyllableDurationFile = "./questionData/"+FolderName+"/syllabletime.csv"
JsonOutputDirectory = "./questionData/"+FolderName+"/json/"




def time_format_converter(time):
    """time format converter
    """
    seconds = time
    minutes = seconds // 60
    hours = minutes // 60
    getTime =  "%02.3f" % (seconds % 60)
    return getTime

""" get transcriptions into dictionary {1 : ['abc', 'def', 'ghi']} """
AllTranscriptions = {}
with open(LisToTranscriptions, mode='rU') as f:
    reader = csv.reader(f)
    for num, row in enumerate(reader):
        key = row[0]
        value = {"1":row[1],"2":row[2],"3":row[3],"4":row[4],"5":row[5],"6":row[6],"7":row[7]}
        AllTranscriptions[key] = value

""" get syllables duration into dictionary {1 : ['abc', 'def', 'ghi']} """
AllSyllablesDuration = {}
with open(SyllableDurationFile, mode='rU') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the headers
    lkey = FolderName + "1"
    for num, row in enumerate(reader):
        if row[0] == lkey:
            if lkey not in AllSyllablesDuration:
                AllSyllablesDuration[lkey] = {}
            key = int(row[1])
            value = float(row[2])
            AllSyllablesDuration[lkey][key] = value
        else:
            lkey = row[0]
            if lkey not in AllSyllablesDuration:
                AllSyllablesDuration[lkey] = {}
            key = int(row[1])
            value = float(row[2])
            AllSyllablesDuration[lkey][key] = value
#for x in AllSyllablesDuration:
#    print(x, AllSyllablesDuration[x])

AllStarttimes = {}
with open(SyllableStartFile, mode='rU') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the headers
    for num, row in enumerate(reader):
        AllStarttimes[row[0]] = row[1]

""" create/check for  the json output directory"""
if not os.path.exists(JsonOutputDirectory):
    os.makedirs(JsonOutputDirectory)
else:
    pass

for wav in os.listdir(AudioFolder):
    if wav.startswith('.'):
        continue
    baseName = os.path.splitext(os.path.basename(wav))[0]
    wav = AudioFolder + wav

    with contextlib.closing(wave.open(wav,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        time = float(frames / float(rate))

        """edit time format to hh:mm:ss """
        timeHMS = time_format_converter(time)

        SampleStarttime = AllStarttimes.get(baseName)
        SampleSylDurations = AllSyllablesDuration.get(baseName)
        SampleDuration = sum(SampleSylDurations.values())
        TranscriptionSyllables = AllTranscriptions.get(baseName[2:])

        FoTime = DataFolder + baseName + ".csv"
        ContourData = {}
        with open(FoTime, mode='rU') as f:
            reader = csv.reader(f)
            for num, row in enumerate(reader):
                key = row[0]
                value = row[1]
                ContourData[key] = value


        #print(baseName,SampleStarttime,SampleDuration,SampleSylDurations,TranscriptionSyllables)


        JsonDict = {"SampleName": baseName,"SyllablesDuration": SampleSylDurations,"StartTime": SampleStarttime,"SampleDuration": SampleDuration,"SampleText": TranscriptionSyllables,"ContourData": ContourData}












        jfile = JsonOutputDirectory + baseName + ".json"
        with open(jfile, 'w') as outfile:
            json.dump(JsonDict, outfile, indent=4)
