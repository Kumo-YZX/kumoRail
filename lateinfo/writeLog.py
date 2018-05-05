import datetime

logfilePath='/var/www/clv/log/'
fileName ='getlatelog'
timeZone ='HKT'

class writrLog(object):

    def __init__(self, filePath=logfilePath, output=1):
        self._path =filePath
        self._output =1

    def write(self, logStr):
        if logStr[-1] != '\n':
            logStr += '\n'
        time =datetime.datetime.now().strftime(timeZone+'-%Y-%m-%d-%H-%M-%S:')
        date =datetime.datetime.now().strftime('%Y%m%d')
        logStr =time +logStr
        if self._output:
            print logStr
        with open(self._path+fileName+date+'.log', 'a') as fo:
            fo.write(logStr.encode('utf8'))

