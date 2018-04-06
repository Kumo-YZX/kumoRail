#--------------------------------------------------------------------------------#
# File name:importTest.py
# Author:Kumo
# Last edit time(Y-m-d):2018-04-05
# Description:Some function for importing necessary data from json file(s) or 
#             webpages and testing models.
#--------------------------------------------------------------------------------#

def importEmuTrainInfo():
    from emuinfo import emudb
    for name in ['emuinfo/emuinfo.json']:
        emudb.store(name)

def updateSta():
    from lateinfo import db2
    mydb = db2.staDb()
    if mydb.updateSta():
        print 'update station info done'
    else:
        print 'update station info failed'

def importTimetable(filename='lateinfo/allsch.json'):
    import json
    from lateinfo import db2
    with open(filename, 'r') as fi:
        allsch = json.load(fi)
    schdb = db2.schDb()
    for every in allsch:
        schdb.saveJson(every)
    print 'import sch done'

def importResult(filename='lateinfo/allres.json'):
    import json
    from datetime import datetime
    from lateinfo import db2
    with open(filename, 'r') as fi:
        allres = json.load(fi)
    resdb = db2.resDb()
    for every in allres:
        every['resTime'] = datetime.strptime(every['resTime'], '%Y-%m-%d-%H-%M-%S')
        resdb.saveJson(every)
    print 'import res done'

def importTest():
    importEmuTrainInfo()
    updateSta()
    importTimetable()
    importResult()
    
if __name__ == '__main__':
    importTest()
