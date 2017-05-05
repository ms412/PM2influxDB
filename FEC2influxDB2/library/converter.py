
class converter(object):

    def __init__(self,data,log):
        self._data = data
        self._log = log

    def csv2influx(self):

        series = []
     #   print('l',self._data)
        for row in self._data:
           # print('xx',row)
            pointValues = {
                "time": row.get('EndTime'),
  #              "measurement": row.get('EventName'),
                "measurement": 'PM',
                'fields': {
   #                'value': row.get('Value'),
                    row.get('EventName'):row.get('Value'),
                },
                'tags': {
                    "NEName": row.get('NEName'),
                    "ShelfID": row.get('ShelfID'),
                    "BrdID": row.get('BrdID'),
                    "PortID": row.get('PortNO'),
                },
            }
            series.append(pointValues)
        self._log.info('Number of data rows converted %s', len(series))
        return series