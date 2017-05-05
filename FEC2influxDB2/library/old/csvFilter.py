import re
import copy
import csv
from datetime import datetime
import time


from library.csvMapper import csvMapper
from library.dicttree import dicttree
from library.dicttree import NestedDict
from library.timeStampManager import timeStampManager



class csvFilter(object):
    def __init__(self, csvfile):

     #   print('filter',csvfile,  filter)
        self._csvfile = csvfile
        self._filter = 0

        # self._timeStampMgr = timeStampManager(lastUpdate)
#        self._timeStamp = lastUpdate
        self._csvData = csvMapper(csvfile)

        self._dataBuffer_PMContainer = {}
        self._dataBuffer_NE = {}
        self._dataBuffer = {}

        self._buffer = NestedDict()

    def getEventDates(self):
        datelist = []
        with open(self._csvfile) as csvfile:
            obj = csv.DictReader(csvfile, delimiter='\t')
            for row in obj:
                templist = []
                templist.append(row['EndTime'])
                if not templist in datelist:
                    datelist.append(templist)

        #    print(datelist)
        return datelist



    def getInterfaces(self):
        NE = set()
        buffer = NestedDict()
        datalist = []
        with open(self._csvfile) as csvfile:
            obj = csv.DictReader(csvfile, delimiter='\t')
            for row in obj:
             #   print(row)
                store = {}
                templist = []
                templist.append(row['NEName'])
                templist.append(row['ShelfID'])
                templist.append(row['BrdID'])
                templist.append(row['PortNO'])
              #  print('templist',templist)
                if not templist in datalist:
                    datalist.append(templist)
               #     print(datalist)


              #  print(row['NEName'])

      #      print('NE',len(datalist),datalist)
            #print(buffer)
        return datalist

    def generateTag(self, interface):
        tag = {}
        tag['NEName']= interface[0]
        tag['ShelfID'] = interface[1]
        tag['BrdID'] = interface[2]
        tag['PortNO'] = interface[3]
        return tag

    def generateFields(self,endTime,filter):
     #   print (endTime,filter)
        fields = {}
        with open(self._csvfile) as csvfile:
            obj = csv.DictReader(csvfile, delimiter='\t')
            for row in obj:
             #   print(row)
                subfields = {}
                if (row['NEName'] == filter[0]) & (row['ShelfID'] == filter[1]) & (row['BrdID'] == filter[2]) & (row['PortNO'] == filter[3]) & (row['EndTime'] == endTime[0]):
              #  if (row['NEName'] == filter[0]) & (row['ShelfID'] == filter[1]) & (row['BrdID'] == filter[2]) & (row['PortNO'] == filter[3]):
                   # print('found',row)
                    fields[row['EventName']] = row['Value']
               #     print('TEST',row['EventName'],row['Value'])
                  #  fields['EventName'] = row['EventName']
                    #subfields['EventID'] = row['EventID']
                    #subfields['Value'] = row['Value']
                   # subfields['UnitName'] = row['UnitName']
                   # fields[row['EventName']]= subfields
      #  print('Field:',fields)

        return fields






    def stringToEpoch(self, date):
       # print('Date',date)
        prog = re.compile('^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
        result = prog.match(date)
        #print(result)

        if date != '0':
            utc_time = datetime.strptime(prog.match(date).group(), "%Y-%m-%d %H:%M:%S")
            epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds()
        else:
            epoch_time = 0
    #    print('Time Epoch:',epoch_time)
       # current_time = datetime.strftime('%Y-%m-%dT%H:%M:%SZ',time.localtime(epoch_time))
        current_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(epoch_time))
     #   print('Time Epoch:',epoch_time, current_time)
        return current_time

    def filterData(self):
    #    print(self._filter)
        for row in self._csvData:
           # print(row)
            if (row['NEName'] == self._filter[0]) & (row['ShelfID'] == self._filter[1]) & (row['BrdID'] == self._filter[2]) & (row['PortNO'] == self._filter[3]):
                self.storeData(self.stringToEpoch(row['EndTime']), row)
          #      print(row)

    def storeData(self,timeStamp,row):

        NEID = row['NEName'] + '-' + row['ShelfID'] + '-' + row['BrdID'] + '-' + row['PortNO']
        pm = {'PMValue': row['Value'],'PMUnit':row['UnitName']}

        self._buffer[timeStamp][NEID][row['EventName']] = pm
     #   print(self._buffer)



    def storeDataold(self, timeStamp, row):
        NEID = row['NEName'] + '-' + row['ShelfID'] + '-' + row['BrdID'] + '-' + row['PortNO']

        pmData = {}
        pmContainer = {}
        print('test', self._dataBuffer_PMContainer)
        pmDate = {}
        pmNE = {}
        pmData['PMValue'] = row['Value']
        pmData['PMUnit'] = row['UnitName']
      #  pmContainer[row['PMParameterName']] = pmData
        pmContainer[row['EventName']] = pmData
      #  print(pmContainer)
        #  pmContainer['EndTime']=timeStamp
        #self._dataBuffer_PMContainer[row['EventName']] = pmData.copy()
      #  self._dataBuffer_PMContainer[NEID]=copy.deepcopy(pmContainer)
        self._dataBuffer[pmDate][NEID]=copy.deepcopy(pmContainer)
     #  pmNE[NEID] = self._dataBuffer_PMContainer
       # print(pmNE)
      #  self._dataBuffer_NE.update(pmNE)
       # self._buffer.append(self._dataBuffer_NE)

        #pmDate[timeStamp]= self._dataBuffer_NE
        #self._dataBuffer.update(pmDate)
        print(self._dataBuffer)

        return True

    def getResults(self):
       # print('buffersize', len(self._dataBuffer), self._dataBuffer)
        return self._buffer



if __name__ == '__main__':
#    msgadapter = msgAdapter()
    filefilterA = csvFilter('c:/temp/Schedule_pfm_WDM_20160728120734393.txt', ['ZHH990.88.1.US1.1', '2', '20', '1'])
    filefilterB = csvFilter('c:/temp/Schedule_pfm_WDM_20160728120734393.txt', ['GEB990.9832.1.US1.2', '0', '17', '1'])

    #  filemgr = csvFileManager('c:/temp/Schedule_pfm_WDM_20160726090747297.txt',1469518253,['ZHH990.88.1.US1.1','2','20','IN/OUT'])
    # print('TimeStamps',filemgr.getTimeStampNewerThan())
    # print('TimeStamps',filemgr.getTimeStampNewerThan(1469518220))
    filefilterA.filterData()
    filefilterB.filterData()
#    temp = filemgr.getData()

  #  z = x.copy()
    storeC = {}
#    print(filefilterA.getDataAll())
    storeA=filefilterA.getDataAll()
    storeB=filefilterB.getDataAll()

 #   storeA = {'a':{'b':{'c':4}}}
  #  storeB  = {'a':{'d':{'c':4}}}

    def merge(a, b, path=None):
        "merges b into a"
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass # same leaf value
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a


    #xy = (merge(storeA,storeB))
    xxx = dicttree()
    xxx.set(storeA)
    xxx.merge(storeB)
    yyy = (xxx.get())

    for key,value in yyy.items():
        #print(key)
        for key1,value1 in value.items():
           print('test',key,key1)
