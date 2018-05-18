#--------------------------------------------------------------------------------#
# File name:getlate.py
# Author:Kumo
# Last edit time(Y-m-d):2018-05-10
# Description:This script runs independently to collect information of trains'
#             arrival time.An endless loop is held in function getData but it 
#             will be replaced in later version.
#--------------------------------------------------------------------------------#

import tools
import json
import db2, hook, datetime, random, re, time, socket
import writeLog

def loadModule(name, path):
    import os, imp
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), path))

loadModule('config', '../config.py')
import config

def getData():

    schqdb = db2.schDb()
    staqdb = db2.staDb()
    ressdb = db2.resDb()
    log =writeLog.writrLog()
    log.write('getlate starts')
    # header={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
    #         "Accept":"*/*"}
    queryCache = []

    while(True):
        
        nowTime = datetime.datetime.now() + datetime.timedelta(hours = config.zoneDelta)
        today = nowTime.strftime('%Y-%m-%d')
        nowInt = nowTime.hour*60 +nowTime.minute
        log.write('Time:' +tools.int2str(nowInt))
        queryStartInt = nowInt +2 if nowInt <1438 else nowInt -1438
        queryEndInt = nowInt +5 if nowInt <1435 else nowInt -1435
        resStartInt = nowInt -5 if nowInt >4 else nowInt +1435
        resEndInt = nowInt -2 if nowInt >1 else nowInt +1438
        # find schs in the window
        if queryEndInt > queryStartInt:
            state, res = schqdb.getSch(queryStartInt, queryEndInt)
        else:
            state0, res0 = schqdb.getSch(queryStartInt, 1440)
            state1, res1 = schqdb.getSch(0, queryEndInt)
            state = state1 +state0
            res =[]
            for every in res0:
                res.append(every)
            for every in res1:
                res.append(every)

        #add to cache
        if state:
            for everyRes in res:
                status = 1
                for everyCache in queryCache:
                    if everyRes['trainNum'] == everyCache['trainNum']:
                        status = 0
                        break
                if status:
                    everyRes['actTime'] = 1441
                    everyRes['status'] = 0
                    queryCache.append(everyRes)
        cacheStr = 'cache length:' +str(len(queryCache)) +' : '
        for everyCache in queryCache:
            cacheStr =cacheStr +everyCache['trainNum'] +\
                    '-' +everyCache['arrSta']+\
                    '-' +tools.int2str(everyCache['arrTime'])+\
                    '-' +tools.int2str(everyCache['actTime'])+' / '
        log.write(cacheStr)

        # try:
        i =0
        #proxy base number, start number
        proxyUsed =0
        while i < len(queryCache):
            if (queryCache[i]['arrTime'] if queryCache[i]['actTime']==1441 else queryCache[i]['actTime']) in (range(resStartInt,resEndInt) if resEndInt>resStartInt else range(resStartInt,1440)+range(0,resEndInt)):
                queryStatus, staInfo = staqdb.searchByTele(queryCache[i]['arrSta'])
                lateData =hook.getLate(tools.EncodeGbk(staInfo['staCn']),
                                       queryCache[i]['trainNum'],
                                       today,
                                       tools.EncodeUtf8(staInfo['staCn']),
                                       datetime.datetime.now().strftime("%s")+ str(random.randint(1000,9999)),
                                       queryCache[i]['group'])
                while(proxyUsed <4):
                    if proxyUsed ==3:
                        getStatus, Res2 =lateData.localGet()
                        break
                    getStatus, Res2 =lateData.proxyGet(proxyUsed)
                    if getStatus:
                        break
                    proxyUsed +=1
                lateData.writeProxyFile()
                Res2 = Res2 +'99:99'
                ActAr = re.findall('\\d{2}:\\d{2}', Res2)
                # ActNo = re.findall('\w\d{1,4}', Res.read())
                infoStr = 'Re: '+'Train No:'+queryCache[i]['trainNum']+\
                          ' | '+'Station Telecode:'+staInfo['staTele']+\
                          ' | '+'Schedule Arrival Time:'+tools.int2str(queryCache[i]['arrTime'])+\
                          ' | '+'Actual Arrival Time:'+ActAr[0]
                log.write(infoStr)
                if ActAr[0] == '99:99':
                    queryCache[i]['status'] =queryCache[i]['status'] +1
                    if queryCache[i]['status'] >2:
                        log.write('too many bad connection, quit')
                        queryCache.pop(i)
                    i =i +1
                else:
                    actInt =tools.str2int(ActAr[0])
                    if nowInt-actInt>=0 and nowInt-actInt<=60:
                        log.write('No problem, write to database: '+\
                            queryCache[i]['trainNum'] +'' +queryCache[i]['arrSta'] +'' +ActAr[0])
                        ressdb.saveRes(queryCache[i]['trainNum'], queryCache[i]['arrSta'], queryCache[i]['arrTime'], actInt)
                        queryCache.pop(i)
                    elif nowInt-actInt>=-1440 and nowInt-actInt<=-1380:
                        log.write('Cross Zero, write to database: '+\
                            queryCache[i]['trainNum'] +'' +queryCache[i]['arrSta'] +'' +ActAr[0])
                        ressdb.saveRes(queryCache[i]['trainNum'], queryCache[i]['arrSta'], queryCache[i]['arrTime'], actInt)
                        queryCache.pop(i)
                    else:
                        log.write(queryCache[i]['trainNum'] +'' +queryCache[i]['arrSta'] +'' +tools.int2str(queryCache[i]['actTime']) +'' +ActAr[0])
                        queryCache[i]['actTime'] = actInt
                        i =i +1
            else:
                i= i +1
        time.sleep(48)
        # except (urllib2.URLError, urllib2.HTTPError), err:
        #     print err 
        #     print 'quit'

if __name__ == "__main__":
    getData()