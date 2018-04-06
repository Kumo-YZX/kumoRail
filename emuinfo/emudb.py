#--------------------------------------------------------------------------------#
# File name:emudb.py
# Author:Kumo
# Last edit time(Y-m-d):2018-04-03
# Description:This is the model of emuDB.EmuDB is the database that stores 
#             information about emu trains.This infomation contians emu model
#             (as type), department, departure&arrival station and so on.Function
#             store() can store infos to database from json files.
#--------------------------------------------------------------------------------#

from pymongo import MongoClient

class emuinfoDb(object):

    def __init__(self, address='127.0.0.1', port=27017):
        self.__mySet = MongoClient(address, port).emuDb.emuinfoSet
        print 'emuinfoDb init Done'

    def storeData(self, infoDict):# trainNo, havedata, emutype, vehicleDep, staffDep, startSta, endSta, sequence, remark)
        self.__mySet.insert_one(infoDict)
        return 1
    
    def queryData(self, trainNo):
        res = self.__mySet.find({"trainNo":trainNo})
        if res.count():
            return 1, res[0]
        else:
            return 0, []
        
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
    
    def deleteInfo(self, trainNo):
        deleteObj = self.__mySet.delete_many({"trainNo":trainNo})
        return deleteObj.deleted_count

def store(fileName='emuinfo.json'):
    import json
    with open(fileName, 'r') as fi:
        emuinfo = json.load(fi)
    myDb = emuinfoDb()
    for every in emuinfo:
        myDb.storeData(every)
    print 'Store '+fileName+' Done'

if __name__ == '__main__':
    store()
