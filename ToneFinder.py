from __future__ import division
import  sys, os, csv, pylab, math
from dataInjection import DataFromCsv
from terminaltables import AsciiTable
from collections import OrderedDict

from sys import argv

script, name = argv



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
        fo = self.getFoValues()
        min_fo = self.getFoStats()[2] # Baseline can be set to n points under actual value
        max_fo = self.getFoStats()[1]
        range_fo = max_fo - min_fo
        fo_list_scaled = [round((item - min_fo) * (100.0/range_fo),0) for item in fo]
        return fo_list_scaled

    def scaleFoERB(self):
        fo = self.getFoValues()
        fo_list_scaled = [round((21.4 * math.log10((0.00437 * item) +1))*10,0) for item in fo]
        return fo_list_scaled

################################################################################
##
#   time scaling methods:
#   percentage (PCT)
#   isometric grid
#
    def getBoundariesPCT(self):
        boundaries = self.getFrameBoundaries(self.frames_per_syllable)
        min_time = boundaries[0]
        max_time = boundaries[-1]
        range_time = max_time - min_time
        boundaries_scaled = [(item - min_time) * (100.0/range_time) for item in boundaries]
        return boundaries_scaled

    def scaleTimePCT(self): # Returns time values scalded to percentages,
                            # relatively to minimum and maximum values #
        time = self.getTimeValues()
        boundaries = self.getFrameBoundaries(self.frames_per_syllable)
        min_time = boundaries[0]
        max_time = boundaries[-1]
        range_time = max_time - min_time
        time_list_scaled = [(item - min_time) * (100.0/range_time) for item in time]
        return time_list_scaled

    def scaleTimeIsometric(self):
        frame_boundaries_scaled = self.getBoundariesPCT()
        target_frame_size = 100.0 / self.getTotalFrameNumber()
        #print("ref:", target_frame_size, len(self.retrieveSpans()), self.frames_per_syllable)
        isometric_time = []
        for x in self.scaleTimePCT():
            for boundary in frame_boundaries_scaled:
                if x > boundary and x <= frame_boundaries_scaled[frame_boundaries_scaled.index(boundary) + 1]:
                    syl_span =   frame_boundaries_scaled[frame_boundaries_scaled.index(boundary) + 1] - frame_boundaries_scaled[frame_boundaries_scaled.index(boundary)]
                    #print("SPAN", syl_span)
                    cumul = frame_boundaries_scaled.index(boundary) * target_frame_size
                    adjusted_x = (((x - boundary) / syl_span) * target_frame_size) + cumul
                    #print(frame_boundaries_scaled.index(boundary), x, adjusted_x, syl_span, cumul)
                    isometric_time.append(adjusted_x)
        #print("LEN ADJUSTED TIME", len(isometric_time))
        return isometric_time

################################################################################
##
#   pretones
#
    def getPretones(self):
        fo = self.scaleFoPCT()
        boundaries = self.getBoundariesPCT()
        isometric_time = self.scaleTimeIsometric()
        x = 0
        first_pretone = x, 0, isometric_time[0], fo[0]
        pretones = [first_pretone]
        for left_boundary in boundaries:
            if boundaries.index(left_boundary) == len(boundaries) - 1:
                break
            else:
                x += 1
                right_boundary = boundaries[boundaries.index(left_boundary)+1]
                pre_time_indexed = [(ind, x) for ind, x in enumerate(isometric_time) if x > left_boundary and x <= right_boundary]
                pre_indexes = [x[0] for x in pre_time_indexed]
                pre_time = [x[1] for x in pre_time_indexed]
                pre_fo = []
                for i in pre_indexes:
                    pre_fo.append(fo[i])
                group = list(zip(pre_indexes, pre_time, pre_fo))
                if not group:
                    pass
                else:
                    max_pre = max(group, key=lambda item:item[2])
                    min_pre = min(group, key=lambda item:item[2])
                    # recompose tuples
                    max_pre = x, max_pre[0], max_pre[1], max_pre[2]
                    min_pre = x, min_pre[0], min_pre[1], min_pre[2]
                    if max_pre[1] > min_pre[1]:
                        pretones.append(min_pre)
                        pretones.append(max_pre)
                    else:
                        pretones.append(max_pre)
                        pretones.append(min_pre)
        x += 1
        last_pretone_index = len(fo) - 1
        last_pretone = x , last_pretone_index, isometric_time[last_pretone_index], fo[last_pretone_index]
        pretones.append(last_pretone)
        return pretones
        #IF FIRST GROUP check if duplicate with first
        #IF MAX = MIN, differentiate

################################################################################
##
#   tones
#
    def getTones(self):
        pretones = self.getPretones()
        TL = pretones[0]
        TR = pretones[-1]
        pretones = pretones[1:-1]
        first_pre_max = max(pretones, key=lambda item:item[3])
        second_pre_max = max(pretones, key=lambda item:item[3])
        if first_pre_max[3] >= second_pre_max[3]:
            H = first_pre_max
        else:
            H = second_pre_max
        print("H : ", H)
        for x in pretones:
            print(x[0], x[1], x[2], x[3])






################################################################################
##
#   movement detection tools
#
    def mvtDetectionScan(self):
        fo_list = self.scaleFoPCT()
        time_list = self.scaleTimePCT()
        list_length = len(fo_list)
        #print(len(time_list),len(fo_list))
        init = fo_list[0]
        prev_scan = 0
        fo_mvt_list = []
        index_list = []
        #print("///", fo_mvt_list, index_list)
        for i,  x in enumerate(fo_list):
            #print(i,x, list_length - 1, fo_list[i-1])
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
            else:# scan_check == 0 and prev_scan == 1:
                fo_mvt_list.append(x)
                index_list.append(i)

        time_mvt_list = [x for x in time_list if time_list.index(x) in index_list ]
        #print("...", len(index_list),len(fo_mvt_list),len(time_mvt_list),'\n',index_list,'\n', fo_mvt_list,'\n',time_mvt_list)
        mvt_raw = list(zip(time_mvt_list, fo_mvt_list))
        return mvt_raw, index_list


    def printMvtDetectionScan(self):    # writes data into php file to be used
                                        # for front-end visualization
        name = self.getTokenTag()
        # RAW SCAN
        mvt_list = self.mvtDetectionScan()[0]
        #print(self.getTokenTag() + " has " + str(len(mvt_list)) + " turning points.")
        mydata = "/Applications/XAMPP/xamppfiles/htdocs/oftenback/linguistics/raw_scan.php"
        with open(mydata, 'w') as myphpfile:
            #add line data
            myphpfile.write("var lineData = [  \n")
            for pair in mvt_list:
                row = "{ 'x': " + str(pair[0]*3.99 + 32) + ", 'y': " + str(217 - pair[1] * 1.8) +  " },\n"
                myphpfile.write(row)
            myphpfile.write(" ];")
            #add boundary data
            boundaries = self.getBoundariesPCT()
            myphpfile.write("var boundaryData = [  \n")
            for position in boundaries:
                row = "{ 'xa': " + str(position*3.99 + 32) + ", 'ya': " + "35" + ", 'xb': " + str(position*3.99 + 32) + ", 'yb' : " + "217" + " },\n"
                myphpfile.write(row)
            myphpfile.write(" ];")
            #add title variable
            myphpfile.write("\n var title = '" + name + "';")
            #add fo stats variables
            stats = self.getFoStats()
            myphpfile.write("\n var fo_mean = '" + str(int(stats[0])) + "';")
            myphpfile.write("\n var fo_max = '" + str(int(stats[1])) + "';")
            myphpfile.write("\n var fo_min = '" + str(int(stats[2])) + "';")


        myphpfile.close()
        #for attribute, value in sorted_mvt_dict.items():
        #    print('[{}, {}],'.format(attribute, round(320 - value,0)))

        # PRETONES
        mydata_b = "/Applications/XAMPP/xamppfiles/htdocs/oftenback/linguistics/pretones.php"
        pretones_data = self.getPretones()
        with open(mydata_b, 'w') as myphpfile_b:
            #add line data
            myphpfile_b.write("var lineData = [  \n")
            for pretone in pretones_data:
                row = "{ 'x': " + str(pretone[2]*3.99 + 32) + ", 'y': " + str(217 - pretone[3]  * 1.8) +  " },\n"
                myphpfile_b.write(row)


            myphpfile_b.write(" ];")
            #add boundary data
            boundary_numbers = int(self.getTotalFrameNumber() + 1)
            target_frame_size = 100.0 / self.getTotalFrameNumber()
            i = 1
            boundaries = [0.0]
            while i in range(boundary_numbers):
                boundaries.append(i * float(target_frame_size))
                i += 1
            myphpfile_b.write("var boundaryData = [  \n")
            for position in boundaries:
                row = "{ 'xa': " + str(position*3.99 + 32) + ", 'ya': " + "35" + ", 'xb': " + str(position*3.99 + 32) + ", 'yb' : " + "217" + " },\n"
                myphpfile_b.write(row)
            myphpfile_b.write(" ];")
            #add title variable
            myphpfile_b.write("\n var title = '" + name + "';")
        myphpfile_b.close()












# TESTING #
token = ContourFromCsv("./EM/foCsv/EM" + name + ".csv", "./EM/syllabletime.txt", "./EM/starttimes.txt")
#print(token.csvToLists())
#print(token.retrieveSpans())
#print("fo pct : ", token.scaleFoPCT())
#print(token.scaleFoERB())
#print("time pct : ", token.scaleTimePCT())
#print(len(token.scaleFoPCT()))
#print(len(token.scaleTimePCT()))
#print("RAW", token.getRawTimeValues())
#print("TRIMMED", token.getTimeValues())
#print("TRIM",token.trimSampleIndex())
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
#print("frame list: ", token.getFrameBoundaries(2.0))
#print(token.retrieveSpans())
#print("mvtdetec : ",token.mvtDetectionScan())
#print(token.scaleTimeIsometric())
#for x in token.getPretones():
#    print(x)
print(len(token.getPretones()))
token.getTones()
token.printMvtDetectionScan()

batch_test = False
pretone_len = []
if batch_test is True:
    listing = os.listdir('./EM/foCsv')
    for fichier in listing:
        target_file = "./EM/foCsv/" + fichier
        #print(target_file)
        token = ContourFromCsv(target_file, "./EM/syllabletime.txt", "./EM/starttimes.txt")
        pretone_len.append(len(token.getPretones()))
        #token.printMvtDetectionScan()
    print(pretone_len)
