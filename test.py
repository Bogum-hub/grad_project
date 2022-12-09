import requests

####################### 會員資料相關 ###########################
# resp = requests.post("http://127.0.0.1:5000/register", json={"username":'阿洪',"account":'111@gmail.com', "password":'123456', 'allergy':[{'drug':'綠油精'}, {'drug':'暈速寧片'}], 'bag':[{'藥袋A':[{'startDate':'2022-12-08'},{'endDate':'2022-12-09'}]}, {'藥袋B':[{'startDate':'2022-12-08'},{'endDate':'2022-12-10'}]}, {'藥袋C':[{'startDate':'2022-12-08'},{'endDate':'2022-12-11'}]}]})
# resp = requests.get("http://127.0.0.1:5000/member_data")
# resp = requests.post("http://127.0.0.1:5000/member_update", json={"name":'阿洪洪', "password":'12345', 'allergy':[], 'bag':[{'藥袋A':[{'startDate':'2022-12-08'},{'endDate':'2022-12-09'}]}, {'藥袋B':[{'startDate':'2022-12-08'},{'endDate':'2022-12-10'}]}, {'藥袋C':[{'startDate':'2022-12-08'},{'endDate':'2022-12-11'}]}]})

####################### 藥品內容相關 ###########################
# resp = requests.post("http://127.0.0.1:5000/pred", files={'file':open('photo/bet.jpg', 'rb')})
# resp = requests.post("http://127.0.0.1:5000/interaction", json={"drugA": '"培力"維復康膠囊', "drugB": '"海默尼"脊舒錠10毫克（貝可芬）'})
# resp = requests.post("http://127.0.0.1:5000/search", json={"drug":'    '})
# resp = requests.post("http://127.0.0.1:5000/search_drug", json={"drug":'舒以明片'})

####################### 用藥時程相關 ###########################
# resp = requests.post("http://127.0.0.1:5000/create_schedule", json={"drug": '綠油精', "duration": '3', "daily": '09:00', "scheduleBagId": 3,"hint": '1'})
# resp = requests.put("http://127.0.0.1:5000/create_schedule", json={"sid":1, "drug": '綠油精', "duration": '3', "daily": '09:00', "scheduleBagId": 3,"hint": '1'})
# resp = requests.post("http://127.0.0.1:5000/search_schedule", json={"date":'2022-12-15'})
resp = requests.get("http://127.0.0.1:5000/search_schedule")
# resp = requests.post("http://127.0.0.1:5000/search_schedule_mon", json={"date":'202212', "year":2022, "mon":12})

print(resp.text)