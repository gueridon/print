#	PRInt for Python version 0.1, 2016
#
#	PRInt created by Nicholas Bacuez for his PhD dissertation
#	Thesis available at www.nicholasbacuez.com
#
#	Script created by Nicholas Bacuez
#
#		nicholasbacuez@gmail.com
#
#	DESCRIPTION:
#
#
#
#


import pylab, os, csv


#Create a file to receive all data relative to the sample
#f = open('output_data.txt', 'w')

############################################
# IMPORT DATA FROM PRAAT FILES  		   #
############################################

#Get lists of time and fo values from the original two-column file
def getOriginalValues(file, column):
    listOfValues = []
    rawdata = os.path.join("./data/" + file)
    with open(rawdata, mode='rU') as f:
        reader = csv.reader(f)
        for num, row in enumerate(reader):
            value = row[column]
            listOfValues.append(float(value))
    return listOfValues

#############################################
# SYLLABLE DURATION -> BOUNDARIES -> FRAMES #
#############################################

#Dictionary {sample name : origin time}
def getinit(file):
    sample_tags = []
    sample_inits = []
    rawdata = file.split()
    for number in rawdata:
        i = rawdata.index(number)
        if i % 2 == 0:
            sample_tags.append(number)
        else:
            sample_inits.append(float(number))
    origin_dict = dict(zip(sample_tags,sample_inits))
    return origin_dict

#Generate the right boundary of each frame
def syllable_right_end(frameboundary, framedurations):
    list_frames = []
    for x in frames:
        frameboundary = frameboundary + x
        list_frames.append(float(frameboundary))
        frameboundary = frameboundary + x
        list_frames.append(float(frameboundary))
    return list_frames

#remove values before origin and after end
def clean_lists(time):
    cleanedList = []
    for item in time:
        if item < origin_sample or item > end_sample:
            indexitem = time.index(item)
            cleanedList.append(indexitem)
    return cleanedList


#Evaluate frame membership for each time point in a time list
#and adjust time in % to the frame range. Frame duration target is 7.142857143 here
"""
def leftb(boundaries, num):
    for i, elem in enumerate(boundaries):
        if num <= elem:
            return (boundaries[i-1], i-1)
        #print (boundaries[i-1], i-1)

#list_to_be_ajusted = timelist_pc
# target_frame_size = frame_ref

def adjust_to_scaled_boudaries(list_to_be_ajusted, target_frame_size):
	output_adjusted = []
	for value in list_to_be_ajusted:
		(lB, index) = leftb(frameslist_nmlz, value)
		#print index
		cursylspan = frames_nmlz[index]
		adjusted_value = (((value - lB) / cursylspan)*target_frame_size)+ ((index) * (target_frame_size))
		if adjusted_value < 0:
			adjusted_value = 0
		else:
			output_adjusted.append(round(adjusted_value,2))
	return output_adjusted
		#print adjusted_value
"""

def adjust_to_scaled_boudaries(list_to_be_ajusted, target_frame_size):
    output_adjusted = []
    for value in list_to_be_ajusted:
        for leftboundary in frameslist_nmlz:
            if value > leftboundary and value < frameslist_nmlz[frameslist_nmlz.index(leftboundary) + 1]:
                bin = leftboundary
                cursylspan = frames_nmlz[frameslist_nmlz.index(leftboundary)]
                adjusted_value = (((value - leftboundary) / cursylspan) * target_frame_size)+ (frameslist_nmlz.index(leftboundary) * target_frame_size)
        output_adjusted.append(round(adjusted_value,0))
    return output_adjusted

#TONES : scan fo list for movements at each value: 0 = down, 1 = up or flat
def pretonal_mvt(pt_fo):
    pt_mvt = []
    for i,  x in enumerate(pt_fo):
        if i == 0:
            mvt = 0
        else:
            prev = pt_fo[i-1]
            if prev  < x:
                mvt = 1
            elif prev > x:
                mvt = 0
            elif prev == x:
                mvt = pt_mvt[i-1]
        pt_mvt.append(mvt)
        #print i, "\t", x,"\t", mvt
    return pt_mvt

#TONES : scan list of individual movements for consecutive ascending movements
#direction: 1 going up, 0 going down
def scan_mvt_span(mvt_list):
    output = []
    for i,  x in enumerate(mvt_list):
        if i == 0:
            newx = 0
        else:
            prev_up = output[i-1]
            if x == 1:
                newx = 1 + prev_up
            else:
                newx = 0
        output.append(newx)
    return output

#Method to find a tonal group L-H-L from the highest point in a fo list
def tonal_gp(fo, time, up, down):
    #H
    H_fo = max(fo)
    H_pt = fo.index(int(H_fo))
    H_time = time[H_pt]
    H_gup_value = up[H_pt]
    H_gdown_value = down[H_pt]
    #H_fo = pretones_y.index[H_pt_index]

    #[L]-
    Lead_L_pt = H_pt - H_gup_value
    Lead_L_fo = fo[int(Lead_L_pt)]
    Lead_L_time = time[int(Lead_L_pt)]

    #-[L]
    Trail_L_pt = H_pt + H_gdown_value
    Trail_L_fo = fo[int(Trail_L_pt)]
    Trail_L_time = time[int(Trail_L_pt)]

    Tone =  (Lead_L_pt + 1, Lead_L_fo, Lead_L_time, H_pt + 1, H_fo, H_time, Trail_L_pt + 1, Trail_L_fo, Trail_L_time)
    return Tone


############################################
# MAIN ALGORITHM                           #
############################################

listing = os.listdir('./data')
print listing
figure_counter = 1
for fichier in listing:
    print '####################################################################'
    print '###   ',fichier.upper()
    print '####################################################################'

    timelist = getOriginalValues(fichier, 0)
    #print 'timelist', timelist
    folist = getOriginalValues(fichier, 1)
    #print 'folist', folist
    #open the syllable duration file and make a list of it
    spans = open(os.path.join("./data_syllable/" + os.path.splitext(fichier)[0] + '_syl.txt')).read().splitlines()
    f = open(os.path.splitext(fichier)[0]+'_output_data.txt', 'w')
    print 'spans', spans
    ns = len(spans)
    frame_ref = float(100.0/(ns*2.0))
    print 'number of syllables:', ns
    print 'frame_ref:', frame_ref
    #open the sample origin time file and make a dictionary of it
    origin_list = getinit(open(os.path.join("./data_syllable/" + 'init.txt')).read())
    origin_sample = float(origin_list.get(os.path.splitext(fichier)[0]))
    print 'origin_sample', origin_sample
    #Generate the right boundary of each frame
    #1.get frames duration
    frames = [(float(x))/2.0  for x in spans]
    #2.cumulative sum of frames duration to get their right boundary
    frameslist = syllable_right_end(origin_sample,frames)
    #Get sample's rightmost boundary and overall duration
    end_sample = max(frameslist)
    range_sample = end_sample - origin_sample
    #remove values before origin and after end
    #1. Find index of values before origin and after end
    outOfRangeList = clean_lists(timelist)
    print 'indexlist', outOfRangeList
    #2. Remove the values by index
    folist = [x for x in folist if folist.index(x) not in outOfRangeList ]
    timelist = [x for x in timelist if timelist.index(x) not in outOfRangeList ]
    print 'lentimelist', len(timelist)
    print 'lenfolist', len(folist)



    #Normalization of fo, time, (scalar quantization. Could be ERB...)
    minfo = min(folist) - 10 # Baseline is set to n points under actual value
    maxfo = max(folist)
    rangefo = maxfo - minfo
    folist_nmlz = [round((item - minfo) * (100.0/rangefo),0) for item in folist]
    timelist_nmlz = [round((item - origin_sample) * (100/range_sample), 4) for item in timelist]
    frames_nmlz = [(float(item)/float(range_sample))*100 for item in frames for _ in (0, 1)]
    #Generate the right boundary of each frame expressed in %
    frameboundary_nmlz = 0
    frameslist_nmlz = []
    frameslist_nmlz.append(0)
    for x in frames_nmlz:
        frameboundary_nmlz = frameboundary_nmlz + x
        frameslist_nmlz.append(float(frameboundary_nmlz))
    print "frames :", frames, "\n"
    print "frameslist", frameslist, "\n"
    print "frames_nmlz", frames_nmlz, "\n"
    print "folist_nmlz", folist_nmlz, "\n"
    print "frameslist_nmlz", frameslist_nmlz, "\n"
    #adjust normalized time within each normalized boundary
    timelist_nmlz_frame_adjusted = adjust_to_scaled_boudaries(timelist_nmlz, frame_ref)
    print "timelist_nmlz_frame_adjusted",timelist_nmlz_frame_adjusted
    #normalized time of boundaries
    frameslist_nmlz_frame_adjusted = []
    frame_counter = 1
    while frame_counter < ns*2+1:
        adjusted_frame = frame_counter * frame_ref
        frameslist_nmlz_frame_adjusted.append(adjusted_frame)
        frame_counter += 1

    #frameslist_nmlz_frame_adjusted = adjust_to_scaled_boudaries(frameslist_nmlz, frame_ref)
    print "frameslist_nmlz_frame_adjusted", frameslist_nmlz_frame_adjusted
    #sort time and fo values by frame
    #create list of lists (one list for each frame, for indices, time, and fo)
    x = ns*2
    frames_matrix = [[] for item in range(x)]
    time_by_frame = [[] for item in range(x)]
    fo_by_frame = [[] for item in range(x)]
    #get each boundary and evaluate if each time value is lesser
    #than the boundary and assign it to the frame before this boundary.
    y = len(frameslist_nmlz_frame_adjusted)
    j = 0
    x = len(timelist_nmlz_frame_adjusted)
    i = 0
    while j < y:
        while i < x and timelist_nmlz_frame_adjusted[i] <= frameslist_nmlz_frame_adjusted[j]:
            frames_matrix[j].append(i)
            fo_by_frame[j].append(folist_nmlz[i])
            time_by_frame[j].append(timelist_nmlz_frame_adjusted[i])
            i += 1
    	j += 1

    #print frames_matrix
    print 'fo_by_frame', fo_by_frame
    print 'time_by_frame', time_by_frame


    print '# PRETONES	################################'
    pretones_x = []
    pretones_y = []

    #print "\n-> list of pretones\n\ttime\tfo\nstart\t",round(timelist_nmlz_frame_adjusted[0],0), "\t", folist_nmlz[0]
    f.write("pretone\ttime\tfo\nstart\t%s\t%s\n" % (round(timelist_nmlz_frame_adjusted[0],0),folist_nmlz[0]))
    pretones_x.append(round(timelist_nmlz_frame_adjusted[0],0))
    pretones_y.append(folist_nmlz[0])

    x = 0
    for x in range(ns*2):
        subset_frame = frames_matrix[x]
        if not subset_frame:
            #print x+1, "a", "\t-\t-"
            #print x+1, "b", "\t-\t-"
            f.write("%sa\t-\t-\n" % (x+1))
            f.write("%sb\t-\t-\n" % (x+1))
            #pretones_x.append('x'); pretones_x.append('x')
            #pretones_y.append('y'); pretones_y.append('y')
            x += 1
        else:
            subset_time = time_by_frame[x]
            subset_fo = fo_by_frame[x]
            low = min(subset_fo)
            high = max(subset_fo)
            low_time = round(subset_time[subset_fo.index(low)],0)
            high_time = round(subset_time[subset_fo.index(high)],0)
            if low_time < high_time:
                #print x+1, "a", "\t", low_time, "\t",low
                #print x+1, "b", "\t", high_time, "\t", high
                pretones_x.append(low_time); pretones_x.append(high_time)
                pretones_y.append(low); pretones_y.append(high)
                f.write("%sa\t%s\t%s\n" % (x+1, low_time, low))
                f.write("%sb\t%s\t%s\n" % (x+1, high_time, high))
            else:
                #print x+1, "a", "\t", high_time, "\t", high
                #print x+1, "b", "\t", low_time, "\t",low
                pretones_x.append(high_time); pretones_x.append(low_time)
                pretones_y.append(high); pretones_y.append(low)
                f.write("%sa\t%s\t%s\n" % (x+1, high_time, high))
                f.write("%sb\t%s\t%s\n" % (x+1, low_time, low))
            x += 1
    #print "end\t",round(timelist_nmlz_frame_adjusted[-1],0), "\t", folist_nmlz[-1]
    f.write("end\t%s\t%s" % (round(timelist_nmlz_frame_adjusted[-1],0),folist_nmlz[-1]))
    pretones_x.append(round(timelist_nmlz_frame_adjusted[-1],0))
    pretones_y.append(folist_nmlz[-1])
    f.close()

    pretones_list = tuple(zip(pretones_x, pretones_y))
    print 'PRETONES:', pretones_list
    print 'number of pretones:', len(pretones_list)






    #create a graph for the pretonal contour
    sample_tag = os.path.join(os.path.splitext(fichier)[0])
    pylab.figure(figure_counter)
    pylab.plot(pretones_y, lw = 2, color='k')
    pt = 1.5
    while pt < len(pretones_list)+1:
        pylab.plot([pt, pt], [0, 100], 'k', lw=1)
        pt = pt + 4
    pylab.title('Pretones for sample %s' % sample_tag)
    pylab.xlabel('time in %')
    pylab.ylabel('fo in %')
    pylab.savefig('pretones_'+ sample_tag)
    print "\n-> graph 'Pretones for sample %s' was printed to directory \n" % sample_tag


    print '# TONES ####################################'
    pretones_y_reversed = pretones_y[::-1]
    lastPretone = len(pretones_y) -1
    print 'last pretone:', lastPretone + 1
    #print pretones_y_reversed
    #movement scanning Left -> Right and Right -> Left:
    ups_and_downs = pretonal_mvt(pretones_y)
    print "ups_and_downs is:",ups_and_downs
    ps_and_downs_reversed = pretonal_mvt(pretones_y_reversed)
    print "ps_and_downs_reversed is:",ps_and_downs_reversed
    #scan list of individual movements for consecutive ascending movements
    #direction: 1 going up, 0 going down
    going_up = scan_mvt_span(ups_and_downs)
    print "going_up\tis:", going_up
    going_down_reversed = scan_mvt_span(ps_and_downs_reversed)
    going_down = going_down_reversed[::-1]
    print "going_down\tis:", going_down

    print len(going_up)
    # smoothing
    top = []
    for i, j in enumerate(going_up):
       # print i, ",", j
        if i == len(going_up) -1:
            top.append(i)
        elif i == 0:
            top.append(i)
        elif j > 0 and going_up[i + 1] == 0:
            top.append(i)
    print "top: ", top

    bottom = []
    for i, j in enumerate(going_up):
       # print i, ",", j
        if i == len(going_up) -1:
            break
        elif j > 0 and going_up[i -1] == 0:
            bottom.append(i-1)
    print "bottom: ", bottom

    tonal_contour_pt = sorted(top + bottom)
    print "tonal contour pt : ",tonal_contour_pt
    print pretones_y

    tonal_contour_fo = []
    tonal_contour_time = []
    for x in tonal_contour_pt:
        tonal_contour_fo.append(pretones_y[x])
        tonal_contour_time.append(pretones_x[x])
    print "tonal contour fo : ",tonal_contour_fo
    print "tonal contour time : ",tonal_contour_time

# get going up on tonal_contour_fo and do a second smoothing
# or review below
# below does not work because it stops with the first matching instance
    low_fo =[]
    for x in enumerate(tonal_contour_fo):
        if tonal_contour_fo.index(x) <= 2 or tonal_contour_fo.index(x) >= len(tonal_contour_fo) -3:
            pass
        elif x < tonal_contour_fo[tonal_contour_fo.index(x)-1] and x < tonal_contour_fo[tonal_contour_fo.index(x)+1] and tonal_contour_fo[tonal_contour_fo.index(x)-1] > tonal_contour_fo[tonal_contour_fo.index(x)-3] and tonal_contour_fo[tonal_contour_fo.index(x)+1] > tonal_contour_fo[tonal_contour_fo.index(x)+3]:
            low_fo.append(x)
        elif x < tonal_contour_fo[tonal_contour_fo.index(x)-1] and x < tonal_contour_fo[tonal_contour_fo.index(x)+1] and tonal_contour_fo[tonal_contour_fo.index(x)-2] < tonal_contour_fo[tonal_contour_fo.index(x)-1] and tonal_contour_fo[tonal_contour_fo.index(x)-1] < tonal_contour_fo[tonal_contour_fo.index(x)+1]:
            low_fo.append(x)
        elif x < tonal_contour_fo[tonal_contour_fo.index(x)-1] and x < tonal_contour_fo[tonal_contour_fo.index(x)+1] and tonal_contour_fo[tonal_contour_fo.index(x)-1] > tonal_contour_fo[tonal_contour_fo.index(x)+1] and tonal_contour_fo[tonal_contour_fo.index(x)+1] > tonal_contour_fo[tonal_contour_fo.index(x)+2]:
            low_fo.append(x)
        else:
            pass


    print "low :", low

    #the leftmost tone is the leftmost pretone
    Init_Tone = [0, pretones_x[0], pretones_y[0]]

    #Scan for the main tonal group in the complete list of pretones
    Hstar = tonal_gp(pretones_y, pretones_x, going_up, going_down)
    print "Hstar is: ", Hstar

    #Scan material before the main peak
    prelimit = Hstar[0] #Lead_L_pt
    print "limit is ", prelimit + 1
    if prelimit < 2:
        prepeak = Init_Tone
    else:
        #create the list of pretones before the main peak
        pre_fo_pos = [ y for y in pretones_y if pretones_y.index(int(y)) < prelimit]
        pre_time_pos = [ x for x in pretones_x if pretones_x.index(int(x)) < prelimit]
        print "pre_fo_pos is: ", pre_fo_pos
        print "pre_time_pos is: ", pre_time_pos
        #Scan for the main tonal group in the complete subset of pretones
        prepeak = tonal_gp(pre_fo_pos, pre_time_pos, going_up, going_down)
    print "pre-peak is: ", prepeak

    #Scan material after the main peak
    postlimit = Hstar[6] #Lead_L_pt
    print "limit is ", postlimit
    if postlimit > lastPretone - 2:
        postpeak = [lastPretone, pretones_x[lastPretone], pretones_y[lastPretone]]
    else:
        #create the list of pretones after the main peak
        post_fo_pos = [y for y in pretones_y if pretones_y.index(int(y)) > postlimit]
        post_time_pos = [y for y in pretones_y if pretones_y.index(int(y)) > postlimit]
        print "post_fo_pos is: ", post_fo_pos
        print "post_time_pos is: ", post_time_pos
        #Scan for the main tonal group in the complete subset of pretones
        postpeak = tonal_gp(post_fo_pos, post_time_pos, going_up, going_down)
    print "post-peak is: ", postpeak

    #create the data for the tonal pattern
    if postlimit > lastPretone - 2 and prelimit < 2:
        tp_pt = [prepeak[0],Hstar[0],Hstar[3],Hstar[6],postpeak[0]]
        tp_fo = [prepeak[1],Hstar[1],Hstar[4],Hstar[7],postpeak[1]]
        tp_time = [prepeak[2],Hstar[2],Hstar[5],Hstar[8],postpeak[2]]

    elif postlimit > lastPretone - 2:
        tp_pt = [Init_Tone[0],prepeak[0],prepeak[3],prepeak[6],Hstar[0],Hstar[3],Hstar[6],postpeak[0]]
        tp_fo = [Init_Tone[1],prepeak[1],prepeak[4],prepeak[7],Hstar[1],Hstar[4],Hstar[7],postpeak[1]]
        tp_time = [Init_Tone[2],prepeak[2],prepeak[5],prepeak[8],Hstar[2],Hstar[5],Hstar[8],postpeak[2]]

    elif prelimit < 2:
        tp_pt = [prepeak[0],Hstar[0],Hstar[3],Hstar[6],postpeak[0],postpeak[3],postpeak[6]]
        tp_fo = [prepeak[1],Hstar[1],Hstar[4],Hstar[7],postpeak[1],postpeak[4],postpeak[7]]
        tp_time = [prepeak[2],Hstar[2],Hstar[5],Hstar[8],postpeak[2],postpeak[5],postpeak[8]]

    else:
        tp_pt = [Init_Tone[0],prepeak[0],prepeak[3],prepeak[6],Hstar[0],Hstar[3],Hstar[6],postpeak[0],postpeak[3],postpeak[6]]
        tp_fo = [Init_Tone[1],prepeak[1],prepeak[4],prepeak[7],Hstar[1],Hstar[4],Hstar[7],postpeak[1],postpeak[4],postpeak[7]]
        tp_time = [Init_Tone[2],prepeak[2],prepeak[5],prepeak[8],Hstar[2],Hstar[5],Hstar[8],postpeak[2],postpeak[5],postpeak[8]]

    print 'tonal pattern pt:', tp_pt
    print 'tonal pattern fo:', tp_fo
    print 'tonal pattern time:', tp_time

    #Print a graph of Tones to the directory
    sample_tag = os.path.splitext(fichier)[0]
    pylab.figure(figure_counter+1)
    pylab.plot(tonal_contour_pt, tonal_contour_fo, linewidth = 2, color='k')
    pylab.ylim([0,100])
    pylab.xlim([0,ns*4+2])
    pt = 1.5
    while pt < len(pretones_list)+1:
        pylab.plot([pt, pt], [0, 100], 'k', lw=1)
        pt = pt + 4
    pylab.title('Tones for sample %s' % sample_tag)
    pylab.xlabel('time in %')
    pylab.ylabel('fo in %')
    pylab.savefig('tones_'+ sample_tag)
    print "\n-> graph 'Tones for sample %s' was printed to directory \n" % sample_tag

    figure_counter +=2











    #Associate frame tags to their value
    #syl_dict_pc_frame_adjusted = dict(zip(frame_tags, frameslist_pc_frame_adjusted))
    #print "syl_dict_pc_frame_adjusted:",syl_dict_pc_frame_adjusted






	#Provide fram tags and create a dictionnary for frames {tag : value}
	#frame_tags = ['1a', '1b', '2a', '2b', '3a', '3b', '4a','4b', '5a', '5b', '6a', '6b', '7a', '7b']
	#syl_dict_pc = dict(zip(frame_tags, frameslist_pc))
	#timelist_pc_frame_adjusted = adjust_to_scaled_boudaries(timelist_pc, frame_ref)
	#print "timelist_pc_frame_adjusted",timelist_pc_frame_adjusted
