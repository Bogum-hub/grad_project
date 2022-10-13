from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from drug import transform_image, get_pred
import MySQLdb.cursors

app = Flask(__name__)
CORS(app)

app.secret_key = 'xxxx'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'mydb'
app.config['JSON_AS_ASCII'] = False

mysql = MySQL(app)

@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'POST' and 'account' in request.json and 'password' in request.json:
        account = request.json['account']
        password = request.json['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM member WHERE maccount = % s AND mpassword = % s', (account, password, ))
        account = cursor.fetchone()
        if account:
            session['id'] = account['mId']
            return jsonify({'status':'Login successfully'})
        else:
            #incorrect account / password
            return jsonify({'status':'Account not exists!'})
    return jsonify({'status':'Lack of info'})

@app.route('/logout')
def logout():
    session.pop('id', None)
    return jsonify({'Result':'Logout sucessfully'})

@app.route('/register', methods =['GET', 'POST'])
def register():
    if request.method == 'POST' and 'username' in request.form and 'account' in request.form and 'password' in request.form:
        username = request.form['username']
        account = request.form['account']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select * FROM member WHERE mAccount = %s', (account, ))
        account_check = cursor.fetchone()
        if account_check:
            return jsonify({'result':'Account already exist!'})
        elif not username or not password:
            return jsonify({'result':'Please fill out the form!'})
        else:
            cursor.execute('Insert into member(name, maccount, mpassword) values(%s, %s, %s)', (username, request.form['account'], password,))
            mysql.connection.commit()
            return jsonify({'result':'sign up successfully'})
    else:
        return jsonify({'result':'sign up failed'})
        
@app.route('/search_drug', methods =['GET', 'POST']) #查詢藥物
def drug():
    result = ''
    if request.method == 'POST' and 'drug' in request.json:
        drug = request.json['drug']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM drug WHERE enName = % s or chName = %s', (drug, drug,))
        result = cursor.fetchone()
        if result:
            return jsonify({'Result': 'true', '中文名字': result['chName'], '英文名字':result['enName'], '劑型': result['type'], '形狀': result['shape'], '顏色': result['color'], '適應症' : result['indication']})
        else:
            return jsonify({'Result': 'false'})
    return jsonify({'Result': 'Wrong request'})

@app.route('/search_schedule', methods =['GET', 'POST']) #查詢時程
def schedule():
    result=''
    if request.method =='POST':
        mId = session.get(id)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select drug_permit_license ,chName, startDate, endDate from schedule as s, drug as d, member as m where s.scheduleMid = % s AND d.drugId=s.scheduleDrugId AND m.mId = s.scheduleMid;', (mId, ))
        result = cursor.fetchall()
        if result:
            return jsonify({"Result":result})
        else:
            return jsonify({"Result":'Empty'})
    else:
        return jsonify({"Result":'Wrong Request'})

@app.route('/create_schedule', methods =['GET', 'POST']) #寫入資料表
def create():
    if request.method == 'POST' and 'drug' in request.json and 'timing' in request.json and 'period' in request.json and 'hint' in request.json:
        
        drug_temp = request.json['drug'] 
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('select drugId from drug where chName=%s', (drug_temp, ))
        drug = cursor.fetchone()
        scheduleDrugId = drug['drugId']#先抓出使用者所輸入的藥品名稱

        mid = session.get(id)
        timing = request.json['timing'] #用藥時間 睡前/三餐/其他
        period = request.json['period'] #用藥時長 兩個月/三個月...
        hint = request.json['hint'] #定時提醒
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('insert into schedule (scheduleMid, scheduleDrugId, timing, period, isHint) values (%s, %s, %s, %s, %s)', (mid, scheduleDrugId, timing, period, hint, ))
        mysql.connection.commit()
        return jsonify({'Result':'Creat successfully!'})
    else:
        return jsonify({'Result':'Something went wrong'})
        
#拍攝藥品辨識
@app.route('/pred', methods=['POST','GET'])
def pred():
    if request.method == 'POST':
        file = request.files.get('file')
        img_byte = file.read()
        tensor = transform_image(img_byte)
        result = get_pred(tensor)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from drug where drug_permit_license = %s', (result,))
        drug =  cursor.fetchone()
        return jsonify({'中文名字': drug['chName'], '英文名字':drug['enName'], '形狀': drug['shape'], '顏色': drug['color'], '適應症' : drug['indication'], '劑型' : drug['type']})
    else:
        return jsonify({'Result':'Wrong request'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    
