from __future__ import division
import  sys, os, csv, pylab, math
from dataInjection import DataFromCsv
from terminaltables import AsciiTable
from collections import OrderedDict
from itertools import chain

from sys import argv

#global parameters
script, gp_batch, gp_number_of_frames, gp_number_of_tones, gp_name = argv

class ContourFromCsv(DataFromCsv):

    def __init__(self,contour_data, syllable_data, origin_data): #,syllablecsv):
        super().__init__(contour_data,syllable_data,origin_data)

        self.fo_time = contour_data
        self.spans = syllable_data
        self.origins = origin_data

    frames_per_syllable = float(gp_number_of_frames)

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

    def flattener(self,S): # http://stackoverflow.com/users/307705/mu-mind, http://tinyurl.com/z25rxro
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
        tone_sequence = self.limitToneNumber(tone_sequence, gp_number_of_tones)
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

    def printToWeb(self):    # writes data into php file to be used
                                        # for front-end visualization
        gp_name = self.getTokenTag()
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
            myphpfile.write("\n var title = '" + gp_name + "';")
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
            myphpfile_b.write("\n var title = '" + gp_name + "';")
        myphpfile_b.close()

    # TONES
        mydata_c = "/Applications/XAMPP/xamppfiles/htdocs/oftenback/linguistics/tones.php"
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
            myphpfile_c.write("\n var title = '" + gp_name + "';")
            myphpfile_c.write("\n var toneNumber = '" + gp_number_of_tones + "';")

        myphpfile_c.close()

 ################################
        transitionData = "/Applications/XAMPP/xamppfiles/htdocs/oftenback/linguistics/printVizData.php"
        raw_data = list(zip(self.csvToLists()[0],self.csvToLists()[1]))
        print("len raw = ", len(raw_data) )
        pretones_data = self.getPretones()
        print(len(pretones_data))
        tones_data = self.getTones()
        #print(len(tones_data))
        #print(tones_data)
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
            for pair in raw_data:
                #print((pair[0]-timemin)*(100/timerange))
                if ((pair[0]-timemin)*(100/timerange)) <= 100:
                    row = "[ " + str( ( ((pair[0]-timemin)*(100/timerange))* 3.9) + 32) + ", " + str(217 - (((pair[1]-fomin)*(100/forange)*1.8))) +  " ],\n"
                    myphpfile.write(row)
            myphpfile.write(" ];")
            #add boundary data
            boundaries = self.getBoundariesPCT()
            myphpfile.write("var boundaryRaw = [  \n")
            for position in boundaries:
                row = "[[" + str(position*3.99 + 32) + ", 35]" + ", [" + str(position*3.99 + 32) + ", 217]],\n"
                myphpfile.write(row)
            myphpfile.write(" ];")
            #add title variable
            myphpfile.write("\n var title = '" + gp_name + "';")
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
            lenpretone = len(pretones_data)
            lenraw = len(raw_data)
            spans = len(self.retrieveSpans())
            m = lenraw // lenpretone
            n = lenraw % lenpretone
            o = spans*self.frames_per_syllable
            #print(m, n, o)
            new_pretones = 0
            myphpfile.write("var data1a = [  \n")
            d = 0
            for pretone in pretones_data:
                d += 1
                if n > 0 and d <= n:
                    r = m + 1
                else:
                    r = m
                for x in range(r):
                    row = "[" + str(pretone[2]*3.99 + 32) + ", " + str(217 - pretone[3]  * 1.8) +  "], \n"
                    #print(m, row)
                    new_pretones += 1
                    myphpfile.write(row)


            myphpfile.write(" ];")
            print("lenraw, new_pretones = ", lenraw, new_pretones)


    # TONES
            #add line data
            lenpretone = len(pretones_data)
            lentone = len(tones_data)
            spans = len(self.retrieveSpans())
            m = lenpretone // lentone
            n = lenpretone % lentone
            o = spans*self.frames_per_syllable
            #print(m, n, o)
            new_tones = 0
            myphpfile.write("var data2 = [  \n")
            d = 0
            for tone in tones_data:
                d += 1
                if n > 0 and d <= n:
                    r = m + 1
                else:
                    r = m
                for x in range(r):
                    row = "[" + str(tone[2]*3.99 + 32) + ", " + str(217 - tone[3]  * 1.8) +  "], \n"
                    #print(m, row)
                    new_tones += 1
                    myphpfile.write(row)
            myphpfile.write(" ];")
            print("new_tones = ", new_tones)
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
            myphpfile.write("\n var toneNumber = '" + gp_number_of_tones + "';")
        myphpfile.close()








# TESTING #
token = ContourFromCsv("./EM/foCsv/EM" + gp_name + ".csv", "./EM/syllabletime.txt", "./EM/starttimes.txt")
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
#print(token.getPretones(), len(token.getPretones()))
#print(token.getTones(), len(token.getTones()))
token.printToWeb()

gp_batch_test = int(gp_batch)
folders = ['EM', 'JP']
if gp_batch_test == 1:
    tone_data = []
    for folder in folders:
        listing = os.listdir('./' + folder +'/foCsv')
        for fichier in listing:
            target_file = './' + folder +'/foCsv/' + fichier
            print(target_file, "_____________________________________________________________")
            token = ContourFromCsv(target_file, "./" + folder +"/syllabletime.txt", "./" + folder +"/starttimes.txt")
            token_data = token.getTones()
            tone_data.append(token_data)
        for x in tone_data:
            print(len(x),x)
