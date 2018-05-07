#--------------------------------------------------------------------------------#
# File name:emudb.py
# Author:Kumo
# Last edit time(Y-m-d):2018-04-15
# Description:This is the model of emuDB.EmuDB is the database that stores 
#             information about emu trains.This infomation contians emu model
#             (as type), department, departure&arrival station and so on.Function
#             store() can store infos to database from json files.
#--------------------------------------------------------------------------------#

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('config', '../config.py')
import config
from pymongo import MongoClient

class emuDb(object):
    def __init__(self, address=config.databaseIp, port=config.databasePort):
        self.mydb =MongoClient(address, port).emudb
        print 'emudb loaded'

class emuinfoDb(emuDb):

    def __init__(self):
        emuDb.__init__(self)
        self.__mySet = self.mydb.emuinfoSet
        print 'emuinfoSet loaded'

    def storeData(self, infoDict):# trainNo, havedata, emutype, vehicleDep, staffDep, startSta, endSta, sequence, remark)
        self.__mySet.insert_one(infoDict)
        return 1
    
    def queryData(self, trainNo):
        res = self.__mySet.find({"trainNo":trainNo})
        if res.count():
            return 1, res[0]
        else:
            return 0, {}
        
    def updateInfo(self, infoDict):
        res = self.__mySet.find_one({"trainNo":infoDict["trainNo"]})
        resid = res['_id']
        if res:
            self.__mySet.update_one({"_id":resid},{"$set":infoDict})
            return 1
        else:
            return 0
    
    def allInfo(self):
        return 1, self.__mySet.find({})
    
    def deleteInfo(self, trainNo='ALL'):
        if trainNo =='ALL':
            deleteObj = self.__mySet.delete_many({})
            return deleteObj.deleted_count
        else:
            deleteObj = self.__mySet.delete_many({"trainNo":trainNo})
            return deleteObj.deleted_count

class emuseqDb(emuDb):

    def __init__(self):
        emuDb.__init__(self)
        self.__mySet = self.mydb.emuseqSet
        print 'emuseqSet loaded'
    
    def insertSeq(self, seqDict):
        self.__mySet.insert_one(seqDict)
        return 1
    
    def queryBySeqnum(self, num):
        res =self.__mySet.find({'seqNum':num})
        if res.count():
            return 1,res[0]
        else:
            return 0,{}
    
    def deleteSeq(self,num=-1):
        if num ==-1:
            deleteObj = self.__mySet.delete_many({})
            return deleteObj.deleted_count
        else:
            deleteObj = self.__mySet.delete_many({"seqNum":num})
            return deleteObj.deleted_count

def store(fileName='emuinfo.json'):
    import json
    with open(fileName, 'r') as fi:
        emuinfo = json.load(fi)
    myDb = emuinfoDb()
    print str(myDb.deleteInfo()) +' : deleted'
    for every in emuinfo:
        myDb.storeData(every)
    print 'Store '+fileName+' Done'

if __name__ == '__main__':
    store()
