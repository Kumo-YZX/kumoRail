#--------------------------------------------------------------------------------#
# File name:tools.py
# Author:Kumo
# Last edit time(Y-m-d):2018-04-04
# Description:Many functions that contians analysis tools, hooks, and transform 
#             tools.This functions will be combained with other objects in later 
#             version to make them appropriate.
#--------------------------------------------------------------------------------#

# judge query category
def wordAnalyse(word):
	try:
		print 'word is str type or other'
		if word=='all':
			return 1
			
		if len(word) == 4:
			status=1
			for every in word:
				if every > '9' or every < '0':
					status = 0
					break
			if status:
				return 2

		if word[0] in ['Z', 'T', 'K', 'G', 'D', 'C', 'Y', 'S']:
			status = 1
			for every in word[1:len(word)]:
				if every > '9' or every < '0':
					status = 0
					break
			if status:
				return 3
			status = 1
			for every in word[1:len(word)-3]:
				if every > '9' or every < '0':
					status = 0
					break
			for every in word[len(word)-3:len(word)]:
				if every < 'A' or every > 'Z':
					status = 0
					break
			if status:
				return 4
		
		if len(word) < 6 and len(word) > 0:
			status = 1
			for every in word:
				if every < 'a' or every > 'z':
					status = 0
					break
			if status:
				return 5

		print 'str contain chinese'
		# byteword = word.encode('utf8')
		print word
		if word == '\xE6\x89\x80\xE6\x9C\x89\xE8\xBD\xA6\xE6\xAC\xA1':
			return 1
		
		if word[0] in ['Z', 'T', 'K', 'G', 'D', 'C', 'Y', 'S'] and (len(word)<21 and len(word)>7):
			location = 2
			for location in range(2, 6):
				if word[location] < '0' or word[location] > '9':
					break
			if word[location:location+6] == '\xe5\x81\x9c\xe7\xab\x99':
				return 6
			else:
				return location +5

		print 'analyse end'
		return 0
	except Exception,Argument:
		print Argument
		return 99

# get train information by departure and arrival
def trainNumber(depDa, depSt, arrSt):
	import urllib2, json
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
	import urllib2, json
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

def decodeSave(traSc, No):
	import db2
	stadb = db2.staDb()
	schdb = db2.schDb()
	for EveryDat in traSc:
		state, station = stadb.searchByCn(EveryDat['station_name'])
		if state:
			schdb.saveSch(No, station['staTele'], str2int(EveryDat['arrive_time']))
		else:
			print EveryDat['station_name'] + 'do not found in db'

# transfer time(string) to int numbers
def str2int(timeStr):
	TimSplit = timeStr.split(':')
	Time = int(TimSplit[0])*60+int(TimSplit[1])
	return Time

# transfer int numbers to time(string)
def int2str(timeInt):
	return str(timeInt/60).zfill(2)+':'+str(timeInt%60).zfill(2)

# transfer Chinese string to utf8 code in urls
def EncodeUtf8(str):
	BackStr = ''
	with open('nouse.txt', 'w') as fw:
		fw.write(str.encode('utf8'))
	with open('nouse.txt', 'rb') as fi:
		fi.seek(0.0)
		while True:
			byte = fi.read(1)
			if byte == '':
				break
			else:
				gbk = byte.encode('hex')
				BackStr = BackStr + '-' + gbk.upper()
	return BackStr

# transfer Chinese string to gbk code in urls
def EncodeGbk(str):
	BackStr = ''
	with open('nouse.txt', 'w') as fw:
		fw.write(str.encode('gbk'))
	with open('nouse.txt', 'rb') as fi:
		fi.seek(0.0)
		while True:
			byte = fi.read(1)
			if byte == '':
				break
			else:
				gbk = byte.encode('hex')
				BackStr = BackStr + '%' + gbk.upper()
	return BackStr	

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