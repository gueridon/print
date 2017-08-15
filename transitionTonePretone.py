        transitionData = "/Applications/XAMPP/xamppfiles/htdocs/oftenback/linguistics/transition.php"
        pretones_data = self.getPretones()
        tones_data = self.getTones()
        with open(transitionData, 'w') as myphpfile:
            #add line data
            myphpfile.write("var lineData = [  \n")
            for pair in mvt_list:
                row = "[ " + str(pair[0]*3.99 + 32) + ", " + str(217 - pair[1] * 1.8) +  " ],\n"
                myphpfile.write(row)
            myphpfile.write(" ];")
            #add boundary data
            boundaries = self.getBoundariesPCT()
            myphpfile.write("var boundaryRaw = [  \n")
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

        # PRETONES
            #add line data
            myphpfile.write("var lineData = [  \n")
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
                row = "{ 'xa': " + str(position*3.99 + 32) + ", 'ya': " + "35" + ", 'xb': " + str(position*3.99 + 32) + ", 'yb' : " + "217" + " },\n"
                myphpfile.write(row)
            myphpfile.write(" ];")

    # TONES

            #add line data
            myphpfile.write("var lineData = [  \n")
            for tone in tones_data:
                row = "[" + str(tone[2]*3.99 + 32) + ", " + str(217 - tone[3]  * 1.8) +  "],\n"
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
            myphpfile.write("var boundaryTone = [  \n")
            for position in boundaries:
                row = "{ 'xa': " + str(position*3.99 + 32) + ", 'ya': " + "35" + ", 'xb': " + str(position*3.99 + 32) + ", 'yb' : " + "217" + " },\n"
                myphpfile.write(row)
            myphpfile.write(" ];")
            #add title variable
            myphpfile.write("\n var toneNumber = '" + gp_number_of_tones + "';")

        myphpfile.close()
