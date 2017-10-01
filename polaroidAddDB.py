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
import pymysql
import pymysql.cursors



conn = pymysql.connect(host='localhost', user='root', passwd='pasteque', db='Polaroids')

cur = conn.cursor()

cur.execute("SELECT * FROM polaroid_db")

#print(cur.description)
#for row in cur:
#    print(row)


imagesFolder = '/var/www/html/imagesFolder/polaroidArchive/batchSingles/'

for path, subdirs, files in os.walk(imagesFolder):
   for filename in files:
       if not filename.startswith('.'):
           if not '_v' in filename:
               baseName = str(os.path.splitext(filename)[0])
               largePic = str('./imagesFolder/polaroidArchive/all/' + filename)
               smallPic = str('./imagesFolder/polaroidArchive/all/' + baseName + '_v.jpg')
               date = baseName[:-4]
               datePic = date.replace("_", "-")
               webPic = 'yes'
               print(baseName,datePic,largePic,smallPic,webPic)

               cur.execute("""INSERT INTO polaroid_db (uid, date, file, vignette, web) VALUES(%(uid)s, %(date)s, %(file)s, %(vignette)s, %(web)s)""",{'uid': baseName,'date': datePic,'file': largePic,'vignette': smallPic,'web': webPic})



cur.close()
conn.commit()
conn.close()
