import datetime
from email import message
from lib2to3.pgen2 import token
import os
import json
import requests
import sqlite3
import csv
from click import confirm
import pathlib
from flask import Flask, redirect, render_template, request, abort, url_for, jsonify
from config import *

UPLOAD_FOLDER = './files/guard'
ALLOWED_EXTENSIONS = {'csv, xls, xlsx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# line bot api


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

# get bot data


def get_db(message, table_name):
    conn = sqlite3.connect('telephone.db')
    c = conn.cursor()

    w_list = message.split()

    if w_list[0] == 'ค้นหา':
        try:
            sql = "SELECT * FROM {} WHERE name like '%{}%'".format(
                table_name, w_list[1])
            c.execute(sql)
            data = c.fetchall()
            if data:
                return data
            else:
                sql = "SELECT * FROM {} WHERE place like '%{}%' OR position like '%{}%'" .format(
                    table_name, w_list[1], w_list[1])
                c.execute(sql)
                data = c.fetchall()
                return data
        except Exception as e:
            print(e)
            data = []
            return data
        finally:
            conn.close()

    elif w_list[0] == 'เวร':
        try:
            sql = "SELECT * FROM {} WHERE name like '%{}%'".format(
                'guard', w_list[1])
            c.execute(sql)
            data = c.fetchall()
            if data:
                return data
            else:
                sql = "SELECT * FROM {} WHERE place like '%{}%' OR position like '%{}%'" .format(
                    'guard', w_list[1], w_list[1])
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

# line notify api


def notify(date, checker, confirm, missing):
    url = 'https://notify-api.line.me/api/notify'
    token = 'Egp2Tu5mtFIQInJS6LvBTp3CUvSy9V9mdUXFID2WSIU'

    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer {}".format(token)
    }

    message = 'เวรรักษาการณ์' + '\n' + 'วันที่: ' + date + '\n' + 'ผู้ตรวจ: ' + \
        checker + '\n' + 'ยืนยัน: ' + \
        str(confirm) + '\n' + 'ขาด: ' + str(missing)

    requests.post(url, data={"message": message}, headers=headers)


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
                d_str += 'หน่วยงาน : {}\nเบอร์โทร ทบ : {}\nสส.ทหาร: {}\nองค์การ : {}\nสายตรง : {}\n'.format(
                    d[0], d[1], d[2], d[3], d[4]) + '\n' + '-'*23 + '\n'
            ReplyMessage(Reply_token, d_str[:5000],
                         channel_access_token['rta'])
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
                d_str += 'ชื่อ : {}\n'.format(d[0]) + 'ตำแหน่ง : {}\n'.format(
                    d[1]) + 'หน่วย : {}\n'.format(d[2]) + 'เบอร์โทร : {}\n'.format(d[3]) + '-'*23 + '\n'

            ReplyMessage(Reply_token, d_str[:5000],
                         channel_access_token['mtb29'])
        return request.json, 200
    elif request.method == 'GET':
        d_str = 'It is GET method'
        return d_str, 200
    else:
        abort(400)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/form_upload', methods=['POST', 'GET'])
def form_upload():
    if request.method == 'GET':
        return render_template('form_upload.html')
    if request.method == 'POST':
        checker = request.form['checker']
        file = request.files['file']
        pathlib.Path(app.config['UPLOAD_FOLDER']).mkdir(
            parents=True, exist_ok=True)
        file.filename = "{}-{}.csv".format(
            checker, datetime.datetime.now().strftime("%Y_%m_%d_%H-%M-%S"))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        conn = sqlite3.connect('telephone.db')
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS {}".format('guard'))
        c.execute(
            "Create TABLE IF NOT EXISTS {} (name TEXT, place TEXT, position TEXT, telephone TEXT, note TEXT)".format('guard'))

        with open(os.path.join(app.config['UPLOAD_FOLDER'], file.filename), 'r') as f:
            csv_data = csv.DictReader(f)
            csv_to_db = [(i['name'], i['position'], i['place'],
                          i['phone'], i['note']) for i in csv_data]

        c.executemany("INSERT INTO guard VALUES (?, ?, ?, ?, ?)", csv_to_db)
        conn.commit()
        data = c.execute("SELECT * FROM guard")
        # conn.close()

        # return render_template('result.html', checker=checker, data=data, filename=file.filename)
        return redirect(url_for('result', checker=checker))

        # data = get_db(message)
        # d_str = ''
        # if data == 'Pass':
        #     pass
        # elif not data:
        #     print('Not found : {}'.format(message))
        #     d_str = 'ไม่พบ : {}'.format(message)
        #     return d_str, 200
        # else:
        #     for d in data:
        #         d_str += 'ชื่อ : {}\n'.format(d[0]) + 'ตำแหน่ง : {}\n'.format(d[1]) + 'หน่วย : {}\n'.format(d[2]) + 'เบอร์โทร : {}\n'.format(d[3]) +'-'*23 + '\n'
        #     # return d_str, 200
        #     return render_template('result.html', data=data)


@app.route('/result')
def result():
    # filename = request.args.get('filename')
    checker = request.args.get('checker')
    conn = sqlite3.connect('telephone.db')
    c = conn.cursor()
    data = c.execute("SELECT * FROM guard")
    missing = c.execute(
        "SELECT COUNT(*) FROM guard WHERE note != '{}'".format('ยืนยัน')).fetchone()[0]
    confirm = c.execute(
        "SELECT COUNT(*) FROM guard WHERE note = '{}'".format('ยืนยัน')).fetchone()[0]
    # conn.close()
    data = c.execute("SELECT * FROM guard")
    date = datetime.datetime.now().strftime("%d-%m-%Y เวลา %H:%M:%S")
    notify(date, checker, confirm, missing)
    return render_template('result.html', checker=checker, data=data, date=date, missing=missing, confirm=confirm)

# @app.route('/uploaded', methods=['POST', 'GET'])
# def uploaded():
#     if request.method == 'POST':
#         message = request.form['message']
#         data = get_db(message, 'mtb29_telephone')
#         d_str = ''
#         if data == 'Pass':
#             pass
#         elif not data:
#             print('Not found : {}'.format(message))
#             d_str = 'ไม่พบ : {}'.format(message)
#             return d_str, 200
#         else:
#             for d in data:
#                 d_str += 'ชื่อ : {}\n'.format(d[0]) + 'ตำแหน่ง : {}\n'.format(d[1]) + 'หน่วย : {}\n'.format(d[2]) + 'เบอร์โทร : {}\n'.format(d[3]) +'-'*23 + '\n'
#             return d_str, 200
#     return render_template('form_test.html')


if (__name__ == '__main__'):
    app.run(debug=True, host='127.0.0.1', port=5000)
