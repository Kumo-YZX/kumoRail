#--------------------------------------------------------------------------------#
# File name:getlate.py
# Author:Kumo
# Last edit time(Y-m-d):2018-04-04
# Description:This script runs independently to collect information of trains'
#             arrival time.An endless loop is held in function getData but it 
#             will be replaced in later version.
#--------------------------------------------------------------------------------#

import tools
import json

def getData():
    import db2, datetime, httplib, re, time
    schqdb = db2.schDb()
    staqdb = db2.staDb()
    ressdb = db2.resDb()

    while(True):
        zoneDelta = 0 # delta between your timezone and cst
        startTime = endTime = datetime.datetime.now() + datetime.timedelta(hours = zoneDelta)
        today = startTime.strftime('%Y-%m-%d')
        startTime = startTime + datetime.timedelta(minutes = -8)
        endTime = endTime + datetime.timedelta(minutes = -5)
        state, res = schqdb.getSch(startTime.hour*60+startTime.minute, endTime.hour*60+endTime.minute)
        if state:
            for every in res:
                conn = httplib.HTTPConnection("dynamic.12306.cn")
                queryStatus, staInfo = staqdb.searchByTele(every['arrSta'])
                Site = '/mapping/kfxt/zwdcx/LCZWD/cx.jsp?cz=' +tools.EncodeGbk(staInfo['staCn'])+'&cc='+every['trainNum']+'&cxlx=0&rq='+today+'&czEn=' +tools.EncodeUtf8(staInfo['staCn'])+ '&tp=1889163260221'
                conn.request("GET", Site)
                time.sleep(3)
                Res = conn.getresponse()
                Res2 = Res.read()+'99:99'
                ActAr = re.findall('\\d{2}:\\d{2}', Res2)
        #			ActNo = re.findall('\w\d{1,4}', Res.read())
                if ActAr[0] == '99:99':
                    pass
                else:
                    ressdb.saveRes(every['trainNum'], every['arrSta'], every['arrTime'], tools.str2int(ActAr[0]))
                print 'Re: '+u'\u8f66\u6b21\uff1a'+every['trainNum']+' | '+u'\u5230\u7ad9\uff1a'+staInfo['staCn']+staInfo['staTele']+' | '+u'\u5e94\u5230\uff1a'+tools.int2str(every['arrTime'])+' | '+u'\u5b9e\u5230\uff1a'+ActAr[0]
                print '--------------------------------------------------------------------'
                conn.close()
        time.sleep(50)

if __name__ == "__main__":
    getData()