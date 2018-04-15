#--------------------------------------------------------------------------------#
# File name:importTest.py
# Author:Kumo
# Last edit time(Y-m-d):2018-04-15
# Description:Some function for importing necessary data from json file(s) or 
#             webpages and testing models.
#--------------------------------------------------------------------------------#

import json

def importEmuTrainInfo():
    from emuinfo import emudb
    with open('emuinfo/emuinfo.json', 'r') as fi:
        infoList =json.load(fi)
    mydb =emudb.emuinfoDb()
    for every in infoList:
        mydb.storeData(every)
    print 'importEmuTrainInfo:done'

def importEmuSeq():
    from emuinfo import emudb
    mydb =emudb.emuseqDb()
    with open('emuinfo/seq.json', 'r') as fi:
        seqList =json.load(fi)
    for every in seqList:
        mydb.insertSeq(every)
    print 'importEmuSeq:done'

def emuQuery():
    from emuinfo import emudb
    infodb =emudb.emuinfoDb()
    seqdb =emudb.emuseqDb()
    state1, res1 =infodb.queryData('G79')
    print res1
    state2, res2 =seqdb.queryBySeqnum(20)
    print res2


def updateSta():
    from lateinfo import db2
    mydb = db2.staDb()
    mydb.deleteSta()
    if mydb.updateSta():
        print 'update station info succeed'
    else:
        print 'update station info failed'

def importTimetable(filename='lateinfo/allsch.json'):
    from lateinfo import db2
    with open(filename, 'r') as fi:
        allsch = json.load(fi)
    for every in allsch:
        every['group'] = 0
    schdb = db2.schDb()
    print str(schdb.deleteSch()) + ':deleted'
    for every in allsch:
        schdb.saveJson(every)
    print 'import sch done'

def importResult(filename='lateinfo/lastres.json'):
    from datetime import datetime
    from lateinfo import db2
    with open(filename, 'r') as fi:
        allres = json.load(fi)
    resdb = db2.resDb()
    resdb.deleteRes()
    for every in allres:
        every['resTime'] = datetime.strptime(every['resTime'], '%Y-%m-%d-%H-%M-%S')
        resdb.saveJson(every)
    print 'import res done'

def addUser(filename='lateinfo/users.json'):
    from lateinfo import db2
    with open(filename, 'r') as fi:
        users = json.load(fi)
    userdb = db2.userDb()
    for every in users:
        userdb.addUser(every['name'], every['identify'], every['id'])
        print every['name'] + ':added'
    print 'adduser done'

def importLateinfo():
    updateSta()
    importTimetable()
    importResult()

def importEmuinfo():
    importEmuTrainInfo()
    importEmuSeq()
    emuQuery()
    
if __name__ == '__main__':
    importLateinfo()
    importEmuinfo()
