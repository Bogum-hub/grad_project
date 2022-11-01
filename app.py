import json
from flask import Flask, request, session, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from drug import transform_image, get_pred
import MySQLdb.cursors
import operator

app = Flask(__name__)
CORS(app)

app.secret_key = 'xxxx'

app.config['MYSQL_HOST'] = 'dont-drug-out.cwvau6dpzkxj.ap-northeast-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'mydb'
app.config['JSON_AS_ASCII'] = False

mysql = MySQL(app)
#登入
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
            return jsonify({'status':'Login successfully', 'message': 'hello'+ str(session['id']) })
        else:
            #incorrect account / password
            return jsonify({'status':'Account not exists!'})
    return jsonify({'status':'Lack of info'})
#登出
@app.route('/logout', methods =['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('id', None)
        return jsonify({'Result':'Logout sucessfully'})
#註冊
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
#查詢藥物
@app.route('/search_drug', methods =['GET', 'POST'])
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
#新增用藥時程
@app.route('/create_schedule', methods =['GET', 'POST']) 
def create():
    if request.method == 'POST' and 'drug' in request.json and 'startDate' in request.json and 'endDate' in request.json and 'duration' in request.json and 'daily' in request.json and 'hint' in request.json and 'bag' in request.json:
        
        drug_temp = request.json['drug'] 
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('select drugId from drug where chName=%s or enName=%s', (drug_temp, drug_temp))
        drug = cursor1.fetchone()
        if drug:
            scheduleDrugId = drug['drugId']#先抓出使用者所輸入的藥品名稱
            mid = session['id']
            startDate = request.json['startDate'] #開始吃藥時間
            endDate = request.json['endDate'] #結束吃藥時間
            duration = request.json['duration'] #間隔時間
            daily = request.json['daily'] #每天幾點吃
            hint = request.json['hint'] #定時提醒
            bag = request.json['bag'] #藥袋
            cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor2.execute('insert into schedule(scheduleMid, scheduleDrugId, startDate, endDate, duration, daily, isHint, bag) values (%s, %s, %s, %s, %s, %s, %s, %s)', (mid, scheduleDrugId, startDate, endDate, duration, daily, hint, bag, ))
            mysql.connection.commit()
            return jsonify({'Result':' Schedule create successfully!'})
        else:
            return jsonify({'Result':'Drug not exist!'})
    else:
        return jsonify({'Result': 'error!'})
#查詢用藥時程
@app.route('/search_schedule', methods =['GET', 'POST']) 
def schedule():
    if request.method =='POST' and 'date' in request.json:
        
        mid = session['id']
        date = request.json['date']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select sId, startdate, daily, bag, ishint, chname, enName from schedule, drug where startdate = %s and scheduleMid = %s and drug.drugId = scheduleDrugId' , (date, mid, ))
        result = list(cursor.fetchall())

        return json.dumps(result, indent=4, sort_keys=True, default=str, ensure_ascii=False).encode('utf8')
    else:
        return jsonify({"Result":'Wrong Request'})

#刪除用藥時程
@app.route('/delete_schedule', methods=['POST','GET'])
def schedule_delete():
    if request.method == 'POST' and 'sid_list' in request.json:
        
        a = request.json['sid_list']

        for i in range(len(a)):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("DELETE FROM schedule WHERE sid = %s" % ( a[i]))
            mysql.connection.commit()
            cursor.close()    
        return jsonify({'Result':'Delete Successfully'})
        

#拍攝藥品辨識
@app.route('/pred', methods=['POST','GET'])
def pred():
    if request.method == 'POST':
        file = request.files.get('file')
        img_byte = file.read()
        tensor = transform_image(img_byte)
        result = get_pred(tensor)
        drug = {}

        for i in range(5):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('select * from drug where drug_permit_license = %s', (result[0][i],))
            temp =  cursor.fetchone()
            drug[temp['chName']] = result[1][i]
            sorted_drug = sorted(drug.items(), key=operator.itemgetter(1), reverse=True)
        return jsonify(sorted_drug)
    else:
        return jsonify({'Result':'Wrong request'})
#交互作用
@app.route('/interaction', methods= ['GET', 'POST'])
def interaction():
    if request.method == 'POST' and 'drugA' in request.json and 'drugB' in request.json:
        drugA = request.json['drugA']
        drugB = request.json['drugB']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query =  """
        SELECT drugA.drug_bank_ingred AS drugA_main, drugB.drug_bank_ingred AS drugB_main 
        FROM ingredient AS drugA CROSS JOIN ingredient AS drugB
        WHERE drugA.ingre_drug_permit_license = %s AND drugA.drug_bank_ingred <>'NA' AND drugB.ingre_drug_permit_license= %s AND drugB.drug_bank_ingred<>'NA' AND drugA.drug_bank_ingred
        IN (SELECT ingreA 
            FROM interaction
            WHERE (ingreA = drugA.drug_bank_ingred AND ingreB = drugB.drug_bank_ingred));
        """
        cursor.execute(query, (drugA , drugB))
        result = list(cursor.fetchall())
        if result:
            return json.dumps(result)
        else:
            return jsonify({'Result':'no interaction!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)