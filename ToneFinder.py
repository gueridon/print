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

    number_of_frames = 2.0

    def getTimeValues(self):
        return self.csvToLists()[0]

    def getFoValues(self):
        return self.csvToLists()[1]

    def getFoStats(self):
        mean_fo = sum(self.getFoValues()) / float(len(self.getFoValues()))
        max_fo = max(self.getFoValues())
        min_fo = min(self.getFoValues())
        return mean_fo, max_fo, min_fo

    def overallDurations(self):
        sample_duration =  max(self.getTimeValues()) - min(self.getTimeValues())

        leftmost_boundary = self.getStartTime()
        rightmost_boundary = self.getFrameBoundaries(self.number_of_frames)[-1]
        token_duration = rightmost_boundary - leftmost_boundary

        duration_error = False
        if token_duration > sample_duration:
            duration_error = True

        return sample_duration, token_duration, duration_error

    def getLongestSyllable(self):
        syllables = self.retrieveSpans()
        #longest_syllable = [(key,value) for key,value in syllables.items() if value == max(syllables.values())]
        #return float(longest_syllable[0][1])
        longest_syllable_duration = max(syllables)
        longest_syllable_position = syllables.index(longest_syllable_duration)
        return float(longest_syllable_duration), int(longest_syllable_position)

    def getLeftmostBoundary(self):
        return self.getStartTime()

    def getFrameBoundaries(self, number_of_frame_per_syllable):
        """ Start time of the sample is used as initial value to which frame
            lengths are added consecutively """
        frameboundary = self.getLeftmostBoundary()
        spans = self.retrieveSpans()
        frames = [(float(x))/float(number_of_frame_per_syllable)  for x in spans]
        #print("frame values: ",frames)
        frame_list = []
        for x in frames:
            frameboundary = frameboundary + x
            frame_list.append(float(frameboundary))
            frameboundary = frameboundary + x
            frame_list.append(float(frameboundary))
        return frame_list

######################################################################
##
#   fo scaling methods:
#   percentage (PCT)
#   Equivalent Rectangular Bandwith (ERB)
#
    def scalePCT(self):
        min_fo = self.getFoStats()[2] - 10 # Baseline is set to n points under actual value
        max_fo = self.getFoStats()[1]
        range_fo = max_fo - min_fo
        fo_list_scaled = [round((item - min_fo) * (100.0/range_fo),0) for item in self.getFoValues()]
        return fo_list_scaled

    def scaleERB(self):
        fo_list_scaled = [round((21.4 * math.log10((0.00437 * item) +1))*10,0) for item in self.getFoValues()]
        return fo_list_scaled

######################################################################
##
#   general movement detection tool
#
    def mvtDetectionScan(self):
        fo_list = self.getFoValues()
        list_length = len(fo_list)
        init = fo_list[0]
        prev_scan = 0
        value_list = [fo_list[0]]
        index_list = [fo_list.index(fo_list[0])]
        for i,  x in enumerate(fo_list):
            #this compare each value in the list to the next
            if i < list_length - 1: #all values in the list but the last.
                if x < fo_list[i+1]:
                    scan_check = 0
                elif x == fo_list[i+1]:
                    scan_check = 0
                elif x > fo_list[i+1]:
                    scan_check = 1
            else:# last value in the list is compared to the previous one.
                if x < fo_list[i-1]:
                    scan_check = 0
                elif x == fo_list[i-1]:
                    scan_check = 0
                elif x > fo_list[i-1]:
                    scan_check = 1
                value_list.append(x)
                index_list.append(i)
            # this keeps track of the movement and finds raw H and L points.
            if scan_check == prev_scan:
                continue
            elif scan_check == 0 and prev_scan == 1:
                value_list.append(x)
                index_list.append(i)
            elif scan_check == 1 and prev_scan == 0:
                value_list.append(x)
                index_list.append(i)
            prev_scan = scan_check
        mvt_raw = dict(zip(index_list, value_list))
        return mvt_raw

    def printMvtDetectionScan(self):
        mvt_dict = self.mvtDetectionScan()
        sorted_mvt_dict = OrderedDict(sorted(mvt_dict.items()))


        print(len(mvt_dict))


        with open('mydata.csv', 'w') as mycsvfile:
            thedatawriter = csv.writer(mycsvfile, delimiter=',')
            for attribute, value in sorted_mvt_dict.items():
                row = attribute, value
                thedatawriter.writerow(row)




        for attribute, value in sorted_mvt_dict.items():
            print('{}, {}'.format(attribute, value))









""" TESTING """
token = ContourFromCsv("./EM/foCsv/EM1.csv", "./EM/syllabletime.txt", "./EM/starttimes.txt")
#print(token.csvToLists())
#print(token.retrieveSpans())
print(token.scalePCT())
print(token.scaleERB())
#print(token.getTimeValues())
table_data = [
    [token.getTokenTag(), ''],
    ['fo stats', (round(token.getFoStats()[0],2),round(token.getFoStats()[1],2),round(token.getFoStats()[2],2))],
    ['longest syllable', (round(token.getLongestSyllable()[0],2), token.getLongestSyllable()[1])],
    ['start time', round(token.getLeftmostBoundary(),2)],
    ['sample duration', round(token.overallDurations()[0],2)],
    ['token duration', round(token.overallDurations()[1],2)],
    ['duration error', token.overallDurations()[2]]
]
table = AsciiTable(table_data)
print(table.table)
print("frame list: ", token.getFrameBoundaries(2.0))
print(token.retrieveSpans())
print(token.mvtDetectionScan())
a = token.printMvtDetectionScan()
