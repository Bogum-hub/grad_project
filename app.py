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

app.config['MYSQL_HOST'] = 'drug-back-1124.cwvau6dpzkxj.ap-northeast-1.rds.amazonaws.com'
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
            #有輸入藥品過敏資訊
            if 'allergy' in request.form:
                #先找出使用者id&藥品id
                cursor.execute('select mId from member where maccount = %s;', (request.form['account'], ))
                result = cursor.fetchone()
                mid = result['mId']
                allergy = request.form['allergy']
                query = """
                select drugId from drug where enName = %s or chName = %s;
                """
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(query, (allergy, allergy,))
                result = cursor.fetchone()
                drugid = result['drugId']
                #找出id後新增至allergy table
                query2 = """
                insert into allergy (allergyMid, allergyDrugId) values (%s, %s);
                """
                cursor.execute(query2, (mid, drugid, ))
                mysql.connection.commit()
                return jsonify({'result': '新增帳號&過敏資訊成功'})
            else:
                return jsonify({'result': '新增帳號成功'})
    else:   
        return jsonify({'result':'sign up failed'})

#更新會員資料
@app.route('/member_update', methods =['GET', 'POST'])
def member_update():
    if request.method == 'POST' and 'name' in request.json and 'password' in request.json:
        mid = session['id']
        name = request.json['name']
        password = request.json['password']
        query = """
        update member set name = %s , mPassword = %s where mId = %s;
        """
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query,(name, password, mid))
        mysql.connection.commit()
        return jsonify({'Result':'update successfully!'})
    else:
        return jsonify({'Result':'Something went wrong'})

#取得會員資料
@app.route('/member_data')
def member_data():
    if request.method == "GET":
        id = session['id']
        query = """
        select * from member where mid = %s;
        """
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query,(id,))
        result = cursor.fetchone()
        if result:
            return jsonify({'Result': result})
        else:
            return jsonify({'Result': 'no'})
    else:
        return jsonify({'Result': 'Wrong request'})

#搜尋藥品字串比對
@app.route('/search', methods =['GET', 'POST'])
def search():
    if request.method == 'POST' and 'drug' in request.json:

        drug = str(request.json['drug'])
        if (drug.rstrip() == ''):
            return jsonify({'result':'NA'})

        drug_EN = str(request.json['drug'] + "%")
        drug_CH = str("%" + request.json['drug'] + "%")
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
        SELECT *
        FROM drug 
        GROUP BY enName
        having enName LIKE %s OR chName LIKE %s limit 10
        """
        cursor.execute(query, (drug_EN, drug_CH, ))
        result = list(cursor.fetchall())
        temp = []
        
        if result:
            for i in range(len(result)):
                if(drug.replace(" ","").encode('utf-8').isalpha() == True):
                    temp.append(result[i]['enName'])
                else:
                    temp.append(result[i]['chName'])
            return jsonify(temp)
        else:
            return jsonify({'result':'NA'})

    else:
        return jsonify({'result':'something wrong'})
        
#查詢藥物
@app.route('/search_drug', methods =['GET', 'POST'])
def drug():
    result = ''
    if request.method == 'POST' and 'drug' in request.json:
        mid = 31
        drug = request.json['drug']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query1 = """
        select chName, enName
        from allergy, drug, member
        where allergyMid=%s and allergyMid = mid and chName = %s and allergyDrugId = drugid;
        """
        cursor.execute(query1, (mid, drug,))
        allergy = cursor.fetchone()
        if allergy != None:
            a = '是'
        else:
            a = '否'
        
        #照片存在的情況下
        query = """
        SELECT *
        FROM drug as d, DrugImg as img
        WHERE (enName = %s or chName = %s) and d.drug_permit_license = img.license
        """
        cursor.execute(query, (drug, drug,))
        result = cursor.fetchone()
        if result:
            return jsonify({'中文名字': result['chName'], '英文名字':result['enName'], '劑型': result['type'], '形狀': result['shape'], '顏色': result['color'], '適應症' : result['indication'], '照片':result['link'], '是否過敏':a})
        
        #照片不存在的情況下
        else:
            query = """
            SELECT *
            FROM drug as d, DrugImg as img
            WHERE enName = %s or chName = %s
            """
            cursor.execute(query, (drug, drug,))
            result = cursor.fetchone()
            if result:
                return jsonify({'中文名字': result['chName'], '英文名字':result['enName'], '劑型': result['type'], '形狀': result['shape'], '顏色': result['color'], '適應症' : result['indication'], '照片':'NA', '是否過敏':a})
            else:
                return jsonify({'Result': 'Drug does not exist!'})

    return jsonify({'Result': 'Wrong request'})

#新增用藥時程/編輯用藥時程
@app.route('/create_schedule', methods =['GET', 'POST', 'PUT']) 
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
            return jsonify({'Result':'Drug do not exist!'})

    if request.method == 'PUT' and 'sid' in request.json and 'drug' in request.json and 'startDate' in request.json and 'endDate' in request.json and 'duration' in request.json and 'daily' in request.json and 'hint' in request.json and 'bag' in request.json:
        
        drug_temp = request.json['drug'] 
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('select drugId from drug where chName=%s or enName=%s', (drug_temp, drug_temp))
        drug = cursor1.fetchone()
        
        if drug:
            sid = request.json.get('sid')
            scheduleDrugId = drug['drugId']#先抓出使用者所輸入的藥品名稱
            startDate = request.json['startDate'] #開始吃藥時間
            endDate = request.json['endDate'] #結束吃藥時間
            duration = request.json['duration'] #間隔時間
            daily = request.json['daily'] #每天幾點吃
            hint = request.json['hint'] #定時提醒
            bag = request.json['bag'] #藥袋
            query = """
            UPDATE schedule set scheduledrugid = %s, startDate=%s, enddate=%s, duration=%s, daily=%s, bag=%s, ishint=%s
            where sId = %s;
            """
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query, (scheduleDrugId, startDate, endDate, duration, daily, bag, hint, sid, ))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'result': 'update successfully!'})
    else:
        return jsonify({'Result': 'error!'})

#查詢用藥時程
@app.route('/search_schedule', methods =['GET', 'POST']) 
def schedule():
    if request.method =='POST' and 'date' in request.json:
        mid = session['id']
        date = request.json['date']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
        select sId, startdate, enddate, daily, bag, ishint, chname, enName, duration
        from schedule, drug 
        where startdate <= %s and enddate>= %s and scheduleMid = %s and drug.drugId = scheduleDrugId order by daily
        """
        cursor.execute(query , (date, date, mid, ))
        result = list(cursor.fetchall())
        if result:
            return json.dumps(result, indent=4, sort_keys=True, default=str, ensure_ascii=False).encode('utf8')
        else:
            return jsonify({'Result':'No record!'})
    else:
        return jsonify({"Result":'Wrong Request'})

#查詢用藥時程
@app.route('/search_schedule_mon', methods =['GET', 'POST']) 
def schedule_mon():
    if request.method =='POST' and 'date' in request.json:
        mid = session['id']
        date = request.json['date']
        mon = request.json['mon']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
        select bag, startdate, enddate, scheduleMid, extract(day from startdate) as start, extract(day from enddate) as end, extract(day from startdate) as start_end,
        (	case
            when extract(YEAR_month from enddate) = extract(YEAR_month from startdate) then 'start_end'
            when extract(YEAR_month from startdate) = %s then 'start'
            when extract(YEAR_month from enddate) = %s then 'end'
            else 'yes'
            END) AS if_all_month
        from schedule 
        where scheduleMid=%s
        GROUP BY bag
        HAVING extract(YEAR_month from startdate) <= %s AND %s <= extract(YEAR_month from enddate) 
        ORDER BY bag;
        """
        cursor.execute(query, (date, date, mid, date, date,))
        result = cursor.fetchall()
        c = []

        for i in range(len(result)):
            a = {}
            a['bag'] = result[i]['bag']
            a['date'] = []
            a['month'] = mon
            b = []

            #起始月=結束月
            if(result[i]['if_all_month'] == 'start_end'):
                a['status'] = 'in a month'
                for i in range(result[i]['start'], result[i]['end']+1):
                    b.append(i)
                a['date'] = b

            #起始月
            elif(result[i]['if_all_month'] == 'start'):
                a['status'] = 'start month of schedule'
                match mon:
                    case 1|3|5|7|8|10|12:
                        treshold = 31
                    case 4|6|9|11:
                        treshold = 30
                    case _:
                        treshold = 28
                for i in range(result[i]['start'], treshold+1):
                    b.append(i)
                a['date'] = b

            #結束月
            elif(result[i]['if_all_month'] == 'end'):
                a['status'] = 'end month of schedule'
                for i in range(result[i]['end']):
                    b.append(i+1)
                a['date'] = b
                
            #之間
            else:
                a['status'] = 'all'
                match mon:
                    case 1|3|5|7|8|10|12:
                        a['date'] = 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31
                    case 4|6|9|11:
                        a['date'] = 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30
                    case _:
                        a['date'] = 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28
            c.append(a)

        if result:
            return jsonify({'Result':c})
        else:
            return jsonify({'Result':'No record!'})

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
            cursor.execute('select * from drug where drug_permit_license = %s ', (result[0][i],))
            temp = cursor.fetchone()
            cursor.execute('select * from DrugImg where license = %s;', (result[0][i],))
            temp2 = cursor.fetchone()
            if temp2:
                drug[temp['chName']] = (result[1][i], temp2['link'])
            else:
                drug[temp['chName']] = (result[1][i], 'NA')
            
        sorted_drug = sorted(drug.items(), key=operator.itemgetter(1), reverse=True)
        return jsonify(sorted_drug)

#交互作用
@app.route('/interaction', methods= ['GET', 'POST'])
def interaction():
    if request.method == 'POST' and 'drugA' in request.json and 'drugB' in request.json:

        drugA = request.json['drugA']
        drugB = request.json['drugB']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select drug_permit_license from drug where chName = %s', (drugA,))
        drug1 = cursor.fetchone()
        cursor.execute('select drug_permit_license from drug where chName = %s', (drugB,))
        drug2 = cursor.fetchone()
        
        if drug1 != None and drug2 != None:
            query =  """
            SELECT ingreA, ingreB, description 
            FROM interaction 
            WHERE 
            ingreA IN (SELECT drug_bank_ingred FROM ingredient WHERE ingre_drug_permit_license= %s) AND 
            ingreB IN (SELECT drug_bank_ingred FROM ingredient WHERE ingre_drug_permit_license= %s);
            """
            cursor.execute(query, (drug1['drug_permit_license'] , drug2['drug_permit_license']))
            result = list(cursor.fetchall())
            if result:
                return json.dumps(result, indent=4, sort_keys=True, default=str, ensure_ascii=False).encode('utf8')
            else:
                return jsonify({'Result':"No interaction!"})
        elif drug1 == None and drug2 != None:
            return jsonify({'Result': drugA + " not exit!"})

        elif drug1 != None and drug2 == None:
            return jsonify({'Result': drugB +" not exit!"})
        else:
            return jsonify({'Result':drugA + " and " + drugB + "not exit!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)