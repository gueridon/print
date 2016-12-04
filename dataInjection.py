import  sys, os, csv, pylab, math

class DataFromCsv:

    def __init__(self,fo_time_csv, syllable_csv, tokens_origin_csv):
        self.fo_time = fo_time_csv
        self.spans = syllable_csv
        self.origins = tokens_origin_csv

    def getTokenTag(self):
        base = os.path.basename(self.fo_time)
        tag = os.path.splitext(base)[0]
        return tag


    # Contours saved as two-column csv files (time, fo)
    def csvToLists(self):
        time_list = []
        fo_list = []
        with open(self.fo_time, mode='rU') as f:
            reader = csv.reader(f)
            for num, row in enumerate(reader):
                time = row[0]
                fo = row[1]
                time_list.append(float(time))
                fo_list.append(float(fo))
        return [time_list, fo_list]

    # Syllable spans in a single file: sampleTag, syllable position, duration
    def retrieveSpans(self):
        spans_list = []
        with open(self.spans, mode='rU') as f:
            reader = csv.reader(f,delimiter='\t')
            next(reader)
            for num, row in enumerate(reader):
                if row[0] == self.getTokenTag():
                    spans_list.append(str(row[2]))
        return spans_list

    def getStartTime(self):

        with open(self.origins, mode='rU') as f:
            reader = csv.reader(f,delimiter='\t')
            next(reader)
            tag_row = [row for row in reader if row[0] == self.getTokenTag()]
            return float(tag_row[0][2])

"""
    def getOriginalValues(self):
        with open(self.contour, mode='rU') as f:
            reader = csv.reader(f)
            contour_dict = {k: v for k, v in reader}
        return contour_dict

    def getValues(self, column):
        list_of_values = []
        with open(self.contour, mode='rU') as f:
            reader = csv.reader(f)
            for num, row in enumerate(reader):
                value = row[column]
                list_of_values.append(float(value))
        return list_of_values

            def csvToLists(self):
                time_list = []
                fo_list = []
                with open(self.contour, mode='rU') as f:
                    reader = csv.reader(f)
                    for num, row in enumerate(reader):
                        time = row[0]
                        fo = row[1]
                        time_list.append(float(time))
                        fo_list.append(float(fo))
                return [time_list, fo_list]
"""
