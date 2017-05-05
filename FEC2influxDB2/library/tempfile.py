import json
import time
import datetime

class tempfile():

    def __init__(self,filename):

        self._filename = filename
        print('tempfile',filename)

        if not self.openfile():
            self.createfile()

    def openfile(self):
        try:
            with open(self._filename)as fh:
                data = json.load(fh)
                fh.close()
        except IOError:
            data = None

        return data

    def createfile(self):

        data = {}
        data['INITAL_START']=time.time()
        print('print',data)
        self.writefile(data)


    def writefile(self,data):
        print('tempfile',data)
        with open(self._filename,'w')as fh:
            json.dump(data,fh,indent =4)

        fh.close()
        return True

    def readfile(self):
        with open(self._filename,'r')as fh:
            data = json.load(fh)

        fh.close()
        return data
