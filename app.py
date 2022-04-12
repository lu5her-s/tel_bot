from email import message
import os, json, requests, sqlite3
from flask import Flask, request, abort, jsonify
from config import *

app = Flask(__name__)


def ReplyMessage(Reply_token, TextMessage, Line_Access_Token):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'
    Authorization = 'Bearer {}'.format(Line_Access_Token)
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': Authorization
    }
    data = json.dumps({
        "replyToken": Reply_token,
        "messages": [{
            "type": "text",
            "text": TextMessage
        }]
    })
    r = requests.post(LINE_API, headers=headers, data=data)
    return r.json()

def get_db(message, table_name):
    conn = sqlite3.connect('telephone.db')
    c = conn.cursor()
    
    w_list = message.split()
    
    if w_list[0] == 'ค้นหา':
        try:
            sql = "SELECT * FROM {} WHERE name like '%{}%'".format(table_name, w_list[1])
            c.execute(sql)
            data = c.fetchall()
            if data:
                return data
            else:
                sql = "SELECT * FROM {} WHERE place like '%{}%' OR position like '%{}%'" .format(table_name, w_list[1], w_list[1])
                c.execute(sql)
                data = c.fetchall()
                return data
        except Exception as e:
            print(e)
            data = []
            return data
        finally:
            conn.close()
    else:
        data = 'Pass'
        return data
        
@app.route('/')
def index():
    message = "ค้น บก.ทบ."
    table_name = 'rta_telephone'
    data = get_db(message, table_name)
    d_str = ''
    if data == 'Pass':
        # print('Pass')
        # d_str = 'ค้นหาผิดพลาด'
        pass
    elif not data:
        print('Not found')
        d_str = 'Not Found'
    else:
        print(data)
        d_str = ' '.join([str(elem) for elem in data])
    return d_str

@app.route('/rta', methods=['POST', 'GET'])
def rta():
    if request.method == 'POST':
        payload = request.json
        
        Reply_token = payload['events'][0]['replyToken']
        print(Reply_token)
        message = payload['events'][0]['message']['text']
        m_list = message.split()
        # print(message)
        data = get_db(message, 'rta_telephone')
        d_str = ''
        if data == 'Pass':
            print('Pass')
            # pass
        elif not data:
            print('Not found : {}'.format(m_list[1]))
            d_str = 'ไม่พบ : {}'.format(m_list[1])
            ReplyMessage(Reply_token, d_str, channel_access_token['rta'])
        else:
            print(data)
            # d_str = ' '.join([str(elem) for elem in data])
            for d in data:
                d_str += 'หน่วยงาน : {}\nเบอร์โทร ทบ : {}\nสส.ทหาร: {}\nองค์การ : {}\nสายตรง : {}\n'.format(d[1], d[2], d[3], d[4], d[5]) + '\n' + '-'*23 + '\n'
            ReplyMessage(Reply_token, d_str[:5000], channel_access_token['rta'])
        return request.json, 200
    
    elif request.method == 'GET':
        d_str = 'It is GET method'
        return d_str, 200
    else:
        abort(400)

@app.route('/mtb29', methods=['POST', 'GET'])
def mtb29():
    if request.method == 'POST':
        payload = request.json
        
        Reply_token = payload['events'][0]['replyToken']
        print(Reply_token)
        message = payload['events'][0]['message']['text']
        m_list = message.split()
        data = get_db(message, 'mtb29_telephone')
        d_str = ''
        if data == 'Pass':
            print('Pass')
            # pass
        elif not data:
            print('Not found : {}'.format(m_list[1]))
            d_str = 'ไม่พบ : {}'.format(m_list[1])
            ReplyMessage(Reply_token, d_str, channel_access_token['mtb29'])
        else:
            print(data)
            for d in data:
                d_str += 'ชื่อ : {}\n'.format(d[0]) + 'ตำแหน่ง : {}\n'.format(d[1]) + 'หน่วย : {}\n'.format(d[2]) + 'เบอร์โทร : {}\n'.format(d[3]) +'-'*23 + '\n'
            ReplyMessage(Reply_token, d_str[:5000], channel_access_token['mtb29'])
        return request.json, 200
    elif request.method == 'GET':
        d_str = 'It is GET method'
        return d_str, 200
    else:
        abort(400)
            

if (__name__ == '__main__'):
    app.run(debug=True, host='127.0.0.1', port=5000)
    
    
