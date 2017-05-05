
import csv

class csvManager(object):
    def __init__(self,log,delimiter = '\t'):
        self._log = log
        self._delimiter = delimiter
        self._csvObj = []

    def open(self,file):
        result = True
        with open(file) as csvfile:
            try:
              #  print('File true',csvfile)
                self._log.debug('Open CSV file %s', file)
                csvdata = csv.reader(csvfile, delimiter =self._delimiter)
                keys = next(csvdata)
             #   print('gg',keys)
                for row in csvdata:
                    items = dict(zip(keys,row))
                    self._csvObj.append(items)

                self._log.info('Number of lines in CSV file %s',len(self._csvObj))
            except:
                self._log.error('Failed to open CSV file %s',file)
              #  print('File false')
                result = False
        return result

    def getdata(self):
        #print('size',len(self._csvObj))
        return self._csvObj



