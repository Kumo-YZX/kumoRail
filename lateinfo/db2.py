#--------------------------------------------------------------------------------#
# File name:db2.py
# Author:Kumo
# Last edit time(Y-m-d):2018-04-08
# Description:This is the model of main database that contains lating information
#             and station information and list of trains.
#--------------------------------------------------------------------------------#

from pymongo import MongoClient

class db(object):

    def __init__(self, address='127.0.0.1', port=27017):
        self.mydb = MongoClient(address, port).wxdb
        print 'Wx Database Init Done'

# station database. Station informations are collected form the url in function 
# updateSta.Telecode, name, pinyin of the station are contained.
class staDb(db):

    def __init__(self):
        db.__init__(self)
        self.__stas = self.mydb.staSet
        print 'staDb Init Done'
    
    def updateSta(self):
        import urllib2
        import re
        SiteUrl = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'#?station_version=1.9025'
        RawData = urllib2.urlopen(SiteUrl)
        GetData = re.findall(r'\@\w+\|'+ u"[\x80-\xff]+"+ r'\|\w+\|\w+\|\w+\|\d{1,4}', RawData.read())
        for EveryData in GetData:
            InfoSplit = EveryData.split('|')
            self.__stas.insert_one({"staCn": InfoSplit[1].decode('utf8'), "staTele": InfoSplit[2], "staPy": InfoSplit[4], "staNum":int(InfoSplit[5])})
        return 1

    def deleteSta(self, teleCode):
        if teleCode == '':
            deleteObj = self.__stas.delete_many({})
            return deleteObj.deleted_count
        else:
            deleteObj = self.__stas.delete_many({"staTele":teleCode})
            return deleteObj.deleted_count

    def searchByTele(self, teleCode):
        res = self.__stas.find({"staTele": teleCode})
        if res.count():
            return 1, res[0]
        else:
            return 0, []

    def searchByNum(self, num):
        res = self.__stas.find_one({"staNum": num})
        if res:
            return 1, res
        else:
            return 0, []

    def searchByPy(self, py):
        res = self.__stas.find({"staPy": py})
        if res.count():
            return 1, res
        else:
            return 0, []

    def searchByCn(self, cn):
        res = self.__stas.find({"staCn": cn})
        if res.count():
            return 1, res[0]
        else:
            return 0, []

# list of the train arrivals ()
class schDb(db):

    def  __init__(self):
        db.__init__(self)
        self.__schs = self.mydb.schSet
        print 'schDb Init Done'

    def saveSch(self, trainNum, arrSta, arrTime):
        self.__schs.insert_one({"trainNum": trainNum, "arrSta": arrSta, "arrTime": arrTime})
        return 1

    def saveJson(self, schDict):
        self.__schs.insert_one(schDict)
        return 1

    def getSch(self, startTime, endTime):
        res = self.__schs.find({"arrTime": {"$gt":startTime ,"$lt":endTime}})
        if res.count():
            return 1, res
        else:
            return 0, []
    
    def querySch(self, trainNum):
        res = self.__schs.find({"trainNum": trainNum})
        if res.count():
            return 1, res
        else:
            return 0, []

    def deleteSch(self, trainNum='ALL'):
        if trainNum == 'ALL':
            deleteObj = self.__schs.delete_many({})
            return deleteObj.deleted_count
        else:
            deleteObj = self.__schs.delete_many({"trainNum": trainNum})
            return deleteObj.deleted_count

    def allSch(self):
        res = self.__schs.find({})
        if res.count():
            return 1, res
        else:
            return 0, []

# the lating information 
class resDb(db):

    def __init__(self):
        db.__init__(self)
        self.__ress = self.mydb.resSet

    def saveRes(self, trainNum, arrSta, sch, act):
        import datetime
        self.__ress.insert_one({"resTime":datetime.datetime.now(), "trainNum":trainNum, "arrSta":arrSta, "schTime":sch, "actTime":act})
        return 1
    
    def saveJson(self, resDict):
        self.__ress.insert_one(resDict)
        return 1

    def getRes(self, trainNum, sta, amount):
        res = self.__ress.find({"$and": [{"trainNum":trainNum},{"arrSta":sta}]}).sort("resTime",-1).limit(amount)
        if res.count():
            return 1, res
        else:
            return 0, []

    def deleteRes(self, trainNum):
        if trainNum == '':
            deleteObj = self.__ress.delete_many({})
            return deleteObj.deleted_count
        else:
            deleteObj = self.__ress.delete_many({"trainNum": trainNum})
            return deleteObj.deleted_count
    
    def allRes(self):
        res = self.__ress.find({}).sort("resTime",-1)
        if res.count():
            return 1, res
        else:
            return 0, []

class userDb(db):

    def __init__(self):
        db.__init__(self)
        self.__user = self.mydb.userSet

    def addUser(self, userName, userIdentify, userId):
        self.__user.insert_one({"userName":userName, "userIdentify":userIdentify, "userId":userId})
        return 1

    def findByName(self, userName):
        res = self.__user.find({"userName":userName})
        if res.count():
            return 1,res[0]
        else:
            return 0,{}

    def findById(self, userId):
        res = self.__user.find({"userId":userId})
        if res.count():
            return 1,res[0]
        else:
            return 0,{}

    def findByIdentify(self, userIdentify):
        res = self.__user.find({"userIdentify":userIdentify})
        if res.count():
            return 1,res
        else:
            return 0,[]
    
    def deleteUser(self, userName='ALL'):
        if userName == 'ALL':
            deleteObj = self.__user.delete_many({})
            return deleteObj.deleted_count
        else:
            deleteObj = self.__user.delete_many({"userName":userName})
            return deleteObj.deleted_count

