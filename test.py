import requests

# resp = requests.post("http://127.0.0.1:5000/register", json={"username":'阿洪',"account":'hhhhung@gmail.com', "password":'123456', 'allergy':[]})
# resp = requests.post("http://127.0.0.1:5000/pred", files={'file':open('001022.jpg', 'rb')})
# resp = requests.post("http://127.0.0.1:5000/interaction", json={"drugA": '"培力"維復康膠囊', "drugB": '"海默尼"脊舒錠10毫克（貝可芬）'})
resp = requests.post("http://127.0.0.1:5000/create_schedule", json={"drug": '綠油精', "startDate": '2021-01-01', "endDate": '2021-12-10', "duration": '1', "daily": '23:00', "bag": 'c', "hint": '1'})
# resp = requests.post("http://127.0.0.1:5000/search_schedule", json={"date":'2022-12-01'})
# resp = requests.get("http://127.0.0.1:5000/search_schedule")
# resp = requests.post("http://127.0.0.1:5000/search_schedule_mon", json={"date":'202112', "mon":12})
# resp = requests.post("http://127.0.0.1:5000/search", json={"drug":'    '})
# resp = requests.post("http://127.0.0.1:5000/search_drug", json={"drug":'舒以明片'})
# resp = requests.put("http://127.0.0.1:5000/create_schedule", json={"sid":'18', "drug": '綠油精', "startDate": '2021-10-10', "endDate": '2021-12-10', "duration": '1', "daily": '12:00:00', "bag": '藥袋C', "hint": '1'})
# resp = requests.get("http://127.0.0.1:5000/member_data")
# resp = requests.post("http://127.0.0.1:5000/member_update", json={"name":'阿洪洪', "password":'123456', 'allergy':['綠油精', '暈速寧片']})

print(resp.text)