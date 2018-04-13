#--------------------------------------------------------------------------------#
# File name:getlate.py
# Author:Kumo
# Last edit time(Y-m-d):2018-04-13
# Description:This script runs independently to collect information of trains'
#             arrival time.An endless loop is held in function getData but it 
#             will be replaced in later version.
#--------------------------------------------------------------------------------#

import tools
import json

def getData():
    import db2, datetime, random, urllib2, re, time#, #socks, socket
    schqdb = db2.schDb()
    staqdb = db2.staDb()
    ressdb = db2.resDb()
    header={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept":"*/*"}
    queryCache = []
    while(True):
        try:
            zoneDelta =7 # delta between your timezone and cst
            nowTime = datetime.datetime.now() + datetime.timedelta(hours = zoneDelta)
            today = nowTime.strftime('%Y-%m-%d')
            nowInt = nowTime.hour*60 +nowTime.minute
            print 'Time:' +tools.int2str(nowInt)
            queryStartInt = nowInt +2 if nowInt <1438 else nowInt -1438
            queryEndInt = nowInt +5 if nowInt <1435 else nowInt -1435
            resStartInt = nowInt -5 if nowInt >4 else nowInt +1435
            resEndInt = nowInt -2 if nowInt >1 else nowInt +1438
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
            cacheStr = 'cache' +u'\u7684\u957F\u5EA6\uFF1A' +str(len(queryCache)) +':'
            for everyCache in queryCache:
                cacheStr =cacheStr +everyCache['trainNum'] +\
                        '-' +everyCache['arrSta']+\
                        '-' +tools.int2str(everyCache['arrTime'])+\
                        '-' +tools.int2str(everyCache['actTime'])+' / '
            print cacheStr

            i =0
            while i < len(queryCache):
                if (queryCache[i]['arrTime'] if queryCache[i]['actTime']==1441 else queryCache[i]['actTime']) in (range(resStartInt,resEndInt) if resEndInt>resStartInt else range(resStartInt,1440)+range(0,resEndInt)):
                    queryStatus, staInfo = staqdb.searchByTele(queryCache[i]['arrSta'])
                    apiUrl ='http://dynamic.12306.cn'+\
                            '/mapping/kfxt/zwdcx/LCZWD/cx.jsp?'+\
                            'cz=' +tools.EncodeGbk(staInfo['staCn'])+\
                            '&cc='+queryCache[i]['trainNum']+\
                            '&cxlx=0&rq='+today+\
                            '&czEn=' +tools.EncodeUtf8(staInfo['staCn'])+\
                            '&tp=' +datetime.datetime.now().strftime("%s")+ str(random.randint(1000,9999))
                    print apiUrl
                    request = urllib2.Request(apiUrl, headers=header)
                    Res2 = urllib2.urlopen(request).read().decode('gbk')
                    # print Res2
                    Res2 = Res2 +'99:99'
                    ActAr = re.findall('\\d{2}:\\d{2}', Res2)
                    # ActNo = re.findall('\w\d{1,4}', Res.read())
                    print 'Re: '+u'\u8f66\u6b21\uff1a'+queryCache[i]['trainNum']+\
                          ' | '+u'\u5230\u7ad9\uff1a'+staInfo['staCn']+staInfo['staTele']+\
                          ' | '+u'\u5e94\u5230\uff1a'+tools.int2str(queryCache[i]['arrTime'])+\
                          ' | '+u'\u5b9e\u5230\uff1a'+ActAr[0]
                    if ActAr[0] == '99:99':
                        queryCache[i]['status'] =queryCache[i]['status'] +1
                        if queryCache[i]['status'] >2:
                            print 'too many bad connection, quit'
                            queryCache.pop(i)
                    else:
                        actInt =tools.str2int(ActAr[0])
                        if nowInt-actInt>=0 and nowInt-actInt<=60:
                            print u'\u6CA1\u95EE\u9898\uFF0C\u5199\u5165\u6570\u636E\u5E93\uFF1A'+\
                                queryCache[i]['trainNum'] +queryCache[i]['arrSta'] +ActAr[0]
                            ressdb.saveRes(queryCache[i]['trainNum'], queryCache[i]['arrSta'], queryCache[i]['arrTime'], actInt)
                            queryCache.pop(i)
                        elif nowInt-actInt>=-1440 and nowInt-actInt<=-1380:
                            print u'\u53D1\u751F\u96F6\u70B9\u4EA4\u8D8A\uFF0C\u5199\u5165\u6570\u636E\u5E93\uFF1A'+\
                                queryCache[i]['trainNum'] +queryCache[i]['arrSta'] +ActAr[0]
                            ressdb.saveRes(queryCache[i]['trainNum'], queryCache[i]['arrSta'], queryCache[i]['arrTime'], actInt)
                            queryCache.pop(i)
                        else:
                            print queryCache[i]['trainNum'] +queryCache[i]['arrSta'] +tools.int2str(queryCache[i]['actTime']) +ActAr[0]
                            queryCache[i]['actTime'] = actInt
                            i =i +1
                    
                    print '- '*32
                else:
                    i= i +1
            print '='*64
            time.sleep(48)
        except (urllib2.URLError, urllib2.HTTPError), err:
            print err 
            print 'quit'

if __name__ == "__main__":
    try:
        getData()
    except KeyboardInterrupt, err:
        print err
        print 'bye'