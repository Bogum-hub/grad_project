import json
from datetime import *
from flask import Flask, request, session, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from drug import transform_image, get_pred
import MySQLdb.cursors
import operator

app = Flask(__name__)
CORS(app)

app.secret_key = 'xxxx'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
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
    if request.method == 'POST' and 'username' in request.json and 'account' in request.json and 'password' in request.json and 'bag' in request.json:
        username = request.json['username']
        account = request.json['account']
        password = request.json['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('Select * FROM member WHERE mAccount = %s', (account, ))
        account_check = cursor.fetchone()
        if account_check:
            return jsonify({'Result':'Account already exist!'})
        elif not username or not password:
            return jsonify({'Result':'Please fill out the form!'})
        else:
            cursor.execute('Insert into member(name, maccount, mpassword) values(%s, %s, %s)', (username, request.json['account'], password,))
            mysql.connection.commit()

            cursor.execute('select mId from member where maccount = %s;', (request.json['account'], ))
            result = cursor.fetchone()
            mid = result['mId'] #記錄使用者id

            #新增DEFAULT藥袋時長
            query = """
            insert into bag(bagMid, bagName, startDate, endDate) values(%s, %s, %s, %s);
            """
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query, (mid, '藥袋A', request.json['bag'][0]['藥袋A'][0]['startDate'], request.json['bag'][0]['藥袋A'][1]['endDate'],))
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query, (mid, '藥袋B', request.json['bag'][1]['藥袋B'][0]['startDate'], request.json['bag'][1]['藥袋B'][1]['endDate'],))
            mysql.connection.commit()

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query, (mid, '藥袋C', request.json['bag'][2]['藥袋C'][0]['startDate'], request.json['bag'][2]['藥袋C'][1]['endDate'],))
            mysql.connection.commit()


            #有輸入藥品過敏資訊
            if request.json['allergy'] != []:
                #先找出藥品id
                for i in range(len(request.json['allergy'])):
                    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                    query = """
                    select drugId from drug where enName = %s or chName = %s;
                    """
                    cursor.execute(query, (request.json['allergy'][i]['drug'], request.json['allergy'][i]['drug'],))
                    result = cursor.fetchone()
                    drugid = result['drugId']
                    #找出id後新增至allergy table
                    query2 = """
                    insert into allergy (allergyMid, allergyDrugId) values (%s, %s);
                    """
                    cursor.execute(query2, (mid, drugid, ))
                    mysql.connection.commit()
                return jsonify({'Result': '新增帳號&過敏資訊成功'})
            else:
                return jsonify({'Result': '新增帳號成功'})
    else:   
        return jsonify({'Result':'sign up failed'})

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

        query = """
        update bag set startDate = %s, endDate = %s where bagMid = %s and bagName = %s
        """
        cursor.execute(query,(request.json['bag'][0]['藥袋A'][0]['startDate'], request.json['bag'][0]['藥袋A'][1]['endDate'], mid, '藥袋A'))
        mysql.connection.commit()

        cursor.execute(query,(request.json['bag'][1]['藥袋B'][0]['startDate'], request.json['bag'][1]['藥袋B'][1]['endDate'], mid, '藥袋B'))
        mysql.connection.commit()

        cursor.execute(query,(request.json['bag'][2]['藥袋C'][0]['startDate'], request.json['bag'][2]['藥袋C'][1]['endDate'], mid, '藥袋C'))
        mysql.connection.commit()

        if 'allergy'in request.json:
        #先刪除過敏藥物
            query2 = """
            delete from allergy where allergyMid = %s
            """
            cursor.execute(query2,(mid,))
            mysql.connection.commit()
            #再插入過敏藥物
            for i in range(len(request.json['allergy'])):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                query = """
                select drugId from drug where enName = %s or chName = %s;
                """
                cursor.execute(query, (request.json['allergy'][i]['drug'], request.json['allergy'][i]['drug'],))
                result = cursor.fetchone()
                drugid = result['drugId']
                #找出id後新增至allergy table
                query2 = """
                insert into allergy (allergyMid, allergyDrugId) values (%s, %s);
                """
                cursor.execute(query2, (mid, drugid, ))
                mysql.connection.commit()
        return jsonify({'Result':'update successfully!'})
    else:
        return jsonify({'Result':'Something went wrong'})

#取得會員資料
@app.route('/member_data')
def member_data():
    if request.method == "GET":

        id = session['id']

        ##################會員基本資料#####################
        query = """
        select mId, name, mAccount, mPassword
        from member
        where mid = %s ;
        """
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query,(id, ))
        result = cursor.fetchall()
        result = {'data':result}

        ###################會員藥袋資料###################

        query = """
        select bagName, startDate, endDate
        from member, bag
        where mid = %s and bagMid = mid
        """
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query,(id, ))
        result2 = cursor.fetchall()
        result2 = {'bag':result2}

        ###################會員過敏資料###################

        query = """
        select chName, enName
        from allergy, drug
        where drugId = allergyDrugId and allergyMid = %s;
        """
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query,(id, ))
        result1 = cursor.fetchall()
        if not result1:
            result1 = {'allergy':'NA'}
        else:
            result1 = {'allergy':result1}

        d = result.copy()
        d.update(result1)
        d.update(result2)
        
        return json.dumps(d, indent=4, sort_keys=True, default=str, ensure_ascii=False).encode('utf8')


#搜尋藥品字串比對
@app.route('/search', methods =['GET', 'POST'])
def search():
    if request.method == 'POST' and 'drug' in request.json:

        drug = str(request.json['drug'])
        if (drug.rstrip() == ''):
            return jsonify({'Result':'NA'})

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
            return jsonify({'Result':'NA'})

    else:
        return jsonify({'Result':'something wrong'})
        
#查詢藥物
@app.route('/search_drug', methods =['GET', 'POST'])
def drug():
    result = ''
    if request.method == 'POST' and 'drug' in request.json:
        mid = session['id']
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
    if request.method == 'POST' and 'drug' in request.json  and 'duration' in request.json and 'daily' in request.json and 'hint' in request.json  and 'scheduleBagId' in request.json:

        drug_temp = request.json['drug'] 
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('select drugId from drug where chName=%s or enName=%s', (drug_temp, drug_temp))
        drug = cursor1.fetchone()
        if drug:
            mid = session['id'] 
            scheduleDrugId = drug['drugId']#先抓出使用者所輸入的藥品名稱
            bagID = request.json['scheduleBagId'] #藥袋ID
            duration = request.json['duration'] #間隔時間
            daily = request.json['daily'] #每天幾點吃
            hint = request.json['hint'] #定時提醒
            cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor2.execute('insert into schedule(scheduleMid, scheduleDrugId, scheduleBagId, daily, duration, isHint) values (%s, %s, %s, %s, %s, %s)', (mid, scheduleDrugId, bagID, daily, duration,  hint,  ))
            mysql.connection.commit()
            return jsonify({'Result':' Schedule create successfully!'})
        else:
            return jsonify({'Result':'Drug do not exist!'})

    if request.method == 'PUT' and 'sid' in request.json and 'drug' in request.json  and 'duration' in request.json and 'daily' in request.json and 'hint' in request.json  and 'scheduleBagId' in request.json:
            
        drug_temp = request.json['drug'] 
        cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor1.execute('select drugId from drug where chName=%s or enName=%s', (drug_temp, drug_temp))
        drug = cursor1.fetchone()
        
        if drug:
            sid = request.json.get('sid')
            scheduleDrugId = drug['drugId']#先抓出使用者所輸入的藥品名稱
            bagID = request.json['scheduleBagId'] #藥袋ID
            duration = request.json['duration'] #間隔時間
            daily = request.json['daily'] #每天幾點吃
            hint = request.json['hint'] #定時提醒
            query = """
            UPDATE schedule set scheduledrugid = %s, scheduleBagId = %s, daily=%s, duration=%s, ishint=%s where sId = %s;
            """
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query, (scheduleDrugId, bagID, daily, duration, hint, sid, ))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'Result': 'update successfully!'})
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
        select sId, startdate, enddate, daily, ishint, chname, enName, duration, bagName
        from schedule, drug, bag
        where startdate <= %s and enddate>= %s and scheduleMid = %s and drug.drugId = scheduleDrugId and scheduleBagId = bid order by daily
        """
        cursor.execute(query , (date, date, mid, ))
        result = list(cursor.fetchall())
        if result:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            for i in range(len(result)):
                interval = result[i]['startdate'] - date
                if (interval.days / (result[i]['duration'])) % 1 != 0:
                    del result[i]
            if result == []:
                return jsonify({'Result':'No record!'})
            return json.dumps(result, indent=4, sort_keys=True, default=str, ensure_ascii=False).encode('utf8')
        else:
            return jsonify({'Result':'No record!'})
    
    elif request.method =='GET':
        mid = session['id']
        query = """
        select * from schedule where scheduleMid = %s
        """
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query , (mid, ))
        result = list(cursor.fetchall())
        if result:
            return json.dumps(result, indent=4, sort_keys=True, default=str, ensure_ascii=False).encode('utf8')
        else:
            return jsonify({'Result':'No record!'})

#查詢用藥時程
@app.route('/search_schedule_mon', methods =['GET', 'POST']) 
def schedule_mon():
    if request.method =='POST' and 'date' in request.json:
        mid = session['id']
        date = request.json['date']
        year = request.json['year']
        mon = request.json['mon']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
        select bagName, startdate, enddate, duration, scheduleMid, extract(day from startdate) as start, extract(day from enddate) as end, extract(day from startdate) as start_end,
        (	case
            when extract(YEAR_month from enddate) = extract(YEAR_month from startdate) then 'start_end'
            when extract(YEAR_month from startdate) = %s then 'start'
            when extract(YEAR_month from enddate) = %s then 'end'
            else 'yes'
            END) AS if_all_month
        from schedule, bag 
        where scheduleMid=%s
        HAVING extract(YEAR_month from startdate) <= %s AND %s <= extract(YEAR_month from enddate) 
        """
        cursor.execute(query, (date, date, mid, date, date,))
        result = cursor.fetchall()
        c = []

        for i in range(len(result)):
            a = {}
            a['bag'] = result[i]['bagName']
            a['date'] = []
            a['month'] = mon
            b = []

            #起始月=結束月
            if(result[i]['if_all_month'] == 'start_end'):
                a['status'] = 'in a month'
                for i in range(result[i]['start'], result[i]['end']+1, result[i]['duration']):
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
                for i in range(result[i]['start'], treshold+1, result[i]['duration']):
                    b.append(i)
                a['date'] = b

            #結束月
            elif(result[i]['if_all_month'] == 'end'):
                a['status'] = 'end month of schedule'
                for i in range(result[i]['end'], 1, -result[i]['duration']):
                    b.append(i)
                a['date'] = sorted(b)
                
            #之間
            else:
                a['status'] = 'all'
                day = 1

                while True:
                    starter = str(year) + '-' + str(mon)+ '-0' + str(day)
                    starter = datetime.strptime(starter, '%Y-%m-%d').date()
                    interval = starter - result[i]['startdate'] 
                    if (interval.days / (result[i]['duration'])) % 1 == 0:
                        break
                    else:
                        day = day + 1

                match mon:
                    case 1|3|5|7|8|10|12:
                        end = 31
                    case 4|6|9|11:
                        end = 30
                    case 2:
                        end = 28
                #閏年
                if (mon == 2) and (year % 4 == 0) and (year % 100 !=0) or (year % 400) == 0:
                    end = 29

                for i in range(day, end+1, result[i]['duration']):
                    b.append(i)
                a['date'] = b
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
        if result:
            for i in range(5):
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('select * from drug where drug_permit_license = %s ', (result[0][i],))
                temp = cursor.fetchone()
                cursor.execute('select * from DrugImg where license = %s;', (result[0][i],))
                temp2 = cursor.fetchone()
                if temp2:
                    drug[temp['chName']] = (result[1][i], temp2['link'])
                else:
                    pass
            
            sorted_drug = sorted(drug.items(), key=operator.itemgetter(1), reverse=True)
            return jsonify(sorted_drug)
        else:
            return jsonify({"result":"drug not exists!"})
        

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

#判斷日期
def isValidateDATE(datestr):
    try: 
        date.fromisoformat(datestr)
    except:
        return False
    else:
        return True
#判斷時間
def isValidateTime(timestr):
    try: 
        datetime.strptime(timestr, "%H:%M")
    except:
        return False
    else:
        return True

# #daily格式錯誤
# if(isValidateTime(request.json['daily']) == False):
#     return jsonify({'Result':'Wrong daily format！'})
# #startDate or endDate 格式錯誤
# elif(isValidateDATE(request.json['startDate']) == False or isValidateDATE(request.json['endDate'])== False):
#     return jsonify({'Result':'Wrong Date format！'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)