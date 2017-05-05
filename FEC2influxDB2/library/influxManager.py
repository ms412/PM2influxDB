
import json
from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError


class influxManager(object):
    def __init__(self,config,log):

        print('DB config',config)
        self._dbuser = config.get('USER')
        self._dbpasswd = config.get('PASSWORD')
        self._dbname = config.get('DBNAME')
        self._dbhost = config.get('HOST','localhost')
        self._dbport = config.get('PORT',8086)

        self._log = log

        self._db = None

    def connectdb(self):
        result =  False
        try:
            self._db  = InfluxDBClient(self._dbhost,self._dbport,self._dbuser,self._dbpasswd,self._dbname)
            self._db.create_database(self._dbname)
         #   print('DBTEST',self._db.create_database(self._dbname))
            result = True
        except:
            #print ('FAiler')
            self._log.critical('Cannot connect to DB')
            result = False
        return result

    def createdb(self):
        self.connectdb()
       # print("create db",self._dbname)
        self._log.debug('Create DB %s',self._dbname)
        self._db.create_database(self._dbname)

        #        self._db.create_retention_policy('policy','INF', 'INF', default= True)
        return True

    def writedb(self,str_data):
       # print('data',type(str_data),type(json.loads(str_data)))
        cont= []
        cont.append(str_data)
        self._db.write_points(cont)
        return True

    def querydb(self, query_str):
        value = self._db.query('SELECT'+ self._dbname + 'from' + query_str)
        return value
