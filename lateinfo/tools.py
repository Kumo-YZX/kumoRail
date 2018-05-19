#--------------------------------------------------------------------------------#
# File name:tools.py
# Author:Kumo
# Last edit time(Y-m-d):2018-05-19
# Description:Many functions that contians analysis tools and transform 
#             tools.This functions will be combained with other objects in later 
#             version to make them appropriate.
#--------------------------------------------------------------------------------#

# judge query category
def wordAnalyse(word):
    word02 =str.upper(word[0:2])
    word06 =word[0:6]
    print 'word is str type or other'
    if str.upper(word)=='ALL':
        return 1
    
    if word02 == 'PS':
        return 13
    
    if word02 == 'JL':
        return 14

    if word02 == 'DB':
        return 15

    if word02 == 'JK':
        return 16

    if word02 == 'SF':
        return 11
    
    if word02 == 'SK':
        return 18

    if word02 == 'TJ':
        return 19
    
    if word02 == 'SC':
        return 20

    if word02 =='LY':
        return 21

    print 'str contains chinese'
    # byteword = word.encode('utf8')
    print word
    if word == '\xE8\xBA\xAB\xE4\xBB\xBD':
        return 11

    if word == '\xE6\x89\x80\xE6\x9C\x89\xE8\xBD\xA6\xE6\xAC\xA1':
        return 1
    
    if word06 == '\xE4\xBA\xA4\xE8\xB7\xAF':
        return 3

    if word06 == '\xE6\x97\xB6\xE5\x88\xBB':
        return 12
    
    if word06 == '\xE9\x85\x8D\xE5\xB1\x9E':
        return 2
    
    if word06 == '\xE7\x94\xB5\xE6\x8A\xA5':
        return 5

    if word06 == '\xE7\x9B\x91\xE6\x8E\xA7':
        return 6

    if str.upper(word[0]) in ['Z', 'T', 'K', 'G', 'D', 'C', 'Y', 'S'] +range(49,58) and (len(word)<21 and len(word)>7):
        location = 2
        for location in range(2, 6):
            if word[location] < '0' or word[location] > '9':
                return location +5

    print 'analyse end'
    return 0

def decodeSave(traSc, No):
    import db2
    stadb = db2.staDb()
    schdb = db2.schDb()
    for EveryDat in traSc:
        state, station = stadb.searchByCn(EveryDat['station_name'])
        if state:
            schdb.saveSch(No, station['staTele'], str2int(EveryDat['arrive_time']), group =1)
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