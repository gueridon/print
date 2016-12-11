from __future__ import division
import  sys, os, csv, pylab, math
from dataInjection import DataFromCsv
from terminaltables import AsciiTable
from collections import OrderedDict

class ContourFromCsv(DataFromCsv):

    def __init__(self,contour_data, syllable_data, origin_data): #,syllablecsv):
        super().__init__(contour_data,syllable_data,origin_data)

        self.fo_time = contour_data
        self.spans = syllable_data
        self.origins = origin_data

    @classmethod
    def getRawTimeValues(cls, blah): # Get sample's time values (from data file) #
        return blah * 2

token = ContourFromCsv("./EM/foCsv/EM1.csv", "./EM/syllabletime.txt", "./EM/starttimes.txt")
ContourFromCsv.getRawTimeValues(2)
