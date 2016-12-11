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

    frames_per_syllable = 2.0


################################################################################
##
#   methods to acquire data from files
#
    def getRawTimeValues(self): # Get sample's time values (from data file) #
        return self.csvToLists()[0]

    def getRawFoValues(self): # Get sample's fo values (from data file) #
        return self.csvToLists()[1]

    def getLeftmostBoundary(self): # Get token's start time value (from data file) #
        return self.getStartTime()

################################################################################
##
#   data cleaning
#
    def trimSampleIndex(self): # Returns the index token's value only #
        time = self.getRawTimeValues()
        boundaries = self.getFrameBoundaries(self.frames_per_syllable)
        origin_sample = boundaries[0]
        end_sample = boundaries[-1]
        trimmed_index_list = []
        for item in time:
            if item >= origin_sample and item <= end_sample:
                index_item = time.index(item)
                trimmed_index_list.append(index_item)
        return trimmed_index_list

    def getTimeValues(self): # Excludes time values not in the token #
        time_list = self.getRawTimeValues()
        in_range_list = self.trimSampleIndex()
        return [x for x in time_list if time_list.index(x) in in_range_list ]

    def getFoValues(self): # Excludes fo values not in the token #
        fo_list = self.getRawFoValues()
        in_range_list = self.trimSampleIndex()
        return [x for x in fo_list if fo_list.index(x) in in_range_list ]

################################################################################
##
#   descriptive statistics
#
    def getFoStats(self): # Computes token's statistics on fo: mean, max, min #
        mean_fo = sum(self.getFoValues()) / float(len(self.getFoValues()))
        max_fo = max(self.getFoValues())
        min_fo = min(self.getFoValues())
        return mean_fo, max_fo, min_fo

    def getTimeStats(self): # Computes token's statistics on time: max, min #
        max_time = max(self.getTimeValues())
        min_time = min(self.getTimeValues())
        return max_time, min_time

    def overallDurations(self): # Computes sample's duration & token's duration
                                # Compares both and reports an error if token's
                                # duration is longer than sample's duration #
        sample_duration =  max(self.getTimeValues()) - min(self.getTimeValues())

        leftmost_boundary = self.getStartTime()
        rightmost_boundary = self.getFrameBoundaries(self.frames_per_syllable)[-1]
        token_duration = rightmost_boundary - leftmost_boundary

        duration_error = False
        if token_duration > sample_duration:
            duration_error = True

        return sample_duration, token_duration, duration_error

################################################################################
##
#   syllables & frames
#
    def getLongestSyllable(self):   # Returns the longest syllable's duration
                                    # and its position in the token
        syllables = self.retrieveSpans()
        #longest_syllable = [(key,value) for key,value in syllables.items() if value == max(syllables.values())]
        #return float(longest_syllable[0][1])
        longest_syllable_duration = max(syllables)
        longest_syllable_position = syllables.index(longest_syllable_duration)
        return float(longest_syllable_duration), int(longest_syllable_position)

    def getFrameBoundaries(self, nbr_of_frames_per_syllable):
                                   # Return the list of all syllable boundaries.
                                   # Start time of the sample is used as initial
                                   # value to which frame lengths are added consecutively
        frameboundary = self.getLeftmostBoundary()
        spans = self.retrieveSpans()
        frames = [(float(x))/float(nbr_of_frames_per_syllable)  for x in spans]
        #print("frame values: ",frames)
        frame_list = [frameboundary]
        #counter = 1
        #print(counter,frameboundary)
        for x in frames:
            frameboundary = frameboundary + x
            frame_list.append(float(frameboundary))
            #counter += 1
            #print(counter,frameboundary)
            frameboundary = frameboundary + x
            frame_list.append(float(frameboundary))
            #counter += 1
            #print(counter,frameboundary)
        return frame_list

    def getTotalFrameNumber(self):  # returns overall number of frames
                                    # in the token
        return float(len(self.retrieveSpans())) * self.frames_per_syllable


################################################################################
##
#   fo scaling methods:
#   percentage (PCT)
#   Equivalent Rectangular Bandwith (ERB)
#
    def scaleFoPCT(self):   # Returns fo values scaled to percentages,
                            # relatively to minimum and maximum values
        min_fo = self.getFoStats()[2] # Baseline can be set to n points under actual value
        max_fo = self.getFoStats()[1]
        range_fo = max_fo - min_fo
        fo_list_scaled = [round((item - min_fo) * (100.0/range_fo),0) for item in self.getFoValues()]
        return fo_list_scaled

    def scaleFoERB(self):
        fo_list_scaled = [round((21.4 * math.log10((0.00437 * item) +1))*10,0) for item in self.getFoValues()]
        return fo_list_scaled

################################################################################
##
#   time scaling methods:
#   percentage (PCT)
#   pretones - isometric grid
#
    def scaleTimePCT(self): # Returns time values scalded to percentages,
                            # relatively to minimum and maximum values #
        min_time = self.getFrameBoundaries(self.frames_per_syllable)[0]
        max_time = self.getFrameBoundaries(self.frames_per_syllable)[-1]
        range_time = max_time - min_time
        time_list_scaled = [round((item - min_time) * (100.0/range_time),0) for item in self.getTimeValues()]
        return time_list_scaled

    def scaleTimeIsometric(self):
        min_time = self.getFrameBoundaries(self.frames_per_syllable)[0]
        max_time = self.getFrameBoundaries(self.frames_per_syllable)[-1]
        range_time = max_time - min_time
        frame_boundaries = self.getFrameBoundaries(self.frames_per_syllable)
        frame_boundaries_scaled = [round((item - min_time) * (100.0/range_time),0) for item in frame_boundaries]

        target_frame_size = 100.0 / self.getTotalFrameNumber()
        #print("ref:", target_frame_size, len(self.retrieveSpans()), self.frames_per_syllable)
        adjusted_time = []
        for x in self.scaleTimePCT():
            for boundary in frame_boundaries_scaled:
                if x > boundary and x <= frame_boundaries_scaled[frame_boundaries_scaled.index(boundary) + 1]:
                    syl_span =   frame_boundaries_scaled[frame_boundaries_scaled.index(boundary) + 1] - frame_boundaries_scaled[frame_boundaries_scaled.index(boundary)]
                    #print("SPAN", syl_span)
                    cumul = frame_boundaries_scaled.index(boundary) * target_frame_size
                    adjusted_x = (((x - boundary) / syl_span) * target_frame_size) + cumul
                    #print(frame_boundaries_scaled.index(boundary), x, adjusted_x, syl_span, cumul)
                    adjusted_time.append(adjusted_x)
        print("LEN ADJUSTED TIME", len(adjusted_time))
        return adjusted_time





        #return frame_boundaries_scaled


################################################################################
##
#   movement detection tools
#
    def mvtDetectionScan(self):
        fo_list = self.scaleFoPCT()
        time_list = self.scaleTimePCT()
        list_length = len(fo_list)
        init = fo_list[0]
        prev_scan = 0
        fo_mvt_list = [fo_list[0]]
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
                fo_mvt_list.append(x)
                index_list.append(i)
            # this keeps track of the movement and finds raw H and L points.
            if scan_check == prev_scan:
                continue
            elif scan_check == 0 and prev_scan == 1:
                fo_mvt_list.append(x)
                index_list.append(i)
            elif scan_check == 1 and prev_scan == 0:
                fo_mvt_list.append(x)
                index_list.append(i)
            prev_scan = scan_check

        time_mvt_list = [x for x in time_list if time_list.index(x) in index_list ]
        mvt_raw = dict(zip(time_mvt_list, fo_mvt_list))
        return mvt_raw, index_list

    def printMvtDetectionScan(self):
        mvt_dict = self.mvtDetectionScan()[0]
        sorted_mvt_dict = OrderedDict(sorted(mvt_dict.items()))
        print(self.getTokenTag() + " has " + str(len(mvt_dict)) + " turning points.")
        mydata = "/Applications/XAMPP/xamppfiles/htdocs/oftenback/linguistics/demo_data.php"
        row_count = 0
        with open(mydata, 'w') as myphpfile:
            myphpfile.write("var lineData = [  \n")
            for attribute, value in sorted_mvt_dict.items():
                row = "{ 'x': " + str(attribute*3.99 + 25) + ", 'y': " + str(209 - value * 2) +  " },\n"


                #row_count +=1
                #if row_count > 1:
                #    row = "L " + str(attribute*4) + " " + str(round(200 - value,1)) + "\n"
                #else:
                #    row = "M " + str(attribute*4) + " " + str(round(200 - value,1)) + "\n"
                myphpfile.write(row)
            myphpfile.write(" ];")
            myphpfile.write("\n var title = '" + self.getTokenTag() + "';")
        #for attribute, value in sorted_mvt_dict.items():
        #    print('[{}, {}],'.format(attribute, round(320 - value,0)))









# TESTING #
token = ContourFromCsv("./EM/foCsv/EM18.csv", "./EM/syllabletime.txt", "./EM/starttimes.txt")
#print(token.csvToLists())
#print(token.retrieveSpans())
print(token.scaleFoPCT())
#print(token.scaleFoERB())
print(token.scaleTimePCT())
print(len(token.scaleFoPCT()))
print(len(token.scaleTimePCT()))
#print("RAW", token.getRawTimeValues())
#print("TRIMMED", token.getTimeValues())
print("TRIM",token.trimSampleIndex())
table_data = [
    [token.getTokenTag(), ''],
    ['fo stats', (round(token.getFoStats()[0],2),round(token.getFoStats()[1],2),round(token.getFoStats()[2],2))],
    ['longest syllable', (round(token.getLongestSyllable()[0],2), token.getLongestSyllable()[1])],
    ['start time', round(token.getLeftmostBoundary(),2)],
    ['sample duration', round(token.overallDurations()[0],2)],
    ['token duration', round(token.overallDurations()[1],2)],
    ['token != sample', token.overallDurations()[2]]
]
table = AsciiTable(table_data)
print(table.table)
print("frame list: ", token.getFrameBoundaries(2.0))
print(token.retrieveSpans())
print(token.mvtDetectionScan())
print(token.scaleTimeIsometric())
print(token.scaleTimeIsometric())

token.printMvtDetectionScan()

batch_test = False
if batch_test is True:
    listing = os.listdir('./EM/foCsv')
    for fichier in listing:
        target_file = "./EM/foCsv/" + fichier
        print(target_file)
        token = ContourFromCsv(target_file, "./EM/syllabletime.txt", "./EM/starttimes.txt")
        token.printMvtDetectionScan()
