#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


__app__ = "FEC2influxDB Adapter"
__VERSION__ = "0.9"
__DATE__ = "20.09.2016"
__author__ = "Markus Schiesser"
__contact__ = "Markus.Schiesser@swisscom.com"
__copyright__ = "Copyright (C) 2016 Markus Schiesser"
__license__ = 'GPL v3'

import sys
import os
import datetime
import json
#import logging

from configobj import ConfigObj
from library.tempfile import tempfile
from library.remoteConnect import remoteFiles
from library.logger import logger
#from library.msgbus import msgbus

from library.csvManager import csvManager
from library.converter import converter
from library.influxManager import influxManager



class manager(object):

    def __init__(self,cfgfile):
        self._cfgfile = cfgfile

        '''
        Configuration variables
        '''
        self._cfg_general = None
        self._cfg_server = None
        self._cfg_db = None
        '''
        Object Handles
        '''
        self._db = None

    def readcfg(self):

        print('openfile',self._cfgfile)
        try:
            configObj = ConfigObj(self._cfgfile)
            print(configObj)
            #return True
        except:
            print('ERROR open file:',self._cfgfile)
            return False

        self._cfg_general = configObj.get('GENERAL')
        self._cfg_server = configObj.get('SERVER')
        self._cfg_db = configObj.get('DB')

        self._log = None

        print('Test',self._cfg_general)

        return True

    def start_loging(self):
        _log = logger(self._cfg_general)
        self._log = _log.start()
        self._log.debug('Start FEC2influxDB Version 0.9 Date 24.11.2016')

    def tempfile(self):
        self._tempfile = tempfile(self._cfg_general['TEMPDIR']+ '/'+ self._cfg_general['TEMPFILE'])

    def getFiles(self):
        result = True
        remote= remoteFiles(self._cfg_server,self._cfg_general['TEMPDIR'],self._log)
        filename = remote.collecetFile()
        if filename is None:
            result =  False
        return result,filename

    def collectData(self,filename):

        csvmgr = csvManager(self._log)

        #print(csvmgr.open(filename))
        if csvmgr.open(filename):
            csvdata = csvmgr.getdata()
        else:
            self._log.critical('Failed to open CSV file %s',filename)
            sys.exit('Failed to open CSV file %s', filename)

        conv = converter(csvdata,self._log)
        return (conv.csv2influx())
       # print(conv.csv2influx())

    def influxdb(self):
   #     print ('influx start')
        self._db = influxManager(self._cfg_db,self._log)
       # self._db.connectdb()

    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        if not self.readcfg():
            print('Failed to open file')
            return False
        self.start_loging()
        self.tempfile()
        self.influxdb()


        """
        Check whether DB is created, if not create it
        """
        data = self._tempfile.readfile()
        if data.get('DB',False):
            self._log.debug('DB should be ready')
            print('DB ready')
            self._db.connectdb()
        else:
            self._log.info('DB not read, to be created')
            print('DB not ready')
            if self._db.createdb():
                self._log.info('DB Created')
                data = self._tempfile.readfile()
                data['DB']= True
                data['DB_CREATED'] = str(datetime.datetime.now())
                self._tempfile.writefile(data)
            else:
                self._log.critical('Failed to create DB')
                self._log.critical('Stop execution')
                sys.exit('Failed to create DB')

        """
        get File with latest timestamp from Servers
        """
        result,filename = self.getFiles()
        if result:
            self._log.info('Data File found on server and downloaded %s', filename)
       #     print(filename)
            #    self.collectData(filename)
        else:
            self._log.critical('Data File not found on server %s',filename)
            sys.exit('Failed to download file %s from Server',filename)

        """
        Collect data from CSV file
        """
        self._log.debug('Start to Convert Data')
        data = self.collectData(filename)
        self._log.debug('Start Write Data to DB')
        for item in data:
       #     print(item)
            self._db.writedb(item)
          #  print(item)
        self._log.info('Wrote %s Measurement Values to DB',len(data))
     #
            #   self.influxdb()
   #     print('delete file',filename)
        self._log.debug('Delete data file from local filesystem %s',filename)
        os.remove(filename)

        self._log.info('Data importet to DB successful')

        return True






if __name__ == "__main__":

    print ('main',len(sys.argv))
    if len(sys.argv) == 2:
        print('with commandline',sys.argv[1])
        cfgfile = sys.argv[1]
    else:
        print('read default file')
        cfgfile = 'C:/Users/oper/PycharmProjects/FEC2influxDB2/FEC2influxDB.cfg'
        cfgfile ='./FEC2influxDB.cfg'
      #  cfgfile = '/home/tgdscm41/FEC2influxDB/FEC2mqtt2.cfg'

    mgr_handle = manager(cfgfile)
    mgr_handle.run()