import json
from sys import argv
from pprint import pprint
import glob, sys, time, re, wave
import os, os.path
import csv
import contextlib



#global parameters
script, FolderName = argv

JsonOutputDirectory = "./questionData/"+FolderName+"/json/"

JsonFile = JsonOutputDirectory + "EM1.json"

with open(JsonFile) as data_file:
    data = json.load(data_file)

x = data["ContourData"]
for key, value in x.items():
    print(key, value)
