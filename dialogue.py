#--------------------------------------------------------------------------------#
# File name:dialogue.py
# Author:Kumo
# Last edit time(Y-m-d):2018-03-30
# Description:To analyse the text sent by users and search for data in need, 
#             finally an easy-to-read answer will be returned.
#--------------------------------------------------------------------------------#

def dialogue(user, word):
    from lateinfo import tools, db2
    import json
    res = ''
    try:
        category = tools.wordAnalyse(word)
# query for all trains that are monitored
        if category == 1:
            schdb = db2.schDb()
            status, schall = schdb.allSch()
            trainAll = []
            for every in schall:
                if every['trainNum'] not in trainAll:
                    trainAll.append(every['trainNum'])
            res = u'\u6240\u6709\u8f66\u6b21\uff1a'+' & '.join(trainAll)
# query for information of EMU
        elif category == 2:
            res = tools.processEmuno(word) 
# query for lating inforamtion of a train with its telecode
        elif category == 4:
            resdb = db2.resDb()
            stadb = db2.staDb()
            staTele = word[len(word)-3:len(word)]
            resqueryStatus, traindata = resdb.getRes(word[0:len(word)-3], staTele, 15)
            if resqueryStatus:
                days = []
                staqueryStatus, staData = stadb.searchByTele(staTele)
                if staqueryStatus:
                    res = u'\u8f66\u6b21\uff1a'+traindata[0]["trainNum"] + u'\u0020\u5230\u7ad9\uff1a'+ staData['staCn'] + u'\u0020\u5e94\u5230\uff1a'+tools.int2str(traindata[0]['schTime'])
                    for every in traindata:
                        date = every["resTime"].strftime('%Y-%m-%d')
                        if len(days) and date == days[-1]:
                            pass
                        else:
                            res = res + u'\n\u65e5\u671f\uff1a'+date + u'\u0020\u5b9e\u5230\uff1a'+tools.int2str(every['actTime'])
                            days.append(date)
                        # if len(days) >=5:
                        #     break
                    res = res + u'\n\u6570\u636e\u603b\u91cf\uff1a'+str(len(days))
                else:
                    res = u'\u6570\u636e\u5e93\u5185\u6ca1\u6709\u8be5\u7ad9\u7684\u6570\u636e\uff1f'
            else:
                res = u'\u6b63\u665a\u70b9\u67e5\u8be2\uff1a\u7ad9\u70b9\u5728\u6570\u636e\u5e93\u627e\u4e0d\u5230'
# query for EMU category of D &G &C trains
        elif category == 3:
            from emuinfo import emudb
            word = str.upper(word)
            emudb = emudb.emuinfoDb()
            status, emudata = emudb.queryData(word)
            if status:
                # print 'status1'
                if emudata['haveData']:
                    # print 'havedata'
                    with open('emuinfo/stamap2.json', 'r') as fi:
                        stamap = json.load(fi)
                    with open('emuinfo/depmap.json', 'r') as fi:
                        depmap = json.load(fi)
                    stadb = db2.staDb()
                    status1, startSta = stadb.searchByTele(stamap[emudata['startSta']-1])
                    status2, endSta = stadb.searchByTele(stamap[emudata['endSta']-1])
                    # print stamap[emudata['startSta']-1], stamap[emudata['endSta']-1]
                    if status1 and status2:
                        res = u'\u8f66\u6b21\uff1a'+emudata['trainNo']+u'\n\u8f66\u578b\uff1a'+emudata['emuType']+u'\n\u59cb\u53d1\uff1a'+startSta['staCn']+u'\n\u7ec8\u5230\uff1a'+endSta['staCn']+u'\n\u52a8\u8f66\u6bb5\uff1a'+depmap[emudata['vehicleDep']-1]+u'\n\u5ba2\u8fd0\u6bb5\uff1a'+depmap[emudata['staffDep']-1]
                    else:
                        res = u'\u914d\u5c5e\u67e5\u8be2\uff1a\u7ad9\u70b9\u5728\u6570\u636e\u5e93\u627e\u4e0d\u5230'
                else:
                    res = u'\u8f66\u6b21\uff1a'+emudata['trainNo']+u'\u5b58\u5728\uff0c\u4f46\u65e0\u6570\u636e'
            else:
                res = u'\u8f66\u6b21\u4e0d\u5b58\u5728\uff0c\u4e5f\u65e0\u6570\u636e'
# query for telecode of a station by pinyin
        elif category == 5:
            stadb = db2.staDb()
            staqueryStatus, staData = stadb.searchByPy(word)
            if staqueryStatus:
                res = u'\u67e5\u8be2\u7ed3\u679c\uff1a'
                for every in staData:
                    res = res + u'\n\u7ad9\u540d\uff1a' + every['staCn'] + u'\u0020\u7535\u62a5\u7801\uff1a' + every['staTele']
            else:
                res = u'\u6ca1\u6709\u67e5\u5230\u76f8\u5173\u8f66\u7ad9\uff01'
# query for time table of a train that are monitored with Chinese!
        elif category == 6:
            schqueryStatus, schList = db2.schDb().querySch(word[0:-6])
            if schqueryStatus:
                stadb = db2.staDb()
                res = u'\u67e5\u8be2\u7ed3\u679c\uff1a'
                for every in schList:
                    staqueryStatus, staCn = stadb.searchByTele(every['arrSta'])
                    if staqueryStatus:
                        res = res + u'\n\u7ad9\u70b9\uff1a' + staCn['staCn'] + u'\u0020\u5230\u65f6\uff1a' + tools.int2str(every['arrTime'])
                    else:
                        res = res + u'\n\u7ad9\u70b9\uff1a' + every['arrSta'] + u'\u0020\u5230\u65f6\uff1a' + tools.int2str(every['arrTime'])
            else:
                res = u'\u6ca1\u6709\u8be5\u8f66\u6b21\u7684\u505c\u7ad9\u548c\u6b63\u665a\u70b9\u6570\u636e'
# query for lating inforamtion of a train with the station name with Chinese!
        elif category in range(7,11):
            staqueryStatus, sta = db2.staDb().searchByCn(word[category-5:len(word)].decode('utf8'))
            if staqueryStatus:
                resqueryStatus, traindata = db2.resDb().getRes(word[0:category-5], sta['staTele'], 15)
                if resqueryStatus:
                    days = []
                    res = u'\u8f66\u6b21\uff1a'+traindata[0]["trainNum"] + u'\u0020\u5230\u7ad9\uff1a'+ sta['staCn'] + u'\u0020\u5e94\u5230\uff1a'+tools.int2str(traindata[0]['schTime'])
                    for every in traindata:
                        date = every["resTime"].strftime('%Y-%m-%d')
                        if len(days) and date == days[-1]:
                            pass
                        else:
                            res = res + u'\n\u65e5\u671f\uff1a'+date + u'\u0020\u5b9e\u5230\uff1a'+tools.int2str(every['actTime'])
                            days.append(date)
                        # if len(days) >=5:
                        #     break
                    res = res + u'\n\u6570\u636e\u603b\u91cf\uff1a'+str(len(days))
                else:
                    res = u'\u8be5\u8f66\u4e0d\u505c\u9760\u672c\u7ad9\u6216\u65e0\u6570\u636e'
            else:
                res = u'\u8be5\u7ad9\u53ef\u80fd\u4e0d\u5b58\u5728'
# an error occurs
        elif category == 99:
            res = 'tools error'
        else:
            res = u'\u683c\u5f0f\u6709\u8bef'

    except Exception,Argument:
        print Argument
        res = 'dialogue error'
    diadb = diaDb()
    res = res.encode('utf8')
    diadb.write(user, word, res)
    return res

# the database of every text
class diaDb(object):

    def __init__(self, address='127.0.0.1', port=27017):
        from pymongo import MongoClient
        self.__diaset = MongoClient(address, port).diadb.diaset
        print 'diadb init done'

    def write(self, user, word, reply):
        import datetime
        self.__diaset.insert_one({"time":datetime.datetime.now(), "user":user, "word":word, "reply":reply})
        return 1
    
    def read(self, startTime, endTime):
        res = self.__diaset.find({"time": {"$gt":startTime ,"$lt":endTime}})
        if res.count():
            return 1, res
        else:
            return 0, []
    
    def delete(self, user):
        if user == '':
            deleteObj = self.__diaset.delete_many({})
            return deleteObj.deleted_count
        else:
            deleteObj = self.__diaset.delete_many({})
            return deleteObj.deleted_count
            
    def all(self):
        res = self.__diaset.find({})
        if res.count():
            return 1, res
        else:
            return 0, []

# to save all the data in diaDb in json
def saveDiaData():
    import json
    import datetime
    myset = diaDb()
    status, res = myset.all()
    diaList = []
    now = datetime.datetime.now()
    if status:
        for every in res:
            diaList.append({"time":every['time'].strftime('%Y-%m-%d-%H-%M-%S'), "user":every['user'], "word":every['word'], "reply":every['reply']})
        with open('dia'+now.strftime('%Y%m%d')+'.json', 'w') as fo:
            json.dump(diaList, fo)
        print 'diaDb output Done'
    else:
        print 'diaDb No Data'

if __name__ == "__main__":
    saveDiaData()

