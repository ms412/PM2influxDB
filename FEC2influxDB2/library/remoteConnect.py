import paramiko
import time
import os
import csv

#from library.msgbus import msgbus

class remoteSSH():

    def __init__(self,config):

        self._config = config

        self._host = config.get('HOST',None)
        self._user = config.get('USER',None)
        self._passwd = config.get('PASSWD',None)
        self._path = config.get('PATH',None)
        self._filefilter = config.get('FILE_FILTER',None)
        self._tempfile = config.get('TMP_DIR',None)
        self._sftp = None

    def __del__(self):
        if self._sftp is not None:
            self._sftp.close()

    def connect(self):
        self._sshClient = paramiko.SSHClient()
        self._sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._sshClient.connect(self._host, username=self._user, password=self._passwd,timeout=10)
            self._sftp = self._sshClient.open_sftp()
        except Exception as e:
            print ("Connection Failed")
            return False

        return True

    def chdir(self,directory):
        try:
            self._sftp.chdir(directory)
            print('changed to directory')
        except Exception as e:
            print('directory not found')
            return False

        return True

    def getlatestFile(self,filter):
        fileDate = 0
        fileName = None
        for fileattr in self._sftp.listdir_attr():
            if fileattr.filename.startswith(filter) and fileattr.filename.endswith('txt') and fileattr.st_mtime > fileDate:
                fileDate = fileattr.st_mtime
                fileName = fileattr.filename

        return fileName,fileDate

    def getFilesFromDate(self,date,filter):
        filelist = []
        print ('fromGetDate',date,filter)
        for fileattr in self._sftp.listdir_attr():
            if fileattr.filename.startswith(filter) and fileattr.filename.endswith('txt') and fileattr.st_mtime > date:
                filelist.append(fileattr.filename)
        print(filelist)
        return filelist

    def getFile(self,localdir,filename):
        print('TEst',localdir+'/'+filename,self._path+'/'+filename)
        self._sftp.get(self._path+'/'+filename,localdir+'/'+filename)

        return localdir+'/'+filename

class remoteFiles(object):

    def __init__(self,cfg_server,tempdir,log):
        print('config',cfg_server)
        self._cfg_server = cfg_server
        self._tempdir = tempdir
        self._log = log

        self._processList = {}
        self._dataStore = {}
   #     self._remoteSSH = remoteSSH(config)

    def connect(self):
        result = False
        for key, value in self._cfg_server.items():
            print(key,value)
            remoteHandle = remoteSSH(value)

            if (remoteHandle.connect()):
                self._dataStore[key] = {}
                self._dataStore[key]['PROCESS-ID']=remoteHandle
                print(self._dataStore)
                result = True
             #   print('connected to host:',value.get('HOST',None))
                self._log.debug('Connected to Host %s',value.get('HOST',None))
            else:
              #  print('failed to connect to host:',value.get('HOST',None))
                self._log.error('failed to connect to %s',value.get('HOST',None))

        if not result:
            self._log.critical('No Server found')
        return result

    def lookupfile(self):
       # data = self._dataStore
      #  print('before',self._dataStore)
        dictKeys = list(self._dataStore)
       # print('keys',list(self._dataStore))
        for key in dictKeys:
            value = self._dataStore[key]
        #    print('lookup',key,value)
            processID = self._dataStore[key]['PROCESS-ID']
            if processID.chdir(self._cfg_server[key]['PATH']):
                fileName,fileDate = processID.getlatestFile(self._cfg_server[key]['FILE_FILTER'])
         #       print('filelist, date', fileName,fileDate)

                if fileName is not None:
                    self._dataStore[key]['FILEDATE'] = fileDate
                    self._dataStore[key]['FILENAME'] = fileName
          #          print('self._dataStore',self._dataStore)
                else:
           #         print('delelet',key)
                    del self._dataStore[key]

            else:
            #    print('delete2',key)
                del self._dataStore[key]

        return True

    def latestFile(self):
        timeStampTemp = 0
        latest = None
        for key, value in self._dataStore.items():
            timeStamp = value.get('FILEDATE')
            if timeStampTemp < timeStamp:
                timeStampTemp = timeStamp
                latest = key
        self._log.debug('File with the latest timestamp %s', latest)
        return latest

    def getFile(self,id):
        print(id)
        processID=self._dataStore[id]['PROCESS-ID']
        filename = processID.getFile(self._tempdir,self._dataStore[id]['FILENAME'])

    #    return self._dataStore[id]['FILENAME']
        self._log.debug('get filename %s',filename)
        return filename


    def collecetFile(self):
        filename = None
        if self.connect():
            print('connected')
            if self.lookupfile():
                id = self.latestFile()
                print('ID',id)
                filename = self.getFile(id)
        else:
            print('No Server found')

        return filename