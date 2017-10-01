from __future__ import division
import  sys, os, csv, pylab, math
from dataInjection import DataFromCsv
from terminaltables import AsciiTable
from collections import OrderedDict
from itertools import chain
from operator import itemgetter
import time

from printModule import *
import printConfig

from sys import argv

#global parameters
#script, printConfig.gb_debug, printConfig.gp_batch, printConfig.gp_number_of_frames, printConfig.gp_number_of_tones, printConfig.gp_name = argv

class ContourFromCsv(DataFromCsv):

    def __init__(self,contour_data, syllable_data, origin_data, nof): #,syllablecsv):
        super().__init__(contour_data,syllable_data,origin_data)

        self.fo_time = contour_data
        self.spans = syllable_data
        self.origins = origin_data


        self.frames_per_syllable = float(nof)

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
            for _ in range(int(nbr_of_frames_per_syllable)):
                frameboundary = frameboundary + x
                frame_list.append(float(frameboundary))
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

    def scaleFoBARK(self):
        fo = self.getFoValues()
        fo_list_scaled = [round(6 * math.asinh(item / 600),0) * 25 for item in fo]
        return fo_list_scaled

    def scaleFoMEL(self):
        fo = self.getFoValues()
        fo_list_scaled = [round((2595 * math.log10((0.0014286 * item) +1))/5,0) for item in fo]
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
        if printConfig.scalingMethod == 'PCT':
            fo = self.scaleFoPCT()
        elif printConfig.scalingMethod == 'ERB':
            fo = self.scaleFoERB()
        elif printConfig.scalingMethod == 'BRK':
            fo = self.scaleFoBARK()
        elif printConfig.scalingMethod == 'MEL':
            fo = self.scaleFoMEL()
        #print("len fo", len(fo))
        boundaries = self.getBoundariesPCT()
        isometric_time = self.scaleTimeIsometric()
        x = 0
        first_pretone = x, 0, isometric_time[0], fo[0]
        pretones = [first_pretone]
        for left_boundary in boundaries:
            if boundaries.index(left_boundary) == len(boundaries) - 1:
                continue
            elif x + 1 == len(fo):
                continue
            else:
                x += 1
                right_boundary = boundaries[boundaries.index(left_boundary)+1]
                pre_time_indexed = [(ind, x) for ind, x in enumerate(isometric_time) if x > left_boundary and x <= right_boundary]
                pre_indexes = [x[0] for x in pre_time_indexed]
                #print(pre_indexes)
                pre_time = [x[1] for x in pre_time_indexed]
                pre_fo = []
                for i in pre_indexes:
                    #print(i, fo[i-1]) #CHANGE
                    pre_fo.append(fo[i]) #CHANGE
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
        #print(last_pretone_index)
        last_pretone = x , last_pretone_index, isometric_time[last_pretone_index], fo[last_pretone_index]
        pretones.append(last_pretone)
        return pretones
        #IF FIRST GROUP check if duplicate with first
        #IF MAX = MIN, diEDerentiate

################################################################################
##
#   tones
#
    def getLHL(self, P):
        #print(pretones)
        #print("updated pretones : ", len(pretones))
        #tones = []
        # get H (highest tone)
        H = max(P, key=lambda item:item[3])
        #print("H : ", H)
        # get L- (lowest pretone leading to H)
        lead_fo = H[3]
        Hi = P.index(H)
        i = Hi
        #print("Hi, i : ", Hi, i)
        while i >= -1:
            #print("@ i : ", i)
            if i < 0:
                lead_tone = P[0]
            elif i == Hi:
                lead_tone = H
                #print("yes")
            elif P[i][3] < lead_fo:
                lead_fo = P[i][3]
                lead_tone = P[i]
            else:
                break
            i -= 1
        #print("L- : ", lead_tone)
        # get -L (lowest pretone after H)
        trail_fo = H[3]
        Hi = P.index(H)
        i = Hi
        #print("Hi, i : ", Hi, i)
        while i <= len(P):
            #print("@ i : ", i)
            if i > len(P) -1:
                trail_tone = P[-1]
            elif i == Hi:
                trail_tone = H
                #print("yes")
            elif P[i][3] < trail_fo:
                trail_fo = P[i][3]
                trail_tone = P[i]
            else:
                break
            i += 1
        #print("L- : ", lead_tone)
        #print("H : ", H)
        #print("-L : ", trail_tone)
        LHL = [(lead_tone, H, trail_tone)]
        return(LHL)

    def recursiveTones(self, P):
        #if len(P) <= 3 and len(P) > 0:
        #    LHL = self.getLHL(P)
        if len(P) == 0:
            print("the end")
        else:
            LHL = self.getLHL(P)
            lead_tone = LHL[0][0]
            trail_tone = LHL[0][2]
            # recompose pretone list without main trail_tone
            if P.index(lead_tone) - 1 < 0:
                i = 0
            else:
                i = P.index(lead_tone) - 1
            before = P[:i]
            after = P[P.index(trail_tone) + 1:]
            #print("before : ", i, before)
            #print("after : ", P.index(trail_tone) + 1, after)
            if not after:
                parts = [before]
            elif not before:
                parts = [after]
            elif not before and not after:
                parts = []
            else:
                parts = [before, after]
            return self.getLHL(P) + [self.recursiveTones(part) for part in parts if part]

    def flattener(self,S):
        if S == []:
            return S
        if isinstance(S[0], list):
            return self.flattener(S[0]) + self.flattener(S[1:])
        return S[:1] + self.flattener(S[1:])

    def cleanUpTones(self, tone_list):
        cleanedup_tones = tone_list.copy()
        for tones in cleanedup_tones:
            if tones[0] == tones[1] == tones[2]:
                cleanedup_tones.remove(tones)
        return cleanedup_tones

    def limitToneNumber(self, tone_list, number_of_tones):
        i = 1
        ordered_tones = []
        current_tone_list = tone_list.copy()
        if number_of_tones == 'max':
            tone_limit = len(tone_list)
        else:
            tone_limit = int(number_of_tones)
        while i <= tone_limit:
            #print("len tone_list and current:", len(tone_list), len(current_tone_list))
            list_of_max = []
            if len(current_tone_list) > 0:
                for tone in current_tone_list:
                    #print(tone)
                    max_fo = max(tone, key=lambda item:item[3])
                    loc = (current_tone_list.index(tone), tone.index(max_fo), max_fo)
                    list_of_max.append(loc)
                #print(list_of_max)
                global_max_fo = max(list_of_max, key=lambda item:item[2][3])
                #print("H", i, " is : ", current_tone_list[global_max_fo[0]])
                t = current_tone_list[global_max_fo[0]]
                #add unique identifier (to avoid rightful duplicate pretones to be removed)
                lb = t[0] + ("Lb" + str(i),)
                h = t[1] + ("H" + str(i),)
                la = t[2] + ("La" + str(i),)
                tone = (lb,h,la)
                ordered_tones.append(tone)
                current_tone_list.pop(global_max_fo[0])
                i += 1
            else:
                break
        return ordered_tones

    def getTones(self):
        pretones = self.getPretones()
        #print("initial pretones : ", len(pretones))
        TL = pretones[0]
        TL = TL + ("TL",)
        TR = pretones[-1]
        TR = TR + ("TR",)
        #print("TL : ", TL)
        #print("TR : ", TR)
        pretones = pretones[1:-1]
        tone_extraction = self.recursiveTones(pretones)
        #tone_sequence = sorted(self.flattener(tone_extraction),key=lambda x: x[0][1])#, reverse=True)
        tone_sequence = self.flattener(tone_extraction)
        tone_sequence = self.cleanUpTones(tone_sequence)
        tone_sequence = self.limitToneNumber(tone_sequence, printConfig.gp_number_of_tones)
        #print(tone_sequence)
        tone_points =   [point for tone in tone_sequence for point in tone]
        tone_points = sorted(list(set(tone_points)),key=lambda x: x[1])#, reverse=True)
        #print(tone_points)
        tone_points[0:0] = [TL]
        tone_points.append(TR)
        #print(tone_points)
        return tone_points

################################################################################
##
#   movement detection tools
#
    def mvtDetectionScan(self):
        print('>>>>>>>>>>>>>>>>>>>>', printConfig.scalingMethod)
        if printConfig.scalingMethod == 'PCT':
            fo_list = self.scaleFoPCT()
        elif printConfig.scalingMethod == 'ERB':
            fo_list = self.scaleFoERB()
        elif printConfig.scalingMethod == 'BRK':
            fo_list = self.scaleFoBARK()
        elif printConfig.scalingMethod == 'MEL':
            fo_list = self.scaleFoMEL()
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

    def linearfunction(self, xa, ya, xb, yb , x):
        m = (ya - yb)/(xa - xb)
        y = (m * x) - (m * xa) + ya
        return y


    def printToWeb(self):    # writes data into php file to be used
                                        # for front-end visualization
        printConfig.gp_name = self.get_token_tag()
        # RAW SCAN
        mvt_list = self.mvtDetectionScan()[0]
        #print(self.get_token_tag() + " has " + str(len(mvt_list)) + " turning points.")
        mydata = "/var/www/html/linguistics/raw_scan.php"
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
            myphpfile.write("\n var title = '" + printConfig.gp_name + "';")
            #add fo stats variables
            stats = self.getFoStats()
            myphpfile.write("\n var fo_mean = '" + str(int(stats[0])) + "';")
            myphpfile.write("\n var fo_max = '" + str(int(stats[1])) + "';")
            myphpfile.write("\n var fo_min = '" + str(int(stats[2])) + "';")
        myphpfile.close()
        #for attribute, value in sorted_mvt_dict.items():
        #    print('[{}, {}],'.format(attribute, round(320 - value,0)))

        # PRETONES
        mydata_b = "/var/www/html/linguistics/pretones.php"
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
            myphpfile_b.write("\n var title = '" + printConfig.gp_name + "';")
        myphpfile_b.close()

    # TONES
        mydata_c = "/var/www/html/linguistics/tones.php"
        tones_data = self.getTones()
        with open(mydata_c, 'w') as myphpfile_c:
            #add line data
            myphpfile_c.write("var lineData = [  \n")
            for tone in tones_data:
                row = "{ 'x': " + str(tone[2]*3.99 + 32) + ", 'y': " + str(217 - tone[3]  * 1.8) +  " },\n"
                myphpfile_c.write(row)
            myphpfile_c.write(" ];")
            #add boundary data
            boundary_numbers = int(self.getTotalFrameNumber() + 1)
            target_frame_size = 100.0 / self.getTotalFrameNumber()
            i = 1
            boundaries = [0.0]
            while i in range(boundary_numbers):
                boundaries.append(i * float(target_frame_size))
                i += 1
            myphpfile_c.write("var boundaryData = [  \n")
            for position in boundaries:
                row = "{ 'xa': " + str(position*3.99 + 32) + ", 'ya': " + "35" + ", 'xb': " + str(position*3.99 + 32) + ", 'yb' : " + "217" + " },\n"
                myphpfile_c.write(row)
            myphpfile_c.write(" ];")
            #add title variable
            myphpfile_c.write("\n var title = '" + printConfig.gp_name + "';")
            myphpfile_c.write("\n var toneNumber = '" + printConfig.gp_number_of_tones + "';")

        myphpfile_c.close()

 ################################
        transitionData = "/var/www/html/linguistics/printVizData.php"
        raw_data = list(zip(self.csvToLists()[0],self.csvToLists()[1]))
        print("len raw = ", len(raw_data) )
        #print('raw data', raw_data)
        pretones_data = self.getPretones()
        print('pretone data', pretones_data)
        print("len pretones = ", len(pretones_data))
        tones_data = self.getTones()
        #print(len(tones_data))
        print('tone data', tones_data)
        fomax = self.getFoStats()[1]
        fomin = self.getFoStats()[2]
        forange = fomax - fomin

        boundaries = self.getFrameBoundaries(self.frames_per_syllable)
        timemin = boundaries[0]
        timemax = boundaries[-1]
        timerange = timemax - timemin

        with open(transitionData, 'w') as myphpfile:
            #add line data
            myphpfile.write("var lineRaw = [  \n")
            raw_pct = []
            for pair in raw_data:
                #print((pair[0]-timemin)*(100/timerange))
                if ((pair[0]-timemin)*(100/timerange)) <= 100:
                    x = (pair[0]-timemin)*(100/timerange)
                    y = (pair[1]-fomin)*(100/forange)
                    coor_pct = (x, y)
                    raw_pct.append(coor_pct)
                    row = "[ " + str( (x * 3.9) + 32) + ", " + str(217 - (y *1.8)) +  " ],\n"
                    myphpfile.write(row)
            myphpfile.write(" ];")
            #add boundary data
            boundaries = self.getBoundariesPCT()
            print('boundaries PCT', boundaries)
            myphpfile.write("var boundaryRaw = [  \n")
            for position in boundaries:
                row = "[[" + str(position*3.99 + 32) + ", 35]" + ", [" + str(position*3.99 + 32) + ", 217]],\n"
                myphpfile.write(row)
            myphpfile.write(" ];")
            #add title variable
            myphpfile.write("\n var title = '" + printConfig.gp_name + "';")
            #add fo stats variables
            stats = self.getFoStats()
            myphpfile.write("\n var fo_mean = '" + str(int(stats[0])) + "';")
            myphpfile.write("\n var fo_max = '" + str(int(stats[1])) + "';")
            myphpfile.write("\n var fo_min = '" + str(int(stats[2])) + "';")

        # PRETONES
            #add line data
            myphpfile.write("var data1 = [  \n")
            for pretone in pretones_data:
                row = "[" + str(pretone[2]*3.99 + 32) + ", " + str(217 - pretone[3]  * 1.8) +  " ],\n"
                myphpfile.write(row)
            myphpfile.write(" ];")
            #add boundary data
            boundary_numbers = int(self.getTotalFrameNumber() + 1)
            target_frame_size = 100.0 / self.getTotalFrameNumber()
            i = 1
            boundaries = [0.0]
            while i in range(boundary_numbers):
                boundaries.append(i * float(target_frame_size))
                i += 1
            myphpfile.write("var boundaryPretones = [  \n")

            for position in boundaries:
                row = "[[" + str(position*3.99 + 32) + ", 35], [" + str(position*3.99 + 32) + ", 217]],\n"
                myphpfile.write(row)
            myphpfile.write(" ];")

            #pretones, coming from raw (requires extra points)
            pretones_intervals = [(0,0,pretones_data[0][2],pretones_data[0][3])]
            i = 0
            l = len(pretones_data)
            while i < l - 1:
                interval = (pretones_data[i][2],pretones_data[i][3], pretones_data[i+1][2], pretones_data[i+1][3])
                #print(i, pretones_data[i][2],pretones_data[i][3], pretones_data[i+1][2], pretones_data[i+1][3])
                pretones_intervals.append(interval)
                i += 1
            #print('pretones interval', pretones_intervals)
            myphpfile.write("var data1a = [  \n")
            new_point = 0
            for point in raw_pct:
                for interval in pretones_intervals:
                    if point[0] >= interval[0] and point[0] <= interval[2]:
                        #xa, ya, xb, yb , x
                        new_point += 1
                        new_y = self.linearfunction(interval[0], interval[1], interval[2], interval[3], point[0])
                        #print(new_point, pretones_intervals.index(interval), point[0], new_y, point[1])
                        row = "[" + str(point[0] * 3.99 + 32) + ", " + str(217 - new_y  * 1.8) +  "], \n"
                        myphpfile.write(row)

            myphpfile.write(" ];")
            #print(raw_pct)
            #print('len raw pct',len(raw_pct))
            #print(new_point)


    # TONES
            #add line data
            tones_intervals = [(0,0,tones_data[0][2],tones_data[0][3])]
            it = 0
            lt = len(tones_data)
            while it < lt - 1:
                intervalt = (tones_data[it][2],tones_data[it][3], tones_data[it+1][2], tones_data[it+1][3])
                #print(it, tones_data[it][2],tones_data[it][3], tones_data[it+1][2], tones_data[it+1][3])
                tones_intervals.append(intervalt)
                it += 1
            print('tones interval', tones_intervals)


            myphpfile.write("var data2 = [  \n")
            new_pointt = 0
            for pointt in raw_pct:
                for intervalt in tones_intervals:
                    if pointt[0] > intervalt[0] and pointt[0] <= intervalt[2]:
                        #xa, ya, xb, yb , x
                        new_pointt += 1
                        #print(intervalt[0], intervalt[1], intervalt[2], intervalt[3], pointt[0])
                        new_yt = self.linearfunction(intervalt[0], intervalt[1], intervalt[2], intervalt[3], pointt[0])

                        #print(new_pointt, tones_intervals.index(intervalt), pointt[0], new_yt, pointt[3])
                        rowt = "[" + str(pointt[0] * 3.99 + 32) + ", " + str(217 - new_yt  * 1.8) +  "], \n"
                        myphpfile.write(rowt)

            myphpfile.write(" ];")
            print('len pretones data',len(pretones_data))
            print(new_pointt)

            #add boundary data
            boundary_numbers = int(self.getTotalFrameNumber() + 1)
            target_frame_size = 100.0 / self.getTotalFrameNumber()
            i = 1
            boundaries = [0.0]
            while i in range(boundary_numbers):
                boundaries.append(i * float(target_frame_size))
                i += 1
            myphpfile.write("var boundaryTone = [  \n")
            for position in boundaries:
                row = "{ 'xa': " + str(position*3.99 + 32) + ", 'ya': " + "35" + ", 'xb': " + str(position*3.99 + 32) + ", 'yb' : " + "217" + " },\n"
                myphpfile.write(row)
            myphpfile.write(" ];")
            #add title variable
            myphpfile.write("\n var toneNumber = '" + printConfig.gp_number_of_tones + "';")
        myphpfile.close()







################################################################################
##                                                                            ##
#   CLASSIFIER                                                                 #
##                                                                            ##
################################################################################

    def getlistofcontourelement(self,td,p):# tone_data as parameter, p: position in tuple (frame, fo, time)
        li = []
        for i in td:
            for s in i:
                if s[4] not in li:
                    li.append(s[4])
        li = list(set(li))
        lofl = []
        for e in li:
            elist = [round(element[p],0) for contour in tone_data for element in contour if element[4] == e]
            pair = (e, elist)
            lofl.append(pair)
        return lofl

    def getFrequencyCount(self,tes): #tone element set
        #create a dictionnary to count frequencies of values in the set
        fc = {} #frequency count
        for i in tes:
            if i in fc:
                #at key = i, get the value and add 1
                fc[i] = fc.get(i)+1
            else:
                #at key = 1, value must be created, as 1
                fc[i] = 1
        return fc

    def keywithmaxval(self,d): # d is a dictionnary
        v = list(d.values())
        k = list(d.keys())
        return (max(v), k[v.index(max(v))])

    def median(self,values):
        n = len(values)
        sorted_values = sorted(values)
        midpoint = n // 2
        if n % 2 == 1:
            return sorted_values[midpoint]
        else:
            lo = midpoint - 1
            hi = midpoint
            return (sorted_values[lo] + sorted_values[hi]) / 2

    def makeSubset(self,s):
        ss = {} #subset
        for key,value in s.items():
            if value == 0.0:
                value = 0.1
            if value not in ss:
                s = value
                value = {key}
                ss[s] = value
            else:
                ss[value].add(key)
        return ss

    def frequencyClassifier(self,tevl):
        #lofl = self.getlistofcontourelement(toneElementSet,4)
        #for tevl in listoflist:
            count = self.getFrequencyCount(tevl[1])
            maXFrequency = self.keywithmaxval(count)
            gradedDict = {}
            for k,v in count.items():
                #print(str(k) + ':' + str(round(v/maXFrequency[0],2)))
                gradedDict[k] = round(v/maXFrequency[0],1)
            return gradedDict

    def similarityClassifier(self,tevl):
        #lofl = self.getlistofcontourelement(toneElementSet,4)
        #for tevl in listoflist: #tone element value list
        if isinstance(tevl, set):
            tevl = list(tevl)
            tevs = tevl
        else:
            tevl = tevl[1]
        center = self.median(tevl)
        tevs = list(set(tevl)) ##tone element value set / no duplicate
        maxd = max([abs(center - x) for x in tevs])
        gradedDict = {}
        for v in tevs:
            if maxd == 0:
                gradedDict[v] = 1
            else:
                absd = abs(center - v)
                grade = 1 - (absd * (1/maxd))
                gradedDict[v] = round(grade,1)
        return gradedDict

    def unifiedGrader(self,toneElementSet,el):
        lofl = self.getlistofcontourelement(toneElementSet,el)
        crispSet = {}
        scaledFuzzySet = {}
        for tevl in lofl:
            #frequency
            gradedDictFreq = self.frequencyClassifier(tevl)
            #similarity
            gradedDictSimil = self.similarityClassifier(tevl)
            #unification
            unified = {k : round((v + gradedDictSimil[k])/2,1) for k, v in gradedDictFreq.items() if k in gradedDictSimil}
            #print(tevl[0], unified)

            subsets = self.makeSubset(unified)

            subsetValue = 0
            subsetGrade = 0
            gradeScale = {}
            for key,v in subsets.items():
                gradedDictSubset = self.similarityClassifier(v)
                #print('gradedsubset ',key,gradedDictSubset)
                subsubsets = self.makeSubset(gradedDictSubset)
                #print('subsubset',key,subsubsets)
                subsubsetValue = 0
                subsubsetGrade = 0

                for g,s in subsubsets.items():
                    weightedValue = sum(s) * g
                    subsubsetValue += weightedValue
                    subsubsetGrade += g * len(s)

                if subsubsetValue == 0:
                    defuzzifiedValue = subsubsetValue
                else:
                    defuzzifiedValue = round(subsubsetValue / subsubsetGrade,1)

                subsetValue += key * defuzzifiedValue
                subsetGrade += key
                gradeScale[key] = defuzzifiedValue
            crisp = round(subsetValue / subsetGrade,1)
            crispSet[tevl[0]] = crisp
            scaledFuzzySet[tevl[0]] = gradeScale
        return (crispSet, scaledFuzzySet)



######################################################################
##
#   FiLE PROCESSING
#
def fileModeProcessing(targetFolder, chosenScaling):
    token = ContourFromCsv("./questionData/PO/foCsv/PO" + printConfig.gp_name + ".csv", "./questionData/PO/syllabletime.txt", "./questionData/PO/starttimes.txt", printConfig.gp_number_of_frames)
    table_data = [
        [token.get_token_tag(), ''],
        ['fo stats', (round(token.getFoStats()[0],2),round(token.getFoStats()[1],2),round(token.getFoStats()[2],2))],
        ['longest syllable', (round(token.getLongestSyllable()[0],2), token.getLongestSyllable()[1])],
        ['start time', round(token.getLeftmostBoundary(),2)],
        ['sample duration', round(token.overallDurations()[0],2)],
        ['token duration', round(token.overallDurations()[1],2)],
        ['token != sample', token.overallDurations()[2]]
    ]
    table = AsciiTable(table_data)
    print(table.table)
    token.printToWeb()

    pause()










######################################################################
##
#   RUN PRINT PROGRAM
#
if __name__ == "__main__":


    #printConfig.gb_debug = 'debug'
    #printConfig.gp_batch = '2'
    #printConfig.gp_number_of_frames = '2'
    #printConfig.gp_number_of_tones = '3'
    #printConfig.gp_name = '14'

    # TESTING #
    token = ContourFromCsv("./questionData/EM/json/EM" + printConfig.gp_name + ".json", "./questionData/EM/syllabletime.csv", "./questionData/EM/starttimes.csv", printConfig.gp_number_of_frames)
    table_data = [
        [token.get_token_tag(), ''],
        ['fo stats', (round(token.getFoStats()[0],2),round(token.getFoStats()[1],2),round(token.getFoStats()[2],2))],
        ['longest syllable', (round(token.getLongestSyllable()[0],2), token.getLongestSyllable()[1])],
        ['start time', round(token.getLeftmostBoundary(),2)],
        ['sample duration', round(token.overallDurations()[0],2)],
        ['token duration', round(token.overallDurations()[1],2)],
        ['token != sample', token.overallDurations()[2]]
    ]
    table = AsciiTable(table_data)
    print(table.table)
    token.printToWeb()

    printConfig.gp_batch_test = int(printConfig.gp_batch)
    #folders = ['FL','AC','CA','CB','CJ','ED','EM','FF','GR','JC','JP','NB','PC','PM','PN','PO','RR','SV']



    #folders = ['AC', 'EM', 'ED', 'NB']
    folders = ['EM']


    totalLines = 0
    totalFiles = 0
    for folder in folders:
        listing = os.listdir('./questionData/' + folder +'/json')
        numFiles = len(listing)
        totalFiles += numFiles
        """
        for fichier in listing:
            if fichier == '.DS_Store':
                pass
            else:
                target_file = './questionData/' + folder +'/foCsv/' + fichier
                numLines = sum(1 for line in open(target_file))
                print(target_file, numLines)
                totalLines += numLines
        """
    increment = totalFiles//50
    print(totalFiles, increment)


    if printConfig.gp_batch_test == 1:
        toolbar_width = 50
        # setup toolbar
        sys.stdout.write("\u25A0%s\u25A0" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['
        tone_data = []
        syllable_data_collection = []
        all_boundaries = []
        counter = 0
        for folder in folders:
            listing = os.listdir('./questionData/' + folder +'/json')
            for fichier in listing:
                if '.DS_Store' in fichier or '._' in fichier:
                    pass
                else:
                    target_file = './questionData/' + folder +'/json/' + fichier
                    if printConfig.gb_debug == 'debug':
                        print(target_file, "_____________________________________________________________")
                    token = ContourFromCsv(target_file, "./questionData/" + folder +"/syllabletime.csv", "./questionData/" + folder +"/starttimes.csv", printConfig.gp_number_of_frames)
                    token_data = token.getTones()
                    tone_data.append(token_data)

                    longest_syllable_data = token.getLongestSyllable()
                    syllable_data_collection.append(longest_syllable_data)

                    syllables = token.retrieveSpans()
                    x = len(syllables)
                    all_boundaries.append(x)


                    counter += 1
                    if counter % increment == 0:
                            sys.stdout.write(u"\u25A1")
                            sys.stdout.flush()
        sys.stdout.write("\n")
        #token.frequencyClassifier(tone_data)
        time = token.unifiedGrader(tone_data,2)
        fo = token.unifiedGrader(tone_data,3)

        crispFo = fo[0]
        crispTime = time[0]
        """ element : (time,fo) """
        crispAll = [(k, v, crispFo[k]) for k,v in crispTime.items() if k in crispFo]
        crispAll = sorted(crispAll, key=lambda x:x[1])
        print('crispall',crispAll)
        timeList = [x[1] for x in crispAll]
        foList = [x[2] for x in crispAll]
        print('timelist',timeList)
        print('folist',foList)

        allTones = []

        n = 1
        while n <= int(printConfig.gp_number_of_tones):
            toneEls = []
            for el in crispAll:
                if el[0][-1] == str(n):
                    toneEls.append(el)
            allTones.append(toneEls)
            n += 1
        #print(crispFo,crispTime)

        print('alltones 1', allTones)
        #allTonesFlattned = []
        #for x in allTones:
        #    for y in x:
        #        allTonesFlattned.append(y)

        allTonesFlattened = [y for x in allTones for y in x ]
        print('alltones 2', allTonesFlattened)
        allTonesFlattened = sorted(allTonesFlattened, key=itemgetter(1))
        print('alltones 3', allTonesFlattened)

        print(syllable_data_collection)
        print(all_boundaries)

        crispData = "/var/www/html/linguistics/printVizDataContour.php"

        with open(crispData, 'w') as myphpfile:
            #add line data
            myphpfile.write("var lineCrisp = [  \n")
            for point in allTonesFlattened:
                row = "[" + str(point[1] * 3.99 + 32) + ", " + str(217 - point[2]  * 1.8) +  "], \n"
                myphpfile.write(row)
            myphpfile.write(" ];")
            #add boundary data
            """
            boundary_numbers = int(self.getTotalFrameNumber() + 1)
            #target_frame_size = 100.0 / self.getTotalFrameNumber()
            i = 1
            boundaries = [0.0]
            while i in range(boundary_numbers):
                boundaries.append(i * float(target_frame_size))
                i += 1
            myphpfile.write("var boundaryTone = [  \n")
            for position in boundaries:
                row = "{ 'xa': " + str(position*3.99 + 32) + ", 'ya': " + "35" + ", 'xb': " + str(position*3.99 + 32) + ", 'yb' : " + "217" + " },\n"
                myphpfile.write(row)
            myphpfile.write(" ];")"""


            #myphpfile.write("var lineCrisp = [[ 39.495233422681714, 204.95213601196318 ],[ 42.94121181790261, 207.01321044971792 ],[ 46.38719021312351, 207.0150463757695 ],[ 49.833168608344394, 208.3591727612627 ]];")
        myphpfile.close()



    """
        #maxes = [max(toneElement, key=lambda x: x[1][0]) for toneElement in allTones]
        #print(maxes)
    """
