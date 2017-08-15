import glob, sys, time, re, argparse
import os, os.path
from os.path import basename
from xml.etree import ElementTree
import csv
import lxml.builder
import lxml.etree
import contextlib
import wave
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from sys import argv
import sqlite3

db = sqlite3.connect('printaudio.db')
c = db.cursor()
# Create table

c.execute('''
    DROP TABLE IF EXISTS questions
''')


c.execute('''
    CREATE TABLE questions (id TEXT PRIMARY KEY,
                        length REAL,
                        duration REAL,
                        starttime REAL,
                        transcription TEXT,
                        numberofsyllables REAL)
''')







#global parameters
script, folderName = argv

"""Remove empty lines after tree re-write"""
def noblanklinetree(xmlfile):
    with open(xmlfile,"r") as f:
        lines = f.readlines()
    with open(xmlfile,"w") as f:
        [f.write(line) for line in lines if line.strip() ]

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")



def timeFormatConverter(time):
    """time format converter
    """
    seconds = time
    minutes = seconds // 60
    hours = minutes // 60
    getTime =  "%02.3f" % (seconds % 60)
    return getTime







listoTranscriptions = "./questionData/questionList.csv"
audioFolder = "./questionData/"+folderName+"/audio/"
syllableStartFile = "./questionData/"+folderName+"/starttimes.csv"
syllableDurationFile = "./questionData/"+folderName+"/syllabletime.csv"
xmloutputDirectory = "./questionData/"+folderName+"/xml/"

""" get transcriptions into dictionary {1 : ['abc', 'def', 'ghi']} """
allTranscriptions = {}
with open(listoTranscriptions, mode='rU') as f:
    reader = csv.reader(f)
    for num, row in enumerate(reader):
        key = row[0]
        value = [row[1],row[2],row[3],row[4],row[5],row[6],row[7]]
        allTranscriptions[key] = value

""" get syllables duration into dictionary {1 : ['abc', 'def', 'ghi']} """
allSyllablesDuration = {}
with open(syllableDurationFile, mode='rU') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the headers
    lkey = folderName + "1"
    for num, row in enumerate(reader):
        if row[0] == lkey:
            if lkey not in allSyllablesDuration:
                allSyllablesDuration[lkey] = {}
            key = int(row[1])
            value = float(row[2])
            allSyllablesDuration[lkey][key] = value
        else:
            lkey = row[0]
            if lkey not in allSyllablesDuration:
                allSyllablesDuration[lkey] = {}
            key = int(row[1])
            value = float(row[2])
            allSyllablesDuration[lkey][key] = value
for x in allSyllablesDuration:
    print(x, allSyllablesDuration[x])

allStarttimes = {}
with open(syllableStartFile, mode='rU') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the headers
    for num, row in enumerate(reader):
        allStarttimes[row[0]] = row[1]






""" create/check for  the xml output directory"""
if not os.path.exists(xmloutputDirectory):
    os.makedirs(xmloutputDirectory)
else:
    pass

for wav in os.listdir(audioFolder):
    if wav.startswith('.'):
        continue
    baseName = os.path.splitext(os.path.basename(wav))[0]
    wav = audioFolder + wav
    with contextlib.closing(wave.open(wav,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        time = float(frames / float(rate))

        """edit time format to hh:mm:ss """
        timeHMS = timeFormatConverter(time)

        sampleStarttime = allStarttimes.get(baseName)
        sampleSylDurations = allSyllablesDuration.get(baseName)
        sampleDuration = sum(sampleSylDurations.values())
        transcriptionSyllables = allTranscriptions.get(baseName[2:])



        top = Element('sample')
        comment = Comment('nicholas bacuez')
        top.append(comment)

        identifier = SubElement(top, 'id')
        identifier.text = baseName


        time = SubElement(top, 'time')

        length = SubElement(time, 'fileduration')
        length.text = timeHMS

        duration = SubElement(time, 'sampleduration')
        duration.text = str(sampleDuration)

        starttime = SubElement(time, 'starttime')
        starttime.text = sampleStarttime

        transcription = SubElement(top, 'transcription')
        transcription.text = ' '.join(transcriptionSyllables)





        

        c.execute("DROP TABLE IF EXISTS "+ baseName)
        c.execute("CREATE TABLE "+ baseName +" (syllable TEXT PRIMARY KEY, duration REAL)")

        syllables = SubElement(top, 'syllables')
        x = 1
        y = float(sampleStarttime)
        while x <= len(sampleSylDurations):
            syl = SubElement(syllables, 'syl')
            #syl.set('sylref', str(x) )
            syllableRef = SubElement(syl, 'syllableRef')
            syllableRef.text = str(x)

            syllableduration = SubElement(syl, 'syllableduration')
            syllableduration.text = str(sampleSylDurations.get(x))

            if x > 1:
                if x-1 in sampleSylDurations:
                    y += sampleSylDurations.get(x-1)
                elif x-2 in sampleSylDurations:
                    y += sampleSylDurations.get(x-2)
            syllablestart = SubElement(syl, 'syllablestart')
            syllablestart.text = str(y)

            syllabletext = SubElement(syl, 'syllabletext')
            syllabletext.text = transcriptionSyllables[x-1]
            x += 1

        #print(prettify(top))


        # Insert sample into table
        transcript = ' '.join(transcriptionSyllables)
        c.execute('''INSERT INTO questions (id, length, duration, starttime,transcription)
                  VALUES(?,?,?,?,?)''', (baseName,timeHMS, sampleDuration, sampleStarttime,transcript))



        k = xmloutputDirectory + baseName + ".xml"
        #print(k)
        tostring(top)
        newtree =  prettify(top)
        output_file = open(k, 'wb' )
        #output_file.write( '<?xml version="1.0"?>' )
        #newtree = newtree.encode('ascii', 'ignore')
        newtree = newtree.encode('utf8')
        output_file.write(newtree)
        output_file.close()
        noblanklinetree(k)


db.commit()
db.close()
