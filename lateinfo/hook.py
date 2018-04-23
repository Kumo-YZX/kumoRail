#--------------------------------------------------------------------------------#
# File name:hook.py
# Author:Kumo
# Last edit time(Y-m-d):2018-04-14
# Description:Provide hooks to catch data from website.
#--------------------------------------------------------------------------------#
import urllib2, json, socket

header={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept":"*/*"}

class trainData(object):

    def __init__(self, date='0000-00-00'):
        if date == '0000-00-00':
            import datetime
            date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.__trainclassUrl = ['http://mobile.12306.cn/weixin/wxcore/queryTrain?ticket_no=', '&depart_date=' +date]
        self.__trainTimetableUrl = ['http://mobile.12306.cn/weixin/czxx/queryByTrainNo?train_no=', '&from_station_telecode=BBB&to_station_telecode=BBB&depart_date=' +date]

    def setTrainNum(self, trainNum):
        self.__trainNum = trainNum
        return 1
        
    def getTrainStrcode(self):
        try:
            rawData = urllib2.urlopen(self.__trainclassUrl[0] +self.__trainNum[0] +self.__trainclassUrl[1], timeout=1.4)
            unpackedData = json.loads(rawData.read())['data']
        except (urllib2.URLError, urllib2.HTTPError), err:
            print err
            return 0

        self.__trainStrcode=[]
        for every in unpackedData:
            if every['ticket_no']==self.__trainNum:
                self.__trainStrcode.append(every['train_code'])
        if len(self.__trainStrcode):
            return 1
        else:
            return 2

    def getTrainTimetable(self):
        print self.__trainStrcode
        unpackedData=[]
        try:
            for every in self.__trainStrcode:
                rawData = urllib2.urlopen(self.__trainTimetableUrl[0] +every +self.__trainTimetableUrl[1], timeout=1.4)
                unpackedData.append(json.loads(rawData.read())['data']['data'])
        except (urllib2.URLError, urllib2.HTTPError), err:
            print err
            return 0

        return unpackedData

class getLate(object):

    def __init__(self, staGbk, trainNum, dayStr, staUtf, timeStr, proxyFilename='proxyList.json'):
        self._apiUrl ='http://dynamic.12306.cn'+\
                      '/mapping/kfxt/zwdcx/LCZWD/cx.jsp?'+\
                      'cz=' +staGbk+\
                      '&cc='+trainNum+\
                      '&cxlx=0&rq='+dayStr+\
                      '&czEn=' +staUtf+\
                      '&tp=' +timeStr
        print self._apiUrl
        with open(proxyFilename, 'r') as fi:
            self._proxyList =json.load(fi)

    def proxyGet(self, proxyNo):
        self._proxyUrl ='http://user:password@' +self._proxyList[proxyNo]['address']+':'+str(self._proxyList[proxyNo]['port'])
        print self._proxyUrl
        proxySupport = urllib2.ProxyHandler({'http':self._proxyUrl})
        opener = urllib2.build_opener(proxySupport)
        urllib2.install_opener(opener)
        try:
            request = urllib2.Request(self._apiUrl, headers=header)
            Res2 = urllib2.urlopen(request, timeout=5).read().decode('gbk')
        except (urllib2.HTTPError, urllib2.URLError, socket.timeout, socket.error) as error:
            print error
            print 'proxy connect failed : ' +self._proxyUrl
            self._proxyList[proxyNo]['fail'] +=1
            return 0, ''
        return 1, Res2

    def localGet(self):
        try:
            request = urllib2.Request(self._apiUrl, headers=header)
            Res2 = urllib2.urlopen(request, timeout=5).read().decode('gbk')
        except (urllib2.HTTPError, urllib2.URLError, socket.timeout, socket.error) as error:
            print error
            print 'local connect failed'
            return 0, ''
        return 1, Res2

    def writeProxyFile(self, proxyFilename='proxyList.json'):
        with open(proxyFilename, 'w') as fo:
            json.dump(self._proxyList, fo)
        return 1

def getTrainArrival(trainNum):
    mytrain = trainData()
    mytrain.setTrainNum(trainNum)
    if mytrain.getTrainStrcode() in [0,2]:
        return u'\u6CA1\u6709\u8BE5\u8F66\u6B21\uFF0C\u6216\u8005\u662F\u670D\u52A1\u5668\u9519\u8BEF'
    data = mytrain.getTrainTimetable()
    res =u'\u6CA1\u6709\u67E5\u8BE2\u5230\u8BE5\u8F66\u6B21\u4FE1\u606F\uFF01'
    for everyTrain in data:
        print everyTrain
        if everyTrain != []:
            everyTrain[0]['arrive_time'] ='-----'
            everyTrain[-1]['start_time'] ='-----'
            res =u'\u5217\u8f66\u7b49\u7ea7\uff1a' +everyTrain[0]['train_class_name'] +u'\u0020\u8f66\u6b21\uff1a' +everyTrain[0]['station_train_code']
            for every in everyTrain:
                res = res +'\n' +every['station_name'] +'--'*(6-len(every['station_name'])) +every['arrive_time'] +'--' +every['start_time']
        else:
            print 'void trainStr here'
    return res

# get train information by departure and arrival
def trainNumber(depDa, depSt, arrSt):
# ?the code in line 81 is used when Python version <=2.7.9
#    ssl._create_default_https_context = ssl._create_unverified_context
	SiteUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date='+depDa+'&leftTicketDTO.from_station='+depSt+'&leftTicketDTO.to_station='+arrSt+'&purpose_codes=ADULT'
	DataGet = urllib2.urlopen(SiteUrl)
	edData = json.loads(DataGet.read())
	edData = edData['data']
	edData = edData['result']
	reData = []
	for everyDat in edData:
		datSplit = everyDat.split('|')
		reData.append({'trainStr':datSplit[2], 'trainNum':datSplit[3], 'depSta':datSplit[4], 'depTime':datSplit[8], 'arrSta':datSplit[5], 'arrTime':datSplit[9], 'consTime':datSplit[10]})
		print u'\u4e32\u7801\uff1a'+datSplit[2]+u'\u8f66\u6b21\uff1a'+datSplit[3]+u'\u59cb\u53d1\u7ad9\uff1a'+datSplit[4]+u'\u7ec8\u70b9\u7ad9\uff1a'+datSplit[5]
	return reData

# get train timetable 
def trainTimetb(Date, depSt, arrSt, trainStr):
# ?the code in line 98 is used when Python version <=2.7.9
#    ssl._create_default_https_context = ssl._create_unverified_context
	SiteUrl = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no='+trainStr+'&from_station_telecode='+depSt+'&to_station_telecode='+arrSt+'&depart_date='+Date
	DataGet = urllib2.urlopen(SiteUrl)
	edData = json.loads(DataGet.read())
	edData = edData['data']
	edData = edData['data']
	edData.pop(0)
	for everyDat in edData:
		print everyDat['station_name'].ljust(16)+everyDat['arrive_time'].center(16)+everyDat['start_time'].rjust(16)
	return edData 

# get emu information by it's number from passearch.info
def processEmuno(msg):
	import httplib
	import re
	
	connUrl = httplib.HTTPConnection('www.passearch.info')
	siteUrl = '/emu.php?type=number&keyword=' + msg
	connUrl.request('GET', siteUrl)
	resMsg = connUrl.getresponse()
	recText = resMsg.read()
	recForm = re.findall(r'<table border="0" align="center">(.*?)</table>', recText)
	if len(recForm) == 0:
		reText = u'\u6ca1\u6709\u627e\u5230\u52a8\u8f66\u7ec4\u914d\u5c5e\u4fe1\u606f'
	else:
		recCount = len(re.findall(r'<tr>', recForm[0])) - 1
		recTd = re.findall(r'<td>(.*?)</td>', recForm[0])
		emuModel = re.findall(r'<a href=emu.php\?type=model&keyword=.*?>(.*?)</a>', recForm[0])
		emuBureau = re.findall(r'<a href=emu.php\?type=bureau&keyword=.*?>(.*?)</a>', recForm[0])
		emuDepartment = re.findall(r'<a href=emu.php\?type=department&keyword=.*?>(.*?)</a>', recForm[0])
		reText = u'\u67e5\u8be2\u5230' + str(recCount) + u'\u6761\uff1a'
		for every in range(recCount):
			emuManufacturer = recTd[7*every+4]
			emuRemark = recTd[7*every+5]
			reText = reText + u'\n\u7b2c' + str(every+1) + u'\u6761\uff1a\n\u8f66\u578b\uff1a' + emuModel[every] + u'\n\u8def\u5c40\uff1a' + emuBureau[every].decode('utf8') + u'\n\u52a8\u8f66\u6240\uff1a' + emuDepartment[every].decode('utf8') + u'\n\u5382\u5bb6\uff1a' + emuManufacturer.decode('utf8') + u'\n\u5907\u6ce8\uff1a' + emuRemark.decode('utf8')
	# print reText
	return reText

if __name__ == '__main__':
    trainNum = raw_input()
    print getTrainArrival(trainNum)