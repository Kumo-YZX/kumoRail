#--------------------------------------------------------------------------------#
# File:main.py
# Author:Kumo
# Last edit time(Y-m-d):2018-03-29
# Description:The main program of flask server. You can run this script directly 
#             to test the service. 
#--------------------------------------------------------------------------------#

from flask import Flask, request
from encrypt.WXBizMsgCrypt import WXBizMsgCrypt
from wx import reply2, receive
from dialogue import dialogue
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.appSecretyKey

#url for home page
@app.route('/')
def page():
    return '<h1>Home page</h1>'

#url for WeChat bot application
@app.route('/wx', methods=['GET', 'POST'])
def handle():
# usability veryfication by WeChat
    if request.method == 'GET': 
        try:
            sign = request.args.get('signature')
            stamp = request.args.get('timestamp')
            nonce = request.args.get('nonce')
            echo = request.args.get('echostr')
            token = config.token

            list = [token, stamp, nonce]
            list.sort()
            import hashlib
            sha1 = hashlib.sha1()
            map(sha1.update, list)
            hashCode = sha1.hexdigest()
            print 'hashCode, signature:' + hashCode, sign
            if hashCode == sign:
                return echo
            else:
                return 'verify failed'
        except Exception, Argment:
            return Argment
# process the query and return replies
    elif request.method == 'POST':
        try:
            token = config.token
            encodingkey = config.encodingkey
            appid = config.appid
            decryptObj = WXBizMsgCrypt(token, encodingkey, appid)
            stamp = request.args.get('timestamp')
            nonce = request.args.get('nonce')
            msgSign = request.args.get('msg_signature')
            decStatus, wxData = decryptObj.DecryptMsg(request.data, msgSign, stamp, nonce)
            if decStatus:
                return 'Decrypt fail:' + str(decStatus)
            print 'wxData:', wxData
            recData = receive.parse_xml(wxData)
            if isinstance(recData, receive.Msg) and recData.MsgType == 'text':
                toUser = recData.FromUserName
                fromUser = recData.ToUserName
                word = recData.Content
                content = dialogue(toUser, word)
                encryptObj = WXBizMsgCrypt(token, encodingkey, appid)
                encStatus, replyData = encryptObj.EncryptMsg(reply2.TextMsg(toUser, fromUser, content), nonce, stamp)
                if encStatus:
                    return 'Encrypt fail:' + str(encStatus)
                return replyData
            else:
                print 'wrong format'
                return '<>'
        except Exception, Argment:
            return Argment

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=8098)
