import  sys, os, csv, pylab, math, json

class DataFromCsv(object):

    def __init__(self,json_file, syllable_csv, tokens_origin_csv):
        self.json_file = json_file
        self.spans = syllable_csv
        self.origins = tokens_origin_csv

    def get_token_tag(self):
        base = os.path.basename(self.json_file)
        tag = os.path.splitext(base)[0]
        return tag

    def csvToLists(self):
        TimeList = []
        FoList = []
        with open(self.json_file) as f:
            data = f.read()
            JsonData = json.loads(data)
        ContourData = JsonData["ContourData"]
        for key, value in ContourData.items():
            time = key.strip()
            fo = value.strip()
            TimeList.append(float(time))
            FoList.append(float(fo))
        return [TimeList, FoList]

    # Syllable spans in a single file: sampleTag, syllable position, duration
    def retrieveSpans(self):
        SpansList = []
        with open(self.spans, mode='rU') as f:
            reader = csv.reader(f,delimiter=',')
            next(reader)
            for num, row in enumerate(reader):
                if row[0] == self.get_token_tag():
                    SpansList.append(str(row[2]))
        return SpansList

    def getStartTime(self):
        with open(self.origins, mode='rU') as f:
            reader = csv.reader(f,delimiter=',')
            next(reader)

            TagRow = []
            for row in reader:
                #print("row",row)
                if row[0] == self.get_token_tag():
                    TagRow.append(row)

            #TagRow = [row for row in reader if row[0] == self.get_token_tag()]
            #print('la valeur', TagRow)
            return float(TagRow[0][1])

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
                TimeList = []
                FoList = []
                with open(self.contour, mode='rU') as f:
                    reader = csv.reader(f)
                    for num, row in enumerate(reader):
                        time = row[0]
                        fo = row[1]
                        TimeList.append(float(time))
                        FoList.append(float(fo))
                return [TimeList, FoList]
"""
